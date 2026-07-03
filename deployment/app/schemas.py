from typing import Any, Dict
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    customer_id: int = Field(..., description="Customer ID to score")


class PredictionResponse(BaseModel):
    customer_id: int
    bad_debt_probability: float
    prediction_label: str
    decision: str
    recommendation: str
    customer_snapshot: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    scoring_data_loaded: bool
    display_data_loaded: bool
    total_customers_available: int