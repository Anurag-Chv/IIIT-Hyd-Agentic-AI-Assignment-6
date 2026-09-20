"""
Reflector module for SkyVault Agent.
After the agent produces an answer, this component asks Gemini
to review the process and highlight strengths or gaps.

⚠️ Note: In Assignment 5, all tool calls are routed through MCPClient/MCPServer.
Reflection should critique not only tool usage but also efficiency and completeness
of the MCP-mediated process.
"""

import sys
from pathlib import Path

# Ensure Common/ is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent / "Common"))

from llm import chat

# System prompt for reflection
REFLECTOR_SYSTEM = """You are reviewing the SkyVault assistant's work.
After the agent has answered a user query, provide a short critique.
Comment on:
- Tool usage (were any unnecessary?)
- Efficiency (could fewer calls have sufficed?)
- Completeness (was any important information missing?)
- Reliability (how confident should the user be?)
Remember: all tools are now invoked via MCP, so consider protocol usage as part of your critique.
"""


def _summarize_tool_calls(tool_calls):
    """
    Convert the list of tool calls into a readable summary.
    """
    if not tool_calls:
        return "No tools were invoked – the assistant answered directly."

    lines = []
    for idx, call in enumerate(tool_calls, start=1):
        lines.append(f"{idx}. {call['name']}({call['args']}) -> {call['result']}")
    return "\n".join(lines)


def reflect(user_question: str, plan: str, tool_calls: list, final_answer: str) -> str:
    """
    Ask Gemini to critique the agent's process after producing the final answer.
    """
    prompt = f"""User query:
{user_question}

Plan followed:
{plan}

Tools used (via MCP):
{_summarize_tool_calls(tool_calls)}

Final answer given:
{final_answer}

Please reflect on the process. Address:
1. Were any tools unnecessary?
2. Was any important information missing?
3. Could the answer have been reached with fewer steps?
4. How reliable should the user consider this answer, and why?
"""
    return chat(prompt, system=REFLECTOR_SYSTEM)


def display_reflection(reflection_text: str) -> None:
    """
    Print the reflection in a clear format after the final answer.
    """
    print("\n--- Reflection Stage ---")
    print(reflection_text.strip())
    print("------------------------\n")
