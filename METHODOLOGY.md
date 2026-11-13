# Evidence, definitions and interpretation

Public-information cutoff: **12 November 2026**. Harmonised 13 November 2026.

The article distinguishes source observations, deterministic illustrations and the author's management proposals. Numerical implementation checks do not verify bank disclosures, estimate a probability of failure or establish a causal explanation of either institution's performance.

## Capital: reconcile definitions before comparing values

| Observation | Reference date or horizon | Interpretation |
|---|---|---|
| Solventa total regulatory capital ratio: 15.01%; cited minimum: 12% | Accounts at 31 March 2026; report published 27 April 2026 | A reported regulatory snapshot; not the author's estimate of usable capital in November |
| Fitch's March report: FCC/RWA 15.2% | Year-end 2025 | Earlier published view; its numerator cannot be equated with accounting equity without reconciliation |
| Fitch's October report: FCC/RWA 10.3%; 15.2% before intangible deductions | Both refer to year-end 2025; 10.3% also reported for June 2026 | The 490bp same-date difference identifies a definition/deduction bridge, not an economic loss over the publication interval |
| S&P reported regulatory capital: 14.4% | October 2025 actual observation quoted in December report | Distinct from S&P's own risk-adjusted capital measure |
| S&P RAC forecast: 5.0–5.5% | Next 12–24 months from December 2025 | Forecast using S&P methodology; not a contradictory observation of the same regulatory ratio |
| BCP resolution trigger: solvency below half the required minimum following statement adjustments | Board decision 2 November, announcement 3 November 2026 | Official qualitative trigger; no exact post-adjustment ratio is supplied in that announcement |

Different ratios can legitimately differ. Their spread alone does not establish inaccurate inputs, unrecognised losses, regulatory non-compliance or a causal path to resolution. Reconcile eligible capital, deductions, consolidation, reporting dates, risk weights and forecast assumptions first. Press-reported exact November ratios remain labelled unconfirmed in the article.

`analysis.py` uses synthetic capital 15 / RWA 100. For a 12% target and no other losses, the opening correction budget is 3, 1.8 or 0 at net RWA growth of 0%, 10% or 25%. These amounts are units of opening RWA, not dollars of ueno capital. The separate growth budget uses a chosen **15% management target**, capital 15 and retained earnings 1.5: capacity 10%, or 3.33% after an opening correction of 1. The two targets serve different illustrations. Net retained earnings already include applicable tax, dividends and recognised losses; do not deduct the same loss twice.

## Credit: an expected stock model, not a bank forecast

`cohort_npl()` aggregates monthly equal-principal cohorts. Lifetime default probability is spread over months using a Weibull timing distribution truncated and normalised at maturity. Defaulted principal freezes at start-of-default-month exposure and exits the gross book after the retention window. Retention is not a recovery estimate. The result is an expected NPL stock divided by expected gross principal, not an average of simulated path ratios.

The central configuration uses 36-month maturity, 6% **lifetime** PD, twelve-month default retention, Weibull shape 2 and scale 18 months. The timing density peaks near month 13. Stationary origination growth is 0%, 46.4% or 100% annually. The published 46.4% is gross-loan growth; matching its number in the synthetic origination regime does not calibrate the actual book.

There are 324 stationary parameter combinations (3 maturities × 3 PDs × 4 retention windows × 3 timing scales × 3 growth rates). These are deterministic sensitivities, not Monte Carlo draws or independent observations. Some assumptions change the direction of the growth effect.

Figure 1 changes origination growth from 46.4% to 0% at month zero. New monthly lending then continues at constant volume. Portfolio composition changes while default assumptions stay fixed. Its 61 monthly observations show a mechanism; they do not predict Nu's or ueno's trajectory or attribute an observed NPL change to seasoning.

Figure 2 solves for twelve PDs consistent with a synthetic 0.4% stock ratio under alternative timing and retention assumptions. They are neither a confidence interval nor estimates of a bank's true PD. The model omits the 60/90-day classification lag, acquired books, regulatory relief, deferrals, prepayments and partial recoveries.

S&P's December report says delinquencies on loans under regulatory transitory measures were not classified as NPLs. Solventa's March 2026 cut-off reports 0.50% delinquency plus 6.01% refinanced/restructured/renewed loans, or a combined 6.51%, versus 15.36% for the system on that broader measure. Restructured loans are not automatically non-performing, and 6.51% is not substituted for a harmonised NPL rate. These observations motivate reconciliation of vintages and classifications.

## Funding and earnings: keep stocks, flows and accounting bases separate

Ueno's 76.75% year-end 2025 and 91.9% June 2026 loans/deposits observations both come from Fitch's October report. Do not splice the March report's 71.5% year-end figure into that change. `funding_ratio()` holds loans constant and reduces deposits; it includes no replacement funding, asset sales or contractual cash-flow timing. Passing 100% is not a liquidity-failure criterion.

Nu's available funding/net credit coverage uses the issuer's management definitions; it is not compared directly with ueno's gross loans/customer deposits. Figure 3 keeps Nu's source-reported FX-neutral growth rates separate from nominal USD balances. Its group scope, geographies, loan mix and NPL definitions differ. Parent cash and capital in separate regulated entities are not assumed freely transferable. See COMPARATOR.md.

The expanded Nu discussion adds two **separate** calculations in `earnings_sensitivity.py`:

1. **IFRS frozen-quarter sensitivity:** Q3 2026 ECL expense US$1,668.5m and profit before tax US$1,350.3m. Increasing only ECL expense by US$1,350.3m eliminates quarterly PBT: a proportional increase of approximately **80.93%**. Revenue and every other expense stay fixed. This is not a dynamic stress test, a survival threshold or a capital buffer. The ECL expense flow is not the allowance stock or realised credit losses.
2. **Managerial credit-cost burden:** cost of credit / credit income is 1,035.8 / 2,489.2 = **41.61%** for Q3 2025, versus 1,788.7 / 3,795.1 = **47.13%** for Q3 2026. Both use the current release's comparable managerial presentation. No managerial amount is substituted into the IFRS sensitivity. Product, country and risk mix can change these ratios; two observations do not establish a future pricing-loss path.

## The comparative inference

Nu illustrates rapid growth alongside disclosed profits, funding and capital resources; it is not a matched control or a risk ranking. Consolidated group results and a single-bank rating commentary do not isolate the effect of intragroup revenue. S&P's earlier observation about ueno's intercompany revenue motivates questions about recurrence, counterparty dependence and stress transferability, not a claim that all of its profit was intragroup or that Nu has no comparable dependencies.

The five growth conditions are the author's proposed decision process, informed by Basel reference practices. They are not inferred management actions at either bank, institution-specific legal requirements, a validated safe-growth limit or proof that a particular stress test would have prevented resolution.

## Reproduce

```sh
python3 analysis.py
python3 validate.py
python3 comparator.py
python3 earnings_sensitivity.py
python3 validate_earnings.py
python3 build_notebook.py
# Optional plotting dependency in requirements-plot.txt
python3 plot_results.py
python3 plot_comparator.py
```

The independent ledger checks 324 stationary configurations and all 61 transition values. Earnings checks verify the break-even identity, the separation of IFRS and managerial inputs, and rejection of incompatible accounting bases. Primary sources and observation dates are linked in `data/article_sources.json` and `data/nu_sources.json`; third-party reports are not republished.
