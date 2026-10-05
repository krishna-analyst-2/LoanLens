"""Command line entry point.

    python -m loanlens prepare   build data/raw/ from Loan_default.csv
    python -m loanlens clean     clean data/raw/ and write data/clean/
    python -m loanlens all       both steps
"""

import argparse

from loanlens.pipeline import clean, prepare


def main() -> None:
    parser = argparse.ArgumentParser(prog="loanlens", description="LoanLens data pipeline")
    parser.add_argument("step", choices=["prepare", "clean", "all"])
    args = parser.parse_args()

    if args.step in ("prepare", "all"):
        prepare()
    if args.step in ("clean", "all"):
        clean()


if __name__ == "__main__":
    main()
