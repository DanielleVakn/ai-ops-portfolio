"""Pandas analytics: churn drivers, risk segments, WoW deltas, financial exposure."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from .data_generator import DatasetBundle


# ---------- helpers ----------

def _safe_pct_change(curr: float, prev: float) -> float:
    if prev == 0:
        return 0.0 if curr == 0 else 1.0
    return (curr - prev) / prev


# ---------- top-level dataclasses ----------

@dataclass
class DriverInsight:
    category: str
    ticket_count_current_week: int
    ticket_count_prev_week: int
    wow_change_pct: float
    avg_resolution_hours: float
    pct_with_cancel_intent: float
    avg_sentiment: float
    severity_high_pct: float
    retention_impact_score: float  # 0..100


@dataclass
class RiskSegment:
    segment_name: str
    customer_count: int
    avg_churn_probability: float
    revenue_at_risk_usd: float
    primary_drivers: list[str]
    recommended_strategy: str


@dataclass
class WowDelta:
    metric: str
    current: float
    previous: float
    pct_change: float
    direction: str  # "up", "down", "flat"
    is_concerning: bool


@dataclass
class FinancialImpact:
    arr_at_risk_usd: float
    monthly_revenue_at_risk_usd: float
    customers_at_risk: int
    avg_clv_at_risk_usd: float
    potential_savings_if_intervened_usd: float


@dataclass
class AnalyticsBundle:
    drivers: list[DriverInsight] = field(default_factory=list)
    risk_segments: list[RiskSegment] = field(default_factory=list)
    wow_deltas: list[WowDelta] = field(default_factory=list)
    financial: FinancialImpact | None = None
    summary_stats: dict[str, Any] = field(default_factory=dict)
    customer_risk_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    overall_churn_risk: str = "Medium"
    overall_risk_score: float = 0.0


# ---------- computation ----------

def compute(bundle: DatasetBundle) -> AnalyticsBundle:
    tickets = bundle.tickets
    deliveries = bundle.deliveries
    refunds = bundle.refunds
    cancellations = bundle.cancellations
    customers = bundle.customers

    weeks = tickets["week_offset"].max()  # current week index
    prev_week = weeks - 1

    drivers = _compute_drivers(tickets, weeks, prev_week)
    customer_risk = _compute_customer_risk(tickets, deliveries, refunds, customers)
    risk_segments = _compute_risk_segments(customer_risk, customers)
    wow_deltas = _compute_wow_deltas(tickets, deliveries, refunds, cancellations, weeks, prev_week)
    financial = _compute_financial_impact(customer_risk, customers, cancellations)
    summary_stats = _summary_stats(tickets, deliveries, refunds, cancellations, customers, weeks)

    risk_score = _overall_risk_score(drivers, wow_deltas, customer_risk)
    risk_label = (
        "Critical" if risk_score >= 75
        else "High" if risk_score >= 55
        else "Medium" if risk_score >= 35
        else "Low"
    )

    return AnalyticsBundle(
        drivers=drivers,
        risk_segments=risk_segments,
        wow_deltas=wow_deltas,
        financial=financial,
        summary_stats=summary_stats,
        customer_risk_table=customer_risk,
        overall_churn_risk=risk_label,
        overall_risk_score=risk_score,
    )


def _compute_drivers(tickets: pd.DataFrame, current_week: int, prev_week: int) -> list[DriverInsight]:
    drivers = []
    curr = tickets[tickets["week_offset"] == current_week]
    prev = tickets[tickets["week_offset"] == prev_week]

    for category in tickets["category"].unique():
        c = curr[curr["category"] == category]
        p = prev[prev["category"] == category]
        if len(c) == 0 and len(p) == 0:
            continue
        avg_res = float(c["resolution_hours"].dropna().mean()) if len(c["resolution_hours"].dropna()) else 0.0
        cancel_pct = float(c["cancellation_intent"].mean() * 100) if len(c) else 0.0
        sentiment = float(c["sentiment_score"].mean()) if len(c) else 0.0
        severity_high_pct = float(((c["severity"].isin(["High", "Critical"])).mean()) * 100) if len(c) else 0.0
        wow = _safe_pct_change(len(c), len(p))

        # Retention impact: weighted combination of volume, intent, sentiment, severity, resolution time.
        impact = (
            (len(c) / max(1, len(curr))) * 30  # share of weekly volume
            + cancel_pct * 0.4
            + max(0, -sentiment) * 25
            + severity_high_pct * 0.25
            + min(avg_res / 60, 1.0) * 15
        )
        impact = float(np.clip(impact, 0, 100))

        drivers.append(
            DriverInsight(
                category=category,
                ticket_count_current_week=int(len(c)),
                ticket_count_prev_week=int(len(p)),
                wow_change_pct=wow,
                avg_resolution_hours=round(avg_res, 1),
                pct_with_cancel_intent=round(cancel_pct, 1),
                avg_sentiment=round(sentiment, 2),
                severity_high_pct=round(severity_high_pct, 1),
                retention_impact_score=round(impact, 1),
            )
        )

    drivers.sort(key=lambda d: d.retention_impact_score, reverse=True)
    return drivers


def _compute_customer_risk(
    tickets: pd.DataFrame,
    deliveries: pd.DataFrame,
    refunds: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    """Per-customer churn probability based on tickets, delivery issues, refund delays, cancel intent."""
    # Aggregate signals per customer.
    tix = tickets.groupby("customer_id").agg(
        ticket_count=("ticket_id", "count"),
        avg_sentiment=("sentiment_score", "mean"),
        cancel_intent_count=("cancellation_intent", "sum"),
        severity_high=("severity", lambda s: (s.isin(["High", "Critical"])).sum()),
        latest_ticket_category=("category", "last"),
    )

    deliv = deliveries.groupby("customer_id").agg(
        delivery_issues=("issue", lambda x: x.notna().sum()),
        on_time_rate=("on_time", "mean"),
    )

    ref = refunds.groupby("customer_id").agg(
        refund_count=("refund_id", "count"),
        avg_refund_days=("days_to_decision", "mean"),
    )

    df = customers.set_index("customer_id").join(tix, how="left").join(deliv, how="left").join(ref, how="left")
    df = df.fillna({
        "ticket_count": 0, "avg_sentiment": 0, "cancel_intent_count": 0,
        "severity_high": 0, "delivery_issues": 0, "on_time_rate": 1.0,
        "refund_count": 0, "avg_refund_days": 0, "latest_ticket_category": "",
    })

    # Churn probability model (rule-based but defensible).
    churn = (
        np.clip(df["ticket_count"] * 0.07, 0, 0.35)
        + np.clip(df["cancel_intent_count"] * 0.20, 0, 0.40)
        + np.clip(df["severity_high"] * 0.06, 0, 0.20)
        + np.clip((1 - df["on_time_rate"]) * 0.30, 0, 0.20)
        + np.clip(df["delivery_issues"] * 0.04, 0, 0.20)
        + np.clip((df["avg_refund_days"] - 7).clip(lower=0) * 0.012, 0, 0.20)
        + np.clip((-df["avg_sentiment"]).clip(lower=0) * 0.25, 0, 0.25)
    )
    df["churn_probability"] = np.clip(churn, 0.02, 0.95).round(3)
    df["revenue_at_risk_usd"] = (df["weekly_value_usd"] * 52 * df["churn_probability"]).round(2)

    # Risk tier
    df["risk_tier"] = pd.cut(
        df["churn_probability"],
        bins=[0, 0.15, 0.35, 0.6, 1.01],
        labels=["Low", "Medium", "High", "Critical"],
    )

    df = df.reset_index()
    return df.sort_values("churn_probability", ascending=False)


def _compute_risk_segments(customer_risk: pd.DataFrame, customers: pd.DataFrame) -> list[RiskSegment]:
    segments: list[RiskSegment] = []

    # 1. Long-tenure users hit by first major issue (2+ yr, churn>0.35)
    s = customer_risk[(customer_risk["tenure_bucket"] == "2+ yr") & (customer_risk["churn_probability"] >= 0.35)]
    if len(s):
        segments.append(RiskSegment(
            segment_name="Long-tenure loyalists with first major operational failure",
            customer_count=len(s),
            avg_churn_probability=float(s["churn_probability"].mean()),
            revenue_at_risk_usd=float(s["revenue_at_risk_usd"].sum()),
            primary_drivers=_top_drivers_from_segment(s),
            recommended_strategy="High-touch personal outreach from senior CX, proactive credit + handwritten apology. These customers churn rarely — losing them is permanent and damages word-of-mouth.",
        ))

    # 2. Customers with refund delays
    s = customer_risk[customer_risk["avg_refund_days"] >= 10]
    if len(s):
        segments.append(RiskSegment(
            segment_name="Customers stuck in refund processing backlog",
            customer_count=len(s),
            avg_churn_probability=float(s["churn_probability"].mean()),
            revenue_at_risk_usd=float(s["revenue_at_risk_usd"].sum()),
            primary_drivers=["Refund delay", "Customer service unresponsive"],
            recommended_strategy="Same-day refund approval for tickets aged >10 days; auto-credit while ticket is in flight to neutralize cancellation intent.",
        ))

    # 3. Customers with explicit cancellation language
    s = customer_risk[customer_risk["cancel_intent_count"] >= 1]
    if len(s):
        segments.append(RiskSegment(
            segment_name="Customers with explicit cancellation intent in support tickets",
            customer_count=len(s),
            avg_churn_probability=float(s["churn_probability"].mean()),
            revenue_at_risk_usd=float(s["revenue_at_risk_usd"].sum()),
            primary_drivers=_top_drivers_from_segment(s),
            recommended_strategy="Flag in retention queue; manager-level callback within 24h with targeted save offer (skip-week + 30% off next box).",
        ))

    # 4. Repeated delivery failures
    s = customer_risk[customer_risk["delivery_issues"] >= 2]
    if len(s):
        segments.append(RiskSegment(
            segment_name="Customers with 2+ delivery incidents in the last 4 weeks",
            customer_count=len(s),
            avg_churn_probability=float(s["churn_probability"].mean()),
            revenue_at_risk_usd=float(s["revenue_at_risk_usd"].sum()),
            primary_drivers=["Late delivery", "Cold chain failure", "Damaged packaging"],
            recommended_strategy="Move to premium carrier route; proactive replacement shipment + 1-week credit before next incident.",
        ))

    # 5. New customers (0-3mo) with any major issue
    s = customer_risk[(customer_risk["tenure_bucket"] == "0-3 mo") & (customer_risk["churn_probability"] >= 0.3)]
    if len(s):
        segments.append(RiskSegment(
            segment_name="New customers (under 3 months) experiencing early-life failure",
            customer_count=len(s),
            avg_churn_probability=float(s["churn_probability"].mean()),
            revenue_at_risk_usd=float(s["revenue_at_risk_usd"].sum()),
            primary_drivers=_top_drivers_from_segment(s),
            recommended_strategy="Onboarding recovery flow: dedicated CX owner for first 30 days post-incident, free replacement box, lifetime value rescue is highest here.",
        ))

    return segments


def _top_drivers_from_segment(seg: pd.DataFrame) -> list[str]:
    if "latest_ticket_category" not in seg.columns:
        return []
    cats = seg["latest_ticket_category"]
    cats = cats[cats != ""]
    return cats.value_counts().head(3).index.tolist()


def _compute_wow_deltas(
    tickets: pd.DataFrame,
    deliveries: pd.DataFrame,
    refunds: pd.DataFrame,
    cancellations: pd.DataFrame,
    current_week: int,
    prev_week: int,
) -> list[WowDelta]:
    deltas: list[WowDelta] = []

    def _delta(name: str, curr: float, prev: float, concerning_if_up: bool = True) -> WowDelta:
        pct = _safe_pct_change(curr, prev)
        direction = "up" if pct > 0.02 else "down" if pct < -0.02 else "flat"
        is_concerning = (direction == "up" and concerning_if_up) or (direction == "down" and not concerning_if_up)
        return WowDelta(
            metric=name, current=curr, previous=prev,
            pct_change=pct, direction=direction, is_concerning=is_concerning,
        )

    # Ticket volume
    deltas.append(_delta(
        "Total support tickets",
        len(tickets[tickets["week_offset"] == current_week]),
        len(tickets[tickets["week_offset"] == prev_week]),
    ))

    # Cancellation intent rate
    curr_intent = tickets[tickets["week_offset"] == current_week]["cancellation_intent"].mean() * 100
    prev_intent = tickets[tickets["week_offset"] == prev_week]["cancellation_intent"].mean() * 100
    deltas.append(_delta("Cancellation intent rate (%)", float(curr_intent), float(prev_intent)))

    # Food safety tickets
    deltas.append(_delta(
        "Food safety complaints",
        len(tickets[(tickets["week_offset"] == current_week) & (tickets["category"] == "Food safety concern")]),
        len(tickets[(tickets["week_offset"] == prev_week) & (tickets["category"] == "Food safety concern")]),
    ))

    # Refund decision time
    curr_ref = refunds[refunds["week_offset"] == current_week]["days_to_decision"].mean()
    prev_ref = refunds[refunds["week_offset"] == prev_week]["days_to_decision"].mean()
    deltas.append(_delta(
        "Avg days to refund decision",
        float(curr_ref) if not np.isnan(curr_ref) else 0.0,
        float(prev_ref) if not np.isnan(prev_ref) else 0.0,
    ))

    # On-time delivery rate
    curr_ot = deliveries[deliveries["week_offset"] == current_week]["on_time"].mean() * 100
    prev_ot = deliveries[deliveries["week_offset"] == prev_week]["on_time"].mean() * 100
    deltas.append(_delta(
        "On-time delivery rate (%)",
        float(curr_ot), float(prev_ot),
        concerning_if_up=False,
    ))

    # Cancellations
    deltas.append(_delta(
        "Cancellations",
        len(cancellations[cancellations["week_offset"] == current_week]),
        len(cancellations[cancellations["week_offset"] == prev_week]),
    ))

    return deltas


def _compute_financial_impact(
    customer_risk: pd.DataFrame,
    customers: pd.DataFrame,
    cancellations: pd.DataFrame,
) -> FinancialImpact:
    at_risk = customer_risk[customer_risk["churn_probability"] >= 0.35]
    arr_at_risk = float(at_risk["revenue_at_risk_usd"].sum())
    monthly_at_risk = arr_at_risk / 12
    customers_at_risk = int(len(at_risk))
    avg_clv = float(at_risk["lifetime_value_usd"].mean()) if len(at_risk) else 0.0
    # Assume a well-targeted intervention saves ~35% of the at-risk revenue.
    potential_savings = arr_at_risk * 0.35
    return FinancialImpact(
        arr_at_risk_usd=round(arr_at_risk, 2),
        monthly_revenue_at_risk_usd=round(monthly_at_risk, 2),
        customers_at_risk=customers_at_risk,
        avg_clv_at_risk_usd=round(avg_clv, 2),
        potential_savings_if_intervened_usd=round(potential_savings, 2),
    )


def _summary_stats(tickets, deliveries, refunds, cancellations, customers, current_week) -> dict[str, Any]:
    curr_tix = tickets[tickets["week_offset"] == current_week]
    return {
        "total_customers": int(len(customers)),
        "tickets_this_week": int(len(curr_tix)),
        "open_tickets": int((tickets["resolved"] == False).sum()),  # noqa: E712
        "cancellations_this_week": int(len(cancellations[cancellations["week_offset"] == current_week])),
        "refund_backlog_count": int((refunds["days_to_decision"] >= 10).sum()),
        "avg_sentiment_this_week": round(float(curr_tix["sentiment_score"].mean()), 2),
        "on_time_delivery_pct": round(float(deliveries[deliveries["week_offset"] == current_week]["on_time"].mean() * 100), 1),
    }


def _overall_risk_score(drivers, wow_deltas, customer_risk) -> float:
    top_driver_impact = drivers[0].retention_impact_score if drivers else 0
    concerning_deltas = sum(1 for d in wow_deltas if d.is_concerning and d.pct_change > 0.15)
    pct_high_risk_customers = (customer_risk["churn_probability"] >= 0.35).mean() * 100
    score = (top_driver_impact * 0.4) + (concerning_deltas * 8) + (pct_high_risk_customers * 0.8)
    return round(min(score, 100), 1)
