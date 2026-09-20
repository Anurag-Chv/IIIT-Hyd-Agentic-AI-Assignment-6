# SkyVault Agent – Assignment 05

## Overview
SkyVault is an airline operations assistant built using Google Gemini and the **Model Context Protocol (MCP)**. It answers operational queries by routing tool calls through an MCPServer/MCPClient layer. The agent follows three stages:

1. **Planning** – outlines a Goal and Plan before acting.  
2. **Execution** – calls tools via MCP until Gemini returns a text answer.  
3. **Reflection** – critiques tool usage and completeness after answering.  

Persistent memory tools (`remember`, `recall`) were added in this assignment.

---

## Project Layout
- `main.py` – entry point, runs demo queries or interactive chat.  
- `agent.py` – agent lifecycle: plan, MCP tool loop, answer, reflection.  
- `planner.py` – generates Goal and Plan.  
- `reflector.py` – critiques tool usage after final answer.  
- `config.py` – loads `.env` and exposes API settings.  
- `Common/llm.py` – Gemini client wrapper.  
- `Common/schemas.py` – static tool declarations (reference only).  
- `Common/tools.py` – tool implementations.  
- `Common/data.py` – mock dictionaries for flights, aircraft, passengers, maintenance, weather.  
- `mcp_server.py` – MCPServer with ToolRegistry.  
- `mcp_client.py` – MCPClient with `list_tools` and `call_tool`.  
- `gatebot.py` – small demo script showing tool reuse outside the agent.  
- `app.py` – unit tests and demo runner.  
- `.env.example` – template for environment variables.  
- `requirements.txt` – dependencies.

---

## Setup

### Windows
```bash
python -m venv venviiit
venviiit\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

### macOS / Linux
```bash
python3 -m venv venviiit
source venviiit/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

### Environment variables
```bash
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-3.6-flash
MODEL_TEMPERATURE=0.2
MAX_TOOL_ROUNDS=8
```

---

## Run Instructions
```bash
# Run unit tests
python app.py -v

# Run built-in demos
python main.py

# Start interactive chat
python main.py --chat

# Run tool + MCP demo
python app.py demo

# Optional exploration
python gatebot.py
```

---

## Example Prompts
- What is the status of flight AI101?  
- Find the booking details for passenger Rahul Sharma.  
- Flight UK873 is scheduled from Delhi. What is the weather at DEL, the flight status, and the maintenance record for aircraft VT-VST?  
- I usually work Terminal 2, remember that.  
- Find me an open gate.  

---

## Reflection Questions

### 1. Document grounding vs function grounding
Earlier assignments grounded answers in retrieved text. Now grounding means **function calls**. A wrong tool call can mislead with authoritative‑looking data. If tools ever write state, the risk is higher.

### 2. What if a function and its declaration drift apart?
If `tools.py` and `schemas.py` disagree, Gemini sends mismatched arguments and breaks execution. Running `python app.py -v` surfaces mismatches early.

### 3. What changes if SkyVault can cancel bookings or reassign gates?
Read‑only tools are low‑risk. Write tools are high‑impact. Misinterpreted queries could cancel bookings or reassign gates. Safeguards: require human approval and log every change.

### 4. Function descriptions vs system prompt
Function descriptions drive correct routing more than the system prompt. Clear declarations improved tool selection in multi‑tool queries.

---

## Reflection Based on My Runs
- Flight AI101: one correct tool call, complete info, highly reliable.  
- Passenger Rahul Sharma: one correct tool call, complete booking details.  
- Flight UK873 multi‑step: three correct tool calls, all info included.  
- Memory persistence: `remember` stored Terminal 2 successfully.  
- Recall + gate: validated via `app.py demo`, recall returned T2 and MCP call found gate B5.  

---

## Final Report
- Approach: MCP tool loop with planning and reflection.  
- Tool descriptions: clear declarations improved routing.  
- Planning and reflection: planning made intent visible; reflection surfaced efficiency and reliability.  
- Multi‑tool loop: agent repeats function_call → execute → function_response until Gemini returns text.  
- Error handling: not yet implemented. Next step is to wrap tools in `try/except` and return structured error dicts.  
- Improvements: add error handling, logging of tool calls, and compare newer Gemini models for accuracy.

---

## Submission Checklist
- Include `.env.example`, not `.env`  
- Exclude `__pycache__/`, `.venv/`, `.env`  
- Confirm `python app.py -v` passes (23 tests OK)  
- Confirm `python main.py` runs with a valid API key  

---

## Final Conclusion
SkyVault demonstrates how Gemini can be grounded in function calls over mock data via MCP. The agent successfully plans, executes, and reflects on its answers. Memory persistence was added, and MCP integration proved reliable. All unit tests passed, confirming tool correctness. Future work should add error handling and safeguards before introducing write actions. Overall, this assignment shows a practical, working agent that can answer operational queries clearly and efficiently.
