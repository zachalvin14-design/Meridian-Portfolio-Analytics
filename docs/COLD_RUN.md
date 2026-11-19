# Cold run and prediction lock

## Before the prediction is locked

Install dependencies using the repository's [README](../README.md). The app's default stress dashboard runs the 6.5% return / 10% reserve combination on startup. The full test suite also evaluates that setting. Keep both closed until the prediction commit exists on GitHub.

For a pre-lock smoke check, run the existing suite with the stress-grid test deselected.

```bash
.venv/bin/python -m pytest -q -k 'not test_stress_scenarios_and_dual_mandates'
```

## Lock the prediction remotely

1. Start from a clean baseline commit. Work AI-off and personally fill in the prediction, reasoning, timestamp with UTC offset, and prior exposure fields in [LOCKED_CHANGED_INPUT.md](LOCKED_CHANGED_INPUT.md). Keep the post-lock fields blank.
2. Review the prediction diff, commit only the record, then push `main` to the GitHub repository you created. Run each command only after the previous step succeeds.

```bash
git diff -- docs/LOCKED_CHANGED_INPUT.md
git add docs/LOCKED_CHANGED_INPUT.md
git diff --cached --name-only
git commit -m "Lock AI-off changed-input prediction"
git push -u origin main
```

3. Immediately after pushing, compare the full SHA from each command. Proceed only when both match and the commit view on GitHub contains the completed prediction.

```bash
git rev-parse HEAD
git ls-remote --exit-code origin refs/heads/main
```

## Reproduce from a clean checkout

Use a fresh clone of your GitHub repository and check out the verified prediction SHA. Replace the two angle-bracketed placeholders with the actual URL and SHA.

```bash
git clone '<YOUR_GITHUB_REPOSITORY_URL>' meridian-cold-run
cd meridian-cold-run
git checkout '<PREDICTION_COMMIT_SHA>'
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run app.py
```

Record the commit SHA, Python version, operating system, pytest result and app launch result. In the app, confirm the default inputs, an empty signal, the baseline comparison, and stress dashboard. Follow the locked record's designated run steps, then save the observed results in a separate evidence commit. Fresh-install and designated-run evidence are pending.
