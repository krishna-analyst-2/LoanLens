# Insights Report

Covers FR7 (summary statistics and key insights). All numbers come from the cleaned data
(49,750 loans, 45,770 customers) and match `data/clean/expected_results.md`.

## Portfolio summary

| Metric | Value |
|---|---:|
| Loans | 49,750 |
| Customers | 45,770 |
| Total lent | 6.35 billion |
| Defaulted loans | 5,755 |
| Default rate | 11.57% |
| Amount in defaulted loans | 838 million (13.2% of the total) |

Loans that default tend to be larger than average: 11.6% of loans default, but they account for
13.2% of the money lent.

## Risk factors, strongest first

| # | Factor | Lowest risk | Highest risk | Ratio |
|---|---|---|---|---|
| 1 | Age | 56+: 5.7% | 18-25: 19.8% | 3.5x |
| 2 | Interest rate | under 8%: 6.2% | 18% and above: 17.1% | 2.8x |
| 3 | Loan amount | under 50K: 8.2% | 200K and above: 16.1% | 2.0x |
| 4 | Income | 100K and above: 9.5% | under 40K: 18.1% | 1.9x |
| 5 | Employment length | 5+ years: 9.1% | under 1 year: 16.9% | 1.9x |
| 6 | Employment type | Full-time: 9.7% | Unemployed: 13.2% | 1.4x |
| 7 | Education | PhD: 10.3% | High School: 13.2% | 1.3x |
| 8 | Credit score | Excellent: 9.8% | Poor: 12.4% | 1.3x |
| 9 | DTI ratio | under 0.3: 10.8% | 0.7 and above: 12.5% | 1.2x |

**Age** is the clearest factor. The default rate falls with every age band, from 19.8% for
18-25 year olds to 5.7% for borrowers aged 56 and over. Young borrowers have a risk index of
1.71, meaning they default 71% more often than the average borrower.

**Interest rate** comes next. Loans above 18% default at 17.1%, nearly three times the rate of
loans under 8%. Some of this is circular, since lenders charge riskier borrowers more, but it
still makes the rate a useful warning sign.

**Income** behaves more like a threshold than a slope. Borrowers earning under 40K default at
18.1%, while everyone above that sits between 9.5% and 11.4%.

**Loan amount and employment length** both add risk steadily. Default goes from 8.2% for loans
under 50K to 16.1% for loans of 200K or more, and from 9.1% for people employed 5+ years to
16.9% for those in their first year.

## Risk factors stack up

The heatmaps on the Borrower Profile page show that the factors add to each other:

| Segment | Loans | Default rate |
|---|---:|---:|
| Age 18-25, income under 40K, interest rate 18%+ | 404 | 38.9% |
| Age 18-25, income under 40K | 1,357 | 29.3% |
| Whole portfolio | 49,750 | 11.6% |
| Age 56+, income 100K+, interest rate under 8% | 1,258 | 1.2% |

The riskiest segment defaults about 30 times as often as the safest one.

## Factors linked to lower risk

Each of these comes with a default rate about 2 percentage points lower:

| Factor | Yes | No |
|---|---:|---:|
| Has a co-signer | 10.5% | 12.6% |
| Has dependents | 10.6% | 12.6% |
| Has a mortgage | 10.7% | 12.4% |

Married borrowers default at 10.2%, compared with 12.1% for single and 12.4% for divorced
borrowers.

## Things that turned out not to matter

- **Loan term.** Every term from 12 to 60 months defaults at 11.4-11.7%. The PRD listed term as a
  likely risk factor, but the data doesn't support that.
- **Credit score** matters less than expected. Excellent scores default only 2.6 points less
  than poor ones. Also, 51% of borrowers end up in the Poor band because scores in this dataset
  are spread evenly between 300 and 849, which isn't how real credit scores are distributed.
- **Loan purpose** makes little difference. Home loans are lowest at 10.3%, the rest are between
  11.4% and 12.2%.
- **Default rate over time** is flat at 11.1-12.1% per year. This is expected because IssueDate
  was generated randomly. The growth in volume (5,885 loans in 2019 to 11,392 in 2024) was also
  built in.

## Recommendations

1. Flag high-risk combinations when people apply. Applicants under 26 with income below 40K
   asking for high-rate loans default almost 39% of the time.
2. Ask for a co-signer more often for young or low-income applicants.
3. Limit loan size relative to income for applicants who have been employed less than a year.
4. Don't rely on credit score alone. In this data, age, income and employment history separate
   good and bad borrowers better.

## Limitations

- The Kaggle data looks synthetic (balanced categories, evenly spread numbers), so these results
  are a learning exercise rather than evidence about real lending.
- IssueDate and CustomerID were added for this project, so time trends don't mean anything.
- Everything here is correlation. To measure the effect of one factor while holding the others
  constant, you would need a model such as logistic regression.
