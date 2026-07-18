"""
AI-Powered Startup Due Diligence Platform
------------------------------------------
Main dashboard (app.py)

Required packages (add to requirements.txt):
    streamlit
    pandas
    numpy
    plotly
    reportlab
    matplotlib

Run with:  streamlit run app.py

NOTE ON DATA INTEGRATION
------------------------
This dashboard expects other pages of the project (e.g. "Add Startup",
"Financial Analysis", "Due Diligence Scoring Engine") to store each
evaluated startup as a dict inside st.session_state["startups"], shaped like:

st.session_state["startups"] = [
    {
        "name": "Acme AI",
        "overall_score": 78,                 # 0-100
        "risk_level": "Low",                 # "Low" | "Medium" | "High"
        "recommendation": "Invest",          # short text
        "date_added": "2026-05-01",
        "category_scores": {
            "Financials": 80,
            "Team": 75,
            "Product": 82,
            "Market": 70,
            "Customers": 65,
            "Funding": 74,
            "Legal": 90,
        },
    },
    ...
]

If that key is missing/empty, this dashboard falls back to clearly-labeled
DEMO data so the UI still looks complete during a presentation/demo.
"""

from __future__ import annotations

import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

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

# Matplotlib is used ONLY to rasterize a chart for embedding in the PDF
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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

if "startups" not in st.session_state:
    st.session_state.startups = []  # populated by other pages in the real app


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


