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


def stress_dashboard(returns, volatility, correlation, target, reserve, baseline, current, assets, value):
    st.header("7. Stress Testing")
    st.caption(
        "The original allocation is the optimized portfolio for the active sidebar settings. "
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
    if not st.toggle("Run all stress scenarios", value=True):
        return [], []

    rows = run_scenarios(
        scenarios(returns, volatility, correlation, target, reserve),
        baseline, returns, correlation * volatility[:, None] * volatility[None, :],
        current, assets, value,
    )
    frame = pd.DataFrame(rows)
    percent = [
        "Scenario target", "Scenario reserve floor", "Expected return", "Annual volatility",
        "First-year net return", "Treasury reserve", "Trade turnover",
        "Turnover vs. original allocation", "Expected return change", "Annual volatility change",
        *assets, *(f"Δ {asset}" for asset in assets),
    ]
    groups = list(frame["Group"].unique())
    shown_groups = st.multiselect("Scenario groups", groups, default=groups)
    visible = frame.loc[frame["Group"].isin(shown_groups)]
    formats = {name: "{:.2%}" for name in percent if name in frame}
    if "First-year cost ($)" in frame:
        formats["First-year cost ($)"] = "${:,.2f}"
    st.dataframe(visible.style.format(formats, na_rep="—"), hide_index=True, width="stretch")

    st.subheader("Largest changes from the original allocation")
    if baseline is None:
        st.write("Change metrics are unavailable because the baseline did not produce verified weights.")
    else:
        for metric in ("Turnover vs. original allocation", "Expected return change", "Annual volatility change"):
            if metric in frame and frame[metric].notna().any():
                values = frame[metric].abs()
                peak = values.max()
                labels = frame.loc[(values - peak).abs() <= 1e-8, "Scenario"].tolist()
                st.write(f"**{metric}** · {peak:.2%} absolute · {', '.join(labels)}")
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

    return rows, instability_reasons(rows)


def committee_dashboard(baseline, returns, signal, rows, instability):
    st.header("8. Investment Committee Recommendation")
    failures = (
        mandate_failures(baseline.weights, returns, ORIGINAL_TARGET, ORIGINAL_RESERVE)
        if baseline.weights is not None else []
    )
    decision = recommend(baseline, failures, signal.status, rows, instability)
    st.subheader(f"Current decision · {decision.action}")
    st.metric("Proposed live allocation range", decision.allocation_range)
    if decision.allocation_range == "0%":
        st.warning("Process stop. Do not initiate or rebalance a live allocation. Model outputs are for review.")
    st.write(
        f"Baseline optimization: {baseline.status}. "
        f"Signal: {signal.status}. Stress scenarios with verified weights: "
        f"{sum(row['Optimization'] == 'Verified' for row in rows)} of {len(rows)}."
    )
    for reason in decision.reasons:
        st.write(f"• {reason}")

    with st.expander("Decision rules and monitoring triggers"):
        st.markdown(f"""
- **REJECT** when baseline or scenario optimization fails, verified weights breach the applicable constraints, the baseline breaches the original mandate, timing integrity fails, or stress results are materially unstable.
- **PILOT** means educational validation only while required data, dated window tests, full stress results, or benchmark holdout evidence are missing.
- **ADOPT** after validation gates clear. A committee-authorized cap is required to fund the strategy. An approved funded strategy can continue under ADOPT while within its cap and drift tolerance.
- **ALLOCATE** for initial funding after validation and committee approval with an explicit size cap.
- **REBALANCE** for an approved funded strategy when weight drift reaches 5 pp or funding exceeds its approved cap.
- **Review triggers** include return below 6.5%, reserve below 3%, weight restrictions breached, unavailable source vintages, or failed optimization. Reassess after three monthly reviews below benchmark rolling Sharpe.
- **Material stress thresholds** are more than {TURNOVER_LIMIT:.0%} one-way allocation change, {RETURN_CHANGE_LIMIT * 100:.1f} pp expected-return change, or {VOLATILITY_CHANGE_LIMIT * 100:.1f} pp volatility change. These are prototype review thresholds.
""")
