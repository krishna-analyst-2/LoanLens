"""Grouping of numeric fields into bands, matching dax/02_Calculated_Columns.dax.

Each band is (upper bound, label). Upper bounds are exclusive, e.g. an age of 26
falls in "26-35", not "18-25".
"""

import numpy as np
import pandas as pd

AGE_BANDS = [(26, "18-25"), (36, "26-35"), (46, "36-45"), (56, "46-55"), (np.inf, "56+")]
INCOME_BANDS = [(40_000, "Under 40K"), (70_000, "40K-70K"), (100_000, "70K-100K"), (np.inf, "100K+")]
CREDIT_BANDS = [(580, "Poor (300-579)"), (670, "Fair (580-669)"), (740, "Good (670-739)"),
                (800, "Very Good (740-799)"), (np.inf, "Excellent (800-850)")]
EMPLOYMENT_LENGTH_BANDS = [(12, "Under 1 yr"), (36, "1-3 yrs"), (60, "3-5 yrs"), (np.inf, "5+ yrs")]
RATE_BANDS = [(8, "Low (<8%)"), (13, "Moderate (8-13%)"), (18, "High (13-18%)"),
              (np.inf, "Very High (18%+)")]
AMOUNT_BANDS = [(50_000, "Under 50K"), (100_000, "50K-100K"), (150_000, "100K-150K"),
                (200_000, "150K-200K"), (np.inf, "200K+")]
DTI_BANDS = [(0.3, "Low (<0.3)"), (0.5, "Medium (0.3-0.5)"), (0.7, "High (0.5-0.7)"),
             (np.inf, "Very High (0.7+)")]

CUSTOMER_BANDS = {
    "Age Group": ("Age", AGE_BANDS),
    "Income Band": ("Income", INCOME_BANDS),
    "Credit Score Band": ("CreditScore", CREDIT_BANDS),
    "Employment Length": ("MonthsEmployed", EMPLOYMENT_LENGTH_BANDS),
}
LOAN_BANDS = {
    "Interest Rate Band": ("InterestRate", RATE_BANDS),
    "Loan Amount Band": ("LoanAmount", AMOUNT_BANDS),
    "DTI Band": ("DTIRatio", DTI_BANDS),
}


def band(value, bands) -> str:
    if pd.isna(value):
        return "Unknown"
    for upper, label in bands:
        if value < upper:
            return label
    return bands[-1][1]


def labels(bands) -> list[str]:
    """Band labels in display order, with Unknown last."""
    return [label for _, label in bands] + ["Unknown"]


def add_bands(customers: pd.DataFrame, loans: pd.DataFrame) -> pd.DataFrame:
    """Join loans to customers and add every band column plus the issue year."""
    customers = customers.copy()
    for name, (column, bands) in CUSTOMER_BANDS.items():
        customers[name] = customers[column].map(lambda v, b=bands: band(v, b))

    joined = loans.merge(customers, on="CustomerID", how="left", validate="many_to_one")
    for name, (column, bands) in LOAN_BANDS.items():
        joined[name] = joined[column].map(lambda v, b=bands: band(v, b))
    joined["Year"] = joined["IssueDate"].dt.year
    return joined
