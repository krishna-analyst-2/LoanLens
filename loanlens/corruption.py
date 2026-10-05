"""Adds realistic data quality problems so there is something to clean in Power Query.

Every changed value is recorded, so the log can be checked against the cleaning results.
"""

import numpy as np
import pandas as pd

from loanlens import config


class MessMaker:
    def __init__(self, table_name: str, df: pd.DataFrame, key: str, rng: np.random.Generator):
        self.table = table_name
        self.df = df.astype(str).astype(object)
        self.key = key
        self.rng = rng
        self.log: list[dict] = []
        self._used: dict[str, set] = {}

    def pick(self, column: str, share: float) -> np.ndarray:
        """Random rows for a column. A row is never picked twice for the same column."""
        used = self._used.setdefault(column, set())
        candidates = np.array([i for i in self.df.index if i not in used])
        n = min(round(len(self.df) * share), len(candidates))
        chosen = self.rng.choice(candidates, size=n, replace=False)
        used.update(chosen.tolist())
        return chosen

    def apply(self, column: str, rows, change, issue: str, fix: str) -> None:
        for i in rows:
            old = self.df.at[i, column]
            new = change(old)
            self.df.at[i, column] = new
            self.log.append({
                "Table": self.table, "RecordID": self.df.at[i, self.key], "Column": column,
                "IssueType": issue, "OriginalValue": old, "RawValue": new, "ExpectedFix": fix,
            })

    def add_duplicates(self, n: int) -> None:
        rows = self.rng.choice(self.df.index, size=n, replace=False)
        dupes = self.df.loc[rows]
        for record_id in dupes[self.key]:
            self.log.append({
                "Table": self.table, "RecordID": record_id, "Column": "(entire row)",
                "IssueType": "Duplicate row", "OriginalValue": "", "RawValue": "",
                "ExpectedFix": "Remove duplicate rows",
            })
        combined = pd.concat([self.df, dupes], ignore_index=True)
        self.df = combined.sample(frac=1, random_state=config.SEED).reset_index(drop=True)

    def case_variant(self, value: str) -> str:
        style = self.rng.integers(0, 3)
        if style == 0:
            return value.lower()
        if style == 1:
            return value.upper()
        return f"  {value} "


def mess_up_customers(customers: pd.DataFrame, rng: np.random.Generator) -> MessMaker:
    m = MessMaker("Customers", customers, "CustomerID", rng)

    m.apply("Income", m.pick("Income", 0.015), lambda v: "",
            "Missing value", "Impute median income, flag IncomeImputed = TRUE")

    def employment_variant(v: str) -> str:
        style = rng.integers(0, 4)
        return [v.lower(), v.upper(), f" {v}  ", v.lower().replace("-", " ")][style]
    m.apply("EmploymentType", m.pick("EmploymentType", 0.03), employment_variant,
            "Inconsistent text", "Standardize to Full-time / Part-time / Self-employed / Unemployed")

    def education_variant(v: str) -> str:
        style = rng.integers(0, 3)
        return [v.replace("'", ""), v.lower(), v.upper()][style]
    m.apply("Education", m.pick("Education", 0.02), education_variant,
            "Inconsistent text", "Standardize to Bachelor's / Master's / High School / PhD")

    m.apply("MaritalStatus", m.pick("MaritalStatus", 0.005), lambda v: "",
            "Missing value", "Replace with 'Unknown'")
    m.apply("MaritalStatus", m.pick("MaritalStatus", 0.01), m.case_variant,
            "Inconsistent text", "Standardize to Married / Single / Divorced")

    yes_no_variants = {"Yes": ["Y", "yes", "1", "TRUE"], "No": ["N", "no", "0", "FALSE"]}
    for col in ("HasMortgage", "HasDependents"):
        m.apply(col, m.pick(col, 0.02), lambda v: rng.choice(yes_no_variants[v]),
                "Inconsistent text", "Standardize to Yes / No")

    m.apply("Age", m.pick("Age", 0.002), lambda v: str(rng.choice([0, -5, 150, 200, 999])),
            "Impossible value", "Ages outside 18-100 set to blank")
    m.apply("CreditScore", m.pick("CreditScore", 0.002), lambda v: str(rng.choice([0, 999, 1200])),
            "Impossible value", "Scores outside 300-850 set to blank")

    m.add_duplicates(round(len(customers) * config.CUSTOMER_DUPLICATE_SHARE))
    return m


def mess_up_loans(loans: pd.DataFrame, rng: np.random.Generator) -> MessMaker:
    m = MessMaker("Loans", loans, "LoanID", rng)

    m.apply("InterestRate", m.pick("InterestRate", 0.03), lambda v: f"{v}%",
            "Mixed number format", "Remove % sign and convert to number")
    m.apply("InterestRate", m.pick("InterestRate", 0.008), lambda v: "",
            "Missing value", "Impute median interest rate, flag InterestRateImputed = TRUE")

    m.apply("LoanPurpose", m.pick("LoanPurpose", 0.03), m.case_variant,
            "Inconsistent text", "Standardize to Auto / Business / Education / Home / Other")
    m.apply("LoanPurpose", m.pick("LoanPurpose", 0.005), lambda v: "",
            "Missing value", "Replace with 'Unknown'")

    yes_no_variants = {"Yes": ["Y", "yes", "1"], "No": ["N", "no", "0"]}
    m.apply("HasCoSigner", m.pick("HasCoSigner", 0.02), lambda v: rng.choice(yes_no_variants[v]),
            "Inconsistent text", "Standardize to Yes / No")

    m.apply("Default", m.pick("Default", 0.01), lambda v: {"1": "Yes", "0": "No"}[v],
            "Mixed format", "Convert Yes/No to 1/0")

    m.apply("LoanTerm", m.pick("LoanTerm", 0.002), lambda v: str(rng.choice([0, 999])),
            "Impossible value", "Terms other than 12/24/36/48/60 set to blank")

    def day_first(v: str) -> str:
        y, mth, d = v.split("-")
        return f"{d}/{mth}/{y}"
    m.apply("IssueDate", m.pick("IssueDate", 0.05), day_first,
            "Mixed date format", "Parse both yyyy-MM-dd and dd/MM/yyyy")

    m.add_duplicates(config.N_DUPLICATE_LOANS)
    return m
