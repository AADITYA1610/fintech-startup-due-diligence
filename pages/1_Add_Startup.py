"""
AI-Powered Startup Due Diligence Platform
------------------------------------------
Single-file app (app.py)

Required packages (add to requirements.txt):
    streamlit
    pandas
    numpy
    plotly
    reportlab
    matplotlib

Run with:  streamlit run app.py

WHAT CHANGED IN THIS VERSION
-----------------------------
- The "Add Startup" page is now a tab inside app.py (no separate pages/ file).
- Every saved startup gets an automatic scoring pass (build_category_scores)
  covering Financials, Team, Product, Market, Customers, Funding, Legal.
  NOTE: this is a placeholder scoring engine built from the fields already
  collected in the form. Swap `build_category_scores()` out for your real
  Due Diligence Scoring Engine whenever it's ready — everything downstream
  (charts, PDF, dashboard) only depends on the dict it returns.
- Right after a startup is saved, interactive Plotly charts for THAT startup
  are shown, plus a "Download PDF Report" button scoped to that startup.
- The Dashboard tab aggregates every startup saved this session. If none
  have been saved yet, it falls back to clearly-labeled demo data.
"""

from __future__ import annotations

import io
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from src.financial_metrics import calculate_all_financial_metrics

# ReportLab (PDF generation)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
)

# Matplotlib is used ONLY to rasterize charts for embedding in PDFs
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


CATEGORY_NAMES = ["Financials", "Team", "Product", "Market", "Customers", "Funding", "Legal"]


# --------------------------------------------------------------------------- #
# PAGE CONFIG
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Startup Due Diligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------- #
# SESSION STATE
# --------------------------------------------------------------------------- #
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "startup_records" not in st.session_state:
    st.session_state.startup_records = []  # each entry: form data + "scores" + "meta"


# --------------------------------------------------------------------------- #
# THEME / CSS
# --------------------------------------------------------------------------- #
def get_theme_colors(dark: bool) -> dict:
    if dark:
        return {
            "bg": "#0E1117",
            "bg_secondary": "#161B22",
            "card_bg": "linear-gradient(135deg, #1B2130 0%, #10141C 100%)",
            "text": "#F5F6FA",
            "sub_text": "#9CA3AF",
            "border": "#2A3040",
            "accent1": "#6C63FF",
            "accent2": "#00D4B4",
            "accent3": "#FF6B9D",
            "shadow": "0 8px 24px rgba(0,0,0,0.45)",
        }
    return {
        "bg": "#F7F8FC",
        "bg_secondary": "#FFFFFF",
        "card_bg": "linear-gradient(135deg, #FFFFFF 0%, #F1F3FF 100%)",
        "text": "#1A1D29",
        "sub_text": "#5B6270",
        "border": "#E6E8F0",
        "accent1": "#5B4EF5",
        "accent2": "#00B899",
        "accent3": "#F5537C",
        "shadow": "0 8px 24px rgba(91,78,245,0.12)",
    }


