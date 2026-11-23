"""Streamlit components for the signal, scenario comparisons and decision."""
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import ORIGINAL_RESERVE, ORIGINAL_TARGET, mandate_failures
from committee import recommend
from signal_data import Signal, evaluate_signal, fingerprint
from stress import (
    RETURN_CHANGE_LIMIT, TURNOVER_LIMIT, VOLATILITY_CHANGE_LIMIT,
    instability_reasons, run_scenarios, scenarios,
)


def signal_card():
    with st.expander("Point-in-time signal data card"):
        st.caption(
            "Lab 13 provides the base training assumptions. The optional signal uses "
            "historical observations supplied with original source and vintage evidence."
        )
        decision_at = st.text_input(
            "Decision date and time with UTC offset",
            placeholder="YYYY-MM-DDTHH:MM:SS±HH:MM",
        )
        uploaded = st.file_uploader("Global equity index observations (source evidence CSV)", type="csv")
        st.code("series,source,evidence,observation_date,published_at,available_at,value", language="text")
        st.caption(
            "Use one consistent global equity index and provider, with observation dates "
            "in YYYY-MM-DD, publication and availability timestamps with UTC offsets, "
            "and evidence links or archive identifiers for each historical vintage."
        )
        confirmed = st.checkbox(
            "I checked the historical values, publication and availability against the cited sources",
            key=f"signal_verification_{fingerprint(uploaded.getvalue()) if uploaded else 'missing'}",
            disabled=uploaded is None,
        )
        if uploaded is None:
            signal = evaluate_signal(None, decision_at)
        else:
            raw = uploaded.getvalue()
            st.caption(f"Input SHA-256: {fingerprint(raw)}")
            try:
                data = pd.read_csv(BytesIO(raw))
                signal = evaluate_signal(data, decision_at, confirmed)
            except (ValueError, UnicodeError) as error:
                signal = Signal("Integrity failure", f"Cannot read CSV. {error}")

        st.write(f"Decision cutoff: {decision_at or 'Unavailable'}")
        st.write(f"Signal status: {signal.status}. {signal.detail}")
        st.caption(
            "Take the two latest eligible observation dates and the latest available vintage "
            "for each. A higher index level adds 0.50 pp to the modeled global equity "
            "return. A lower level subtracts 0.50 pp. A flat level leaves it unchanged."
        )
        st.caption(
            f"Records excluded by the cutoff: {signal.excluded}. "
            f"Applied global equity return adjustment: {100 * signal.adjustment:+.2f} pp."
        )
        if signal.observations is not None and not signal.observations.empty:
            st.dataframe(signal.observations, hide_index=True)
        else:
            st.write("Observation dates, sources, publication and availability records are unavailable.")
        if signal.change is not None:
            st.write(f"Change between selected index levels: {signal.change:+.2%}")
    return signal


@st.cache_data(show_spinner=False)
def assess_stress(returns, volatility, correlation, target, reserve, baseline, current, assets, value):
    rows = run_scenarios(
        scenarios(returns, volatility, correlation, target, reserve),
        baseline, returns, correlation * volatility[:, None] * volatility[None, :],
        current, assets, value,
    )
    return rows, instability_reasons(rows)


