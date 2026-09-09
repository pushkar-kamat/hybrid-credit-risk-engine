from pathlib import Path
import joblib 
import shap

# Project Path
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR/'models'/'credit_risk_lgbm.pkl'
THRESHOLD_PATH = BASE_DIR/'models'/'credit_risk_threshold.pkl'

# Load trained model and threshold
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"LightGBM Model not found at: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

def load_threshold():
    if not THRESHOLD_PATH.exists():
        raise FileNotFoundError(f"Decision threshold not found at: {THRESHOLD_PATH}")
    return joblib.load(THRESHOLD_PATH)

# Create SHAP explainer 
def create_explainer(model):

    return shap.TreeExplainer(model)
