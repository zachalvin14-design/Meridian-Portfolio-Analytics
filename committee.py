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
    if any(row["Optimization"] != "Verified" for row in stress_rows):
        hard_stops.append("At least one stress scenario did not produce verified weights.")
    hard_stops.extend(instability)

    missing = []
    if signal_status != "Source attested":
        missing.append("Point-in-time signal evidence is missing or unverified.")
    if not live_inputs_verified:
        missing.append("Required live return, volatility and correlation inputs are unverified.")
    if not window_reviewed:
        missing.append("Historical estimation-window sensitivity is unavailable.")
    if not stress_rows:
        missing.append("Run the full stress suite before reviewing a live allocation.")
    if not benchmark_validated:
        missing.append("Holdout results against the benchmark require validation.")
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
