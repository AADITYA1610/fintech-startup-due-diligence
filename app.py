from __future__ import annotations

from typing import Any

import streamlit as st


st.set_page_config(
    page_title="Startup Due Diligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize shared application state.

    analysis_history:
        Stores all startup analyses completed during the current
        Streamlit session.

    latest_analysis:
        Stores the most recently completed startup analysis.
    """

    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []

    if "latest_analysis" not in st.session_state:
        st.session_state.latest_analysis = None


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """Convert a value to float safely."""

    try:
        if value is None or value == "":
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def get_company_name(
    analysis: dict[str, Any],
) -> str:
    """Extract the company name from an analysis record."""

    startup_record = analysis.get(
        "startup_record",
        {},
    )

    company_data = startup_record.get(
        "company",
        {},
    )

    company_name = str(
        company_data.get(
            "company_name",
            company_data.get(
                "name",
                "Unnamed Startup",
            ),
        )
    ).strip()

    return company_name or "Unnamed Startup"


def get_dashboard_statistics() -> dict[str, Any]:
    """
    Calculate dashboard statistics from the analysis history.
    """

    history = st.session_state.analysis_history

    startup_count = len(history)
    low_risk_count = 0
    high_risk_count = 0
    total_score = 0.0

    for analysis in history:
        risk_report = analysis.get(
            "risk_report",
            {},
        )

        scoring_result = analysis.get(
            "scoring_result",
            {},
        )

        risk_level = str(
            risk_report.get(
                "overall_risk_level",
                "",
            )
        ).strip()

        if risk_level == "Low":
            low_risk_count += 1

        if risk_level in {
            "High",
            "Critical",
        }:
            high_risk_count += 1

        score = safe_float(
            scoring_result.get(
                "overall_score",
                scoring_result.get(
                    "total_score",
                    scoring_result.get(
                        "due_diligence_score",
                        0,
                    ),
                ),
            )
        )

        total_score += score

    average_score = (
        total_score / startup_count
        if startup_count > 0
        else 0.0
    )

    return {
        "startup_count": startup_count,
        "low_risk_count": low_risk_count,
        "high_risk_count": high_risk_count,
        "average_score": round(
            average_score,
            2,
        ),
    }


# ============================================================
# DASHBOARD COMPONENTS
# ============================================================

def display_dashboard_metrics() -> None:
    """Display high-level platform statistics."""

    statistics = get_dashboard_statistics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Startups Evaluated",
            value=statistics["startup_count"],
        )

    with col2:
        st.metric(
            label="Low-Risk Startups",
            value=statistics["low_risk_count"],
        )

    with col3:
        st.metric(
            label="High-Risk Startups",
            value=statistics["high_risk_count"],
        )

    with col4:
        st.metric(
            label="Average Score",
            value=(
                f"{statistics['average_score']:.2f}/100"
            ),
        )


def display_platform_capabilities() -> None:
    """Display the main platform capabilities."""

    st.subheader("Platform Capabilities")

    capability_col1, capability_col2, capability_col3 = (
        st.columns(3)
    )

    with capability_col1:
        st.info(
            """
            **Financial Analysis**

            Analyse revenue, expenses, profitability, burn rate,
            cash runway, liquidity, leverage and financial stability.
            """
        )

    with capability_col2:
        st.info(
            """
            **Risk Assessment**

            Identify financial, market, legal, technology,
            customer, funding and team-related risks.
            """
        )

    with capability_col3:
        st.info(
            """
            **Investment Insights**

            Generate category scores, risk findings, red flags,
            priority actions and an investment recommendation.
            """
        )


def display_latest_analysis() -> None:
    """Display a summary of the latest completed analysis."""

    latest_analysis = st.session_state.latest_analysis

    st.subheader("Latest Startup Analysis")

    if not latest_analysis:
        st.info(
            "No startup has been analysed yet. Open the "
            "Add Startup page to begin an assessment."
        )
        return

    company_name = get_company_name(
        latest_analysis
    )

    scoring_result = latest_analysis.get(
        "scoring_result",
        {},
    )

    risk_report = latest_analysis.get(
        "risk_report",
        {},
    )

    recommendation_report = latest_analysis.get(
        "recommendation_report",
        {},
    )

    due_diligence_score = safe_float(
        recommendation_report.get(
            "due_diligence_score",
            scoring_result.get(
                "overall_score",
                scoring_result.get(
                    "total_score",
                    0,
                ),
            ),
        )
    )

    risk_score = safe_float(
        recommendation_report.get(
            "overall_risk_score",
            risk_report.get(
                "overall_risk_score",
                0,
            ),
        )
    )

    risk_level = str(
        recommendation_report.get(
            "overall_risk_level",
            risk_report.get(
                "overall_risk_level",
                "Not Available",
            ),
        )
    ).strip()

    investment_decision = str(
        recommendation_report.get(
            "investment_decision",
            "Not Available",
        )
    ).strip()

    st.markdown(
        f"### {company_name}"
    )

    score_col, risk_col, level_col, decision_col = (
        st.columns(4)
    )

    with score_col:
        st.metric(
            label="Due-Diligence Score",
            value=f"{due_diligence_score:.2f}/100",
        )

    with risk_col:
        st.metric(
            label="Overall Risk Score",
            value=f"{risk_score:.2f}/100",
        )

    with level_col:
        st.metric(
            label="Risk Level",
            value=risk_level,
        )

    with decision_col:
        st.metric(
            label="Investment Decision",
            value=investment_decision,
        )

    executive_summary = str(
        recommendation_report.get(
            "executive_summary",
            "",
        )
    ).strip()

    if executive_summary:
        st.markdown("#### Executive Summary")
        st.write(executive_summary)

    red_flags = recommendation_report.get(
        "red_flags",
        [],
    )

    top_recommendations = recommendation_report.get(
        "top_recommendations",
        [],
    )

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.markdown("#### Material Red Flags")

        if not red_flags:
            st.success(
                "No critical or high-severity red flags "
                "were identified."
            )

        else:
            for red_flag in red_flags[:5]:
                severity = str(
                    red_flag.get(
                        "severity",
                        "High",
                    )
                )

                title = str(
                    red_flag.get(
                        "title",
                        "Risk requires attention",
                    )
                )

                category = str(
                    red_flag.get(
                        "category",
                        "General",
                    )
                )

                st.error(
                    f"**{severity}: {title}**\n\n"
                    f"Category: {category}"
                )

    with summary_col2:
        st.markdown("#### Top Recommended Actions")

        if not top_recommendations:
            st.success(
                "No immediate corrective actions are required."
            )

        else:
            for recommendation in (
                top_recommendations[:5]
            ):
                priority = str(
                    recommendation.get(
                        "priority",
                        "Low",
                    )
                )

                title = str(
                    recommendation.get(
                        "title",
                        "Recommended action",
                    )
                )

                action = str(
                    recommendation.get(
                        "action",
                        "",
                    )
                )

                st.warning(
                    f"**{priority}: {title}**\n\n"
                    f"{action}"
                )


def display_analysis_history() -> None:
    """Display a summary table of completed analyses."""

    history = st.session_state.analysis_history

    st.subheader("Analysis History")

    if not history:
        st.caption(
            "Completed startup analyses will appear here."
        )
        return

    history_rows: list[dict[str, Any]] = []

    for index, analysis in enumerate(
        reversed(history),
        start=1,
    ):
        scoring_result = analysis.get(
            "scoring_result",
            {},
        )

        risk_report = analysis.get(
            "risk_report",
            {},
        )

        recommendation_report = analysis.get(
            "recommendation_report",
            {},
        )

        score = safe_float(
            recommendation_report.get(
                "due_diligence_score",
                scoring_result.get(
                    "overall_score",
                    scoring_result.get(
                        "total_score",
                        0,
                    ),
                ),
            )
        )

        risk_score = safe_float(
            recommendation_report.get(
                "overall_risk_score",
                risk_report.get(
                    "overall_risk_score",
                    0,
                ),
            )
        )

        history_rows.append(
            {
                "S.No.": index,
                "Startup": get_company_name(
                    analysis
                ),
                "Due-Diligence Score": round(
                    score,
                    2,
                ),
                "Risk Score": round(
                    risk_score,
                    2,
                ),
                "Risk Level": risk_report.get(
                    "overall_risk_level",
                    "Not Available",
                ),
                "Investment Decision": (
                    recommendation_report.get(
                        "investment_decision",
                        "Not Available",
                    )
                ),
            }
        )

    st.dataframe(
        history_rows,
        use_container_width=True,
        hide_index=True,
    )


def display_sidebar() -> None:
    """Display application navigation and project details."""

    with st.sidebar:
        st.header("Navigation")

        st.page_link(
            "app.py",
            label="Dashboard",
            icon="🏠",
        )

        st.page_link(
            "pages/1_Add_Startup.py",
            label="Add Startup",
            icon="➕",
        )

        st.divider()

        st.markdown(
            """
            **Analysis Modules**

            - Financial Health
            - Founders & Team
            - Product & Technology
            - Market Opportunity
            - Customers & Traction
            - Funding Position
            - Legal & Compliance
            - Risk Assessment
            - Investment Recommendation
            """
        )

        st.divider()

        completed_count = len(
            st.session_state.analysis_history
        )

        st.metric(
            label="Session Analyses",
            value=completed_count,
        )

        st.caption(
            "IBM Internship Project · Group DS12"
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """Run the main Streamlit dashboard."""

    initialize_session_state()
    display_sidebar()

    st.title(
        "AI-Powered Startup Due Diligence Platform"
    )

    st.markdown(
        """
        Evaluate startup viability, financial health, growth
        potential, founder strength, regulatory compliance and
        investment risk using structured, data-driven analysis.
        """
    )

    st.divider()

    display_dashboard_metrics()

    st.divider()

    display_latest_analysis()

    st.divider()

    display_platform_capabilities()

    st.divider()

    display_analysis_history()

    st.divider()

    st.subheader("Development Status")

    st.progress(85)

    st.caption(
        "Financial metrics, compliance evaluation, category "
        "scoring, risk analysis and investment recommendation "
        "engines are complete. Frontend integration is in progress."
    )


if __name__ == "__main__":
    main()