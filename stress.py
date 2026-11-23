"""Deterministic one-factor and mandate-grid stress tests."""
from dataclasses import dataclass

import numpy as np

from analytics import (
    ORIGINAL_RESERVE, ORIGINAL_TARGET, mandate_failures, optimize,
    portfolio_return, portfolio_volatility, treasury_reserve,
)

TURNOVER_LIMIT = 0.20
RETURN_CHANGE_LIMIT = 0.015
VOLATILITY_CHANGE_LIMIT = 0.025


@dataclass(frozen=True)
class Scenario:
    name: str
    group: str
    returns: np.ndarray
    volatility: np.ndarray
    correlation: np.ndarray
    target: float
    reserve: float
    cost_bps: int = 0

    @property
    def covariance(self):
        return np.outer(self.volatility, self.volatility) * self.correlation


def scenarios(returns, volatility, correlation, target, reserve):
    base = dict(returns=returns, volatility=volatility, correlation=correlation,
                target=target, reserve=reserve)

    for pp in (-2, -1, 1, 2):
        yield Scenario(f"Returns {pp:+} pp", "Expected returns", **(base | {"returns": returns + pp / 100}))
    for pct in (-20, -10, 10, 20):
        yield Scenario(f"Volatility {pct:+}%", "Volatility",
                       **(base | {"volatility": volatility * (1 + pct / 100)}))

    for label, anchor in (
        ("Lower correlation", np.eye(len(returns))),
        ("Higher common correlation", np.ones((len(returns), len(returns)))),
    ):
        yield Scenario(label, "Correlation", **(base | {"correlation": 0.75 * correlation + 0.25 * anchor}))

    for bps in (0, 10, 25, 50):
        yield Scenario(f"Trading cost {bps} bp", "Transaction costs", **base, cost_bps=bps)

    for floor in (3, 5, 10, 20):
        for goal in (5.5, 6.5, 7.0):
            yield Scenario(f"{goal:.1f}% return / {floor}% reserve", "Constraints",
                           **(base | {"target": goal / 100, "reserve": floor / 100}))


def one_way_turnover(weights, reference):
    return float(0.5 * np.abs(weights - reference).sum())


def transaction_cost(weights, reference, bps):
    return one_way_turnover(weights, reference) * bps / 10_000


def run_scenarios(cases, baseline, baseline_returns, baseline_covariance, current, assets, value):
    if baseline is not None:
        base_return = portfolio_return(baseline, baseline_returns)
        base_volatility = portfolio_volatility(baseline, baseline_covariance)

    rows = []
    for scenario in cases:
        result = optimize(scenario.returns, scenario.covariance, scenario.target, scenario.reserve)
        weights = result.weights
        row = {
            "Scenario": scenario.name, "Group": scenario.group,
            "Scenario target": scenario.target, "Scenario reserve floor": scenario.reserve,
            "Solver succeeded": result.solver_succeeded, "Optimization": result.status,
            "Scenario verdict": "FAIL", "Scenario rule failures": result.details,
            "Original mandate verdict": "Unavailable", "Original mandate failures": "No verified portfolio",
        }
        if weights is not None:
            gross = portfolio_return(weights, scenario.returns)
            risk = portfolio_volatility(weights, scenario.covariance)
            cost = transaction_cost(weights, current, scenario.cost_bps)
            original = mandate_failures(
                weights, scenario.returns, ORIGINAL_TARGET, ORIGINAL_RESERVE, cost,
            )
            row.update({
                "Scenario verdict": "PASS", "Scenario rule failures": "",
                "Expected return": gross, "Annual volatility": risk,
                "Treasury reserve": treasury_reserve(weights),
                "Original mandate verdict": "FAIL" if original else "PASS",
                "Original mandate failures": "; ".join(original),
                "Trade turnover": one_way_turnover(weights, current),
                "Cost (bp per unit turnover)": scenario.cost_bps,
                "First-year cost ($)": cost * value,
                "First-year net return": gross - cost,
                "Turnover vs. original allocation": one_way_turnover(weights, baseline) if baseline is not None else np.nan,
                "Expected return change": gross - base_return if baseline is not None else np.nan,
                "Annual volatility change": risk - base_volatility if baseline is not None else np.nan,
            })
            for index, asset in enumerate(assets):
                row[asset] = weights[index]
                row[f"Δ {asset}"] = weights[index] - baseline[index] if baseline is not None else np.nan
        elif result.status == "Infeasible":
            row["Scenario rule failures"] = f"Expected return cannot meet target at required reserve. {result.details}"
        elif result.status == "Solver failed":
            row["Scenario verdict"] = "Unavailable"
        rows.append(row)
    return rows


def instability_reasons(rows):
    reasons = []
    thresholds = (
        ("Turnover vs. original allocation", TURNOVER_LIMIT),
        ("Expected return change", RETURN_CHANGE_LIMIT),
        ("Annual volatility change", VOLATILITY_CHANGE_LIMIT),
    )
    for field, limit in thresholds:
        exceeded = [row["Scenario"] for row in rows if abs(row.get(field, np.nan)) > limit + 1e-8]
        if exceeded:
            if field.startswith("Turnover"):
                reasons.append(f"Turnover vs. active baseline exceeds {limit:.1%} in {', '.join(exceeded)}.")
            else:
                reasons.append(f"Absolute {field.lower()} exceeds {limit * 100:.1f} pp in {', '.join(exceeded)}.")
    return reasons
