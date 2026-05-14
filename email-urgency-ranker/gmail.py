import json
import re
import base64
from datetime import datetime, timedelta, timezone
import requests


GMAIL_API = "https://gmail.googleapis.com/gmail/v1/users/me"


def fetch_emails(api_key: str, oauth_token: str, mcp_url: str, model: str,
                 count: int = None, hours: int = None) -> list[dict]:
    """
    Fetch emails from Gmail REST API.
    Provide either count or hours, not both.
    """
    if not count and not hours:
        raise ValueError("Provide either count or hours.")

    headers = {"Authorization": f"Bearer {oauth_token}"}

    params = {"maxResults": count or 100}
    if hours:
        after_ts = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp())
        params["q"] = f"after:{after_ts}"

    try:
        r = requests.get(f"{GMAIL_API}/messages", headers=headers, params=params, timeout=15)
        _raise_for_status(r)
        data = r.json()
    except Exception as e:
        raise Exception(str(e))

    messages = data.get("messages", [])
    if not messages:
        return []

    emails = []
    for msg in messages:
        try:
            detail = _get_message(msg["id"], headers)
            if detail:
                emails.append(detail)
        except Exception:
            continue

    return emails


def _get_message(msg_id: str, headers: dict) -> dict | None:
    r = requests.get(
        f"{GMAIL_API}/messages/{msg_id}",
        headers=headers,
        params={"format": "full"},
        timeout=15,
    )
    _raise_for_status(r)
    data = r.json()

    payload = data.get("payload", {})
    hdrs = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

    subject    = hdrs.get("subject", "(no subject)")
    sender_raw = hdrs.get("from", "Unknown")
    reply_to   = hdrs.get("reply-to", sender_raw)
    date_raw   = hdrs.get("date", "")
    sender, sender_email = _parse_sender(sender_raw)
    _, reply_to_email    = _parse_sender(reply_to)

    body = _extract_body(payload)

    return {
        "id":           msg_id,
        "sender":       sender,
        "sender_email": sender_email,
        "subject":      subject,
        "body_preview": body[:500],
        "timestamp":    date_raw,
        "thread_id":    data.get("threadId", ""),
        "reply_to":     reply_to_email or sender_email,
    }


def _extract_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    mime = payload.get("mimeType", "")

    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return _decode_b64(data)

    if mime.startswith("multipart/"):
        for part in payload.get("parts", []):
            text = _extract_body(part)
            if text:
                return text

    return ""


def _decode_b64(data: str) -> str:
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    except Exception:
        return ""


def _parse_sender(raw: str) -> tuple[str, str]:
    """Parse 'Display Name <email@example.com>' into (name, email)."""
    raw = raw.strip()
    match = re.match(r"^(.*?)\s*<([^>]+)>$", raw)
    if match:
        name  = match.group(1).strip().strip('"')
        email = match.group(2).strip()
        return name or email, email
    if "@" in raw:
        return raw, raw
    return raw, ""


def _raise_for_status(r: requests.Response):
    if r.status_code == 401:
        raise Exception("Gmail OAuth token is invalid or expired. Generate a new token and paste it into app.py.")
    if r.status_code == 403:
        raise Exception("Gmail access denied. Make sure your OAuth token includes the https://mail.google.com/ scope.")
    if not r.ok:
        raise Exception(f"Gmail API error {r.status_code}: {r.text[:200]}")
