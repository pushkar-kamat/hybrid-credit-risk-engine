from src.cache import initialize_cache, create_applicant_key, get_cached_memo, save_cached_memo

# Create the cache database/table
initialize_cache()

# Example applicant
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

# Create unique key
key = create_applicant_key(borrower)

print("Cache Key:")
print(key)

# Initially there should be no memo
cached = get_cached_memo(key)

print("\nBefore saving:")
print(cached)

# Save a test memo
test_memo = "This is a cached test credit memo."

save_cached_memo(key, test_memo)

# Read it back
cached = get_cached_memo(key)

print("\nAfter saving:")
print(cached)