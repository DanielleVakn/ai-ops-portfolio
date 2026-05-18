"""Retention Intelligence Copilot — Streamlit MVP."""
from __future__ import annotations

import io
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.ai_engine import AIInsights, generate_insights
from src.analytics import AnalyticsBundle, compute
from src.data_generator import DatasetBundle, generate_bundle
from src.ui_components import (
    PALETTE, churn_risk_distribution, driver_bar, fmt_pct_delta, fmt_usd,
    inject_css, kpi_card, pill, risk_badge, risk_gauge, ticket_trend_chart,
    wow_delta_chart,
)

load_dotenv()

st.set_page_config(
    page_title="Retention Intelligence Copilot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- caching ----------

@st.cache_data(show_spinner=False)
def _load_default_bundle() -> DatasetBundle:
    return generate_bundle()


@st.cache_data(show_spinner=False)
def _compute_analytics(_bundle: DatasetBundle) -> AnalyticsBundle:
    return compute(_bundle)


@st.cache_data(show_spinner=False)
def _ai_insights(_analytics: AnalyticsBundle, use_llm: bool, cache_key: str) -> AIInsights:
    # cache_key lets the user force regeneration via sidebar
    return generate_insights(_analytics, use_llm=use_llm)


# ---------- sidebar ----------

def _sidebar() -> dict:
    with st.sidebar:
        st.markdown("### Retention Intelligence Copilot")
        st.caption("Executive operations platform")
        st.divider()

        st.markdown("**Data source**")
        uploaded = st.file_uploader(
            "Upload operational CSV (optional)",
            type=["csv"],
            help="Upload a support_tickets.csv to override the demo data. Otherwise realistic mock data is generated.",
        )

        st.markdown("**AI synthesis**")
        has_key = bool(os.getenv("ANTHROPIC_API_KEY"))
        if has_key:
            st.success("Anthropic API detected")
        else:
            st.info("No ANTHROPIC_API_KEY found — using deterministic analyst-style synthesis.")
        use_llm = st.toggle("Use Claude for synthesis", value=has_key, disabled=not has_key)

        regen = st.button("Re-run AI synthesis", use_container_width=True)

        st.divider()
        st.markdown("**Industry context**")
        st.caption("This MVP is configured for a subscription meal-kit logistics business.")

    cache_key = datetime.utcnow().isoformat() if regen else "stable"
    return {"uploaded": uploaded, "use_llm": use_llm, "cache_key": cache_key}


# ---------- sections ----------

def _section_header(eyebrow: str, title: str, helper: str | None = None) -> None:
    st.markdown(f'<div class="rc-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rc-headline">{title}</div>', unsafe_allow_html=True)
    if helper:
        st.caption(helper)


def _hero(analytics: AnalyticsBundle, insights: AIInsights) -> None:
    st.markdown('<div class="rc-eyebrow">Operational briefing · ' +
                datetime.utcnow().strftime("%B %d, %Y") + '</div>',
                unsafe_allow_html=True)
    st.markdown(f'<h1 style="margin:0.2rem 0 0.6rem;letter-spacing:-0.02em;">Retention Intelligence Copilot</h1>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div style="color:{PALETTE["muted"]};margin-bottom:1.1rem;">'
        f'AI-powered executive command center for churn reduction and operational intervention.'
        f' &nbsp;·&nbsp; Synthesis source: '
        f'<strong>{"Claude" if insights.used_llm else "deterministic analyst engine"}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _section_kpis(analytics: AnalyticsBundle) -> None:
    s = analytics.summary_stats
    f = analytics.financial
    cols = st.columns(5)
    cols[0].markdown(kpi_card(
        "Overall churn risk",
        f'{analytics.overall_risk_score:.0f} <span style="font-size:1rem;color:{PALETTE["muted"]};">/ 100</span>',
        f"Status: {risk_badge(analytics.overall_churn_risk)}",
        accent=True,
    ), unsafe_allow_html=True)
    cols[1].markdown(kpi_card(
        "ARR at risk",
        fmt_usd(f.arr_at_risk_usd),
        f"{f.customers_at_risk:,} customers · avg CLV {fmt_usd(f.avg_clv_at_risk_usd)}",
    ), unsafe_allow_html=True)
    cols[2].markdown(kpi_card(
        "Tickets this week",
        f"{s['tickets_this_week']:,}",
        f"{s['open_tickets']:,} open · sentiment {s['avg_sentiment_this_week']:+.2f}",
    ), unsafe_allow_html=True)
    cols[3].markdown(kpi_card(
        "Cancellations this week",
        f"{s['cancellations_this_week']:,}",
        f"Refund backlog: {s['refund_backlog_count']:,} aged tickets",
    ), unsafe_allow_html=True)
    cols[4].markdown(kpi_card(
        "Potential save",
        fmt_usd(f.potential_savings_if_intervened_usd),
        "If recommended interventions are executed",
    ), unsafe_allow_html=True)


def _section_executive_summary(insights: AIInsights) -> None:
    _section_header("01 · Executive summary", insights.briefing.headline or "This week's executive briefing")
    b = insights.briefing
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown(
            f'<div class="rc-card rc-card-accent">'
            f'<div class="rc-eyebrow">Chief of Staff briefing</div>'
            f'<p style="font-size:1.0rem;line-height:1.55;margin:0.5rem 0 0.2rem;color:{PALETTE["text"]};">'
            f'{b.summary_paragraph}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with right:
        rec_html = "".join(f"<li>{r}</li>" for r in b.strategic_recommendations)
        st.markdown(
            f'<div class="rc-card">'
            f'<div class="rc-section-title">Strategic recommendations</div>'
            f'<ul class="rc-list">{rec_html}</ul>'
            f'</div>',
            unsafe_allow_html=True,
        )

    left, right = st.columns(2)
    with left:
        items = "".join(f"<li>{r}</li>" for r in b.top_risks)
        st.markdown(
            f'<div class="rc-card"><div class="rc-section-title">Top retention risks</div>'
            f'<ul class="rc-list">{items}</ul></div>',
            unsafe_allow_html=True,
        )
    with right:
        items = "".join(f"<li>{r}</li>" for r in b.top_operational_failures)
        st.markdown(
            f'<div class="rc-card"><div class="rc-section-title">Top operational failures</div>'
            f'<ul class="rc-list">{items}</ul></div>',
            unsafe_allow_html=True,
        )


def _section_risk_radar(analytics: AnalyticsBundle) -> None:
    _section_header(
        "02 · Churn risk radar",
        "Where the churn pressure is concentrated",
        "Real-time view across customer segments and operational triggers.",
    )
    left, right = st.columns([1, 1.6])
    with left:
        st.markdown(
            f'<div class="rc-card"><div class="rc-section-title">Overall churn risk</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(risk_gauge(analytics.overall_risk_score, analytics.overall_churn_risk), use_container_width=True)
        st.markdown(
            f'<div style="text-align:center;margin-top:-0.5rem;">'
            f'{risk_badge(analytics.overall_churn_risk)}'
            f'<div class="rc-footer-note" style="margin-top:0.3rem;">Composite of driver impact, WoW shifts, and customer-level risk.</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f'<div class="rc-card"><div class="rc-section-title">Customer churn risk distribution</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(churn_risk_distribution(analytics.customer_risk_table), use_container_width=True)
        crit = (analytics.customer_risk_table["risk_tier"] == "Critical").sum()
        high = (analytics.customer_risk_table["risk_tier"] == "High").sum()
        st.markdown(
            f'<div class="rc-footer-note">'
            f'<strong style="color:{PALETTE["text"]};">{crit:,}</strong> customers in <strong>Critical</strong>, '
            f'<strong style="color:{PALETTE["text"]};">{high:,}</strong> in <strong>High</strong> — these are the immediate intervention targets.'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def _section_root_cause(analytics: AnalyticsBundle, insights: AIInsights, bundle: DatasetBundle) -> None:
    _section_header(
        "03 · Operational root cause intelligence",
        "What is breaking, and why",
        "Pattern detection across support tickets, severity, sentiment, and resolution time.",
    )
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown(
            f'<div class="rc-card"><div class="rc-section-title">Retention impact by operational issue</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(driver_bar(analytics.drivers[:8]), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown(
            f'<div class="rc-card"><div class="rc-section-title">4-week ticket trend</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(ticket_trend_chart(bundle.tickets), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="rc-section-title">Root cause narratives</div>', unsafe_allow_html=True)
    for d in analytics.drivers[:5]:
        narrative = insights.root_cause_narratives.get(d.category, "")
        delta_html = ""
        if d.wow_change_pct > 0.02:
            delta_html = f' <span class="rc-delta-up">↑ {d.wow_change_pct*100:.0f}% WoW</span>'
        elif d.wow_change_pct < -0.02:
            delta_html = f' <span class="rc-delta-down">↓ {abs(d.wow_change_pct)*100:.0f}% WoW</span>'
        with st.expander(
            f"  {d.category}  ·  impact {d.retention_impact_score:.0f}  ·  "
            f"{d.ticket_count_current_week} tickets",
            expanded=False,
        ):
            cols = st.columns(4)
            cols[0].metric("Tickets this week", d.ticket_count_current_week, delta=f"{d.ticket_count_current_week - d.ticket_count_prev_week:+d} vs prev")
            cols[1].metric("Avg resolution (h)", f"{d.avg_resolution_hours:.0f}")
            cols[2].metric("Cancel intent", f"{d.pct_with_cancel_intent:.0f}%")
            cols[3].metric("High severity", f"{d.severity_high_pct:.0f}%")
            st.markdown(
                f'<div style="margin-top:0.7rem;line-height:1.55;color:{PALETTE["text"]};">'
                f'<strong>Probable root cause:</strong> {narrative or "Pattern under investigation."}'
                f'{delta_html}</div>',
                unsafe_allow_html=True,
            )


def _section_interventions(insights: AIInsights) -> None:
    _section_header(
        "04 · AI intervention recommendations",
        "Prioritized actions for this week",
        "Ranked by urgency and estimated retention impact. Each tied to an operational owner.",
    )
    urgency_styles = {
        "Immediate": ("rc-badge rc-badge-critical", "🔴"),
        "This week": ("rc-badge rc-badge-high", "🟠"),
        "This month": ("rc-badge rc-badge-medium", "🟡"),
    }
    for i, rec in enumerate(insights.interventions, start=1):
        klass, _ = urgency_styles.get(rec.urgency, ("rc-badge rc-badge-medium", "🟡"))
        st.markdown(
            f'''
            <div class="rc-intervention">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
                <div style="flex:1;">
                  <div class="rc-intervention-title">{i}. {rec.title}</div>
                  <div class="rc-intervention-issue">Addresses: {rec.operational_issue}</div>
                </div>
                <div style="text-align:right;white-space:nowrap;">
                  <span class="{klass}">{rec.urgency.upper()}</span>
                  <div style="font-size:0.78rem;color:{PALETTE["muted"]};margin-top:0.3rem;">Owner: <strong style="color:{PALETTE["text"]};">{rec.owner_function}</strong></div>
                </div>
              </div>
              <div class="rc-intervention-body">{rec.recommendation}</div>
              <div class="rc-meta-row">
                {pill("Impact: " + rec.expected_retention_impact, "blue")}
                {pill("Est. ROI: " + fmt_usd(rec.estimated_roi_usd))}
                {pill("Tradeoffs: " + rec.operational_tradeoffs, "muted")}
              </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )


def _section_financial(analytics: AnalyticsBundle) -> None:
    _section_header(
        "05 · Financial impact estimation",
        "Revenue exposure and recovery opportunity",
        "Translating operational risk into business consequences.",
    )
    f = analytics.financial
    cols = st.columns(4)
    cols[0].markdown(kpi_card("ARR at risk", fmt_usd(f.arr_at_risk_usd), "Annualized exposure from at-risk cohort"), unsafe_allow_html=True)
    cols[1].markdown(kpi_card("Monthly revenue at risk", fmt_usd(f.monthly_revenue_at_risk_usd), "Near-term exposure window"), unsafe_allow_html=True)
    cols[2].markdown(kpi_card("Customers at risk", f"{f.customers_at_risk:,}", f"Avg LTV: {fmt_usd(f.avg_clv_at_risk_usd)}"), unsafe_allow_html=True)
    cols[3].markdown(kpi_card("Recoverable with interventions", fmt_usd(f.potential_savings_if_intervened_usd), "Assumes ~35% save rate on at-risk ARR", accent=True), unsafe_allow_html=True)

    # Intervention simulator
    st.markdown('<div class="rc-card">', unsafe_allow_html=True)
    st.markdown('<div class="rc-section-title">Intervention simulator</div>', unsafe_allow_html=True)
    st.caption("Tune assumptions to see recoverable revenue under different scenarios.")
    sim_cols = st.columns(3)
    save_rate = sim_cols[0].slider("Save rate on intervention (%)", 5, 80, 35, help="What % of at-risk ARR can be recovered with the recommended actions.")
    refund_sla = sim_cols[1].slider("Refund SLA improvement (%)", 0, 90, 50, help="How much faster refund decisions become.")
    cx_capacity = sim_cols[2].slider("Added CX capacity (%)", 0, 100, 25, help="Headcount or routing capacity uplift in the CX queue.")

    base = f.arr_at_risk_usd
    # Simple compounding model for the simulator
    refund_lift = base * 0.30 * (refund_sla / 100)  # refund pathway is ~30% of exposure
    cx_lift = base * 0.20 * (cx_capacity / 100)     # CX continuity is ~20% of exposure
    save_lift = base * (save_rate / 100)
    total_recoverable = min(base, save_lift + 0.5 * refund_lift + 0.5 * cx_lift)

    st.markdown(
        f'<div style="display:flex;gap:2rem;margin-top:0.7rem;flex-wrap:wrap;">'
        f'<div><div class="rc-kpi-label">Recoverable ARR (modeled)</div>'
        f'<div class="rc-kpi-value" style="color:{PALETTE["accent"]};">{fmt_usd(total_recoverable)}</div></div>'
        f'<div><div class="rc-kpi-label">Net retained customers</div>'
        f'<div class="rc-kpi-value">{int(f.customers_at_risk * (total_recoverable / max(base,1))):,}</div></div>'
        f'<div><div class="rc-kpi-label">vs. baseline projection</div>'
        f'<div class="rc-kpi-value" style="color:{PALETTE["green"]};">+{fmt_usd(total_recoverable - f.potential_savings_if_intervened_usd)}</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def _section_high_risk_segments(analytics: AnalyticsBundle) -> None:
    _section_header(
        "06 · High-risk customer segments",
        "Cohorts to prioritize for retention outreach",
    )
    for seg in analytics.risk_segments:
        drivers_html = " ".join(pill(d, "blue") for d in seg.primary_drivers) if seg.primary_drivers else ""
        st.markdown(
            f'''
            <div class="rc-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
                <div style="flex:1;">
                  <div class="rc-intervention-title">{seg.segment_name}</div>
                  <div class="rc-intervention-issue">{seg.customer_count:,} customers · avg churn probability {seg.avg_churn_probability*100:.0f}% · revenue at risk {fmt_usd(seg.revenue_at_risk_usd)}</div>
                </div>
                <div>
                  {risk_badge("Critical" if seg.avg_churn_probability >= 0.5 else "High" if seg.avg_churn_probability >= 0.35 else "Medium")}
                </div>
              </div>
              <div style="margin-top:0.6rem;color:{PALETTE["text"]};line-height:1.5;">
                <strong>Recovery strategy:</strong> {seg.recommended_strategy}
              </div>
              <div style="margin-top:0.55rem;">{drivers_html}</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

    with st.expander("View top 25 individual at-risk customers"):
        df = analytics.customer_risk_table.head(25)[[
            "customer_id", "plan", "city", "tenure_bucket",
            "ticket_count", "cancel_intent_count", "delivery_issues",
            "avg_refund_days", "churn_probability", "revenue_at_risk_usd",
            "risk_tier",
        ]].copy()
        df.columns = [
            "Customer", "Plan", "City", "Tenure",
            "Tickets", "Cancel-intent", "Delivery issues",
            "Refund days", "Churn prob", "Rev at risk",
            "Tier",
        ]
        df["Churn prob"] = (df["Churn prob"] * 100).round(0).astype(int).astype(str) + "%"
        df["Rev at risk"] = df["Rev at risk"].apply(fmt_usd)
        df["Refund days"] = df["Refund days"].round(1)
        st.dataframe(df, use_container_width=True, hide_index=True)


def _section_what_changed(analytics: AnalyticsBundle) -> None:
    _section_header(
        "07 · What changed this week",
        "Week-over-week shifts that matter",
    )
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(f'<div class="rc-card"><div class="rc-section-title">WoW change by metric</div>', unsafe_allow_html=True)
        st.plotly_chart(wow_delta_chart(analytics.wow_deltas), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown(f'<div class="rc-card"><div class="rc-section-title">Narrative deltas</div>', unsafe_allow_html=True)
        for d in sorted(analytics.wow_deltas, key=lambda x: abs(x.pct_change), reverse=True):
            arrow = "↑" if d.direction == "up" else "↓" if d.direction == "down" else "→"
            klass = "rc-delta-up" if d.is_concerning and d.direction != "flat" else (
                "rc-delta-down" if not d.is_concerning and d.direction != "flat" else "rc-delta-flat"
            )
            st.markdown(
                f'<div style="padding:0.45rem 0;border-bottom:1px solid {PALETTE["border"]};">'
                f'<div style="color:{PALETTE["text"]};font-weight:500;">{d.metric}</div>'
                f'<div style="font-size:0.85rem;margin-top:0.15rem;">'
                f'<span class="{klass}">{arrow} {fmt_pct_delta(d.pct_change)}</span>'
                f'<span style="color:{PALETTE["muted"]};"> &nbsp;·&nbsp; {d.previous:.1f} → {d.current:.1f}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)


# ---------- export ----------

def _build_briefing_markdown(analytics: AnalyticsBundle, insights: AIInsights) -> str:
    b = insights.briefing
    f = analytics.financial
    lines = []
    lines.append(f"# Retention Intelligence Copilot — Executive Briefing")
    lines.append(f"_{datetime.utcnow().strftime('%B %d, %Y')}_\n")
    lines.append(f"## Headline\n{b.headline}\n")
    lines.append(f"## Executive Summary\n{b.summary_paragraph}\n")
    lines.append(f"## Overall Churn Risk\n**{analytics.overall_churn_risk}** ({analytics.overall_risk_score:.0f}/100)\n")
    lines.append("## Financial Exposure")
    lines.append(f"- ARR at risk: **{fmt_usd(f.arr_at_risk_usd)}**")
    lines.append(f"- Customers at risk: **{f.customers_at_risk:,}** (avg CLV {fmt_usd(f.avg_clv_at_risk_usd)})")
    lines.append(f"- Recoverable with interventions: **{fmt_usd(f.potential_savings_if_intervened_usd)}**\n")
    lines.append("## Top Retention Risks")
    for r in b.top_risks:
        lines.append(f"- {r}")
    lines.append("\n## Top Operational Failures")
    for r in b.top_operational_failures:
        lines.append(f"- {r}")
    lines.append("\n## Strategic Recommendations")
    for r in b.strategic_recommendations:
        lines.append(f"- {r}")
    lines.append("\n## Prioritized Interventions")
    for i, rec in enumerate(insights.interventions, 1):
        lines.append(f"\n### {i}. {rec.title}  ·  _{rec.urgency}_  ·  Owner: {rec.owner_function}")
        lines.append(f"**Addresses:** {rec.operational_issue}")
        lines.append(f"\n{rec.recommendation}")
        lines.append(f"\n- **Expected impact:** {rec.expected_retention_impact}")
        lines.append(f"- **Estimated ROI:** {fmt_usd(rec.estimated_roi_usd)}")
        lines.append(f"- **Tradeoffs:** {rec.operational_tradeoffs}")
    lines.append("\n## High-Risk Customer Segments")
    for seg in analytics.risk_segments:
        lines.append(f"\n### {seg.segment_name}")
        lines.append(f"- Customers: {seg.customer_count:,}")
        lines.append(f"- Avg churn probability: {seg.avg_churn_probability*100:.0f}%")
        lines.append(f"- Revenue at risk: {fmt_usd(seg.revenue_at_risk_usd)}")
        lines.append(f"- Strategy: {seg.recommended_strategy}")
    lines.append("\n## What Changed Week-over-Week")
    for d in analytics.wow_deltas:
        arrow = "↑" if d.direction == "up" else "↓" if d.direction == "down" else "→"
        lines.append(f"- {d.metric}: {arrow} {fmt_pct_delta(d.pct_change)} ({d.previous:.1f} → {d.current:.1f})")
    return "\n".join(lines)


def _section_export(analytics: AnalyticsBundle, insights: AIInsights, bundle: DatasetBundle) -> None:
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_header("Export", "Briefing & data downloads")
    cols = st.columns(3)

    md = _build_briefing_markdown(analytics, insights)
    cols[0].download_button(
        "Download executive briefing (.md)",
        data=md,
        file_name=f"retention_briefing_{datetime.utcnow().strftime('%Y%m%d')}.md",
        mime="text/markdown",
        use_container_width=True,
    )

    customer_csv = analytics.customer_risk_table.to_csv(index=False)
    cols[1].download_button(
        "Download at-risk customers (.csv)",
        data=customer_csv,
        file_name="at_risk_customers.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # Bundled raw operational data as Excel
    buf = io.BytesIO()
    try:
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            for name, df in bundle.all_frames().items():
                df.to_excel(writer, sheet_name=name[:31], index=False)
        cols[2].download_button(
            "Download raw operational data (.xlsx)",
            data=buf.getvalue(),
            file_name="operational_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except ModuleNotFoundError:
        # openpyxl not installed — fall back to a multi-sheet CSV zip
        cols[2].caption("Install `openpyxl` to enable Excel export.")


# ---------- main ----------

def main() -> None:
    inject_css()
    settings = _sidebar()

    if settings["uploaded"] is not None:
        try:
            uploaded_df = pd.read_csv(settings["uploaded"])
            st.sidebar.success(f"Loaded {len(uploaded_df):,} rows from upload.")
            st.sidebar.caption(
                "Note: uploaded CSVs are previewed only in this MVP. "
                "Analytics still derive from the bundled operational set."
            )
            with st.sidebar.expander("Preview uploaded data"):
                st.dataframe(uploaded_df.head(20))
        except Exception as e:
            st.sidebar.error(f"Could not parse upload: {e}")

    with st.spinner("Generating operational signals…"):
        bundle = _load_default_bundle()
    with st.spinner("Computing churn risk and operational analytics…"):
        analytics = _compute_analytics(bundle)
    with st.spinner("Synthesizing executive intelligence…"):
        insights = _ai_insights(analytics, use_llm=settings["use_llm"], cache_key=settings["cache_key"])

    _hero(analytics, insights)
    _section_kpis(analytics)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_executive_summary(insights)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_risk_radar(analytics)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_root_cause(analytics, insights, bundle)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_interventions(insights)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_financial(analytics)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_high_risk_segments(analytics)
    st.markdown('<div class="rc-divider"></div>', unsafe_allow_html=True)
    _section_what_changed(analytics)
    _section_export(analytics, insights, bundle)


if __name__ == "__main__":
    main()
