from typing import Any


# ============================================================
# RECOMMENDATION CONSTANTS
# ============================================================

RECOMMENDATION_PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


INVESTMENT_DECISIONS = {
    "INVEST": "Invest",
    "INVEST_WITH_CONDITIONS": "Invest with Conditions",
    "HOLD": "Hold",
    "REJECT": "Reject",
}


# ============================================================
# SAFE CONVERSION HELPERS
# ============================================================

def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convert a value to float safely.

    Invalid, empty, or missing values return the provided default.
    """

    try:
        if value is None or value == "":
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Convert a value to integer safely.

    Invalid, empty, or missing values return the provided default.
    """

    try:
        if value is None or value == "":
            return default

        return int(float(value))

    except (TypeError, ValueError):
        return default


# ============================================================
# RECOMMENDATION CREATION
# ============================================================

def create_recommendation(
    category: str,
    title: str,
    description: str,
    priority: str,
    action: str,
    rationale: str = "",
    expected_impact: str = "",
) -> dict[str, str]:
    """
    Create a standard recommendation object.

    Parameters
    ----------
    category:
        Recommendation category such as Financial Health,
        Market Opportunity, or Legal & Compliance.

    title:
        Short recommendation heading.

    description:
        Explanation of the issue or improvement opportunity.

    priority:
        One of Critical, High, Medium, or Low.

    action:
        Specific action the startup should take.

    rationale:
        Reason why the recommendation is important.

    expected_impact:
        Expected outcome after implementing the recommendation.
    """

    valid_priorities = {
        "Critical",
        "High",
        "Medium",
        "Low",
    }

    normalized_priority = (
        priority
        if priority in valid_priorities
        else "Low"
    )

    return {
        "category": str(category).strip(),
        "title": str(title).strip(),
        "description": str(description).strip(),
        "priority": normalized_priority,
        "action": str(action).strip(),
        "rationale": str(rationale).strip(),
        "expected_impact": str(expected_impact).strip(),
    }


# ============================================================
# RECOMMENDATION SORTING
# ============================================================

