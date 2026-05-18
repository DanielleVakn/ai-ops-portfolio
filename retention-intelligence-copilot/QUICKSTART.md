# Quick Start

## Setup (one-time)

```bash
cd retention-intelligence-copilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

```bash
source .venv/bin/activate
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Optional: Enable Claude-powered synthesis

By default, the app uses a deterministic analyst engine to generate all AI insights. To enable live Claude synthesis:

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

Then in the sidebar, toggle **"Use Claude for synthesis"** to on.

## What you'll see

- **Executive Summary** — Headline + Chief-of-Staff briefing + strategic recommendations
- **Churn Risk Radar** — Risk gauge (0–100) + customer risk distribution
- **Operational Root Cause** — Top drivers with week-over-week deltas + expandable narratives
- **AI Interventions** — 5–7 prioritized actions with urgency, owner, impact, ROI
- **Financial Impact** — ARR at risk + intervention simulator
- **High-Risk Segments** — Cohorts to target for retention + top 25 customers
- **What Changed** — Week-over-week deltas + concern flagging

## Exports

- **Executive briefing** → Markdown (print-friendly, email-ready)
- **At-risk customers** → CSV (import to CX platform)
- **Operational data** → XLSX (raw tickets, deliveries, refunds, cancellations, customers)

## Data

The MVP ships with **realistic mock data** seeded to tell a story:
- 1,200 customers
- 1,000+ tickets with refund delays, food safety, cold-chain failures
- Deliberate spike in the latest week: refund decision time +190% WoW

To test with your own data, upload a CSV in the sidebar (columns: customer_id, category, resolution_hours, sentiment_score, etc.). The analytics still derive from the bundled set in this MVP, but you can see the upload shape.

## Architecture

- **app.py** — Streamlit UI, 7 sections, caching, exports
- **src/data_generator.py** — Mock operational signals (1,200 customers, 4 weeks)
- **src/analytics.py** — Churn drivers, risk segments, WoW deltas, financial impact
- **src/ai_engine.py** — Claude synthesis (or deterministic fallback)
- **src/ui_components.py** — Styled cards, gauges, charts (dark theme)

No database. No infrastructure. ~1,400 lines of Python.

## Notes

- **Caching:** Data generation, analytics, and AI synthesis are cached. Use "Re-run AI synthesis" in the sidebar to regenerate.
- **Risk scores:** The app's "Critical" rating is driven by driver impact, WoW shifts, and customer-level churn probability. The mock data is intentionally set to showcase this.
- **Interventions:** Each recommendation names an operational owner (CX Ops, Logistics, Finance, Product) and an estimated ROI based on the cohort size and expected impact.
