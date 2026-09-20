from Common.data import load_inbox


NOISE_DOMAINS = {
    "dropbox.com", "slack.com", "vercel.com", "amazon.com",
    "netflix.com", "apple.com", "spotify.com", "coursera.org",
    "lyft.com", "figma.com", "bluebottlecoffee.com",
    "pagerduty.com", "producthunt.com", "accounts.google.com",
    "postmarkapp.com", "datadoghq.com", "mailchimp.com",
    "zoom.us", "digitalocean.com", "twitter.com", "medium.com",
    "substack.com", "intercom.io", "chase.com", "robinhood.com",
    "doordash.com", "todoist.com", "hackernewsletter.com",
    "uber.com", "namecheap.com", "linkedin.com", "grammarly.com",
    "united.com",
}

NOISE_KEYWORDS = {
    "receipt", "invoice paid", "invoice from", "monthly invoice",
    "usage report", "weekly report", "daily digest",
    "campaign report", "account statement", "verification code",
    "screen time report", "your order", "your bill",
    "your monthly", "your weekly", "your daily",
    "new notifications", "new login", "new sign-in",
    "cloud recording is ready", "monitor ok again",
    "incident resolved", "payout is on the way",
}

SECURITY_KEYWORDS = {
    "password", "security", "sign-in", "login",
    "verification code", "account was changed",
}


def _domain(sender):
    return sender.lower().split("@", 1)[-1] if "@" in sender else ""


def _contains(message, keywords):
    text = (
        message.get("subject", "") + " " +
        message.get("body", "")
    ).lower()

    return any(word in text for word in keywords)


def classify_by_rule(message):
    if _contains(message, SECURITY_KEYWORDS):
        return None

    if (
        _domain(message.get("from", "")) in NOISE_DOMAINS
        and _contains(message, NOISE_KEYWORDS)
    ):
        return {
            "handled_by_rule": True,
            "disposition": "archive",
            "reason": "Automated receipt, report or notification.",
            "rule": "automated_noise",
        }

    return None


def classify_inbox_by_rules():
    results = []

    for message in load_inbox():
        decision = classify_by_rule(message)

        if decision:
            results.append({
                "message_id": message["id"],
                **decision,
            })

    return results


if __name__ == "__main__":
    results = classify_inbox_by_rules()
    print(f"Rule-handled messages: {len(results)}")

    for item in results:
        print(
            f"{item['message_id']}: "
            f"{item['disposition']} - {item['reason']}"
        )