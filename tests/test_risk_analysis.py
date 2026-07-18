import pytest

from src.compliance_engine import calculate_compliance_score
from src.financial_metrics import calculate_all_financial_metrics
from src.risk_analysis import (
    analyze_compliance_risk,
    analyze_financial_risk,
    classify_risk_level,
    create_risk_finding,
)
import src.risk_analysis as risk_analysis

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_healthy_startup_data() -> dict:
    """
    Return sample startup data representing a financially healthy
    and compliant FinTech startup.
    """

    return {
        # Financial information
        "monthly_revenue": 500000,
        "monthly_expenses": 300000,
        "cash_balance": 3000000,
        "current_assets": 2000000,
        "current_liabilities": 800000,
        "total_debt": 500000,
        "total_equity": 2000000,
        "revenue_growth_rate": 25,
        "customer_lifetime_value": 15000,
        "customer_acquisition_cost": 3000,
        "churn_rate": 5,
        "financial_records_available": (
            "Audited Records Available"
        ),

        # Regulatory information
        "regulator_identified": True,
        "regulatory_registration": True,
        "required_licenses": True,
        "regulatory_penalties": 0,

        # KYC and AML
        "kyc_implemented": True,
        "aml_implemented": True,
        "transaction_monitoring": True,
        "suspicious_activity_process": True,

        # Data security
        "data_encryption": True,
        "security_audit": True,
        "pci_dss_compliant": True,
        "access_controls": True,
        "incident_response_plan": True,

        # Fraud prevention
        "fraud_detection": True,
        "fraud_team": True,
        "fraud_incidents": 0,

        # Privacy and legal controls
        "privacy_policy": True,
        "customer_consent": True,
        "data_retention_policy": True,
        "data_breaches": 0,
    }


def calculate_financial_result(
    startup_data: dict,
) -> dict:
    """
    Calculate financial metrics from sample startup data.
    """

    return calculate_all_financial_metrics(
        monthly_revenue=startup_data["monthly_revenue"],
        monthly_expenses=startup_data["monthly_expenses"],
        cash_balance=startup_data["cash_balance"],
        current_assets=startup_data["current_assets"],
        current_liabilities=startup_data[
            "current_liabilities"
        ],
        total_debt=startup_data["total_debt"],
        total_equity=startup_data["total_equity"],
        revenue_growth_rate=startup_data[
            "revenue_growth_rate"
        ],
        customer_lifetime_value=startup_data[
            "customer_lifetime_value"
        ],
        customer_acquisition_cost=startup_data[
            "customer_acquisition_cost"
        ],
        churn_rate=startup_data["churn_rate"],
        financial_records_available=startup_data[
            "financial_records_available"
        ],
    )


# ============================================================
# RISK UTILITY TESTS
# ============================================================

def test_create_risk_finding_returns_expected_structure():
    """
    A risk finding should contain all required fields.
    """

    finding = create_risk_finding(
        category="Financial Risk",
        title="Low cash runway",
        description="Cash runway is below six months.",
        severity="High",
        impact="Operations may be disrupted.",
        recommendation="Secure additional working capital.",
    )

    assert finding == {
        "category": "Financial Risk",
        "title": "Low cash runway",
        "description": "Cash runway is below six months.",
        "severity": "High",
        "impact": "Operations may be disrupted.",
        "recommendation": (
            "Secure additional working capital."
        ),
    }


def test_create_risk_finding_rejects_invalid_severity():
    """
    The risk engine should reject unsupported severity labels.
    """

    with pytest.raises(ValueError):
        create_risk_finding(
            category="Financial Risk",
            title="Sample risk",
            description="Sample description",
            severity="Very Dangerous",
            impact="Sample impact",
            recommendation="Sample recommendation",
        )


@pytest.mark.parametrize(
    ("risk_score", "expected_level"),
    [
        (0, "Low"),
        (29.99, "Low"),
        (30, "Medium"),
        (54.99, "Medium"),
        (55, "High"),
        (74.99, "High"),
        (75, "Critical"),
        (100, "Critical"),
    ],
)
def test_classify_risk_level_boundaries(
    risk_score,
    expected_level,
):
    """
    Risk-score thresholds should produce the correct labels.
    """

    assert classify_risk_level(risk_score) == expected_level


