
from typing import Any, Dict

import joblib
import pandas as pd

from app.config import (
    CUSTOMER_ID_COL,
    DISPLAY_DATA_PATH,
    FEATURE_COLUMNS_PATH,
    MODEL_PATH,
    SCORING_DATA_PATH,
)

from app.utils import (
    build_recommendation,
    map_probability_to_decision,
    map_probability_to_label,
)


class BadDebtInferenceService:
    def __init__(self):
        self.model = None
        self.scoring_df = None
        self.display_df = None
        self.feature_columns = None

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load the model and deployment datasets into memory."""

        # Validate required artifact files.
        required_files = {
            "Model": MODEL_PATH,
            "Scoring dataset": SCORING_DATA_PATH,
            "Display dataset": DISPLAY_DATA_PATH,
            "Feature columns": FEATURE_COLUMNS_PATH,
        }

        for name, path in required_files.items():
            if not path.exists():
                raise FileNotFoundError(
                    f"{name} file not found: {path}"
                )

        # Load the trained model and deployment data.
        self.model = joblib.load(MODEL_PATH)
        self.scoring_df = pd.read_csv(SCORING_DATA_PATH)
        self.display_df = pd.read_csv(DISPLAY_DATA_PATH)
        self.feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

        # Validate customer ID columns.
        if CUSTOMER_ID_COL not in self.scoring_df.columns:
            raise KeyError(
                f"'{CUSTOMER_ID_COL}' not found in scoring dataset."
            )

        if CUSTOMER_ID_COL not in self.display_df.columns:
            raise KeyError(
                f"'{CUSTOMER_ID_COL}' not found in display dataset."
            )

        # Validate that all required model features are available.
        missing_features = [
            column
            for column in self.feature_columns
            if column not in self.scoring_df.columns
        ]

        if missing_features:
            raise ValueError(
                "Scoring dataset is missing required model features: "
                f"{missing_features[:10]}"
            )

        print("Bad Debt Prediction artifacts loaded successfully.")
        print(f"Model path: {MODEL_PATH}")
        print(f"Total customers: {len(self.scoring_df)}")
        print(f"Model features: {len(self.feature_columns)}")

    def health(self) -> Dict[str, Any]:
        """Return the inference service health status."""

        return {
            "status": "ok",
            "model_loaded": self.model is not None,
            "scoring_data_loaded": self.scoring_df is not None,
            "display_data_loaded": self.display_df is not None,
            "total_customers_available": (
                int(len(self.scoring_df))
                if self.scoring_df is not None
                else 0
            ),
        }

    def _get_customer_scoring_row(
        self, customer_id: int
    ) -> pd.Series:
        """Retrieve the model features for a customer."""

        row = self.scoring_df.loc[
            self.scoring_df[CUSTOMER_ID_COL] == customer_id
        ]

        if row.empty:
            raise ValueError(
                f"Customer ID {customer_id} not found "
                "in scoring dataset."
            )

        return row.iloc[0]

    def _get_customer_display_row(
        self, customer_id: int
    ) -> Dict[str, Any]:
        """Retrieve customer information for the API response."""

        row = self.display_df.loc[
            self.display_df[CUSTOMER_ID_COL] == customer_id
        ]

        if row.empty:
            return {}

        display_row = row.iloc[0].to_dict()

        # Convert missing values into JSON-friendly values.
        cleaned = {}

        for key, value in display_row.items():
            if pd.isna(value):
                cleaned[key] = None
            elif hasattr(value, "item"):
                cleaned[key] = value.item()
            else:
                cleaned[key] = value

        return cleaned

    def predict_by_customer_id(
        self, customer_id: int
    ) -> Dict[str, Any]:
        """Predict bad-debt risk for a given customer ID."""

        if self.model is None:
            raise RuntimeError("The prediction model is not loaded.")

        # Get the customer's feature data.
        scoring_row = self._get_customer_scoring_row(customer_id)

        # Preserve the feature order used by the trained model.
        X = pd.DataFrame(
            [scoring_row[self.feature_columns].values],
            columns=self.feature_columns,
        )

        # Get the probability of the positive class (bad debt).
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(X)

            if probabilities.shape[1] < 2:
                raise ValueError(
                    "The model does not provide a probability "
                    "for the positive class."
                )

            bad_debt_probability = float(probabilities[0][1])

        else:
            prediction = self.model.predict(X)[0]
            bad_debt_probability = float(prediction)

        # Ensure the probability is within the valid range.
        bad_debt_probability = max(
            0.0, min(1.0, bad_debt_probability)
        )

        # Convert probability into a business decision.
        decision = map_probability_to_decision(
            bad_debt_probability
        )

        prediction_label = map_probability_to_label(
            bad_debt_probability
        )

        recommendation = build_recommendation(decision)

        # Retrieve customer details for display.
        customer_snapshot = self._get_customer_display_row(
            customer_id
        )

        # Return the prediction result.
        return {
            "customer_id": int(customer_id),
            "bad_debt_probability": round(
                bad_debt_probability, 6
            ),
            "prediction_label": prediction_label,
            "decision": decision,
            "recommendation": recommendation,
            "customer_snapshot": customer_snapshot,
        }
