# FIN 439 - PROJECT 2
# MERIDIAN PORTFOLIO ANALYTICS
# Investment Management Application
#
# AI Disclosure: OpenAI ChatGPT assisted with Python coding, application
# structure, debugging guidance, and documentation drafting.
# The student is responsible for validating the analysis and making
# the final investment decision.
#
# EDUCATIONAL USE ONLY - NOT INVESTMENT ADVICE

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import analytics
from part_two import assess_stress, committee_dashboard, signal_card, stress_dashboard

st.set_page_config(
    page_title="Meridian Portfolio Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 Meridian Portfolio Analytics")
st.subheader("Investment Committee Decision Dashboard")
st.caption("FIN 439 | Project 2 | Investment Management Application")
st.info(
    "AI Disclosure: OpenAI ChatGPT assisted with coding, application design, "
    "and documentation. The student is responsible for validating the analysis "
    "and making the investment decision. This application is for educational "
    "purposes only and does not constitute investment advice."
)

# Lab 13 investment universe
assets = [
    "Treasury Bills",
    "Treasury 10-Year Note",
    "Investment Grade Bonds",
    "Global Equity",
]
expected_returns = np.array([0.035, 0.043, 0.050, 0.080])
asset_volatility = np.array([0.005, 0.070, 0.060, 0.160])
correlation_matrix = np.array([
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
])
covariance_matrix = np.outer(asset_volatility, asset_volatility) * correlation_matrix

st.sidebar.title("Investment Mandate")
st.sidebar.markdown(
    "Adjust portfolio requirements and observe how the optimized allocation changes."
)
target_return = st.sidebar.slider(
    "Minimum Expected Annual Return",
    min_value=3.5, max_value=8.0, value=6.5, step=0.5, format="%.1f%%",
) / 100
minimum_reserve = st.sidebar.slider(
    "Minimum Treasury Reserve",
    min_value=0, max_value=30, value=3, step=1, format="%d%%",
) / 100
risk_free_rate = st.sidebar.number_input(
    "Annual Risk-Free Rate (decimal)",
    min_value=0.0, max_value=0.10, value=0.045, step=0.005, format="%.3f",
    help="Enter 0.045 for 4.5%. This rate affects the modeled Sharpe ratio only.",
)
portfolio_value = st.sidebar.number_input(
    "Portfolio Value ($)",
    min_value=1000, max_value=1000000000, value=100000000, step=1000000,
)
st.sidebar.markdown("---")
st.sidebar.write("Portfolio Constraints")
st.sidebar.write("Fully Invested: 100%")
st.sidebar.write("Short Selling: Not Permitted")
st.sidebar.write(f"Minimum Treasury Reserve: {minimum_reserve:.1%}")
st.sidebar.write(f"Minimum Expected Return: {target_return:.1%}")

with st.sidebar:
    signal = signal_card()
modeled_returns = expected_returns.copy()
modeled_returns[assets.index("Global Equity")] += signal.adjustment


def portfolio_return(weights):
    return analytics.portfolio_return(weights, modeled_returns)


def portfolio_volatility(weights):
    return analytics.portfolio_volatility(weights, covariance_matrix)


def portfolio_sharpe(weights):
    risk = portfolio_volatility(weights)
    if risk <= 0:
        return np.nan
    return (portfolio_return(weights) - risk_free_rate) / risk


def mandate_check(weights):
    failures = analytics.mandate_failures(weights, modeled_returns, target_return, minimum_reserve)
    return "FAIL: " + "; ".join(failures) if failures else "PASS"


benchmark_weights = np.array([0.00, 0.00, 0.40, 0.60])
equal_weights = np.array([0.25, 0.25, 0.25, 0.25])
inverse_volatility = 1 / asset_volatility
inverse_vol_weights = inverse_volatility / inverse_volatility.sum()
portfolios = {
    "Benchmark": benchmark_weights,
    "Equal Weight": equal_weights,
    "Inverse Volatility": inverse_vol_weights,
}

baseline = analytics.optimize(modeled_returns, covariance_matrix, target_return, minimum_reserve)
stress_rows, instability = assess_stress(
    modeled_returns, asset_volatility, correlation_matrix, target_return,
    minimum_reserve, baseline.weights, benchmark_weights, assets, portfolio_value,
)
committee_dashboard(
    baseline, modeled_returns, signal, stress_rows, instability, target_return, minimum_reserve,
)
if baseline.status == "Infeasible":
    maximum = portfolio_return(analytics.maximum_return_weights(modeled_returns, minimum_reserve))
    st.warning(
        f"Infeasible mandate. With a minimum Treasury reserve of {minimum_reserve:.0%}, "
        f"the highest achievable expected annual return is {maximum:.3%}. "
        f"The selected target of {target_return:.1%} exceeds that maximum. "
        "Lower the return target or the minimum Treasury reserve to run the optimizer."
    )
elif baseline.weights is None:
    st.error(f"Optimization unsuccessful. {baseline.status}. {baseline.details}")
else:
    portfolios["Optimized Portfolio"] = baseline.weights