def test_classify_risk_level_handles_scores_outside_range():
    """
    Values below zero and above one hundred should be safely limited.
    """

    assert classify_risk_level(-20) == "Low"
    assert classify_risk_level(150) == "Critical"


# ============================================================
# FINANCIAL RISK TESTS
# ============================================================

def test_healthy_startup_has_low_financial_risk():
    """
    A profitable startup with strong liquidity and audited records
    should receive a low financial-risk result.
    """

    startup_data = create_healthy_startup_data()
    financial_result = calculate_financial_result(
        startup_data
    )

    result = analyze_financial_risk(
        startup_data=startup_data,
        financial_result=financial_result,
    )

    assert result["score"] < 30
    assert result["level"] == "Low"
    assert isinstance(result["findings"], list)
    assert isinstance(result["positive_signals"], list)
    assert len(result["positive_signals"]) > 0


def test_cash_runway_below_three_months_is_critical():
    """
    Cash runway below three months should create a critical finding.
    """

    startup_data = create_healthy_startup_data()

    startup_data["monthly_revenue"] = 100000
    startup_data["monthly_expenses"] = 300000
    startup_data["cash_balance"] = 400000

    financial_result = calculate_financial_result(
        startup_data
    )

    result = analyze_financial_risk(
        startup_data=startup_data,
        financial_result=financial_result,
    )

    critical_titles = [
        finding["title"]
        for finding in result["findings"]
        if finding["severity"] == "Critical"
    ]

    assert "Critically low cash runway" in critical_titles


def test_no_monthly_revenue_creates_financial_risk():
    """
    A startup with no monthly revenue should receive a finding.
    """

    startup_data = create_healthy_startup_data()

    startup_data["monthly_revenue"] = 0
    startup_data["monthly_expenses"] = 200000
    startup_data["cash_balance"] = 2000000

    financial_result = calculate_financial_result(
        startup_data
    )

    result = analyze_financial_risk(
        startup_data=startup_data,
        financial_result=financial_result,
    )

    finding_titles = [
        finding["title"]
        for finding in result["findings"]
    ]

    assert "No current monthly revenue" in finding_titles


def test_high_debt_to_equity_creates_high_risk_finding():
    """
    A debt-to-equity ratio above three should create a high-risk finding.
    """

    startup_data = create_healthy_startup_data()

    startup_data["total_debt"] = 4000000
    startup_data["total_equity"] = 1000000

    financial_result = calculate_financial_result(
        startup_data
    )

    result = analyze_financial_risk(
        startup_data=startup_data,
        financial_result=financial_result,
    )

    matching_findings = [
        finding
        for finding in result["findings"]
        if finding["title"]
        == "Very high debt-to-equity ratio"
    ]

    assert len(matching_findings) == 1
    assert matching_findings[0]["severity"] == "High"


def test_unavailable_financial_records_create_high_risk():
    """
    Missing financial records should create a high-risk finding.
    """

    startup_data = create_healthy_startup_data()

    startup_data["financial_records_available"] = (
        "No Records Available"
    )

    financial_result = calculate_financial_result(
        startup_data
    )

    result = analyze_financial_risk(
        startup_data=startup_data,
        financial_result=financial_result,
    )

    matching_findings = [
        finding
        for finding in result["findings"]
        if finding["title"] == "Financial records unavailable"
    ]

    assert len(matching_findings) == 1
    assert matching_findings[0]["severity"] == "High"


def test_financial_risk_score_never_exceeds_one_hundred():
    """
    Multiple financial problems should not produce a score above 100.
    """

    startup_data = create_healthy_startup_data()

    startup_data.update(
        {
            "monthly_revenue": 0,
            "monthly_expenses": 500000,
            "cash_balance": 100000,
            "current_assets": 100000,
            "current_liabilities": 1000000,
            "total_debt": 5000000,
            "total_equity": 100000,
            "customer_lifetime_value": 500,
            "customer_acquisition_cost": 5000,
            "financial_records_available": (
                "No Records Available"
            ),
        }
    )

    financial_result = calculate_financial_result(
        startup_data
    )

    result = analyze_financial_risk(
        startup_data=startup_data,
        financial_result=financial_result,
    )

    assert 0 <= result["score"] <= 100


