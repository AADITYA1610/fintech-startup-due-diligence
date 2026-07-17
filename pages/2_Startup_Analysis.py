from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.scoring_engine import calculate_due_diligence_scores


st.set_page_config(
    page_title="Startup Analysis",
    page_icon="📊",
    layout="wide",
)


def initialize_session_state() -> None:
    """
    Ensure that startup_records exists in session state.
    """

    if "startup_records" not in st.session_state:
        st.session_state.startup_records = []


def format_currency(value: float | int | None) -> str:
    """
    Format a number as Indian rupee currency.
    """

    if value is None:
        return "Not Available"

    return f"₹{value:,.2f}"


def display_overall_assessment(
    startup_record: dict[str, Any],
    scoring_result: dict[str, Any],
) -> None:
    """
    Display the overall due-diligence result.
    """

    company = startup_record["company"]
    metrics = startup_record["calculated_metrics"]

    st.title("Startup Due-Diligence Analysis")

    st.write(
        f"Analysis for **{company['company_name']}** "
        f"from the **{company['industry']}** industry."
    )

    st.divider()

    overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

    with overview_col1:
        st.metric(
            label="Overall Score",
            value=f"{scoring_result['overall_score']}/100",
        )

    with overview_col2:
        st.metric(
            label="Risk Level",
            value=scoring_result["risk_level"],
        )

    with overview_col3:
        st.metric(
            label="Financial Score",
            value=f"{metrics['financial_health_score']}/100",
        )

    with overview_col4:
        runway = metrics["cash_runway_months"]

        if runway is None:
            runway_text = "No Current Burn"
        else:
            runway_text = f"{runway:.1f} months"

        st.metric(
            label="Cash Runway",
            value=runway_text,
        )

    st.subheader("Investment Recommendation")

    recommendation = scoring_result["investment_recommendation"]

    if scoring_result["overall_score"] >= 80:
        st.success(recommendation)
    elif scoring_result["overall_score"] >= 65:
        st.success(recommendation)
    elif scoring_result["overall_score"] >= 50:
        st.warning(recommendation)
    else:
        st.error(recommendation)


def display_category_scores(
    scoring_result: dict[str, Any],
) -> None:
    """
    Display category scores as metrics and a chart.
    """

    st.subheader("Category-Level Assessment")

    category_scores = scoring_result["category_scores"]

    first_row = st.columns(4)

    first_categories = [
        "Financial Health",
        "Founders & Team",
        "Product & Technology",
        "Market Opportunity",
    ]

    for column, category in zip(first_row, first_categories):
        with column:
            st.metric(
                label=category,
                value=f"{category_scores[category]:.2f}/100",
            )

    second_row = st.columns(3)

    second_categories = [
        "Customers & Traction",
        "Funding Position",
        "Legal & Compliance",
    ]

    for column, category in zip(second_row, second_categories):
        with column:
            st.metric(
                label=category,
                value=f"{category_scores[category]:.2f}/100",
            )

    chart_data = pd.DataFrame(
        {
            "Category": list(category_scores.keys()),
            "Score": list(category_scores.values()),
        }
    )

    figure = px.bar(
        chart_data,
        x="Score",
        y="Category",
        orientation="h",
        text="Score",
        title="Due-Diligence Category Scores",
        range_x=[0, 100],
    )

    figure.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside",
    )

    figure.update_layout(
        xaxis_title="Score out of 100",
        yaxis_title="",
        height=500,
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
    )


