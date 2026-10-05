import pandas as pd

from loanlens.cleaning import clean_customers, clean_loans, parse_date

CUSTOMER_HEADER = ["CustomerID", "Age", "Income", "CreditScore", "MonthsEmployed", "NumCreditLines",
                   "Education", "EmploymentType", "MaritalStatus", "HasMortgage", "HasDependents"]
LOAN_HEADER = ["LoanID", "CustomerID", "IssueDate", "LoanAmount", "InterestRate", "LoanTerm",
               "DTIRatio", "LoanPurpose", "HasCoSigner", "Default"]


def make_raw(header, rows):
    return pd.DataFrame(rows, columns=header).astype(object)


def test_customers_text_is_standardized():
    raw = make_raw(CUSTOMER_HEADER, [
        ["C1", "30", "50000", "600", "10", "2", "bachelors", " FULL-TIME ", "married", "Y", "0"],
        ["C2", "40", "60000", "700", "20", "3", "MASTER'S", "self employed", "", "TRUE", "no"],
        ["C3", "50", "70000", "800", "30", "1", "PhD", "Unemployed", "SINGLE", "No", "1"],
    ])
    clean = clean_customers(raw).set_index("CustomerID")

    assert clean["Education"].tolist() == ["Bachelor's", "Master's", "PhD"]
    assert clean["EmploymentType"].tolist() == ["Full-time", "Self-employed", "Unemployed"]
    assert clean["MaritalStatus"].tolist() == ["Married", "Unknown", "Single"]
    assert clean["HasMortgage"].tolist() == ["Yes", "Yes", "No"]
    assert clean["HasDependents"].tolist() == ["No", "No", "Yes"]


def test_customers_duplicates_outliers_and_imputation():
    raw = make_raw(CUSTOMER_HEADER, [
        ["C1", "150", "40000", "999", "10", "2", "PhD", "Full-time", "Married", "Yes", "No"],
        ["C2", "30", "", "650", "10", "2", "PhD", "Full-time", "Married", "Yes", "No"],
        ["C3", "45", "60000", "700", "10", "2", "PhD", "Full-time", "Married", "Yes", "No"],
        ["C3", "45", "60000", "700", "10", "2", "PhD", "Full-time", "Married", "Yes", "No"],
    ])
    clean = clean_customers(raw).set_index("CustomerID")

    assert len(clean) == 3
    assert pd.isna(clean.at["C1", "Age"])
    assert pd.isna(clean.at["C1", "CreditScore"])
    assert clean.at["C2", "Income"] == 50000
    assert clean["IncomeImputed"].tolist() == [False, True, False]


def test_loans_formats_are_fixed():
    raw = make_raw(LOAN_HEADER, [
        ["L1", "C1", "2021-03-15", "1000", "12.5%", "36", "0.4", "home", "y", "Yes"],
        ["L2", "C1", "15/03/2021", "2000", "", "999", "0.5", "", "N", "0"],
        ["L3", "C2", "2022-01-01", "3000", "14.5", "60", "0.6", " AUTO ", "1", "1"],
    ])
    clean = clean_loans(raw).set_index("LoanID")

    assert clean.at["L1", "InterestRate"] == 12.5
    assert clean.at["L2", "InterestRate"] == 13.5
    assert clean["InterestRateImputed"].tolist() == [False, True, False]
    assert clean.at["L1", "IssueDate"] == clean.at["L2", "IssueDate"]
    assert pd.isna(clean.at["L2", "LoanTerm"])
    assert clean["LoanPurpose"].tolist() == ["Home", "Unknown", "Auto"]
    assert clean["HasCoSigner"].tolist() == ["Yes", "No", "Yes"]
    assert clean["Default"].tolist() == [1, 0, 1]
    assert clean["LoanStatus"].tolist() == ["Default", "Non-Default", "Default"]


def test_parse_date_handles_both_formats_and_garbage():
    assert parse_date("2020-02-29") == parse_date("29/02/2020")
    assert parse_date("not a date") is None
    assert parse_date(None) is None
