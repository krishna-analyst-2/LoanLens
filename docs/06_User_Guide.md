# User Guide

How to open and explore the finished `LoanLens.pbix` report.

## Opening the report

1. Install Power BI Desktop (free from the Microsoft Store).
2. Open `LoanLens.pbix`.
3. If you get a data source error, go to **Home > Transform data > Edit parameters**, set
   `DataFolder` to the `data\raw\` folder on your machine (ending with a backslash) and click
   **Apply changes**.

## Pages

| Page | What it shows |
|---|---|
| Overview | Size of the portfolio and how many loans default |
| Risk Factors | Which borrower and loan characteristics go with higher default |
| Trends | Loan volume and default rate over time |
| Borrower Profile | How factors combine, and which groups are safest or riskiest |
| Data Quality | What was wrong with the raw data and how it was fixed |
| Loan Details | Hidden drill-through page listing individual loans |

## Using it

| To do this | Do this |
|---|---|
| Look at one year or loan purpose | Use the slicers at the top. They apply to every page. |
| Focus on one group | Click a bar. The rest of the page filters to it. Click again to clear. |
| Select several groups | Ctrl + click |
| See exact numbers | Hover over a bar to see the tooltip |
| See the loans behind a bar | Right-click the bar > Drill through > Loan Details |
| Clear all filters | Click the Reset button |
| See a chart's data as a table | Hover the visual > More options (...) > Show as a table |
| Export data | Hover the visual > More options (...) > Export data |

## Reading the numbers

- **Default Rate**: defaulted loans divided by all loans in the current selection.
- **Overall Default Rate**: the grey dashed line at 11.57%. It doesn't change with slicers, so
  it works as a benchmark.
- **Risk Index**: segment default rate divided by the overall rate. 1.0 is average, 1.5 means
  50% more likely to default, 0.5 means half as likely.
- **Unknown**: borrowers whose value was missing or impossible in the raw data. They are kept
  rather than deleted so the totals stay complete.

## Short walkthrough

1. On the Overview page, note the overall default rate of 11.57%.
2. On Risk Factors, find which chart has the biggest gap between its lowest and highest bar
   (it's age).
3. Click the 18-25 bar in the age chart and look at the interest rate chart. Young borrowers on
   rates of 18% or more default at about 29%.
4. On Borrower Profile, find the darkest cell in the Age x Income heatmap.
5. Look at the loan term chart. A flat chart is a result too: term doesn't affect default here.
6. On Trends, read the note explaining why the default rate is flat over time.
7. On Data Quality, check how many incomes were imputed and think about why the median was used
   rather than the mean.
8. Right-click any bar and drill through to the individual loans.

## Glossary

| Term | Meaning |
|---|---|
| Default | The borrower stopped repaying the loan |
| DTI ratio | Debt-to-income, the share of income already going to debt payments |
| EMI / Monthly Payment | The fixed monthly instalment that repays the loan with interest |
| Imputation | Filling a missing value with an estimate, here the median |
| Fact table | Table of events you count, here the loans |
| Dimension table | Table of descriptions you filter by, here customers and dates |
| Measure | A calculation that responds to the current filters, like Default Rate |
