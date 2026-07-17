from __future__ import annotations

from typing import Any


def calculate_profit_loss(
    monthly_revenue: float,
    monthly_expenses: float,
) -> float:
    """
    Calculate monthly profit or loss.

    A positive result indicates profit.
    A negative result indicates loss.
    """

    return monthly_revenue - monthly_expenses


def calculate_burn_rate(
    monthly_revenue: float,
    monthly_expenses: float,
) -> float:
    """
    Calculate the monthly net burn rate.

    Burn rate represents how much cash the startup is losing
    every month.

    If revenue is greater than or equal to expenses,
    the burn rate is zero.
    """

    return max(monthly_expenses - monthly_revenue, 0.0)


def calculate_cash_runway(
    cash_balance: float,
    burn_rate: float,
) -> float | None:
    """
    Calculate how many months the startup can continue operating.

    None is returned when the startup has no current burn rate.
    """

    if burn_rate <= 0:
        return None

    return cash_balance / burn_rate


def calculate_profit_margin(
    monthly_revenue: float,
    profit_loss: float,
) -> float | None:
    """
    Calculate profit margin as a percentage.

    None is returned when revenue is zero.
    """

    if monthly_revenue <= 0:
        return None

    return (profit_loss / monthly_revenue) * 100


def calculate_current_ratio(
    current_assets: float,
    current_liabilities: float,
) -> float | None:
    """
    Calculate the current ratio.

    Current ratio = Current assets / Current liabilities

    None is returned when current liabilities are zero.
    """

    if current_liabilities <= 0:
        return None

    return current_assets / current_liabilities


def calculate_debt_to_equity_ratio(
    total_debt: float,
    total_equity: float,
) -> float | None:
    """
    Calculate the debt-to-equity ratio.

    None is returned when total equity is zero.
    """

    if total_equity <= 0:
        return None

    return total_debt / total_equity


def calculate_revenue_expense_ratio(
    monthly_revenue: float,
    monthly_expenses: float,
) -> float | None:
    """
    Calculate revenue relative to expenses.

    A value above 1 means revenue is higher than expenses.
    """

    if monthly_expenses <= 0:
        return None

    return monthly_revenue / monthly_expenses


def calculate_ltv_cac_ratio(
    customer_lifetime_value: float,
    customer_acquisition_cost: float,
) -> float | None:
    """
    Calculate the customer lifetime value to acquisition cost ratio.

    None is returned when customer acquisition cost is zero.
    """

    if customer_acquisition_cost <= 0:
        return None

    return customer_lifetime_value / customer_acquisition_cost


def calculate_financial_health_score(
    monthly_revenue: float,
    monthly_expenses: float,
    revenue_growth_rate: float,
    cash_runway_months: float | None,
    current_ratio: float | None,
    debt_to_equity_ratio: float | None,
    financial_records_available: str,
) -> float:
    """
    Calculate a rule-based financial health score out of 100.

    This is an analytical prototype score and not a guaranteed
    investment recommendation.
    """

    score = 0.0

    # ---------------------------------------------------------
    # PROFITABILITY: MAXIMUM 25 POINTS
    # ---------------------------------------------------------
    if monthly_revenue > monthly_expenses:
        score += 25
    elif monthly_revenue == monthly_expenses and monthly_revenue > 0:
        score += 18
    elif monthly_revenue > 0:
        score += 10

    # ---------------------------------------------------------
    # REVENUE GROWTH: MAXIMUM 20 POINTS
    # ---------------------------------------------------------
    if revenue_growth_rate >= 30:
        score += 20
    elif revenue_growth_rate >= 15:
        score += 16
    elif revenue_growth_rate >= 5:
        score += 12
    elif revenue_growth_rate >= 0:
        score += 7

    # ---------------------------------------------------------
    # CASH RUNWAY: MAXIMUM 20 POINTS
    # ---------------------------------------------------------
    if cash_runway_months is None:
        score += 20
    elif cash_runway_months >= 18:
        score += 20
    elif cash_runway_months >= 12:
        score += 16
    elif cash_runway_months >= 6:
        score += 10
    elif cash_runway_months >= 3:
        score += 5

    # ---------------------------------------------------------
    # LIQUIDITY: MAXIMUM 15 POINTS
    # ---------------------------------------------------------
    if current_ratio is None:
        score += 5
    elif current_ratio >= 2:
        score += 15
    elif current_ratio >= 1.5:
        score += 12
    elif current_ratio >= 1:
        score += 8
    elif current_ratio >= 0.5:
        score += 4

    # ---------------------------------------------------------
    # DEBT LEVEL: MAXIMUM 10 POINTS
    # ---------------------------------------------------------
    if debt_to_equity_ratio is None:
        score += 5
    elif debt_to_equity_ratio <= 0.5:
        score += 10
    elif debt_to_equity_ratio <= 1:
        score += 8
    elif debt_to_equity_ratio <= 2:
        score += 4

    # ---------------------------------------------------------
    # FINANCIAL RECORD QUALITY: MAXIMUM 10 POINTS
    # ---------------------------------------------------------
    record_scores = {
        "Audited Records Available": 10,
        "Unaudited Records Available": 7,
        "Partial Records Available": 4,
        "No Records Available": 0,
    }

    score += record_scores.get(financial_records_available, 0)

    return round(min(score, 100.0), 2)


