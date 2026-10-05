"""The two pipeline steps: build the raw files, then clean them."""

import numpy as np
import pandas as pd

from loanlens import config
from loanlens.bands import add_bands
from loanlens.cleaning import clean_customers, clean_loans, read_raw
from loanlens.corruption import mess_up_customers, mess_up_loans
from loanlens.report import build_report
from loanlens.sampling import build_tables


def prepare() -> None:
    """Build data/raw/ from the Kaggle file."""
    if not config.SOURCE_FILE.exists():
        raise SystemExit(f"Source file not found: {config.SOURCE_FILE}\n"
                         "Download Loan_default.csv from Kaggle (see README).")

    rng = np.random.default_rng(config.SEED)
    customers, loans = build_tables(pd.read_csv(config.SOURCE_FILE), rng)
    messy_customers = mess_up_customers(customers, rng)
    messy_loans = mess_up_loans(loans, rng)

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    messy_customers.df.to_csv(config.RAW_DIR / "customers_raw.csv", index=False)
    messy_loans.df.to_csv(config.RAW_DIR / "loans_raw.csv", index=False)
    log = pd.DataFrame(messy_customers.log + messy_loans.log)
    log.to_csv(config.RAW_DIR / "data_quality_log.csv", index=False)

    print(f"customers_raw.csv : {len(messy_customers.df):>6,} rows ({len(customers):,} unique customers)")
    print(f"loans_raw.csv     : {len(messy_loans.df):>6,} rows ({len(loans):,} unique loans)")
    print(f"data_quality_log  : {len(log):>6,} logged issues")


def clean() -> None:
    """Clean data/raw/ into data/clean/ and write expected_results.md."""
    raw_customers = read_raw(config.RAW_DIR / "customers_raw.csv")
    raw_loans = read_raw(config.RAW_DIR / "loans_raw.csv")
    raw_counts = {"customers": len(raw_customers), "loans": len(raw_loans)}

    customers = clean_customers(raw_customers)
    loans = clean_loans(raw_loans)
    joined = add_bands(customers, loans)

    config.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    customers.to_csv(config.CLEAN_DIR / "customers_clean.csv", index=False)
    loans.assign(IssueDate=loans["IssueDate"].dt.strftime("%Y-%m-%d")).to_csv(
        config.CLEAN_DIR / "loans_clean.csv", index=False)
    report = build_report(raw_counts, customers, loans, joined)
    (config.CLEAN_DIR / "expected_results.md").write_text(report, encoding="utf-8")

    print(f"Customers: {raw_counts['customers']:,} raw -> {len(customers):,} clean")
    print(f"Loans    : {raw_counts['loans']:,} raw -> {len(loans):,} clean")
    print(f"Default rate: {loans['Default'].mean():.2%}")