# ============================================================
# COMPLIANCE RISK TESTS
# ============================================================

def test_fully_compliant_startup_has_low_compliance_risk():
    """
    A startup with all compliance controls should have low risk.
    """

    startup_data = create_healthy_startup_data()

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    assert compliance_result["compliance_score"] == 100
    assert result["score"] == 0
    assert result["level"] == "Low"
    assert result["findings"] == []
    assert len(result["positive_signals"]) > 0


def test_missing_required_licence_creates_critical_risk():
    """
    Missing required licences should create a critical risk
    and force the compliance-risk score to at least 80.
    """

    startup_data = create_healthy_startup_data()
    startup_data["required_licenses"] = False

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    critical_titles = [
        finding["title"]
        for finding in result["findings"]
        if finding["severity"] == "Critical"
    ]

    assert (
        "Required operating licences not confirmed"
        in critical_titles
    )

    assert result["score"] >= 80
    assert result["level"] == "Critical"


def test_missing_aml_controls_create_high_risk():
    """
    Missing AML controls should create a high-risk finding.
    """

    startup_data = create_healthy_startup_data()
    startup_data["aml_implemented"] = False

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    matching_findings = [
        finding
        for finding in result["findings"]
        if finding["title"] == "AML controls not confirmed"
    ]

    assert len(matching_findings) == 1
    assert matching_findings[0]["severity"] == "High"
    assert result["score"] >= 65


def test_single_data_breach_creates_high_risk():
    """
    One historical data breach should create a high-risk finding.
    """

    startup_data = create_healthy_startup_data()
    startup_data["data_breaches"] = 1

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    matching_findings = [
        finding
        for finding in result["findings"]
        if finding["title"] == "Historical data breach reported"
    ]

    assert len(matching_findings) == 1
    assert matching_findings[0]["severity"] == "High"
    assert result["score"] >= 70


def test_multiple_data_breaches_create_critical_risk():
    """
    Two or more data breaches should create a critical finding.
    """

    startup_data = create_healthy_startup_data()
    startup_data["data_breaches"] = 2

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    matching_findings = [
        finding
        for finding in result["findings"]
        if finding["title"] == "Historical data breach reported"
    ]

    assert len(matching_findings) == 1
    assert matching_findings[0]["severity"] == "Critical"
    assert result["score"] >= 85
    assert result["level"] == "Critical"


def test_three_regulatory_penalties_create_critical_risk():
    """
    Three or more regulatory penalties should create critical risk.
    """

    startup_data = create_healthy_startup_data()
    startup_data["regulatory_penalties"] = 3

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    matching_findings = [
        finding
        for finding in result["findings"]
        if finding["title"] == "Regulatory penalties reported"
    ]

    assert len(matching_findings) == 1
    assert matching_findings[0]["severity"] == "Critical"
    assert result["score"] >= 80


def test_compliance_risk_score_never_exceeds_one_hundred():
    """
    A startup with every compliance failure should still receive
    a maximum score of 100.
    """

    startup_data = create_healthy_startup_data()

    startup_data.update(
        {
            "regulator_identified": False,
            "regulatory_registration": False,
            "required_licenses": False,
            "regulatory_penalties": 10,
            "kyc_implemented": False,
            "aml_implemented": False,
            "transaction_monitoring": False,
            "suspicious_activity_process": False,
            "data_encryption": False,
            "security_audit": False,
            "pci_dss_compliant": False,
            "access_controls": False,
            "incident_response_plan": False,
            "fraud_detection": False,
            "fraud_team": False,
            "fraud_incidents": 10,
            "privacy_policy": False,
            "customer_consent": False,
            "data_retention_policy": False,
            "data_breaches": 5,
        }
    )

    compliance_result = calculate_compliance_score(
        startup_data
    )

    result = analyze_compliance_risk(
        startup_data=startup_data,
        compliance_result=compliance_result,
    )

    assert 0 <= result["score"] <= 100
    assert result["level"] == "Critical"

# ============================================================
# SOURCE SCORE AND HELPER TESTS
# ============================================================

