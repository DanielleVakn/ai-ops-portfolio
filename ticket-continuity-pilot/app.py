import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from io import StringIO

load_dotenv()

from analysis import (
    analyze_ticket,
    generate_manager_briefing,
    batch_analyze_tickets,
    filter_unsafe_tickets,
    export_results_to_csv,
)
from ui_helpers import (
    inject_custom_css,
    render_header,
    render_result_section,
    render_metrics,
    render_continuity_failures_card,
    render_rep_transitions_card,
    render_root_causes_card,
    render_predicted_outcomes_card,
    render_safe_to_close_card,
    render_escalation_card,
    _make_badge,
    _verdict_to_variant,
    _variant_to_hex,
)

st.set_page_config(
    page_title="Ticket Copilot",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_custom_css()

# Initialize session state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "ticket_input" not in st.session_state:
    st.session_state.ticket_input = ""
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None
if "unsafe_tickets" not in st.session_state:
    st.session_state.unsafe_tickets = None

render_header()

# Mode selection tabs
tab1, tab2 = st.tabs(["🎟️ Single Ticket", "📊 Batch Analysis"])

# ==================== SINGLE TICKET MODE ====================
with tab1:
    col1, col2 = st.columns([2, 1], gap="medium")

    with col1:
        st.markdown('<div class="tc-section-label">Ticket Input</div>', unsafe_allow_html=True)

        input_method = st.radio(
            "Input method",
            ["Paste text", "Upload file"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if input_method == "Paste text":
            ticket_text = st.text_area(
                "Paste ticket conversation",
                height=300,
                placeholder="Paste customer support ticket history here...",
                label_visibility="collapsed",
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload ticket",
                type=["txt", "md"],
                label_visibility="collapsed",
            )
            ticket_text = ""
            if uploaded_file:
                ticket_text = uploaded_file.read().decode("utf-8")
                st.success(f"Loaded: {uploaded_file.name}")

        st.session_state.ticket_input = ticket_text

    with col2:
        st.markdown('<div class="tc-section-label">Settings</div>', unsafe_allow_html=True)
        api_provider = st.selectbox(
            "API Provider",
            ["Anthropic", "OpenAI"],
            label_visibility="collapsed",
        )
        st.session_state.api_provider = api_provider
        st.info("Uses Claude Opus for fast, accurate analysis", icon="ℹ️")

    # Analysis button
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        analyze_button = st.button(
            "🔍 Analyze Ticket",
            key="analyze_btn",
            use_container_width=True,
            type="primary",
        )

    with col2:
        if st.session_state.analysis_result:
            clear_button = st.button("Clear", key="clear_btn", use_container_width=True)
            if clear_button:
                st.session_state.analysis_result = None
                st.rerun()

    # Trigger analysis
    if analyze_button:
        if not ticket_text.strip():
            st.error("Please provide ticket content to analyze")
        else:
            with st.spinner("🤖 Analyzing ticket..."):
                try:
                    result = analyze_ticket(
                        ticket_text,
                        provider=st.session_state.get("api_provider", "Anthropic"),
                    )
                    st.session_state.analysis_result = result
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

    # Display results
    if st.session_state.analysis_result:
        st.divider()
        result = st.session_state.analysis_result

        # ── Key Metrics
        st.markdown('<div class="tc-section-label">Key Metrics</div>', unsafe_allow_html=True)
        render_metrics(result)

        st.divider()

        # ── Quick Actions
        st.markdown('<div class="tc-section-label">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("📋 Generate Manager Briefing", use_container_width=True, type="primary"):
            briefing = generate_manager_briefing(result)
            st.markdown(briefing)
            st.divider()

        # ── Executive Summary
        st.markdown('<div class="tc-section-label">Executive Summary</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1.5, 1])

        with col1:
            render_result_section("Summary", result.get("summary"), collapsible=False)

        with col2:
            render_result_section(
                "Customer Sentiment",
                result.get("sentiment"),
                collapsible=False,
            )

        st.divider()

        # ── Continuity Analysis
        st.markdown('<div class="tc-section-label">Continuity Analysis</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            render_continuity_failures_card(result.get("continuity_failures", {}))

        with col2:
            render_rep_transitions_card(result.get("rep_transition_count", "?"))

        with col3:
            render_root_causes_card(result.get("root_causes", ""))

        st.divider()

        # ── Issues & Actions
        st.markdown('<div class="tc-section-label">Issues & Actions</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            render_result_section(
                "⚠️ Unresolved Issues",
                result.get("unresolved_issues"),
                collapsible=True,
                expanded=True,
            )

        with col2:
            render_result_section(
                "🎯 Recommended Actions",
                result.get("recommended_actions"),
                collapsible=True,
                expanded=True,
            )

        st.divider()

        # ── Risk Assessment
        st.markdown('<div class="tc-section-label">Risk Assessment</div>', unsafe_allow_html=True)
        render_predicted_outcomes_card(result.get("predicted_outcomes_if_closed"))

        st.divider()

        # ── Handoff Information
        st.markdown('<div class="tc-section-label">Handoff Information</div>', unsafe_allow_html=True)
        render_result_section(
            "🤝 Handoff Summary for Next Rep",
            result.get("handoff_summary"),
            collapsible=True,
            expanded=True,
        )

        st.divider()

        # ── Safety & Risk Assessment
        st.markdown('<div class="tc-section-label">Safety & Risk Assessment</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                '<div class="tc-result-header">Safe to Close Assessment</div>',
                unsafe_allow_html=True,
            )
            render_safe_to_close_card(result.get("safe_to_close", {}))

        with col2:
            st.markdown(
                '<div class="tc-result-header">Escalation Risk</div>',
                unsafe_allow_html=True,
            )
            render_escalation_card(result.get("escalation_risk", {}))

        st.divider()

        # ── Additional Context
        st.markdown('<div class="tc-section-label">Additional Context</div>', unsafe_allow_html=True)
        render_result_section(
            "📋 Detailed Analysis",
            result.get("detailed_context"),
            collapsible=True,
            expanded=False,
        )


# ==================== BATCH ANALYSIS MODE ====================
with tab2:
    st.markdown('<div class="tc-section-label">Batch Ticket Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:.9rem;color:#64748b;margin-bottom:1rem;">'
        'Upload a CSV file with tickets and filter for unsafe-to-close cases.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            '<div style="font-size:.8rem;font-weight:600;color:#64748b;margin-bottom:.35rem;">'
            'CSV FORMAT REQUIRED</div>'
            '<div style="font-size:.85rem;color:#94a3b8;margin-bottom:.75rem;">'
            'Columns: <code>id</code>, <code>content</code> (ticket text)</div>',
            unsafe_allow_html=True,
        )
        batch_file = st.file_uploader(
            "Upload CSV file with tickets",
            type=["csv"],
            label_visibility="collapsed",
        )

    with col2:
        st.markdown(
            '<div style="font-size:.8rem;font-weight:600;color:#64748b;margin-bottom:.5rem;">'
            'SETTINGS</div>',
            unsafe_allow_html=True,
        )
        batch_api_provider = st.selectbox(
            "API Provider",
            ["Anthropic", "OpenAI"],
            key="batch_provider",
            label_visibility="collapsed",
        )

    if batch_file:
        st.divider()

        try:
            df = pd.read_csv(batch_file)

            if "id" not in df.columns or "content" not in df.columns:
                st.error("❌ CSV must have 'id' and 'content' columns")
            else:
                st.success(f"✅ Loaded {len(df)} tickets")
                tickets = df.to_dict("records")

                if st.button(
                    f"🔍 Analyze {len(tickets)} Tickets",
                    use_container_width=True,
                    type="primary",
                ):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def progress_callback(current, total):
                        progress_bar.progress(current / total)
                        status_text.text(f"Analyzing {current}/{total}...")

                    with st.spinner(f"Analyzing {len(tickets)} tickets..."):
                        try:
                            results = batch_analyze_tickets(
                                tickets,
                                provider=batch_api_provider,
                                progress_callback=progress_callback,
                            )
                            st.session_state.batch_results = results
                            unsafe = filter_unsafe_tickets(results)
                            st.session_state.unsafe_tickets = unsafe
                            progress_bar.empty()
                            status_text.empty()
                        except Exception as e:
                            st.error(f"Batch analysis failed: {str(e)}")

        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")

    # Display batch results
    if st.session_state.unsafe_tickets is not None:
        st.divider()

        unsafe = st.session_state.unsafe_tickets
        total_results = len(st.session_state.batch_results)
        pct = int((len(unsafe) / total_results) * 100) if total_results > 0 else 0

        # Batch summary banner
        if len(unsafe) > 0:
            banner_color = "#ef4444"
            banner_badge = _make_badge("Requires Attention", "red")
        else:
            banner_color = "#22c55e"
            banner_badge = _make_badge("All Clear", "green")

        st.markdown(f"""
<div class="tc-batch-banner" style="border-left:4px solid {banner_color};">
  <div>
    <span class="tc-batch-banner-num" style="color:{banner_color};">{len(unsafe)}</span>
    <span class="tc-batch-banner-total">/{total_results}</span>
  </div>
  <div class="tc-batch-banner-meta">
    <div class="tc-batch-banner-label">Batch Analysis Results</div>
    <div style="margin:.25rem 0 .35rem;">{banner_badge}</div>
    <div class="tc-batch-banner-desc">
      {pct}% of tickets flagged as unsafe to close
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        if len(unsafe) == 0:
            st.success("✅ All tickets are safe to close!")
        else:
            # Summary table
            st.markdown(
                '<div class="tc-section-label">Risk Summary</div>',
                unsafe_allow_html=True,
            )
            summary_data = []
            for result in unsafe:
                safe_to_close = result.get("safe_to_close", {})
                escalation = result.get("escalation_risk", {})
                summary_data.append({
                    "Ticket ID": result.get("id", ""),
                    "Summary": result.get("summary", "")[:80],
                    "Sentiment": result.get("sentiment", {}).get("score", "?"),
                    "Escalation": escalation.get("level", "?") if isinstance(escalation, dict) else "?",
                    "Rep Transitions": result.get("rep_transition_count", "?"),
                    "Safe to Close": safe_to_close.get("verdict", "?") if isinstance(safe_to_close, dict) else "?",
                })

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)

            # Export
            st.divider()
            if st.button("📥 Export Results to CSV", use_container_width=True):
                csv_buffer = StringIO()
                summary_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_buffer.getvalue(),
                    file_name="unsafe_tickets_report.csv",
                    mime="text/csv",
                )

            # Detailed view
            st.markdown(
                '<div class="tc-section-label">Detailed Unsafe Tickets</div>',
                unsafe_allow_html=True,
            )
            for i, result in enumerate(unsafe, 1):
                summary_snippet = result.get("summary", "")[:60]
                with st.expander(f"{result.get('id')} — {summary_snippet}...", expanded=False):
                    escal = result.get("escalation_risk", {})
                    safe = result.get("safe_to_close", {})

                    # Badge row
                    escal_level = escal.get("level", "?").upper() if isinstance(escal, dict) else "?"
                    escal_variant = _verdict_to_variant(escal_level, mode="risk")
                    unsafe_badge = _make_badge("Unsafe to Close", "red")
                    escal_badge = _make_badge(f"{escal_level} Escalation", escal_variant)
                    st.markdown(
                        f'<div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:.75rem;">'
                        f'{unsafe_badge}{escal_badge}</div>',
                        unsafe_allow_html=True,
                    )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Escalation Risk", escal_level)
                    with col2:
                        st.metric("Sentiment", result.get("sentiment", {}).get("score", "?"))
                    with col3:
                        st.metric("Rep Transitions", result.get("rep_transition_count", "?"))

                    st.markdown("**Why Not Safe to Close:**")
                    st.markdown(safe.get("reasoning", "N/A") if isinstance(safe, dict) else "N/A")

                    st.markdown("**Recommended Actions:**")
                    st.markdown(result.get("recommended_actions", "N/A"))
