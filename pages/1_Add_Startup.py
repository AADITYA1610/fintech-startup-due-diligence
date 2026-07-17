from __future__ import annotations

from datetime import date
from typing import Any

import streamlit as st

from src.financial_metrics import calculate_all_financial_metrics


st.set_page_config(
    page_title="Add Startup",
    page_icon="➕",
    layout="wide",
)


def initialize_session_state() -> None:
    """
    Create the startup_records list when the application
    runs for the first time.
    """

    if "startup_records" not in st.session_state:
        st.session_state.startup_records = []


def validate_startup_data(
    company_name: str,
    industry: str,
    founder_count: int,
    monthly_revenue: float,
    monthly_expenses: float,
    cash_balance: float,
) -> list[str]:
    """Validate important startup fields."""

    errors: list[str] = []

    if not company_name.strip():
        errors.append("Company name is required.")

    if not industry.strip():
        errors.append("Industry is required.")

    if founder_count < 1:
        errors.append("A startup must have at least one founder.")

    if monthly_revenue < 0:
        errors.append("Monthly revenue cannot be negative.")

    if monthly_expenses < 0:
        errors.append("Monthly expenses cannot be negative.")

    if cash_balance < 0:
        errors.append("Cash balance cannot be negative.")

    return errors


def format_currency(value: float | int | None) -> str:
    """
    Format a numeric value as Indian rupee currency.
    """

    if value is None:
        return "Not Available"

    return f"₹{value:,.2f}"


def format_ratio(value: float | None) -> str:
    """
    Format a ratio value to two decimal places.
    """

    if value is None:
        return "Not Available"

    return f"{value:.2f}"


def format_percentage(value: float | None) -> str:
    """
    Format a percentage value.
    """

    if value is None:
        return "Not Available"

    return f"{value:.2f}%"


def display_financial_warnings(warnings: list[str]) -> None:
    """
    Display financial warnings returned by the analysis engine.
    """

    if not warnings:
        st.success(
            "No major financial warning was identified "
            "from the entered data."
        )
        return

    st.warning(
        f"{len(warnings)} financial concern(s) were identified."
    )

    for warning in warnings:
        st.write(f"- {warning}")


