import streamlit as st


# ─── CSS INJECTION ───────────────────────────────────────────────────────────

def inject_custom_css():
    """Inject the global design system CSS."""
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

:root {
  --navy:       #0f172a;
  --navy-mid:   #1e293b;
  --teal:       #0ea5e9;
  --teal-dark:  #0284c7;
  --bg:         #f1f5f9;
  --card:       #ffffff;
  --border:     #e2e8f0;
  --text:       #1e293b;
  --subtext:    #64748b;
  --green:      #22c55e;
  --amber:      #f59e0b;
  --red:        #ef4444;
  --slate:      #94a3b8;
  --shadow-xs:  0 1px 2px rgba(0,0,0,.05);
  --shadow-sm:  0 1px 3px rgba(0,0,0,.07), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md:  0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
  --r-sm: 8px;
  --r-md: 12px;
  --r-lg: 16px;
}

/* ── GLOBAL ── */
.stApp { background: var(--bg) !important; font-family: 'Inter', system-ui, sans-serif; }
.block-container { padding-top: 0 !important; max-width: 1400px !important; }

/* ── HEADER ── */
.tc-header {
  background: linear-gradient(135deg, #0f172a 0%, #1a3356 58%, #0c2d4e 100%);
  padding: 1.75rem 2.5rem 1.75rem;
  margin: 0 -4rem 2rem -4rem;
  position: relative;
  overflow: hidden;
}
.tc-header::before {
  content: '';
  position: absolute; top: -50%; right: -2%; width: 44%; height: 220%;
  background: radial-gradient(ellipse at right, rgba(14,165,233,.11) 0%, transparent 65%);
  pointer-events: none;
}
.tc-header::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(14,165,233,.5) 50%, transparent 100%);
}
.tc-brand-pill {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(14,165,233,.14); border: 1px solid rgba(14,165,233,.3);
  border-radius: 100px; color: #7dd3fc;
  font-size: .68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  padding: .2rem .75rem; margin-bottom: .9rem;
}
.tc-brand-pill-dot {
  width: 5px; height: 5px; border-radius: 50%; background: var(--teal);
  animation: pdot 2.2s ease-in-out infinite;
}
@keyframes pdot { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:.35; transform:scale(.7); } }
.tc-header h1 {
  color: #fff; font-size: 1.875rem; font-weight: 800;
  margin: 0 0 .4rem; letter-spacing: -.025em; line-height: 1.2;
}
.tc-header p { color: rgba(255,255,255,.5); font-size: .9rem; margin: 0; line-height: 1.55; }

/* ── SECTION LABELS ── */
.tc-section-label {
  display: flex; align-items: center; gap: .6rem;
  font-size: .95rem; font-weight: 700; color: var(--navy-mid);
  margin: 1.5rem 0 .9rem; padding-bottom: .55rem;
  border-bottom: 1.5px solid var(--border);
}
.tc-section-label::before {
  content: ''; display: inline-block;
  width: 3px; height: 1rem; flex-shrink: 0; border-radius: 2px;
  background: linear-gradient(180deg, var(--teal), var(--teal-dark));
}

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--card); border: 1px solid var(--border); border-bottom: none;
  border-radius: var(--r-md) var(--r-md) 0 0; padding: .4rem .5rem 0;
  box-shadow: var(--shadow-sm);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif !important; font-size: .875rem !important;
  font-weight: 600 !important; color: var(--subtext) !important;
  padding: .6rem 1.25rem !important;
  border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
  background: transparent !important; border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"] {
  color: var(--teal-dark) !important; background: rgba(14,165,233,.07) !important;
  border-bottom: 2px solid var(--teal) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  background: var(--card); border: 1px solid var(--border); border-top: none;
  border-radius: 0 0 var(--r-md) var(--r-md); padding: 1.75rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

/* ── BUTTONS ── */
[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--teal), var(--teal-dark)) !important;
  border: none !important; border-radius: var(--r-sm) !important;
  font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
  font-size: .875rem !important; color: #fff !important;
  box-shadow: 0 2px 8px rgba(14,165,233,.35) !important;
  transition: all .2s ease !important;
}
[data-testid="stBaseButton-primary"]:hover {
  transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(14,165,233,.5) !important;
}
[data-testid="stBaseButton-secondary"] {
  background: var(--card) !important; border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important; font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important; color: var(--subtext) !important; transition: all .15s ease !important;
}
[data-testid="stBaseButton-secondary"]:hover {
  border-color: var(--teal) !important; color: var(--teal-dark) !important;
  background: rgba(14,165,233,.04) !important;
}