def test_clamp_source_score_limits_values():
    assert risk_analysis.clamp_source_score(-20) == 0.0
    assert risk_analysis.clamp_source_score(50) == 50.0
    assert risk_analysis.clamp_source_score(150) == 100.0


def test_group_findings_by_severity():
    findings = [
        {"severity": "High", "title": "High issue"},
        {"severity": "Critical", "title": "Critical issue"},
        {"severity": "Medium", "title": "Medium issue"},
        {"severity": "Low", "title": "Low issue"},
    ]

    grouped = risk_analysis._group_findings_by_severity(
        findings
    )

    assert len(grouped["Critical"]) == 1
    assert len(grouped["High"]) == 1
    assert len(grouped["Medium"]) == 1
    assert len(grouped["Low"]) == 1


def test_sort_findings_by_severity():
    findings = [
        {"severity": "Low"},
        {"severity": "Critical"},
        {"severity": "Medium"},
        {"severity": "High"},
    ]

    sorted_findings = (
        risk_analysis._sort_findings_by_severity(
            findings
        )
    )

    severities = [
        finding["severity"]
        for finding in sorted_findings
    ]

    assert severities == [
        "Critical",
        "High",
        "Medium",
        "Low",
    ]


def test_count_findings_by_severity():
    findings = [
        {"severity": "Critical"},
        {"severity": "High"},
        {"severity": "High"},
        {"severity": "Medium"},
        {"severity": "Low"},
    ]

    counts = risk_analysis._count_findings_by_severity(
        findings
    )

    assert counts == {
        "Critical": 1,
        "High": 2,
        "Medium": 1,
        "Low": 1,
    }


# ============================================================
# TEAM RISK TESTS
# ============================================================

def test_healthy_team_has_low_risk():
    team_data = {
        "founder_count": 3,
        "founder_experience_years": 7,
        "previous_startup_experience": "Yes",
        "industry_experience_years": 6,
        "technical_team_strength": 9,
        "business_team_strength": 8,
        "team_stability": 9,
        "key_person_dependency": "Low",
        "founder_details": (
            "Experienced founders with technical, financial, "
            "and business backgrounds."
        ),
    }

    result = risk_analysis.analyze_team_risk(
        team_data=team_data,
        team_score=90,
        initial_risk="Low",
    )

    assert result["score"] == 10.0
    assert result["level"] == "Low"
    assert result["findings"] == []
    assert len(result["positive_signals"]) >= 5
    assert result["source_score"] == 90.0


def test_weak_team_produces_high_risk_findings():
    team_data = {
        "founder_count": 1,
        "founder_experience_years": 0,
        "previous_startup_experience": "No",
        "industry_experience_years": 0,
        "technical_team_strength": 2,
        "business_team_strength": 2,
        "team_stability": 2,
        "key_person_dependency": "High",
        "founder_details": "",
    }

    result = risk_analysis.analyze_team_risk(
        team_data=team_data,
        team_score=30,
        initial_risk="High",
    )

    assert result["score"] >= 70
    assert result["level"] in {"High", "Critical"}
    assert len(result["findings"]) >= 7

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert "Single-founder dependency" in finding_titles
    assert "Weak technical team" in finding_titles
    assert "Weak business team" in finding_titles
    assert "High key-person dependency" in finding_titles


def test_team_manual_high_risk_applies_minimum_floor():
    team_data = {
        "founder_count": 3,
        "founder_experience_years": 7,
        "previous_startup_experience": "Yes",
        "industry_experience_years": 7,
        "technical_team_strength": 9,
        "business_team_strength": 9,
        "team_stability": 9,
        "key_person_dependency": "Low",
        "founder_details": "Complete founder details.",
    }

    result = risk_analysis.analyze_team_risk(
        team_data=team_data,
        team_score=95,
        initial_risk="High",
    )

    assert result["score"] >= 55
    assert result["level"] in {"High", "Critical"}


# ============================================================
# PRODUCT AND TECHNOLOGY RISK TESTS
# ============================================================

