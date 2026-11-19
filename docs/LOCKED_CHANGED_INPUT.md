# Locked Changed-Input Record
## FIN 439 — Project 2: Meridian Portfolio Analytics

**Student:** Zachary Alvin  
**GitHub Repository:** https://github.com/zachalvin14-design/Meridian-Portfolio-Analytics  
**Experiment:** Treasury Reserve Constraint Sensitivity  
**Status:** AI-assisted prediction prepared; experiment results pending

### 1. Purpose

The purpose of this experiment is to evaluate how increasing the minimum Treasury reserve requirement affects the allocation, expected return, volatility, and feasibility of the Meridian minimum-volatility portfolio.

The experiment tests whether the optimization system responds consistently to a change in investment constraints while maintaining the original expected-return objective.

### 2. Original Investment Mandate

The Meridian Portfolio Analytics application minimizes annualized portfolio volatility subject to an expected annual return of at least 6.5%, a minimum 3% allocation to eligible Treasury assets, full investment, and no short selling.

The investment universe consists of four asset classes:

| Asset Class | Expected Annual Return | Annual Volatility |
|---|---:|---:|
| Treasury bills | 3.5% | 0.5% |
| Treasury 10-year note | 4.3% | 7.0% |
| Investment-grade bonds | 5.0% | 6.0% |
| Global equity | 8.0% | 16.0% |

All assumptions are taken from the course-authored Lab 13 training inputs.

### 3. Changed Input

The minimum eligible Treasury reserve requirement will increase from 3% to 10%.

The expected-return objective remains 6.5%. The investment universe, expected returns, covariance matrix, long-only restriction, and fully invested requirement remain unchanged.

### 4. AI-Assisted Prediction — Before Experiment

**Predicted change in portfolio weights:**

I predict that increasing the minimum Treasury reserve from 3% to 10% will increase the portfolio's allocation to Treasury assets if the original optimized reserve allocation is below 10%.

Because Treasury bills and Treasury notes have lower expected returns than global equity, the optimizer may need to maintain or increase global equity exposure relative to other assets to satisfy the 6.5% expected-return requirement.

I expect the optimizer to reduce allocations to assets that provide a less attractive combination of expected return, volatility, and diversification under the tighter reserve requirement.

**Predicted change in portfolio volatility:**

I predict that the optimized portfolio's minimum achievable volatility will either increase or remain unchanged.

A tighter constraint reduces the feasible investment opportunity set. Therefore, the minimum possible volatility cannot decrease when all other assumptions remain constant.

If the original optimized portfolio already holds at least 10% in eligible Treasury assets, the new constraint may have no effect.

**Predicted feasibility:**

I predict that the revised portfolio will remain feasible.

The 6.5% expected-return requirement can theoretically be satisfied with a 10% Treasury allocation and sufficient global equity exposure under the course assumptions.

However, feasibility does not guarantee that the resulting portfolio will be attractive from a risk-adjusted performance perspective.

**Reasoning:**

Portfolio optimization involves balancing expected return, volatility, diversification, and investment restrictions.

Increasing the minimum Treasury reserve requirement reduces the optimizer's flexibility. Treasury assets generally offer lower expected returns than global equity in the Lab 13 assumptions, so the optimizer must balance the reserve requirement against the 6.5% return objective.

The direction of individual asset-weight changes depends on the covariance matrix and whether the original reserve constraint is binding.

The primary expectation is that the revised portfolio will remain feasible, while its minimum achievable volatility cannot be lower than that of the original optimization.

### 5. Prediction Lock and Disclosure

**Prediction prepared:** November 19, 2026

**Prediction authoring:** OpenAI ChatGPT assisted with preparing the prediction and reasoning.

**Student responsible for reviewing and approving the prediction:** Zachary Alvin

**Prediction commit SHA:** To be recorded after committing to GitHub.

**Prior exposure disclosure:**

Earlier Part 2 automated testing included the 6.5% expected-return and 10% Treasury reserve scenario. This prior execution is disclosed for transparency. The numerical results of that earlier run have not been provided in this record.

This prediction is AI-assisted and must not be represented as an independently authored AI-off prediction.

### 6. Actual Experiment Results

**Status:** Not yet recorded.

The following fields must be completed using actual application output after the prediction has been committed.

**Treasury bills allocation:** Pending

**Treasury 10-year note allocation:** Pending

**Investment-grade bond allocation:** Pending

**Global equity allocation:** Pending

**Expected annual return:** Pending

**Annualized portfolio volatility:** Pending

**Total eligible Treasury reserve:** Pending

**Optimization status:** Pending

**Mandate compliance:** Pending

### 7. Prediction Versus Actual Results

To be completed after the changed-input experiment.

The comparison will evaluate whether the predicted direction of portfolio-weight changes, volatility response, and feasibility matched the observed results.

Any differences will be explained using the optimization constraints, expected-return assumptions, and covariance structure.

### 8. Investment Committee Implications

The experiment evaluates the sensitivity of the Meridian portfolio to changes in reserve requirements.

Even if the optimization remains feasible, the committee should not automatically approve live investment.

The process must demonstrate reliable data, reproducible calculations, stable portfolio allocations, acceptable transaction costs, and compliance with the full investment mandate.

The current provisional recommendation remains REJECT with 0% live allocation until the required validation is complete.

### 9. AI Use and Educational Disclaimer

OpenAI ChatGPT and Codex assisted with Python programming, application development, debugging, testing, documentation, and the prediction in this record.

The student retains responsibility for reviewing the analysis and making the final investment decision.

This project is for educational purposes only and does not constitute investment advice.