def display_saved_record(record: dict[str, Any]) -> None:
    """
    Display a complete summary of the newly saved startup.
    """

    company = record["company"]
    financial = record["financial"]
    customers = record["customers"]
    metrics = record["calculated_metrics"]

    st.success("Startup information saved successfully.")

    # ---------------------------------------------------------
    # BASIC STARTUP SUMMARY
    # ---------------------------------------------------------
    st.subheader("Saved Startup Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.metric(
            label="Company",
            value=company["company_name"],
        )

    with summary_col2:
        st.metric(
            label="Industry",
            value=company["industry"],
        )

    with summary_col3:
        st.metric(
            label="Monthly Revenue",
            value=format_currency(financial["monthly_revenue"]),
        )

    with summary_col4:
        st.metric(
            label="Monthly Profit/Loss",
            value=format_currency(metrics["profit_loss"]),
        )

    st.divider()

    # ---------------------------------------------------------
    # FINANCIAL HEALTH SUMMARY
    # ---------------------------------------------------------
    st.subheader("Financial Health Assessment")

    health_col1, health_col2, health_col3, health_col4 = st.columns(4)

    with health_col1:
        st.metric(
            label="Financial Health Score",
            value=f"{metrics['financial_health_score']}/100",
        )

    with health_col2:
        st.metric(
            label="Financial Health",
            value=metrics["financial_health_label"],
        )

    with health_col3:
        st.metric(
            label="Monthly Burn Rate",
            value=format_currency(metrics["burn_rate"]),
        )

    with health_col4:
        runway = metrics["cash_runway_months"]

        if runway is None:
            runway_text = "No Current Burn"
        else:
            runway_text = f"{runway:.1f} months"

        st.metric(
            label="Cash Runway",
            value=runway_text,
        )

    # ---------------------------------------------------------
    # FINANCIAL RATIOS
    # ---------------------------------------------------------
    st.markdown("#### Important Financial Ratios")

    ratio_col1, ratio_col2, ratio_col3, ratio_col4 = st.columns(4)

    with ratio_col1:
        st.metric(
            label="Profit Margin",
            value=format_percentage(
                metrics["profit_margin_percentage"]
            ),
            help=(
                "Profit or loss expressed as a percentage "
                "of monthly revenue."
            ),
        )

    with ratio_col2:
        st.metric(
            label="Current Ratio",
            value=format_ratio(metrics["current_ratio"]),
            help=(
                "Current assets divided by current liabilities. "
                "A value above 1 generally means current assets "
                "are greater than current liabilities."
            ),
        )

    with ratio_col3:
        st.metric(
            label="Debt-to-Equity",
            value=format_ratio(metrics["debt_to_equity_ratio"]),
            help=(
                "Total debt divided by total equity. "
                "A lower value generally indicates lower dependence "
                "on borrowed money."
            ),
        )

    with ratio_col4:
        st.metric(
            label="Revenue/Expense Ratio",
            value=format_ratio(metrics["revenue_expense_ratio"]),
            help=(
                "Monthly revenue divided by monthly expenses. "
                "A value above 1 means revenue exceeds expenses."
            ),
        )

    customer_ratio_col1, customer_ratio_col2 = st.columns(2)

    with customer_ratio_col1:
        st.metric(
            label="LTV-to-CAC Ratio",
            value=format_ratio(metrics["ltv_cac_ratio"]),
            help=(
                "Customer lifetime value divided by customer "
                "acquisition cost."
            ),
        )

    with customer_ratio_col2:
        st.metric(
            label="Customer Churn Rate",
            value=format_percentage(customers["churn_rate"]),
            help=(
                "The percentage of customers lost during "
                "the measurement period."
            ),
        )

    # ---------------------------------------------------------
    # WARNINGS
    # ---------------------------------------------------------
    st.markdown("#### Financial Concerns")

    display_financial_warnings(
        metrics["financial_warnings"]
    )

    # ---------------------------------------------------------
    # COMPLETE INFORMATION
    # ---------------------------------------------------------
    with st.expander("View complete saved startup information"):
        st.json(record)


