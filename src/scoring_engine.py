from __future__ import annotations

from typing import Any
from src.compliance_engine import calculate_compliance_score


CATEGORY_WEIGHTS = {
    "Financial Health": 0.25,
    "Founders & Team": 0.15,
    "Product & Technology": 0.15,
    "Market Opportunity": 0.15,
    "Customers & Traction": 0.10,
    "Funding Position": 0.08,
    "Legal & Compliance": 0.12,
}


def clamp_score(score: float) -> float:
    """
    Keep a score between 0 and 100.
    """

    return round(max(0.0, min(score, 100.0)), 2)


def calculate_team_score(team: dict[str, Any]) -> float:
    """
    Calculate the founders and team score out of 100.
    """

    score = 0.0

    founder_count = team.get("founder_count", 0)
    founder_experience = team.get("founder_experience_years", 0.0)
    industry_experience = team.get("industry_experience_years", 0.0)
    previous_experience = team.get(
        "previous_startup_experience",
        "Information Not Available",
    )

    technical_strength = team.get("technical_team_strength", 1)
    business_strength = team.get("business_team_strength", 1)
    team_stability = team.get("team_stability", 1)

    dependency = team.get(
        "key_person_dependency",
        "Information Not Available",
    )

    # Founder structure: maximum 10 points
    if founder_count >= 3:
        score += 10
    elif founder_count == 2:
        score += 8
    elif founder_count == 1:
        score += 5

    # Founder professional experience: maximum 15 points
    if founder_experience >= 10:
        score += 15
    elif founder_experience >= 5:
        score += 12
    elif founder_experience >= 2:
        score += 8
    elif founder_experience > 0:
        score += 4

    # Relevant industry experience: maximum 15 points
    if industry_experience >= 10:
        score += 15
    elif industry_experience >= 5:
        score += 12
    elif industry_experience >= 2:
        score += 8
    elif industry_experience > 0:
        score += 4

    # Previous startup experience: maximum 10 points
    startup_experience_scores = {
        "Yes": 10,
        "Partially": 6,
        "No": 2,
        "Information Not Available": 0,
    }

    score += startup_experience_scores.get(previous_experience, 0)

    # Team quality ratings: maximum 45 points
    score += (technical_strength / 10) * 15
    score += (business_strength / 10) * 15
    score += (team_stability / 10) * 15

    # Dependency risk: maximum 5 points
    dependency_scores = {
        "Low": 5,
        "Moderate": 3,
        "High": 0,
        "Information Not Available": 1,
    }

    score += dependency_scores.get(dependency, 0)

    return clamp_score(score)


def calculate_product_score(product: dict[str, Any]) -> float:
    """
    Calculate product and technology score out of 100.
    """

    score = 0.0

    product_stage = product.get("product_stage", "Concept Only")
    working_mvp = product.get(
        "working_mvp",
        "Information Not Available",
    )
    intellectual_property = product.get(
        "intellectual_property",
        "Information Not Available",
    )

    uniqueness = product.get("product_uniqueness", 1)
    technology_readiness = product.get("technology_readiness", 1)
    scalability = product.get("product_scalability", 1)

    problem_statement = product.get("problem_statement", "").strip()
    product_description = product.get("product_description", "").strip()
    unique_selling_proposition = product.get(
        "unique_selling_proposition",
        "",
    ).strip()

    # Product stage: maximum 20 points
    stage_scores = {
        "Concept Only": 3,
        "Prototype": 7,
        "Minimum Viable Product": 12,
        "Early Customers": 16,
        "Market Ready": 18,
        "Scaling": 20,
    }

    score += stage_scores.get(product_stage, 0)

    # MVP status: maximum 10 points
    mvp_scores = {
        "Yes": 10,
        "Under Development": 5,
        "No": 0,
        "Information Not Available": 1,
    }

    score += mvp_scores.get(working_mvp, 0)

    # Intellectual property: maximum 15 points
    intellectual_property_scores = {
        "Patent Granted": 15,
        "Patent Filed": 12,
        "Trademark Registered": 9,
        "Internally Developed Technology": 8,
        "No Intellectual Property": 3,
        "Information Not Available": 1,
    }

    score += intellectual_property_scores.get(
        intellectual_property,
        0,
    )

    # Product ratings: maximum 45 points
    score += (uniqueness / 10) * 15
    score += (technology_readiness / 10) * 15
    score += (scalability / 10) * 15

    # Product documentation quality: maximum 10 points
    if problem_statement:
        score += 3

    if product_description:
        score += 3

    if unique_selling_proposition:
        score += 4

    return clamp_score(score)


