# Submission manifest

| Item | Contents or status |
| --- | --- |
| [Application](../app.py) | Working Streamlit entry point. |
| Application modules | `analytics.py`, `signal_data.py`, `stress.py`, `committee.py`, and `part_two.py`. |
| [Automated tests](../tests/) | Two pytest modules. See the validation record for observed results and the prediction guard. |
| [README](../README.md) and [requirements](../requirements.txt) | Setup, launch, tests, dependencies, data sources and limitations. |
| [Decision memo](decision-memo.md) | Committee decision, allocation range, decision rules and monitoring. |
| [Validation and AI use](validation-and-ai-use.md) | Observed verification, model assumptions, limitations and independent review status. |
| [Cold run](COLD_RUN.md) | Remote lock protocol, clean-checkout steps and evidence to record. |
| [Locked record](LOCKED_CHANGED_INPUT.md) | Experiment protocol and fields awaiting the student's prediction and the designated run. |

## Pending submission evidence

- GitHub repository URL and remote-verified prediction commit SHA.
- Student-authored AI-off prediction, timestamp, and any prior exposure disclosure.
- Designated changed-input results and interpretation, committed after the prediction lock.
- Clean-clone run log and independent student verification and sign-off.
- Verified historical vintages, compatible estimation-window inputs, live-input validation, and benchmark holdout evidence.

Git was initialized locally for Part 3. No commit, remote configuration, or push was performed during preparation.
