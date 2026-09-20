"""
Main entry point for InboxHero.

Usage:
    python main.py          # run a small demo
    python main.py --chat   # start interactive chat
"""

import sys

from agent import ask


def run_demo():
    """Run a few simple InboxHero queries."""
    print("=== InboxHero Demo ===")

    answer = ask(
        "Give me a summary of the inbox and tell me what needs attention."
    )
    print("Answer:", answer)

    print("\n=== Search Demo ===")
    answer = ask(
        "Find messages related to the board review."
    )
    print("Answer:", answer)


def chat():
    """Start an interactive InboxHero chat."""
    print("InboxHero | type 'quit' or 'exit' to leave\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye.")
            break

        reply = ask(user_input)
        print(f"\nAssistant: {reply}\n" + "-" * 50)


def main():
    """Run demo mode or interactive mode."""
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        chat()
    else:
        run_demo()


if __name__ == "__main__":
    main()