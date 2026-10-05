"""Paths and settings shared by the whole pipeline."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILE = ROOT / "Loan_default.csv"
RAW_DIR = ROOT / "data" / "raw"
CLEAN_DIR = ROOT / "data" / "clean"

SEED = 42

# The PRD caps the dataset at 50,000 records: 49,750 unique loans + 250 duplicates
N_UNIQUE_LOANS = 49_750
N_DUPLICATE_LOANS = 250

# Share of loans that belong to a customer who already has another loan
REPEAT_CUSTOMER_SHARE = 0.08
CUSTOMER_DUPLICATE_SHARE = 0.01

# Share of loans issued per year (volume grows over time, with a dip in 2020)
YEAR_WEIGHTS = {2019: 0.12, 2020: 0.11, 2021: 0.15, 2022: 0.18, 2023: 0.21, 2024: 0.23}

CUSTOMER_COLS = [
    "CustomerID", "Age", "Income", "CreditScore", "MonthsEmployed", "NumCreditLines",
    "Education", "EmploymentType", "MaritalStatus", "HasMortgage", "HasDependents",
]
LOAN_COLS = [
    "LoanID", "CustomerID", "IssueDate", "LoanAmount", "InterestRate", "LoanTerm",
    "DTIRatio", "LoanPurpose", "HasCoSigner", "Default",
]
