import streamlit as st

# ── CONFIG ────────────────────────────────────────────────────────────────────
API_KEY          = "YOUR_API_KEY_HERE"
GMAIL_OAUTH_TOKEN = "YOUR_GMAIL_OAUTH_TOKEN"
GMAIL_MCP_URL    = "GMAIL_MCP_URL_HERE"
MODEL            = "claude-sonnet-4-20250514"
APP_TITLE        = "Executive Inbox Intelligence"
APP_SUBTITLE     = "AI-powered urgency ranking tool for executive inboxes."
# ─────────────────────────────────────────────────────────────────────────────

from gmail import fetch_emails
from scoring import score_emails
from actions import generate_reply_draft, build_reply_gmail_url, build_forward_gmail_url

# ── PAGE SETUP ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📬",
    layout="wide",
)

# ── GLOBAL STYLES ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Card container */
.email-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 14px;
    background: #ffffff;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.email-card.ignored {
    opacity: 0.35;
    pointer-events: none;
}
/* Score badge */
.score-badge {
    display: inline-block;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 12px;
    color: white;
    margin-left: 8px;
}
.badge-green  { background-color: #28a745; }
.badge-yellow { background-color: #e6a817; color: #333; }
.badge-red    { background-color: #dc3545; }
/* Dot indicator */
.dot { font-size: 22px; line-height: 1; vertical-align: middle; }
.dot-green  { color: #28a745; }
.dot-yellow { color: #e6a817; }
.dot-red    { color: #dc3545; }
/* Meta row */
.meta { font-size: 13px; color: #555; margin: 4px 0 8px; }
.summary-text { font-size: 14px; margin: 6px 0; }
.reason-text  { font-size: 12px; color: #666; font-style: italic; }
.divider { border-top: 1px solid #f0f0f0; margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ────────────────────────────────────────────────────────
for key, default in [
    ("emails_scored", []),
    ("ignored_ids", set()),
    ("reply_drafts", {}),
    ("fetched", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── HELPERS ───────────────────────────────────────────────────────────────────
COLOR_DOT   = {"green": "dot-green", "yellow": "dot-yellow", "red": "dot-red"}
COLOR_BADGE = {"green": "badge-green", "yellow": "badge-yellow", "red": "badge-red"}


def _esc(text: str) -> str:
    """Minimal HTML escape for user content rendered via unsafe_allow_html."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def tokens_configured() -> bool:
    return (
        API_KEY != "YOUR_ANTHROPIC_API_KEY"
        and GMAIL_OAUTH_TOKEN != "YOUR_GMAIL_OAUTH_TOKEN"
    )

def _filter_emails(emails: list, min_score: int) -> list:
    return [e for e in emails if e.get("urgency_score", 0) >= min_score]

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/HelloFresh_Logo.svg/320px-HelloFresh_Logo.svg.png",
        width=160,
    )
    st.markdown("---")
    st.markdown("**Connection Status**")

    if API_KEY != "YOUR_ANTHROPIC_API_KEY":
        st.success("Claude API — connected")
    else:
        st.error("Claude API — not configured")

    if GMAIL_OAUTH_TOKEN != "YOUR_GMAIL_OAUTH_TOKEN":
        st.success("Gmail MCP — token set")
    else:
        st.error("Gmail MCP — token missing")

    st.markdown("---")
    st.caption("Tokens are set in app.py — never shown in the UI.")
    st.markdown("---")
    st.markdown("**Urgency Legend**")
    st.markdown("🟢 1–3 &nbsp; Low priority")
    st.markdown("🟡 4–6 &nbsp; Medium priority")
    st.markdown("🔴 7–10 &nbsp; High priority")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"## 📬 {APP_TITLE}")
st.markdown(f"*{APP_SUBTITLE}*")
st.markdown("---")

if not tokens_configured():
    st.warning(
        "Add your `API_KEY` and `GMAIL_OAUTH_TOKEN` at the top of `app.py` to get started.",
        icon="⚠️",
    )
    st.stop()

# ── INPUT ROW ─────────────────────────────────────────────────────────────────
col_mode, col_val, col_btn = st.columns([2, 2, 1.5])

with col_mode:
    fetch_mode = st.radio(
        "Fetch by",
        ["Number of emails", "Time range"],
        horizontal=True,
        key="fetch_mode_radio",
    )

with col_val:
    if fetch_mode == "Number of emails":
        fetch_count = st.selectbox("Count", [10, 20, 30, 40], key="count_select")
        fetch_hours = None
    else:
        hours_map = {"Last 2 hours": 2, "Last 4 hours": 4, "Last 7 hours": 7, "Last 24 hours": 24}
        hours_label = st.selectbox("Time range", list(hours_map.keys()), key="hours_select")
        fetch_hours = hours_map[hours_label]
        fetch_count = None

with col_btn:
    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
    fetch_clicked = st.button("Fetch & Score Emails", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── FETCH + SCORE ─────────────────────────────────────────────────────────────
if fetch_clicked:
    st.session_state.emails_scored = []
    st.session_state.ignored_ids = set()
    st.session_state.reply_drafts = {}
    st.session_state.fetched = False

    with st.spinner("Connecting to Gmail and fetching emails…"):
        try:
            raw_emails = fetch_emails(
                api_key=API_KEY,
                oauth_token=GMAIL_OAUTH_TOKEN,
                mcp_url=GMAIL_MCP_URL,
                model=MODEL,
                count=fetch_count,
                hours=fetch_hours,
            )
        except Exception as e:
            st.error(str(e))
            st.stop()

    if not raw_emails:
        st.info("No emails found for the selected range. Try a wider range.", icon="📭")
        st.stop()

    with st.spinner(f"Scoring {len(raw_emails)} emails for urgency…"):
        try:
            scored = score_emails(api_key=API_KEY, model=MODEL, emails=raw_emails)
        except Exception as e:
            st.warning(f"Scoring failed — showing emails without scores. ({e})", icon="⚠️")
            scored = raw_emails

    st.session_state.emails_scored = scored
    st.session_state.fetched = True
    st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if not st.session_state.fetched or not st.session_state.emails_scored:
    if not fetch_clicked:
        st.markdown(
            "<div style='text-align:center;color:#aaa;margin-top:60px;font-size:16px'>"
            "Select a fetch mode above and click <b>Fetch & Score Emails</b> to begin."
            "</div>",
            unsafe_allow_html=True,
        )
    st.stop()

emails_all = st.session_state.emails_scored
total = len(emails_all)

# Filter bar
filter_col, info_col = st.columns([2, 4])
with filter_col:
    score_filter = st.selectbox(
        "Show emails",
        ["All", "Score 4+", "Score 6+", "Score 8+"],
        key="score_filter",
    )
with info_col:
    min_score_map = {"All": 1, "Score 4+": 4, "Score 6+": 6, "Score 8+": 8}
    min_score = min_score_map[score_filter]
    visible = _filter_emails(emails_all, min_score)
    ignored_count = len(st.session_state.ignored_ids)
    st.markdown(
        f"<div style='margin-top:10px;color:#555;font-size:14px'>"
        f"Showing <b>{len(visible)}</b> of <b>{total}</b> emails"
        + (f" &nbsp;|&nbsp; {ignored_count} ignored" if ignored_count else "")
        + "</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

if not visible:
    st.info("No emails match this filter. Try a lower score threshold.", icon="🔍")
    st.stop()

# ── EMAIL CARDS ───────────────────────────────────────────────────────────────
for email in visible:
    eid        = email["id"]
    color      = email.get("color", "green")
    score      = email.get("urgency_score", 0)
    action_sug = email.get("suggested_action", "Reply")
    is_ignored = eid in st.session_state.ignored_ids
    ignored_cls = "ignored" if is_ignored else ""

    # Per-card session state keys
    reply_key    = f"show_reply_{eid}"
    delegate_key = f"show_delegate_{eid}"
    fwd_key      = f"fwd_to_{eid}"
    for k, default in [(reply_key, False), (delegate_key, False), (fwd_key, "")]:
        if k not in st.session_state:
            st.session_state[k] = default

    dot_cls   = COLOR_DOT.get(color, "dot-green")
    badge_cls = COLOR_BADGE.get(color, "badge-green")

    # Card header HTML
    st.markdown(
        f'<div class="email-card {ignored_cls}">'
        f'<span class="dot {dot_cls}">●</span>'
        f'<span class="score-badge {badge_cls}">{score}/10</span>'
        f'&nbsp;&nbsp;<b>{_esc(email["subject"])}</b>'
        f'<div class="meta">From: {_esc(email["sender"])} &lt;{_esc(email["sender_email"])}&gt;'
        f'&nbsp;&nbsp;|&nbsp;&nbsp;{_esc(email.get("timestamp",""))}</div>'
        f'<div class="summary-text">{_esc(email.get("summary",""))}</div>'
        f'<div class="reason-text">Reason: {_esc(email.get("urgency_reason",""))}</div>'
        f'<div class="reason-text">Suggested action: <b>{action_sug}</b></div>'
        f'<div class="divider"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not is_ignored:
        a_col, b_col, c_col, _ = st.columns([1.2, 1.2, 1, 4])

        with a_col:
            if st.button("Reply", key=f"reply_btn_{eid}", use_container_width=True):
                st.session_state[reply_key] = not st.session_state[reply_key]
                st.session_state[delegate_key] = False
        with b_col:
            if st.button("Delegate", key=f"delegate_btn_{eid}", use_container_width=True):
                st.session_state[delegate_key] = not st.session_state[delegate_key]
                st.session_state[reply_key] = False
        with c_col:
            if st.button("Ignore", key=f"ignore_btn_{eid}", use_container_width=True):
                st.session_state.ignored_ids.add(eid)
                st.rerun()

        # Reply panel
        if st.session_state[reply_key]:
            with st.container(border=True):
                st.markdown("**Draft Reply**")
                if eid not in st.session_state.reply_drafts:
                    with st.spinner("Drafting reply…"):
                        try:
                            draft = generate_reply_draft(API_KEY, MODEL, email)
                            st.session_state.reply_drafts[eid] = draft
                        except Exception as e:
                            st.error(str(e))
                            st.session_state.reply_drafts[eid] = ""
                draft = st.session_state.reply_drafts.get(eid, "")
                edited = st.text_area(
                    "Edit before sending",
                    value=draft,
                    height=150,
                    key=f"reply_text_{eid}",
                )
                gmail_url = build_reply_gmail_url(email, edited)
                st.link_button("Open Draft in Gmail →", url=gmail_url, type="primary")

        # Delegate panel
        if st.session_state[delegate_key]:
            with st.container(border=True):
                st.markdown("**Forward to a colleague**")
                fwd_to = st.text_input(
                    "Recipient email address",
                    placeholder="colleague@hellofresh.com",
                    key=fwd_key,
                )
                if fwd_to.strip():
                    fwd_gmail_url = build_forward_gmail_url(email, fwd_to)
                    st.link_button("Forward in Gmail →", url=fwd_gmail_url, type="primary")
                else:
                    st.caption("Enter a recipient email address above.")

    st.markdown("")  # spacing
