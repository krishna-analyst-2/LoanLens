# Power Query Cleaning Guide

Covers FR1 (import) and FR2 (cleaning).

The goal is to load the two raw CSV files, fix the problems listed in the
[data dictionary](01_Data_Dictionary.md), and end up with two clean tables:
`Customers` with 45,770 rows and `Loans` with 49,750 rows.

There are two ways to do it:

- **Option A:** paste the finished M scripts from `powerquery/`. Quick, and the results match
  `expected_results.md`.
- **Option B:** build the same steps by clicking through the Power Query UI. Slower, but you
  learn more. You can also do B first and then compare it with A.

## Setup

1. Check that `data/raw/customers_raw.csv` and `data/raw/loans_raw.csv` exist.
2. Open Power BI Desktop, start a blank report and save it as `LoanLens.pbix`.
3. Open Power Query: **Home > Transform data**.
4. Create a parameter for the folder: **Home > Manage Parameters > New Parameter**
   - Name: `DataFolder`
   - Type: Text
   - Current Value: the full path to `data\raw\`, for example
     `C:\krishna\College\intership\euron_1\data\raw\`. It has to end with a backslash.

## Option A: paste the scripts

For `powerquery/01_Customers.m` and then `powerquery/02_Loans.m`:

1. **Home > New Source > Blank Query**
2. Rename the query to `Customers` (or `Loans`).
3. **Home > Advanced Editor**, replace everything with the contents of the file, click **Done**.
4. Check the preview for errors.

Then **Home > Close & Apply**.

## Option B: step by step in the UI

### Customers

1. **Home > New Source > Text/CSV**, pick `customers_raw.csv`, click **Transform Data**. Rename the
   query to `Customers`.
2. Delete the automatic **Changed Type** step in Applied Steps. Setting types this early turns
   values like `TRUE` or `Y` into errors, so set them after the text is cleaned.
3. Select all columns (Ctrl+A) and use **Transform > Format > Trim** to remove extra spaces.
4. With all columns still selected, use **Replace Values**: leave "Value to find" empty, set
   "Replace with" to `null`, and tick **Match entire cell contents** under Advanced options.
   Empty cells are now proper nulls.
5. **Home > Remove Rows > Remove Duplicates** (all columns selected). Rows drop from 46,228 to
   45,770.
6. EmploymentType: **Format > lowercase**, replace a space with `-`, then replace `full-time`
   with `Full-time`, `part-time` with `Part-time`, `self-employed` with `Self-employed` and
   `unemployed` with `Unemployed` (match entire cell contents each time).
7. Education: lowercase, remove the `'`, then map `bachelors`, `masters`, `high school` and
   `phd` to `Bachelor's`, `Master's`, `High School` and `PhD`.
8. MaritalStatus: **Format > Capitalize Each Word**, then replace `null` with `Unknown`.
9. HasMortgage and HasDependents: add a Conditional Column that returns `Yes` for
   yes / y / true / 1, `No` for no / n / false / 0 and `Unknown` otherwise. Remove the original
   column and rename the new one. The `ToYesNo` function in the script does the same thing.
10. Set Age, Income, CreditScore, MonthsEmployed and NumCreditLines to Whole Number.
11. Age: replace values below 18 or above 100 with null (Conditional Column, then swap it in).
    Do the same for CreditScore outside 300-850.
12. Add a Custom Column `IncomeImputed` with the formula `[Income] = null` and type True/False.
13. Replace null Income with the median, 82,860. (In the UI you can find it with
    **Transform > Statistics > Median** on a copy of the query; the script uses `List.Median`.)

### Loans

1. Import `loans_raw.csv` the same way and rename it to `Loans`. Delete the Changed Type step,
   trim, turn empty cells into null and remove duplicates. Rows drop from 50,000 to 49,750.
2. InterestRate: replace `%` with nothing, then change the type to Decimal Number. If your
   Windows settings use a comma as the decimal separator, use **Change Type > Using Locale >
   English (United States)**.
3. Add `InterestRateImputed` = `[InterestRate] = null`, then replace null InterestRate with the
   median, 13.45.
4. LoanPurpose: lowercase, Capitalize Each Word, replace null with `Unknown`.
5. HasCoSigner: same Yes / No conversion as for Customers.
6. Default: replace `Yes` with `1` and `No` with `0`, then set it to Whole Number.
7. IssueDate: add a Custom Column

   ```
   try Date.FromText([IssueDate], [Format="yyyy-MM-dd"])
   otherwise Date.FromText([IssueDate], [Format="dd/MM/yyyy"])
   ```

   set it to Date, remove the old column and rename the new one. 2,488 dates are written
   day-first, and a plain type change would either fail on them or swap day and month.
8. LoanAmount and LoanTerm to Whole Number, DTIRatio to Decimal Number.
9. LoanTerm: keep 12, 24, 36, 48 and 60, set anything else to null.
10. Add a Conditional Column `LoanStatus`: `Default` when Default = 1, otherwise `Non-Default`.

Then **Home > Close & Apply**.

## Checking the result

| Check | Expected |
|---|---|
| Customers row count | 45,770 |
| Loans row count | 49,750 |
| Errors (View > Column quality) | 0% in every column |
| Distinct EmploymentType values (View > Column distribution) | 4 |
| Loans with a null IssueDate | 0 |

The full list of expected numbers is in `data/clean/expected_results.md`.

Column quality and column profiling only look at the first 1,000 rows by default. Click the
status bar at the bottom and switch to "Column profiling based on entire data set" to see
everything. Screenshots of these views before and after cleaning are useful for the write-up.

## Common problems

| Problem | Fix |
|---|---|
| `DataSource.NotFound` | The DataFolder path is wrong or doesn't end with a backslash. |
| "We couldn't convert to Number" | A Changed Type step runs before the cleaning. Move it after. |
| InterestRate shows 1523 instead of 15.23 | Locale issue. Change the type using locale English (United States). |
| Duplicates still there | Remove Duplicates has to run on all columns, after trimming. |
