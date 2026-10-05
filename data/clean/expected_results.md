# LoanLens - Expected Results

Created by `python -m loanlens clean`. Once the Power Query and DAX steps are done,
the cards and charts in Power BI should show these numbers (with no slicers applied).

## Data cleaning summary

| Check | Customers | Loans |
|---|---:|---:|
| Raw rows | 46,228 | 50,000 |
| Duplicate rows removed | 458 | 250 |
| Clean rows | 45,770 | 49,750 |
| Values imputed (median) | 687 Income | 398 InterestRate |
| Impossible values blanked | 92 Age, 92 CreditScore | 100 LoanTerm |
| 'Unknown' categories | 229 MaritalStatus | 249 LoanPurpose |
| Unparsed dates | - | 0 |

Median income used for imputation: **82,860**  
Median interest rate used for imputation: **13.450**

## KPI cards

| Measure | Expected value |
|---|---:|
| Total Loans | 49,750 |
| Total Customers | 45,770 |
| Defaulted Loans | 5,755 |
| Default Rate | 11.57% |
| Total Loan Amount | 6,352,443,263 |
| Defaulted Amount | 837,877,503 |
| Avg Loan Amount | 127,687 |
| Avg Interest Rate | 13.50% |
| Avg Credit Score | 574.9 |
| Avg Income | 82,578 |
| Avg DTI Ratio | 0.499 |

## Default rate by risk factor

| Age Group | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| 18-25 | 7,578 | 1,502 | 19.82% |
| 26-35 | 9,593 | 1,506 | 15.70% |
| 36-45 | 9,620 | 1,117 | 11.61% |
| 46-55 | 9,431 | 847 | 8.98% |
| 56+ | 13,427 | 770 | 5.73% |
| Unknown | 101 | 13 | 12.87% |

| Income Band | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Under 40K | 9,132 | 1,649 | 18.06% |
| 40K-70K | 10,709 | 1,220 | 11.39% |
| 70K-100K | 11,686 | 1,159 | 9.92% |
| 100K+ | 18,223 | 1,727 | 9.48% |

| Credit Score Band | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Poor (300-579) | 25,264 | 3,122 | 12.36% |
| Fair (580-669) | 8,155 | 936 | 11.48% |
| Good (670-739) | 6,206 | 667 | 10.75% |
| Very Good (740-799) | 5,369 | 557 | 10.37% |
| Excellent (800-850) | 4,658 | 457 | 9.81% |
| Unknown | 98 | 16 | 16.33% |

| Employment Length | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Under 1 yr | 4,918 | 833 | 16.94% |
| 1-3 yrs | 9,958 | 1,473 | 14.79% |
| 3-5 yrs | 9,876 | 1,185 | 12.00% |
| 5+ yrs | 24,998 | 2,264 | 9.06% |

| Interest Rate Band | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Low (<8%) | 12,766 | 793 | 6.21% |
| Moderate (8-13%) | 10,912 | 1,043 | 9.56% |
| High (13-18%) | 11,073 | 1,356 | 12.25% |
| Very High (18%+) | 14,999 | 2,563 | 17.09% |

| Loan Amount Band | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Under 50K | 9,112 | 744 | 8.17% |
| 50K-100K | 10,180 | 936 | 9.19% |
| 100K-150K | 10,129 | 1,082 | 10.68% |
| 150K-200K | 10,045 | 1,335 | 13.29% |
| 200K+ | 10,284 | 1,658 | 16.12% |

| DTI Band | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Low (<0.3) | 12,112 | 1,309 | 10.81% |
| Medium (0.3-0.5) | 12,561 | 1,417 | 11.28% |
| High (0.5-0.7) | 12,437 | 1,454 | 11.69% |
| Very High (0.7+) | 12,640 | 1,575 | 12.46% |

| LoanTerm | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| 12 | 10,033 | 1,164 | 11.60% |
| 24 | 9,745 | 1,136 | 11.66% |
| 36 | 9,846 | 1,120 | 11.38% |
| 48 | 9,867 | 1,132 | 11.47% |
| 60 | 10,159 | 1,187 | 11.68% |

| EmploymentType | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Full-time | 12,431 | 1,211 | 9.74% |
| Part-time | 12,331 | 1,487 | 12.06% |
| Self-employed | 12,449 | 1,407 | 11.30% |
| Unemployed | 12,539 | 1,650 | 13.16% |

| Education | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Bachelor's | 12,497 | 1,489 | 11.91% |
| High School | 12,548 | 1,656 | 13.20% |
| Master's | 12,457 | 1,345 | 10.80% |
| PhD | 12,248 | 1,265 | 10.33% |

| MaritalStatus | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Divorced | 16,354 | 2,029 | 12.41% |
| Married | 16,608 | 1,700 | 10.24% |
| Single | 16,538 | 1,993 | 12.05% |
| Unknown | 250 | 33 | 13.20% |

| LoanPurpose | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| Auto | 9,785 | 1,172 | 11.98% |
| Business | 10,008 | 1,210 | 12.09% |
| Education | 9,827 | 1,115 | 11.35% |
| Home | 10,081 | 1,037 | 10.29% |
| Other | 9,800 | 1,194 | 12.18% |
| Unknown | 249 | 27 | 10.84% |

| HasCoSigner | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| No | 24,921 | 3,141 | 12.60% |
| Yes | 24,829 | 2,614 | 10.53% |

| HasDependents | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| No | 24,848 | 3,122 | 12.56% |
| Yes | 24,902 | 2,633 | 10.57% |

| HasMortgage | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| No | 24,892 | 3,094 | 12.43% |
| Yes | 24,858 | 2,661 | 10.70% |

## Default rate by year

| Year | Loans | Defaults | Default Rate |
|---|---:|---:|---:|
| 2019 | 5,885 | 707 | 12.01% |
| 2020 | 5,409 | 633 | 11.70% |
| 2021 | 7,479 | 903 | 12.07% |
| 2022 | 9,015 | 1,004 | 11.14% |
| 2023 | 10,570 | 1,221 | 11.55% |
| 2024 | 11,392 | 1,287 | 11.30% |