def test_market_ready_product_has_low_risk():
    product_data = {
        "product_name": "FinTech Platform",
        "problem_statement": (
            "Investors lack structured startup due diligence."
        ),
        "product_description": (
            "An automated startup evaluation and risk-analysis platform."
        ),
        "product_stage": "Market Ready",
        "working_mvp": "Yes",
        "intellectual_property": "Patent Granted",
        "product_uniqueness": 9,
        "technology_readiness": 9,
        "product_scalability": 9,
        "unique_selling_proposition": (
            "Combines financial, compliance, and startup-risk analysis."
        ),
    }

    result = (
        risk_analysis.analyze_product_technology_risk(
            product_data=product_data,
            product_score=90,
            initial_risk="Low",
        )
    )

    assert result["score"] == 10.0
    assert result["level"] == "Low"
    assert result["findings"] == []
    assert len(result["positive_signals"]) >= 5


def test_concept_product_without_mvp_has_high_risk():
    product_data = {
        "product_name": "",
        "problem_statement": "",
        "product_description": "",
        "product_stage": "Concept Only",
        "working_mvp": "No",
        "intellectual_property": "No Intellectual Property",
        "product_uniqueness": 2,
        "technology_readiness": 2,
        "product_scalability": 2,
        "unique_selling_proposition": "",
    }

    result = (
        risk_analysis.analyze_product_technology_risk(
            product_data=product_data,
            product_score=25,
            initial_risk="High",
        )
    )

    assert result["score"] >= 70
    assert result["level"] in {"High", "Critical"}

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert "Product remains at concept stage" in finding_titles
    assert "No working MVP available" in finding_titles
    assert "Very low technology readiness" in finding_titles
    assert "Low product scalability" in finding_titles
    assert "Low product differentiation" in finding_titles


# ============================================================
# MARKET RISK TESTS
# ============================================================

def test_strong_market_has_low_risk():
    market_data = {
        "target_customers": (
            "Angel investors, venture funds, and accelerators"
        ),
        "total_addressable_market": 2_000_000_000,
        "serviceable_available_market": 500_000_000,
        "market_growth_rate": 25,
        "competitor_count": 3,
        "competition_level": "Low",
        "competitive_advantage_strength": 9,
        "competitor_details": (
            "Three competitors were assessed for pricing and features."
        ),
    }

    result = risk_analysis.analyze_market_risk(
        market_data=market_data,
        market_score=90,
        initial_risk="Low",
    )

    assert result["score"] == 10.0
    assert result["level"] == "Low"
    assert result["findings"] == []
    assert len(result["positive_signals"]) >= 4


def test_weak_market_data_produces_risk_findings():
    market_data = {
        "target_customers": "",
        "total_addressable_market": 0,
        "serviceable_available_market": 0,
        "market_growth_rate": -5,
        "competitor_count": 0,
        "competition_level": "Very High",
        "competitive_advantage_strength": 2,
        "competitor_details": "",
    }

    result = risk_analysis.analyze_market_risk(
        market_data=market_data,
        market_score=30,
        initial_risk="High",
    )

    assert result["score"] >= 70
    assert result["level"] in {"High", "Critical"}

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert (
        "Target customers not clearly defined"
        in finding_titles
    )
    assert (
        "Total addressable market not estimated"
        in finding_titles
    )
    assert "Market is contracting" in finding_titles
    assert (
        "Very high competitive intensity"
        in finding_titles
    )
    assert "Weak competitive advantage" in finding_titles


def test_serviceable_market_cannot_exceed_total_market():
    market_data = {
        "target_customers": "Small businesses",
        "total_addressable_market": 100_000_000,
        "serviceable_available_market": 200_000_000,
        "market_growth_rate": 10,
        "competitor_count": 2,
        "competition_level": "Moderate",
        "competitive_advantage_strength": 7,
        "competitor_details": "Competitor information available.",
    }

    result = risk_analysis.analyze_market_risk(
        market_data=market_data,
        market_score=70,
    )

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert (
        "Serviceable market exceeds total market"
        in finding_titles
    )


# ============================================================
# CUSTOMER AND TRACTION RISK TESTS
# ============================================================

def test_strong_customer_traction_has_low_risk():
    customer_data = {
        "total_customers": 1000,
        "new_customers_monthly": 100,
        "customers_lost_monthly": 5,
        "customer_growth_rate": 20,
        "retention_rate": 95,
        "churn_rate": 3,
        "customer_acquisition_cost": 100,
        "customer_lifetime_value": 500,
        "major_customer_dependency": "Low",
    }

    result = risk_analysis.analyze_customer_risk(
        customer_data=customer_data,
        customer_score=90,
        initial_risk="Low",
    )

    assert result["score"] == 10.0
    assert result["level"] == "Low"
    assert result["findings"] == []
    assert len(result["positive_signals"]) >= 6


