# Retention Intelligence Copilot — Product Overview

## Vision

An AI-powered **executive command center** that transforms fragmented operational signals into retention-focused intelligence for leadership at subscription/logistics businesses.

**The problem:** Modern companies have dashboards and KPIs, but executives lack:
- Operational causality (why are customers churning?)
- Actionable prioritization (what should we do first?)
- Financial clarity (what's the retention exposure?)
- Synthesis speed (waiting for BI dashboards, not real-time intelligence)

**The solution:** This MVP demonstrates how AI can serve as a Chief-of-Staff layer that:
- Ingests operational signals (tickets, deliveries, refunds, cancellations)
- Surfaces root causes (weighted by retention impact)
- Recommends interventions (with owner, urgency, ROI)
- Translates to financial impact (ARR at risk, recovery opportunity)

## Key Differentiators

1. **Operational specificity.** Not "improve customer satisfaction." Rather: "Escalate refund tickets aged >7d to priority queue; auto-issue credits while approval is pending" (owner: CX Ops, urgency: Immediate, ROI: $36K/wk).

2. **AI-native but not chatbot.** Claude synthesizes a tight context payload into structured recommendations. No freeform chat. Every output has a schema, urgency, owner, and dollar estimate.

3. **Works offline.** A deterministic analyst engine produces identical output shape without an API key, so the tool is never blocked on LLM availability.

4. **Executive voice.** System prompt anchors Claude as "Chief of Staff to the COO" — the output reads like a strategic advisor, not a BI tool.

5. **MVP-grade Polish.** Dark executive theme, risk gauges, intervention cards, financial simulator. Looks like a tool that can be shown to the C-suite.

## Sections (7 core + bonuses)

| Section | Purpose | Output |
|---------|---------|--------|
| **Executive Summary** | Chief-of-Staff briefing | Headline + summary + top risks + strategic recs |
| **Churn Risk Radar** | Overall risk state | Gauge (0–100) + customer-tier distribution |
| **Operational Root Cause** | Pattern detection | Impact bar + 4-week trend + narratives (expandable) |
| **AI Interventions** | Prioritized actions | 5–7 cards (urgency, owner, impact, ROI, tradeoffs) |
| **Financial Impact** | Exposure + recovery | ARR/MRR at risk + **intervention simulator** (bonus) |
| **High-Risk Segments** | Cohort targeting | 5 segments + top 25 individual customers |
| **What Changed** | WoW deltas | Metric comparison + concern flagging |
| **Exports** | Data sharing | Briefing (Markdown), customers (CSV), raw (XLSX) |

## Architecture

```
~2,150 lines of clean Python (no infra, no DB, no APIs except Claude)

app.py                        # Streamlit UI wires sections + caching + export
├─ src/data_generator.py      # 1,200 customers + 1,000+ operational signals (mock)
├─ src/analytics.py           # Pandas: drivers, segments, WoW, financial
├─ src/ai_engine.py           # Claude + deterministic fallback
└─ src/ui_components.py       # Styled cards, gauges, charts (dark theme)
```

## Example Output (Fallback / Deterministic Synthesis)

**Data:** Mock dataset with 1,200 customers, 4 weeks of signals, deliberate spike in refund delays (+190% WoW) and food-safety complaints (+96%).

**Output:**
```
Headline:
"Food safety concern is the dominant retention threat this week; 
 avg days to refund decision up 135% WoW."

Overall Risk: CRITICAL (88/100)
ARR at Risk: $747K across 323 customers
Potential Recovery: $261K with recommended interventions

Top Interventions (prioritized by urgency × impact):
1. [IMMEDIATE] Escalate aged refund tickets to priority queue
   Owner: CX Ops | ROI: $36.8K | Expected impact: 18–25% churn reduction
   
2. [IMMEDIATE] Same-day senior-CX response for food safety tickets
   Owner: CX Ops | ROI: $28.1K | Expected impact: ~30% churn reduction
   
3. [THIS WEEK] Proactive replacement shipment + carrier review
   Owner: Logistics | ROI: $23.7K | Expected impact: ~22% secondary-churn reduction

4. [THIS WEEK] Billing reconciliation sweep + auto-credit
   Owner: Finance | ROI: $16.6K | Expected impact: Eliminates billing-driven churn

5. [THIS WEEK] Single-owner continuity model for at-risk tickets
   Owner: CX Ops | ROI: $14.4K | Expected impact: ~15% NPS lift in cohort

Risk Segments (operational targeting):
- Long-tenure loyalists hit by first major issue (48 customers, $182K ARR at risk)
  → Recovery: high-touch personal outreach + proactive credit
  
- Customers in refund processing backlog (67 customers, $159K ARR at risk)
  → Recovery: same-day approval + auto-credit while ticket is in flight
  
- Customers with explicit cancellation intent (92 customers, $218K ARR at risk)
  → Recovery: manager-level callback + save offer (skip-week + 30% off)
```

**Claude-powered synthesis** (with API key) produces the same structure but with deeper causal reasoning and more sophisticated prioritization.

## User Journey

1. **Open app** → Real-time data generation (or upload CSV)
2. **Skim executive summary** → Understand the week's retention picture in 30 seconds
3. **Review risk radar + root causes** → See what's breaking and why
4. **Scan interventions** → Know which lever to pull, who owns it, and what it'll save
5. **Check segments** → Identify the customers to call today
6. **Export briefing** → Share with the leadership team (Markdown → PDF)

## Success Metrics

For the **MVP**, success looks like:
- ✅ Reduced ambiguity on churn causality (execs know *why* customers are leaving)
- ✅ Faster decision-making (priorities are pre-ranked)
- ✅ Accountable interventions (each has an owner, urgency, expected ROI)
- ✅ Finance-aware (everything translates to ARR impact)
- ✅ Polished enough to show leadership (not a prototype, a tool)

For **production**, the next phases would be:
- Real data ingestion (connect to support ticketing, subscription, payment systems)
- Predictive churn scoring (ML model, not heuristics)
- Closed-loop impact tracking (did the intervention work?)
- Proactive alerts (churn risk flagged in real-time, not weekly)
- Multi-tenant SaaS (white-label for other subscription companies)

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Streamlit** (not React/Django) | Speed to MVP, live iteration, caching, authentication built-in |
| **Mock data** (not live DB) | Offline, repeatable, tells a coherent story without schema complexity |
| **Claude** (not GPT-4) | Structured JSON out of the box, better system prompts, cost-effective |
| **Deterministic fallback** | Never blocked on LLM availability; same UX offline or online |
| **Dark theme** | Executive aesthetic, reduces eye strain for long sessions, modern feel |
| **Single file for UI** | Low cognitive load, Streamlit handles reactivity, no state management |

![Output](screenshots/retention_copilot1.png)
![Output](screenshots/retention_copilot2.png)
![Output](screenshots/retention_copilot3.png)
![Output](screenshots/retention_copilot4.png)
![Output](screenshots/retention_copilot5.png)
![Output](screenshots/retention_copilot6.png)
![Output](screenshots/retention_copilot7.png)
![Output](screenshots/retention_copilot8.png)
![Output](screenshots/retention_copilot9.png)
![Output](screenshots/retention_copilot10.png)




└── PRODUCT_OVERVIEW.md       # This file
```
