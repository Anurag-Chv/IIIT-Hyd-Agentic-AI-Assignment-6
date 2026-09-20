"""
Main entry point for SkyVault Agent.
Now routes all tool calls through MCPClient/MCPServer (JSON-RPC).
Demonstrates planning, tool usage, memory persistence, and reflection.

Usage:
    python main.py          # run demo queries
    python main.py --chat   # start interactive chat loop
"""

import sys
from agent import ask


def run_demos():
    """Run a few sample queries to show how the agent works."""
    print("=== Demo 1: Flight status (via MCP) ===")
    answer = ask("What is the status of flight AI101?")
    print("Answer:", answer)

    print("\n=== Demo 2: Passenger lookup (via MCP) ===")
    answer = ask("Find the booking details for passenger Rahul Sharma.")
    print("Answer:", answer)

    print("\n=== Demo 3: Multi-step operations (via MCP) ===")
    answer = ask(
        "Flight UK873 is scheduled from Delhi. "
        "What is the weather at DEL, the flight status, "
        "and the maintenance record for aircraft VT-VST?"
    )
    print("Answer:", answer)

    print("\n=== Demo 4: Memory persistence (via MCP) ===")
    answer = ask("I usually work Terminal 2, remember that.")
    print("Answer:", answer)

    print("\n=== Demo 5: Recall fact and use in tool call (via MCP) ===")
    answer = ask("Find me an open gate.")  # should recall Terminal 2 automatically
    print("Answer:", answer)


def chat():
    """Interactive chat loop with the SkyVault Agent."""
    print("SkyVault Agent | type 'quit' or 'exit' to leave\n")

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
    """Decide whether to run demo mode or chat mode."""
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        chat()
    else:
        run_demos()


if __name__ == "__main__":
    main()
