"""Generates realistic mock operational data for a subscription/logistics company."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
random.seed(42)

CITIES = [
    "Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt",
    "London", "Manchester", "New York", "Boston", "Chicago",
    "Toronto", "Amsterdam", "Paris", "Madrid", "Sydney",
]

COMPLAINT_CATEGORIES = [
    "Late delivery",
    "Missing item",
    "Damaged packaging",
    "Cold chain failure",
    "Food safety concern",
    "Wrong items shipped",
    "Billing error",
    "Refund delay",
    "App / account issue",
    "Subscription pause failed",
    "Recipe quality",
    "Customer service unresponsive",
]

CHANNELS = ["email", "chat", "phone", "in-app", "social"]
PLANS = ["2-person / 3 meals", "2-person / 4 meals", "4-person / 3 meals", "4-person / 4 meals", "Family box"]
TENURE_BUCKETS = ["0-3 mo", "3-6 mo", "6-12 mo", "1-2 yr", "2+ yr"]

CANCELLATION_CUES = [
    "thinking of cancelling",
    "want to cancel",
    "this is my last chance",
    "considering competitors",
    "switching to a competitor",
    "if this happens again",
    "very disappointed",
    "lost trust",
]


@dataclass
class DatasetBundle:
    tickets: pd.DataFrame
    deliveries: pd.DataFrame
    refunds: pd.DataFrame
    cancellations: pd.DataFrame
    customers: pd.DataFrame
    generated_at: datetime

    def all_frames(self) -> dict[str, pd.DataFrame]:
        return {
            "support_tickets": self.tickets,
            "deliveries": self.deliveries,
            "refunds": self.refunds,
            "cancellations": self.cancellations,
            "customers": self.customers,
        }


def _customers(n: int = 1200) -> pd.DataFrame:
    today = datetime.utcnow().date()
    rows = []
    for i in range(n):
        signup_days = int(RNG.integers(15, 900))
        tenure_days = signup_days
        plan = random.choice(PLANS)
        weekly_value = {
            "2-person / 3 meals": 49.0,
            "2-person / 4 meals": 62.0,
            "4-person / 3 meals": 79.0,
            "4-person / 4 meals": 99.0,
            "Family box": 119.0,
        }[plan]
        rows.append(
            {
                "customer_id": f"C{100000 + i}",
                "signup_date": today - timedelta(days=signup_days),
                "tenure_days": tenure_days,
                "tenure_bucket": _bucket_tenure(tenure_days),
                "plan": plan,
                "city": random.choice(CITIES),
                "weekly_value_usd": weekly_value,
                "lifetime_value_usd": round(weekly_value * tenure_days / 7 * 0.85, 2),
            }
        )
    return pd.DataFrame(rows)


def _bucket_tenure(days: int) -> str:
    if days < 90:
        return "0-3 mo"
    if days < 180:
        return "3-6 mo"
    if days < 365:
        return "6-12 mo"
    if days < 730:
        return "1-2 yr"
    return "2+ yr"


def _tickets(customers: pd.DataFrame, weeks: int = 4) -> pd.DataFrame:
    """Generate support tickets with a deliberate worsening trend in the most recent week."""
    today = datetime.utcnow()
    rows = []
    ticket_id = 700000

    # Weight categories so refund/food-safety/cold-chain dominate as "hot" themes.
    base_weights = {
        "Late delivery": 0.16,
        "Missing item": 0.10,
        "Damaged packaging": 0.08,
        "Cold chain failure": 0.10,
        "Food safety concern": 0.08,
        "Wrong items shipped": 0.07,
        "Billing error": 0.07,
        "Refund delay": 0.13,
        "App / account issue": 0.06,
        "Subscription pause failed": 0.05,
        "Recipe quality": 0.05,
        "Customer service unresponsive": 0.05,
    }
    cats = list(base_weights.keys())
    weights = np.array(list(base_weights.values()))
    weights = weights / weights.sum()

    for week in range(weeks):
        # The most recent week (week=0 here, where we map below) sees a spike in
        # refund delays, food safety, and cold chain failures.
        week_age = weeks - 1 - week  # 0 = oldest, weeks-1 = most recent
        weekly_weights = weights.copy()
        if week_age == weeks - 1:  # most recent week
            for i, cat in enumerate(cats):
                if cat in ("Refund delay", "Food safety concern", "Cold chain failure"):
                    weekly_weights[i] *= 1.55
            weekly_weights = weekly_weights / weekly_weights.sum()

        # Volume rises in the most recent week.
        base_volume = 220
        volume_multiplier = 1.0 + (0.08 * week_age) + (0.35 if week_age == weeks - 1 else 0.0)
        volume = int(base_volume * volume_multiplier)

        for _ in range(volume):
            cat = RNG.choice(cats, p=weekly_weights)
            customer = customers.sample(1).iloc[0]
            ts = today - timedelta(
                days=7 * (weeks - 1 - week_age) + int(RNG.integers(0, 7)),
                hours=int(RNG.integers(0, 24)),
            )

            severity = _severity_for(cat)
            resolution_hours = _resolution_for(cat, week_age, weeks)
            resolved = resolution_hours is not None
            sentiment = _sentiment_for(cat)
            cancel_intent = sentiment < -0.55 and RNG.random() < 0.55
            mention = random.choice(CANCELLATION_CUES) if cancel_intent else ""

            rows.append(
                {
                    "ticket_id": f"T{ticket_id}",
                    "customer_id": customer["customer_id"],
                    "created_at": ts,
                    "category": cat,
                    "channel": random.choice(CHANNELS),
                    "severity": severity,
                    "resolution_hours": resolution_hours if resolved else None,
                    "resolved": resolved,
                    "sentiment_score": round(sentiment, 2),
                    "cancellation_intent": cancel_intent,
                    "verbatim_snippet": mention or _verbatim_for(cat),
                    "city": customer["city"],
                    "plan": customer["plan"],
                    "tenure_bucket": customer["tenure_bucket"],
                    "week_offset": week_age,  # 0 = oldest, weeks-1 = current
                }
            )
            ticket_id += 1

    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def _severity_for(category: str) -> str:
    high_categories = {"Food safety concern", "Cold chain failure", "Billing error"}
    medium_categories = {"Refund delay", "Missing item", "Subscription pause failed", "Customer service unresponsive"}
    if category in high_categories:
        return RNG.choice(["High", "Critical", "Medium"], p=[0.45, 0.25, 0.30])
    if category in medium_categories:
        return RNG.choice(["High", "Medium", "Low"], p=[0.30, 0.55, 0.15])
    return RNG.choice(["High", "Medium", "Low"], p=[0.15, 0.55, 0.30])


def _resolution_for(category: str, week_age: int, weeks: int) -> float | None:
    """Refunds in the most recent week take dramatically longer (the 'story' the AI should find)."""
    if RNG.random() < 0.18:
        return None  # still open
    if category == "Refund delay":
        if week_age == weeks - 1:
            return float(np.clip(RNG.normal(58, 18), 20, 120))
        return float(np.clip(RNG.normal(22, 8), 6, 60))
    if category == "Food safety concern":
        return float(np.clip(RNG.normal(12, 6), 2, 48))
    if category == "Cold chain failure":
        return float(np.clip(RNG.normal(36, 14), 8, 96))
    if category == "Billing error":
        return float(np.clip(RNG.normal(28, 12), 6, 80))
    return float(np.clip(RNG.normal(14, 8), 1, 60))


def _sentiment_for(category: str) -> float:
    base = {
        "Food safety concern": -0.78,
        "Cold chain failure": -0.65,
        "Refund delay": -0.62,
        "Billing error": -0.55,
        "Customer service unresponsive": -0.58,
        "Missing item": -0.40,
        "Damaged packaging": -0.30,
        "Wrong items shipped": -0.42,
        "Late delivery": -0.35,
        "Subscription pause failed": -0.45,
        "App / account issue": -0.25,
        "Recipe quality": -0.20,
    }[category]
    return float(np.clip(base + RNG.normal(0, 0.15), -1.0, 0.5))


def _verbatim_for(category: str) -> str:
    samples = {
        "Late delivery": "Box arrived two days late again.",
        "Missing item": "Two ingredients missing from this week's box.",
        "Damaged packaging": "Box was crushed and contents leaked.",
        "Cold chain failure": "Meat was warm to the touch when it arrived.",
        "Food safety concern": "Found mold on the produce — really concerned.",
        "Wrong items shipped": "Received the wrong meals entirely.",
        "Billing error": "Charged twice for the same week.",
        "Refund delay": "Still waiting on my refund from two weeks ago.",
        "App / account issue": "Cannot update my address in the app.",
        "Subscription pause failed": "Asked to pause and was charged anyway.",
        "Recipe quality": "Recipes have been bland the last few weeks.",
        "Customer service unresponsive": "No reply to my support email for 5 days.",
    }
    return samples.get(category, "")


def _deliveries(customers: pd.DataFrame, weeks: int = 4) -> pd.DataFrame:
    today = datetime.utcnow()
    rows = []
    sample = customers.sample(min(700, len(customers)), random_state=1)
    for _, customer in sample.iterrows():
        # 4 deliveries per sampled customer over the period.
        for week in range(weeks):
            week_age = weeks - 1 - week
            on_time_prob = 0.92 if week_age != weeks - 1 else 0.84
            cold_chain_ok_prob = 0.97 if week_age != weeks - 1 else 0.91
            on_time = RNG.random() < on_time_prob
            cold_chain_ok = RNG.random() < cold_chain_ok_prob
            issue = None
            if not on_time:
                issue = "Late delivery"
            elif not cold_chain_ok:
                issue = "Cold chain failure"
            elif RNG.random() < 0.04:
                issue = random.choice(["Damaged packaging", "Missing item", "Wrong items shipped"])

            rows.append(
                {
                    "delivery_id": f"D{800000 + len(rows)}",
                    "customer_id": customer["customer_id"],
                    "delivery_date": (today - timedelta(days=7 * week_age + int(RNG.integers(0, 7)))).date(),
                    "city": customer["city"],
                    "on_time": on_time,
                    "cold_chain_ok": cold_chain_ok,
                    "issue": issue,
                    "compensation_usd": round(float(RNG.uniform(0, 25)), 2) if issue else 0.0,
                    "week_offset": week_age,
                }
            )
    return pd.DataFrame(rows)


def _refunds(tickets: pd.DataFrame) -> pd.DataFrame:
    refund_tix = tickets[tickets["category"].isin(["Refund delay", "Billing error", "Missing item"])].copy()
    refund_tix = refund_tix.sample(min(len(refund_tix), 320), random_state=2)
    rows = []
    for _, t in refund_tix.iterrows():
        requested = float(RNG.uniform(8, 110))
        approved_prob = 0.78 if t["category"] == "Billing error" else 0.62
        approved = RNG.random() < approved_prob
        days_to_decision = (
            float(RNG.normal(6, 2)) if t["week_offset"] != tickets["week_offset"].max()
            else float(RNG.normal(14, 4))
        )
        rows.append(
            {
                "refund_id": f"R{900000 + len(rows)}",
                "customer_id": t["customer_id"],
                "ticket_id": t["ticket_id"],
                "requested_usd": round(requested, 2),
                "approved": approved,
                "amount_usd": round(requested * (0.85 if approved else 0.0), 2),
                "days_to_decision": round(max(1.0, days_to_decision), 1),
                "week_offset": t["week_offset"],
            }
        )
    return pd.DataFrame(rows)


def _cancellations(customers: pd.DataFrame, tickets: pd.DataFrame, weeks: int = 4) -> pd.DataFrame:
    rows = []
    # Customers with cancellation_intent in tickets are more likely to cancel.
    intent_customers = set(tickets.loc[tickets["cancellation_intent"], "customer_id"].unique())
    for week_age in range(weeks):
        base = 28
        if week_age == weeks - 1:
            base = int(base * 1.45)
        n = int(RNG.normal(base, 4))
        for _ in range(n):
            # Pick cancellation skewed to intent customers
            if intent_customers and RNG.random() < 0.6:
                cid = random.choice(list(intent_customers))
            else:
                cid = customers.sample(1).iloc[0]["customer_id"]
            customer = customers[customers["customer_id"] == cid].iloc[0]
            reasons = [
                "Refund issues",
                "Delivery quality",
                "Food safety concern",
                "Price",
                "Lifestyle change",
                "Recipe variety",
                "Support experience",
            ]
            reason_weights = [0.22, 0.18, 0.10, 0.18, 0.12, 0.10, 0.10]
            if week_age == weeks - 1:
                reason_weights[0] += 0.08
                reason_weights[1] += 0.05
                reason_weights[2] += 0.03
                reason_weights = [w / sum(reason_weights) for w in reason_weights]
            reason = RNG.choice(reasons, p=reason_weights)
            rows.append(
                {
                    "cancellation_id": f"X{600000 + len(rows)}",
                    "customer_id": cid,
                    "cancelled_at": (datetime.utcnow() - timedelta(days=7 * week_age + int(RNG.integers(0, 7)))).date(),
                    "reason": reason,
                    "tenure_bucket": customer["tenure_bucket"],
                    "lifetime_value_usd": customer["lifetime_value_usd"],
                    "plan": customer["plan"],
                    "week_offset": week_age,
                }
            )
    return pd.DataFrame(rows)


def generate_bundle() -> DatasetBundle:
    customers = _customers()
    tickets = _tickets(customers)
    deliveries = _deliveries(customers)
    refunds = _refunds(tickets)
    cancellations = _cancellations(customers, tickets)
    return DatasetBundle(
        tickets=tickets,
        deliveries=deliveries,
        refunds=refunds,
        cancellations=cancellations,
        customers=customers,
        generated_at=datetime.utcnow(),
    )
