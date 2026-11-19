import numpy as np
import pandas as pd
import pytest

from analytics import Optimization, optimize
from committee import recommend
from signal_data import evaluate_signal
from stress import instability_reasons

CUTOFF = "2025-02-01T17:00:00-05:00"


@pytest.fixture
def records():
    # Synthetic test fixtures only. The app ships without dated signal observations.
    return pd.DataFrame([
        ("2024-12-31", "2025-01-02T19:00:00Z", "2025-01-02T20:00:00Z", 100),
        ("2025-01-31", "2025-01-31T20:00:00Z", "2025-02-01T21:00:00Z", 105),
        ("2025-01-31", "2025-01-31T20:00:00Z", "2025-02-01T22:01:00Z", 95),
        ("2025-02-28", "2025-02-28T20:00:00Z", "2025-02-28T21:00:00Z", 90),
    ], columns=["observation_date", "published_at", "available_at", "value"]).assign(
        series="Test series", source="Test provider", evidence="Test fixture",
    )


def test_excludes_future_dates_and_late_revisions(records):
    signal = evaluate_signal(records, CUTOFF, confirmed=True)
    assert signal.status == "Source attested"
    assert signal.excluded == 2
    assert signal.observations["value"].tolist() == [100, 105]
    assert signal.adjustment == pytest.approx(0.005)


def test_signal_changes_allocations_when_applied(records):
    signal = evaluate_signal(records, CUTOFF, confirmed=True)
    returns = np.array([0.035, 0.043, 0.05, 0.08])
    cov = np.diag([0.005, 0.07, 0.06, 0.16]) ** 2
    adjusted = returns.copy()
    adjusted[-1] += signal.adjustment
    base = optimize(returns, cov, 0.065, 0.03).weights
    changed = optimize(adjusted, cov, 0.065, 0.03).weights
    assert changed[-1] < base[-1]


def test_missing_and_unverified_data_do_not_apply_a_tilt(records):
    assert evaluate_signal(None, CUTOFF).status == "Missing"
    assert evaluate_signal(records, "2025-01-15T00:00:00Z", confirmed=True).status == "Missing"
    signal = evaluate_signal(records, CUTOFF)
    assert signal.status == "Unverified" and signal.adjustment == 0


@pytest.mark.parametrize("field,bad", [
    ("available_at", "2025-01-01T12:00:00Z"),
    ("published_at", "2025-01-02T19:00:00"),
    ("value", np.inf),
    ("evidence", ""),
])
def test_invalid_provenance_or_value_stops_signal(records, field, bad):
    records[field] = records[field].astype(object)
    records.loc[0, field] = bad
    signal = evaluate_signal(records, CUTOFF, confirmed=True)
    assert signal.status == "Integrity failure" and signal.adjustment == 0


@pytest.mark.parametrize("options,action,allocation", [
    ({}, "ADOPT", "0%"),
    ({"committee_approved": True, "allocation_limit": 0.1}, "ALLOCATE", "0%–10.0%"),
    ({"committee_approved": True, "allocation_limit": 0.1, "current_allocation": 0.04,
      "drift": 0.05}, "REBALANCE", "0%–10.0%"),
    ({"live_inputs_verified": False}, "PILOT", "0%"),
])
def test_committee_evidence_and_authority(options, action, allocation):
    evidence = dict(live_inputs_verified=True, window_reviewed=True, benchmark_validated=True)
    decision = recommend(Optimization("Verified", True), [], "Source attested",
                         [{"Optimization": "Verified"}], [], **(evidence | options))
    assert (decision.action, decision.allocation_range) == (action, allocation)


def test_instability_and_integrity_trigger_stops():
    row = {"Scenario": "Test", "Optimization": "Verified", "Turnover vs. original allocation": 0.21}
    reasons = instability_reasons([row])
    assert "Test" in reasons[0]
    for status, unstable in [("Integrity failure", []), ("Source attested", reasons)]:
        decision = recommend(Optimization("Verified", True), [], status, [row], unstable)
        assert (decision.action, decision.allocation_range) == ("REJECT", "0%")
