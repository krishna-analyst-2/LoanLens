"""Writes expected_results.md, the numbers the Power BI report should show."""

import pandas as pd

from loanlens import bands


def rate_table(df: pd.DataFrame, by: str, order=None) -> str:
    g = df.groupby(by).agg(Loans=("LoanID", "size"), Defaults=("Default", "sum"))
    g["Default Rate"] = g["Defaults"] / g["Loans"]
    if order:
        g = g.reindex([o for o in order if o in g.index])
    lines = [f"| {by} | Loans | Defaults | Default Rate |", "|---|---:|---:|---:|"]
    for idx, r in g.iterrows():
        lines.append(f"| {idx} | {r['Loans']:,} | {r['Defaults']:,} | {r['Default Rate']:.2%} |")
    return "\n".join(lines)


def cleaning_summary(raw_counts: dict, customers: pd.DataFrame, loans: pd.DataFrame) -> list[str]:
    median_income = int(customers.loc[customers["IncomeImputed"], "Income"].iloc[0])
    median_rate = loans.loc[loans["InterestRateImputed"], "InterestRate"].iloc[0]
    return [
        "## Data cleaning summary",
        "",
        "| Check | Customers | Loans |",
        "|---|---:|---:|",
        f"| Raw rows | {raw_counts['customers']:,} | {raw_counts['loans']:,} |",
        f"| Duplicate rows removed | {raw_counts['customers'] - len(customers):,} | "
        f"{raw_counts['loans'] - len(loans):,} |",
        f"| Clean rows | {len(customers):,} | {len(loans):,} |",
        f"| Values imputed (median) | {int(customers['IncomeImputed'].sum()):,} Income | "
        f"{int(loans['InterestRateImputed'].sum()):,} InterestRate |",
        f"| Impossible values blanked | {int(customers['Age'].isna().sum()):,} Age, "
        f"{int(customers['CreditScore'].isna().sum()):,} CreditScore | "
        f"{int(loans['LoanTerm'].isna().sum()):,} LoanTerm |",
        f"| 'Unknown' categories | {int((customers['MaritalStatus'] == 'Unknown').sum()):,} MaritalStatus | "
        f"{int((loans['LoanPurpose'] == 'Unknown').sum()):,} LoanPurpose |",
        f"| Unparsed dates | - | {int(loans['IssueDate'].isna().sum()):,} |",
        "",
        f"Median income used for imputation: **{median_income:,}**  ",
        f"Median interest rate used for imputation: **{median_rate:.3f}**",
        "",
    ]


def kpi_table(loans: pd.DataFrame, joined: pd.DataFrame) -> list[str]:
    total = len(loans)
    defaults = int(loans["Default"].sum())
    defaulted_amount = int(loans.loc[loans["Default"] == 1, "LoanAmount"].sum())
    return [
        "## KPI cards",
        "",
        "| Measure | Expected value |",
        "|---|---:|",
        f"| Total Loans | {total:,} |",
        f"| Total Customers | {loans['CustomerID'].nunique():,} |",
        f"| Defaulted Loans | {defaults:,} |",
        f"| Default Rate | {defaults / total:.2%} |",
        f"| Total Loan Amount | {int(loans['LoanAmount'].sum()):,} |",
        f"| Defaulted Amount | {defaulted_amount:,} |",
        f"| Avg Loan Amount | {loans['LoanAmount'].mean():,.0f} |",
        f"| Avg Interest Rate | {loans['InterestRate'].mean():.2f}% |",
        f"| Avg Credit Score | {joined['CreditScore'].mean():.1f} |",
        f"| Avg Income | {joined['Income'].mean():,.0f} |",
        f"| Avg DTI Ratio | {loans['DTIRatio'].mean():.3f} |",
        "",
    ]


def build_report(raw_counts: dict, customers: pd.DataFrame, loans: pd.DataFrame,
                 joined: pd.DataFrame) -> str:
    banded = [(name, spec[1]) for name, spec in {**bands.CUSTOMER_BANDS, **bands.LOAN_BANDS}.items()]
    categorical = ["LoanTerm", "EmploymentType", "Education", "MaritalStatus", "LoanPurpose",
                   "HasCoSigner", "HasDependents", "HasMortgage"]

    sections = [
        "# LoanLens - Expected Results",
        "",
        "Created by `python -m loanlens clean`. Once the Power Query and DAX steps are done,",
        "the cards and charts in Power BI should show these numbers (with no slicers applied).",
        "",
        *cleaning_summary(raw_counts, customers, loans),
        *kpi_table(loans, joined),
        "## Default rate by risk factor",
        "",
    ]
    for name, band_list in banded:
        sections += [rate_table(joined, name, bands.labels(band_list)), ""]
    for column in categorical:
        sections += [rate_table(joined, column), ""]
    sections += ["## Default rate by year", "", rate_table(joined, "Year"), ""]
    return "\n".join(sections)