/* ── BADGES ── */
.tc-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: .28rem .8rem; border-radius: 100px; font-size: .72rem;
  font-weight: 700; letter-spacing: .07em; text-transform: uppercase;
  border: 1px solid; white-space: nowrap;
}
.tc-badge-dot { width: 5px; height: 5px; border-radius: 50%; }
.tc-badge-green  { background: rgba(34,197,94,.09);  color: #15803d; border-color: rgba(34,197,94,.28);  }
.tc-badge-green  .tc-badge-dot { background: #22c55e; }
.tc-badge-amber  { background: rgba(245,158,11,.09); color: #92400e; border-color: rgba(245,158,11,.28); }
.tc-badge-amber  .tc-badge-dot { background: #f59e0b; }
.tc-badge-red    { background: rgba(239,68,68,.09);  color: #991b1b; border-color: rgba(239,68,68,.28);  }
.tc-badge-red    .tc-badge-dot { background: #ef4444; }
.tc-badge-slate  { background: rgba(148,163,184,.12); color: #475569; border-color: rgba(148,163,184,.28); }
.tc-badge-slate  .tc-badge-dot { background: #94a3b8; }

/* ── KPI CARDS ── */
.tc-kpi-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--r-md);
  padding: 1.4rem 1.5rem; box-shadow: var(--shadow-sm); overflow: hidden;
  position: relative; height: 100%; transition: box-shadow .2s;
}
.tc-kpi-card:hover { box-shadow: var(--shadow-md); }
.tc-kpi-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .1em;
  color: var(--subtext); margin: 0 0 .55rem;
}
.tc-kpi-value {
  font-size: 2.5rem; font-weight: 800; line-height: 1.05;
  margin: 0 0 .5rem; letter-spacing: -.04em;
}
.tc-kpi-caption { font-size: .78rem; color: var(--subtext); margin-top: .3rem; }

/* ── CONTENT CARDS ── */
.tc-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--r-md);
  padding: 1.1rem 1.25rem; box-shadow: var(--shadow-sm); height: 100%;
  margin-bottom: .5rem;
}
.tc-card-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em;
  color: var(--subtext); margin: 0 0 .5rem; padding-bottom: .5rem;
  border-bottom: 1px solid var(--border);
}
.tc-card-big-num {
  font-size: 2.25rem; font-weight: 800; letter-spacing: -.03em;
  margin: .25rem 0 .4rem; color: var(--text);
}

/* ── RESULT SECTION CARD ── */
.tc-result-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--r-md);
  padding: 1.1rem 1.25rem; box-shadow: var(--shadow-sm); margin-bottom: .6rem;
}
.tc-result-header {
  font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em;
  color: var(--subtext); padding-bottom: .5rem; border-bottom: 1px solid var(--border);
  margin-bottom: .65rem;
}

/* ── BATCH BANNER ── */
.tc-batch-banner {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--r-md);
  padding: 1.25rem 1.5rem; box-shadow: var(--shadow-sm); margin-bottom: 1.25rem;
  display: flex; align-items: center; gap: 1.25rem;
}
.tc-batch-banner-num {
  font-size: 2.75rem; font-weight: 800; line-height: 1;
  letter-spacing: -.04em; flex-shrink: 0;
}
.tc-batch-banner-total { font-size: 1.1rem; color: var(--subtext); font-weight: 500; }
.tc-batch-banner-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em;
  color: var(--subtext); margin-bottom: .2rem;
}
.tc-batch-banner-desc { font-size: .85rem; color: var(--subtext); }

