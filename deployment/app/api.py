from fastapi import FastAPI, HTTPException

from deployment.app.inference import BadDebtInferenceService
from deployment.app.schemas import HealthResponse, PredictionRequest, PredictionResponse

app = FastAPI(
    title="Bad Debt Prediction API",
    description="Customer-ID based EMI bad debt prediction service",
    version="1.0.0"
)

# Load artifacts once at startup
try:
    inference_service = BadDebtInferenceService()
except Exception as e:
    inference_service = None
    startup_error = str(e)
else:
    startup_error = None


@app.get("/health", response_model=HealthResponse)
def health_check():
    if inference_service is None:
        raise HTTPException(status_code=500, detail=f"Service failed to start: {startup_error}")

    return inference_service.health()


@app.post("/predict-by-customer", response_model=PredictionResponse)
def predict_by_customer(request: PredictionRequest):
    if inference_service is None:
        raise HTTPException(status_code=500, detail=f"Service failed to start: {startup_error}")

    try:
        result = inference_service.predict_by_customer_id(request.customer_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")