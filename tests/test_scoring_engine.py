from src.scoring_engine import (
    calculate_customer_score,
    calculate_legal_score,
    calculate_product_score,
    calculate_team_score,
    get_investment_recommendation,
    get_risk_level,
)


def test_strong_team_score() -> None:
    team = {
        "founder_count": 3,
        "founder_experience_years": 10,
        "industry_experience_years": 10,
        "previous_startup_experience": "Yes",
        "technical_team_strength": 9,
        "business_team_strength": 9,
        "team_stability": 9,
        "key_person_dependency": "Low",
    }

    result = calculate_team_score(team)

    assert result >= 85


def test_weak_team_score() -> None:
    team = {
        "founder_count": 1,
        "founder_experience_years": 0,
        "industry_experience_years": 0,
        "previous_startup_experience": "No",
        "technical_team_strength": 2,
        "business_team_strength": 2,
        "team_stability": 2,
        "key_person_dependency": "High",
    }

    result = calculate_team_score(team)

    assert result < 35


def test_market_ready_product_score() -> None:
    product = {
        "product_stage": "Market Ready",
        "working_mvp": "Yes",
        "intellectual_property": "Patent Filed",
        "product_uniqueness": 8,
        "technology_readiness": 9,
        "product_scalability": 9,
        "problem_statement": "A clear customer problem.",
        "product_description": "A working software product.",
        "unique_selling_proposition": "Faster and cheaper.",
    }

    result = calculate_product_score(product)

    assert result >= 75


def test_strong_customer_score() -> None:
    customers = {
        "total_customers": 10000,
        "new_customers_monthly": 500,
        "customers_lost_monthly": 20,
        "customer_growth_rate": 20,
        "retention_rate": 92,
        "churn_rate": 5,
        "customer_acquisition_cost": 1000,
        "customer_lifetime_value": 5000,
        "major_customer_dependency": "Low",
    }

    result = calculate_customer_score(customers)

    assert result >= 80


def test_compliant_legal_score() -> None:
    company = {
        "registration_status": "Registered",
    }

    legal = {
        "required_licenses_available": "Yes",
        "tax_compliance": "Compliant",
        "founder_agreement": "Yes",
        "employee_agreements": "Yes",
        "pending_lawsuits": "No",
        "regulatory_issues": "No",
        "privacy_policy_available": "Yes",
        "data_security_measures": "Strong",
    }

    result = calculate_legal_score(
        legal=legal,
        company=company,
    )

    assert result == 100


def test_recommendation_labels() -> None:
    assert get_investment_recommendation(85) == (
        "Strong Investment Candidate"
    )

    assert get_investment_recommendation(55) == (
        "Moderate Potential – Proceed with Caution"
    )


def test_risk_levels() -> None:
    assert get_risk_level(85) == "Low"
    assert get_risk_level(55) == "Moderate"
    assert get_risk_level(20) == "Critical"