/* ── INPUTS ── */
[data-baseweb="textarea"],[data-baseweb="input"] {
  border-radius: var(--r-sm) !important; border-color: var(--border) !important;
  font-family: 'Inter', sans-serif !important; font-size: .9rem !important;
  background: var(--card) !important;
}
[data-baseweb="textarea"]:focus-within,[data-baseweb="input"]:focus-within {
  border-color: var(--teal) !important; box-shadow: 0 0 0 3px rgba(14,165,233,.12) !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
  border: 1px solid var(--border) !important; border-radius: var(--r-sm) !important;
  background: var(--card) !important; box-shadow: var(--shadow-xs) !important;
  margin-bottom: .4rem;
}
[data-testid="stExpander"] summary {
  font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
  font-size: .875rem !important; color: var(--text) !important;
}

/* ── PROGRESS BAR ── */
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, var(--teal), var(--teal-dark)) !important;
  border-radius: 100px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border-radius: var(--r-md) !important; overflow: hidden;
  box-shadow: var(--shadow-sm) !important; border: 1px solid var(--border) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] { border-radius: var(--r-sm) !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stInfo"] { background: rgba(14,165,233,.06) !important; border-color: rgba(14,165,233,.25) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploaderDropzone"] {
  border-radius: var(--r-md) !important; border: 2px dashed var(--border) !important;
  background: rgba(241,245,249,.6) !important; transition: border-color .2s, background .2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--teal) !important; background: rgba(14,165,233,.04) !important;
}

/* ── METRIC WIDGETS ── */
[data-testid="stMetric"] {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--r-sm); padding: .875rem 1rem; box-shadow: var(--shadow-xs);
}
[data-testid="stMetricLabel"] {
  font-family: 'Inter', sans-serif !important; font-size: .7rem !important;
  font-weight: 700 !important; text-transform: uppercase !important;
  letter-spacing: .08em !important; color: var(--subtext) !important;
}
[data-testid="stMetricValue"] {
  font-family: 'Inter', sans-serif !important; font-size: 1.75rem !important;
  font-weight: 800 !important; color: var(--text) !important; letter-spacing: -.025em !important;
}

/* ── DIVIDER ── */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.25rem 0 !important; }

/* ── H3 OVERRIDE ── */
.stMarkdown h3 {
  font-family: 'Inter', sans-serif !important; font-size: .95rem !important;
  font-weight: 700 !important; color: var(--navy-mid) !important;
  padding-bottom: .4rem !important; border-bottom: 1.5px solid var(--border) !important;
  margin-top: 1.2rem !important; letter-spacing: -.01em !important;
}
</style>""", unsafe_allow_html=True)


# ─── HEADER ──────────────────────────────────────────────────────────────────

def render_header():
    """Render the app header."""
    st.markdown("""
<div class="tc-header">
  <div class="tc-brand-pill">
    <span class="tc-brand-pill-dot"></span>
    HelloFresh Support Intelligence
  </div>
  <h1>🎟️ Ticket Continuity Copilot</h1>
  <p>AI-powered analysis to prevent premature closure and ensure seamless handoffs.</p>