def generate_financial_warnings(
    monthly_revenue: float,
    monthly_expenses: float,
    revenue_growth_rate: float,
    cash_runway_months: float | None,
    current_ratio: float | None,
    debt_to_equity_ratio: float | None,
    churn_rate: float,
    ltv_cac_ratio: float | None,
    financial_records_available: str,
) -> list[str]:
    """
    Generate financial and business warnings based on entered data.
    """

    warnings: list[str] = []

    if monthly_revenue == 0:
        warnings.append(
            "The startup currently reports no monthly revenue."
        )

    if monthly_expenses > monthly_revenue:
        warnings.append(
            "Monthly expenses are higher than monthly revenue."
        )

    if revenue_growth_rate < 0:
        warnings.append(
            "The startup is reporting negative revenue growth."
        )

    if cash_runway_months is not None:
        if cash_runway_months < 3:
            warnings.append(
                "Cash runway is critically low at less than 3 months."
            )
        elif cash_runway_months < 6:
            warnings.append(
                "Cash runway is low at less than 6 months."
            )
        elif cash_runway_months < 12:
            warnings.append(
                "Cash runway is below the generally safer 12-month level."
            )

    if current_ratio is not None and current_ratio < 1:
        warnings.append(
            "Current liabilities are higher than current assets."
        )

    if (
        debt_to_equity_ratio is not None
        and debt_to_equity_ratio > 2
    ):
        warnings.append(
            "The startup has a high debt-to-equity ratio."
        )

    if churn_rate > 20:
        warnings.append(
            "Customer churn is high at more than 20%."
        )
    elif churn_rate > 10:
        warnings.append(
            "Customer churn requires attention."
        )

    if ltv_cac_ratio is not None:
        if ltv_cac_ratio < 1:
            warnings.append(
                "Customer acquisition cost is greater than "
                "customer lifetime value."
            )
        elif ltv_cac_ratio < 3:
            warnings.append(
                "The LTV-to-CAC ratio is below the preferred level of 3."
            )

    if financial_records_available == "No Records Available":
        warnings.append(
            "No financial records are available for verification."
        )
    elif financial_records_available == "Partial Records Available":
        warnings.append(
            "Only partial financial records are available."
        )

    return warnings


def get_financial_health_label(score: float) -> str:
    """
    Convert the financial score into a readable category.
    """

    if score >= 80:
        return "Excellent"

    if score >= 65:
        return "Good"

    if score >= 45:
        return "Moderate"

    if score >= 25:
        return "Weak"

    return "Critical"


def calculate_all_financial_metrics(
    monthly_revenue: float,
    monthly_expenses: float,
    cash_balance: float,
    current_assets: float,
    current_liabilities: float,
    total_debt: float,
    total_equity: float,
    revenue_growth_rate: float,
    customer_lifetime_value: float,
    customer_acquisition_cost: float,
    churn_rate: float,
    financial_records_available: str,
) -> dict[str, Any]:
    """
    Calculate all financial metrics and return them together.

    This function acts as the main entry point for financial analysis.
    """

    profit_loss = calculate_profit_loss(
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
    )

    burn_rate = calculate_burn_rate(
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
    )

    cash_runway_months = calculate_cash_runway(
        cash_balance=cash_balance,
        burn_rate=burn_rate,
    )

    profit_margin = calculate_profit_margin(
        monthly_revenue=monthly_revenue,
        profit_loss=profit_loss,
    )

    current_ratio = calculate_current_ratio(
        current_assets=current_assets,
        current_liabilities=current_liabilities,
    )

    debt_to_equity_ratio = calculate_debt_to_equity_ratio(
        total_debt=total_debt,
        total_equity=total_equity,
    )

    revenue_expense_ratio = calculate_revenue_expense_ratio(
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
    )

    ltv_cac_ratio = calculate_ltv_cac_ratio(
        customer_lifetime_value=customer_lifetime_value,
        customer_acquisition_cost=customer_acquisition_cost,
    )

    financial_health_score = calculate_financial_health_score(
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
        revenue_growth_rate=revenue_growth_rate,
        cash_runway_months=cash_runway_months,
        current_ratio=current_ratio,
        debt_to_equity_ratio=debt_to_equity_ratio,
        financial_records_available=financial_records_available,
    )

    financial_warnings = generate_financial_warnings(
        monthly_revenue=monthly_revenue,
        monthly_expenses=monthly_expenses,
        revenue_growth_rate=revenue_growth_rate,
        cash_runway_months=cash_runway_months,
        current_ratio=current_ratio,
        debt_to_equity_ratio=debt_to_equity_ratio,
        churn_rate=churn_rate,
        ltv_cac_ratio=ltv_cac_ratio,
        financial_records_available=financial_records_available,
    )

    return {
        "profit_loss": profit_loss,
        "burn_rate": burn_rate,
        "cash_runway_months": cash_runway_months,
        "profit_margin_percentage": profit_margin,
        "current_ratio": current_ratio,
        "debt_to_equity_ratio": debt_to_equity_ratio,
        "revenue_expense_ratio": revenue_expense_ratio,
        "ltv_cac_ratio": ltv_cac_ratio,
        "financial_health_score": financial_health_score,
        "financial_health_label": get_financial_health_label(
            financial_health_score
        ),
        "financial_warnings": financial_warnings,
    }