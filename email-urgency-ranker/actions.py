import urllib.parse
import anthropic

REPLY_SYSTEM = """You are an executive assistant drafting concise, professional email replies
on behalf of the President of 'COMPANY'S_NAME'.
Write in first person, confident and warm.
Maximum 3 sentences. No sign-off needed — the user will add their name."""

GMAIL_COMPOSE = "https://mail.google.com/mail/?view=cm&fs=1"


def generate_reply_draft(api_key: str, model: str, email: dict) -> str:
    """Ask Claude to draft a short reply for the given email."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = (
        f"Draft a reply to this email.\n\n"
        f"From: {email['sender']} <{email['sender_email']}>\n"
        f"Subject: {email['subject']}\n"
        f"Body: {email['body_preview']}\n\n"
        f"Urgency context: {email.get('urgency_reason', '')}\n"
        "Write only the reply body — no greeting, no sign-off."
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=512,
            system=REPLY_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except anthropic.AuthenticationError:
        raise Exception("Anthropic API key is invalid.")
    except anthropic.APIConnectionError:
        raise Exception("Could not reach the Anthropic API. Check your internet connection.")
    except anthropic.APIError as e:
        raise Exception(f"Could not generate reply draft: {str(e)}")


def build_reply_gmail_url(email: dict, reply_text: str) -> str:
    """Return a Gmail compose URL pre-filled for a reply."""
    to      = email.get("reply_to") or email.get("sender_email", "")
    subject = f"Re: {email.get('subject', '')}"
    params  = urllib.parse.urlencode({"to": to, "su": subject, "body": reply_text})
    return f"{GMAIL_COMPOSE}&{params}"


def build_forward_gmail_url(email: dict, recipient_email: str) -> str:
    """Return a Gmail compose URL pre-filled for a forward."""
    forward_body = (
        f"---------- Forwarded message ----------\n"
        f"From: {email.get('sender', '')} <{email.get('sender_email', '')}>\n"
        f"Subject: {email.get('subject', '')}\n"
        f"Date: {email.get('timestamp', '')}\n\n"
        f"{email.get('body_preview', '')}"
    )
    params = urllib.parse.urlencode({
        "to":   recipient_email.strip(),
        "su":   f"Fwd: {email.get('subject', '')}",
        "body": forward_body,
    })
    return f"{GMAIL_COMPOSE}&{params}"