</div>
""", unsafe_allow_html=True)


# ─── BADGE UTILITIES ─────────────────────────────────────────────────────────

def _make_badge(label: str, variant: str) -> str:
    """Return HTML string for a pill badge. variant: 'green'|'amber'|'red'|'slate'"""
    cls = f"tc-badge-{variant}" if variant in ("green", "amber", "red", "slate") else "tc-badge-slate"
    return (
        f'<span class="tc-badge {cls}">'
        f'<span class="tc-badge-dot"></span>'
        f'{label}'
        f'</span>'
    )


def _verdict_to_variant(value: str, mode: str = "verdict") -> str:
    """Map verdict/level strings to badge color variants."""
    v = str(value).strip().upper()
    if mode == "verdict":
        return {"YES": "green", "NO": "red", "MAYBE": "amber"}.get(v, "slate")
    elif mode == "risk":
        return {"LOW": "green", "MEDIUM": "amber", "HIGH": "red"}.get(v, "slate")
    elif mode == "sentiment":
        try:
            score = float(v)
            if score >= 7:
                return "green"
            if score >= 4:
                return "amber"
            return "red"
        except Exception:
            return "slate"
    return "slate"


def _variant_to_hex(variant: str) -> str:
    """Return hex color for a badge variant."""
    return {"green": "#22c55e", "amber": "#f59e0b", "red": "#ef4444"}.get(variant, "#94a3b8")


def _to_html_list(items: any) -> str:
    """Convert a list or bullet-string to an HTML unordered list."""
    if not items:
        return '<em style="color:#94a3b8;font-size:.875rem;">None identified</em>'
    if isinstance(items, list):
        rows = [f"<li>{str(i).strip()}</li>" for i in items if str(i).strip()]
        if not rows:
            return '<em style="color:#94a3b8;font-size:.875rem;">None identified</em>'
        return f'<ul style="margin:.25rem 0;padding-left:1.2rem;line-height:1.7;font-size:.9rem;">{"".join(rows)}</ul>'
    text = str(items).strip()
    if not text:
        return '<em style="color:#94a3b8;font-size:.875rem;">None identified</em>'
    if "•" in text or "\n" in text:
        lines = [ln.strip().lstrip("•").strip() for ln in text.replace("•", "\n").split("\n") if ln.strip().lstrip("•").strip()]
        if lines:
            rows = "".join(f"<li>{ln}</li>" for ln in lines)
            return f'<ul style="margin:.25rem 0;padding-left:1.2rem;line-height:1.7;font-size:.9rem;">{rows}</ul>'
    return f'<p style="margin:0;line-height:1.7;font-size:.9rem;">{text}</p>'


# ─── LEGACY COMPAT ───────────────────────────────────────────────────────────

def render_status_badge(label: str, status: str, color_map: dict) -> str:
    """Generate a styled status badge (legacy compatibility)."""
    color = color_map.get(status.upper(), "gray")
    emoji_map = {"🟢": "✅", "🟡": "⚠️", "🔴": "❌", "gray": "⚪"}
    emoji = emoji_map.get(color, "")
    return f"{emoji} **{status.upper()}**"


# ─── COMPONENT RENDERERS ─────────────────────────────────────────────────────

def render_confidence_bar(confidence: str) -> None:
    """Render a confidence badge."""
    conf_lower = str(confidence).lower().strip()
    variant = {"high": "green", "medium": "amber", "low": "red"}.get(conf_lower, "slate")
    st.markdown(_make_badge(f"Confidence: {confidence.upper()}", variant), unsafe_allow_html=True)


def render_sentiment_card(sentiment_data: dict) -> None:
    """Render sentiment with visual score bar."""
    if isinstance(sentiment_data, str):
        _safe_markdown(sentiment_data)
        return

    score = sentiment_data.get("score", "N/A")
    overall = str(sentiment_data.get("overall", "unknown")).strip().upper()
    indicators = str(sentiment_data.get("key_indicators", "")).strip()

    try:
        score_val = float(score) if score != "N/A" else None
        if score_val is not None:
            variant = _verdict_to_variant(str(score_val), mode="sentiment")
            color = _variant_to_hex(variant)
            score_pct = int((score_val / 10) * 100)
            badge = _make_badge(overall, variant)
            st.markdown(f"""
<div style="margin-bottom:.5rem;">
  {badge}
  <span style="font-size:1.6rem;font-weight:800;color:{color};margin-left:.5rem;
               letter-spacing:-.025em;vertical-align:middle;">{score}/10</span>
</div>
<div style="background:#e2e8f0;border-radius:100px;height:5px;margin-bottom:.5rem;overflow:hidden;">
  <div style="width:{score_pct}%;height:100%;background:{color};border-radius:100px;"></div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(_make_badge(overall, "slate"), unsafe_allow_html=True)
    except Exception:
        st.markdown(_make_badge(overall, "slate"), unsafe_allow_html=True)

    if indicators:
        st.markdown(
            f'<div style="font-size:.85rem;color:#64748b;margin-top:.3rem;">'
            f'<strong>Drivers:</strong> {indicators}</div>',
            unsafe_allow_html=True,
        )


def render_safe_to_close_card(data: dict) -> None:
    """Render safe-to-close assessment with verdict badge."""
    if isinstance(data, str):
        _safe_markdown(data)
        return

    verdict = str(data.get("verdict", "UNKNOWN")).strip().upper()
    confidence = str(data.get("confidence", "unknown")).strip()
    reasoning = str(data.get("reasoning", "")).strip()

    variant = _verdict_to_variant(verdict, mode="verdict")
    color = _variant_to_hex(variant)
    badge = _make_badge(verdict, variant)
    conf_badge = _make_badge(f"Confidence: {confidence.upper()}", variant)

    st.markdown(f"""
<div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.75rem;flex-wrap:wrap;">
  <span style="font-size:2.25rem;font-weight:800;color:{color};letter-spacing:-.035em;">{verdict}</span>
  {badge}
  {conf_badge}
</div>
""", unsafe_allow_html=True)

    if reasoning:
        _safe_markdown(reasoning)


