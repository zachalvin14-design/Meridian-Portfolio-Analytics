# Submission manifest

[Meridian Portfolio Analytics on GitHub](https://github.com/zachalvin14-design/Meridian-Portfolio-Analytics)

| Item | Contents or status |
| --- | --- |
| [Application](../app.py) | Streamlit entry point verified from a fresh GitHub clone. |
| Application modules | `analytics.py`, `signal_data.py`, `stress.py`, `committee.py`, and `part_two.py`. |
| [Automated tests](../tests/) | Complete suite passed: 29 tests in 14.37s. |
| [README](../README.md) and [requirements](../requirements.txt) | Setup, launch, tests, dependencies, data sources and limitations. |
| [Decision memo](decision-memo.md) | Committee decision, allocation range, decision rules and monitoring. |
| [Validation and AI use](validation-and-ai-use.md) | Observed verification, model assumptions, limitations and independent review status. |
| [Clean-clone evidence](COLD_RUN.md) | Fresh install, test results, HTTP launch checks and Streamlit AppTest results. |
| [Locked record](LOCKED_CHANGED_INPUT.md) | Published AI-assisted prediction, prior-testing disclosure, and the designated 3%-to-10% reserve experiment and comparison. |

## Verified publication

- Prediction commit: `484c36ddc85147c15130136491c730ab3d731486`.
- Results commit and clean-clone HEAD: `f99651ddddbd6ba44b2326da2c86092a61a5d36b`.

## Remaining gaps

- The recorded prediction is AI-assisted. An independently authored AI-off prediction was not recorded before the experiment.
- Independent student review and sign-off have not been documented.
- Verified point-in-time market observations and vintages, compatible estimation-window inputs, live-input and full mandate validation, and benchmark holdout evidence are unavailable or pending. The application continues to recommend 0% live allocation.