def test_no_customers_and_bad_unit_economics_produce_high_risk():
    customer_data = {
        "total_customers": 0,
        "new_customers_monthly": 1,
        "customers_lost_monthly": 5,
        "customer_growth_rate": -10,
        "retention_rate": 20,
        "churn_rate": 35,
        "customer_acquisition_cost": 1000,
        "customer_lifetime_value": 500,
        "major_customer_dependency": "High",
    }

    result = risk_analysis.analyze_customer_risk(
        customer_data=customer_data,
        customer_score=20,
        initial_risk="High",
    )

    assert result["score"] >= 80
    assert result["level"] in {"High", "Critical"}

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert "No existing customers reported" in finding_titles
    assert "Customer base is shrinking" in finding_titles
    assert "Negative customer growth" in finding_titles
    assert "Critical customer churn" in finding_titles
    assert "Unsustainable LTV-to-CAC ratio" in finding_titles
    assert "High customer concentration" in finding_titles


def test_customer_risk_detects_missing_unit_economics():
    customer_data = {
        "total_customers": 100,
        "new_customers_monthly": 20,
        "customers_lost_monthly": 5,
        "customer_growth_rate": 15,
        "retention_rate": 90,
        "churn_rate": 5,
        "customer_acquisition_cost": 0,
        "customer_lifetime_value": 0,
        "major_customer_dependency": "Low",
    }

    result = risk_analysis.analyze_customer_risk(
        customer_data=customer_data,
        customer_score=80,
    )

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert (
        "Customer unit economics unavailable"
        in finding_titles
    )


# ============================================================
# FUNDING RISK TESTS
# ============================================================

def test_well_documented_funding_position_has_low_risk():
    funding_data = {
        "previous_funding": 10_000_000,
        "number_of_funding_rounds": 2,
        "current_valuation": 100_000_000,
        "funding_sought": 10_000_000,
        "equity_offered": 10,
        "investor_count": 3,
        "investor_details": (
            "Three verified early-stage investors."
        ),
        "use_of_funds": (
            "Product development, compliance, hiring, and marketing."
        ),
    }

    result = risk_analysis.analyze_funding_risk(
        funding_data=funding_data,
        funding_score=90,
    )

    assert result["score"] == 10.0
    assert result["level"] == "Low"
    assert result["findings"] == []
    assert len(result["positive_signals"]) >= 5


def test_incomplete_funding_proposal_is_critical():
    funding_data = {
        "previous_funding": 0,
        "number_of_funding_rounds": 0,
        "current_valuation": 0,
        "funding_sought": 50_000_000,
        "equity_offered": 0,
        "investor_count": 0,
        "investor_details": "",
        "use_of_funds": "",
    }

    result = risk_analysis.analyze_funding_risk(
        funding_data=funding_data,
        funding_score=40,
    )

    assert result["score"] >= 80
    assert result["level"] in {"High", "Critical"}

    finding_titles = {
        finding["title"]
        for finding in result["findings"]
    }

    assert "Valuation not provided" in finding_titles
    assert "Equity offer not specified" in finding_titles
    assert "Use of funds not defined" in finding_titles
    assert (
        "Funding proposal is materially incomplete"
        in finding_titles
    )


def test_excessive_equity_offer_creates_critical_finding():
    funding_data = {
        "previous_funding": 5_000_000,
        "number_of_funding_rounds": 1,
        "current_valuation": 100_000_000,
        "funding_sought": 20_000_000,
        "equity_offered": 60,
        "investor_count": 1,
        "investor_details": "Existing investor documented.",
        "use_of_funds": "Product and market expansion.",
    }

    result = risk_analysis.analyze_funding_risk(
        funding_data=funding_data,
        funding_score=70,
    )

    critical_findings = [
        finding
        for finding in result["findings"]
        if finding["severity"] == "Critical"
    ]

    assert len(critical_findings) >= 1
    assert any(
        finding["title"] == "Excessive equity offered"
        for finding in critical_findings
    )


