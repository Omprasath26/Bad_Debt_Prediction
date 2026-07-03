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
        """
        Load model and deployment datasets into memory.
        """
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        if not SCORING_DATA_PATH.exists():
            raise FileNotFoundError(f"Scoring dataset not found: {SCORING_DATA_PATH}")

        if not DISPLAY_DATA_PATH.exists():
            raise FileNotFoundError(f"Display dataset not found: {DISPLAY_DATA_PATH}")

        if not FEATURE_COLUMNS_PATH.exists():
            raise FileNotFoundError(f"Feature columns file not found: {FEATURE_COLUMNS_PATH}")

        self.model = joblib.load(MODEL_PATH)
        self.scoring_df = pd.read_csv(SCORING_DATA_PATH)
        self.display_df = pd.read_csv(DISPLAY_DATA_PATH)
        self.feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

        # sanity checks
        if CUSTOMER_ID_COL not in self.scoring_df.columns:
            raise KeyError(f"'{CUSTOMER_ID_COL}' not found in scoring dataset.")

        if CUSTOMER_ID_COL not in self.display_df.columns:
            raise KeyError(f"'{CUSTOMER_ID_COL}' not found in display dataset.")

        missing_features = [col for col in self.feature_columns if col not in self.scoring_df.columns]
        if missing_features:
            raise ValueError(
                f"Scoring dataset is missing required model features: {missing_features[:10]}"
            )

    def health(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "model_loaded": self.model is not None,
            "scoring_data_loaded": self.scoring_df is not None,
            "display_data_loaded": self.display_df is not None,
            "total_customers_available": int(len(self.scoring_df)) if self.scoring_df is not None else 0,
        }

    def _get_customer_scoring_row(self, customer_id: int) -> pd.Series:
        row = self.scoring_df.loc[self.scoring_df[CUSTOMER_ID_COL] == customer_id]
        if row.empty:
            raise ValueError(f"Customer ID {customer_id} not found in scoring dataset.")
        return row.iloc[0]

    def _get_customer_display_row(self, customer_id: int) -> Dict[str, Any]:
        row = self.display_df.loc[self.display_df[CUSTOMER_ID_COL] == customer_id]
        if row.empty:
            return {}

        display_row = row.iloc[0].to_dict()

        # Convert NaN to None for cleaner JSON
        cleaned = {}
        for k, v in display_row.items():
            if pd.isna(v):
                cleaned[k] = None
            else:
                cleaned[k] = v
        return cleaned

    def predict_by_customer_id(self, customer_id: int) -> Dict[str, Any]:
        """
        Predict bad debt risk for a given customer id.
        """
        scoring_row = self._get_customer_scoring_row(customer_id)

        # Extract ordered feature vector
        X = pd.DataFrame([scoring_row[self.feature_columns].values], columns=self.feature_columns)

        # Model probability for positive class (bad debt risk)
        if hasattr(self.model, "predict_proba"):
            bad_debt_probability = float(self.model.predict_proba(X)[0][1])
        else:
            pred = self.model.predict(X)[0]
            bad_debt_probability = float(pred)

        decision = map_probability_to_decision(bad_debt_probability)
        prediction_label = map_probability_to_label(bad_debt_probability)
        recommendation = build_recommendation(decision)

        customer_snapshot = self._get_customer_display_row(customer_id)

        return {
            "customer_id": int(customer_id),
            "bad_debt_probability": round(bad_debt_probability, 6),
            "prediction_label": prediction_label,
            "decision": decision,
            "recommendation": recommendation,
            "customer_snapshot": customer_snapshot,
        }