def calculate_market_score(market: dict[str, Any]) -> float:
    """
    Calculate market opportunity score out of 100.
    """

    score = 0.0

    target_customers = market.get("target_customers", "").strip()
    total_market = market.get("total_addressable_market", 0.0)
    serviceable_market = market.get(
        "serviceable_available_market",
        0.0,
    )
    growth_rate = market.get("market_growth_rate", 0.0)
    competitor_count = market.get("competitor_count", 0)
    competition_level = market.get(
        "competition_level",
        "Information Not Available",
    )
    competitive_advantage = market.get(
        "competitive_advantage_strength",
        1,
    )
    competitor_details = market.get("competitor_details", "").strip()

    # Target customer clarity: maximum 10 points
    if target_customers:
        score += 10

    # Total addressable market: maximum 20 points
    if total_market >= 10_000_000_000:
        score += 20
    elif total_market >= 1_000_000_000:
        score += 16
    elif total_market >= 100_000_000:
        score += 12
    elif total_market > 0:
        score += 7

    # Serviceable market: maximum 15 points
    if serviceable_market > 0 and total_market > 0:
        serviceable_percentage = (
            serviceable_market / total_market
        ) * 100

        if serviceable_percentage >= 50:
            score += 15
        elif serviceable_percentage >= 25:
            score += 12
        elif serviceable_percentage >= 10:
            score += 8
        else:
            score += 4

    # Market growth: maximum 25 points
    if growth_rate >= 30:
        score += 25
    elif growth_rate >= 20:
        score += 21
    elif growth_rate >= 10:
        score += 16
    elif growth_rate >= 5:
        score += 10
    elif growth_rate >= 0:
        score += 5

    # Competition: maximum 10 points
    competition_scores = {
        "Low": 10,
        "Moderate": 8,
        "High": 5,
        "Very High": 2,
        "Information Not Available": 1,
    }

    score += competition_scores.get(competition_level, 0)

    # Competitive advantage: maximum 15 points
    score += (competitive_advantage / 10) * 15

    # Competitor research: maximum 5 points
    if competitor_details or competitor_count > 0:
        score += 5

    return clamp_score(score)


def calculate_customer_score(customers: dict[str, Any]) -> float:
    """
    Calculate customer traction score out of 100.
    """

    score = 0.0

    total_customers = customers.get("total_customers", 0)
    new_customers = customers.get("new_customers_monthly", 0)
    customers_lost = customers.get("customers_lost_monthly", 0)
    growth_rate = customers.get("customer_growth_rate", 0.0)
    retention_rate = customers.get("retention_rate", 0.0)
    churn_rate = customers.get("churn_rate", 0.0)
    acquisition_cost = customers.get(
        "customer_acquisition_cost",
        0.0,
    )
    lifetime_value = customers.get(
        "customer_lifetime_value",
        0.0,
    )
    customer_dependency = customers.get(
        "major_customer_dependency",
        "Information Not Available",
    )

    # Existing customer base: maximum 15 points
    if total_customers >= 100_000:
        score += 15
    elif total_customers >= 10_000:
        score += 13
    elif total_customers >= 1_000:
        score += 10
    elif total_customers >= 100:
        score += 7
    elif total_customers > 0:
        score += 4

    # Monthly net customer acquisition: maximum 10 points
    net_new_customers = new_customers - customers_lost

    if net_new_customers >= 1000:
        score += 10
    elif net_new_customers >= 100:
        score += 8
    elif net_new_customers > 0:
        score += 5
    elif net_new_customers == 0 and total_customers > 0:
        score += 2

    # Customer growth rate: maximum 20 points
    if growth_rate >= 30:
        score += 20
    elif growth_rate >= 15:
        score += 16
    elif growth_rate >= 5:
        score += 12
    elif growth_rate >= 0:
        score += 6

    # Retention rate: maximum 20 points
    if retention_rate >= 90:
        score += 20
    elif retention_rate >= 80:
        score += 16
    elif retention_rate >= 70:
        score += 12
    elif retention_rate >= 50:
        score += 7
    elif retention_rate > 0:
        score += 3

    # Churn rate: maximum 10 points
    if churn_rate <= 5:
        score += 10
    elif churn_rate <= 10:
        score += 8
    elif churn_rate <= 20:
        score += 5
    elif churn_rate <= 30:
        score += 2

    # LTV/CAC ratio: maximum 20 points
    if acquisition_cost > 0:
        ltv_cac_ratio = lifetime_value / acquisition_cost

        if ltv_cac_ratio >= 5:
            score += 20
        elif ltv_cac_ratio >= 3:
            score += 16
        elif ltv_cac_ratio >= 2:
            score += 10
        elif ltv_cac_ratio >= 1:
            score += 5
    elif lifetime_value > 0:
        score += 10

    # Customer concentration risk: maximum 5 points
    dependency_scores = {
        "Low": 5,
        "Moderate": 3,
        "High": 0,
        "Information Not Available": 1,
    }

    score += dependency_scores.get(customer_dependency, 0)

    return clamp_score(score)


