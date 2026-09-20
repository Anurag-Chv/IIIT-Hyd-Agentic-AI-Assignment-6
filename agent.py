"""
Agent module for SkyVault.
Refactored to use MCPClient instead of direct tool imports.
Handles the main loop where Gemini requests tool calls and we execute them
through the MCP protocol until a final answer is produced.
"""

import sys
from pathlib import Path

# Ensure Common/ is on the path
_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "Common"))
sys.path.insert(0, str(_ROOT))

from google.genai import types

import config
from llm import get_client
from planner import create_plan, display_plan
from reflector import reflect, display_reflection
from mcp_server import MCPServer, ToolRegistry
from mcp_client import MCPClient

# Initialize MCP layer
_registry = ToolRegistry()
_server = MCPServer(_registry)
_client = MCPClient(_server)

MAX_TOOL_ROUNDS = config.MAX_TOOL_ROUNDS

SYSTEM_PROMPT = (
    "You are SkyVault, a FlightOps assistant supporting airline ground staff. "
    "Use the available tools when operational data is needed. "
    "If the query can be answered directly, respond without tools."
)


def _execute_tool(tool_name: str, tool_args: dict):
    """Run the requested tool via MCPClient and show its input/output."""
    print(f"Tool requested: {tool_name}({tool_args})")
    result = _client.call_tool(tool_name, tool_args)
    print(f"Tool result   : {result}")
    return result


def ask(user_prompt: str) -> str:
    """
    Main agent routine:
    - Generate a plan for the question.
    - Start a Gemini chat with tool declarations (from MCPClient).
    - Loop through tool calls until Gemini returns text.
    - Reflect on the process and return the final answer.
    """
    plan = create_plan(user_prompt)
    display_plan(plan)

    # Get tool declarations dynamically from MCPClient
    tool_declarations = []
    for tool in _client.list_tools():
        tool_declarations.append(
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters={
                    "type": "OBJECT",
                    "properties": tool["params"],
                    "required": tool["required"],
                },
            )
        )

    chat = get_client().chats.create(
        model=config.MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=f"{SYSTEM_PROMPT}\n\nPlanned steps:\n{plan}",
            tools=[types.Tool(function_declarations=tool_declarations)],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        ),
    )

    response = chat.send_message(user_prompt)
    tool_rounds = 0
    tool_history = []

    while response.function_calls:
        tool_rounds += 1
        if tool_rounds > MAX_TOOL_ROUNDS:
            return "Stopped after exceeding maximum tool calls. Please simplify the query."

        tool_request = response.function_calls[0]
        tool_name = tool_request.name
        tool_args = dict(tool_request.args)

        try:
            result = _execute_tool(tool_name, tool_args)
        except Exception as e:
            result = {"error": str(e)}

        tool_history.append({"name": tool_name, "args": tool_args, "result": result})

        response = chat.send_message(
            types.Part.from_function_response(
                name=tool_name,
                response={"result": result},
            )
        )

    if tool_rounds == 0:
        print("(No tool calls were needed)")
    else:
        print(f"(Completed – {tool_rounds} tool call(s) executed)")

    final_answer = response.text or ""
    reflection = reflect(user_prompt, plan, tool_history, final_answer)
    display_reflection(reflection)
    return final_answer


# Demo run (only executes if agent.py is run directly)
if __name__ == "__main__":
    print("=== Demo: Agent with MCP ===")
    answer = ask("What is the status of flight AI101?")
    print("Answer:", answer)
