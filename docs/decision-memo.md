# Meridian investment committee decision memo

**Decision: REJECT the current live allocation proposal. Proposed live allocation: 0%.**

The current baseline is a training model that minimizes annual volatility under the 6.5% return target and 3% Treasury reserve floor. The default baseline passed the implemented mandate checks in Part 2. The full default stress run still triggered the process stop. A uniform 2 percentage point reduction in the modeled expected returns made the target infeasible at the required reserve. The current signal has no supplied source observations, and the live return, volatility and correlation inputs, historical estimation windows, and benchmark holdout remain unverified.

## Decision rules

| Decision | Rule |
| --- | --- |
| REJECT | Baseline or scenario optimization fails, returned weights fail applicable checks, the baseline fails the original mandate, point-in-time integrity fails, or stress results breach a materiality threshold. Live funding stays at 0%. |
| PILOT | No hard stop is identified and required evidence or full stress results are pending. Continue educational validation with 0% live funding. |
| ADOPT | Evidence gates clear. Live funding stays at 0% until committee authority and a sizing limit exist. An approved funded strategy within its limit and drift tolerance may continue under ADOPT. |
| ALLOCATE | After evidence gates clear, use an approved limit for initial funding. |
| REBALANCE | After evidence gates clear, an approved, already funded strategy reaches 5 percentage points of drift or exceeds its funding cap. |

## Monitoring and return to committee

Pause if the modeled expected return falls below 6.5%, Treasury reserve drops below 3%, weight restrictions fail, optimization fails, or the source vintages cannot be verified. The prototype flags changes greater than 20% one-way turnover, 1.5 percentage points of annual expected return, or 2.5 percentage points of annual volatility relative to the baseline. Reassess after three consecutive monthly reviews below the benchmark's rolling Sharpe. Revisit funding only after the evidence, stress, mandate, and authorization gates are satisfied.