def calculate_funding_score(funding: dict[str, Any]) -> float:
    """
    Calculate funding position score out of 100.
    """

    score = 0.0

    previous_funding = funding.get("previous_funding", 0.0)
    number_of_rounds = funding.get("number_of_funding_rounds", 0)
    current_valuation = funding.get("current_valuation", 0.0)
    funding_sought = funding.get("funding_sought", 0.0)
    equity_offered = funding.get("equity_offered", 0.0)
    investor_count = funding.get("investor_count", 0)
    investor_details = funding.get("investor_details", "").strip()
    use_of_funds = funding.get("use_of_funds", "").strip()

    # Previous funding validation: maximum 20 points
    if previous_funding >= 100_000_000:
        score += 20
    elif previous_funding >= 10_000_000:
        score += 16
    elif previous_funding > 0:
        score += 10
    else:
        score += 5

    # Funding-round history: maximum 10 points
    if number_of_rounds >= 3:
        score += 10
    elif number_of_rounds == 2:
        score += 8
    elif number_of_rounds == 1:
        score += 5
    elif previous_funding == 0:
        score += 3

    # Existing investors: maximum 15 points
    if investor_count >= 5:
        score += 15
    elif investor_count >= 3:
        score += 12
    elif investor_count >= 1:
        score += 8

    # Investor details: maximum 10 points
    if investor_details:
        score += 10

    # Use-of-funds clarity: maximum 20 points
    if use_of_funds:
        score += 20

    # Valuation availability: maximum 10 points
    if current_valuation > 0:
        score += 10

    # Funding ask relative to valuation: maximum 10 points
    if current_valuation > 0 and funding_sought > 0:
        funding_percentage = (
            funding_sought / current_valuation
        ) * 100

        if funding_percentage <= 20:
            score += 10
        elif funding_percentage <= 40:
            score += 7
        elif funding_percentage <= 60:
            score += 4

    # Equity-offer reasonableness: maximum 5 points
    if 5 <= equity_offered <= 25:
        score += 5
    elif 0 < equity_offered <= 40:
        score += 3

    return clamp_score(score)


def calculate_legal_score(
    legal: dict[str, Any],
    company: dict[str, Any],
) -> float:
    """
    Calculate legal and compliance score out of 100.
    """

    score = 0.0

    registration_status = company.get(
        "registration_status",
        "Information Not Available",
    )

    licence_status = legal.get(
        "required_licenses_available",
        "Information Not Available",
    )
    tax_compliance = legal.get(
        "tax_compliance",
        "Information Not Available",
    )
    founder_agreement = legal.get(
        "founder_agreement",
        "Information Not Available",
    )
    employee_agreements = legal.get(
        "employee_agreements",
        "Information Not Available",
    )
    pending_lawsuits = legal.get(
        "pending_lawsuits",
        "Information Not Available",
    )
    regulatory_issues = legal.get(
        "regulatory_issues",
        "Information Not Available",
    )
    privacy_policy = legal.get(
        "privacy_policy_available",
        "Information Not Available",
    )
    security_measures = legal.get(
        "data_security_measures",
        "Information Not Available",
    )

    # Company registration: maximum 15 points
    registration_scores = {
        "Registered": 15,
        "Registration in Progress": 8,
        "Not Registered": 0,
        "Information Not Available": 2,
    }

    score += registration_scores.get(registration_status, 0)

    # Required licences: maximum 15 points
    licence_scores = {
        "Yes": 15,
        "Partially": 8,
        "No": 0,
        "Not Applicable": 15,
        "Information Not Available": 2,
    }

    score += licence_scores.get(licence_status, 0)

    # Tax compliance: maximum 15 points
    tax_scores = {
        "Compliant": 15,
        "Partially Compliant": 7,
        "Non-Compliant": 0,
        "Information Not Available": 2,
    }

    score += tax_scores.get(tax_compliance, 0)

    # Founder agreement: maximum 10 points
    founder_agreement_scores = {
        "Yes": 10,
        "No": 0,
        "Information Not Available": 2,
    }

    score += founder_agreement_scores.get(founder_agreement, 0)

    # Employee agreements: maximum 10 points
    employee_agreement_scores = {
        "Yes": 10,
        "Partially": 5,
        "No": 0,
        "Information Not Available": 2,
    }

    score += employee_agreement_scores.get(employee_agreements, 0)

    # Lawsuit status: maximum 10 points
    lawsuit_scores = {
        "No": 10,
        "Yes": 0,
        "Information Not Available": 2,
    }

    score += lawsuit_scores.get(pending_lawsuits, 0)

    # Regulatory status: maximum 10 points
    regulatory_scores = {
        "No": 10,
        "Yes": 0,
        "Information Not Available": 2,
    }

    score += regulatory_scores.get(regulatory_issues, 0)

    # Privacy policy: maximum 7 points
    privacy_scores = {
        "Yes": 7,
        "No": 0,
        "Not Applicable": 7,
        "Information Not Available": 1,
    }

    score += privacy_scores.get(privacy_policy, 0)

    # Data security: maximum 8 points
    security_scores = {
        "Strong": 8,
        "Adequate": 5,
        "Weak": 1,
        "Not Applicable": 8,
        "Information Not Available": 1,
    }

    score += security_scores.get(security_measures, 0)

    return clamp_score(score)


