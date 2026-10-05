# Data Dictionary

## Source

| Item | Detail |
|---|---|
| Dataset | Kaggle "Loan Default Prediction Dataset" (`Loan_default.csv`), https://www.kaggle.com/datasets/nikhil1e9/loan-default |
| Size | 255,347 loans, 18 columns, no missing values, no duplicates |
| Files used in Power BI | `data/raw/customers_raw.csv`, `data/raw/loans_raw.csv` (built with `python -m loanlens prepare`) |

### What was added to the original data

The Kaggle data looks synthetic (every category has almost exactly the same number of rows).
For this project I also added the following, mainly to have something to model and clean:

1. A random sample of 49,750 loans, to stay inside the 50,000 record limit in the PRD.
2. `CustomerID`. 92% of loans get their own customer and 8% are assigned to an existing one, which
   gives a one-to-many Customer to Loan relationship. For those 8%, the loan keeps its own loan
   details but uses the borrower details of the customer it was assigned to.
3. `IssueDate`, random dates from 2019 to 2024 with more loans in later years. The default rate
   over time is therefore flat and isn't a real trend.
4. Data quality problems (listed at the bottom of this page). Every changed value is recorded in
   `data/raw/data_quality_log.csv`.

## Customers (dimension, 45,770 rows after cleaning)

| Column | Type | Description | Cleaning |
|---|---|---|---|
| CustomerID | Text | Borrower ID, e.g. `CUST-000001`. Primary key | Duplicate rows removed |
| Age | Whole number | Age in years (18 to 69) | Values outside 18-100 set to blank |
| Income | Whole number | Annual income (15,000 to 149,999) | Missing values replaced with the median (82,860) |
| IncomeImputed | True/False | TRUE when Income was filled with the median | Added in Power Query |
| CreditScore | Whole number | Credit score (300 to 849) | Values outside 300-850 set to blank |
| MonthsEmployed | Whole number | Months in current job (0 to 119) | None |
| NumCreditLines | Whole number | Open credit lines (1 to 4) | None |
| Education | Text | High School, Bachelor's, Master's, PhD | Case and apostrophe variants fixed |
| EmploymentType | Text | Full-time, Part-time, Self-employed, Unemployed | Case, spacing and hyphen variants fixed |
| MaritalStatus | Text | Married, Single, Divorced, Unknown | Case variants fixed, missing set to Unknown |
| HasMortgage | Text | Yes / No | Y, N, 1, 0, TRUE, FALSE mapped to Yes / No |
| HasDependents | Text | Yes / No | Same as HasMortgage |

## Loans (fact, 49,750 rows after cleaning)

| Column | Type | Description | Cleaning |
|---|---|---|---|
| LoanID | Text | Loan ID. Primary key | Duplicate rows removed |
| CustomerID | Text | Borrower. Foreign key to Customers | None |
| IssueDate | Date | Date the loan was issued (2019 to 2024, synthetic) | Both `yyyy-MM-dd` and `dd/MM/yyyy` parsed |
| LoanAmount | Whole number | Amount borrowed (5,000 to 249,999) | None |
| InterestRate | Decimal | Annual interest rate in % (2 to 25) | `%` sign removed, missing replaced with the median (13.45) |
| InterestRateImputed | True/False | TRUE when InterestRate was filled with the median | Added in Power Query |
| LoanTerm | Whole number | Term in months (12, 24, 36, 48, 60) | Other values set to blank |
| DTIRatio | Decimal | Debt-to-income ratio (0.1 to 0.9) | None |
| LoanPurpose | Text | Auto, Business, Education, Home, Other, Unknown | Case variants fixed, missing set to Unknown |
| HasCoSigner | Text | Yes / No | Y, N, 1, 0 mapped to Yes / No |
| Default | Whole number | 1 = defaulted, 0 = repaid | Yes / No converted to 1 / 0 |
| LoanStatus | Text | "Default" or "Non-Default" | Added in Power Query from Default |

## Calculated columns (DAX)

| Table | Column | Values |
|---|---|---|
| Customers | Age Group | 18-25, 26-35, 36-45, 46-55, 56+, Unknown |
| Customers | Income Band | Under 40K, 40K-70K, 70K-100K, 100K+ |
| Customers | Credit Score Band | Poor (300-579), Fair (580-669), Good (670-739), Very Good (740-799), Excellent (800-850), Unknown |
| Customers | Employment Length | Under 1 yr, 1-3 yrs, 3-5 yrs, 5+ yrs |
| Loans | Interest Rate Band | Low (<8%), Moderate (8-13%), High (13-18%), Very High (18%+) |
| Loans | Loan Amount Band | Under 50K, 50K-100K, 100K-150K, 150K-200K, 200K+ |
| Loans | DTI Band | Low (<0.3), Medium (0.3-0.5), High (0.5-0.7), Very High (0.7+) |
| Loans | Monthly Payment | Monthly instalment (EMI) |
| Loans | Loan to Income | LoanAmount / annual Income |
| Loans | Payment to Income | Monthly Payment / monthly Income |

Each band column has a matching `Order` column so the bands sort in a sensible order in charts.

## Data quality issues in the raw files

| Table | Issue | Rows | Fix |
|---|---|---:|---|
| Customers | Exact duplicate rows | 458 | Remove duplicates |
| Customers | Missing Income | 687 | Median + IncomeImputed flag |
| Customers | EmploymentType variants (`full-time`, `FULL-TIME`, `full time`, extra spaces) | 1,373 | Map to the 4 standard values |
| Customers | Education variants (`Bachelors`, `master's`, `PHD`) | 915 | Map to the 4 standard values |
| Customers | MaritalStatus missing | 229 | Unknown |
| Customers | MaritalStatus case variants | 458 | Standardize |
| Customers | HasMortgage variants (`Y`, `1`, `TRUE`, ...) | 915 | Yes / No |
| Customers | HasDependents variants | 915 | Yes / No |
| Customers | Impossible Age (0, -5, 150, 200, 999) | 92 | Blank |
| Customers | Impossible CreditScore (0, 999, 1200) | 92 | Blank |
| Loans | Exact duplicate rows | 250 | Remove duplicates |
| Loans | InterestRate stored as text like `15.23%` | 1,492 | Remove `%`, convert to number |
| Loans | Missing InterestRate | 398 | Median + InterestRateImputed flag |
| Loans | LoanPurpose case variants | 1,492 | Standardize |
| Loans | LoanPurpose missing | 249 | Unknown |
| Loans | HasCoSigner variants | 995 | Yes / No |
| Loans | Default stored as `Yes`/`No` | 498 | 1 / 0 |
| Loans | Impossible LoanTerm (0, 999) | 100 | Blank |
| Loans | IssueDate written as `dd/MM/yyyy` | 2,488 | Parse both formats |
