# Clean-clone validation

## Observed run

| Check | Result |
| --- | --- |
| Source | GitHub repository `zachalvin14-design/Meridian-Portfolio-Analytics`, cloned into a new temporary directory outside the working project |
| Cloned HEAD | `f99651ddddbd6ba44b2326da2c86092a61a5d36b`, matched the published changed-input results commit |
| Operating system | macOS 26.6.2, build 25G83, arm64 |
| Interpreter | Python 3.9.6 in a fresh `.venv` |
| Dependency installation | `pip install -r requirements.txt` succeeded; `pip check` reported `No broken requirements found.` |
| Complete test suite | `29 passed in 14.37s` with no deselections or prediction guard |
| Streamlit 1.50.0 launch | Server started headless on loopback. The root page returned HTTP 200 and the health endpoint returned HTTP 200 with body `ok`. |
| Default dashboard | A separate Streamlit AppTest session ran with zero Python exceptions. The default 6.5% return / 3% reserve settings produced four portfolio comparison rows, five Plotly charts, and 26 stress scenarios. |
| Stress and committee results | Twenty-five stress scenarios had verified weights. The −2 percentage point expected-return shock was infeasible, as modeled. The default committee decision was REJECT with 0% proposed live allocation. |

The dashboard check used Streamlit's test session to inspect the tables, headings, metrics, and chart elements. The HTTP check separately verified the running server. AppTest emitted its bare-mode context warning and completed successfully. This run is automated verification, with independent student review still pending.

## Reproduce the verified run

Start from a directory outside your working repository and use Python 3.9.6 to reproduce the documented environment.

```bash
git clone https://github.com/zachalvin14-design/Meridian-Portfolio-Analytics.git meridian-cold-run
cd meridian-cold-run
git checkout --detach f99651ddddbd6ba44b2326da2c86092a61a5d36b
git rev-parse HEAD
python3 -V
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit and verify the default mandate, portfolio comparison, stress table, and committee decision. [The locked record](LOCKED_CHANGED_INPUT.md) contains the controlled 3%-to-10% experiment results and comparison.

## Published experiment history

Local and GitHub `main` both pointed to prediction commit `484c36ddc85147c15130136491c730ab3d731486` before the designated run. The results were then recorded separately in `f99651ddddbd6ba44b2326da2c86092a61a5d36b` and verified on GitHub. The prediction is explicitly AI-assisted and the record discloses earlier Part 2 execution of the same scenario. The independently authored AI-off requirement remains unmet.
