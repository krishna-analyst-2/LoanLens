"""Cleaning rules for the raw files.

These follow the Power Query scripts in powerquery/ step for step, so the output
can be used to check the numbers in the Power BI report.
"""

from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

EMPLOYMENT_MAP = {"full-time": "Full-time", "part-time": "Part-time",
                  "self-employed": "Self-employed", "unemployed": "Unemployed"}
EDUCATION_MAP = {"bachelors": "Bachelor's", "masters": "Master's",
                 "high school": "High School", "phd": "PhD"}
MARITAL_MAP = {"married": "Married", "single": "Single", "divorced": "Divorced"}
PURPOSE_MAP = {"auto": "Auto", "business": "Business", "education": "Education",
               "home": "Home", "other": "Other"}
YES_VALUES = {"yes", "y", "true", "1"}
NO_VALUES = {"no", "n", "false", "0"}
VALID_TERMS = {12, 24, 36, 48, 60}
DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y")


def read_raw(path: Path) -> pd.DataFrame:
    """Read a raw CSV with every column as text, like Power Query does before typing."""
    return pd.read_csv(path, dtype=str, keep_default_na=False).astype(object)


def normalize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Trim every value and turn empty strings into nulls."""
    return df.apply(lambda col: col.map(lambda v: (v.strip() or None) if isinstance(v, str) else None))


def standardize(series: pd.Series, mapping: dict, reshape_key=lambda k: k) -> pd.Series:
    """Map messy labels onto standard ones. Missing or unknown labels become 'Unknown'."""
    def convert(v):
        if pd.isna(v):
            return "Unknown"
        return mapping.get(reshape_key(v.lower()), "Unknown")
    return series.map(convert)


def to_yes_no(series: pd.Series) -> pd.Series:
    def convert(v):
        if pd.isna(v):
            return "Unknown"
        k = v.lower()
        if k in YES_VALUES:
            return "Yes"
        if k in NO_VALUES:
            return "No"
        return "Unknown"
    return series.map(convert)


def to_default_flag(v):
    if pd.isna(v):
        return None
    k = v.lower()
    if k in YES_VALUES:
        return 1
    if k in NO_VALUES:
        return 0
    return None


def parse_date(v) -> date | None:
    if pd.isna(v):
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    return None


def to_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series).astype("Int64")


def clean_customers(raw: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text(raw).drop_duplicates()

    df["EmploymentType"] = standardize(df["EmploymentType"], EMPLOYMENT_MAP, lambda k: k.replace(" ", "-"))
    df["Education"] = standardize(df["Education"], EDUCATION_MAP, lambda k: k.replace("'", ""))
    df["MaritalStatus"] = standardize(df["MaritalStatus"], MARITAL_MAP)
    df["HasMortgage"] = to_yes_no(df["HasMortgage"])
    df["HasDependents"] = to_yes_no(df["HasDependents"])

    for col in ("Age", "Income", "CreditScore", "MonthsEmployed", "NumCreditLines"):
        df[col] = to_int(df[col])

    df.loc[(df["Age"] < 18) | (df["Age"] > 100), "Age"] = pd.NA
    df.loc[(df["CreditScore"] < 300) | (df["CreditScore"] > 850), "CreditScore"] = pd.NA

    median_income = round(float(df["Income"].median()))
    df["IncomeImputed"] = df["Income"].isna()
    df["Income"] = df["Income"].fillna(median_income)

    columns = ["CustomerID", "Age", "Income", "IncomeImputed", "CreditScore", "MonthsEmployed",
               "NumCreditLines", "Education", "EmploymentType", "MaritalStatus",
               "HasMortgage", "HasDependents"]
    return df[columns].reset_index(drop=True)


def clean_loans(raw: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text(raw).drop_duplicates()

    df["InterestRate"] = pd.to_numeric(df["InterestRate"].map(
        lambda v: None if pd.isna(v) else v.replace("%", "")))
    median_rate = float(df["InterestRate"].median())
    df["InterestRateImputed"] = df["InterestRate"].isna()
    df["InterestRate"] = df["InterestRate"].fillna(median_rate)

    df["LoanPurpose"] = standardize(df["LoanPurpose"], PURPOSE_MAP)
    df["HasCoSigner"] = to_yes_no(df["HasCoSigner"])
    df["Default"] = df["Default"].map(to_default_flag).astype("Int64")
    df["LoanStatus"] = np.where(df["Default"] == 1, "Default", "Non-Default")

    df["LoanAmount"] = to_int(df["LoanAmount"])
    df["DTIRatio"] = pd.to_numeric(df["DTIRatio"])
    df["LoanTerm"] = to_int(df["LoanTerm"])
    df.loc[~df["LoanTerm"].isin(VALID_TERMS), "LoanTerm"] = pd.NA
    df["IssueDate"] = pd.to_datetime(df["IssueDate"].map(parse_date))

    columns = ["LoanID", "CustomerID", "IssueDate", "LoanAmount", "InterestRate",
               "InterestRateImputed", "LoanTerm", "DTIRatio", "LoanPurpose", "HasCoSigner",
               "Default", "LoanStatus"]
    return df[columns].reset_index(drop=True)