def display_financial_snapshot(
    startup_record: dict[str, Any],
) -> None:
    """
    Display important financial and customer metrics.
    """

    st.subheader("Financial and Traction Snapshot")

    financial = startup_record["financial"]
    customers = startup_record["customers"]
    metrics = startup_record["calculated_metrics"]

    financial_col1, financial_col2, financial_col3, financial_col4 = (
        st.columns(4)
    )

    with financial_col1:
        st.metric(
            label="Monthly Revenue",
            value=format_currency(financial["monthly_revenue"]),
        )

    with financial_col2:
        st.metric(
            label="Monthly Expenses",
            value=format_currency(financial["monthly_expenses"]),
        )

    with financial_col3:
        st.metric(
            label="Monthly Profit/Loss",
            value=format_currency(metrics["profit_loss"]),
        )

    with financial_col4:
        st.metric(
            label="Monthly Burn Rate",
            value=format_currency(metrics["burn_rate"]),
        )

    traction_col1, traction_col2, traction_col3, traction_col4 = st.columns(4)

    with traction_col1:
        st.metric(
            label="Total Customers",
            value=f"{customers['total_customers']:,}",
        )

    with traction_col2:
        st.metric(
            label="Customer Growth",
            value=f"{customers['customer_growth_rate']:.2f}%",
        )

    with traction_col3:
        st.metric(
            label="Retention Rate",
            value=f"{customers['retention_rate']:.2f}%",
        )

    with traction_col4:
        ltv_cac_ratio = metrics["ltv_cac_ratio"]

        st.metric(
            label="LTV/CAC Ratio",
            value=(
                f"{ltv_cac_ratio:.2f}"
                if ltv_cac_ratio is not None
                else "Not Available"
            ),
        )


def display_financial_warnings(
    startup_record: dict[str, Any],
) -> None:
    """
    Display warnings generated by the financial engine.
    """

    st.subheader("Identified Financial Concerns")

    warnings = startup_record["calculated_metrics"][
        "financial_warnings"
    ]

    if not warnings:
        st.success(
            "No major financial warning was identified "
            "from the provided information."
        )
        return

    for warning in warnings:
        st.warning(warning)


def display_scoring_methodology(
    scoring_result: dict[str, Any],
) -> None:
    """
    Explain how the weighted overall score is calculated.
    """

    with st.expander("View scoring methodology"):
        st.write(
            """
            Each due-diligence category receives a score out of 100.
            The final score is calculated using a weighted average.
            """
        )

        weights = scoring_result["category_weights"]

        methodology_data = []

        for category, weight in weights.items():
            methodology_data.append(
                {
                    "Category": category,
                    "Weight": f"{weight * 100:.0f}%",
                    "Category Score": (
                        scoring_result["category_scores"][category]
                    ),
                    "Weighted Contribution": round(
                        scoring_result["category_scores"][category]
                        * weight,
                        2,
                    ),
                }
            )

        st.dataframe(
            methodology_data,
            use_container_width=True,
            hide_index=True,
        )

        st.info(
            """
            This score is an analytical prototype designed to support
            due-diligence review. It should not be treated as a guaranteed
            investment decision or professional financial advice.
            """
        )


def main() -> None:
    """
    Run the startup-analysis page.
    """

    initialize_session_state()

    if not st.session_state.startup_records:
        st.warning(
            "No startup has been saved during this session."
        )

        st.info(
            "Open the Add Startup page, complete the form and save "
            "the startup before opening this analysis page."
        )

        st.stop()

    startup_names = [
        record["company"]["company_name"]
        for record in st.session_state.startup_records
    ]

    selected_index = st.selectbox(
        "Select a startup to analyse",
        options=range(len(startup_names)),
        format_func=lambda index: startup_names[index],
    )

    startup_record = st.session_state.startup_records[selected_index]

    scoring_result = calculate_due_diligence_scores(
        startup_record
    )

    display_overall_assessment(
        startup_record=startup_record,
        scoring_result=scoring_result,
    )

    st.divider()

    display_category_scores(scoring_result)

    st.divider()

    display_financial_snapshot(startup_record)

    st.divider()

    display_financial_warnings(startup_record)

    st.divider()

    display_scoring_methodology(scoring_result)

    with st.expander("View complete startup record"):
        st.json(startup_record)


if __name__ == "__main__":
    main()