def main() -> None:
    """Run the startup data-entry page."""

    initialize_session_state()

    st.title("Add Startup for Due Diligence")

    st.write(
        """
        Enter the available information about the startup.
        The platform will use this information for financial analysis,
        risk assessment and investment scoring.
        """
    )

    st.info(
        """
        Fields marked with * are important for the initial assessment.
        Enter the most accurate information currently available.
        """
    )

    with st.form("startup_due_diligence_form"):
        company_tab, team_tab, product_tab, market_tab = st.tabs(
            [
                "Company",
                "Founders & Team",
                "Product",
                "Market",
            ]
        )

        financial_tab, customer_tab, funding_tab, legal_tab = st.tabs(
            [
                "Financial",
                "Customers",
                "Funding",
                "Legal & Risks",
            ]
        )

        # ---------------------------------------------------------
        # COMPANY INFORMATION
        # ---------------------------------------------------------
        with company_tab:
            st.subheader("Company Information")

            company_col1, company_col2 = st.columns(2)

            with company_col1:
                company_name = st.text_input(
                    "Company name *",
                    placeholder="Example: FinTrack Technologies",
                )

                registration_number = st.text_input(
                    "Registration number",
                    placeholder="Example: U72900XX2022PTC123456",
                )

                founding_date = st.date_input(
                    "Founding date",
                    value=date(2022, 1, 1),
                    max_value=date.today(),
                )

                headquarters = st.text_input(
                    "Headquarters",
                    placeholder="Example: Bengaluru, India",
                )

            with company_col2:
                industry = st.text_input(
                    "Industry *",
                    placeholder="Example: FinTech",
                )

                startup_stage = st.selectbox(
                    "Startup stage",
                    [
                        "Idea Stage",
                        "Pre-Seed",
                        "Seed",
                        "Series A",
                        "Series B",
                        "Series C or Later",
                        "Growth Stage",
                    ],
                )

                registration_status = st.selectbox(
                    "Registration status",
                    [
                        "Registered",
                        "Registration in Progress",
                        "Not Registered",
                        "Information Not Available",
                    ],
                )

                employee_count = st.number_input(
                    "Number of employees",
                    min_value=0,
                    value=1,
                    step=1,
                )

            website = st.text_input(
                "Company website",
                placeholder="https://example.com",
            )

            company_description = st.text_area(
                "Company description",
                placeholder=(
                    "Briefly explain what the startup does and "
                    "which customers it serves."
                ),
                height=120,
            )

        # ---------------------------------------------------------
        # FOUNDERS AND TEAM
        # ---------------------------------------------------------
        with team_tab:
            st.subheader("Founders and Team")

            team_col1, team_col2 = st.columns(2)

            with team_col1:
                founder_count = st.number_input(
                    "Number of founders *",
                    min_value=1,
                    value=1,
                    step=1,
                )

                founder_experience_years = st.number_input(
                    "Average founder experience in years",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                )

                previous_startup_experience = st.selectbox(
                    "Do the founders have previous startup experience?",
                    [
                        "Yes",
                        "No",
                        "Partially",
                        "Information Not Available",
                    ],
                )

                industry_experience = st.number_input(
                    "Average industry experience in years",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                )

            with team_col2:
                technical_team_strength = st.slider(
                    "Technical team strength",
                    min_value=1,
                    max_value=10,
                    value=5,
                    help="1 means very weak and 10 means very strong.",
                )

                business_team_strength = st.slider(
                    "Business team strength",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

                team_stability = st.slider(
                    "Team stability",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

                key_person_dependency = st.selectbox(
                    "Key-person dependency risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

            founder_details = st.text_area(
                "Founder and key team details",
                placeholder=(
                    "Mention founder names, education, experience, "
                    "roles and relevant achievements."
                ),
                height=150,
            )

        # ---------------------------------------------------------
        # PRODUCT INFORMATION
        # ---------------------------------------------------------
        with product_tab:
            st.subheader("Product or Service")

            product_name = st.text_input(
                "Product or service name",
                placeholder="Example: FinTrack Expense Manager",
            )

            problem_statement = st.text_area(
                "What problem does the product solve?",
                placeholder="Describe the customer problem clearly.",
                height=120,
            )

            product_description = st.text_area(
                "Product or service description",
                placeholder="Explain how the product solves the problem.",
                height=120,
            )

            product_col1, product_col2 = st.columns(2)

            with product_col1:
                product_stage = st.selectbox(
                    "Product stage",
                    [
                        "Concept Only",
                        "Prototype",
                        "Minimum Viable Product",
                        "Early Customers",
                        "Market Ready",
                        "Scaling",
                    ],
                )

                working_mvp = st.selectbox(
                    "Is a working MVP available?",
                    [
                        "Yes",
                        "No",
                        "Under Development",
                        "Information Not Available",
                    ],
                )

                intellectual_property = st.selectbox(
                    "Intellectual property status",
                    [
                        "Patent Granted",
                        "Patent Filed",
                        "Trademark Registered",
                        "Internally Developed Technology",
                        "No Intellectual Property",
                        "Information Not Available",
                    ],
                )

            with product_col2:
                product_uniqueness = st.slider(
                    "Product uniqueness",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

                technology_readiness = st.slider(
                    "Technology readiness",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

                product_scalability = st.slider(
                    "Product scalability",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

            unique_selling_proposition = st.text_area(
                "Unique selling proposition",
                placeholder=(
                    "Explain what makes the product different "
                    "from competing solutions."
                ),
                height=100,
            )

        # ---------------------------------------------------------
        # MARKET INFORMATION
        # ---------------------------------------------------------
        with market_tab:
            st.subheader("Market Opportunity")

            target_customers = st.text_area(
                "Target customers",
                placeholder=(
                    "Example: Small and medium-sized Indian businesses "
                    "with 10–100 employees."
                ),
                height=100,
            )

            market_col1, market_col2 = st.columns(2)

            with market_col1:
                total_addressable_market = st.number_input(
                    "Total addressable market in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                )

                serviceable_available_market = st.number_input(
                    "Serviceable available market in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                )

                market_growth_rate = st.number_input(
                    "Estimated annual market growth rate (%)",
                    min_value=-100.0,
                    max_value=1000.0,
                    value=0.0,
                    step=1.0,
                )

            with market_col2:
                competitor_count = st.number_input(
                    "Number of major competitors",
                    min_value=0,
                    value=0,
                    step=1,
                )

                competition_level = st.selectbox(
                    "Competition level",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Very High",
                        "Information Not Available",
                    ],
                )

                competitive_advantage_strength = st.slider(
                    "Competitive advantage strength",
                    min_value=1,
                    max_value=10,
                    value=5,
                )

            competitor_details = st.text_area(
                "Major competitors",
                placeholder=(
                    "Mention competitor names and important differences."
                ),
                height=120,
            )

        # ---------------------------------------------------------
        # FINANCIAL INFORMATION
        # ---------------------------------------------------------
        with financial_tab:
            st.subheader("Financial Health")

            st.caption(
                "Enter monthly figures wherever applicable."
            )

            financial_col1, financial_col2 = st.columns(2)

            with financial_col1:
                monthly_revenue = st.number_input(
                    "Monthly revenue in ₹ *",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

                monthly_expenses = st.number_input(
                    "Monthly expenses in ₹ *",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

                cash_balance = st.number_input(
                    "Available cash balance in ₹ *",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

                gross_profit = st.number_input(
                    "Monthly gross profit in ₹",
                    value=0.0,
                    step=10000.0,
                )

            with financial_col2:
                current_assets = st.number_input(
                    "Current assets in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

                current_liabilities = st.number_input(
                    "Current liabilities in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

                total_debt = st.number_input(
                    "Total debt in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

                total_equity = st.number_input(
                    "Total equity in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=10000.0,
                )

            revenue_growth_rate = st.number_input(
                "Revenue growth rate (%)",
                min_value=-100.0,
                max_value=1000.0,
                value=0.0,
                step=1.0,
            )

            financial_records_available = st.selectbox(
                "Are financial records available for verification?",
                [
                    "Audited Records Available",
                    "Unaudited Records Available",
                    "Partial Records Available",
                    "No Records Available",
                ],
            )

        # ---------------------------------------------------------
        # CUSTOMER INFORMATION
        # ---------------------------------------------------------
        with customer_tab:
            st.subheader("Customers and Growth")

            customer_col1, customer_col2 = st.columns(2)

            with customer_col1:
                total_customers = st.number_input(
                    "Total customers",
                    min_value=0,
                    value=0,
                    step=1,
                )

                new_customers_monthly = st.number_input(
                    "New customers acquired per month",
                    min_value=0,
                    value=0,
                    step=1,
                )

                customers_lost_monthly = st.number_input(
                    "Customers lost per month",
                    min_value=0,
                    value=0,
                    step=1,
                )

                customer_growth_rate = st.number_input(
                    "Customer growth rate (%)",
                    min_value=-100.0,
                    max_value=1000.0,
                    value=0.0,
                    step=1.0,
                )

            with customer_col2:
                retention_rate = st.number_input(
                    "Customer retention rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                )

                churn_rate = st.number_input(
                    "Customer churn rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                )

                customer_acquisition_cost = st.number_input(
                    "Customer acquisition cost in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                )

                customer_lifetime_value = st.number_input(
                    "Customer lifetime value in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                )

            major_customer_dependency = st.selectbox(
                "Dependency on one or a few major customers",
                [
                    "Low",
                    "Moderate",
                    "High",
                    "Information Not Available",
                ],
            )

        # ---------------------------------------------------------
        # FUNDING INFORMATION
        # ---------------------------------------------------------
        with funding_tab:
            st.subheader("Funding")

            funding_col1, funding_col2 = st.columns(2)

            with funding_col1:
                previous_funding = st.number_input(
                    "Total previous funding received in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                )

                number_of_funding_rounds = st.number_input(
                    "Number of previous funding rounds",
                    min_value=0,
                    value=0,
                    step=1,
                )

                current_valuation = st.number_input(
                    "Current startup valuation in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                )

            with funding_col2:
                funding_sought = st.number_input(
                    "Funding currently sought in ₹",
                    min_value=0.0,
                    value=0.0,
                    step=100000.0,
                )

                equity_offered = st.number_input(
                    "Equity offered (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=0.5,
                )

                investor_count = st.number_input(
                    "Number of existing investors",
                    min_value=0,
                    value=0,
                    step=1,
                )

            investor_details = st.text_area(
                "Previous or existing investor details",
                placeholder="Mention investor names and funding rounds.",
                height=100,
            )

            use_of_funds = st.text_area(
                "Planned use of new funding",
                placeholder=(
                    "Example: Product development, recruitment, "
                    "marketing and geographical expansion."
                ),
                height=120,
            )

        # ---------------------------------------------------------
        # LEGAL AND RISK INFORMATION
        # ---------------------------------------------------------
        with legal_tab:
            st.subheader("Legal, Compliance and Risks")

            legal_col1, legal_col2 = st.columns(2)

            with legal_col1:
                required_licenses_available = st.selectbox(
                    "Are all required licences available?",
                    [
                        "Yes",
                        "No",
                        "Partially",
                        "Not Applicable",
                        "Information Not Available",
                    ],
                )

                tax_compliance = st.selectbox(
                    "Tax compliance status",
                    [
                        "Compliant",
                        "Partially Compliant",
                        "Non-Compliant",
                        "Information Not Available",
                    ],
                )

                founder_agreement = st.selectbox(
                    "Is a founder agreement available?",
                    [
                        "Yes",
                        "No",
                        "Information Not Available",
                    ],
                )

                employee_agreements = st.selectbox(
                    "Are employee agreements available?",
                    [
                        "Yes",
                        "No",
                        "Partially",
                        "Information Not Available",
                    ],
                )

            with legal_col2:
                pending_lawsuits = st.selectbox(
                    "Are there any pending lawsuits?",
                    [
                        "No",
                        "Yes",
                        "Information Not Available",
                    ],
                )

                regulatory_issues = st.selectbox(
                    "Are there any regulatory issues?",
                    [
                        "No",
                        "Yes",
                        "Information Not Available",
                    ],
                )

                privacy_policy_available = st.selectbox(
                    "Is a data privacy policy available?",
                    [
                        "Yes",
                        "No",
                        "Not Applicable",
                        "Information Not Available",
                    ],
                )

                data_security_measures = st.selectbox(
                    "Data security measures",
                    [
                        "Strong",
                        "Adequate",
                        "Weak",
                        "Not Applicable",
                        "Information Not Available",
                    ],
                )

            legal_issue_details = st.text_area(
                "Legal or compliance issue details",
                placeholder=(
                    "Describe any lawsuits, regulatory concerns, "
                    "licence issues or unresolved obligations."
                ),
                height=120,
            )

            st.markdown("#### Initial Risk Indicators")

            risk_col1, risk_col2 = st.columns(2)

            with risk_col1:
                financial_risk_indicator = st.selectbox(
                    "Financial risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

                market_risk_indicator = st.selectbox(
                    "Market risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

                technology_risk_indicator = st.selectbox(
                    "Technology risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

            with risk_col2:
                team_risk_indicator = st.selectbox(
                    "Team dependency risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

                legal_risk_indicator = st.selectbox(
                    "Legal risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

                customer_risk_indicator = st.selectbox(
                    "Customer risk",
                    [
                        "Low",
                        "Moderate",
                        "High",
                        "Information Not Available",
                    ],
                )

        st.divider()

        submit_button = st.form_submit_button(
            "Save Startup Information",
            type="primary",
            use_container_width=True,
        )

    if submit_button:
        validation_errors = validate_startup_data(
            company_name=company_name,
            industry=industry,
            founder_count=founder_count,
            monthly_revenue=monthly_revenue,
            monthly_expenses=monthly_expenses,
            cash_balance=cash_balance,
        )

        if validation_errors:
            st.error("Please correct the following problems:")

            for error in validation_errors:
                st.write(f"- {error}")

            return

        financial_metrics = calculate_all_financial_metrics(
            monthly_revenue=monthly_revenue,
            monthly_expenses=monthly_expenses,
            cash_balance=cash_balance,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            total_debt=total_debt,
            total_equity=total_equity,
            revenue_growth_rate=revenue_growth_rate,
            customer_lifetime_value=customer_lifetime_value,
            customer_acquisition_cost=customer_acquisition_cost,
            churn_rate=churn_rate,
            financial_records_available=financial_records_available,
        )

        startup_record = {
            "company": {
                "company_name": company_name.strip(),
                "registration_number": registration_number.strip(),
                "founding_date": str(founding_date),
                "industry": industry.strip(),
                "startup_stage": startup_stage,
                "registration_status": registration_status,
                "employee_count": employee_count,
                "headquarters": headquarters.strip(),
                "website": website.strip(),
                "description": company_description.strip(),
            },
            "founders_and_team": {
                "founder_count": founder_count,
                "founder_experience_years": founder_experience_years,
                "previous_startup_experience": (
                    previous_startup_experience
                ),
                "industry_experience_years": industry_experience,
                "technical_team_strength": technical_team_strength,
                "business_team_strength": business_team_strength,
                "team_stability": team_stability,
                "key_person_dependency": key_person_dependency,
                "founder_details": founder_details.strip(),
            },
            "product": {
                "product_name": product_name.strip(),
                "problem_statement": problem_statement.strip(),
                "product_description": product_description.strip(),
                "product_stage": product_stage,
                "working_mvp": working_mvp,
                "intellectual_property": intellectual_property,
                "product_uniqueness": product_uniqueness,
                "technology_readiness": technology_readiness,
                "product_scalability": product_scalability,
                "unique_selling_proposition": (
                    unique_selling_proposition.strip()
                ),
            },
            "market": {
                "target_customers": target_customers.strip(),
                "total_addressable_market": total_addressable_market,
                "serviceable_available_market": (
                    serviceable_available_market
                ),
                "market_growth_rate": market_growth_rate,
                "competitor_count": competitor_count,
                "competition_level": competition_level,
                "competitive_advantage_strength": (
                    competitive_advantage_strength
                ),
                "competitor_details": competitor_details.strip(),
            },
            "financial": {
                "monthly_revenue": monthly_revenue,
                "monthly_expenses": monthly_expenses,
                "cash_balance": cash_balance,
                "gross_profit": gross_profit,
                "current_assets": current_assets,
                "current_liabilities": current_liabilities,
                "total_debt": total_debt,
                "total_equity": total_equity,
                "revenue_growth_rate": revenue_growth_rate,
                "financial_records_available": (
                    financial_records_available
                ),
            },
            "customers": {
                "total_customers": total_customers,
                "new_customers_monthly": new_customers_monthly,
                "customers_lost_monthly": customers_lost_monthly,
                "customer_growth_rate": customer_growth_rate,
                "retention_rate": retention_rate,
                "churn_rate": churn_rate,
                "customer_acquisition_cost": (
                    customer_acquisition_cost
                ),
                "customer_lifetime_value": customer_lifetime_value,
                "major_customer_dependency": (
                    major_customer_dependency
                ),
            },
            "funding": {
                "previous_funding": previous_funding,
                "number_of_funding_rounds": number_of_funding_rounds,
                "current_valuation": current_valuation,
                "funding_sought": funding_sought,
                "equity_offered": equity_offered,
                "investor_count": investor_count,
                "investor_details": investor_details.strip(),
                "use_of_funds": use_of_funds.strip(),
            },
            "legal_and_compliance": {
                "required_licenses_available": (
                    required_licenses_available
                ),
                "tax_compliance": tax_compliance,
                "founder_agreement": founder_agreement,
                "employee_agreements": employee_agreements,
                "pending_lawsuits": pending_lawsuits,
                "regulatory_issues": regulatory_issues,
                "privacy_policy_available": (
                    privacy_policy_available
                ),
                "data_security_measures": data_security_measures,
                "legal_issue_details": legal_issue_details.strip(),
            },
            "initial_risks": {
                "financial_risk": financial_risk_indicator,
                "market_risk": market_risk_indicator,
                "technology_risk": technology_risk_indicator,
                "team_risk": team_risk_indicator,
                "legal_risk": legal_risk_indicator,
                "customer_risk": customer_risk_indicator,
            },
            "calculated_metrics": financial_metrics,
        }

        st.session_state.startup_records.append(startup_record)

        display_saved_record(startup_record)

    st.divider()

    st.caption(
        f"Startups saved during this session: "
        f"{len(st.session_state.startup_records)}"
    )


if __name__ == "__main__":
    main()