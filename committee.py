"""Committee rules for the educational dashboard."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    action: str
    allocation_range: str
    reasons: tuple


def recommend(baseline, original_failures, signal_status, stress_rows, instability,
              *, live_inputs_verified=False, window_reviewed=False,
              committee_approved=False, benchmark_validated=False,
              allocation_limit=None, current_allocation=0.0, drift=0.0):
    hard_stops = []
    if baseline.status != "Verified":
        hard_stops.append(f"Baseline optimization: {baseline.status}.")
    if original_failures:
        hard_stops.append("Baseline fails the original mandate: " + "; ".join(original_failures))
    if signal_status == "Integrity failure":
        hard_stops.append("Point-in-time data integrity failed.")
    stress_failures = {
        "Infeasible": "Economically infeasible stress constraints",
        "Solver failed": "Stress solver failed",
        "Constraint violation": "Stress solver returned weights that breached constraints",
    }
    for status in dict.fromkeys(row["Optimization"] for row in stress_rows):
        if status == "Verified":
            continue
        explanation = stress_failures.get(status, f"Unverified stress results ({status})")
        scenarios = [row["Scenario"] for row in stress_rows if row["Optimization"] == status]
        if scenarios:
            hard_stops.append(f"{explanation}: {', '.join(scenarios)}.")
    hard_stops.extend(instability)

    missing = []
    if signal_status != "Source attested":
        missing.append("Point-in-time signal evidence is missing or unverified.")
    if not live_inputs_verified:
        missing.append("Required live return, volatility and correlation inputs are unverified.")
    if not window_reviewed:
        missing.append("Historical estimation-window sensitivity is unavailable.")
    if not benchmark_validated:
        missing.append("Holdout results against the benchmark require validation.")
    if not stress_rows:
        return Decision(
            "Assessment Pending", "0%",
            ("Stress assessment has not run for the active inputs.", *hard_stops, *missing),
        )
    if hard_stops:
        return Decision("REJECT", "0%", tuple(hard_stops + missing))
    if missing:
        return Decision("PILOT", "0%", tuple(missing))
    if not committee_approved or allocation_limit is None or not 0 < allocation_limit <= 1:
        return Decision("ADOPT", "0%", ("Model evidence gates passed. Trading authority or a sizing limit is pending.",))
    if current_allocation <= 0:
        return Decision("ALLOCATE", f"0%–{allocation_limit:.1%}", ("Committee-authorized initial funding.",))
    if drift >= 0.05 or current_allocation > allocation_limit:
        return Decision("REBALANCE", f"0%–{allocation_limit:.1%}", ("Weight drift reached 5 pp or funding exceeds the approved cap.",))
    return Decision("ADOPT", f"0%–{allocation_limit:.1%}", ("Continue the approved program within its funding cap.",))
