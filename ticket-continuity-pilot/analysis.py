import json
import os
import csv
from prompts import TICKET_ANALYSIS_PROMPT


def analyze_ticket(ticket_content: str, provider: str = "Anthropic") -> dict:
    """
    Analyze a support ticket using Claude API and return structured results.

    Args:
        ticket_content: The ticket conversation/history text
        provider: "Anthropic" or "OpenAI"

    Returns:
        Dictionary with analysis results
    """
    if provider == "Anthropic":
        return _analyze_with_anthropic(ticket_content)
    elif provider == "OpenAI":
        return _analyze_with_openai(ticket_content)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _analyze_with_anthropic(ticket_content: str) -> dict:
    """Call Claude API for ticket analysis."""
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in .env file")

    client = Anthropic(api_key=api_key)

    prompt = TICKET_ANALYSIS_PROMPT.format(ticket_content=ticket_content)

    message = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract JSON from response
    response_text = message.content[0].text
    result = _parse_json_response(response_text)

    return result


def _analyze_with_openai(ticket_content: str) -> dict:
    """Call OpenAI API for ticket analysis."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = TICKET_ANALYSIS_PROMPT.format(ticket_content=ticket_content)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=2000
    )

    response_text = response.choices[0].message.content
    result = _parse_json_response(response_text)

    return result


def _parse_json_response(response_text: str) -> dict:
    """
    Extract and parse JSON from model response.
    Handles cases where JSON is wrapped in markdown code blocks.
    """
    text = response_text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse API response as JSON: {str(e)}\n\nResponse: {text[:500]}")

    return result


def format_sentiment(sentiment_data: dict) -> str:
    """Format sentiment data for display."""
    if isinstance(sentiment_data, str):
        return sentiment_data

    score = sentiment_data.get("score", "N/A")
    overall = sentiment_data.get("overall", "unknown").upper()
    indicators = sentiment_data.get("key_indicators", "")

    return f"""
**Overall:** {overall} ({score}/10)

**Key Indicators:** {indicators}
"""


def format_safe_to_close(data: dict) -> str:
    """Format safe to close assessment for display."""
    if isinstance(data, str):
        return data

    verdict = data.get("verdict", "UNKNOWN").upper()
    confidence = data.get("confidence", "unknown").upper()
    reasoning = data.get("reasoning", "")

    return f"""
**Verdict:** {verdict}
**Confidence:** {confidence}

{reasoning}
"""


def format_escalation_risk(data: dict) -> str:
    """Format escalation risk assessment for display."""
    if isinstance(data, str):
        return data

    level = data.get("level", "UNKNOWN").upper()
    reasoning = data.get("reasoning", "")
    actions = data.get("required_actions_to_prevent", "")

    return f"""
**Level:** {level}

**Risk Factors:**
{reasoning}

**Prevention Actions:**
{actions}
"""


def batch_analyze_tickets(tickets: list, provider: str = "Anthropic", progress_callback=None) -> list:
    """
    Analyze multiple tickets and return results.

    Args:
        tickets: List of dicts with 'id' and 'content' keys
        provider: "Anthropic" or "OpenAI"
        progress_callback: Function to call with (current, total) for progress tracking

    Returns:
        List of analysis results with ticket IDs
    """
    results = []

    for idx, ticket in enumerate(tickets):
        if progress_callback:
            progress_callback(idx + 1, len(tickets))

        try:
            ticket_id = ticket.get("id", f"Ticket-{idx+1}")
            ticket_content = ticket.get("content", "")

            if not ticket_content.strip():
                results.append({
                    "id": ticket_id,
                    "error": "Empty ticket content",
                    "safe_to_close": None,
                })
                continue

            result = analyze_ticket(ticket_content, provider)
            result["id"] = ticket_id
            results.append(result)

        except Exception as e:
            results.append({
                "id": ticket.get("id", f"Ticket-{idx+1}"),
                "error": str(e),
                "safe_to_close": None,
            })

    return results


def filter_unsafe_tickets(results: list) -> list:
    """Filter analysis results to only those marked as NOT safe to close."""
    unsafe = []

    for result in results:
        if result.get("error"):
            continue

        safe_to_close = result.get("safe_to_close", {})
        if isinstance(safe_to_close, dict):
            verdict = safe_to_close.get("verdict", "").lower()
            if verdict == "no":
                unsafe.append(result)

    return unsafe


def export_results_to_csv(results: list, filepath: str) -> None:
    """Export unsafe ticket results to CSV."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Ticket ID",
            "Summary",
            "Escalation Level",
            "Safe to Close",
            "Confidence",
            "Rep Transitions",
            "Continuity Issues",
            "Recommended Actions"
        ])

        for result in results:
            safe_to_close = result.get("safe_to_close", {})
            verdict = safe_to_close.get("verdict", "?") if isinstance(safe_to_close, dict) else "?"
            confidence = safe_to_close.get("confidence", "?") if isinstance(safe_to_close, dict) else "?"

            escalation = result.get("escalation_risk", {})
            escalation_level = escalation.get("level", "?") if isinstance(escalation, dict) else "?"

            continuity = result.get("continuity_failures", {})
            continuity_detected = continuity.get("detected", "no") if isinstance(continuity, dict) else "no"

            writer.writerow([
                result.get("id", ""),
                result.get("summary", "")[:100],
                escalation_level,
                verdict,
                confidence,
                result.get("rep_transition_count", "?"),
                continuity_detected,
                str(result.get("recommended_actions", ""))[:200],
            ])


def generate_manager_briefing(result: dict) -> str:
    """Generate a 30-second executive briefing for managers."""
    summary = str(result.get("summary", "")).strip()
    sentiment_score = str(result.get("sentiment", {}).get("score", "?")).strip()
    safe_to_close = str(result.get("safe_to_close", {}).get("verdict", "unknown")).strip().upper()
    escalation_level = str(result.get("escalation_risk", {}).get("level", "unknown")).strip().upper()
    rep_count = str(result.get("rep_transition_count", "?")).strip()
    continuity = result.get("continuity_failures", {})
    recommended = str(result.get("recommended_actions", "")).strip()

    lines = [
        "### 30-Second Manager Briefing",
        "",
        f"**Status:** {summary}",
        "",
        "**Risk Profile:**",
        f"- Customer Sentiment: {sentiment_score}/10",
        f"- Escalation Risk: {escalation_level}",
        f"- Rep Transitions: {rep_count}",
        f"- Safe to Close: {safe_to_close}",
        "",
    ]

    if isinstance(continuity, dict) and continuity.get("detected") == "yes":
        issues = str(continuity.get("issues", "")).strip()
        lines.extend([
            "**⚠️ Continuity Issues Detected:**",
            issues,
            "",
        ])

    lines.extend([
        "**Immediate Action Required:**",
        recommended,
        "",
        "---",
        "*Generated by Ticket Continuity Copilot*",
    ])

    return "\n".join(lines)