# ============================================================
# MANUAL RISK FLOOR TESTS
# ============================================================

def test_apply_manual_risk_floor_preserves_higher_score():
    risk_result = {
        "score": 75,
        "level": "Critical",
        "findings": [],
        "positive_signals": [],
    }

    adjusted = risk_analysis._apply_manual_risk_floor(
        risk_result=risk_result,
        initial_risk="Moderate",
    )

    assert adjusted["score"] == 75
    assert adjusted["level"] == "Critical"

def test_apply_manual_risk_floor_raises_low_score():
    risk_result = {
        "score": 10,
        "level": "Low",
        "findings": [],
        "positive_signals": [],
    }

    adjusted = risk_analysis._apply_manual_risk_floor(
        risk_result=risk_result,
        initial_risk="High",
    )

    assert adjusted["score"] == 55
    assert adjusted["level"] in {"High", "Critical"}


# ============================================================
# HIGHEST-RISK CATEGORY TEST
# ============================================================

def test_get_highest_risk_categories_returns_descending_order():
    category_risks = {
        "Financial Health": {
            "score": 20,
            "level": "Low",
            "findings": [],
        },
        "Market Opportunity": {
            "score": 80,
            "level": "Critical",
            "findings": [{}, {}],
        },
        "Founders & Team": {
            "score": 60,
            "level": "High",
            "findings": [{}],
        },
    }

    result = risk_analysis._get_highest_risk_categories(
        category_risks,
        limit=2,
    )

    assert len(result) == 2
    assert result[0]["category"] == "Market Opportunity"
    assert result[0]["score"] == 80
    assert result[1]["category"] == "Founders & Team"
    assert result[1]["score"] == 60


# ============================================================
# OVERALL RISK AGGREGATION TESTS
# ============================================================

def _fake_risk_result(
    score,
    findings=None,
    positive_signals=None,
):
    return {
        "score": score,
        "level": risk_analysis.classify_risk_level(score),
        "findings": findings or [],
        "positive_signals": positive_signals or [],
    }


def test_calculate_overall_risk_uses_category_weights(
    monkeypatch,
):
    monkeypatch.setattr(
        risk_analysis,
        "analyze_financial_risk",
        lambda *args, **kwargs: _fake_risk_result(10),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_team_risk",
        lambda *args, **kwargs: _fake_risk_result(20),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_product_technology_risk",
        lambda *args, **kwargs: _fake_risk_result(30),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_market_risk",
        lambda *args, **kwargs: _fake_risk_result(40),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_customer_risk",
        lambda *args, **kwargs: _fake_risk_result(50),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_funding_risk",
        lambda *args, **kwargs: _fake_risk_result(60),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_compliance_risk",
        lambda *args, **kwargs: _fake_risk_result(70),
    )

    startup_record = {
        "financial": {},
        "calculated_metrics": {},
        "founders_and_team": {},
        "product": {},
        "market": {},
        "customers": {},
        "funding": {},
        "compliance": {},
        "initial_risks": {},
    }

    scoring_result = {
        "category_scores": {
            "Founders & Team": 80,
            "Product & Technology": 70,
            "Market Opportunity": 60,
            "Customers & Traction": 50,
            "Funding Position": 40,
        },
        "compliance_result": {},
    }

    result = risk_analysis.calculate_overall_risk(
        startup_record=startup_record,
        scoring_result=scoring_result,
    )

    # Weighted calculation:
    # 10(0.25) + 20(0.15) + 30(0.15)
    # + 40(0.15) + 50(0.10) + 60(0.08)
    # + 70(0.12) = 34.20

    assert result["weighted_risk_score"] == 34.2
    assert result["overall_risk_score"] == 34.2
    assert len(result["category_risks"]) == 7
    assert result["override_applied"] is False
    assert result["risk_summary"]["total_findings"] == 0