def stress_dashboard(rows, assets):
    st.header("8. Stress Testing")
    if not rows:
        st.info("Stress assessment has not run for the active inputs.")
        return
    if not st.toggle("Show stress scenario details", value=True):
        st.caption("The committee decision still uses the complete stress assessment.")
        return
    st.caption(
        "Changes and allocation turnover use the optimized portfolio for the active sidebar settings as the baseline. "
        "Original mandate compliance always uses a 6.5% return target and a 3% Treasury floor, "
        "evaluated with each scenario's return estimates after any modeled first-year trading cost."
    )
    st.caption(
        "Correlation scenarios blend the baseline matrix 75/25 with either an identity "
        "matrix or an all-ones matrix. Both blends preserve positive semidefiniteness. "
        "Transaction-cost tests keep the optimizer's gross target and charge a one-time cost "
        "on one-way turnover from the app's 40% investment-grade bond / 60% global equity benchmark."
    )
    st.info(
        "Estimation-window test unavailable. The course's ETF snapshot has a different "
        "asset universe and unverified historical adjustment vintages. A dated, source-verified "
        "return history mapped to these four Lab 13 sleeves is required."
    )
    frame = pd.DataFrame(rows)
    groups = list(frame["Group"].unique())
    shown_groups = st.multiselect("Scenario groups", groups, default=groups)
    visible = frame.loc[frame["Group"].isin(shown_groups)]
    headings = {
        "Expected return": "Gross expected return",
        "Scenario verdict": "Scenario mandate (gross)",
        "Original mandate verdict": "Original mandate (first-year net)",
        "Trade turnover": "Trading turnover vs. benchmark",
        "Turnover vs. original allocation": "Turnover vs. active baseline",
    }
    details = visible.rename(columns=headings).copy()
    changes = ["Expected return change", "Annual volatility change", *(f"Δ {asset}" for asset in assets)]
    for column in changes:
        if column in details:
            details[f"{column} (pp)"] = details.pop(column) * 100
    percent = [
        "Scenario target", "Scenario reserve floor", "Gross expected return", "Annual volatility",
        "First-year net return", "Treasury reserve", "Trading turnover vs. benchmark",
        "Turnover vs. active baseline", *assets,
    ]
    formats = {name: "{:.2%}" for name in percent if name in details}
    formats.update({f"{name} (pp)": "{:+.2f}" for name in changes if f"{name} (pp)" in details})
    if "First-year cost ($)" in details:
        formats["First-year cost ($)"] = "${:,.2f}"

    overview = [
        "Scenario", "Optimization", "Gross expected return", "Annual volatility",
        "Treasury reserve", "Scenario mandate (gross)", "Original mandate (first-year net)",
    ]
    overview = [name for name in overview if name in details]
    st.dataframe(
        details[overview].style.format({name: formats[name] for name in overview if name in formats}, na_rep="—"),
        hide_index=True, width="stretch",
    )
    with st.expander("Full scenario table, including weights, costs, and mandate reasons"):
        st.dataframe(details.style.format(formats, na_rep="—"), hide_index=True, width="stretch")

    st.subheader("Largest changes from the active baseline")
    turnover_field = "Turnover vs. original allocation"
    if turnover_field not in frame or frame[turnover_field].isna().all():
        st.write("No verified baseline and scenario weights are available for comparison.")
    else:
        for metric in (turnover_field, "Expected return change", "Annual volatility change"):
            values = frame[metric].abs()
            peak = values.max()
            labels = frame.loc[(values - peak).abs() <= 1e-8, "Scenario"].tolist()
            size = f"{peak:.2%}" if metric == turnover_field else f"{peak * 100:.2f} pp"
            st.write(f"**{headings.get(metric, metric)}** · {size} absolute · {', '.join(labels)}")
    if "Expected return" in visible:
        modeled = visible.dropna(subset=["Expected return"])
        if not modeled.empty:
            comparison = px.scatter(
                modeled, x="Annual volatility", y="Expected return", color="Group",
                hover_name="Scenario", hover_data=["First-year net return", "Treasury reserve"],
                title="Scenario risk and expected return",
            )
            comparison.update_layout(xaxis_tickformat=".1%", yaxis_tickformat=".1%")
            st.plotly_chart(comparison)
            weights = modeled.melt(id_vars=["Scenario"], value_vars=assets, var_name="Asset", value_name="Weight")
            allocation = px.bar(weights, x="Scenario", y="Weight", color="Asset", title="Scenario allocations")
            allocation.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(allocation)


def committee_dashboard(baseline, returns, signal, rows, instability, target, reserve):
    st.header("1. Investment Committee Recommendation")
    failures = (
        mandate_failures(baseline.weights, returns, ORIGINAL_TARGET, ORIGINAL_RESERVE)
        if baseline.weights is not None else []
    )
    decision = recommend(baseline, failures, signal.status, rows, instability)
    st.subheader(f"Current decision · {decision.action}")
    allocation, return_floor, reserve_floor = st.columns(3)
    allocation.metric("Proposed live allocation range", decision.allocation_range)
    return_floor.metric("Active gross return floor", f"{target:.1%}")
    reserve_floor.metric("Active Treasury reserve floor", f"{reserve:.0%}")
    st.write(f"**Primary reason** · {decision.reasons[0]}")
    if decision.allocation_range == "0%":
        st.warning("Process stop. Do not initiate or rebalance a live allocation. Model outputs are for review.")
    verified_count = sum(row["Optimization"] == "Verified" for row in rows)
    stress_status = f"{verified_count} of {len(rows)} verified" if rows else "Pending"
    st.write(
        f"Baseline optimization: {baseline.status}. "
        f"Signal: {signal.status}. Stress assessment: {stress_status}."
    )
    if len(decision.reasons) > 1:
        with st.expander("Additional decision evidence"):
            for reason in decision.reasons[1:]:
                st.write(f"• {reason}")

    with st.expander("Decision rules and monitoring triggers"):
        st.markdown(f"""
- **Assessment Pending** until the stress suite has been assessed for the active inputs. Live allocation stays at 0%.
- **REJECT** for economic infeasibility, solver failure, failed mandate checks, point-in-time integrity failure, or material stress instability.
- **PILOT** means educational validation only while required data, dated window tests, or benchmark holdout evidence are missing after stress assessment.
- **ADOPT** after validation gates clear. A committee-authorized cap is required to fund the strategy. An approved funded strategy can continue under ADOPT while within its cap and drift tolerance.
- **ALLOCATE** for initial funding after validation and committee approval with an explicit size cap.
- **REBALANCE** for an approved funded strategy when weight drift reaches 5 pp or funding exceeds its approved cap.
- **Review triggers** include return below 6.5%, reserve below 3%, weight restrictions breached, unavailable source vintages, or failed optimization. Reassess after three monthly reviews below benchmark rolling Sharpe.
- **Material stress thresholds** are more than {TURNOVER_LIMIT:.0%} one-way allocation change, {RETURN_CHANGE_LIMIT * 100:.1f} pp expected-return change, or {VOLATILITY_CHANGE_LIMIT * 100:.1f} pp volatility change. These are prototype review thresholds.
""")
