"""Reusable Streamlit UI components and chart builders."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

PALETTE = {
    "bg": "#0E1117",
    "panel": "#161b22",
    "border": "#2a313c",
    "text": "#E6EDF3",
    "muted": "#8b949e",
    "accent": "#FF6B35",        # HelloFresh-ish orange
    "accent_soft": "#FFB28A",
    "green": "#3FB950",
    "yellow": "#F1C40F",
    "red": "#F85149",
    "blue": "#58A6FF",
}

RISK_COLOR = {
    "Low": PALETTE["green"],
    "Medium": PALETTE["yellow"],
    "High": PALETTE["accent"],
    "Critical": PALETTE["red"],
}


# ---------- CSS / global styling ----------

CUSTOM_CSS = f"""
<style>
:root {{
  --rc-bg: {PALETTE['bg']};
  --rc-panel: {PALETTE['panel']};
  --rc-border: {PALETTE['border']};
  --rc-text: {PALETTE['text']};
  --rc-muted: {PALETTE['muted']};
  --rc-accent: {PALETTE['accent']};
}}
.main .block-container {{ padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1280px; }}
h1, h2, h3, h4 {{ color: var(--rc-text); letter-spacing: -0.01em; }}
.rc-eyebrow {{
  text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.72rem;
  color: var(--rc-muted); font-weight: 600;
}}
.rc-headline {{
  font-size: 1.55rem; font-weight: 700; color: var(--rc-text); margin: 0.2rem 0 0.4rem;
  line-height: 1.25;
}}
.rc-card {{
  background: var(--rc-panel); border: 1px solid var(--rc-border);
  border-radius: 14px; padding: 1.1rem 1.25rem; margin-bottom: 0.75rem;
}}
.rc-card-accent {{ border-left: 4px solid var(--rc-accent); }}
.rc-kpi-label {{ font-size: 0.78rem; color: var(--rc-muted); text-transform: uppercase; letter-spacing: 0.08em; }}
.rc-kpi-value {{ font-size: 1.7rem; font-weight: 700; color: var(--rc-text); margin-top: 0.2rem; }}
.rc-kpi-sub {{ font-size: 0.78rem; color: var(--rc-muted); margin-top: 0.2rem; }}
.rc-badge {{
  display: inline-block; padding: 3px 10px; border-radius: 999px;
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.04em;
}}
.rc-badge-low {{ background: rgba(63,185,80,0.15); color: {PALETTE['green']}; }}
.rc-badge-medium {{ background: rgba(241,196,15,0.15); color: {PALETTE['yellow']}; }}
.rc-badge-high {{ background: rgba(255,107,53,0.18); color: {PALETTE['accent']}; }}
.rc-badge-critical {{ background: rgba(248,81,73,0.18); color: {PALETTE['red']}; }}
.rc-delta-up {{ color: {PALETTE['red']}; font-weight: 600; }}
.rc-delta-down {{ color: {PALETTE['green']}; font-weight: 600; }}
.rc-delta-flat {{ color: var(--rc-muted); }}
.rc-section-title {{
  font-size: 1.05rem; font-weight: 700; color: var(--rc-text);
  margin: 0.6rem 0 0.5rem;
}}
.rc-list {{ margin: 0; padding-left: 1.1rem; color: var(--rc-text); }}
.rc-list li {{ margin-bottom: 0.35rem; line-height: 1.45; }}
.rc-pill {{
  display: inline-block; padding: 4px 10px; border-radius: 6px;
  font-size: 0.72rem; font-weight: 600; background: rgba(255,107,53,0.13);
  color: var(--rc-accent); margin-right: 6px;
}}
.rc-pill-blue {{ background: rgba(88,166,255,0.15); color: {PALETTE['blue']}; }}
.rc-pill-muted {{ background: rgba(139,148,158,0.15); color: var(--rc-muted); }}
.rc-divider {{ border-top: 1px solid var(--rc-border); margin: 1.5rem 0 1rem; }}
.rc-intervention {{
  background: var(--rc-panel); border: 1px solid var(--rc-border);
  border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;
}}
.rc-intervention-title {{ font-size: 1.05rem; font-weight: 700; color: var(--rc-text); margin-bottom: 0.25rem; }}
.rc-intervention-issue {{ font-size: 0.82rem; color: var(--rc-muted); margin-bottom: 0.55rem; }}
.rc-intervention-body {{ font-size: 0.92rem; color: var(--rc-text); line-height: 1.5; }}
.rc-meta-row {{ display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 0.5rem; font-size: 0.78rem; }}
.rc-meta-row strong {{ color: var(--rc-text); }}
.rc-footer-note {{ font-size: 0.78rem; color: var(--rc-muted); margin-top: 0.3rem; }}
</style>
"""


# ---------- atoms ----------

def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def risk_badge(level: str) -> str:
    klass = f"rc-badge rc-badge-{level.lower()}"
    return f'<span class="{klass}">{level.upper()}</span>'


def pill(text: str, kind: str = "default") -> str:
    klass = "rc-pill"
    if kind == "blue":
        klass += " rc-pill-blue"
    elif kind == "muted":
        klass += " rc-pill-muted"
    return f'<span class="{klass}">{text}</span>'


def kpi_card(label: str, value: str, sub: str | None = None, accent: bool = False) -> str:
    accent_class = " rc-card-accent" if accent else ""
    sub_html = f'<div class="rc-kpi-sub">{sub}</div>' if sub else ""
    return f"""
    <div class="rc-card{accent_class}">
      <div class="rc-kpi-label">{label}</div>
      <div class="rc-kpi-value">{value}</div>
      {sub_html}
    </div>
    """


def fmt_usd(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:,.0f}"


def fmt_pct_delta(pct: float) -> str:
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct*100:.0f}%"


# ---------- charts ----------

def risk_gauge(risk_score: float, risk_label: str) -> go.Figure:
    color = RISK_COLOR.get(risk_label, PALETTE["accent"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        number={"font": {"color": PALETTE["text"], "size": 36}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": PALETTE["muted"], "tickfont": {"color": PALETTE["muted"]}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": PALETTE["bg"],
            "borderwidth": 0,
            "steps": [
                {"range": [0, 35], "color": "rgba(63,185,80,0.18)"},
                {"range": [35, 55], "color": "rgba(241,196,15,0.18)"},
                {"range": [55, 75], "color": "rgba(255,107,53,0.20)"},
                {"range": [75, 100], "color": "rgba(248,81,73,0.22)"},
            ],
            "threshold": {
                "line": {"color": PALETTE["text"], "width": 3},
                "thickness": 0.75,
                "value": risk_score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=PALETTE["panel"],
        plot_bgcolor=PALETTE["panel"],
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(color=PALETTE["text"]),
    )
    return fig


def driver_bar(drivers) -> go.Figure:
    categories = [d.category for d in drivers]
    impact = [d.retention_impact_score for d in drivers]
    tickets = [d.ticket_count_current_week for d in drivers]
    colors = [
        RISK_COLOR["Critical"] if s >= 60
        else RISK_COLOR["High"] if s >= 40
        else RISK_COLOR["Medium"] if s >= 20
        else RISK_COLOR["Low"]
        for s in impact
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=impact, y=categories, orientation="h",
        marker=dict(color=colors),
        text=[f"impact {i:.0f} · {t} tickets" for i, t in zip(impact, tickets)],
        textposition="outside",
        textfont=dict(color=PALETTE["text"]),
        hovertemplate="<b>%{y}</b><br>Retention impact: %{x:.1f}<br>Tickets this week: %{customdata}<extra></extra>",
        customdata=tickets,
    ))
    fig.update_layout(
        paper_bgcolor=PALETTE["panel"],
        plot_bgcolor=PALETTE["panel"],
        height=max(280, 38 * len(categories) + 80),
        margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(
            title="Retention impact score (0–100)",
            color=PALETTE["muted"],
            gridcolor=PALETTE["border"],
            zerolinecolor=PALETTE["border"],
            range=[0, max(impact) * 1.25 if impact else 100],
        ),
        yaxis=dict(
            color=PALETTE["text"],
            categoryorder="total ascending",
            tickfont=dict(size=12),
        ),
        showlegend=False,
        font=dict(color=PALETTE["text"]),
    )
    return fig


def wow_delta_chart(deltas) -> go.Figure:
    metrics = [d.metric for d in deltas]
    pcts = [d.pct_change * 100 for d in deltas]
    colors = [
        RISK_COLOR["Critical"] if d.is_concerning and abs(d.pct_change) > 0.25
        else RISK_COLOR["High"] if d.is_concerning
        else RISK_COLOR["Low"]
        for d in deltas
    ]
    fig = go.Figure(go.Bar(
        x=pcts, y=metrics, orientation="h",
        marker=dict(color=colors),
        text=[f"{p:+.0f}%" for p in pcts],
        textposition="outside",
        textfont=dict(color=PALETTE["text"]),
        hovertemplate="<b>%{y}</b><br>WoW: %{x:+.1f}%<extra></extra>",
    ))
    max_abs = max([abs(p) for p in pcts] + [10])
    fig.update_layout(
        paper_bgcolor=PALETTE["panel"],
        plot_bgcolor=PALETTE["panel"],
        height=max(260, 38 * len(metrics) + 60),
        margin=dict(l=10, r=80, t=10, b=10),
        xaxis=dict(
            title="Week-over-week change (%)",
            color=PALETTE["muted"],
            gridcolor=PALETTE["border"],
            zerolinecolor=PALETTE["muted"],
            range=[-max_abs * 1.25, max_abs * 1.25],
        ),
        yaxis=dict(color=PALETTE["text"], categoryorder="total ascending"),
        showlegend=False,
        font=dict(color=PALETTE["text"]),
    )
    return fig


def churn_risk_distribution(customer_risk: pd.DataFrame) -> go.Figure:
    counts = customer_risk["risk_tier"].value_counts().reindex(
        ["Low", "Medium", "High", "Critical"], fill_value=0
    )
    fig = go.Figure(go.Bar(
        x=counts.index, y=counts.values,
        marker=dict(color=[RISK_COLOR[t] for t in counts.index]),
        text=[f"{int(v):,}" for v in counts.values],
        textposition="outside",
        textfont=dict(color=PALETTE["text"]),
        hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=PALETTE["panel"],
        plot_bgcolor=PALETTE["panel"],
        height=260,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(color=PALETTE["text"], title=""),
        yaxis=dict(color=PALETTE["muted"], title="Customers", gridcolor=PALETTE["border"]),
        showlegend=False,
        font=dict(color=PALETTE["text"]),
    )
    return fig


def ticket_trend_chart(tickets: pd.DataFrame) -> go.Figure:
    """Stacked weekly trend by category for top categories."""
    top_cats = (
        tickets["category"].value_counts().head(6).index.tolist()
    )
    pivot = (
        tickets[tickets["category"].isin(top_cats)]
        .groupby(["week_offset", "category"])
        .size()
        .reset_index(name="count")
    )
    weeks = sorted(pivot["week_offset"].unique())
    week_labels = [f"W-{int(tickets['week_offset'].max() - w)}" for w in weeks]
    fig = go.Figure()
    color_cycle = [
        PALETTE["accent"], PALETTE["blue"], PALETTE["yellow"],
        PALETTE["green"], PALETTE["red"], PALETTE["accent_soft"],
    ]
    for i, cat in enumerate(top_cats):
        ydata = []
        for w in weeks:
            row = pivot[(pivot["week_offset"] == w) & (pivot["category"] == cat)]
            ydata.append(int(row["count"].iloc[0]) if len(row) else 0)
        fig.add_trace(go.Scatter(
            x=week_labels, y=ydata, mode="lines+markers",
            name=cat, line=dict(width=2.5, color=color_cycle[i % len(color_cycle)]),
            marker=dict(size=7),
        ))
    fig.update_layout(
        paper_bgcolor=PALETTE["panel"],
        plot_bgcolor=PALETTE["panel"],
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(color=PALETTE["muted"], gridcolor=PALETTE["border"]),
        yaxis=dict(color=PALETTE["muted"], gridcolor=PALETTE["border"], title="Tickets"),
        legend=dict(font=dict(color=PALETTE["text"], size=11), bgcolor="rgba(0,0,0,0)"),
        font=dict(color=PALETTE["text"]),
    )
    return fig