def test_critical_finding_forces_critical_overall_risk(
    monkeypatch,
):
    normal_result = _fake_risk_result(20)

    critical_finding = {
        "category": "Funding Risk",
        "title": "Critical funding issue",
        "description": "Funding terms are unsafe.",
        "severity": "Critical",
        "impact": "Investment capital may be at risk.",
        "recommendation": (
            "Resolve the funding issue before proceeding."
        ),
    }

    monkeypatch.setattr(
        risk_analysis,
        "analyze_financial_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_team_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_product_technology_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_market_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_customer_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_funding_risk",
        lambda *args, **kwargs: _fake_risk_result(
            20,
            findings=[critical_finding],
        ),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_compliance_risk",
        lambda *args, **kwargs: normal_result,
    )

    startup_record = {
        "financial": {},
        "calculated_metrics": {},
        "founders_and_team": {},
        "product": {},
        "market": {},
        "customers": {},
        "funding": {},
        "compliance": {},
        "initial_risks": {},
    }

    scoring_result = {
        "category_scores": {},
        "compliance_result": {},
    }

    result = risk_analysis.calculate_overall_risk(
        startup_record=startup_record,
        scoring_result=scoring_result,
    )

    assert result["weighted_risk_score"] == 20.0
    assert result["overall_risk_score"] == 75.0
    assert result["overall_risk_level"] == "Critical"
    assert result["override_applied"] is True
    assert result["risk_summary"]["critical_findings"] == 1
    assert "Funding Risk" in (
        result["risk_summary"]["critical_categories"]
    )


def test_category_score_of_80_applies_override(
    monkeypatch,
):
    normal_result = _fake_risk_result(20)
    very_high_result = _fake_risk_result(85)

    monkeypatch.setattr(
        risk_analysis,
        "analyze_financial_risk",
        lambda *args, **kwargs: very_high_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_team_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_product_technology_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_market_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_customer_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_funding_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_compliance_risk",
        lambda *args, **kwargs: normal_result,
    )

    startup_record = {
        "financial": {},
        "calculated_metrics": {},
        "founders_and_team": {},
        "product": {},
        "market": {},
        "customers": {},
        "funding": {},
        "compliance": {},
        "initial_risks": {},
    }

    result = risk_analysis.calculate_overall_risk(
        startup_record=startup_record,
        scoring_result={
            "category_scores": {},
            "compliance_result": {},
        },
    )

    assert result["overall_risk_score"] >= 70
    assert result["override_applied"] is True
    assert "Financial Health" in (
        result["risk_summary"][
            "very_high_risk_categories"
        ]
    )


def test_five_high_findings_apply_override(
    monkeypatch,
):
    high_findings = [
        {
            "category": "Market Risk",
            "title": f"High risk {index}",
            "description": "Risk description.",
            "severity": "High",
            "impact": "High impact.",
            "recommendation": "Resolve the risk.",
        }
        for index in range(5)
    ]

    normal_result = _fake_risk_result(20)

    monkeypatch.setattr(
        risk_analysis,
        "analyze_financial_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_team_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_product_technology_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_market_risk",
        lambda *args, **kwargs: _fake_risk_result(
            20,
            findings=high_findings,
        ),
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_customer_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_funding_risk",
        lambda *args, **kwargs: normal_result,
    )

    monkeypatch.setattr(
        risk_analysis,
        "analyze_compliance_risk",
        lambda *args, **kwargs: normal_result,
    )

    startup_record = {
        "financial": {},
        "calculated_metrics": {},
        "founders_and_team": {},
        "product": {},
        "market": {},
        "customers": {},
        "funding": {},
        "compliance": {},
        "initial_risks": {},
    }

    result = risk_analysis.calculate_overall_risk(
        startup_record=startup_record,
        scoring_result={
            "category_scores": {},
            "compliance_result": {},
        },
    )

    assert result["weighted_risk_score"] == 20.0
    assert result["overall_risk_score"] == 60.0
    assert result["override_applied"] is True
    assert result["risk_summary"]["high_findings"] == 5


def test_generate_risk_report_delegates_to_overall_risk(
    monkeypatch,
):
    expected_result = {
        "overall_risk_score": 42,
        "overall_risk_level": "Moderate",
    }

    monkeypatch.setattr(
        risk_analysis,
        "calculate_overall_risk",
        lambda startup_record, scoring_result: (
            expected_result
        ),
    )

    result = risk_analysis.generate_risk_report(
        startup_record={"company": {}},
        scoring_result={"category_scores": {}},
    )

    assert result == expected_result