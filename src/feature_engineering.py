import pandas as pd

FEATURE_COLUMNS = [
    "CreditUtilization",
    "Age",
    "Late30-59DaysPastDue",
    "DebtRatio",
    "MonthlyIncome",
    "OpenCreditLines",
    "Late90DaysPastDue",
    "RealEstateLoans",
    "Late60-89DaysPastDue",
    "Dependents",
    "TotalLate",
    "IncomePerPerson",
]

def create_features(borrower: dict) -> pd.DataFrame:

    """
    Convert raw borrower information into the exact
    feature structure expected by the LightGBM model
    """

    data = borrower.copy()

    # Same feature engineering used durimg model traning
    data['TotalLate'] = (
        data['Late30-59DaysPastDue'] + data['Late60-89DaysPastDue'] + data['Late90DaysPastDue']
    )

    data['IncomePerPerson'] = (
        data['MonthlyIncome'] / (data['Dependents'] + 1)
    )

    X = pd.DataFrame([data])
    
    # Ensure exact feature order
    X = X[FEATURE_COLUMNS]

    return X
