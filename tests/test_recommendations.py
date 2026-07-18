import pytest

from src import recommendations


# ============================================================
# HELPER TESTS
# ============================================================

def test_safe_float_returns_default_for_invalid_value():
    assert recommendations._safe_float(
        "invalid",
        7.5,
    ) == 7.5


def test_safe_int_converts_float_string():
    assert recommendations._safe_int("4.9") == 4


def test_create_recommendation_normalizes_invalid_priority():
    result = recommendations.create_recommendation(
        category="Financial Health",
        title="Test title",
        description="Test description",
        priority="Urgent",
        action="Take action",
    )

    assert result["priority"] == "Low"


def test_sort_recommendations_by_priority():
    items = [
        {"title": "Low", "priority": "Low"},
        {"title": "Critical", "priority": "Critical"},
        {"title": "Medium", "priority": "Medium"},
        {"title": "High", "priority": "High"},
    ]

    sorted_items = (
        recommendations.sort_recommendations_by_priority(
            items
        )
    )

    assert [
        item["priority"]
        for item in sorted_items
    ] == [
        "Critical",
        "High",
        "Medium",
        "Low",
    ]


def test_remove_duplicate_recommendations_ignores_case():
    items = [
        {
            "category": "Financial Health",
            "title": "Reduce Burn",
        },
        {
            "category": "financial health",
            "title": " reduce burn ",
        },
    ]

    result = (
        recommendations.remove_duplicate_recommendations(
            items
        )
    )

    assert len(result) == 1


def test_get_top_recommendations_respects_limit():
    items = [
        {
            "category": "A",
            "title": "One",
            "priority": "Low",
        },
        {
            "category": "B",
            "title": "Two",
            "priority": "Critical",
        },
        {
            "category": "C",
            "title": "Three",
            "priority": "High",
        },
    ]

    result = recommendations.get_top_recommendations(
        items,
        limit=2,
    )

    assert len(result) == 2
    assert result[0]["priority"] == "Critical"
    assert result[1]["priority"] == "High"


def test_count_recommendations_by_priority():
    items = [
        {"priority": "Critical"},
        {"priority": "High"},
        {"priority": "High"},
        {"priority": "Unknown"},
    ]

    counts = (
        recommendations.count_recommendations_by_priority(
            items
        )
    )

    assert counts == {
        "Critical": 1,
        "High": 2,
        "Medium": 0,
        "Low": 1,
    }


def test_group_recommendations_by_category():
    items = [
        {
            "category": "Financial Health",
            "title": "A",
        },
        {
            "category": "Financial Health",
            "title": "B",
        },
        {
            "category": "Market Opportunity",
            "title": "C",
        },
    ]

    grouped = (
        recommendations.group_recommendations_by_category(
            items
        )
    )

    assert len(grouped["Financial Health"]) == 2
    assert len(grouped["Market Opportunity"]) == 1


# ============================================================
# RISK FINDING CONVERSION TESTS
# ============================================================

def test_get_finding_priority_defaults_to_low():
    finding = {
        "severity": "Unknown",
    }

    assert (
        recommendations._get_finding_priority(
            finding
        )
        == "Low"
    )


def test_recommendation_from_risk_finding():
    finding = {
        "category": "Financial Health",
        "title": "Low runway",
        "description": "Runway is below six months.",
        "severity": "Critical",
        "impact": "Business continuity risk.",
        "recommendation": "Raise bridge funding.",
    }

    result = (
        recommendations.recommendation_from_risk_finding(
            finding
        )
    )

    assert result["category"] == "Financial Health"
    assert result["priority"] == "Critical"
    assert result["action"] == "Raise bridge funding."


def test_recommendations_from_findings_skips_invalid_items():
    findings = [
        {
            "category": "Market Opportunity",
            "title": "Weak differentiation",
            "severity": "High",
        },
        "invalid",
        None,
    ]

    result = recommendations.recommendations_from_findings(
        findings
    )

    assert len(result) == 1
    assert result[0]["title"] == "Weak differentiation"


# ============================================================
# CATEGORY RECOMMENDATION TESTS
# ============================================================

