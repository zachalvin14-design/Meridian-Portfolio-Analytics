from unittest.mock import patch

import numpy as np
import pytest

from analytics import (
    mandate_failures, optimize, portfolio_return, portfolio_volatility, treasury_reserve,
)
from stress import one_way_turnover, run_scenarios, scenarios, transaction_cost

RETURNS = np.array([0.035, 0.043, 0.05, 0.08])
VOL = np.array([0.005, 0.07, 0.06, 0.16])
CORR = np.array([
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
])
COV = np.outer(VOL, VOL) * CORR
BENCHMARK = np.array([0, 0, 0.4, 0.6])
ASSETS = ["Bills", "Notes", "Bonds", "Equity"]


def test_return_and_volatility():
    assert portfolio_return(BENCHMARK, RETURNS) == pytest.approx(0.068)
    assert portfolio_volatility(BENCHMARK, COV) == pytest.approx(np.sqrt(0.010944))


@pytest.mark.parametrize("target,reserve", [(0.065, 0.03), (0.055, 0.20), (0.08, 0)])
def test_optimized_weights_meet_all_constraints(target, reserve):
    result = optimize(RETURNS, COV, target, reserve)
    assert result.status == "Verified"
    assert sum(result.weights) == pytest.approx(1)
    assert np.all(result.weights >= 0)
    assert np.all(result.weights <= 1)
    assert treasury_reserve(result.weights) >= reserve - 1e-8
    assert portfolio_return(result.weights, RETURNS) >= target - 1e-10


@pytest.mark.parametrize("weights,expected", [
    ([0.01, 0, 0.4, 0.7], "Not fully invested"),
    ([-0.02, 0.03, 0.4, 0.59], "Short selling violation"),
    ([0, 0, -0.01, 1.01], "Individual weight above 100%"),
    ([0.2, 0.2, 0.4, 0.2], "Expected return below target"),
    ([0.01, 0.01, 0.3, 0.68], "Treasury reserve below minimum"),
    ([np.nan, 0, 0, 1], "Non-finite portfolio weights"),
])
def test_failed_mandate_rules(weights, expected):
    assert expected in mandate_failures(np.array(weights), RETURNS, 0.065, 0.03)


def test_infeasible_optimization_skips_solver():
    with patch("analytics.minimize") as solver:
        result = optimize(RETURNS, COV, 0.08, 0.03)
    solver.assert_not_called()
    assert result.status == "Infeasible" and result.weights is None
    assert "7.889%" in result.details


def test_optimizer_rejects_invalid_solver_output():
    with patch("analytics.minimize") as solver:
        solver.return_value.success = True
        solver.return_value.x = BENCHMARK
        result = optimize(RETURNS, COV, 0.065, 0.03)
    assert result.status == "Constraint violation" and result.weights is None
    assert "Treasury reserve" in result.details


def test_stress_scenarios_and_dual_mandates():
    cases = list(scenarios(RETURNS, VOL, CORR, 0.065, 0.03))
    assert len(cases) == 26
    for case in cases:
        assert np.linalg.eigvalsh(case.covariance).min() >= -1e-12
        assert np.diag(case.correlation) == pytest.approx(np.ones(4))
    assert cases[0].returns == pytest.approx(RETURNS - 0.02)
    assert cases[4].volatility == pytest.approx(VOL * 0.80)
    baseline = optimize(RETURNS, COV, 0.065, 0.03).weights
    rows = run_scenarios(cases, baseline, RETURNS, COV, BENCHMARK, ASSETS, 100_000_000)
    by_name = {row["Scenario"]: row for row in rows}
    assert by_name["Returns -2 pp"]["Optimization"] == "Infeasible"
    row = by_name["5.5% return / 3% reserve"]
    assert row["Scenario verdict"] == "PASS"
    assert row["Original mandate verdict"] == "FAIL"
    assert row["Original mandate failures"] == "Expected return below target"
    assert sum(row[asset] for asset in ASSETS) == pytest.approx(1)
    assert sum(row[f"Δ {asset}"] for asset in ASSETS) == pytest.approx(0)
    assert by_name["Volatility +20%"]["Annual volatility change"] == pytest.approx(
        0.2 * portfolio_volatility(baseline, COV), abs=1e-6
    )
    priced = by_name["Trading cost 50 bp"]
    assert priced["First-year net return"] < priced["Expected return"]
    assert priced["Scenario verdict"] == "PASS" and priced["Original mandate verdict"] == "FAIL"


@pytest.mark.parametrize("bps,cost", [(0, 0), (10, 0.0002), (25, 0.0005), (50, 0.001)])
def test_transaction_cost_uses_one_way_turnover(bps, cost):
    weights = np.array([0.1, 0.1, 0.4, 0.4])
    assert one_way_turnover(weights, BENCHMARK) == pytest.approx(0.2)
    assert transaction_cost(weights, BENCHMARK, bps) == pytest.approx(cost)
