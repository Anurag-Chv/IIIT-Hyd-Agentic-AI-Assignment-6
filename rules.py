"""
Rule-based routing for obvious inbox messages.
Messages that are clearly just noise can bypass the LLM.
"""

from Common.data import load_inbox


# These are common senders/categories that are usually automated.
NOISE_DOMAINS = {
    "dropbox.com",
    "slack.com",
    "vercel.com",
    "amazon.com",
    "netflix.com",
    "apple.com",
    "spotify.com",
    "coursera.org",
    "lyft.com",
    "figma.com",
    "bluebottlecoffee.com",
    "pagerduty.com",
    "producthunt.com",
    "accounts.google.com",
    "postmarkapp.com",
    "datadoghq.com",
    "mailchimp.com",
    "zoom.us",
    "digitalocean.com",
    "twitter.com",
    "medium.com",
    "substack.com",
    "intercom.io",
    "chase.com",
    "robinhood.com",
    "doordash.com",
    "todoist.com",
    "hackernewsletter.com",
    "uber.com",
    "namecheap.com",
    "linkedin.com",
    "grammarly.com",
    "united.com",
}


def _sender_domain(sender: str) -> str:
    """Return the domain part of an email address."""
    if "@" not in sender:
        return ""

    return sender.split("@", 1)[1].lower()


def _looks_like_receipt_or_notification(message: dict) -> bool:
    """Check for obvious automated mail."""
    subject = message.get("subject", "").lower()
    body = message.get("body", "").lower()

    keywords = [
        "receipt",
        "invoice paid",
        "invoice from",
        "monthly invoice",
        "usage report",
        "weekly report",
        "daily digest",
        "campaign report",
        "account statement",
        "verification code",
        "screen time report",
        "your order",
        "your bill",
        "your monthly",
        "your weekly",
        "your daily",
        "new notifications",
        "new login",
        "new sign-in",
        "cloud recording is ready",
        "monitor ok again",
        "incident resolved",
        "payout is on the way",
    ]

    return any(
        keyword in subject or keyword in body
        for keyword in keywords
    )


def _looks_like_security_alert(message: dict) -> bool:
    """
    Security-related mail should not be automatically archived.
    """
    subject = message.get("subject", "").lower()
    body = message.get("body", "").lower()

    keywords = [
        "password",
        "security",
        "sign-in",
        "login",
        "verification code",
        "account was changed",
    ]

    return any(
        keyword in subject or keyword in body
        for keyword in keywords
    )


def classify_by_rule(message: dict) -> dict | None:
    """
    Return a rule-based decision for obvious noise.

    Returns None when the message should go to the model path.
    """
    sender = message.get("from", "")
    domain = _sender_domain(sender)

    # Never auto-archive security-related messages.
    if _looks_like_security_alert(message):
        return None

    if domain in NOISE_DOMAINS:
        if _looks_like_receipt_or_notification(message):
            return {
                "handled_by_rule": True,
                "disposition": "archive",
                "reason": "Automated receipt, report or notification.",
                "rule": "automated_noise",
            }

    return None


def classify_inbox_by_rules() -> list:
    """
    Run the rules against the complete inbox.

    Returns only messages handled by rules.
    """
    decisions = []

    for message in load_inbox():
        decision = classify_by_rule(message)

        if decision is not None:
            decisions.append(
                {
                    "message_id": message["id"],
                    **decision,
                }
            )

    return decisions


if __name__ == "__main__":
    results = classify_inbox_by_rules()

    print(f"Rule-handled messages: {len(results)}")

    for result in results:
        print(
            f"{result['message_id']}: "
            f"{result['disposition']} - "
            f"{result['reason']}"
        )