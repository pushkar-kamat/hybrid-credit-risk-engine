import pandas as pd 
import numpy as np

from src.model import load_model, load_threshold, create_explainer
from src.feature_engineering import create_features, FEATURE_COLUMNS
from src.policy_engine import determine_action

class CreditRiskEngine:

    def __init__(self):
        self.model = load_model()
        self.threshold = load_threshold()
        self.explainer = create_explainer(self.model)

    def predict(self, borrower: dict) -> dict:

        # Feature Engineering 
        X = create_features(borrower)

        # Probability of Default
        probability = self.model.predict_proba(X)[0, 1]

        # Apply saved Threshold
        prediction = int(probability >= self.threshold)

        if prediction == 1:
            decision = "Default Risk"
        else:
            decision = "Non-Default Risk"

        policy = determine_action(
            probability=probability,
            decision=decision
        )

        # SHAP Explanation
        shap_values = self.explainer.shap_values(X)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_values = np.asarray(shap_values)[0]

        # SHAP Table
        shap_df = pd.DataFrame({
            'feature': FEATURE_COLUMNS,
            'value': X.iloc[0].values,
            'shap_value': shap_values
        })

        shap_df['direction'] = np.where(
            shap_df['shap_value'] > 0,
            "increase_default_risk",
            "decrease_default_risk"
        )

        shap_df['abs_shap'] = shap_df['shap_value'].abs()

        shap_df = shap_df.sort_values('abs_shap', ascending=False)

        return {
            "probability": float(probability),
            "probability_percent": float(probability * 100),
            "threshold": float(self.threshold),
            "prediction": prediction,
            "decision": decision,
            "policy": policy,
            "features": X,
            "shap_values": shap_df 
        }

def build_risk_context(result: dict) -> dict:
    """
    Convert raw model and SHAP output into
    clean JSON Structure for LLM
    """

    shap_df = result['shap_values']

    positive = shap_df[shap_df['shap_value'] > 0].head(5)
    negative = shap_df[shap_df['shap_value'] < 0].head(5)

    risk_factors = []

    for _, row in positive.iterrows():
        risk_factors.append({
            "feature": row['feature'],
            "value": float(row['value']),
            "shap_value": round(float(row['shap_value']), 4)
        })

    protective_factors = []

    for _, row in negative.iterrows():
        protective_factors.append({
            "feature": row['feature'],
            "value": float(row['value']),
            "shap_value": round(float(row['shap_value']), 4)
        })

    return {
        "probability_of_default": round(result['probability_percent'], 2),
        "decision_threshold": round(result['threshold'] * 100, 2),
        "decision": result['decision'],
        "policy": result['policy'],
        "risk_factors": risk_factors,
        "protective_factors": protective_factors
    }