def empty_risk_report():
    return {
        "category_risks": {},
        "all_findings": [],
        "positive_signals": [],
        "overall_risk_score": 0,
        "weighted_risk_score": 0,
        "overall_risk_level": "Low",
        "override_applied": False,
    }


def test_generate_financial_recommendations_for_low_runway():
    startup_record = {
        "financial": {
            "monthly_revenue": 100000,
            "monthly_expenses": 150000,
        },
        "calculated_metrics": {
            "cash_runway_months": 3,
            "financial_health_score": 30,
        },
    }

    result = (
        recommendations.generate_financial_recommendations(
            startup_record=startup_record,
            risk_report=empty_risk_report(),
        )
    )

    titles = {
        item["title"]
        for item in result
    }

    assert "Reduce the monthly cash burn" in titles
    assert "Extend the available cash runway" in titles
    assert "Prepare a financial recovery plan" in titles


def test_generate_team_recommendations_for_weak_team():
    startup_record = {
        "founders_and_team": {
            "founder_count": 1,
            "technical_team_strength": 3,
            "business_team_strength": 2,
            "key_person_dependency": "High",
        }
    }

    result = recommendations.generate_team_recommendations(
        startup_record=startup_record,
        risk_report=empty_risk_report(),
    )

    titles = {
        item["title"]
        for item in result
    }

    assert "Reduce single-founder dependency" in titles
    assert "Strengthen technical leadership" in titles
    assert "Improve commercial leadership" in titles
    assert "Create a succession and delegation plan" in titles


def test_generate_product_recommendations_for_concept_stage():
    startup_record = {
        "product": {
            "product_stage": "Concept",
            "working_mvp": "No",
            "technology_readiness": 3,
            "product_scalability": 4,
        }
    }

    result = (
        recommendations.generate_product_recommendations(
            startup_record=startup_record,
            risk_report=empty_risk_report(),
        )
    )

    titles = {
        item["title"]
        for item in result
    }

    assert "Develop and validate a working MVP" in titles
    assert "Improve technology readiness" in titles
    assert "Create a product scalability plan" in titles


def test_generate_market_recommendations_for_invalid_market_data():
    startup_record = {
        "market": {
            "target_customers": "",
            "total_addressable_market": 100,
            "serviceable_available_market": 200,
            "competitive_advantage_strength": 3,
        }
    }

    result = (
        recommendations.generate_market_recommendations(
            startup_record=startup_record,
            risk_report=empty_risk_report(),
        )
    )

    titles = {
        item["title"]
        for item in result
    }

    assert "Define the target customer segment" in titles
    assert "Correct the market-size assumptions" in titles
    assert "Strengthen competitive differentiation" in titles


def test_generate_customer_recommendations_for_weak_traction():
    startup_record = {
        "customers": {
            "total_customers": 0,
            "retention_rate": 50,
            "churn_rate": 20,
            "customer_acquisition_cost": 100,
            "customer_lifetime_value": 200,
        }
    }

    result = (
        recommendations.generate_customer_recommendations(
            startup_record=startup_record,
            risk_report=empty_risk_report(),
        )
    )

    titles = {
        item["title"]
        for item in result
    }

    assert "Obtain initial customer validation" in titles
    assert "Improve customer retention" in titles
    assert "Reduce customer churn" in titles
    assert "Improve customer unit economics" in titles


def test_generate_funding_recommendations_for_missing_details():
    startup_record = {
        "funding": {
            "current_valuation": 0,
            "funding_sought": 5000000,
            "equity_offered": 60,
            "use_of_funds": "",
        }
    }

    result = (
        recommendations.generate_funding_recommendations(
            startup_record=startup_record,
            risk_report=empty_risk_report(),
        )
    )

    titles = {
        item["title"]
        for item in result
    }

    assert "Provide a defensible startup valuation" in titles
    assert "Define the use of investment funds" in titles
    assert "Review the proposed equity dilution" in titles


