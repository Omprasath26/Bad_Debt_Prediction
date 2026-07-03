
from app.config import GOOD_MAX_THRESHOLD, BAD_MAX_THRESHOLD

def map_probability_to_decision(probability: float) -> str:
    """
    Convert bad debt probability into business-friendly decision.
    """
    if probability <= GOOD_MAX_THRESHOLD:
        return "Good"
    elif probability <= BAD_MAX_THRESHOLD:
        return "Bad"
    else:
        return "Reject"


def map_probability_to_label(probability: float) -> str:
    """
    Convert probability into risk label.
    """
    if probability <= GOOD_MAX_THRESHOLD:
        return "Low Risk"
    elif probability <= BAD_MAX_THRESHOLD:
        return "Medium Risk"
    else:
        return "High Risk"


def build_recommendation(decision: str) -> str:
    """
    Human-readable recommendation for UI / business users.
    """
    if decision == "Good":
        return "Customer appears low risk. EMI approval can be considered."
    elif decision == "Bad":
        return "Customer has moderate repayment risk. Review profile before EMI approval."
    else:
        return "High risk customer. EMI approval is not recommended."