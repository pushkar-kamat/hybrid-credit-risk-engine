def determine_action(probability: float, decision: str) -> dict:
    """
    Apply deterministic business-policy logic to the ML result.

    This policy is for the project demonstration and is separate
    from the machine learning model.
    """

    if probability >= 0.20:
        return {
            "risk_level": "High",
            "recommended_action": "Enhanced underwriting review",
            "reason": (
                "The model classified the borrower as Default Risk "
                "because the probability of default is at or above "
                "the configured decision threshold."
            )
        }

    elif probability >= 0.10:
        return {
            "risk_level": "Moderate",
            "recommended_action": "Additional underwriting review",
            "reason": (
                "The probability of default is below the default-risk "
                "threshold but falls within the moderate-risk band."
            )
        }

    else:
        return {
            "risk_level": "Low",
            "recommended_action": "Standard underwriting review",
            "reason": (
                "The probability of default is below the "
                "moderate-risk band."
            )
        }