def inject_css(t: dict) -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: {t['bg']};
            color: {t['text']};
        }}

        section[data-testid="stSidebar"] {{
            background: {t['bg_secondary']};
            border-right: 1px solid {t['border']};
        }}

        .hero {{
            padding: 2.2rem 2.5rem;
            border-radius: 20px;
            background: linear-gradient(120deg, {t['accent1']} 0%, {t['accent3']} 100%);
            box-shadow: {t['shadow']};
            margin-bottom: 1.8rem;
        }}
        .hero h1 {{
            font-family: 'Poppins', sans-serif;
            font-weight: 800;
            font-size: 2.1rem;
            color: #FFFFFF;
            margin-bottom: 0.4rem;
        }}
        .hero p {{
            color: rgba(255,255,255,0.9);
            font-size: 1.02rem;
            max-width: 780px;
            margin: 0;
        }}

        .kpi-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 1.3rem 1.4rem;
            box-shadow: {t['shadow']};
            transition: transform 0.15s ease;
        }}
        .kpi-card:hover {{ transform: translateY(-4px); }}
        .kpi-label {{
            font-size: 0.82rem;
            font-weight: 600;
            color: {t['sub_text']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .kpi-value {{
            font-family: 'Poppins', sans-serif;
            font-size: 2.0rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }}

        .section-title {{
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 1.3rem;
            color: {t['text']};
            margin: 1.4rem 0 0.8rem 0;
            border-left: 5px solid {t['accent1']};
            padding-left: 0.7rem;
        }}

        .info-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 1.2rem 1.3rem;
            box-shadow: {t['shadow']};
            height: 100%;
        }}
        .info-card h4 {{ font-family: 'Poppins', sans-serif; color: {t['accent1']}; margin-bottom: 0.4rem; }}
        .info-card p {{ color: {t['sub_text']}; font-size: 0.92rem; line-height: 1.45; }}

        .demo-badge {{
            display: inline-block;
            background: {t['accent3']};
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 0.15rem 0.6rem;
            border-radius: 20px;
            margin-left: 0.5rem;
        }}

        .footer-note {{
            text-align: center;
            color: {t['sub_text']};
            font-size: 0.8rem;
            margin-top: 2.5rem;
            padding-top: 1rem;
            border-top: 1px solid {t['border']};
        }}

        div[data-testid="stDownloadButton"] button {{
            background: linear-gradient(120deg, {t['accent1']}, {t['accent3']});
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.4rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# SCORING ENGINE (placeholder — swap for the real engine when ready)
# --------------------------------------------------------------------------- #
def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def safe_num(value: Any, default: float = 0.0) -> float:
    return value if isinstance(value, (int, float)) else default


def build_category_scores(record: dict[str, Any]) -> dict[str, Any]:
    """Derive category scores, overall score, risk level and recommendation
    from the raw form data + calculated financial metrics."""

    metrics = record["calculated_metrics"]
    team = record["founders_and_team"]
    product = record["product"]
    market = record["market"]
    customers = record["customers"]
    funding = record["funding"]
    legal = record["legal_and_compliance"]

    # --- Financials: reuse the financial health score from financial_metrics.py
    financials_score = clamp(safe_num(metrics.get("financial_health_score"), 50))

    # --- Team
    team_experience_bonus = {"Yes": 5, "Partially": 2, "No": 0, "Information Not Available": 0}
    key_person_penalty = {"High": 8, "Moderate": 3, "Low": 0, "Information Not Available": 0}
    team_score = clamp(
        (team["technical_team_strength"] + team["business_team_strength"] + team["team_stability"]) / 3 * 10
        + team_experience_bonus.get(team["previous_startup_experience"], 0)
        - key_person_penalty.get(team["key_person_dependency"], 0)
    )

    # --- Product
    stage_bonus = {
        "Concept Only": -10, "Prototype": -5, "Minimum Viable Product": 0,
        "Early Customers": 5, "Market Ready": 10, "Scaling": 15,
    }
    mvp_bonus = {"Yes": 5, "No": -5, "Under Development": 0, "Information Not Available": 0}
    product_score = clamp(
        (product["product_uniqueness"] + product["technology_readiness"] + product["product_scalability"]) / 3 * 10
        + stage_bonus.get(product["product_stage"], 0)
        + mvp_bonus.get(product["working_mvp"], 0)
    )

    # --- Market
    competition_penalty = {"Low": 0, "Moderate": -5, "High": -10, "Very High": -15, "Information Not Available": -5}
    market_score = clamp(
        market["competitive_advantage_strength"] * 10
        + min(max(market["market_growth_rate"], 0), 50) * 0.3
        + competition_penalty.get(market["competition_level"], 0)
    )

    # --- Customers
    ltv_cac = metrics.get("ltv_cac_ratio")
    ltv_bonus = 0
    if isinstance(ltv_cac, (int, float)):
        if ltv_cac >= 3:
            ltv_bonus = 10
        elif ltv_cac >= 1:
            ltv_bonus = 3
        else:
            ltv_bonus = -10
    customers_score = clamp(customers["retention_rate"] - customers["churn_rate"] * 0.5 + ltv_bonus)

    # --- Funding
    funding_score = clamp(
        50
        + min(funding["number_of_funding_rounds"], 5) * 5
        + min(funding["investor_count"], 10) * 2
        + (10 if funding["current_valuation"] > 0 else 0)
        - (10 if funding["equity_offered"] > 30 else 0)
    )

    # --- Legal
    legal_map = {
        "Yes": 10, "Compliant": 10, "No": 10, "Strong": 10, "Adequate": 5, "Not Applicable": 5,
        "Information Not Available": 0, "Partially": 3, "Partially Compliant": 3,
        "Weak": -10, "Non-Compliant": -10,
    }
    legal_fields = [
        legal["required_licenses_available"], legal["tax_compliance"], legal["founder_agreement"],
        legal["employee_agreements"], legal["privacy_policy_available"], legal["data_security_measures"],
    ]
    legal_score = 50.0
    for field_value in legal_fields:
        legal_score += legal_map.get(field_value, 0)
    if legal["pending_lawsuits"] == "Yes":
        legal_score -= 15
    if legal["regulatory_issues"] == "Yes":
        legal_score -= 15
    legal_score = clamp(legal_score)

    category_scores = {
        "Financials": round(financials_score, 1),
        "Team": round(team_score, 1),
        "Product": round(product_score, 1),
        "Market": round(market_score, 1),
        "Customers": round(customers_score, 1),
        "Funding": round(funding_score, 1),
        "Legal": round(legal_score, 1),
    }
    overall_score = round(sum(category_scores.values()) / len(category_scores), 1)

    if overall_score >= 70:
        risk_level, recommendation = "Low", "Invest"
    elif overall_score >= 50:
        risk_level, recommendation = "Medium", "Watch"
    else:
        risk_level, recommendation = "High", "Avoid"

    return {
        "category_scores": category_scores,
        "overall_score": overall_score,
        "risk_level": risk_level,
        "recommendation": recommendation,
    }


# --------------------------------------------------------------------------- #
# DEMO DATA (only used when no real startups exist yet)
# --------------------------------------------------------------------------- #
def build_demo_rows() -> list[dict]:
    rng = np.random.default_rng(42)
    names = ["NovaTech", "GreenGrid", "Finlytics", "MedIQ", "UrbanFleet", "PayNest"]
    rows = []
    for i, name in enumerate(names):
        cat_scores = {c: int(rng.integers(40, 95)) for c in CATEGORY_NAMES}
        overall = int(np.mean(list(cat_scores.values())))
        risk = "Low" if overall >= 70 else "Medium" if overall >= 50 else "High"
        row = {
            "name": name,
            "overall_score": overall,
            "risk_level": risk,
            "recommendation": "Invest" if overall >= 70 else "Watch" if overall >= 50 else "Avoid",
            "date_added": f"2026-0{(i % 6) + 1}-1{i}",
        }
        row.update(cat_scores)
        rows.append(row)
    return rows


def startup_records_to_rows() -> tuple[pd.DataFrame, bool]:
    """Returns (dataframe, is_demo)."""
    records = st.session_state.get("startup_records", [])
    if not records:
        return pd.DataFrame(build_demo_rows()), True

    rows = []
    for record in records:
        scores = record["scores"]
        row = {
            "name": record["company"]["company_name"],
            "overall_score": scores["overall_score"],
            "risk_level": scores["risk_level"],
            "recommendation": scores["recommendation"],
            "date_added": record["meta"]["date_added"],
        }
        row.update(scores["category_scores"])
        rows.append(row)
    return pd.DataFrame(rows), False


# --------------------------------------------------------------------------- #
# CHART HELPERS (interactive, Plotly — used live in the app)
# --------------------------------------------------------------------------- #
def render_startup_charts(record: dict[str, Any], scores: dict[str, Any], theme: dict, key_prefix: str) -> None:
    metrics = record["calculated_metrics"]
    cat = scores["category_scores"]

    col1, col2 = st.columns(2)

    with col1:
        labels = list(cat.keys()) + [list(cat.keys())[0]]
        values = list(cat.values()) + [list(cat.values())[0]]
        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=values, theta=labels, fill="toself",
                line_color=theme["accent1"], fillcolor=theme["accent1"], opacity=0.6,
            )
        )
        fig_radar.update_layout(
            title="Category Score Breakdown",
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=30, r=30, t=50, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color=theme["text"],
        )
        st.plotly_chart(fig_radar, use_container_width=True, key=f"{key_prefix}_radar")

    with col2:
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=scores["overall_score"],
                title={"text": "Overall Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": theme["accent1"]},
                    "steps": [
                        {"range": [0, 50], "color": theme["accent3"]},
                        {"range": [50, 70], "color": "#FFD166"},
                        {"range": [70, 100], "color": theme["accent2"]},
                    ],
                },
            )
        )
        fig_gauge.update_layout(
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color=theme["text"],
        )
        st.plotly_chart(fig_gauge, use_container_width=True, key=f"{key_prefix}_gauge")

    col3, col4 = st.columns(2)

    with col3:
        ratio_labels = ["Profit Margin %", "Current Ratio", "Debt-to-Equity", "Revenue/Expense", "LTV/CAC"]
        ratio_values = [
            safe_num(metrics.get("profit_margin_percentage")),
            safe_num(metrics.get("current_ratio")),
            safe_num(metrics.get("debt_to_equity_ratio")),
            safe_num(metrics.get("revenue_expense_ratio")),
            safe_num(metrics.get("ltv_cac_ratio")),
        ]
        fig_ratios = go.Figure(go.Bar(x=ratio_labels, y=ratio_values, marker_color=theme["accent2"]))
        fig_ratios.update_layout(
            title="Key Financial Ratios",
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=theme["text"],
        )
        st.plotly_chart(fig_ratios, use_container_width=True, key=f"{key_prefix}_ratios")

    with col4:
        risks = record["initial_risks"]
        risk_map = {"Low": 1, "Moderate": 2, "High": 3, "Information Not Available": 0}
        risk_labels = ["Financial", "Market", "Technology", "Team", "Legal", "Customer"]
        risk_keys = ["financial_risk", "market_risk", "technology_risk", "team_risk", "legal_risk", "customer_risk"]
        risk_values = [risk_map.get(risks[k], 0) for k in risk_keys]
        fig_risk = go.Figure(go.Bar(x=risk_labels, y=risk_values, marker_color=theme["accent3"]))
        fig_risk.update_layout(
            title="Initial Risk Indicators (0=N/A · 1=Low · 2=Moderate · 3=High)",
            yaxis=dict(range=[0, 3]),
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=theme["text"],
        )
        st.plotly_chart(fig_risk, use_container_width=True, key=f"{key_prefix}_riskbar")


