from src.financial_metrics import (
    calculate_burn_rate,
    calculate_cash_runway,
    calculate_current_ratio,
    calculate_debt_to_equity_ratio,
    calculate_ltv_cac_ratio,
    calculate_profit_loss,
)


def test_profit_calculation() -> None:
    result = calculate_profit_loss(
        monthly_revenue=700000,
        monthly_expenses=500000,
    )

    assert result == 200000


def test_loss_calculation() -> None:
    result = calculate_profit_loss(
        monthly_revenue=500000,
        monthly_expenses=700000,
    )

    assert result == -200000


def test_burn_rate() -> None:
    result = calculate_burn_rate(
        monthly_revenue=500000,
        monthly_expenses=700000,
    )

    assert result == 200000


def test_zero_burn_rate_for_profitable_startup() -> None:
    result = calculate_burn_rate(
        monthly_revenue=700000,
        monthly_expenses=500000,
    )

    assert result == 0


def test_cash_runway() -> None:
    result = calculate_cash_runway(
        cash_balance=5000000,
        burn_rate=200000,
    )

    assert result == 25


def test_cash_runway_without_burn() -> None:
    result = calculate_cash_runway(
        cash_balance=5000000,
        burn_rate=0,
    )

    assert result is None


def test_current_ratio() -> None:
    result = calculate_current_ratio(
        current_assets=3000000,
        current_liabilities=1500000,
    )

    assert result == 2


def test_debt_to_equity_ratio() -> None:
    result = calculate_debt_to_equity_ratio(
        total_debt=1000000,
        total_equity=5000000,
    )

    assert result == 0.2


def test_ltv_cac_ratio() -> None:
    result = calculate_ltv_cac_ratio(
        customer_lifetime_value=8000,
        customer_acquisition_cost=1000,
    )

    assert result == 8