def sort_recommendations_by_priority(
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Sort recommendations from highest to lowest priority.

    Recommendations with the same priority keep their
    original relative order.
    """

    return sorted(
        recommendations,
        key=lambda recommendation: (
            RECOMMENDATION_PRIORITY_ORDER.get(
                str(
                    recommendation.get(
                        "priority",
                        "Low",
                    )
                ),
                0,
            )
        ),
        reverse=True,
    )


# ============================================================
# DUPLICATE REMOVAL
# ============================================================

def remove_duplicate_recommendations(
    recommendations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Remove duplicate recommendations.

    Two recommendations are considered duplicates when their
    category and title are the same, ignoring letter case and
    surrounding spaces.
    """

    unique_recommendations: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()

    for recommendation in recommendations:
        category = str(
            recommendation.get(
                "category",
                "",
            )
        ).strip().lower()

        title = str(
            recommendation.get(
                "title",
                "",
            )
        ).strip().lower()

        duplicate_key = (
            category,
            title,
        )

        if duplicate_key in seen_keys:
            continue

        seen_keys.add(duplicate_key)
        unique_recommendations.append(
            recommendation
        )

    return unique_recommendations


# ============================================================
# PRIORITY FILTERING
# ============================================================

def filter_recommendations_by_priority(
    recommendations: list[dict[str, Any]],
    priorities: list[str],
) -> list[dict[str, Any]]:
    """
    Return only recommendations whose priority appears in
    the provided priority list.
    """

    allowed_priorities = {
        str(priority).strip()
        for priority in priorities
    }

    return [
        recommendation
        for recommendation in recommendations
        if str(
            recommendation.get(
                "priority",
                "",
            )
        ).strip()
        in allowed_priorities
    ]


# ============================================================
# TOP RECOMMENDATION SELECTION
# ============================================================

def get_top_recommendations(
    recommendations: list[dict[str, Any]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Return the highest-priority recommendations.

    Duplicate recommendations are removed before sorting.
    """

    if limit <= 0:
        return []

    unique_recommendations = (
        remove_duplicate_recommendations(
            recommendations
        )
    )

    sorted_recommendations = (
        sort_recommendations_by_priority(
            unique_recommendations
        )
    )

    return sorted_recommendations[:limit]


# ============================================================
# RECOMMENDATION SUMMARY
# ============================================================

def count_recommendations_by_priority(
    recommendations: list[dict[str, Any]],
) -> dict[str, int]:
    """
    Count recommendations by priority level.
    """

    counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
    }

    for recommendation in recommendations:
        priority = str(
            recommendation.get(
                "priority",
                "Low",
            )
        )

        if priority not in counts:
            priority = "Low"

        counts[priority] += 1

    return counts


def group_recommendations_by_category(
    recommendations: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Group recommendations by their category.
    """

    grouped: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for recommendation in recommendations:
        category = str(
            recommendation.get(
                "category",
                "General",
            )
        ).strip()

        if not category:
            category = "General"

        grouped.setdefault(
            category,
            [],
        ).append(recommendation)

    return grouped

# ============================================================
# RISK FINDING TO RECOMMENDATION CONVERSION
# ============================================================

RISK_SEVERITY_TO_PRIORITY = {
    "Critical": "Critical",
    "High": "High",
    "Medium": "Medium",
    "Low": "Low",
}


def _get_finding_priority(
    finding: dict[str, Any],
) -> str:
    """
    Convert a risk finding severity into a recommendation
    priority.
    """

    severity = str(
        finding.get(
            "severity",
            "Low",
        )
    ).strip()

    return RISK_SEVERITY_TO_PRIORITY.get(
        severity,
        "Low",
    )


def _get_finding_action(
    finding: dict[str, Any],
) -> str:
    """
    Extract the recommended action from a risk finding.

    A fallback action is returned when the finding does not
    contain a recommendation.
    """

    action = str(
        finding.get(
            "recommendation",
            "",
        )
    ).strip()

    if action:
        return action

    title = str(
        finding.get(
            "title",
            "identified risk",
        )
    ).strip()

    return (
        f"Investigate and resolve the issue related to "
        f"{title.lower()}."
    )


def recommendation_from_risk_finding(
    finding: dict[str, Any],
    default_category: str = "General",
) -> dict[str, str]:
    """
    Convert one risk finding into a standard recommendation.
    """

    category = str(
        finding.get(
            "category",
            default_category,
        )
    ).strip()

    if not category:
        category = default_category

    title = str(
        finding.get(
            "title",
            "Risk requires attention",
        )
    ).strip()

    description = str(
        finding.get(
            "description",
            "",
        )
    ).strip()

    rationale = str(
        finding.get(
            "impact",
            "",
        )
    ).strip()

    priority = _get_finding_priority(
        finding
    )

    action = _get_finding_action(
        finding
    )

    expected_impact = (
        "Reduced due-diligence risk and improved startup "
        "readiness."
    )

    if priority == "Critical":
        expected_impact = (
            "Removal of a critical investment blocker and "
            "prevention of major financial, legal, or "
            "operational exposure."
        )

    elif priority == "High":
        expected_impact = (
            "Material reduction in investment risk and "
            "improved startup credibility."
        )

    elif priority == "Medium":
        expected_impact = (
            "Improved operational readiness and stronger "
            "due-diligence results."
        )

    elif priority == "Low":
        expected_impact = (
            "Incremental improvement in startup quality and "
            "investor confidence."
        )

    return create_recommendation(
        category=category,
        title=title,
        description=description,
        priority=priority,
        action=action,
        rationale=rationale,
        expected_impact=expected_impact,
    )


def recommendations_from_findings(
    findings: list[dict[str, Any]],
    default_category: str = "General",
) -> list[dict[str, str]]:
    """
    Convert multiple risk findings into recommendations.
    """

    recommendations: list[dict[str, str]] = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        recommendations.append(
            recommendation_from_risk_finding(
                finding=finding,
                default_category=default_category,
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# CATEGORY RISK EXTRACTION
# ============================================================

def _get_category_risk(
    risk_report: dict[str, Any],
    category: str,
) -> dict[str, Any]:
    """
    Safely retrieve one category's risk analysis result.
    """

    category_risks = risk_report.get(
        "category_risks",
        {},
    )

    category_result = category_risks.get(
        category,
        {},
    )

    if not isinstance(category_result, dict):
        return {}

    return category_result


def _get_category_findings(
    risk_report: dict[str, Any],
    category: str,
) -> list[dict[str, Any]]:
    """
    Safely retrieve findings for one risk category.
    """

    category_result = _get_category_risk(
        risk_report=risk_report,
        category=category,
    )

    findings = category_result.get(
        "findings",
        [],
    )

    if not isinstance(findings, list):
        return []

    return [
        finding
        for finding in findings
        if isinstance(finding, dict)
    ]


# ============================================================
# FINANCIAL RECOMMENDATIONS
# ============================================================

def generate_financial_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate recommendations related to financial health.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Financial Health",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Financial Health",
    )

    financial_data = startup_record.get(
        "financial",
        {},
    )

    calculated_metrics = startup_record.get(
        "calculated_metrics",
        {},
    )

    monthly_revenue = _safe_float(
        financial_data.get(
            "monthly_revenue",
            0,
        )
    )

    monthly_expenses = _safe_float(
        financial_data.get(
            "monthly_expenses",
            0,
        )
    )

    cash_runway = _safe_float(
        calculated_metrics.get(
            "cash_runway_months",
            0,
        )
    )

    financial_health_score = _safe_float(
        calculated_metrics.get(
            "financial_health_score",
            0,
        )
    )

    if monthly_revenue <= 0:
        recommendations.append(
            create_recommendation(
                category="Financial Health",
                title="Establish a measurable revenue model",
                description=(
                    "The startup currently reports no recurring "
                    "monthly revenue."
                ),
                priority="High",
                action=(
                    "Define pricing, validate willingness to pay, "
                    "and establish monthly revenue targets."
                ),
                rationale=(
                    "A startup without measurable revenue has "
                    "limited evidence of commercial validation."
                ),
                expected_impact=(
                    "Improved revenue predictability and stronger "
                    "investor confidence."
                ),
            )
        )

    if (
        monthly_expenses > monthly_revenue
        and monthly_expenses > 0
    ):
        recommendations.append(
            create_recommendation(
                category="Financial Health",
                title="Reduce the monthly cash burn",
                description=(
                    "Monthly expenses exceed monthly revenue."
                ),
                priority="High",
                action=(
                    "Review major expense categories, remove "
                    "non-essential spending, and prepare a "
                    "cost-reduction plan."
                ),
                rationale=(
                    "Persistent negative cash flow can reduce "
                    "runway and increase dependence on external "
                    "funding."
                ),
                expected_impact=(
                    "Lower burn rate, longer runway, and improved "
                    "financial sustainability."
                ),
            )
        )

    if 0 < cash_runway < 6:
        recommendations.append(
            create_recommendation(
                category="Financial Health",
                title="Extend the available cash runway",
                description=(
                    "The calculated cash runway is below six "
                    "months."
                ),
                priority="Critical",
                action=(
                    "Immediately prepare a runway-extension plan "
                    "through cost control, revenue acceleration, "
                    "or bridge funding."
                ),
                rationale=(
                    "A short runway creates an immediate business "
                    "continuity and fundraising risk."
                ),
                expected_impact=(
                    "Reduced liquidity risk and additional time "
                    "to achieve business milestones."
                ),
            )
        )

    if financial_health_score < 40:
        recommendations.append(
            create_recommendation(
                category="Financial Health",
                title="Prepare a financial recovery plan",
                description=(
                    "The calculated financial health score is "
                    "weak."
                ),
                priority="High",
                action=(
                    "Create a documented plan covering revenue "
                    "growth, expense control, liquidity, debt, "
                    "and unit economics."
                ),
                rationale=(
                    "Weak overall financial health can affect "
                    "valuation, funding eligibility, and business "
                    "continuity."
                ),
                expected_impact=(
                    "A clearer path toward financial stability "
                    "and improved investor readiness."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# FOUNDERS AND TEAM RECOMMENDATIONS
# ============================================================

def generate_team_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate recommendations related to founders and team.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Founders & Team",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Founders & Team",
    )

    team_data = startup_record.get(
        "founders_and_team",
        {},
    )

    founder_count = _safe_int(
        team_data.get(
            "founder_count",
            0,
        )
    )

    technical_strength = _safe_float(
        team_data.get(
            "technical_team_strength",
            0,
        )
    )

    business_strength = _safe_float(
        team_data.get(
            "business_team_strength",
            0,
        )
    )

    key_person_dependency = str(
        team_data.get(
            "key_person_dependency",
            "",
        )
    ).strip().lower()

    if founder_count <= 1:
        recommendations.append(
            create_recommendation(
                category="Founders & Team",
                title="Reduce single-founder dependency",
                description=(
                    "The business appears highly dependent on one "
                    "founder."
                ),
                priority="High",
                action=(
                    "Build a dependable leadership team, assign "
                    "clear responsibilities, and document critical "
                    "operating processes."
                ),
                rationale=(
                    "Single-founder dependency increases execution "
                    "and continuity risk."
                ),
                expected_impact=(
                    "Improved leadership resilience and reduced "
                    "key-person exposure."
                ),
            )
        )

    if technical_strength < 5:
        recommendations.append(
            create_recommendation(
                category="Founders & Team",
                title="Strengthen technical leadership",
                description=(
                    "The technical capability of the current team "
                    "is below the preferred level."
                ),
                priority="High",
                action=(
                    "Hire or appoint an experienced technical lead "
                    "and create a technology delivery roadmap."
                ),
                rationale=(
                    "Weak technical leadership can delay product "
                    "delivery, scalability, and security."
                ),
                expected_impact=(
                    "Improved technology execution and product "
                    "development quality."
                ),
            )
        )

    if business_strength < 5:
        recommendations.append(
            create_recommendation(
                category="Founders & Team",
                title="Improve commercial leadership",
                description=(
                    "The team has limited business-development or "
                    "commercial capability."
                ),
                priority="High",
                action=(
                    "Add experienced sales, finance, operations, "
                    "or business-development leadership."
                ),
                rationale=(
                    "A technically strong product may still fail "
                    "without sales and operational execution."
                ),
                expected_impact=(
                    "Stronger go-to-market execution and improved "
                    "revenue-generation capability."
                ),
            )
        )

    if key_person_dependency == "high":
        recommendations.append(
            create_recommendation(
                category="Founders & Team",
                title="Create a succession and delegation plan",
                description=(
                    "Important business knowledge or authority is "
                    "concentrated in one person."
                ),
                priority="High",
                action=(
                    "Delegate responsibilities, document critical "
                    "knowledge, and identify backups for key roles."
                ),
                rationale=(
                    "High key-person dependency can disrupt the "
                    "business if that individual becomes "
                    "unavailable."
                ),
                expected_impact=(
                    "Improved operational continuity and reduced "
                    "leadership concentration risk."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# PRODUCT AND TECHNOLOGY RECOMMENDATIONS
# ============================================================

def generate_product_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate product and technology recommendations.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Product & Technology",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Product & Technology",
    )

    product_data = startup_record.get(
        "product",
        {},
    )

    product_stage = str(
        product_data.get(
            "product_stage",
            "",
        )
    ).strip().lower()

    working_mvp = str(
        product_data.get(
            "working_mvp",
            "",
        )
    ).strip().lower()

    technology_readiness = _safe_float(
        product_data.get(
            "technology_readiness",
            0,
        )
    )

    scalability = _safe_float(
        product_data.get(
            "product_scalability",
            0,
        )
    )

    if (
        product_stage in {
            "",
            "concept",
            "concept only",
            "idea",
        }
        or working_mvp in {
            "",
            "no",
            "false",
        }
    ):
        recommendations.append(
            create_recommendation(
                category="Product & Technology",
                title="Develop and validate a working MVP",
                description=(
                    "The product has not yet demonstrated a "
                    "sufficiently validated working version."
                ),
                priority="High",
                action=(
                    "Build a minimum viable product, test it with "
                    "representative customers, and document the "
                    "results."
                ),
                rationale=(
                    "An MVP provides evidence that the product can "
                    "solve the intended problem."
                ),
                expected_impact=(
                    "Improved product validation and reduced "
                    "technology execution risk."
                ),
            )
        )

    if technology_readiness < 5:
        recommendations.append(
            create_recommendation(
                category="Product & Technology",
                title="Improve technology readiness",
                description=(
                    "The current technology readiness level is "
                    "below the preferred threshold."
                ),
                priority="High",
                action=(
                    "Prepare a technical roadmap covering "
                    "architecture, testing, security, deployment, "
                    "and operational reliability."
                ),
                rationale=(
                    "Low technology readiness can create delays, "
                    "failures, and unexpected development costs."
                ),
                expected_impact=(
                    "More reliable product delivery and lower "
                    "technical implementation risk."
                ),
            )
        )

    if scalability < 5:
        recommendations.append(
            create_recommendation(
                category="Product & Technology",
                title="Create a product scalability plan",
                description=(
                    "The product may not currently support rapid "
                    "customer or transaction growth."
                ),
                priority="Medium",
                action=(
                    "Perform load testing, identify bottlenecks, "
                    "and document the infrastructure scaling "
                    "strategy."
                ),
                rationale=(
                    "Scalability limitations can reduce service "
                    "quality as the startup grows."
                ),
                expected_impact=(
                    "Improved capacity planning and readiness for "
                    "future growth."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# MARKET RECOMMENDATIONS
# ============================================================

def generate_market_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate market opportunity recommendations.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Market Opportunity",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Market Opportunity",
    )

    market_data = startup_record.get(
        "market",
        {},
    )

    target_customers = str(
        market_data.get(
            "target_customers",
            "",
        )
    ).strip()

    tam = _safe_float(
        market_data.get(
            "total_addressable_market",
            0,
        )
    )

    sam = _safe_float(
        market_data.get(
            "serviceable_available_market",
            0,
        )
    )

    competitive_advantage = _safe_float(
        market_data.get(
            "competitive_advantage_strength",
            0,
        )
    )

    if not target_customers:
        recommendations.append(
            create_recommendation(
                category="Market Opportunity",
                title="Define the target customer segment",
                description=(
                    "The intended customer group is not clearly "
                    "defined."
                ),
                priority="High",
                action=(
                    "Create detailed customer profiles covering "
                    "industry, size, geography, needs, budget, and "
                    "buying behaviour."
                ),
                rationale=(
                    "An unclear target customer makes product, "
                    "pricing, and marketing decisions unreliable."
                ),
                expected_impact=(
                    "More focused product development and "
                    "go-to-market execution."
                ),
            )
        )

    if tam <= 0 or sam <= 0:
        recommendations.append(
            create_recommendation(
                category="Market Opportunity",
                title="Validate the addressable market",
                description=(
                    "The total or serviceable market has not been "
                    "supported with measurable estimates."
                ),
                priority="High",
                action=(
                    "Estimate TAM and SAM using documented market "
                    "data, realistic assumptions, and customer "
                    "segmentation."
                ),
                rationale=(
                    "Investors require evidence that the market is "
                    "large enough to support meaningful growth."
                ),
                expected_impact=(
                    "Stronger market credibility and improved "
                    "valuation justification."
                ),
            )
        )

    if tam > 0 and sam > tam:
        recommendations.append(
            create_recommendation(
                category="Market Opportunity",
                title="Correct the market-size assumptions",
                description=(
                    "The serviceable market is larger than the "
                    "total addressable market."
                ),
                priority="High",
                action=(
                    "Review and correct the TAM and SAM "
                    "calculations with consistent definitions."
                ),
                rationale=(
                    "Inconsistent market sizing reduces investor "
                    "confidence in the startup's projections."
                ),
                expected_impact=(
                    "More reliable market analysis and financial "
                    "forecasting."
                ),
            )
        )

    if competitive_advantage < 5:
        recommendations.append(
            create_recommendation(
                category="Market Opportunity",
                title="Strengthen competitive differentiation",
                description=(
                    "The startup currently has a weak competitive "
                    "advantage."
                ),
                priority="High",
                action=(
                    "Identify defensible advantages such as data, "
                    "technology, partnerships, cost, distribution, "
                    "or regulatory capability."
                ),
                rationale=(
                    "Weak differentiation makes it easier for "
                    "competitors to acquire the same customers."
                ),
                expected_impact=(
                    "Improved market positioning and stronger "
                    "customer-acquisition potential."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# CUSTOMER AND TRACTION RECOMMENDATIONS
# ============================================================

def generate_customer_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate customer and traction recommendations.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Customers & Traction",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Customers & Traction",
    )

    customer_data = startup_record.get(
        "customers",
        {},
    )

    total_customers = _safe_int(
        customer_data.get(
            "total_customers",
            0,
        )
    )

    retention_rate = _safe_float(
        customer_data.get(
            "retention_rate",
            0,
        )
    )

    churn_rate = _safe_float(
        customer_data.get(
            "churn_rate",
            0,
        )
    )

    cac = _safe_float(
        customer_data.get(
            "customer_acquisition_cost",
            0,
        )
    )

    ltv = _safe_float(
        customer_data.get(
            "customer_lifetime_value",
            0,
        )
    )

    if total_customers <= 0:
        recommendations.append(
            create_recommendation(
                category="Customers & Traction",
                title="Obtain initial customer validation",
                description=(
                    "The startup currently reports no active "
                    "customers."
                ),
                priority="High",
                action=(
                    "Run pilot programs, secure design partners, "
                    "and collect measurable customer feedback."
                ),
                rationale=(
                    "Customer validation demonstrates that the "
                    "product solves a real and valuable problem."
                ),
                expected_impact=(
                    "Improved product-market-fit evidence and "
                    "stronger investment readiness."
                ),
            )
        )

    if retention_rate > 0 and retention_rate < 70:
        recommendations.append(
            create_recommendation(
                category="Customers & Traction",
                title="Improve customer retention",
                description=(
                    "The reported customer retention rate is weak."
                ),
                priority="High",
                action=(
                    "Analyse cancellation reasons, improve "
                    "onboarding, and introduce proactive customer "
                    "success processes."
                ),
                rationale=(
                    "Poor retention reduces customer lifetime "
                    "value and weakens recurring growth."
                ),
                expected_impact=(
                    "Higher recurring revenue and stronger "
                    "customer lifetime value."
                ),
            )
        )

    if churn_rate >= 15:
        recommendations.append(
            create_recommendation(
                category="Customers & Traction",
                title="Reduce customer churn",
                description=(
                    "Customer churn is at a materially high level."
                ),
                priority="High",
                action=(
                    "Segment churned customers, identify the main "
                    "causes, and implement retention interventions."
                ),
                rationale=(
                    "High churn can offset new customer growth and "
                    "make acquisition spending inefficient."
                ),
                expected_impact=(
                    "Improved revenue stability and sustainable "
                    "customer growth."
                ),
            )
        )

    if cac > 0 and ltv > 0 and ltv / cac < 3:
        recommendations.append(
            create_recommendation(
                category="Customers & Traction",
                title="Improve customer unit economics",
                description=(
                    "The customer lifetime value to acquisition "
                    "cost ratio is below the preferred level."
                ),
                priority="High",
                action=(
                    "Reduce acquisition costs, improve pricing, "
                    "increase retention, and expand customer "
                    "lifetime value."
                ),
                rationale=(
                    "Weak unit economics can make customer growth "
                    "financially unsustainable."
                ),
                expected_impact=(
                    "More efficient customer growth and improved "
                    "profitability."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# FUNDING RECOMMENDATIONS
# ============================================================

def generate_funding_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate funding-position recommendations.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Funding Position",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Funding Position",
    )

    funding_data = startup_record.get(
        "funding",
        {},
    )

    valuation = _safe_float(
        funding_data.get(
            "current_valuation",
            0,
        )
    )

    funding_sought = _safe_float(
        funding_data.get(
            "funding_sought",
            0,
        )
    )

    equity_offered = _safe_float(
        funding_data.get(
            "equity_offered",
            0,
        )
    )

    use_of_funds = str(
        funding_data.get(
            "use_of_funds",
            "",
        )
    ).strip()

    if funding_sought > 0 and valuation <= 0:
        recommendations.append(
            create_recommendation(
                category="Funding Position",
                title="Provide a defensible startup valuation",
                description=(
                    "Funding is being requested without a stated "
                    "valuation."
                ),
                priority="Critical",
                action=(
                    "Prepare a valuation supported by financial "
                    "performance, traction, market size, growth, "
                    "and comparable transactions."
                ),
                rationale=(
                    "Investors cannot assess funding terms without "
                    "a defensible valuation."
                ),
                expected_impact=(
                    "Clearer investment terms and stronger funding "
                    "credibility."
                ),
            )
        )

    if funding_sought > 0 and not use_of_funds:
        recommendations.append(
            create_recommendation(
                category="Funding Position",
                title="Define the use of investment funds",
                description=(
                    "The startup has not explained how the "
                    "requested capital will be allocated."
                ),
                priority="Critical",
                action=(
                    "Create a milestone-based allocation covering "
                    "product, team, marketing, operations, "
                    "compliance, and contingency reserves."
                ),
                rationale=(
                    "Investors need visibility into how capital "
                    "will create measurable business value."
                ),
                expected_impact=(
                    "Improved capital accountability and stronger "
                    "investor confidence."
                ),
            )
        )

    if equity_offered > 50:
        recommendations.append(
            create_recommendation(
                category="Funding Position",
                title="Review the proposed equity dilution",
                description=(
                    "The proposed equity offer may create excessive "
                    "founder dilution."
                ),
                priority="Critical",
                action=(
                    "Reassess the funding amount, valuation, and "
                    "equity structure with professional financial "
                    "and legal advice."
                ),
                rationale=(
                    "Excessive dilution can reduce founder control "
                    "and create long-term governance problems."
                ),
                expected_impact=(
                    "A more sustainable ownership structure and "
                    "better alignment between founders and "
                    "investors."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# LEGAL AND COMPLIANCE RECOMMENDATIONS
# ============================================================

def generate_compliance_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Generate legal and regulatory compliance recommendations.
    """

    findings = _get_category_findings(
        risk_report=risk_report,
        category="Legal & Compliance",
    )

    recommendations = recommendations_from_findings(
        findings=findings,
        default_category="Legal & Compliance",
    )

    compliance_data = startup_record.get(
        "compliance",
        {},
    )

    regulator_identified = bool(
        compliance_data.get(
            "regulator_identified",
            False,
        )
    )

    regulatory_registration = bool(
        compliance_data.get(
            "regulatory_registration",
            False,
        )
    )

    required_licenses = bool(
        compliance_data.get(
            "required_licenses",
            False,
        )
    )

    kyc_implemented = bool(
        compliance_data.get(
            "kyc_implemented",
            False,
        )
    )

    aml_implemented = bool(
        compliance_data.get(
            "aml_implemented",
            False,
        )
    )

    transaction_monitoring = bool(
        compliance_data.get(
            "transaction_monitoring",
            False,
        )
    )

    if not regulator_identified:
        recommendations.append(
            create_recommendation(
                category="Legal & Compliance",
                title="Identify the applicable financial regulator",
                description=(
                    "The startup has not clearly identified the "
                    "regulator governing its financial activities."
                ),
                priority="Critical",
                action=(
                    "Obtain regulatory advice and document all "
                    "applicable regulators, laws, and reporting "
                    "requirements."
                ),
                rationale=(
                    "Operating without understanding the applicable "
                    "regulatory framework can expose the startup to "
                    "enforcement action."
                ),
                expected_impact=(
                    "Reduced regulatory uncertainty and improved "
                    "compliance readiness."
                ),
            )
        )

    if not regulatory_registration:
        recommendations.append(
            create_recommendation(
                category="Legal & Compliance",
                title="Complete regulatory registration",
                description=(
                    "Required regulatory registration has not been "
                    "confirmed."
                ),
                priority="Critical",
                action=(
                    "Verify registration obligations and complete "
                    "the required applications before conducting "
                    "regulated activities."
                ),
                rationale=(
                    "Unregistered financial activity may result in "
                    "penalties or suspension."
                ),
                expected_impact=(
                    "Improved legal operating readiness and lower "
                    "enforcement risk."
                ),
            )
        )

    if not required_licenses:
        recommendations.append(
            create_recommendation(
                category="Legal & Compliance",
                title="Obtain all required financial licences",
                description=(
                    "The availability of required licences has not "
                    "been confirmed."
                ),
                priority="Critical",
                action=(
                    "Prepare a licence checklist and obtain all "
                    "mandatory approvals before product launch or "
                    "expansion."
                ),
                rationale=(
                    "Missing licences can make business activities "
                    "legally non-compliant."
                ),
                expected_impact=(
                    "Reduced legal risk and improved ability to "
                    "operate regulated services."
                ),
            )
        )

    if not kyc_implemented or not aml_implemented:
        recommendations.append(
            create_recommendation(
                category="Legal & Compliance",
                title="Implement complete KYC and AML controls",
                description=(
                    "The startup does not yet demonstrate complete "
                    "customer verification and anti-money-"
                    "laundering controls."
                ),
                priority="Critical",
                action=(
                    "Implement risk-based KYC, customer due "
                    "diligence, sanctions screening, AML policies, "
                    "record keeping, and escalation procedures."
                ),
                rationale=(
                    "Weak KYC and AML controls can expose a FinTech "
                    "business to fraud, money laundering, and "
                    "regulatory penalties."
                ),
                expected_impact=(
                    "Reduced financial-crime exposure and improved "
                    "regulatory compliance."
                ),
            )
        )

    if not transaction_monitoring:
        recommendations.append(
            create_recommendation(
                category="Legal & Compliance",
                title="Introduce transaction monitoring",
                description=(
                    "The startup does not currently confirm an "
                    "active transaction-monitoring system."
                ),
                priority="High",
                action=(
                    "Implement transaction rules, risk thresholds, "
                    "alert review, suspicious-activity escalation, "
                    "and audit logs."
                ),
                rationale=(
                    "Transaction monitoring is essential for "
                    "detecting suspicious or fraudulent financial "
                    "activity."
                ),
                expected_impact=(
                    "Earlier detection of financial crime and "
                    "stronger compliance oversight."
                ),
            )
        )

    return remove_duplicate_recommendations(
        recommendations
    )


# ============================================================
# ALL CATEGORY RECOMMENDATIONS
# ============================================================

def generate_all_category_recommendations(
    startup_record: dict[str, Any],
    risk_report: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    """
    Generate recommendations for all due-diligence categories.
    """

    return {
        "Financial Health": (
            generate_financial_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
        "Founders & Team": (
            generate_team_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
        "Product & Technology": (
            generate_product_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
        "Market Opportunity": (
            generate_market_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
        "Customers & Traction": (
            generate_customer_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
        "Funding Position": (
            generate_funding_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
        "Legal & Compliance": (
            generate_compliance_recommendations(
                startup_record=startup_record,
                risk_report=risk_report,
            )
        ),
    }


def flatten_category_recommendations(
    category_recommendations: dict[
        str,
        list[dict[str, Any]],
    ],
) -> list[dict[str, Any]]:
    """
    Combine category-wise recommendations into one list.
    """

    flattened: list[dict[str, Any]] = []

    for recommendations in (
        category_recommendations.values()
    ):
        if not isinstance(recommendations, list):
            continue

        flattened.extend(
            recommendation
            for recommendation in recommendations
            if isinstance(recommendation, dict)
        )

    unique_recommendations = (
        remove_duplicate_recommendations(
            flattened
        )
    )

    return sort_recommendations_by_priority(
        unique_recommendations
    )
# ============================================================
# INVESTMENT DECISION CONFIGURATION
# ============================================================

INVESTMENT_SCORE_THRESHOLDS = {
    "Invest": {
        "minimum_due_diligence_score": 75.0,
        "maximum_risk_score": 30.0,
    },
    "Invest with Conditions": {
        "minimum_due_diligence_score": 60.0,
        "maximum_risk_score": 50.0,
    },
    "Hold": {
        "minimum_due_diligence_score": 40.0,
        "maximum_risk_score": 70.0,
    },
}


DECISION_CONFIDENCE_LABELS = {
    "High": "High Confidence",
    "Moderate": "Moderate Confidence",
    "Low": "Low Confidence",
}


# ============================================================
# SAFE REPORT EXTRACTION
# ============================================================

def _get_due_diligence_score(
    scoring_result: dict[str, Any],
) -> float:
    """
    Safely extract the overall due-diligence score.
    """

    possible_keys = (
        "overall_score",
        "total_score",
        "due_diligence_score",
        "weighted_score",
        "final_score",
    )

    for key in possible_keys:
        if key in scoring_result:
            return max(
                0.0,
                min(
                    _safe_float(
                        scoring_result.get(key),
                        0.0,
                    ),
                    100.0,
                ),
            )

    return 0.0


def _get_overall_risk_score(
    risk_report: dict[str, Any],
) -> float:
    """
    Safely extract the adjusted overall risk score.
    """

    return max(
        0.0,
        min(
            _safe_float(
                risk_report.get(
                    "overall_risk_score",
                    risk_report.get(
                        "weighted_risk_score",
                        0.0,
                    ),
                ),
                0.0,
            ),
            100.0,
        ),
    )


def _get_overall_risk_level(
    risk_report: dict[str, Any],
) -> str:
    """
    Safely extract the overall risk level.
    """

    level = str(
        risk_report.get(
            "overall_risk_level",
            "Low",
        )
    ).strip()

    valid_levels = {
        "Low",
        "Moderate",
        "High",
        "Critical",
    }

    if level not in valid_levels:
        return "Low"

    return level


def _get_all_risk_findings(
    risk_report: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Safely extract all consolidated risk findings.
    """

    findings = risk_report.get(
        "all_findings",
        [],
    )

    if not isinstance(findings, list):
        return []

    return [
        finding
        for finding in findings
        if isinstance(finding, dict)
    ]


def _get_positive_signals(
    risk_report: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Safely extract positive signals from the risk report.
    """

    signals = risk_report.get(
        "positive_signals",
        [],
    )

    if not isinstance(signals, list):
        return []

    normalized_signals: list[dict[str, Any]] = []

    for signal in signals:
        if isinstance(signal, dict):
            normalized_signals.append(signal)

        elif isinstance(signal, str):
            normalized_signals.append(
                {
                    "category": "General",
                    "signal": signal,
                }
            )

    return normalized_signals


# ============================================================
# RED FLAGS
# ============================================================

def extract_red_flags(
    risk_report: dict[str, Any],
) -> list[dict[str, str]]:
    """
    Extract critical and high-severity risk findings.
    """

    red_flags: list[dict[str, str]] = []

    for finding in _get_all_risk_findings(
        risk_report
    ):
        severity = str(
            finding.get(
                "severity",
                "Low",
            )
        ).strip()

        if severity not in {
            "Critical",
            "High",
        }:
            continue

        red_flags.append(
            {
                "category": str(
                    finding.get(
                        "category",
                        "General",
                    )
                ).strip(),
                "title": str(
                    finding.get(
                        "title",
                        "Risk requires attention",
                    )
                ).strip(),
                "severity": severity,
                "description": str(
                    finding.get(
                        "description",
                        "",
                    )
                ).strip(),
                "impact": str(
                    finding.get(
                        "impact",
                        "",
                    )
                ).strip(),
            }
        )

    return sorted(
        red_flags,
        key=lambda item: (
            RECOMMENDATION_PRIORITY_ORDER.get(
                item["severity"],
                0,
            )
        ),
        reverse=True,
    )


# ============================================================
# STRENGTHS
# ============================================================

def extract_strengths(
    risk_report: dict[str, Any],
    scoring_result: dict[str, Any],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Extract startup strengths from positive risk signals and
    high category scores.
    """

    strengths: list[dict[str, Any]] = []

    for signal in _get_positive_signals(
        risk_report
    ):
        signal_text = str(
            signal.get(
                "signal",
                "",
            )
        ).strip()

        if not signal_text:
            continue

        strengths.append(
            {
                "category": str(
                    signal.get(
                        "category",
                        "General",
                    )
                ).strip(),
                "title": signal_text,
                "source": "Risk Analysis",
            }
        )

    category_scores = scoring_result.get(
        "category_scores",
        {},
    )

    if isinstance(category_scores, dict):
        for category, score in category_scores.items():
            numeric_score = _safe_float(
                score,
                0.0,
            )

            if numeric_score < 75:
                continue

            strengths.append(
                {
                    "category": str(category),
                    "title": (
                        f"Strong performance in {category}"
                    ),
                    "source": "Scoring Engine",
                    "score": round(
                        numeric_score,
                        2,
                    ),
                }
            )

    unique_strengths: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for strength in strengths:
        key = (
            str(
                strength.get(
                    "category",
                    "",
                )
            ).strip().lower(),
            str(
                strength.get(
                    "title",
                    "",
                )
            ).strip().lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_strengths.append(strength)

    return unique_strengths[:max(limit, 0)]


# ============================================================
# WEAKNESSES
# ============================================================

def extract_weaknesses(
    risk_report: dict[str, Any],
    scoring_result: dict[str, Any],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Extract startup weaknesses from findings and weak scores.
    """

    weaknesses: list[dict[str, Any]] = []

    for finding in _get_all_risk_findings(
        risk_report
    ):
        severity = str(
            finding.get(
                "severity",
                "Low",
            )
        ).strip()

        if severity not in {
            "Critical",
            "High",
            "Medium",
        }:
            continue

        weaknesses.append(
            {
                "category": str(
                    finding.get(
                        "category",
                        "General",
                    )
                ).strip(),
                "title": str(
                    finding.get(
                        "title",
                        "Identified weakness",
                    )
                ).strip(),
                "severity": severity,
                "description": str(
                    finding.get(
                        "description",
                        "",
                    )
                ).strip(),
            }
        )

    category_scores = scoring_result.get(
        "category_scores",
        {},
    )

    if isinstance(category_scores, dict):
        for category, score in category_scores.items():
            numeric_score = _safe_float(
                score,
                0.0,
            )

            if numeric_score >= 50:
                continue

            weaknesses.append(
                {
                    "category": str(category),
                    "title": (
                        f"Weak performance in {category}"
                    ),
                    "severity": (
                        "High"
                        if numeric_score < 30
                        else "Medium"
                    ),
                    "score": round(
                        numeric_score,
                        2,
                    ),
                }
            )

    weaknesses = sorted(
        weaknesses,
        key=lambda item: (
            RECOMMENDATION_PRIORITY_ORDER.get(
                str(
                    item.get(
                        "severity",
                        "Low",
                    )
                ),
                0,
            )
        ),
        reverse=True,
    )

    unique_weaknesses: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for weakness in weaknesses:
        key = (
            str(
                weakness.get(
                    "category",
                    "",
                )
            ).strip().lower(),
            str(
                weakness.get(
                    "title",
                    "",
                )
            ).strip().lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        unique_weaknesses.append(weakness)

    return unique_weaknesses[:max(limit, 0)]


# ============================================================
# INVESTMENT DECISION LOGIC
# ============================================================

def determine_investment_decision(
    scoring_result: dict[str, Any],
    risk_report: dict[str, Any],
) -> str:
    """
    Determine the investment recommendation.

    The decision uses:
    - overall due-diligence score
    - overall risk score
    - overall risk level
    - critical findings
    - risk overrides
    """

    due_diligence_score = _get_due_diligence_score(
        scoring_result
    )

    risk_score = _get_overall_risk_score(
        risk_report
    )

    risk_level = _get_overall_risk_level(
        risk_report
    )

    red_flags = extract_red_flags(
        risk_report
    )

    critical_red_flags = [
        red_flag
        for red_flag in red_flags
        if red_flag["severity"] == "Critical"
    ]

    override_applied = bool(
        risk_report.get(
            "override_applied",
            False,
        )
    )

    if (
        risk_level == "Critical"
        or critical_red_flags
        or risk_score >= 75
    ):
        return INVESTMENT_DECISIONS["REJECT"]

    if (
        due_diligence_score >= 75
        and risk_score <= 30
        and risk_level == "Low"
        and not override_applied
    ):
        return INVESTMENT_DECISIONS["INVEST"]

    if (
        due_diligence_score >= 60
        and risk_score <= 50
        and risk_level in {
            "Low",
            "Moderate",
        }
    ):
        return INVESTMENT_DECISIONS[
            "INVEST_WITH_CONDITIONS"
        ]

    if (
        due_diligence_score >= 40
        and risk_score <= 70
        and risk_level in {
            "Moderate",
            "High",
        }
    ):
        return INVESTMENT_DECISIONS["HOLD"]

    return INVESTMENT_DECISIONS["REJECT"]


# ============================================================
# DECISION CONFIDENCE
# ============================================================

def calculate_decision_confidence(
    scoring_result: dict[str, Any],
    risk_report: dict[str, Any],
) -> dict[str, Any]:
    """
    Estimate confidence in the investment decision.

    Confidence is higher when:
    - score and risk results strongly agree
    - sufficient category data is available
    - the result is far from decision thresholds
    """

    due_diligence_score = _get_due_diligence_score(
        scoring_result
    )

    risk_score = _get_overall_risk_score(
        risk_report
    )

    category_scores = scoring_result.get(
        "category_scores",
        {},
    )

    available_category_count = 0

    if isinstance(category_scores, dict):
        available_category_count = sum(
            1
            for value in category_scores.values()
            if value is not None
        )

    completeness_score = min(
        available_category_count / 7,
        1.0,
    )

    score_risk_alignment = abs(
        due_diligence_score
        - (100.0 - risk_score)
    )

    alignment_component = max(
        0.0,
        1.0 - score_risk_alignment / 100.0,
    )

    distance_from_neutral = (
        abs(due_diligence_score - 50.0)
        + abs(risk_score - 50.0)
    ) / 100.0

    raw_confidence = (
        completeness_score * 40
        + alignment_component * 35
        + min(distance_from_neutral, 1.0) * 25
    )

    confidence_score = round(
        min(
            max(
                raw_confidence,
                0.0,
            ),
            100.0,
        ),
        2,
    )

    if confidence_score >= 75:
        confidence_level = "High"

    elif confidence_score >= 50:
        confidence_level = "Moderate"

    else:
        confidence_level = "Low"

    return {
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "confidence_label": (
            DECISION_CONFIDENCE_LABELS[
                confidence_level
            ]
        ),
        "available_category_count": (
            available_category_count
        ),
        "score_risk_alignment_difference": round(
            score_risk_alignment,
            2,
        ),
    }


# ============================================================
# INVESTMENT CONDITIONS
# ============================================================

def generate_investment_conditions(
    recommendations: list[dict[str, Any]],
    decision: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Return key conditions that should be completed before
    investment.
    """

    if decision not in {
        INVESTMENT_DECISIONS[
            "INVEST_WITH_CONDITIONS"
        ],
        INVESTMENT_DECISIONS["HOLD"],
    }:
        return []

    priority_recommendations = (
        filter_recommendations_by_priority(
            recommendations,
            priorities=[
                "Critical",
                "High",
            ],
        )
    )

    return get_top_recommendations(
        priority_recommendations,
        limit=limit,
    )


# ============================================================
# DECISION RATIONALE
# ============================================================

def generate_decision_rationale(
    decision: str,
    scoring_result: dict[str, Any],
    risk_report: dict[str, Any],
) -> str:
    """
    Generate a plain-language explanation for the final
    investment decision.
    """

    score = _get_due_diligence_score(
        scoring_result
    )

    risk_score = _get_overall_risk_score(
        risk_report
    )

    risk_level = _get_overall_risk_level(
        risk_report
    )

    red_flags = extract_red_flags(
        risk_report
    )

    critical_count = sum(
        1
        for flag in red_flags
        if flag["severity"] == "Critical"
    )

    high_count = sum(
        1
        for flag in red_flags
        if flag["severity"] == "High"
    )

    if decision == INVESTMENT_DECISIONS["INVEST"]:
        return (
            f"The startup achieved a due-diligence score of "
            f"{score:.2f}/100 with an overall risk score of "
            f"{risk_score:.2f}/100. The risk level is "
            f"{risk_level}, and no material investment blocker "
            f"was identified."
        )

    if (
        decision
        == INVESTMENT_DECISIONS[
            "INVEST_WITH_CONDITIONS"
        ]
    ):
        return (
            f"The startup achieved a due-diligence score of "
            f"{score:.2f}/100 and a risk score of "
            f"{risk_score:.2f}/100. The opportunity is "
            f"potentially investable, but identified high-priority "
            f"risks should be resolved through defined investment "
            f"conditions."
        )

    if decision == INVESTMENT_DECISIONS["HOLD"]:
        return (
            f"The startup achieved a due-diligence score of "
            f"{score:.2f}/100 with a risk score of "
            f"{risk_score:.2f}/100. The current risk level is "
            f"{risk_level}, with {high_count} high-severity "
            f"finding(s). Further validation and risk reduction "
            f"are required before an investment decision."
        )

    return (
        f"The startup achieved a due-diligence score of "
        f"{score:.2f}/100 with an overall risk score of "
        f"{risk_score:.2f}/100. The assessment identified "
        f"{critical_count} critical and {high_count} high-severity "
        f"finding(s), making the opportunity unsuitable for "
        f"investment in its current state."
    )


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

def generate_executive_summary(
    startup_record: dict[str, Any],
    scoring_result: dict[str, Any],
    risk_report: dict[str, Any],
    decision: str,
    strengths: list[dict[str, Any]],
    weaknesses: list[dict[str, Any]],
    red_flags: list[dict[str, Any]],
) -> str:
    """
    Generate an investor-facing executive summary.
    """

    company_data = startup_record.get(
        "company",
        {},
    )

    company_name = str(
        company_data.get(
            "company_name",
            company_data.get(
                "name",
                "The startup",
            ),
        )
    ).strip()

    if not company_name:
        company_name = "The startup"

    score = _get_due_diligence_score(
        scoring_result
    )

    risk_score = _get_overall_risk_score(
        risk_report
    )

    risk_level = _get_overall_risk_level(
        risk_report
    )

    strongest_categories = [
        strength.get(
            "category",
            "General",
        )
        for strength in strengths[:3]
    ]

    weakest_categories = [
        weakness.get(
            "category",
            "General",
        )
        for weakness in weaknesses[:3]
    ]

    strongest_text = (
        ", ".join(
            dict.fromkeys(
                str(category)
                for category in strongest_categories
            )
        )
        if strongest_categories
        else "no clearly established category strengths"
    )

    weakest_text = (
        ", ".join(
            dict.fromkeys(
                str(category)
                for category in weakest_categories
            )
        )
        if weakest_categories
        else "no major weaknesses"
    )

    return (
        f"{company_name} received an overall due-diligence score "
        f"of {score:.2f}/100 and an adjusted risk score of "
        f"{risk_score:.2f}/100, corresponding to a "
        f"{risk_level} risk profile. The current investment "
        f"recommendation is '{decision}'. Key strengths are "
        f"concentrated in {strongest_text}, while the main areas "
        f"requiring attention are {weakest_text}. The assessment "
        f"identified {len(red_flags)} material red flag(s). "
        f"Investors should review the highest-priority actions and "
        f"any proposed investment conditions before proceeding."
    )


# ============================================================
# COMPLETE RECOMMENDATION REPORT
# ============================================================

def generate_recommendation_report(
    startup_record: dict[str, Any],
    scoring_result: dict[str, Any],
    risk_report: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate the complete investor recommendation report.

    This is the main public function intended for dashboards,
    PDF reports, and final platform integration.
    """

    category_recommendations = (
        generate_all_category_recommendations(
            startup_record=startup_record,
            risk_report=risk_report,
        )
    )

    all_recommendations = (
        flatten_category_recommendations(
            category_recommendations
        )
    )

    decision = determine_investment_decision(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    confidence = calculate_decision_confidence(
        scoring_result=scoring_result,
        risk_report=risk_report,
    )

    red_flags = extract_red_flags(
        risk_report
    )

    strengths = extract_strengths(
        risk_report=risk_report,
        scoring_result=scoring_result,
    )

    weaknesses = extract_weaknesses(
        risk_report=risk_report,
        scoring_result=scoring_result,
    )

    top_recommendations = get_top_recommendations(
        all_recommendations,
        limit=5,
    )

    investment_conditions = (
        generate_investment_conditions(
            recommendations=all_recommendations,
            decision=decision,
            limit=5,
        )
    )

    priority_counts = (
        count_recommendations_by_priority(
            all_recommendations
        )
    )

    decision_rationale = (
        generate_decision_rationale(
            decision=decision,
            scoring_result=scoring_result,
            risk_report=risk_report,
        )
    )

    executive_summary = (
        generate_executive_summary(
            startup_record=startup_record,
            scoring_result=scoring_result,
            risk_report=risk_report,
            decision=decision,
            strengths=strengths,
            weaknesses=weaknesses,
            red_flags=red_flags,
        )
    )

    return {
        "investment_decision": decision,
        "decision_rationale": decision_rationale,
        "decision_confidence": confidence,
        "executive_summary": executive_summary,
        "category_recommendations": (
            category_recommendations
        ),
        "all_recommendations": all_recommendations,
        "top_recommendations": top_recommendations,
        "investment_conditions": (
            investment_conditions
        ),
        "recommendation_counts": priority_counts,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "red_flags": red_flags,
        "due_diligence_score": (
            _get_due_diligence_score(
                scoring_result
            )
        ),
        "overall_risk_score": (
            _get_overall_risk_score(
                risk_report
            )
        ),
        "overall_risk_level": (
            _get_overall_risk_level(
                risk_report
            )
        ),
    }


def generate_investment_recommendation(
    startup_record: dict[str, Any],
    scoring_result: dict[str, Any],
    risk_report: dict[str, Any],
) -> dict[str, Any]:
    """
    Public convenience alias for generating the complete
    investment recommendation report.
    """

    return generate_recommendation_report(
        startup_record=startup_record,
        scoring_result=scoring_result,
        risk_report=risk_report,
    )