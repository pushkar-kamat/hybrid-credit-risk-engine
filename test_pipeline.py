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

result = pipeline.run(borrower)


print("=" *50)
print("PIPELINE TEST")
print("=" * 50)

print("\nRisk Context:")
print(result["risk_context"])

print("\nCredit Risk Memo:")
print("-" * 50)
print(result["memo"])