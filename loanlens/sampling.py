"""Turns the Kaggle file into separate Customer and Loan tables."""

import numpy as np
import pandas as pd

from loanlens import config


def assign_customers(n_loans: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Give every loan a CustomerID. Most loans get a new customer, a few reuse one.

    Returns the CustomerID per loan and the row positions that created each customer.
    """
    n_repeat = round(n_loans * config.REPEAT_CUSTOMER_SHARE)
    n_customers = n_loans - n_repeat
    order = rng.permutation(n_loans)
    owner_rows, repeat_rows = order[:n_customers], order[n_customers:]

    new_ids = np.array([f"CUST-{i:06d}" for i in range(1, n_customers + 1)], dtype=object)
    customer_ids = np.empty(n_loans, dtype=object)
    customer_ids[owner_rows] = new_ids
    customer_ids[repeat_rows] = rng.choice(new_ids, size=n_repeat, replace=True)
    return customer_ids, owner_rows


def random_issue_dates(n_loans: int, rng: np.random.Generator) -> pd.Series:
    """Random issue dates spread over the years in YEAR_WEIGHTS."""
    years = pd.Series(rng.choice(list(config.YEAR_WEIGHTS), size=n_loans,
                                 p=list(config.YEAR_WEIGHTS.values())))
    year_start = pd.to_datetime(years.astype(str) + "-01-01")
    days_in_year = years.map(lambda y: pd.Timestamp(y, 12, 31).dayofyear).to_numpy()
    offsets = (rng.random(n_loans) * days_in_year).astype(int)
    return (year_start + pd.to_timedelta(offsets, unit="D")).dt.strftime("%Y-%m-%d")


def build_tables(source: pd.DataFrame, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sample the source data and split it into clean Customers and Loans tables."""
    sample = source.sample(n=config.N_UNIQUE_LOANS, random_state=config.SEED).reset_index(drop=True)

    customer_ids, owner_rows = assign_customers(len(sample), rng)
    sample["CustomerID"] = customer_ids
    # Borrower details come from the loan that created the customer
    customers = (sample.loc[owner_rows, config.CUSTOMER_COLS]
                 .sort_values("CustomerID").reset_index(drop=True))

    sample["IssueDate"] = random_issue_dates(len(sample), rng)
    loans = sample[config.LOAN_COLS].sort_values(["IssueDate", "LoanID"]).reset_index(drop=True)
    return customers, loans
