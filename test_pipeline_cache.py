from src.pipeline import CreditRiskPipeline


borrower = {
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
}


pipeline = CreditRiskPipeline()


# Assessment does NOT call Gemini
assessment = pipeline.assess(borrower)

print("\nProbability:")
print(
    f"{assessment['risk_context']['probability_of_default']:.2f}%"
)

print("Decision:")
print(
    assessment["risk_context"]["decision"]
)


# Memo generation
print("\nGenerating memo...")

memo = pipeline.generate_memo(
    borrower,
    assessment["risk_context"]
)

print("\nMemo:")
print(memo)