def render_escalation_card(data: dict) -> None:
    """Render escalation risk with level badge and detail expanders."""
    if isinstance(data, str):
        _safe_markdown(data)
        return

    level = str(data.get("level", "UNKNOWN")).strip().upper()
    reasoning = str(data.get("reasoning", "")).strip()
    actions = str(data.get("required_actions_to_prevent", "")).strip()

    variant = _verdict_to_variant(level, mode="risk")
    color = _variant_to_hex(variant)
    badge = _make_badge(f"{level} Risk", variant)

    st.markdown(f"""
<div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.75rem;flex-wrap:wrap;">
  <span style="font-size:2.25rem;font-weight:800;color:{color};letter-spacing:-.035em;">{level}</span>
  {badge}
</div>
""", unsafe_allow_html=True)

    if reasoning:
        with st.expander("Risk Factors", expanded=True):
            _safe_markdown(_format_list_as_markdown(reasoning))

    if actions:
        with st.expander("Prevention Actions", expanded=True):
            _safe_markdown(_format_list_as_markdown(actions))


def render_metrics(result: dict) -> None:
    """Render safe-to-close and escalation risk as KPI hero cards."""
    col1, col2 = st.columns(2)

    with col1:
        safe_verdict = result.get("safe_to_close", {})
        if isinstance(safe_verdict, dict):
            verdict = safe_verdict.get("verdict", "?").strip().upper()
            confidence = safe_verdict.get("confidence", "?").strip().capitalize()
            variant = _verdict_to_variant(verdict, mode="verdict")
            color = _variant_to_hex(variant)
            badge = _make_badge(verdict, variant)
            st.markdown(f"""
<div class="tc-kpi-card" style="border-left:4px solid {color};">
  <div class="tc-kpi-label">Safe to Close</div>
  <div class="tc-kpi-value" style="color:{color};">{verdict}</div>
  <div style="margin:.25rem 0 .3rem;">{badge}</div>
  <div class="tc-kpi-caption">Confidence: {confidence}</div>
</div>
""", unsafe_allow_html=True)

    with col2:
        escalation = result.get("escalation_risk", {})
        if isinstance(escalation, dict):
            level = escalation.get("level", "?").strip().upper()
            variant = _verdict_to_variant(level, mode="risk")
            color = _variant_to_hex(variant)
            badge = _make_badge(f"{level} Risk", variant)
            st.markdown(f"""
<div class="tc-kpi-card" style="border-left:4px solid {color};">
  <div class="tc-kpi-label">Escalation Risk</div>
  <div class="tc-kpi-value" style="color:{color};">{level}</div>
  <div style="margin:.25rem 0 .3rem;">{badge}</div>
  <div class="tc-kpi-caption">Escalation probability assessment</div>
</div>
""", unsafe_allow_html=True)


def render_result_section(
    title: str,
    content: any,
    collapsible: bool = False,
    expanded: bool = True,
) -> None:
    """Render a result section — card for non-collapsible, expander for collapsible."""
    if collapsible:
        with st.expander(title, expanded=expanded):
            _render_section_content(title, content)
        return

    # Non-collapsible with simple (string/list) content → full HTML card
    if not isinstance(content, dict):
        title_html = f'<div class="tc-result-header">{title}</div>' if title else ""
        if content:
            body_html = _to_html_list(content) if isinstance(content, list) else (
                f'<div style="font-size:.9rem;line-height:1.7;color:#1e293b;">'
                f'{str(content).strip()}</div>'
            )
        else:
            body_html = '<em style="color:#94a3b8;font-size:.875rem;">No data available</em>'
        st.markdown(
            f'<div class="tc-result-card">{title_html}{body_html}</div>',
            unsafe_allow_html=True,
        )
        return

    # Non-collapsible with dict content → styled title, then native renderer
    if title:
        st.markdown(f'<div class="tc-result-header">{title}</div>', unsafe_allow_html=True)
    _render_section_content(title, content)


