# Locked changed-input record

**Status: Awaiting the student's AI-off prediction and verified remote prediction commit.**

The proposed change is a single-input controlled experiment using the existing Lab 13 model. No Part 3 changed-input run or results have been recorded. Earlier Part 2 stress testing included this same constraint combination. Keep any previous scenario output out of view while writing the prediction, and disclose any prior exposure if it occurred. The remote lock establishes the order of this prediction and the designated run.

## Complete personally before any designated run

| Field | Record |
| --- | --- |
| Original input | Minimum Treasury reserve of 3%. |
| Changed input | Minimum Treasury reserve of 10%. |
| Held fixed | Expected annual return target of 6.5%, all four Lab 13 assets and estimates, baseline covariance, fully invested long-only constraints, no uploaded signal, 4.5% risk-free rate, and $100 million display value. |
| My AI-off prediction | [Student writes the prediction here before running or viewing results.] |
| Reasoning for my prediction | [Student explains the predicted direction and any expected trade-offs, without AI or model output.] |
| Prediction timestamp | [Student enters the actual local date and time with UTC offset.] |
| Prior exposure to the scenario output | [Student discloses any exposure, or records none if accurate.] |

Commit this prediction section and push it to GitHub before starting the designated run. Compare the full local commit hash with the hash returned from GitHub for the pushed branch. Preserve the prediction commit. Its own hash goes in the evidence section in a later commit because inserting it into the prediction commit would change that commit's hash. See [COLD_RUN.md](COLD_RUN.md) for commands.

## Complete only after verifying the remote prediction commit

Open the app with the default inputs and no signal upload. Turn off **Run all stress scenarios** to isolate the controlled comparison. Record the optimized baseline allocation and metrics at 3%. Change only **Minimum Treasury Reserve** to 10% and record the optimized allocation, expected return, annual volatility, Treasury reserve, and mandate verdict. Record any displayed infeasibility or solver error if applicable. Report weight and metric differences in percentage points.

| Field | Record |
| --- | --- |
| Git commit hash | [Full SHA of the remote-verified prediction commit.] |
| Actual observed result | [Baseline and changed-input outputs and the run evidence.] |
| Difference between prediction and result | [Compare actual results with the locked prediction.] |
| Interpretation | [Explain which results support or challenge the prediction and their implications.] |

Commit the run evidence separately, leaving the original prediction commit intact.
