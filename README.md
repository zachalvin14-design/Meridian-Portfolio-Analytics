AI Use: OpenAI ChatGPT and Codex assisted with coding, debugging, testing, and documentation. I retain responsibility for independently reviewing the analysis and for the investment decision. My November 23, 2026 personal dashboard review and the separate AI-assisted CSV inspection are documented in the [validation record](docs/validation-and-ai-use.md). Independent sign-off remains pending.

Educational Disclaimer: This project is for educational purposes only and is not investment advice.

# Meridian Portfolio Analytics

FIN 439 Project 2 is a Streamlit investment committee dashboard. It compares a constrained minimum-volatility portfolio with a 40% investment-grade bonds / 60% global equity benchmark, equal weight, and inverse volatility.

## Install and run

The documented environment uses Python 3.9.6. Check that `python3 --version` points to the intended interpreter before creating the environment. From the repository root, create an isolated environment, install the pinned direct dependencies, and check dependency consistency.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

Launch the app from the repository root.

```bash
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit. The app requires no API credentials or market data downloads. See the [clean-clone validation](docs/COLD_RUN.md) for the verified environment and launch results.

## Investment mandate

Minimize modeled annual volatility subject to long-only weights, full investment, a minimum modeled annual expected return of 6.5%, and at least 3% in Treasury bills and Treasury 10-year notes combined. The sidebar changes the optimization target and reserve floor. The comparison table checks the active gross mandate. Stress results also test the original 6.5% return and 3% reserve floors using first-year returns after modeled costs. The default Sharpe input is a 4.5% risk-free rate and the default dollar allocation scale is $100 million.

The committee is deciding whether to initiate a live allocation now. The default recommendation is REJECT with 0% proposed live allocation. The model uses annual return and risk assumptions, with a separate first-year net return check for modeled trading costs. The [decision memo](docs/decision-memo.md) explains the distinction between baseline portfolio construction and Edition B decision evidence.

## Dashboard workflow

The committee summary at the top shows the decision, live allocation, active floors, and primary reason. The full stress assessment informs the decision for the active inputs, including when its table and charts are hidden. An unperformed assessment displays **Assessment Pending** and **0%** live allocation. Use the compact stress table for status and mandate verdicts, and expand the full table for costs, weights, and percentage-point changes.

## Inputs and limitations

- The four asset classes, annual expected returns and volatilities (decimal fractions), and unitless correlations are embedded in `app.py` and attributed to FIN 439 Lab 13. The repository does not provide a dated Lab 13 source artifact or a distribution license for it. These are illustrative course inputs. Annual covariance is correlation multiplied by both assets' annual volatilities. The model uses these annual inputs directly.
- The optional global equity signal reads a user-supplied, source-attested CSV of index levels. The data card lists the schema and displays the file hash and selected vintages. Late publications and revisions are excluded using the offset-aware cutoff. The signal applies a fixed return adjustment based on the direction of change between two eligible index levels. Upload only authorized data and omit credentials and personal information. This repository ships with no verified point-in-time observations or external evidence for that signal.
- The separate course ETF snapshot uses a different universe and has unverified historical adjustment vintages. This app therefore reports estimation-window sensitivity as unavailable.
- The benchmark is a fixed 40% investment-grade bond and 60% global equity comparison. Equal weight divides exposure evenly, and inverse volatility normalizes the reciprocal of each sleeve's annual volatility. Sharpe is modeled gross annual expected return less the annual risk-free rate, divided by annual volatility.
- Stress tests are model sensitivity checks. Live input validation, benchmark holdout validation, full mandate review, historical window testing, and trading authorization are pending.

## Automated tests

Run the complete suite from the repository root.

```bash
.venv/bin/python -m pytest -q
```

The published results commit passed 29 tests in a fresh clone. The expanded suite includes Streamlit AppTest coverage for the default dashboard, hidden stress details, and pending assessment. See [validation and AI use](docs/validation-and-ai-use.md) for the evidence and [the decision memo](docs/decision-memo.md) for the stop decision.

## Submission records

- [Locked changed-input record](docs/LOCKED_CHANGED_INPUT.md) records the published 3%-to-10% Treasury reserve experiment. The prediction was AI-assisted, so the independently authored AI-off requirement remains unmet.
- [Submission manifest](docs/submission-manifest.md)
