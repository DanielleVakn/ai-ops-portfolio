import json
import re
import anthropic

SYSTEM_PROMPT = """You are an executive assistant to the President of 'COMPANY'S NAME'.
Your job is to score emails by urgency and recommend the right action.

Scoring rubric (1–10):
- 9–10: Immediate CEO/board-level crisis, legal emergency, system outage with revenue impact
- 7–8: C-suite request, same-day deadline, investor or major partner escalation
- 5–6: Important but not time-critical: internal strategy, key partner comms, hiring decisions
- 3–4: FYI updates, routine reports, low-urgency requests from direct reports
- 1–2: Newsletters, automated notifications, cold outreach, non-actionable updates

Suggested action rules:
- Reply: Sender expects a personal response from the President
- Delegate: Can be handled by a direct report or EA
- Ignore: No action required

Return ONLY a JSON array. No markdown, no explanation."""


def score_emails(api_key: str, model: str, emails: list[dict]) -> list[dict]:
    """
    Score a list of emails for urgency using Claude.
    Returns the same list with added keys:
      urgency_score, summary, urgency_reason, suggested_action, color
    Sorted descending by urgency_score.
    """
    if not emails:
        return []

    client = anthropic.Anthropic(api_key=api_key)

    email_payload = [
        {
            "index": i,
            "id": e["id"],
            "sender": e["sender"],
            "sender_email": e["sender_email"],
            "subject": e["subject"],
            "body_preview": e["body_preview"],
            "timestamp": e["timestamp"],
        }
        for i, e in enumerate(emails)
    ]

    prompt = (
        "Score each email below. Return a JSON array where each object has:\n"
        "  index (int), id (string), urgency_score (int 1-10), "
        "summary (one sentence), urgency_reason (one sentence), "
        "suggested_action ('Reply' | 'Delegate' | 'Ignore')\n\n"
        f"Emails:\n{json.dumps(email_payload, indent=2)}"
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError:
        raise Exception("Anthropic API key is invalid.")
    except anthropic.APIConnectionError:
        raise Exception("Could not reach the Anthropic API. Check your internet connection.")
    except anthropic.APIError as e:
        raise Exception(f"Scoring API error: {str(e)}")

    raw_text = _extract_text(response)
    scores = _parse_json_array(raw_text)

    scored_map = {}
    for s in scores:
        if not isinstance(s, dict):
            continue
        idx = s.get("index")
        if idx is None:
            idx = s.get("id")
        scored_map[str(idx)] = s

    result = []
    for i, email in enumerate(emails):
        score_data = scored_map.get(str(i)) or scored_map.get(email["id"]) or {}
        urgency = int(score_data.get("urgency_score", 5))
        urgency = max(1, min(10, urgency))
        enriched = {
            **email,
            "urgency_score": urgency,
            "summary": str(score_data.get("summary", "No summary available.")),
            "urgency_reason": str(score_data.get("urgency_reason", "Score estimated.")),
            "suggested_action": _validate_action(score_data.get("suggested_action", "Reply")),
            "color": _urgency_color(urgency),
        }
        result.append(enriched)

    result.sort(key=lambda e: e["urgency_score"], reverse=True)
    return result


def _validate_action(action: str) -> str:
    valid = {"Reply", "Delegate", "Ignore"}
    return action if action in valid else "Reply"


def _urgency_color(score: int) -> str:
    if score <= 3:
        return "green"
    if score <= 6:
        return "yellow"
    return "red"


def _extract_text(response) -> str:
    return " ".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()


def _parse_json_array(text: str) -> list:
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    raise Exception("Could not parse scoring results. Showing emails unscored.")
