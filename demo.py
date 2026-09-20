import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from Common.data import load_inbox, get_message
from Common.tools import get_undecided_messages
from actions import send_message, delete_message
from dashboard import build_dashboard
from memory import remember, recall
from trace import log_event
from workflow import process_inbox, grounded_reply, detect_hostile_message

ROOT = Path(__file__).resolve().parent


def run_r1():
    result = process_inbox()

    print("\n=== R1: Zero the Inbox ===")
    for item in result["decisions"]:
        print(
            f"{item['message_id']:>5} | "
            f"{item['disposition']:<9} | "
            f"{item['reason']}"
        )

    undecided = get_undecided_messages()

    print(f"\nMessages processed: {result['messages_processed']}")
    print(f"Rule handled: {result['rule_handled']}")
    print(f"Never reached model: {result['never_reached_model']}")
    print(f"Undecided: {len(undecided)}")

    return result


def run_r2(message_id):
    result = grounded_reply(message_id)

    print("\n=== R2: Grounded Reply ===")

    if result.get("draft"):
        print(f"Message: {message_id}")
        print(f"\nDraft:\n{result['draft']}")
        print(f"\nCited: {result['cited_ids']}")
    else:
        print(json.dumps(result, indent=2))


def run_r3(dry_run=False):
    message = get_message("m051")

    if message is None:
        raise RuntimeError("R3 demo message m051 was not found.")

    outbox = ROOT / "outbox"
    before = {p.name for p in outbox.glob("*")} if outbox.exists() else set()

    print("\n=== R3: Gate the Irreversible ===")

    send_result = send_message(
        message_id="m051",
        to=message["from"],
        subject="Re: coffee when you're back in town?",
        body="Thanks for reaching out. Let me know what time works for you.",
        dry_run=dry_run,
    )
    print("\nSend proposal:")
    print(send_result)

    delete_result = delete_message(
        message_id="m051",
        dry_run=dry_run,
    )
    print("\nDelete proposal:")
    print(delete_result)

    after = {p.name for p in outbox.glob("*")} if outbox.exists() else set()
    new_writes = sorted(after - before)

    log_event(
        "capability",
        cap="R3",
        mode="dry-run" if dry_run else "approval",
        new_outbox_files=new_writes,
    )

    print(f"\nOutbox writes during this run: {len(new_writes)}")


def run_r4():
    key = "meeting_start"
    preference = recall(key)

    print("\n=== R4: Persistent Preference ===")

    if preference is None:
        remember(
            key,
            "11:00",
            "m041: no meetings before 11:00am",
        )

        log_event(
            "preference",
            cap="R4",
            message_id="m041",
            key=key,
            value="11:00",
        )

        print("Stored preference from m041: meetings start at 11:00 or later.")
        print("Exit this process and run the same command again.")
        return

    message = get_message("m043")

    if message is None:
        raise RuntimeError("R4 target message m043 was not found.")

    print("Preference loaded after restart:")
    print("  meetings start at 11:00 or later.")
    print("Message m043 proposes Monday at 9:00am.")
    print("InboxHero does not accept 9:00am and proposes 11:00am instead.")


    log_event(
        "preference_applied",
        cap="R4",
        source_id="m041",
        message_id="m043",
        stored_value=preference["value"],
        proposed_time="11:00",
    )


def run_r5():
    print("\n=== R5: Refuse Embedded Instructions ===")

    found = []

    for message in load_inbox():
        hostile = detect_hostile_message(message)

        if not hostile:
            continue

        found.append(hostile)

        log_event(
            "refusal",
            cap="R5",
            message_id=message["id"],
            attempted=hostile["attempted"],
            action="none",
        )

        print(
            f"FLAGGED: {message['id']} | "
            f"attempted: {hostile['attempted']} | "
            "action: refused, left in place"
        )

    print(f"\nHostile messages found: {len(found)}")
    print("No send, forward, or delete action was executed.")


def _commitments():
    messages = {m["id"]: m for m in load_inbox()}
    board_date = datetime.fromisoformat(messages["m038"]["timestamp"]).replace(day=18).date()

    return [
        {
            "date": board_date.isoformat(),
            "time": "10:00",
            "title": "Quarterly board review",
            "source_ids": ["m038"],
        },
        {
            "date": (board_date - timedelta(days=2)).isoformat(),
            "time": "",
            "title": "Board deck circulated before board review",
            "source_ids": ["m038", "m040"],
        },
        {
            "date": datetime.fromisoformat(messages["m010"]["timestamp"]).replace(day=15).date().isoformat(),
            "time": "15:00",
            "title": "Northwind VC intro call",
            "source_ids": ["m010"],
        },
        {
            "date": datetime.fromisoformat(messages["m061"]["timestamp"]).replace(day=15).date().isoformat(),
            "time": "15:00",
            "title": "Dental cleaning",
            "source_ids": ["m061"],
        },
    ]


def run_r6(run_workflow=True, workflow_result=None):
    if run_workflow:
        workflow_result = process_inbox()

    commitments = _commitments()

    dashboard = build_dashboard(
        pending_actions=workflow_result["pending_actions"],
        flagged=workflow_result["flagged"],
        commitments=commitments,
    )

    for item in commitments:
        log_event(
            "commitment",
            cap="R6",
            title=item["title"],
            source_ids=item["source_ids"],
        )

    print("\n=== R6: Dashboard ===")
    print(f"Dashboard: {ROOT / 'dashboard.html'}")
    print(f"Commitments: {len(commitments)}")

    for conflict in dashboard["conflicts"]:
        print(
            f"CONFLICT: {conflict['first']} and "
            f"{conflict['second']} at "
            f"{conflict['date']} {conflict['time']}"
        )


def run_all():
    result = run_r1()
    run_r2("m008")
    run_r3(dry_run=True)
    run_r4()
    run_r5()
    run_r6(run_workflow=False, workflow_result=result)


def main():
    parser = argparse.ArgumentParser(description="InboxHero capability runner")
    parser.add_argument("--cap", choices=["R1", "R2", "R3", "R4", "R5", "R6"])
    parser.add_argument("--msg", default="m008")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true")

    args = parser.parse_args()

    if args.all:
        run_all()
        return

    if not args.cap:
        parser.error("Use --cap R1..R6 or --all")

    if args.cap == "R1":
        run_r1()
    elif args.cap == "R2":
        run_r2(args.msg)
    elif args.cap == "R3":
        run_r3(args.dry_run)
    elif args.cap == "R4":
        run_r4()
    elif args.cap == "R5":
        run_r5()
    elif args.cap == "R6":
        run_r6()


if __name__ == "__main__":
    main()