st.header("2. Investment Universe")
universe_df = pd.DataFrame({
    "Asset Class": assets,
    "Lab 13 Expected Annual Return": expected_returns,
    "Modeled Expected Annual Return": modeled_returns,
    "Annual Volatility": asset_volatility,
})
st.dataframe(
    universe_df.style.format({
        "Lab 13 Expected Annual Return": "{:.2%}",
        "Modeled Expected Annual Return": "{:.2%}",
        "Annual Volatility": "{:.2%}",
    }),
    width="stretch",
    hide_index=True,
)
st.caption(
    "Source: FIN 439 Lab 13 course-authored training assumptions. "
    "These values are not historical market estimates or forward-looking guarantees."
)

st.header("3. Portfolio Comparison")
comparison_rows = []
for name, weights in portfolios.items():
    comparison_rows.append({
        "Portfolio": name,
        "Expected Return": portfolio_return(weights),
        "Annual Volatility": portfolio_volatility(weights),
        "Sharpe Ratio": portfolio_sharpe(weights),
        "Treasury Reserve": analytics.treasury_reserve(weights),
        "Active Mandate Verdict (Gross)": mandate_check(weights),
    })
comparison_df = pd.DataFrame(comparison_rows)
st.dataframe(
    comparison_df.style.format({
        "Expected Return": "{:.2%}",
        "Annual Volatility": "{:.2%}",
        "Sharpe Ratio": "{:.3f}",
        "Treasury Reserve": "{:.2%}",
    }),
    width="stretch",
    hide_index=True,
)
st.caption(f"Modeled annual Sharpe uses gross expected return and a {risk_free_rate:.2%} annual risk-free rate.")

st.header("4. Portfolio Allocations")
allocation_rows = []
for name, weights in portfolios.items():
    for asset, weight in zip(assets, weights):
        allocation_rows.append({"Portfolio": name, "Asset Class": asset, "Weight": weight})
allocation_df = pd.DataFrame(allocation_rows)
fig_allocation = px.bar(
    allocation_df,
    x="Portfolio",
    y="Weight",
    color="Asset Class",
    title="Asset Allocation by Portfolio",
    barmode="stack",
    hover_data={"Weight": ":.2%"},
)
fig_allocation.update_layout(yaxis_tickformat=".0%", height=500)
st.plotly_chart(fig_allocation)

st.header("5. Risk vs. Expected Return")
fig_risk = px.scatter(
    comparison_df,
    x="Annual Volatility",
    y="Expected Return",
    color="Portfolio",
    text="Portfolio",
    title="Portfolio Risk-Return Comparison",
    labels={"Expected Return": "Expected Annual Return"},
    hover_data={"Annual Volatility": ":.2%", "Expected Return": ":.2%"},
)
fig_risk.update_traces(marker=dict(size=15), textposition="top center")
fig_risk.update_layout(xaxis_tickformat=".1%", yaxis_tickformat=".1%", height=500)
st.plotly_chart(fig_risk)

st.header("6. Optimized Portfolio Dashboard")
if "Optimized Portfolio" in portfolios:
    w = portfolios["Optimized Portfolio"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Expected Annual Return", f"{portfolio_return(w):.2%}")
    col2.metric("Annual Volatility", f"{portfolio_volatility(w):.2%}")
    col3.metric("Sharpe Ratio", f"{portfolio_sharpe(w):.3f}")
    col4.metric("Treasury Reserve", f"{analytics.treasury_reserve(w):.2%}")

    optimized_df = pd.DataFrame({
        "Asset Class": assets,
        "Portfolio Weight": w,
        "Dollar Allocation": w * portfolio_value,
    })
    st.dataframe(
        optimized_df.style.format({
            "Portfolio Weight": "{:.2%}",
            "Dollar Allocation": "${:,.2f}",
        }),
        width="stretch",
        hide_index=True,
    )
    fig_pie = px.pie(
        optimized_df,
        names="Asset Class",
        values="Portfolio Weight",
        title="Optimized Portfolio Composition",
        hole=0.4,
    )
    st.plotly_chart(fig_pie)
else:
    st.warning("No verified feasible optimized portfolio is available under these settings.")

st.header("7. Active Mandate Compliance (Gross)")
for name, weights in portfolios.items():
    verdict = mandate_check(weights)
    if verdict == "PASS":
        st.success(f"{name}: PASS — all implemented mandate checks satisfied.")
    else:
        st.error(f"{name}: {verdict}")
st.warning(
    "These are the checks implemented in this application. Lab 13 states that full "
    "Meridian mandate compliance requires additional checks."
)

stress_dashboard(stress_rows, assets)

st.header("9. Export Investment Results")
st.caption("CSV returns, volatility, reserves, and weights are decimal fractions. A weight of 0.03 represents 3%.")
st.download_button(
    label="Download Portfolio Comparison",
    data=comparison_df.to_csv(index=False),
    file_name="portfolio_comparison.csv",
    mime="text/csv",
    on_click="ignore",
)
st.download_button(
    label="Download Portfolio Allocations",
    data=allocation_df.to_csv(index=False),
    file_name="portfolio_allocations.csv",
    mime="text/csv",
    on_click="ignore",
)
st.markdown("---")
st.caption(
    "Meridian Portfolio Analytics | FIN 439 Project 2 | "
    "Educational use only — not investment advice."
)
