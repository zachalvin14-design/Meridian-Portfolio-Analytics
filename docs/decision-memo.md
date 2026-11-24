# Meridian investment committee decision memo

**Decision: REJECT the current live allocation proposal. Proposed live allocation: 0%.**

The committee is asked to keep live funding at 0% at this review and allow educational validation to continue. Returns and volatility use an annual horizon. Trading costs are assessed once against modeled first-year return.

The baseline construction answers the Edition A question of whether a minimum-volatility portfolio can satisfy the modeled constraints. The Edition B assessment adds stress, point-in-time evidence gates, and a committee decision. Base-case feasibility supports continued analysis. The downside shock and missing live evidence support withholding funding. A separately identifiable Edition A submission is not linked in the manifest.

## Base case

The Lab 13 model minimizes annual volatility subject to the 6.5% gross expected-return floor, the 3% Treasury reserve floor, full investment, and long-only weights. The default solution holds 3.0% Treasury 10-year notes, 46.3% investment-grade bonds, and 50.7% global equity. Its weighted expected return is `0.030 × 4.3% + 0.463 × 5.0% + 0.507 × 8.0% = 6.50%`. Both the return and reserve floors bind.

| Portfolio | Gross expected return | Annual volatility | Modeled Sharpe at 4.5% risk-free | Active gross mandate |
| --- | ---: | ---: | ---: | --- |
| Optimized | 6.50% | 9.24% | 0.216 | PASS |
| 40% investment-grade bonds / 60% global equity | 6.80% | 10.46% | 0.220 | FAIL, no eligible Treasury reserve |

The optimized portfolio achieves lower modeled volatility and has a slightly lower modeled Sharpe ratio than the benchmark. These are model outputs. Live return, volatility, and correlation inputs, point-in-time market observations, historical estimation windows, and benchmark holdout evidence remain pending.

## Stress evidence

- **−2 percentage points to all expected returns.** The highest modeled equity return falls to 6.00%, and the best eligible Treasury return falls to 2.30%. The 3% reserve requirement caps the portfolio at `0.97 × 6.00% + 0.03 × 2.30% = 5.889%`. The 6.5% target is economically infeasible. The pre-check establishes this before SLSQP runs.
- **+2 percentage points to all expected returns.** The reoptimized portfolio still targets 6.50% gross return. Volatility falls from 9.24% to 2.99%, a change of **−6.25 pp**. One-way turnover versus the active baseline is **58.97%**. These exceed the **2.5 pp absolute volatility change** and **20% one-way turnover** thresholds. The expected-return change is zero, within its **1.5 pp** threshold. The favorable shock illustrates allocation sensitivity because higher assumed returns let the optimizer use more lower-volatility assets at the same return floor.
- **Numerical solver failure** means the optimizer returned an unsuccessful solver status after the feasibility pre-check. An invalid solver output can also fail post-solve constraint checks. The default run produced **25 verified scenarios and one economically infeasible scenario**. Each of those failure classes blocks funding under the current rules.
- **Trading costs.** The optimizer targets gross return. The fixed original mandate test deducts the one-time cost from first-year modeled return. At 50 bp per unit of turnover, the first-year net return is 6.4535%, below the original 6.5% floor.

## Decision rules

| Decision | Rule |
| --- | --- |
| Assessment Pending | Stress assessment has not run for the active inputs. Live funding stays at 0%. |
| REJECT | The baseline or any stress scenario is infeasible, the solver fails, verified weights are unavailable or breach their applicable constraints, the baseline breaches the original mandate, point-in-time integrity fails, or stress results breach a materiality threshold. Live funding stays at 0%. |
| PILOT | The stress assessment is available and there is no hard stop, but required validation evidence is missing. Continue educational validation with 0% live funding. |
| ADOPT | Evidence gates clear. Live funding stays at 0% until committee authority and a sizing limit exist. An approved funded strategy within its limit and drift tolerance may continue under ADOPT. |
| ALLOCATE | After evidence gates clear, use an approved limit for initial funding. |
| REBALANCE | After evidence gates clear, an approved, already funded strategy reaches 5 percentage points of drift or exceeds its funding cap. |

The prototype funding gate includes optimization status and material changes across every configured scenario. This includes alternative return targets and reserve floors. Those cases test how a different policy would affect the strategy, and an infeasible alternative policy does not establish infeasibility under the original mandate. A scenario's original-mandate verdict is reported for review and is not itself a hard stop in the current rule. The default REJECT already follows from the −2 pp return shock under the original settings. Before live use, the committee should decide which scenarios belong in the funding gate. Hiding the scenario details leaves the assessment and decision in effect.

## Monitoring and return to committee

Pause if modeled expected return falls below 6.5%, Treasury reserve drops below 3%, weight restrictions fail, optimization fails, or source vintages cannot be verified. The proposed monitoring rule calls for reassessment after three consecutive monthly reviews below the benchmark's rolling Sharpe. Historical benchmark data, the lookback, and the review owner still need to be documented before that rule can be used operationally. Revisit funding after the evidence, stress, mandate, and authorization gates are satisfied.