def get_investment_recommendation(overall_score: float) -> str:
    """
    Convert the overall score into an investment recommendation.
    """

    if overall_score >= 80:
        return "Strong Investment Candidate"

    if overall_score >= 65:
        return "Promising – Proceed with Detailed Due Diligence"

    if overall_score >= 50:
        return "Moderate Potential – Proceed with Caution"

    if overall_score >= 35:
        return "High Risk – Significant Improvements Required"

    return "Not Recommended at Present"


def get_risk_level(overall_score: float) -> str:
    """
    Convert the overall score into a risk level.
    """

    if overall_score >= 80:
        return "Low"

    if overall_score >= 65:
        return "Low to Moderate"

    if overall_score >= 50:
        return "Moderate"

    if overall_score >= 35:
        return "High"

    return "Critical"

def calculate_due_diligence_scores(
    startup_record: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate all category scores and the weighted overall score.

    The Legal & Compliance category combines:
    - 35% general legal readiness
    - 65% detailed FinTech compliance readiness
    """

    financial_score = startup_record["calculated_metrics"].get(
        "financial_health_score",
        0.0,
    )

    team_score = calculate_team_score(
        startup_record["founders_and_team"]
    )

    product_score = calculate_product_score(
        startup_record["product"]
    )

    market_score = calculate_market_score(
        startup_record["market"]
    )

    customer_score = calculate_customer_score(
        startup_record["customers"]
    )

    funding_score = calculate_funding_score(
        startup_record["funding"]
    )

    # General legal readiness from the original legal section.
    legal_score = calculate_legal_score(
        legal=startup_record.get(
            "legal_and_compliance",
            {},
        ),
        company=startup_record.get(
            "company",
            {},
        ),
    )

    # Detailed FinTech compliance assessment.
    compliance_result = calculate_compliance_score(
        startup_record.get(
            "compliance",
            {},
        )
    )

    fintech_compliance_score = compliance_result[
        "compliance_score"
    ]

    # Combine general legal readiness and FinTech compliance.
    combined_legal_compliance_score = clamp_score(
        (legal_score * 0.35)
        + (fintech_compliance_score * 0.65)
    )

    category_scores = {
        "Financial Health": financial_score,
        "Founders & Team": team_score,
        "Product & Technology": product_score,
        "Market Opportunity": market_score,
        "Customers & Traction": customer_score,
        "Funding Position": funding_score,
        "Legal & Compliance": combined_legal_compliance_score,
    }

    overall_score = sum(
        category_scores[category]
        * CATEGORY_WEIGHTS[category]
        for category in category_scores
    )

    overall_score = clamp_score(overall_score)

    return {
        "category_scores": category_scores,
        "category_weights": CATEGORY_WEIGHTS,
        "overall_score": overall_score,
        "risk_level": get_risk_level(overall_score),
        "investment_recommendation": (
            get_investment_recommendation(overall_score)
        ),
        "compliance_result": compliance_result,
        "legal_compliance_breakdown": {
            "legal_score": legal_score,
            "fintech_compliance_score": fintech_compliance_score,
            "combined_score": combined_legal_compliance_score,
        },
    }