"""Point-in-time input contract for a two-observation global equity signal."""
from dataclasses import dataclass
from hashlib import sha256
import math
from typing import Optional

import pandas as pd

REQUIRED_COLUMNS = {
    "series", "source", "evidence", "observation_date",
    "published_at", "available_at", "value",
}
SIGNAL_TILT = 0.005


@dataclass(frozen=True)
class Signal:
    status: str
    detail: str
    adjustment: float = 0.0
    change: Optional[float] = None
    observations: Optional[pd.DataFrame] = None
    excluded: int = 0


def timestamp(value):
    parsed = pd.Timestamp(value)
    if pd.isna(parsed) or parsed.tzinfo is None:
        raise ValueError("Use timestamps with an explicit UTC offset.")
    return parsed.tz_convert("UTC")


def evaluate_signal(data, decision_at, confirmed=False):
    """Apply a fixed tilt only to complete, eligible, user-attested source records."""
    if data is None:
        return Signal("Missing", "No source observations supplied.")
    try:
        cutoff = timestamp(decision_at)
        if not REQUIRED_COLUMNS.issubset(data.columns):
            missing = ", ".join(sorted(REQUIRED_COLUMNS - set(data.columns)))
            raise ValueError(f"Missing fields: {missing}")
        rows = data.copy()
        for field in ("series", "source", "evidence"):
            rows[field] = rows[field].fillna("").astype(str).str.strip()
            if rows[field].eq("").any():
                raise ValueError(f"Every observation needs {field}.")
        if not rows["observation_date"].astype(str).str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
            raise ValueError("Use YYYY-MM-DD for observation dates.")
        rows["observation_date"] = pd.to_datetime(rows["observation_date"], errors="raise")
        for field in ("published_at", "available_at"):
            rows[field] = pd.to_datetime(rows[field].map(timestamp), utc=True)
        rows["value"] = pd.to_numeric(rows["value"])
        if not rows["value"].map(lambda value: math.isfinite(value) and value > 0).all():
            raise ValueError("Index levels must be finite and positive.")
        publication_dates = rows["published_at"].dt.tz_localize(None).dt.normalize()
        if (publication_dates < rows["observation_date"]).any():
            raise ValueError("An observation date follows its publication date in UTC.")
        if (rows["available_at"] < rows["published_at"]).any():
            raise ValueError("Availability precedes publication.")
        if rows[["series", "source"]].drop_duplicates().shape[0] > 1:
            raise ValueError("Use a single consistent global equity series and provider.")
        if rows.duplicated(["observation_date", "available_at"]).any():
            raise ValueError("Duplicate observation vintages are ambiguous.")
    except (ValueError, TypeError, OverflowError) as error:
        return Signal("Integrity failure", str(error))

    cutoff_date = cutoff.tz_localize(None).normalize()
    eligible = rows.loc[
        (rows["observation_date"] <= cutoff_date)
        & (rows["published_at"] <= cutoff)
        & (rows["available_at"] <= cutoff)
    ].sort_values(["observation_date", "available_at"])
    excluded = len(rows) - len(eligible)
    observations = eligible.drop_duplicates("observation_date", keep="last").tail(2)
    if len(observations) < 2:
        return Signal("Missing", "Two distinct eligible observations are required.",
                      observations=observations, excluded=excluded)
    if not confirmed:
        return Signal("Unverified", "Source records and historical vintages require verification.",
                      observations=observations, excluded=excluded)
    change = float(observations["value"].iloc[1] / observations["value"].iloc[0] - 1)
    if not math.isfinite(change):
        return Signal("Integrity failure", "Observed change is outside the numeric range.",
                      observations=observations, excluded=excluded)
    tilt = SIGNAL_TILT if change > 0 else -SIGNAL_TILT if change < 0 else 0.0
    return Signal("Source attested", "Timing checks passed. Source verification is user-attested.",
                  tilt, change, observations, excluded)


def fingerprint(raw):
    return sha256(raw).hexdigest()
