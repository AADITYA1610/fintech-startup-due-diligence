from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="Startup Due Diligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Run the main Streamlit application."""

    st.title("AI-Powered Startup Due Diligence Platform")

    st.markdown(
        """
        Evaluate startup viability, financial health, growth potential,
        founder strength and investment risk using data-driven analysis.
        """
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Startups Evaluated",
            value="0",
        )

    with col2:
        st.metric(
            label="Low-Risk Startups",
            value="0",
        )

    with col3:
        st.metric(
            label="High-Risk Startups",
            value="0",
        )

    with col4:
        st.metric(
            label="Average Score",
            value="0/100",
        )

    st.subheader("Platform Capabilities")

    capability_col1, capability_col2, capability_col3 = st.columns(3)

    with capability_col1:
        st.info(
            """
            **Financial Analysis**

            Analyse revenue, expenses, profitability, burn rate,
            cash runway and financial stability.
            """
        )

    with capability_col2:
        st.info(
            """
            **Risk Assessment**

            Identify financial, market, legal, technology,
            customer and team-related risks.
            """
        )

    with capability_col3:
        st.info(
            """
            **Investment Insights**

            Generate category scores, an overall investment score
            and a structured recommendation.
            """
        )

    st.subheader("Development Status")

    st.progress(10)

    st.caption(
        "Project setup completed. Startup data-entry and analysis modules "
        "will be added next."
    )

    with st.sidebar:
        st.header("Navigation")

        st.page_link(
            "app.py",
            label="Dashboard",
            icon="🏠",
        )

        st.divider()

        st.markdown(
            """
            **Upcoming Modules**

            - Add Startup
            - Financial Analysis
            - Market Analysis
            - Risk Assessment
            - ML Prediction
            - Report Generation
            """
        )

        st.divider()

        st.caption("IBM Internship Project · Group DS12")


if __name__ == "__main__":
    main()