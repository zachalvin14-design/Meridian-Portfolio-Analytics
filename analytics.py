"""Reusable Lab 13 portfolio calculations and constrained optimization."""
from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy.optimize import minimize

WEIGHT_TOLERANCE = 1e-8
RETURN_TOLERANCE = 1e-10
ORIGINAL_TARGET = 0.065
ORIGINAL_RESERVE = 0.03


def portfolio_return(weights, returns):
    return float(weights @ returns)


def portfolio_volatility(weights, covariance):
    return float(np.sqrt(max(weights @ covariance @ weights, 0.0)))


def treasury_reserve(weights):
    return float(sum(weights[:2]))


def mandate_failures(weights, returns, target, reserve, cost=0.0):
    if not np.all(np.isfinite(weights)):
        return ["Non-finite portfolio weights"]

    failures = []
    if abs(np.sum(weights) - 1) > WEIGHT_TOLERANCE:
        failures.append("Not fully invested")
    if np.any(weights < -WEIGHT_TOLERANCE):
        failures.append("Short selling violation")
    if np.any(weights > 1 + WEIGHT_TOLERANCE):
        failures.append("Individual weight above 100%")
    if portfolio_return(weights, returns) - cost < target - RETURN_TOLERANCE:
        failures.append("Expected return below target")
    if treasury_reserve(weights) < reserve - WEIGHT_TOLERANCE:
        failures.append("Treasury reserve below minimum")
    return failures


def maximum_return_weights(returns, reserve):
    weights = np.zeros(len(returns))
    weights[np.argmax(returns[:2])] = reserve
    weights[np.argmax(returns)] += 1 - reserve
    return weights


@dataclass
class Optimization:
    status: str
    solver_succeeded: bool
    weights: Optional[np.ndarray] = None
    details: str = ""


def optimize(returns, covariance, target, reserve):
    start = maximum_return_weights(returns, reserve)
    maximum = portfolio_return(start, returns)
    if target > maximum + RETURN_TOLERANCE:
        return Optimization("Infeasible", False, details=f"Maximum achievable return: {maximum:.3%}")

    reserve_mask = np.zeros_like(returns)
    reserve_mask[:2] = 1
    result = minimize(
        lambda w: float(w @ covariance @ w),
        start,
        jac=lambda w: 2 * (covariance @ w),
        method="SLSQP",
        bounds=[(0.0, 1.0)] * len(returns),
        constraints=[
            {"type": "eq", "fun": lambda w: np.sum(w) - 1, "jac": lambda w: np.ones_like(w)},
            {"type": "ineq", "fun": lambda w: w @ returns - target, "jac": lambda w: returns},
            {"type": "ineq", "fun": lambda w: w @ reserve_mask - reserve, "jac": lambda w: reserve_mask},
        ],
        options={"ftol": 1e-12, "maxiter": 3000},
    )
    if not result.success:
        return Optimization("Solver failed", False, details=str(result.message))
    failures = mandate_failures(result.x, returns, target, reserve)
    if failures:
        return Optimization("Constraint violation", True, details="; ".join(failures))
    return Optimization("Verified", True, result.x)
