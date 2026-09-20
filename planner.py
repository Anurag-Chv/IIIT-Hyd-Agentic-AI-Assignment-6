"""
Planner module for SkyVault Agent.
Prepares a clear Goal and step-by-step Plan
before any tool execution begins, so the agent’s intent is visible.

⚠️ Note: In Assignment 5, tool declarations are now fetched dynamically
via MCPClient.list_tools(). This file remains as a static reference only.
"""

import sys
from pathlib import Path

# Add Common/ folder to Python path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent / "Common"))

from llm import chat
from schemas import skyvault_tool_declarations


def _tools_summary():
    """
    Create a short overview of all available tools
    with their required parameters and descriptions.
    """
    lines = []
    for declaration in skyvault_tool_declarations:
        required = declaration.parameters.required or []
        params = ", ".join(required)
        lines.append(f"- {declaration.name}({params}): {declaration.description}")
    return "\n".join(lines)


# System prompt for Gemini planning
PLANNER_SYSTEM = f"""You are assisting with SkyVault planning.
Before running any tools, outline a one-sentence Goal and a numbered Plan.
Use only the tools listed below when needed.
If the query can be answered directly, note that no tools are required.

Available tools (static reference):
{_tools_summary()}

Format your response exactly like this:
Goal:
<short statement of what needs to be figured out>

Plan:
1. <first step, tool if applicable>
2. <next step>
3. <continue until complete>
"""


def create_plan(user_question: str) -> str:
    """
    Ask the Gemini model to generate a Goal and Plan
    for the given user question.
    """
    prompt = f"User query: {user_question}\n\nPlease provide a Goal and Plan."
    return chat(prompt, system=PLANNER_SYSTEM)


def display_plan(plan_text: str) -> None:
    """
    Print the Goal and Plan in a readable format
    before tool execution starts.
    """
    print("\n--- Planning Stage ---")
    print(plan_text.strip())
    print("----------------------\n")


# Demo run (only executes if planner.py is run directly)
if __name__ == "__main__":
    sample_question = "What is the status of flight AI101?"
    plan = create_plan(sample_question)
    display_plan(plan)
