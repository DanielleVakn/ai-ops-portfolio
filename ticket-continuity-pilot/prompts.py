TICKET_ANALYSIS_PROMPT = """Analyze this support ticket and provide structured insights. Be concise and direct.

TICKET:
{ticket_content}

Output JSON (no markdown, no code blocks):

{{
    "summary": "2-3 sentence executive summary",
    "unresolved_issues": "List of open issues. Format: '• Issue: description'",
    "sentiment": {{
        "overall": "positive|neutral|negative",
        "score": "1-10",
        "key_indicators": "Brief drivers (tone, language, satisfaction)"
    }},
    "handoff_summary": "What next rep needs to know and what's been tried",
    "recommended_actions": "Numbered action list. Format: '1. Action: recommendation'",
    "detailed_context": "Timeline, failed solutions, technical details",
    "safe_to_close": {{
        "verdict": "yes|no|maybe",
        "confidence": "high|medium|low",
        "reasoning": "Why? What's needed to close safely?"
    }},
    "escalation_risk": {{
        "level": "low|medium|high",
        "reasoning": "Why might escalate? Frustration patterns?",
        "required_actions_to_prevent": "Must-do actions to prevent escalation"
    }},
    "continuity_failures": {{
        "detected": "yes|no",
        "count": "Number found",
        "issues": "Continuity breakdowns. Format: '• Pattern: description'"
    }},
    "rep_transition_count": "Total reps who handled this",
    "root_causes": "Root cause categories. Format: '• Category: description'",
    "predicted_outcomes_if_closed": "Negative outcomes if closed early. Format: '• Outcome: description'"
}}

Rules:
- Be conservative on safe_to_close (keep open if unsure)
- Count reps accurately
- Flag lost context patterns
- Be actionable"""
