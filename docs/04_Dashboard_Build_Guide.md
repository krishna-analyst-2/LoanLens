# Dashboard Build Guide

Covers FR4 (risk factors), FR5 (trends), FR6 (filters), FR7 (summary statistics) and FR8
(interactivity).

## Before starting

1. Load the theme: **View > Themes > Browse for themes**, pick `theme/LoanLens_theme.json`.
   Dark blue is used for volumes, red for default risk.
2. Page size: **Format page > Canvas settings > 16:9**.
3. Every page uses the same layout: a title bar with slicers at the top, a row of KPI cards, then
   two rows of two visuals.

Whenever a chart shows Default Rate by category, add the Overall Default Rate (11.57%) as a line
so it's easy to see which groups are above or below average.

## Page 1: Overview

| Visual | Fields | Notes |
|---|---|---|
| 6 cards | Total Loans, Total Customers, Total Loan Amount, Defaulted Loans, Default Rate, Defaulted Amount | Show amounts in millions. Default Rate in red. |
| Donut | Legend `Loans[LoanStatus]`, values Total Loans | Roughly 88% / 12% |
| Line chart | X `Date[Year Quarter]`, Y Default Rate and Overall Default Rate | Overall as a grey dashed line |
| Bar chart | Y `Loans[LoanPurpose]`, X Default Rate | Sorted descending |
| Card | Default Rate Headline | Sentence that updates with the slicers |
| Slicers | `Date[Year]`, `Loans[LoanPurpose]`, `Customers[EmploymentType]`, `Customers[Education]` | Dropdowns to save space |

## Page 2: Risk Factors

Six "Line and clustered column" charts in a 3 x 2 grid. In each chart, put the band column on
the X axis, Default Rate as the column (red) and Overall Default Rate as the line (grey, dashed).
Turn data labels on with format 0.0%.

| Chart | X axis | Expected pattern |
|---|---|---|
| Age | `Customers[Age Group]` | 19.8% for 18-25 down to 5.7% for 56+. Strongest factor. |
| Interest rate | `Loans[Interest Rate Band]` | 6.2% up to 17.1% |
| Income | `Customers[Income Band]` | 18.1% under 40K, 9-11% for the rest |
| Employment length | `Customers[Employment Length]` | 16.9% under 1 year, 9.1% at 5+ years |
| Loan amount | `Loans[Loan Amount Band]` | 8.2% up to 16.1% |
| Credit score | `Customers[Credit Score Band]` | 12.4% down to 9.8%, weaker than expected |

On the side, add a table with `Customers[Age Group]`, Total Loans, Default Rate and Risk Index,
with a background colour rule on Risk Index (red above 1, green below 1).

## Page 3: Trends

| Visual | Fields | Notes |
|---|---|---|
| Line chart | X `Date[Year Month]`, Y Default Rate and Default Rate 12M Rolling | Monthly values are noisy, the rolling line smooths them |
| Column chart | X `Date[Year]`, Y Total Loans, tooltip Loan Growth YoY % | Volume grows every year except 2020 |
| Line chart | X `Date[Year]`, Y Default Rate, legend `Customers[Age Group]` | Shows the age gap stays the same over time |
| Card | Default Rate vs Prior Year | Text version of Default Rate YoY Change. Pick a year in the slicer to compare it with the year before |
| Text box | Note that IssueDate is synthetic, so the flat default rate is expected | |

## Page 4: Borrower Profile

| Visual | Fields | Notes |
|---|---|---|
| Matrix | Rows `Customers[Age Group]`, columns `Customers[Income Band]`, values Default Rate | Background colour gradient from white to red. 18-25 with income under 40K is about 29%. |
| Matrix | Rows `Customers[Education]`, columns `Customers[EmploymentType]`, values Default Rate | Same formatting |
| Bar chart | `Customers[EmploymentType]` by Default Rate | |
| 3 column charts | `Loans[HasCoSigner]`, `Customers[HasDependents]`, `Customers[HasMortgage]` by Default Rate | The "Yes" group is about 2 points lower each time |
| Column chart | `Loans[LoanTerm]` by Default Rate | Flat, term makes no difference |

## Page 5: Data Quality

| Visual | Fields |
|---|---|
| Cards | Imputed Income Count (687), Imputed Interest Rate Count (398), Unknown Age Count (92), Unknown Credit Score Count (92), Unknown Loan Term Count (100) |
| Table | Raw rows, duplicates removed and clean rows, typed in with Enter data from `expected_results.md` |
| Donut | `Loans[InterestRateImputed]` by Total Loans |
| Text box | Short list of the problems found and how they were fixed (from the data dictionary) |

## Page 6: Loan Details (drill-through)

1. Add a table with LoanID, CustomerID, IssueDate, LoanAmount, InterestRate, LoanTerm,
   Monthly Payment, Payment to Income and LoanStatus.
2. Under **Visualizations > Build > Drill through**, add `Customers[Age Group]`,
   `Loans[Interest Rate Band]` and `Loans[LoanPurpose]`.
3. Right-clicking a bar on pages 2-4 now offers **Drill through > Loan Details**.
4. Hide the page (right-click the tab > Hide page). Power BI adds a back button automatically.

## Interactivity checklist

- [ ] Sync slicers across all pages (**View > Sync slicers**)
- [ ] Set Edit interactions so clicking a bar filters the other visuals instead of highlighting
- [ ] Page navigator buttons at the top of every page (**Insert > Buttons > Navigator**)
- [ ] Total Loans and Risk Index in the tooltips of every risk chart
- [ ] A reset button that clears all slicers (bookmark + button)
- [ ] Alt text on every visual (**Format > General > Alt text**)
- [ ] Performance Analyzer: every visual loads in under a second (NFR3)

## Performance results (NFR3)

Recorded with Performance Analyzer in Power BI Desktop on all five report pages (export saved as
`docs/performance_analyzer.json`):

| Step | Events | Slowest | Average |
|---|---:|---:|---:|
| DAX query | 35 | 584 ms | 169 ms |
| Visual render | 72 | 619 ms | 249 ms |

Every visual loads in under a second. The larger totals in the Performance Analyzer pane (around
1 s) are mostly "Other", which is time a visual spends waiting for the visuals before it.

## Export

- Save the `.pbix`.
- **File > Export > Export to PDF** for the PDF version.
- Optionally publish to the Power BI Service to share a link.
