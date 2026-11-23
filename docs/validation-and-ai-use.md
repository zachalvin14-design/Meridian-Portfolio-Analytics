# Validation and AI use

## Observed verification

| Check | Actual outcome |
| --- | --- |
| Part 2 full pytest suite | 29 passed. |
| Part 3 post-edit pytest rerun | 29 passed in 0.44 seconds. A temporary in-process guard suppressed the single stress solver call at the locked 6.5% return and 10% reserve setting. The test files and application were unchanged. |
| Part 3 pre-lock pytest command | 28 passed, 1 stress-grid test deselected. |
| Part 2 Streamlit checks | The app launched. Automated Streamlit sessions exercised the charts, scenario filtering, default stop decision, disabled stress suite, and an infeasible baseline. |
| Clean clone and fresh install | GitHub clone matched `f99651ddddbd6ba44b2326da2c86092a61a5d36b`. macOS 26.6.2 (25G83), arm64, Python 3.9.6. All requirements installed in a fresh environment and pip reported no broken requirements. |
| Clean-clone full pytest suite | `29 passed in 14.37s` with no deselections or guard. |
| Clean-clone Streamlit launch | Streamlit 1.50.0 served the root page and health endpoint with HTTP 200. AppTest found zero Python exceptions, four portfolio comparison rows, five Plotly charts, 26 stress scenarios (25 verified and one modeled infeasible), and REJECT with 0% live allocation. See [the clean-clone run](COLD_RUN.md). |
| Changed-input experiment | Remote prediction SHA verified before the designated run. Both constrained optimizations passed the implemented checks. Results were published separately in `f99651ddddbd6ba44b2326da2c86092a61a5d36b`. See [the locked record](LOCKED_CHANGED_INPUT.md). |
| Dashboard decision-control update | 32 pytest cases passed in the local course environment, including three Streamlit AppTest cases. The default shows REJECT and 0% with 26 scenarios. Hiding stress details preserves the decision; an unperformed assessment shows Assessment Pending and 0%. Pip reported no broken requirements. |
| Independent student review | Pending documentation by the student. No independent sign-off is claimed. |

The original 29 cases cover return and volatility calculations, valid weight totals and bounds, return and Treasury reserve compliance, infeasibility screening, rejection of invalid solver output, scenario math and separate mandate checks, one-way turnover costs, point-in-time signal selection and impact, and committee decisions.

## Model and numerical checks

SciPy SLSQP minimizes variance using its analytic gradient. Minimizing variance yields the same portfolio as minimizing volatility. The model checks the maximum achievable return before calling the solver. It accepts final weights only when finite and compliant with the budget, long-only bounds, return floor, and Treasury reserve floor. Absolute weight tolerances are 1e-8 for budget, bounds, and reserve; the absolute return tolerance is 1e-10 in decimal return units. The solver uses `ftol=1e-12` and up to 3,000 iterations.

## Point-in-time checks and scope

The signal requires source, evidence, observation date, publication and availability timestamps, and finite positive index levels. It checks chronological order and rejects ambiguous duplicate vintages. It excludes publications and vintages after the offset-aware cutoff and uses the most recent eligible vintage for each of the two latest eligible observation dates. Source confirmation is user-attested. The app ships with no verified historical observations or evidence for live allocation. The test fixtures are synthetic and confined to the test suite.

## Stress suite

| Input | Scenarios |
| --- | --- |
| Expected returns | Uniform changes of −2, −1, +1 and +2 percentage points |
| Volatility | Relative changes of −20%, −10%, +10% and +20% |
| Correlation | 75/25 blends with an identity or all-ones matrix, preserving positive semidefiniteness |
| Transaction costs | 0, 10, 25 and 50 bp applied once to one-way turnover from the benchmark |
| Constraints | All 12 pairings of 3%, 5%, 10%, 20% reserve and 5.5%, 6.5%, 7.0% return |
| Historical estimation window | Unavailable; compatible source-verified dated returns are missing |

Scenario optimization uses gross return. Original mandate checks use each scenario's modeled return after any first-year cost and the fixed 6.5% and 3% floors. The results depend on training inputs and do not establish realized performance. Transaction costs are a simple sensitivity model that omits execution effects. Full live mandate review, dated-window sensitivity, and benchmark holdout evidence are pending. The [decision memo](decision-memo.md) documents REJECT and the 0% live range.

## AI assistance and independent review

ChatGPT and Codex assisted with coding, debugging, tests, and documentation. AI-assisted verification includes the test and Streamlit runs above. The published prediction was AI-assisted, and the historical record discloses that prior Part 2 testing executed the same scenario. The independently authored AI-off prediction requirement remains unmet. The student should record their own completed checks and evidence here, including which outputs they reproduced, what inputs and commit they used, and any discrepancies. Leave sign-off pending until those checks occur.