def render_continuity_failures_card(data: dict) -> None:
    """Render continuity failure detection as a styled card."""
    if isinstance(data, str):
        _safe_markdown(data)
        return

    detected = str(data.get("detected", "no")).strip().lower() == "yes"
    count = str(data.get("count", "0")).strip()
    issues = data.get("issues", "")

    if detected:
        badge = _make_badge(f"{count} Issues Detected", "red")
        issues_html = _to_html_list(issues)
        st.markdown(f"""
<div class="tc-card">
  <div class="tc-card-label">Continuity Failures</div>
  <div style="margin:.35rem 0 .6rem;">{badge}</div>
  <div>{issues_html}</div>
</div>
""", unsafe_allow_html=True)
    else:
        badge = _make_badge("No Issues", "green")
        st.markdown(f"""
<div class="tc-card">
  <div class="tc-card-label">Continuity Failures</div>
  <div style="margin:.35rem 0 .4rem;">{badge}</div>
  <div style="font-size:.85rem;color:#15803d;">Handoff quality looks good</div>
</div>
""", unsafe_allow_html=True)


def render_rep_transitions_card(count: any) -> None:
    """Render rep transition count with risk badge."""
    try:
        count = int(count) if isinstance(count, str) else count
    except Exception:
        count = "?"

    if isinstance(count, int):
        if count > 3:
            variant, risk_label = "red", "High context-loss risk"
        elif count > 1:
            variant, risk_label = "amber", "Medium context-loss risk"
        else:
            variant, risk_label = "green", "Low context-loss risk"
        badge = _make_badge(risk_label, variant)
    else:
        badge = _make_badge("Unknown", "slate")

    display = count if isinstance(count, int) else "?"
    st.markdown(f"""
<div class="tc-card">
  <div class="tc-card-label">Rep Transitions</div>
  <div class="tc-card-big-num">{display}</div>
  <div>{badge}</div>
</div>
""", unsafe_allow_html=True)


def render_root_causes_card(causes: any) -> None:
    """Render root cause categories as a styled card."""
    causes_html = _to_html_list(causes)
    st.markdown(f"""
<div class="tc-card">
  <div class="tc-card-label">Root Cause Categories</div>
  <div style="margin-top:.4rem;">{causes_html}</div>
</div>
""", unsafe_allow_html=True)


def render_predicted_outcomes_card(outcomes: any) -> None:
    """Render predicted outcomes if ticket closed prematurely."""
    outcomes_html = _to_html_list(outcomes)
    amber_badge = _make_badge("Closure Risk", "amber")
    st.markdown(f"""
<div class="tc-result-card">
  <div class="tc-result-header">If Closed Prematurely</div>
  <div style="margin-bottom:.6rem;">{amber_badge}</div>
  <div>{outcomes_html}</div>
</div>
""", unsafe_allow_html=True)


# ─── INTERNAL HELPERS ────────────────────────────────────────────────────────

def _format_list_as_markdown(items: any) -> str:
    """Convert a list or string to properly formatted markdown bullets."""
    if isinstance(items, list):
        formatted = []
        for item in items:
            item_str = str(item).strip()
            if item_str and not item_str.startswith("•"):
                formatted.append(f"• {item_str}")
            elif item_str:
                formatted.append(item_str)
        return "\n".join(formatted)
    return str(items).strip()


def _safe_markdown(text: any) -> None:
    """Safely render markdown without character iteration issues."""
    if text is None or (isinstance(text, str) and not text.strip()):
        return
    st.write(str(text).strip())


def _render_section_content(title: str, content: any) -> None:
    """Route content to the appropriate renderer based on section title."""
    if isinstance(content, dict):
        if "sentiment" in title.lower():
            render_sentiment_card(content)
        elif "safe to close" in title.lower():
            render_safe_to_close_card(content)
        elif "escalation" in title.lower():
            render_escalation_card(content)
        elif "continuity" in title.lower():
            render_continuity_failures_card(content)
        else:
            for key, value in content.items():
                _safe_markdown(f"**{key}:** {str(value).strip()}")
    elif isinstance(content, list):
        _safe_markdown(_format_list_as_markdown(content))
    else:
        _safe_markdown(content)
