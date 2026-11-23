import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def dashboard():
    app = AppTest.from_file("app.py").run()
    assert not app.exception
    return app


def decision_summary(app):
    decision = next(item.value for item in app.subheader if item.value.startswith("Current decision"))
    allocation = next(metric.value for metric in app.metric if metric.label == "Proposed live allocation range")
    reason = next(item.value for item in app.markdown if item.value.startswith("**Primary reason**"))
    return decision, allocation, reason


def test_default_dashboard(dashboard):
    assert dashboard.header[0].value == "1. Investment Committee Recommendation"
    assert [slider.value for slider in dashboard.slider] == [6.5, 3]
    decision, allocation, reason = decision_summary(dashboard)
    assert (decision, allocation) == ("Current decision · REJECT", "0%")
    assert "Economically infeasible" in reason and "Returns -2 pp" in reason

    comparison = dashboard.dataframe[1].value
    assert comparison["Portfolio"].tolist() == [
        "Benchmark", "Equal Weight", "Inverse Volatility", "Optimized Portfolio",
    ]
    optimized = comparison.iloc[-1]
    assert optimized["Expected Return"] == pytest.approx(0.065)
    assert optimized["Annual Volatility"] == pytest.approx(0.09242629496)
    assert optimized["Treasury Reserve"] == pytest.approx(0.03)
    assert optimized["Active Mandate Verdict (Gross)"] == "PASS"
    assert optimized["Sharpe Ratio"] < comparison.iloc[0]["Sharpe Ratio"]

    stress = dashboard.dataframe[-1].value
    assert len(stress) == 26
    assert stress["Optimization"].value_counts().to_dict() == {"Verified": 25, "Infeasible": 1}
    assert stress.loc[stress["Optimization"] == "Infeasible", "Scenario"].tolist() == ["Returns -2 pp"]
    upside = stress.loc[stress["Scenario"] == "Returns +2 pp"].iloc[0]
    assert upside["Turnover vs. active baseline"] == pytest.approx(0.5897, abs=0.0001)
    assert upside["Annual volatility change (pp)"] == pytest.approx(-6.25, abs=0.01)
    costs = stress.loc[stress["Scenario"] == "Trading cost 50 bp"].iloc[0]
    assert costs["Scenario mandate (gross)"] == "PASS"
    assert costs["Original mandate (first-year net)"] == "FAIL"
    assert costs["First-year net return"] == pytest.approx(0.064535)
    assert len(dashboard.get("plotly_chart")) == 5


def test_hiding_stress_details_preserves_decision(dashboard):
    original = decision_summary(dashboard)
    dashboard.toggle[0].set_value(False).run()
    assert not dashboard.exception
    assert decision_summary(dashboard) == original
    assert len(dashboard.get("plotly_chart")) == 3

    dashboard.slider[0].set_value(8.0).run()
    assert not dashboard.exception
    changed = decision_summary(dashboard)
    assert changed[:2] == ("Current decision · REJECT", "0%")
    assert "Baseline optimization: Infeasible." in changed[2]

    dashboard.toggle[0].set_value(True).run()
    assert not dashboard.exception
    assert decision_summary(dashboard) == changed


def test_unperformed_stress_assessment_shows_pending(monkeypatch):
    import part_two

    monkeypatch.setattr(part_two, "assess_stress", lambda *args: ([], []))
    dashboard = AppTest.from_file("app.py").run()
    assert not dashboard.exception
    decision, allocation, reason = decision_summary(dashboard)
    assert (decision, allocation) == ("Current decision · Assessment Pending", "0%")
    assert "active inputs" in reason