THEME = get_theme_colors(st.session_state.dark_mode)


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

        /* Hero header */
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
            font-size: 2.3rem;
            color: #FFFFFF;
            margin-bottom: 0.4rem;
        }}
        .hero p {{
            color: rgba(255,255,255,0.9);
            font-size: 1.05rem;
            max-width: 780px;
            margin: 0;
        }}

        /* KPI cards */
        .kpi-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 1.3rem 1.4rem;
            box-shadow: {t['shadow']};
            transition: transform 0.15s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
        }}
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
            color: {t['text']};
            margin-top: 0.2rem;
        }}
        .kpi-delta {{
            font-size: 0.78rem;
            font-weight: 600;
            margin-top: 0.3rem;
        }}

        /* Section headers */
        .section-title {{
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 1.35rem;
            color: {t['text']};
            margin: 1.6rem 0 0.8rem 0;
            border-left: 5px solid {t['accent1']};
            padding-left: 0.7rem;
        }}

        /* Capability / info cards */
        .info-card {{
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 16px;
            padding: 1.2rem 1.3rem;
            box-shadow: {t['shadow']};
            height: 100%;
        }}
        .info-card h4 {{
            font-family: 'Poppins', sans-serif;
            color: {t['accent1']};
            margin-bottom: 0.4rem;
        }}
        .info-card p {{
            color: {t['sub_text']};
            font-size: 0.92rem;
            line-height: 1.45;
        }}

        .demo-badge {{
            display: inline-block;
            background: {t['accent3']};
            color: white;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 0.15rem 0.6rem;
            border-radius: 20px;
            margin-left: 0.5rem;
            vertical-align: middle;
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


inject_css(THEME)


# --------------------------------------------------------------------------- #
# DATA HELPERS
# --------------------------------------------------------------------------- #
def build_demo_data() -> list[dict]:
    """Fallback demo dataset so the dashboard looks complete before real
    startups have been added through the rest of the app."""
    rng = np.random.default_rng(42)
    names = ["NovaTech", "GreenGrid", "Finlytics", "MedIQ", "UrbanFleet", "PayNest"]
    risk_levels = ["Low", "Medium", "High"]
    demo = []
    for i, name in enumerate(names):
        cat_scores = {
            "Financials": int(rng.integers(45, 95)),
            "Team": int(rng.integers(50, 95)),
            "Product": int(rng.integers(40, 95)),
            "Market": int(rng.integers(45, 90)),
            "Customers": int(rng.integers(35, 90)),
            "Funding": int(rng.integers(40, 90)),
            "Legal": int(rng.integers(55, 95)),
        }
        overall = int(np.mean(list(cat_scores.values())))
        risk = risk_levels[0] if overall >= 70 else risk_levels[1] if overall >= 50 else risk_levels[2]
        demo.append(
            {
                "name": name,
                "overall_score": overall,
                "risk_level": risk,
                "recommendation": "Invest" if overall >= 70 else "Watch" if overall >= 50 else "Avoid",
                "date_added": f"2026-0{(i % 6) + 1}-1{i}",
                "category_scores": cat_scores,
            }
        )
    return demo


def get_active_data() -> tuple[list[dict], bool]:
    """Returns (data, is_demo)."""
    real = st.session_state.get("startups", [])
    if real:
        return real, False
    return build_demo_data(), True


def to_dataframe(startups: list[dict]) -> pd.DataFrame:
    rows = []
    for s in startups:
        row = {
            "name": s.get("name", "Unknown"),
            "overall_score": s.get("overall_score", 0),
            "risk_level": s.get("risk_level", "Medium"),
            "recommendation": s.get("recommendation", "-"),
            "date_added": s.get("date_added", ""),
        }
        row.update(s.get("category_scores", {}))
        rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# SIDEBAR
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("### 📊 Navigation")

    st.page_link("app.py", label="Dashboard", icon="🏠")
    st.caption("Add the following pages inside a `pages/` folder to enable them:")
    st.markdown(
        """
        - `Add Startup`
        - `Financial Analysis`
        - `Market Analysis`
        - `Risk Assessment`
        - `ML Prediction`
        - `Report Generation`
        """
    )

    st.divider()

    st.toggle("🌙 Dark Mode", key="dark_mode")

    st.divider()
    st.caption("IBM Internship Project · Group DS12")


# Re-apply theme in case the toggle changed this run
THEME = get_theme_colors(st.session_state.dark_mode)
inject_css(THEME)

startups_data, is_demo = get_active_data()
df = to_dataframe(startups_data)

category_cols = ["Financials", "Team", "Product", "Market", "Customers", "Funding", "Legal"]
category_cols = [c for c in category_cols if c in df.columns]


# --------------------------------------------------------------------------- #
# HERO
# --------------------------------------------------------------------------- #
st.markdown(
    f"""
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
        "**demo data** to preview the dashboard. Add real startups via the "
        "**Add Startup** page to replace this automatically."
    )


# --------------------------------------------------------------------------- #
# KPI CARDS
# --------------------------------------------------------------------------- #
total = len(df)
low_risk = int((df["risk_level"] == "Low").sum()) if total else 0
high_risk = int((df["risk_level"] == "High").sum()) if total else 0
avg_score = round(df["overall_score"].mean(), 1) if total else 0.0

kpi_cols = st.columns(4)
kpis = [
    ("Startups Evaluated", f"{total}", THEME["accent1"]),
    ("Low-Risk Startups", f"{low_risk}", THEME["accent2"]),
    ("High-Risk Startups", f"{high_risk}", THEME["accent3"]),
    ("Average Score", f"{avg_score}/100", THEME["accent1"]),
]
for col, (label, value, color) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------- #
# INTERACTIVE VISUALIZATIONS
# --------------------------------------------------------------------------- #
st.markdown('<div class="section-title">📈 Portfolio Analytics</div>', unsafe_allow_html=True)

plot_bg = "rgba(0,0,0,0)"
font_color = THEME["text"]

chart_row1_col1, chart_row1_col2 = st.columns([1.3, 1])

with chart_row1_col1:
    if total:
        fig_scores = px.bar(
            df.sort_values("overall_score", ascending=True),
            x="overall_score",
            y="name",
            orientation="h",
            color="overall_score",
            color_continuous_scale=[THEME["accent3"], THEME["accent1"], THEME["accent2"]],
            labels={"overall_score": "Overall Score", "name": "Startup"},
            title="Overall Score by Startup",
        )
        fig_scores.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font_color=font_color,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_scores, use_container_width=True)

with chart_row1_col2:
    if total:
        risk_counts = df["risk_level"].value_counts().reindex(["Low", "Medium", "High"]).fillna(0)
        fig_risk = go.Figure(
            data=[
                go.Pie(
                    labels=risk_counts.index,
                    values=risk_counts.values,
                    hole=0.55,
                    marker=dict(colors=[THEME["accent2"], THEME["accent1"], THEME["accent3"]]),
                    textinfo="label+percent",
                )
            ]
        )
        fig_risk.update_layout(
            title="Risk Level Distribution",
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font_color=font_color,
            margin=dict(l=10, r=10, t=50, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_risk, use_container_width=True)

chart_row2_col1, chart_row2_col2 = st.columns([1, 1.3])

with chart_row2_col1:
    if total and category_cols:
        avg_by_cat = df[category_cols].mean()
        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=avg_by_cat.values,
                theta=avg_by_cat.index,
                fill="toself",
                line_color=THEME["accent1"],
                fillcolor=THEME["accent1"],
                opacity=0.6,
            )
        )
        fig_radar.update_layout(
            title="Average Score by Category",
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color=font_color),
                angularaxis=dict(color=font_color),
                bgcolor=plot_bg,
            ),
            paper_bgcolor=plot_bg,
            font_color=font_color,
            showlegend=False,
            margin=dict(l=30, r=30, t=50, b=30),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

with chart_row2_col2:
    if total:
        trend_df = df.copy()
        trend_df["date_added"] = pd.to_datetime(trend_df["date_added"], errors="coerce")
        trend_df = trend_df.sort_values("date_added")
        fig_trend = px.line(
            trend_df,
            x="date_added",
            y="overall_score",
            markers=True,
            title="Score Trend Over Time",
            labels={"date_added": "Date Added", "overall_score": "Overall Score"},
        )
        fig_trend.update_traces(line_color=THEME["accent2"], marker=dict(size=9, color=THEME["accent3"]))
        fig_trend.update_layout(
            plot_bgcolor=plot_bg,
            paper_bgcolor=plot_bg,
            font_color=font_color,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

if total:
    with st.expander("🔍 View raw evaluation data"):
        st.dataframe(df, use_container_width=True)


# --------------------------------------------------------------------------- #
# PLATFORM CAPABILITIES
# --------------------------------------------------------------------------- #
st.markdown('<div class="section-title">🧭 Platform Capabilities</div>', unsafe_allow_html=True)

cap_col1, cap_col2, cap_col3 = st.columns(3)
capabilities = [
    ("💰 Financial Analysis", "Analyse revenue, expenses, profitability, burn rate, cash runway and financial stability."),
    ("⚠️ Risk Assessment", "Identify financial, market, legal, technology, customer and team-related risks."),
    ("📈 Investment Insights", "Generate category scores, an overall investment score and a structured recommendation."),
]
for col, (title, desc) in zip([cap_col1, cap_col2, cap_col3], capabilities):
    with col:
        st.markdown(
            f"""
            <div class="info-card">
                <h4>{title}</h4>
                <p>{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------- #
# PDF REPORT GENERATION
# --------------------------------------------------------------------------- #
def make_matplotlib_chart(df: pd.DataFrame, category_cols: list[str]) -> io.BytesIO:
    """Render a simple bar chart with Matplotlib and return it as a PNG buffer
    for embedding inside the PDF (Plotly figures need `kaleido` to export as
    static images, so Matplotlib keeps the PDF export dependency-light)."""
    fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=150)
    if category_cols:
        avg_by_cat = df[category_cols].mean()
        ax.bar(avg_by_cat.index, avg_by_cat.values, color="#5B4EF5")
        ax.set_ylabel("Average Score")
        ax.set_title("Average Score by Category")
        ax.set_ylim(0, 100)
        plt.xticks(rotation=20, ha="right")
    else:
        ax.text(0.5, 0.5, "No category data available", ha="center", va="center")
        ax.axis("off")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_report(df: pd.DataFrame, category_cols: list[str], is_demo: bool) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#5B4EF5")
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"], fontSize=10, textColor=colors.grey
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#1A1D29")
    )

    elements = []

    elements.append(Paragraph("AI-Powered Startup Due Diligence Report", title_style))
    elements.append(
        Paragraph(
            f"Generated on {datetime.now().strftime('%d %b %Y, %H:%M')}"
            + (" &nbsp;|&nbsp; <font color='#F5537C'>DEMO DATA</font>" if is_demo else ""),
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 0.6 * cm))

    # --- Summary KPIs table ---
    total = len(df)
    low_risk = int((df["risk_level"] == "Low").sum()) if total else 0
    high_risk = int((df["risk_level"] == "High").sum()) if total else 0
    avg_score = round(df["overall_score"].mean(), 1) if total else 0.0

    elements.append(Paragraph("Portfolio Summary", heading_style))
    summary_data = [
        ["Startups Evaluated", "Low-Risk", "High-Risk", "Average Score"],
        [str(total), str(low_risk), str(high_risk), f"{avg_score}/100"],
    ]
    summary_table = Table(summary_data, colWidths=[4 * cm] * 4)
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5B4EF5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6E8F0")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F7F8FC")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.6 * cm))

    # --- Category chart ---
    elements.append(Paragraph("Average Score by Category", heading_style))
    chart_buf = make_matplotlib_chart(df, category_cols)
    elements.append(RLImage(chart_buf, width=15 * cm, height=8.2 * cm))
    elements.append(Spacer(1, 0.6 * cm))

    # --- Per-startup table ---
    elements.append(Paragraph("Startup-Level Detail", heading_style))
    table_cols = ["name", "overall_score", "risk_level", "recommendation"]
    table_cols = [c for c in table_cols if c in df.columns]
    header = ["Startup", "Score", "Risk", "Recommendation"][: len(table_cols)]
    detail_data = [header] + df[table_cols].astype(str).values.tolist()

    detail_table = Table(detail_data, colWidths=[4.5 * cm, 3 * cm, 3 * cm, 4 * cm])
    detail_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A1D29")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E6E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F8FC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(detail_table)
    elements.append(Spacer(1, 0.8 * cm))

    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    elements.append(
        Paragraph(
            "Generated automatically by the AI-Powered Startup Due Diligence Platform. "
            "Scores are model-based estimates and should be reviewed alongside independent due diligence.",
            footer_style,
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


st.markdown('<div class="section-title">📄 Report Generation</div>', unsafe_allow_html=True)

report_col1, report_col2 = st.columns([2, 1])
with report_col1:
    st.write(
        "Generate a polished PDF summary of the current portfolio — KPIs, "
        "category breakdown chart, and a per-startup scorecard table — "
        "ready to share with mentors, evaluators or investors."
    )
with report_col2:
    pdf_bytes = generate_pdf_report(df, category_cols, is_demo)
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name=f"due_diligence_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


# --------------------------------------------------------------------------- #
# FOOTER
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <div class="footer-note">
        AI-Powered Startup Due Diligence Platform &nbsp;·&nbsp; IBM Internship Project &nbsp;·&nbsp; Group DS12
    </div>
    """,
    unsafe_allow_html=True,
)