def test_generate_compliance_recommendations_for_missing_controls():
    startup_record = {
        "compliance": {
            "regulator_identified": False,
            "regulatory_registration": False,
            "required_licenses": False,
            "kyc_implemented": False,
            "aml_implemented": False,
            "transaction_monitoring": False,
        }
    }

    result = (
        recommendations.generate_compliance_recommendations(
            startup_record=startup_record,
            risk_report=empty_risk_report(),
        )
    )

    titles = {
        item["title"]
        for item in result
    }

    assert (
        "Identify the applicable financial regulator"
        in titles
    )
    assert "Complete regulatory registration" in titles
    assert "Obtain all required financial licences" in titles
    assert "Implement complete KYC and AML controls" in titles
    assert "Introduce transaction monitoring" in titles


def test_generate_all_category_recommendations_has_all_categories():
    result = (
        recommendations.generate_all_category_recommendations(
            startup_record={},
            risk_report=empty_risk_report(),
        )
    )

    assert set(result.keys()) == {
        "Financial Health",
        "Founders & Team",
        "Product & Technology",
        "Market Opportunity",
        "Customers & Traction",
        "Funding Position",
        "Legal & Compliance",
    }


# ============================================================
# DECISION TESTS
# ============================================================

def test_determine_investment_decision_returns_invest():
    scoring_result = {
        "overall_score": 85,
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 20,
        "overall_risk_level": "Low",
    }

    result = recommendations.determine_investment_decision(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    assert result == "Invest"


def test_determine_investment_decision_returns_invest_with_conditions():
    scoring_result = {
        "overall_score": 68,
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 40,
        "overall_risk_level": "Moderate",
    }

    result = recommendations.determine_investment_decision(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    assert result == "Invest with Conditions"


def test_determine_investment_decision_returns_hold():
    scoring_result = {
        "overall_score": 52,
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 60,
        "overall_risk_level": "High",
    }

    result = recommendations.determine_investment_decision(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    assert result == "Hold"


def test_determine_investment_decision_rejects_critical_risk():
    scoring_result = {
        "overall_score": 90,
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 80,
        "overall_risk_level": "Critical",
    }

    result = recommendations.determine_investment_decision(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    assert result == "Reject"


def test_determine_investment_decision_rejects_critical_finding():
    scoring_result = {
        "overall_score": 90,
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 20,
        "overall_risk_level": "Low",
        "all_findings": [
            {
                "category": "Legal & Compliance",
                "title": "Unlicensed operation",
                "severity": "Critical",
                "description": "Required licence is missing.",
            }
        ],
    }

    result = recommendations.determine_investment_decision(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    assert result == "Reject"


def test_calculate_decision_confidence_returns_valid_range():
    scoring_result = {
        "overall_score": 80,
        "category_scores": {
            "Financial Health": 80,
            "Founders & Team": 75,
            "Product & Technology": 78,
            "Market Opportunity": 77,
            "Customers & Traction": 76,
            "Funding Position": 74,
            "Legal & Compliance": 82,
        },
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 20,
    }

    result = recommendations.calculate_decision_confidence(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    assert 0 <= result["confidence_score"] <= 100
    assert result["confidence_level"] in {
        "High",
        "Moderate",
        "Low",
    }
    assert result["available_category_count"] == 7


# ============================================================
# REPORT EXTRACTION TESTS
# ============================================================

def test_extract_red_flags_returns_only_high_and_critical():
    risk_report = {
        **empty_risk_report(),
        "all_findings": [
            {
                "category": "Financial Health",
                "title": "Critical issue",
                "severity": "Critical",
            },
            {
                "category": "Market Opportunity",
                "title": "High issue",
                "severity": "High",
            },
            {
                "category": "Product & Technology",
                "title": "Medium issue",
                "severity": "Medium",
            },
        ],
    }

    result = recommendations.extract_red_flags(
        risk_report
    )

    assert len(result) == 2
    assert result[0]["severity"] == "Critical"
    assert result[1]["severity"] == "High"


def test_extract_strengths_includes_high_category_scores():
    scoring_result = {
        "category_scores": {
            "Financial Health": 80,
            "Market Opportunity": 60,
        }
    }

    result = recommendations.extract_strengths(
        risk_report=empty_risk_report(),
        scoring_result=scoring_result,
    )

    assert any(
        item["category"] == "Financial Health"
        for item in result
    )


def test_extract_weaknesses_includes_low_category_scores():
    scoring_result = {
        "category_scores": {
            "Financial Health": 25,
            "Market Opportunity": 70,
        }
    }

    result = recommendations.extract_weaknesses(
        risk_report=empty_risk_report(),
        scoring_result=scoring_result,
    )

    assert any(
        item["category"] == "Financial Health"
        for item in result
    )


def test_generate_investment_conditions_for_hold():
    items = [
        {
            "category": "Financial Health",
            "title": "Extend runway",
            "priority": "Critical",
        },
        {
            "category": "Market Opportunity",
            "title": "Validate market",
            "priority": "High",
        },
        {
            "category": "Product & Technology",
            "title": "Improve documentation",
            "priority": "Low",
        },
    ]

    result = (
        recommendations.generate_investment_conditions(
            recommendations=items,
            decision="Hold",
            limit=5,
        )
    )

    assert len(result) == 2
    assert all(
        item["priority"] in {
            "Critical",
            "High",
        }
        for item in result
    )


def test_generate_investment_conditions_empty_for_invest():
    result = (
        recommendations.generate_investment_conditions(
            recommendations=[
                {
                    "category": "General",
                    "title": "Test",
                    "priority": "High",
                }
            ],
            decision="Invest",
        )
    )

    assert result == []


# ============================================================
# COMPLETE REPORT TEST
# ============================================================

def test_generate_recommendation_report():
    startup_record = {
        "company": {
            "company_name": "FinNova",
        },
        "financial": {
            "monthly_revenue": 500000,
            "monthly_expenses": 300000,
        },
        "calculated_metrics": {
            "cash_runway_months": 18,
            "financial_health_score": 82,
        },
        "founders_and_team": {
            "founder_count": 2,
            "technical_team_strength": 8,
            "business_team_strength": 7,
            "key_person_dependency": "Low",
        },
        "product": {
            "product_stage": "Market Ready",
            "working_mvp": "Yes",
            "technology_readiness": 8,
            "product_scalability": 8,
        },
        "market": {
            "target_customers": "Small businesses",
            "total_addressable_market": 100000000,
            "serviceable_available_market": 20000000,
            "competitive_advantage_strength": 8,
        },
        "customers": {
            "total_customers": 1000,
            "retention_rate": 85,
            "churn_rate": 5,
            "customer_acquisition_cost": 1000,
            "customer_lifetime_value": 5000,
        },
        "funding": {
            "current_valuation": 100000000,
            "funding_sought": 10000000,
            "equity_offered": 10,
            "use_of_funds": "Product and market expansion",
        },
        "compliance": {
            "regulator_identified": True,
            "regulatory_registration": True,
            "required_licenses": True,
            "kyc_implemented": True,
            "aml_implemented": True,
            "transaction_monitoring": True,
        },
    }

    scoring_result = {
        "overall_score": 85,
        "category_scores": {
            "Financial Health": 85,
            "Founders & Team": 80,
            "Product & Technology": 82,
            "Market Opportunity": 78,
            "Customers & Traction": 84,
            "Funding Position": 76,
            "Legal & Compliance": 88,
        },
    }

    risk_report = {
        **empty_risk_report(),
        "overall_risk_score": 18,
        "overall_risk_level": "Low",
        "positive_signals": [
            {
                "category": "Financial Health",
                "signal": "Strong cash position",
            }
        ],
    }

    result = (
        recommendations.generate_recommendation_report(
            startup_record=startup_record,
            scoring_result=scoring_result,
            risk_report=risk_report,
        )
    )

    assert result["investment_decision"] == "Invest"
    assert result["due_diligence_score"] == 85
    assert result["overall_risk_score"] == 18
    assert result["overall_risk_level"] == "Low"
    assert "FinNova" in result["executive_summary"]
    assert "category_recommendations" in result
    assert "top_recommendations" in result
    assert "decision_confidence" in result
    assert "strengths" in result
    assert "weaknesses" in result
    assert "red_flags" in result