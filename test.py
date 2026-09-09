# from src.model import load_model, load_threshold, create_explainer

# model = load_model()
# threshold = load_threshold()
# explainer = create_explainer(model)

# print("model:", type(model))
# print("threshold", threshold)
# print("explainer:", type(explainer))

from src.risk_engine import CreditRiskEngine, build_risk_context
from src.memo_generator import CreditMemoGenerator

borrowers = {

    "High Risk Borrower": {
        "CreditUtilization": 0.90,
        "Age": 40,
        "Late30-59DaysPastDue": 5,
        "DebtRatio": 0.90,
        "MonthlyIncome": 5000.0,
        "OpenCreditLines": 15,
        "Late90DaysPastDue": 2,
        "RealEstateLoans": 5,
        "Late60-89DaysPastDue": 2,
        "Dependents": 3.0
    },

    "Borderline Borrower": {
        "CreditUtilization": 0.60,
        "Age": 45,
        "Late30-59DaysPastDue": 1,
        "DebtRatio": 0.50,
        "MonthlyIncome": 8000.0,
        "OpenCreditLines": 10,
        "Late90DaysPastDue": 0,
        "RealEstateLoans": 2,
        "Late60-89DaysPastDue": 0,
        "Dependents": 2.0
    },

    "Low Risk Borrower": {
        "CreditUtilization": 0.15,
        "Age": 35,
        "Late30-59DaysPastDue": 0,
        "DebtRatio": 0.20,
        "MonthlyIncome": 15000.0,
        "OpenCreditLines": 8,
        "Late90DaysPastDue": 0,
        "RealEstateLoans": 1,
        "Late60-89DaysPastDue": 0,
        "Dependents": 1.0
    }
}

engine = CreditRiskEngine()
memo_generator = CreditMemoGenerator()

for borrower_name, borrower in borrowers.items():

    result = engine.predict(borrower)

    risk_context = build_risk_context(result)

    memo = memo_generator.generate_memo(risk_context)

    print("\n" + "=" * 60)
    print(borrower_name)
    print("=" * 60)

    print(
        f"Probability of Default: "
        f"{result['probability_percent']:.2f}%"
    )

    print(
        f"Decision: "
        f"{result['decision']}"
    )

    print("\nCREDIT RISK MEMO")
    print("-" * 60)
    print(memo)