# --------------------------------------------------------------------------- #
# PDF HELPERS
# --------------------------------------------------------------------------- #
def make_matplotlib_category_bar(category_scores: dict[str, float], title: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=150)
    ax.bar(list(category_scores.keys()), list(category_scores.values()), color="#5B4EF5")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score")
    ax.set_title(title)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_startup_pdf(record: dict[str, Any], scores: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=19, textColor=colors.HexColor("#5B4EF5"))
    sub_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=9.5, textColor=colors.grey)
    heading_style = ParagraphStyle("H", parent=styles["Heading2"], textColor=colors.HexColor("#1A1D29"))
    body_style = styles["Normal"]

    company = record["company"]
    financial = record["financial"]
    metrics = record["calculated_metrics"]

    rec_color = {"Invest": "#00B899", "Watch": "#F5A623", "Avoid": "#F5537C"}.get(scores["recommendation"], "#5B4EF5")

    elements = [
        Paragraph(f"{company['company_name']} &mdash; Due Diligence Report", title_style),
        Paragraph(
            f"Generated on {datetime.now().strftime('%d %b %Y, %H:%M')} &nbsp;|&nbsp; "
            f"Industry: {company['industry'] or 'N/A'} &nbsp;|&nbsp; Stage: {company['startup_stage']}",
            sub_style,
        ),
        Spacer(1, 0.5 * cm),
        Paragraph(
            f"<b>Overall Score:</b> {scores['overall_score']}/100 &nbsp;|&nbsp; "
            f"<b>Risk Level:</b> {scores['risk_level']} &nbsp;|&nbsp; "
            f"<font color='{rec_color}'><b>Recommendation: {scores['recommendation']}</b></font>",
            heading_style,
        ),
        Spacer(1, 0.4 * cm),
        Paragraph("Company Overview", heading_style),
    ]

    company_data = [
        ["Headquarters", company.get("headquarters") or "N/A", "Employees", str(company.get("employee_count", "N/A"))],
        ["Founded", company.get("founding_date", "N/A"), "Registration", company.get("registration_status", "N/A")],
    ]
    company_table = Table(company_data, colWidths=[3.3 * cm, 4.7 * cm, 3.3 * cm, 4.7 * cm])
    company_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F7F8FC")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F7F8FC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(company_table)
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Financial Snapshot", heading_style))
    runway = metrics.get("cash_runway_months")
    runway_text = "No Current Burn" if runway is None else f"{runway:.1f} months"
    fin_data = [
        ["Monthly Revenue", f"Rs. {safe_num(financial['monthly_revenue']):,.2f}",
         "Monthly Profit/Loss", f"Rs. {safe_num(metrics.get('profit_loss')):,.2f}"],
        ["Burn Rate", f"Rs. {safe_num(metrics.get('burn_rate')):,.2f}", "Cash Runway", runway_text],
        ["Financial Health", f"{metrics.get('financial_health_score', 'N/A')}/100 "
                              f"({metrics.get('financial_health_label', 'N/A')})",
         "Profit Margin", f"{safe_num(metrics.get('profit_margin_percentage')):.2f}%"],
        ["Current Ratio", f"{safe_num(metrics.get('current_ratio')):.2f}",
         "Debt-to-Equity", f"{safe_num(metrics.get('debt_to_equity_ratio')):.2f}"],
    ]
    fin_table = Table(fin_data, colWidths=[3.3 * cm, 4.7 * cm, 3.3 * cm, 4.7 * cm])
    fin_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6E8F0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F7F8FC")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F7F8FC")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(fin_table)
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Category Score Breakdown", heading_style))
    chart_buf = make_matplotlib_category_bar(scores["category_scores"], "Category Scores")
    elements.append(RLImage(chart_buf, width=15 * cm, height=8.2 * cm))
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("Financial Warnings", heading_style))
    warnings = metrics.get("financial_warnings", [])
    if warnings:
        for warning in warnings:
            elements.append(Paragraph(f"&bull; {warning}", body_style))
    else:
        elements.append(Paragraph("No major financial warning identified.", body_style))

    elements.append(Spacer(1, 0.6 * cm))
    footer_style = ParagraphStyle("F", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    elements.append(Paragraph(
        "Generated automatically by the AI-Powered Startup Due Diligence Platform. "
        "Scores are model-based estimates and should be reviewed alongside independent due diligence.",
        footer_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_portfolio_pdf(df: pd.DataFrame, category_cols: list[str], is_demo: bool) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#5B4EF5"))
    subtitle_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=10, textColor=colors.grey)
    heading_style = ParagraphStyle("H", parent=styles["Heading2"], textColor=colors.HexColor("#1A1D29"))

    elements = [
        Paragraph("AI-Powered Startup Due Diligence Report", title_style),
        Paragraph(
            f"Generated on {datetime.now().strftime('%d %b %Y, %H:%M')}"
            + (" &nbsp;|&nbsp; <font color='#F5537C'>DEMO DATA</font>" if is_demo else ""),
            subtitle_style,
        ),
        Spacer(1, 0.6 * cm),
        Paragraph("Portfolio Summary", heading_style),
    ]

    total = len(df)
    low_risk = int((df["risk_level"] == "Low").sum()) if total else 0
    high_risk = int((df["risk_level"] == "High").sum()) if total else 0
    avg_score = round(df["overall_score"].mean(), 1) if total else 0.0

    summary_data = [
        ["Startups Evaluated", "Low-Risk", "High-Risk", "Average Score"],
        [str(total), str(low_risk), str(high_risk), f"{avg_score}/100"],
    ]
    summary_table = Table(summary_data, colWidths=[4 * cm] * 4)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5B4EF5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6E8F0")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F7F8FC")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Average Score by Category", heading_style))
    if category_cols:
        avg_by_cat = df[category_cols].mean().to_dict()
    else:
        avg_by_cat = {}
    chart_buf = make_matplotlib_category_bar(avg_by_cat, "Average Score by Category")
    elements.append(RLImage(chart_buf, width=15 * cm, height=8.2 * cm))
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Startup-Level Detail", heading_style))
    table_cols = [c for c in ["name", "overall_score", "risk_level", "recommendation"] if c in df.columns]
    header = ["Startup", "Score", "Risk", "Recommendation"][: len(table_cols)]
    detail_data = [header] + df[table_cols].astype(str).values.tolist()
    detail_table = Table(detail_data, colWidths=[4.5 * cm, 3 * cm, 3 * cm, 4 * cm])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A1D29")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F8FC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.8 * cm))

    footer_style = ParagraphStyle("F", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    elements.append(Paragraph(
        "Generated automatically by the AI-Powered Startup Due Diligence Platform. "
        "Scores are model-based estimates and should be reviewed alongside independent due diligence.",
        footer_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------- #
# FORM SUPPORT FUNCTIONS (from the original Add Startup page)
# --------------------------------------------------------------------------- #
def validate_startup_data(
    company_name: str, industry: str, founder_count: int,
    monthly_revenue: float, monthly_expenses: float, cash_balance: float,
) -> list[str]:
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
    if value is None:
        return "Not Available"
    return f"₹{value:,.2f}"


def format_ratio(value: float | None) -> str:
    if value is None:
        return "Not Available"
    return f"{value:.2f}"


def format_percentage(value: float | None) -> str:
    if value is None:
        return "Not Available"
    return f"{value:.2f}%"


def display_financial_warnings(warnings: list[str]) -> None:
    if not warnings:
        st.success("No major financial warning was identified from the entered data.")
        return
    st.warning(f"{len(warnings)} financial concern(s) were identified.")
    for warning in warnings:
        st.write(f"- {warning}")


def display_saved_record(record: dict[str, Any], scores: dict[str, Any], theme: dict, key_prefix: str) -> None:
    company = record["company"]
    financial = record["financial"]
    customers = record["customers"]
    metrics = record["calculated_metrics"]

    st.success("Startup information saved successfully.")

    st.subheader("Saved Startup Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.metric(label="Company", value=company["company_name"])
    with summary_col2:
        st.metric(label="Industry", value=company["industry"])
    with summary_col3:
        st.metric(label="Monthly Revenue", value=format_currency(financial["monthly_revenue"]))
    with summary_col4:
        st.metric(label="Monthly Profit/Loss", value=format_currency(metrics["profit_loss"]))

    st.divider()

    st.subheader("Financial Health Assessment")
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)
    with health_col1:
        st.metric(label="Financial Health Score", value=f"{metrics['financial_health_score']}/100")
    with health_col2:
        st.metric(label="Financial Health", value=metrics["financial_health_label"])
    with health_col3:
        st.metric(label="Monthly Burn Rate", value=format_currency(metrics["burn_rate"]))
    with health_col4:
        runway = metrics["cash_runway_months"]
        runway_text = "No Current Burn" if runway is None else f"{runway:.1f} months"
        st.metric(label="Cash Runway", value=runway_text)

    st.markdown("#### Important Financial Ratios")
    ratio_col1, ratio_col2, ratio_col3, ratio_col4 = st.columns(4)
    with ratio_col1:
        st.metric(label="Profit Margin", value=format_percentage(metrics["profit_margin_percentage"]))
    with ratio_col2:
        st.metric(label="Current Ratio", value=format_ratio(metrics["current_ratio"]))
    with ratio_col3:
        st.metric(label="Debt-to-Equity", value=format_ratio(metrics["debt_to_equity_ratio"]))
    with ratio_col4:
        st.metric(label="Revenue/Expense Ratio", value=format_ratio(metrics["revenue_expense_ratio"]))

    customer_ratio_col1, customer_ratio_col2 = st.columns(2)
    with customer_ratio_col1:
        st.metric(label="LTV-to-CAC Ratio", value=format_ratio(metrics["ltv_cac_ratio"]))
    with customer_ratio_col2:
        st.metric(label="Customer Churn Rate", value=format_percentage(customers["churn_rate"]))

    st.markdown("#### Financial Concerns")
    display_financial_warnings(metrics["financial_warnings"])

    # ------------------------------------------------------------------- #
    # NEW: interactive graphs + score summary for this startup
    # ------------------------------------------------------------------- #
    st.divider()
    st.markdown('<div class="section-title">📊 Startup Analysis</div>', unsafe_allow_html=True)

    score_col1, score_col2, score_col3 = st.columns(3)
    with score_col1:
        st.metric("Overall Score", f"{scores['overall_score']}/100")
    with score_col2:
        st.metric("Risk Level", scores["risk_level"])
    with score_col3:
        st.metric("Recommendation", scores["recommendation"])

    render_startup_charts(record, scores, theme, key_prefix)

    # ------------------------------------------------------------------- #
    # NEW: PDF report download for this startup
    # ------------------------------------------------------------------- #
    st.divider()
    pdf_bytes = generate_startup_pdf(record, scores)
    st.download_button(
        label=f"⬇️ Download PDF Report — {company['company_name']}",
        data=pdf_bytes,
        file_name=f"{company['company_name'].strip().replace(' ', '_') or 'startup'}_due_diligence_report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key=f"{key_prefix}_pdf_download",
    )

    with st.expander("View complete saved startup information"):
        st.json(record)


# --------------------------------------------------------------------------- #
# TAB: DASHBOARD
# --------------------------------------------------------------------------- #
def render_dashboard_tab(theme: dict) -> None:
    df, is_demo = startup_records_to_rows()
    category_cols = [c for c in CATEGORY_NAMES if c in df.columns]

    st.markdown(
        """
        <div class="hero">
            <h1>AI-Powered Startup Due Diligence Platform</h1>
            <p>Evaluate startup viability, financial health, growth potential,
            founder strength and investment risk using data-driven analysis —
            all in one interactive dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_demo:
        st.info(
            "📌 No startups have been added yet, so the charts below show "
            "**demo data**. Add a startup in the **Add Startup** tab to "
            "replace this automatically."
        )

    total = len(df)
    low_risk = int((df["risk_level"] == "Low").sum()) if total else 0
    high_risk = int((df["risk_level"] == "High").sum()) if total else 0
    avg_score = round(df["overall_score"].mean(), 1) if total else 0.0

    kpi_cols = st.columns(4)
    kpis = [
        ("Startups Evaluated", f"{total}", theme["accent1"]),
        ("Low-Risk Startups", f"{low_risk}", theme["accent2"]),
        ("High-Risk Startups", f"{high_risk}", theme["accent3"]),
        ("Average Score", f"{avg_score}/100", theme["accent1"]),
    ]
    for col, (label, value, color) in zip(kpi_cols, kpis):
        with col:
            st.markdown(
                f"""<div class="kpi-card"><div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{value}</div></div>""",
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">📈 Portfolio Analytics</div>', unsafe_allow_html=True)

    plot_bg = "rgba(0,0,0,0)"
    font_color = theme["text"]

    row1_col1, row1_col2 = st.columns([1.3, 1])
    with row1_col1:
        if total:
            fig_scores = px.bar(
                df.sort_values("overall_score", ascending=True),
                x="overall_score", y="name", orientation="h",
                color="overall_score",
                color_continuous_scale=[theme["accent3"], theme["accent1"], theme["accent2"]],
                labels={"overall_score": "Overall Score", "name": "Startup"},
                title="Overall Score by Startup",
            )
            fig_scores.update_layout(
                plot_bgcolor=plot_bg, paper_bgcolor=plot_bg, font_color=font_color,
                coloraxis_showscale=False, margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_scores, use_container_width=True, key="dash_scores")

    with row1_col2:
        if total:
            risk_counts = df["risk_level"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
            fig_risk = go.Figure(data=[go.Pie(
                labels=risk_counts.index, values=risk_counts.values, hole=0.55,
                marker=dict(colors=[theme["accent2"], theme["accent1"], theme["accent3"]]),
                textinfo="label+percent",
            )])
            fig_risk.update_layout(
                title="Risk Level Distribution", plot_bgcolor=plot_bg, paper_bgcolor=plot_bg,
                font_color=font_color, margin=dict(l=10, r=10, t=50, b=10), showlegend=False,
            )
            st.plotly_chart(fig_risk, use_container_width=True, key="dash_risk")

    row2_col1, row2_col2 = st.columns([1, 1.3])
    with row2_col1:
        if total and category_cols:
            avg_by_cat = df[category_cols].mean()
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=avg_by_cat.values, theta=avg_by_cat.index, fill="toself",
                line_color=theme["accent1"], fillcolor=theme["accent1"], opacity=0.6,
            ))
            fig_radar.update_layout(
                title="Average Score by Category",
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], color=font_color),
                           angularaxis=dict(color=font_color), bgcolor=plot_bg),
                paper_bgcolor=plot_bg, font_color=font_color, showlegend=False,
                margin=dict(l=30, r=30, t=50, b=30),
            )
            st.plotly_chart(fig_radar, use_container_width=True, key="dash_radar")

    with row2_col2:
        if total:
            trend_df = df.copy()
            trend_df["date_added"] = pd.to_datetime(trend_df["date_added"], errors="coerce")
            trend_df = trend_df.sort_values("date_added")
            fig_trend = px.line(
                trend_df, x="date_added", y="overall_score", markers=True,
                title="Score Trend Over Time",
                labels={"date_added": "Date Added", "overall_score": "Overall Score"},
            )
            fig_trend.update_traces(line_color=theme["accent2"], marker=dict(size=9, color=theme["accent3"]))
            fig_trend.update_layout(
                plot_bgcolor=plot_bg, paper_bgcolor=plot_bg, font_color=font_color,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_trend, use_container_width=True, key="dash_trend")

    if total:
        with st.expander("🔍 View raw evaluation data"):
            st.dataframe(df, use_container_width=True)

    st.markdown('<div class="section-title">🧭 Platform Capabilities</div>', unsafe_allow_html=True)
    cap_col1, cap_col2, cap_col3 = st.columns(3)
    capabilities = [
        ("💰 Financial Analysis", "Analyse revenue, expenses, profitability, burn rate, cash runway and financial stability."),
        ("⚠️ Risk Assessment", "Identify financial, market, legal, technology, customer and team-related risks."),
        ("📈 Investment Insights", "Generate category scores, an overall investment score and a structured recommendation."),
    ]
    for col, (title, desc) in zip([cap_col1, cap_col2, cap_col3], capabilities):
        with col:
            st.markdown(f"""<div class="info-card"><h4>{title}</h4><p>{desc}</p></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">📄 Portfolio Report</div>', unsafe_allow_html=True)
    report_col1, report_col2 = st.columns([2, 1])
    with report_col1:
        st.write(
            "Generate a polished PDF summary of the whole portfolio — KPIs, "
            "category breakdown chart, and a per-startup scorecard table."
        )
    with report_col2:
        pdf_bytes = generate_portfolio_pdf(df, category_cols, is_demo)
        st.download_button(
            label="⬇️ Download Portfolio PDF",
            data=pdf_bytes,
            file_name=f"portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="dash_portfolio_pdf",
        )

    st.markdown(
        """<div class="footer-note">AI-Powered Startup Due Diligence Platform
        &nbsp;·&nbsp; IBM Internship Project &nbsp;·&nbsp; Group DS12</div>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# TAB: ADD STARTUP
# --------------------------------------------------------------------------- #
def render_add_startup_tab(theme: dict) -> None:
    st.title("Add Startup for Due Diligence")
    st.write(
        "Enter the available information about the startup. The platform "
        "will use this information for financial analysis, risk assessment "
        "and investment scoring."
    )
    st.info(
        "Fields marked with * are important for the initial assessment. "
        "Enter the most accurate information currently available."
    )

    with st.form("startup_due_diligence_form"):
        company_tab, team_tab, product_tab, market_tab = st.tabs(
            ["Company", "Founders & Team", "Product", "Market"]
        )
        financial_tab, customer_tab, funding_tab, legal_tab = st.tabs(
            ["Financial", "Customers", "Funding", "Legal & Risks"]
        )

        with company_tab:
            st.subheader("Company Information")
            company_col1, company_col2 = st.columns(2)
            with company_col1:
                company_name = st.text_input("Company name *", placeholder="Example: FinTrack Technologies")
                registration_number = st.text_input("Registration number", placeholder="Example: U72900XX2022PTC123456")
                founding_date = st.date_input("Founding date", value=date(2022, 1, 1), max_value=date.today())
                headquarters = st.text_input("Headquarters", placeholder="Example: Bengaluru, India")
            with company_col2:
                industry = st.text_input("Industry *", placeholder="Example: FinTech")
                startup_stage = st.selectbox(
                    "Startup stage",
                    ["Idea Stage", "Pre-Seed", "Seed", "Series A", "Series B", "Series C or Later", "Growth Stage"],
                )
                registration_status = st.selectbox(
                    "Registration status",
                    ["Registered", "Registration in Progress", "Not Registered", "Information Not Available"],
                )
                employee_count = st.number_input("Number of employees", min_value=0, value=1, step=1)
            website = st.text_input("Company website", placeholder="https://example.com")
            company_description = st.text_area(
                "Company description",
                placeholder="Briefly explain what the startup does and which customers it serves.",
                height=120,
            )

        with team_tab:
            st.subheader("Founders and Team")
            team_col1, team_col2 = st.columns(2)
            with team_col1:
                founder_count = st.number_input("Number of founders *", min_value=1, value=1, step=1)
                founder_experience_years = st.number_input("Average founder experience in years", min_value=0.0, value=0.0, step=0.5)
                previous_startup_experience = st.selectbox(
                    "Do the founders have previous startup experience?",
                    ["Yes", "No", "Partially", "Information Not Available"],
                )
                industry_experience = st.number_input("Average industry experience in years", min_value=0.0, value=0.0, step=0.5)
            with team_col2:
                technical_team_strength = st.slider("Technical team strength", 1, 10, 5, help="1 means very weak and 10 means very strong.")
                business_team_strength = st.slider("Business team strength", 1, 10, 5)
                team_stability = st.slider("Team stability", 1, 10, 5)
                key_person_dependency = st.selectbox(
                    "Key-person dependency risk",
                    ["Low", "Moderate", "High", "Information Not Available"],
                )
            founder_details = st.text_area(
                "Founder and key team details",
                placeholder="Mention founder names, education, experience, roles and relevant achievements.",
                height=150,
            )

        with product_tab:
            st.subheader("Product or Service")
            product_name = st.text_input("Product or service name", placeholder="Example: FinTrack Expense Manager")
            problem_statement = st.text_area("What problem does the product solve?", placeholder="Describe the customer problem clearly.", height=120)
            product_description = st.text_area("Product or service description", placeholder="Explain how the product solves the problem.", height=120)
            product_col1, product_col2 = st.columns(2)
            with product_col1:
                product_stage = st.selectbox(
                    "Product stage",
                    ["Concept Only", "Prototype", "Minimum Viable Product", "Early Customers", "Market Ready", "Scaling"],
                )
                working_mvp = st.selectbox("Is a working MVP available?", ["Yes", "No", "Under Development", "Information Not Available"])
                intellectual_property = st.selectbox(
                    "Intellectual property status",
                    ["Patent Granted", "Patent Filed", "Trademark Registered", "Internally Developed Technology",
                     "No Intellectual Property", "Information Not Available"],
                )
            with product_col2:
                product_uniqueness = st.slider("Product uniqueness", 1, 10, 5)
                technology_readiness = st.slider("Technology readiness", 1, 10, 5)
                product_scalability = st.slider("Product scalability", 1, 10, 5)
            unique_selling_proposition = st.text_area(
                "Unique selling proposition",
                placeholder="Explain what makes the product different from competing solutions.",
                height=100,
            )

        with market_tab:
            st.subheader("Market Opportunity")
            target_customers = st.text_area(
                "Target customers",
                placeholder="Example: Small and medium-sized Indian businesses with 10–100 employees.",
                height=100,
            )
            market_col1, market_col2 = st.columns(2)
            with market_col1:
                total_addressable_market = st.number_input("Total addressable market in ₹", min_value=0.0, value=0.0, step=100000.0)
                serviceable_available_market = st.number_input("Serviceable available market in ₹", min_value=0.0, value=0.0, step=100000.0)
                market_growth_rate = st.number_input("Estimated annual market growth rate (%)", min_value=-100.0, max_value=1000.0, value=0.0, step=1.0)
            with market_col2:
                competitor_count = st.number_input("Number of major competitors", min_value=0, value=0, step=1)
                competition_level = st.selectbox(
                    "Competition level", ["Low", "Moderate", "High", "Very High", "Information Not Available"],
                )
                competitive_advantage_strength = st.slider("Competitive advantage strength", 1, 10, 5)
            competitor_details = st.text_area("Major competitors", placeholder="Mention competitor names and important differences.", height=120)

        with financial_tab:
            st.subheader("Financial Health")
            st.caption("Enter monthly figures wherever applicable.")
            financial_col1, financial_col2 = st.columns(2)
            with financial_col1:
                monthly_revenue = st.number_input("Monthly revenue in ₹ *", min_value=0.0, value=0.0, step=10000.0)
                monthly_expenses = st.number_input("Monthly expenses in ₹ *", min_value=0.0, value=0.0, step=10000.0)
                cash_balance = st.number_input("Available cash balance in ₹ *", min_value=0.0, value=0.0, step=10000.0)
                gross_profit = st.number_input("Monthly gross profit in ₹", value=0.0, step=10000.0)
            with financial_col2:
                current_assets = st.number_input("Current assets in ₹", min_value=0.0, value=0.0, step=10000.0)
                current_liabilities = st.number_input("Current liabilities in ₹", min_value=0.0, value=0.0, step=10000.0)
                total_debt = st.number_input("Total debt in ₹", min_value=0.0, value=0.0, step=10000.0)
                total_equity = st.number_input("Total equity in ₹", min_value=0.0, value=0.0, step=10000.0)
            revenue_growth_rate = st.number_input("Revenue growth rate (%)", min_value=-100.0, max_value=1000.0, value=0.0, step=1.0)
            financial_records_available = st.selectbox(
                "Are financial records available for verification?",
                ["Audited Records Available", "Unaudited Records Available", "Partial Records Available", "No Records Available"],
            )

        with customer_tab:
            st.subheader("Customers and Growth")
            customer_col1, customer_col2 = st.columns(2)
            with customer_col1:
                total_customers = st.number_input("Total customers", min_value=0, value=0, step=1)
                new_customers_monthly = st.number_input("New customers acquired per month", min_value=0, value=0, step=1)
                customers_lost_monthly = st.number_input("Customers lost per month", min_value=0, value=0, step=1)
                customer_growth_rate = st.number_input("Customer growth rate (%)", min_value=-100.0, max_value=1000.0, value=0.0, step=1.0)
            with customer_col2:
                retention_rate = st.number_input("Customer retention rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                churn_rate = st.number_input("Customer churn rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
                customer_acquisition_cost = st.number_input("Customer acquisition cost in ₹", min_value=0.0, value=0.0, step=100.0)
                customer_lifetime_value = st.number_input("Customer lifetime value in ₹", min_value=0.0, value=0.0, step=100.0)
            major_customer_dependency = st.selectbox(
                "Dependency on one or a few major customers", ["Low", "Moderate", "High", "Information Not Available"],
            )

        with funding_tab:
            st.subheader("Funding")
            funding_col1, funding_col2 = st.columns(2)
            with funding_col1:
                previous_funding = st.number_input("Total previous funding received in ₹", min_value=0.0, value=0.0, step=100000.0)
                number_of_funding_rounds = st.number_input("Number of previous funding rounds", min_value=0, value=0, step=1)
                current_valuation = st.number_input("Current startup valuation in ₹", min_value=0.0, value=0.0, step=100000.0)
            with funding_col2:
                funding_sought = st.number_input("Funding currently sought in ₹", min_value=0.0, value=0.0, step=100000.0)
                equity_offered = st.number_input("Equity offered (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
                investor_count = st.number_input("Number of existing investors", min_value=0, value=0, step=1)
            investor_details = st.text_area("Previous or existing investor details", placeholder="Mention investor names and funding rounds.", height=100)
            use_of_funds = st.text_area(
                "Planned use of new funding",
                placeholder="Example: Product development, recruitment, marketing and geographical expansion.",
                height=120,
            )

        with legal_tab:
            st.subheader("Legal, Compliance and Risks")
            legal_col1, legal_col2 = st.columns(2)
            with legal_col1:
                required_licenses_available = st.selectbox(
                    "Are all required licences available?",
                    ["Yes", "No", "Partially", "Not Applicable", "Information Not Available"],
                )
                tax_compliance = st.selectbox(
                    "Tax compliance status", ["Compliant", "Partially Compliant", "Non-Compliant", "Information Not Available"],
                )
                founder_agreement = st.selectbox("Is a founder agreement available?", ["Yes", "No", "Information Not Available"])
                employee_agreements = st.selectbox(
                    "Are employee agreements available?", ["Yes", "No", "Partially", "Information Not Available"],
                )
            with legal_col2:
                pending_lawsuits = st.selectbox("Are there any pending lawsuits?", ["No", "Yes", "Information Not Available"])
                regulatory_issues = st.selectbox("Are there any regulatory issues?", ["No", "Yes", "Information Not Available"])
                privacy_policy_available = st.selectbox(
                    "Is a data privacy policy available?", ["Yes", "No", "Not Applicable", "Information Not Available"],
                )
                data_security_measures = st.selectbox(
                    "Data security measures", ["Strong", "Adequate", "Weak", "Not Applicable", "Information Not Available"],
                )
            legal_issue_details = st.text_area(
                "Legal or compliance issue details",
                placeholder="Describe any lawsuits, regulatory concerns, licence issues or unresolved obligations.",
                height=120,
            )

            st.markdown("#### Initial Risk Indicators")
            risk_col1, risk_col2 = st.columns(2)
            with risk_col1:
                financial_risk_indicator = st.selectbox("Financial risk", ["Low", "Moderate", "High", "Information Not Available"])
                market_risk_indicator = st.selectbox("Market risk", ["Low", "Moderate", "High", "Information Not Available"])
                technology_risk_indicator = st.selectbox("Technology risk", ["Low", "Moderate", "High", "Information Not Available"])
            with risk_col2:
                team_risk_indicator = st.selectbox("Team dependency risk", ["Low", "Moderate", "High", "Information Not Available"])
                legal_risk_indicator = st.selectbox("Legal risk", ["Low", "Moderate", "High", "Information Not Available"])
                customer_risk_indicator = st.selectbox("Customer risk", ["Low", "Moderate", "High", "Information Not Available"])

        st.divider()
        submit_button = st.form_submit_button("Save Startup Information", type="primary", use_container_width=True)

    if submit_button:
        validation_errors = validate_startup_data(
            company_name=company_name, industry=industry, founder_count=founder_count,
            monthly_revenue=monthly_revenue, monthly_expenses=monthly_expenses, cash_balance=cash_balance,
        )
        if validation_errors:
            st.error("Please correct the following problems:")
            for error in validation_errors:
                st.write(f"- {error}")
            return

        financial_metrics = calculate_all_financial_metrics(
            monthly_revenue=monthly_revenue, monthly_expenses=monthly_expenses, cash_balance=cash_balance,
            current_assets=current_assets, current_liabilities=current_liabilities,
            total_debt=total_debt, total_equity=total_equity, revenue_growth_rate=revenue_growth_rate,
            customer_lifetime_value=customer_lifetime_value, customer_acquisition_cost=customer_acquisition_cost,
            churn_rate=churn_rate, financial_records_available=financial_records_available,
        )

        startup_record = {
            "company": {
                "company_name": company_name.strip(), "registration_number": registration_number.strip(),
                "founding_date": str(founding_date), "industry": industry.strip(),
                "startup_stage": startup_stage, "registration_status": registration_status,
                "employee_count": employee_count, "headquarters": headquarters.strip(),
                "website": website.strip(), "description": company_description.strip(),
            },
            "founders_and_team": {
                "founder_count": founder_count, "founder_experience_years": founder_experience_years,
                "previous_startup_experience": previous_startup_experience,
                "industry_experience_years": industry_experience,
                "technical_team_strength": technical_team_strength, "business_team_strength": business_team_strength,
                "team_stability": team_stability, "key_person_dependency": key_person_dependency,
                "founder_details": founder_details.strip(),
            },
            "product": {
                "product_name": product_name.strip(), "problem_statement": problem_statement.strip(),
                "product_description": product_description.strip(), "product_stage": product_stage,
                "working_mvp": working_mvp, "intellectual_property": intellectual_property,
                "product_uniqueness": product_uniqueness, "technology_readiness": technology_readiness,
                "product_scalability": product_scalability,
                "unique_selling_proposition": unique_selling_proposition.strip(),
            },
            "market": {
                "target_customers": target_customers.strip(),
                "total_addressable_market": total_addressable_market,
                "serviceable_available_market": serviceable_available_market,
                "market_growth_rate": market_growth_rate, "competitor_count": competitor_count,
                "competition_level": competition_level,
                "competitive_advantage_strength": competitive_advantage_strength,
                "competitor_details": competitor_details.strip(),
            },
            "financial": {
                "monthly_revenue": monthly_revenue, "monthly_expenses": monthly_expenses,
                "cash_balance": cash_balance, "gross_profit": gross_profit,
                "current_assets": current_assets, "current_liabilities": current_liabilities,
                "total_debt": total_debt, "total_equity": total_equity,
                "revenue_growth_rate": revenue_growth_rate,
                "financial_records_available": financial_records_available,
            },
            "customers": {
                "total_customers": total_customers, "new_customers_monthly": new_customers_monthly,
                "customers_lost_monthly": customers_lost_monthly, "customer_growth_rate": customer_growth_rate,
                "retention_rate": retention_rate, "churn_rate": churn_rate,
                "customer_acquisition_cost": customer_acquisition_cost,
                "customer_lifetime_value": customer_lifetime_value,
                "major_customer_dependency": major_customer_dependency,
            },
            "funding": {
                "previous_funding": previous_funding, "number_of_funding_rounds": number_of_funding_rounds,
                "current_valuation": current_valuation, "funding_sought": funding_sought,
                "equity_offered": equity_offered, "investor_count": investor_count,
                "investor_details": investor_details.strip(), "use_of_funds": use_of_funds.strip(),
            },
            "legal_and_compliance": {
                "required_licenses_available": required_licenses_available, "tax_compliance": tax_compliance,
                "founder_agreement": founder_agreement, "employee_agreements": employee_agreements,
                "pending_lawsuits": pending_lawsuits, "regulatory_issues": regulatory_issues,
                "privacy_policy_available": privacy_policy_available,
                "data_security_measures": data_security_measures,
                "legal_issue_details": legal_issue_details.strip(),
            },
            "initial_risks": {
                "financial_risk": financial_risk_indicator, "market_risk": market_risk_indicator,
                "technology_risk": technology_risk_indicator, "team_risk": team_risk_indicator,
                "legal_risk": legal_risk_indicator, "customer_risk": customer_risk_indicator,
            },
            "calculated_metrics": financial_metrics,
        }

        scores = build_category_scores(startup_record)
        startup_record["scores"] = scores
        startup_record["meta"] = {"date_added": date.today().isoformat()}

        st.session_state.startup_records.append(startup_record)

        display_saved_record(
            startup_record, scores, theme,
            key_prefix=f"new_{len(st.session_state.startup_records)}",
        )

    st.divider()
    st.caption(f"Startups saved during this session: {len(st.session_state.startup_records)}")

    # Let the user re-open the report for any previously saved startup
    if st.session_state.startup_records:
        with st.expander("📂 View / download report for a previously saved startup"):
            names = [r["company"]["company_name"] for r in st.session_state.startup_records]
            selected = st.selectbox("Choose a startup", options=list(range(len(names))), format_func=lambda i: names[i])
            selected_record = st.session_state.startup_records[selected]
            display_saved_record(
                selected_record, selected_record["scores"], theme,
                key_prefix=f"saved_{selected}",
            )


# --------------------------------------------------------------------------- #
# SIDEBAR + MAIN LAYOUT
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("### 📊 Navigation")
    st.caption("Use the tabs at the top of the page to switch views:")
    st.markdown("- 🏠 **Dashboard** — portfolio-wide analytics\n- ➕ **Add Startup** — enter & score a new startup")
    st.divider()
    st.toggle("🌙 Dark Mode", key="dark_mode")
    st.divider()
    st.caption("IBM Internship Project · Group DS12")

THEME = get_theme_colors(st.session_state.dark_mode)
inject_css(THEME)

tab_dashboard, tab_add_startup = st.tabs(["🏠 Dashboard", "➕ Add Startup"])

with tab_dashboard:
    render_dashboard_tab(THEME)

with tab_add_startup:
    render_add_startup_tab(THEME)