from workflow import process_inbox


def main():
    result = process_inbox()

    print("=== InboxHero ===")
    print(f"Messages processed: {result['messages_processed']}")
    print(f"Rule handled: {result['rule_handled']}")
    print(f"Model handled: {result['model_handled']}")
    print(f"Never reached model: {result['never_reached_model']}")
    print(f"Flagged: {len(result['flagged'])}")


if __name__ == "__main__":
    main()