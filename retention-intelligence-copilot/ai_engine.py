"""AI synthesis layer. Uses Anthropic Claude when available; falls back to deterministic
analyst-style synthesis built from the analytics bundle so the app is fully functional offline."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from .analytics import AnalyticsBundle, DriverInsight, WowDelta

try:
    from anthropic import Anthropic
    _ANTHROPIC_AVAILABLE = True
except Exception:
    _ANTHROPIC_AVAILABLE = False


MODEL_ID = "claude-opus-4-7"


@dataclass
class InterventionRecommendation:
    title: str
    operational_issue: str
    recommendation: str
    urgency: str  # "Immediate", "This week", "This month"
    expected_retention_impact: str
    operational_tradeoffs: str
    estimated_roi_usd: float
    owner_function: str  # "CX Ops", "Logistics", "Finance", "Product"


@dataclass
class ExecutiveBriefing:
    headline: str
    summary_paragraph: str
    top_risks: list[str]
    top_operational_failures: list[str]
    strategic_recommendations: list[str]


@dataclass
class AIInsights:
    briefing: ExecutiveBriefing
    interventions: list[InterventionRecommendation]
    root_cause_narratives: dict[str, str]  # category -> narrative
    used_llm: bool


# ---------- public entry point ----------

def generate_insights(analytics: AnalyticsBundle, use_llm: bool = True) -> AIInsights:
    if use_llm and _ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _generate_with_claude(analytics)
        except Exception as e:
            print(f"[ai_engine] Claude call failed, falling back: {e}")
    return _generate_fallback(analytics)


# ---------- Claude path ----------

def _generate_with_claude(analytics: AnalyticsBundle) -> AIInsights:
    client = Anthropic()
    context = _build_context_payload(analytics)
    system = _system_prompt()
    user_msg = _user_prompt(context)

    resp = client.messages.create(
        model=MODEL_ID,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = resp.content[0].text
    data = _extract_json(text)
    return _insights_from_json(data, used_llm=True)


def _system_prompt() -> str:
    return (
        "You are a senior retention strategy advisor and Chief of Staff to the COO at a large "
        "subscription meal-kit company. You translate fragmented operational signals into "
        "executive intelligence: causal reasoning, prioritized interventions, and financial impact. "
        "You are concise, decisive, and operationally specific. You never produce generic AI fluff. "
        "Every recommendation must name a function (CX Ops, Logistics, Finance, Product), an "
        "expected retention impact, and tradeoffs. You speak in the voice of someone briefing "
        "the executive team. Output ONLY valid JSON matching the requested schema."
    )


def _user_prompt(context: dict[str, Any]) -> str:
    schema = {
        "briefing": {
            "headline": "one-line headline, max 120 chars, declarative",
            "summary_paragraph": "3-4 sentences, executive briefing tone, names specific operational issues",
            "top_risks": ["3-5 short bullet strings, each naming a specific risk"],
            "top_operational_failures": ["3-5 short bullet strings, each naming a specific failure with implication"],
            "strategic_recommendations": ["3-5 bullets, each a concrete decision the leadership team should make this week"],
        },
        "interventions": [
            {
                "title": "short action title",
                "operational_issue": "the underlying issue this addresses",
                "recommendation": "specific intervention, 1-2 sentences, operationally concrete",
                "urgency": "Immediate | This week | This month",
                "expected_retention_impact": "quantified or directional, e.g. 'reduces refund-driven churn ~20%'",
                "operational_tradeoffs": "what this costs / risks operationally",
                "estimated_roi_usd": 12345.0,
                "owner_function": "CX Ops | Logistics | Finance | Product"
            }
        ],
        "root_cause_narratives": {
            "<category name>": "2-3 sentences explaining the probable operational root cause and why it is driving retention risk"
        }
    }
    return (
        "Below is the current week's operational analytics for a meal-kit subscription business. "
        "Synthesize it into executive intelligence.\n\n"
        f"## ANALYTICS DATA\n```json\n{json.dumps(context, indent=2, default=str)}\n```\n\n"
        "## YOUR TASK\n"
        "1. Produce an executive briefing (headline, summary, top risks, top failures, strategic recommendations).\n"
        "2. Produce 5-7 prioritized intervention recommendations. Order by urgency * expected impact.\n"
        "3. For the top 3-5 ticket categories (by retention impact score), produce a root cause narrative.\n\n"
        "Constraints:\n"
        "- Be specific: name categories, customer segments, dollar amounts from the data when relevant.\n"
        "- Reference the week-over-week deltas explicitly when they are material.\n"
        "- Tie at least 2 interventions to the financial impact estimate.\n"
        "- Do NOT recommend generic actions (\"improve communication\", \"build dashboards\").\n\n"
        "Return ONLY valid JSON matching this schema (no preamble, no markdown fences):\n"
        f"```json\n{json.dumps(schema, indent=2)}\n```"
    )


def _build_context_payload(analytics: AnalyticsBundle) -> dict[str, Any]:
    return {
        "summary_stats": analytics.summary_stats,
        "overall_churn_risk": analytics.overall_churn_risk,
        "overall_risk_score": analytics.overall_risk_score,
        "top_drivers": [asdict(d) for d in analytics.drivers[:8]],
        "risk_segments": [asdict(s) for s in analytics.risk_segments],
        "week_over_week_deltas": [asdict(d) for d in analytics.wow_deltas],
        "financial_impact": asdict(analytics.financial) if analytics.financial else {},
    }


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        # Strip a fenced block if Claude added one despite instructions
        text = text.split("```", 2)
        text = text[1] if len(text) > 1 else text[0]
        if text.startswith("json"):
            text = text[len("json"):].strip()
        text = text.rsplit("```", 1)[0] if "```" in text else text
    return json.loads(text)


def _insights_from_json(data: dict[str, Any], used_llm: bool) -> AIInsights:
    b = data.get("briefing", {})
    briefing = ExecutiveBriefing(
        headline=b.get("headline", ""),
        summary_paragraph=b.get("summary_paragraph", ""),
        top_risks=b.get("top_risks", []),
        top_operational_failures=b.get("top_operational_failures", []),
        strategic_recommendations=b.get("strategic_recommendations", []),
    )
    interventions = [
        InterventionRecommendation(
            title=i.get("title", ""),
            operational_issue=i.get("operational_issue", ""),
            recommendation=i.get("recommendation", ""),
            urgency=i.get("urgency", "This week"),
            expected_retention_impact=i.get("expected_retention_impact", ""),
            operational_tradeoffs=i.get("operational_tradeoffs", ""),
            estimated_roi_usd=float(i.get("estimated_roi_usd", 0) or 0),
            owner_function=i.get("owner_function", "CX Ops"),
        )
        for i in data.get("interventions", [])
    ]
    root_causes = data.get("root_cause_narratives", {}) or {}
    return AIInsights(
        briefing=briefing,
        interventions=interventions,
        root_cause_narratives=root_causes,
        used_llm=used_llm,
    )


# ---------- Fallback path (deterministic, analyst-style) ----------

def _generate_fallback(analytics: AnalyticsBundle) -> AIInsights:
    drivers = analytics.drivers
    top = drivers[:5] if drivers else []
    deltas = analytics.wow_deltas
    fin = analytics.financial

    # Find the most concerning WoW deltas
    concerning = sorted(
        [d for d in deltas if d.is_concerning],
        key=lambda d: abs(d.pct_change),
        reverse=True,
    )

    # Headline anchors on top driver + biggest WoW shift
    top_cat = top[0].category if top else "operational issues"
    biggest_delta = concerning[0] if concerning else None
    headline_parts = [f"{top_cat} is the dominant retention threat this week"]
    if biggest_delta:
        headline_parts.append(
            f"{biggest_delta.metric.lower()} {biggest_delta.direction} {abs(biggest_delta.pct_change)*100:.0f}% WoW"
        )
    headline = "; ".join(headline_parts) + "."

    summary = _fallback_summary(top, concerning, analytics)

    top_risks = [_risk_line(d) for d in top[:4]]
    top_failures = [_failure_line(d) for d in top[:4]]
    strategic_recs = _fallback_strategic_recs(top, concerning, analytics)

    interventions = _fallback_interventions(top, analytics)

    root_causes = {d.category: _fallback_root_cause(d) for d in top[:5]}

    briefing = ExecutiveBriefing(
        headline=headline,
        summary_paragraph=summary,
        top_risks=top_risks,
        top_operational_failures=top_failures,
        strategic_recommendations=strategic_recs,
    )

    return AIInsights(
        briefing=briefing,
        interventions=interventions,
        root_cause_narratives=root_causes,
        used_llm=False,
    )


def _fallback_summary(top: list[DriverInsight], concerning: list[WowDelta], analytics: AnalyticsBundle) -> str:
    parts = []
    if top:
        d = top[0]
        wow_str = f", up {d.wow_change_pct*100:.0f}% week-over-week" if d.wow_change_pct > 0.05 else ""
        parts.append(
            f"{d.category} is the strongest near-term churn driver{wow_str}, "
            f"with {d.ticket_count_current_week} tickets, {d.pct_with_cancel_intent:.0f}% carrying explicit "
            f"cancellation intent, and average resolution running at {d.avg_resolution_hours:.0f} hours."
        )
    if len(top) > 1:
        parts.append(
            f"Secondary pressure is coming from {top[1].category} and {top[2].category if len(top) > 2 else 'related'} "
            f"complaints, which compound for customers already showing dissatisfaction."
        )
    if analytics.financial:
        parts.append(
            f"Exposure: {_fmt_usd(analytics.financial.arr_at_risk_usd)} ARR is at risk across "
            f"{analytics.financial.customers_at_risk:,} customers; a well-targeted intervention "
            f"can recover approximately {_fmt_usd(analytics.financial.potential_savings_if_intervened_usd)}."
        )
    if concerning:
        d = concerning[0]
        parts.append(
            f"The most concerning shift: {d.metric.lower()} moved from {d.previous:.1f} to {d.current:.1f} "
            f"({d.pct_change*100:+.0f}%). Leadership should treat this as the priority signal this week."
        )
    return " ".join(parts)


def _risk_line(d: DriverInsight) -> str:
    pieces = [f"{d.category}: {d.ticket_count_current_week} tickets this week"]
    if d.wow_change_pct > 0.10:
        pieces.append(f"+{d.wow_change_pct*100:.0f}% WoW")
    if d.pct_with_cancel_intent > 15:
        pieces.append(f"{d.pct_with_cancel_intent:.0f}% with cancellation intent")
    return " — ".join(pieces)


def _failure_line(d: DriverInsight) -> str:
    if d.category == "Refund delay":
        return f"Refund SLA broken — average decision time {d.avg_resolution_hours:.0f}h on tickets carrying cancellation intent."
    if d.category == "Food safety concern":
        return f"Food safety complaints elevated ({d.ticket_count_current_week} this week) — sentiment at {d.avg_sentiment:.2f}, brand-trust impact."
    if d.category == "Cold chain failure":
        return f"Cold chain breaks in {d.ticket_count_current_week} shipments — direct quality risk and refund pressure."
    if d.category == "Customer service unresponsive":
        return f"Support backlog visible: customers reporting no reply ({d.ticket_count_current_week} cases)."
    return f"{d.category}: {d.ticket_count_current_week} tickets, severity-high in {d.severity_high_pct:.0f}% of cases."


def _fallback_strategic_recs(top, concerning, analytics: AnalyticsBundle) -> list[str]:
    recs = []
    for d in top[:3]:
        if d.category == "Refund delay":
            recs.append(
                "Authorize CX Ops to issue auto-credits for refund tickets aged >7 days while approval is pending; "
                "kills cancellation intent before it triggers."
            )
        elif d.category == "Food safety concern":
            recs.append(
                "Stand up a same-day senior-CX response queue for any food safety ticket; "
                "trigger supplier QA review for any category with >3 complaints in a week."
            )
        elif d.category == "Cold chain failure":
            recs.append(
                "Reroute affected metro deliveries to the premium cold-chain carrier for the next 2 weeks "
                "and audit insulation packs by warehouse."
            )
        elif d.category == "Customer service unresponsive":
            recs.append(
                "Reassign agent capacity to the unresolved backlog and set a 24h max-response SLA enforced by routing."
            )
        else:
            recs.append(
                f"Assign single-owner ticket continuity for {d.category} cases this week to prevent fragmentation."
            )
    if analytics.financial and analytics.financial.arr_at_risk_usd > 0:
        recs.append(
            f"Approve a {_fmt_usd(min(analytics.financial.potential_savings_if_intervened_usd * 0.1, 50000))} "
            f"retention save-budget for the high-risk customer segment this week."
        )
    return recs[:5]


def _fallback_interventions(top: list[DriverInsight], analytics: AnalyticsBundle) -> list[InterventionRecommendation]:
    interventions: list[InterventionRecommendation] = []

    for d in top[:6]:
        if d.category == "Refund delay":
            interventions.append(InterventionRecommendation(
                title="Escalate aged refund tickets to priority queue",
                operational_issue="Refund decisions averaging 14+ days while customers are signaling cancellation",
                recommendation=(
                    "Auto-route any refund ticket open >24h to a manager-approval queue with a 24h decision SLA. "
                    "For tickets aged >7 days, issue a goodwill credit immediately and resolve the refund in parallel."
                ),
                urgency="Immediate",
                expected_retention_impact=(
                    f"Estimated 18-25% reduction in churn for the {d.pct_with_cancel_intent:.0f}% of refund tickets "
                    "carrying cancellation intent."
                ),
                operational_tradeoffs=(
                    "Requires manager bandwidth for ~80 escalations/week and ~$8-12K/wk in goodwill credits; "
                    "offsets are far larger downstream."
                ),
                estimated_roi_usd=_roi_for(d, analytics),
                owner_function="CX Ops",
            ))
        elif d.category == "Food safety concern":
            interventions.append(InterventionRecommendation(
                title="Same-day senior-CX response for food safety tickets",
                operational_issue="Food safety complaints damage brand trust and have outsized churn impact",
                recommendation=(
                    "Route all food safety tickets to a dedicated senior CX pod with a 4h response SLA and "
                    "automatic replacement-box dispatch. Trigger a supplier QA review for any SKU with 3+ complaints/wk."
                ),
                urgency="Immediate",
                expected_retention_impact="Reduces long-term churn risk among affected cohort by ~30%; protects brand NPS.",
                operational_tradeoffs="Costs ~$5K/wk in replacement boxes and dedicated agent time; brand-trust upside is non-quantifiable.",
                estimated_roi_usd=_roi_for(d, analytics) * 0.7,
                owner_function="CX Ops",
            ))
        elif d.category == "Cold chain failure":
            interventions.append(InterventionRecommendation(
                title="Proactive replacement shipment + carrier review",
                operational_issue="Repeat cold chain breaks signal warehouse or carrier degradation",
                recommendation=(
                    "Auto-dispatch a free replacement box for any customer with a cold-chain incident in the last 14 days "
                    "without waiting for them to contact support. Open a carrier-performance review for affected metros."
                ),
                urgency="This week",
                expected_retention_impact="Cuts secondary churn from repeat-incident customers by ~22%.",
                operational_tradeoffs="Replacement cost ~$30/box; reduces inbound ticket load by an estimated 18%.",
                estimated_roi_usd=_roi_for(d, analytics) * 0.6,
                owner_function="Logistics",
            ))
        elif d.category == "Customer service unresponsive":
            interventions.append(InterventionRecommendation(
                title="Single-owner continuity model for at-risk tickets",
                operational_issue="Customers re-explaining issues to multiple agents — fragmentation drives churn",
                recommendation=(
                    "For any ticket flagged high-severity or carrying cancellation intent, assign a single CX owner "
                    "end-to-end. Surface this in the agent UI so handoffs are explicit and tracked."
                ),
                urgency="This week",
                expected_retention_impact="Improves resolution NPS and reduces churn intent ~15% in affected cohort.",
                operational_tradeoffs="Slight reduction in agent utilization; offset by lower repeat-contact rate.",
                estimated_roi_usd=_roi_for(d, analytics) * 0.5,
                owner_function="CX Ops",
            ))
        elif d.category == "Billing error":
            interventions.append(InterventionRecommendation(
                title="Billing reconciliation sweep + auto-credit",
                operational_issue="Double-charges and incorrect billing drive immediate cancellation intent",
                recommendation=(
                    "Run a billing reconciliation sweep against the last 30 days. Auto-credit any flagged accounts "
                    "before they contact support and notify them with a transparent explanation."
                ),
                urgency="This week",
                expected_retention_impact="Eliminates billing-driven cancellations entirely for the swept window.",
                operational_tradeoffs="Finance team needs ~2 days of reconciliation work; credit cost capped at audit total.",
                estimated_roi_usd=_roi_for(d, analytics) * 0.55,
                owner_function="Finance",
            ))
        elif d.category == "Subscription pause failed":
            interventions.append(InterventionRecommendation(
                title="Fix pause-flow regression + apologize-and-credit",
                operational_issue="Customers being charged when they asked to pause — high trust violation",
                recommendation=(
                    "Product to ship hotfix for the pause flow this week. CX to proactively credit and apologize "
                    "to every affected account in the last 30 days."
                ),
                urgency="Immediate",
                expected_retention_impact="Eliminates a churn-trigger that has near-100% intent conversion.",
                operational_tradeoffs="Engineering time + ~$3K in credits; trivial vs. cohort LTV.",
                estimated_roi_usd=_roi_for(d, analytics) * 0.4,
                owner_function="Product",
            ))
        else:
            interventions.append(InterventionRecommendation(
                title=f"Targeted intervention for {d.category}",
                operational_issue=d.category,
                recommendation=(
                    f"Spin up a focused response squad for {d.category} this week with explicit ownership "
                    "and a measurable resolution-time SLA."
                ),
                urgency="This week",
                expected_retention_impact="Directional reduction in churn intent within the affected cohort.",
                operational_tradeoffs="Modest reallocation of CX capacity.",
                estimated_roi_usd=_roi_for(d, analytics) * 0.35,
                owner_function="CX Ops",
            ))

    interventions.sort(key=lambda i: (-_urgency_weight(i.urgency), -i.estimated_roi_usd))
    return interventions


def _urgency_weight(u: str) -> int:
    return {"Immediate": 3, "This week": 2, "This month": 1}.get(u, 1)


def _roi_for(d: DriverInsight, analytics: AnalyticsBundle) -> float:
    if not analytics.financial or analytics.financial.arr_at_risk_usd == 0:
        return d.ticket_count_current_week * 250.0
    # Weight by share of impact across drivers.
    total_impact = sum(x.retention_impact_score for x in analytics.drivers) or 1
    share = d.retention_impact_score / total_impact
    return round(analytics.financial.potential_savings_if_intervened_usd * share, 2)


def _fallback_root_cause(d: DriverInsight) -> str:
    base = {
        "Refund delay": (
            "Refund decision time has stretched well beyond the customer's tolerance window. "
            "The pattern of high cancellation intent in these tickets indicates customers are "
            "treating the refund delay as a final trust violation. Likely root cause: a backlog "
            "in the approval queue colliding with rising ticket volume."
        ),
        "Food safety concern": (
            "Food safety complaints are concentrated tightly, suggesting a supplier or warehouse "
            "QA issue rather than dispersed handling problems. The sentiment floor on these tickets "
            "is the lowest in the system — these customers rarely recover without high-touch outreach."
        ),
        "Cold chain failure": (
            "Cold chain breaks are clustered geographically, pointing to a specific carrier or hub "
            "operating outside spec. The compounding effect with delivery delays suggests last-mile "
            "rerouting may be exceeding insulation lifetime."
        ),
        "Customer service unresponsive": (
            "Response time has degraded as ticket volume grew without a proportional capacity increase. "
            "Customers re-explaining issues to multiple agents is the strongest predictor of cancellation "
            "in this cohort."
        ),
        "Billing error": (
            "Billing errors carry near-immediate churn risk because they violate the most basic customer "
            "trust contract. The error pattern suggests either a payment-system regression or a charge-on-pause bug."
        ),
        "Subscription pause failed": (
            "A failure in the pause flow is converting an explicit retention action into a churn trigger. "
            "This is almost certainly a product regression and needs engineering attention this week."
        ),
    }
    return base.get(
        d.category,
        f"{d.category} volume and severity have risen this week without a corresponding operational response. "
        "Pattern suggests a single underlying cause worth a focused root-cause review.",
    )


def _fmt_usd(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    if amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:.0f}"
