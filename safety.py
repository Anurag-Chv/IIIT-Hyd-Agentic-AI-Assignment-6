"""
Safety gate for irreversible InboxHero actions.
"""

from trace import log_event


IRREVERSIBLE_ACTIONS = {"send", "delete"}


def require_approval(
    action: str,
    message_id: str,
    details=None,
    dry_run: bool = False,
) -> bool:
    """
    Check whether an irreversible action is allowed.

    Returns True only when the user approves the action.
    In dry-run mode, nothing is executed.
    """
    action = action.lower().strip()

    if action not in IRREVERSIBLE_ACTIONS:
        raise ValueError(
            f"Approval is only required for: "
            f"{sorted(IRREVERSIBLE_ACTIONS)}"
        )

    details = details or {}

    if dry_run:
        print(
            f"DRY RUN: would {action} message {message_id}"
        )

        log_event(
            "gate",
            message_id=message_id,
            proposed_action=action,
            details=details,
            human_decision="dry-run",
            outcome="not executed",
        )

        return False

    print(
        f"\nApproval required: {action} message {message_id}"
    )

    if details:
        print(f"Details: {details}")

    answer = input("Approve? (y/n): ").strip().lower()

    approved = answer in ("y", "yes")

    log_event(
        "gate",
        message_id=message_id,
        proposed_action=action,
        details=details,
        human_decision=answer,
        outcome="approved" if approved else "denied",
    )

    return approved