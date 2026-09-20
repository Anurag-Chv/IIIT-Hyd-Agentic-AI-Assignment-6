Your current `README.md` is still referring to a few things we removed or changed:

- `Common/schemas.py` → deleted
- `main.py --chat` → removed
- `agent.py` is now provider-independent with MCP
- `mcp_server.py` is the runtime tool catalog
- the actual GitHub repository URL is known
- R1–R6 and custom capabilities should remain documented as work in progress until we have real evidence

I recommend replacing it with this cleaner version.

```markdown
# InboxHero – IIIT Hyderabad Agentic AI Assignment 6

**GitHub Repository:**  
https://github.com/Anurag-Chv/IIIT-Hyd-Agentic-AI-Assignment-6

## Overview

InboxHero is an agentic email assistant built for Assignment 6 of the IIIT Hyderabad Agentic AI course.

The goal is to process a complete local inbox, decide what should happen to every message, perform allowed actions, and stop safely when human approval is required.

The project uses a custom Python agent architecture with MCP-style tool discovery and execution.

During development, the primary local model is Ollama with `qwen2.5:7b`.

## Project Structure

- `main.py` – development entry point for inbox processing
- `agent.py` – planner, LLM, MCP tools and reflection flow
- `planner.py` – creates the Goal and Plan
- `reflector.py` – reviews the completed agent process
- `workflow.py` – main inbox processing logic
- `rules.py` – handles obvious automated messages before the model
- `safety.py` – approval gate for irreversible actions
- `actions.py` – send/delete implementations
- `trace.py` – JSONL audit log
- `dashboard.py` – generates the three-pane dashboard
- `memory.py` – persistent memory
- `memory_store.json` – local memory store
- `mcp_server.py` – MCP server and runtime tool registry
- `mcp_client.py` – MCP client
- `gatebot.py` – MCP smoke test
- `app.py` – unit and integration tests
- `Common/data.py` – inbox data access
- `Common/tools.py` – tool implementations
- `Common/llm.py` – LLM provider wrapper
- `inbox.json` – supplied mock inbox
- `outbox/` – simulated sent messages
- `decisions.json` – message dispositions
- `message_state.json` – reversible action state
- `.env.example` – environment configuration template
- `requirements.txt` – Python dependencies

## Architecture

The project uses a custom Python agent architecture rather than a third-party agent framework.

The main flow is:

```text
User Request
    ↓
Planner
    ↓
Agent / LLM
    ↓
MCP Client
    ↓
MCP Server
    ↓
Tool Registry
    ↓
Tool Result
    ↓
LLM
    ↓
Final Result
    ↓
Reflector
```

Inbox processing in `workflow.py` uses a separate path:

```text
Inbox Message
    ↓
Hostile Instruction Check
    ↓
Phishing Check
    ↓
Rule-Based Classification
    ↓
LLM Classification when needed
    ↓
Disposition + Reason
    ↓
Reversible Action / Human Review
    ↓
Trace
```

Email content is treated as untrusted data throughout the system.

## Model

Current development setup:

```text
LLM_PROVIDER=ollama
MODEL_NAME=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

The provider is configured through `config.py`.

For local development:

```bash
ollama list
ollama run qwen2.5:7b
```

## Setup

### Windows

```bash
python -m venv venviiit
venviiit\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Set the required values in `.env`.

The `.env` file is local only and is not committed to GitHub.

## Run

### Inbox processing

```bash
python main.py
```

### Tests

```bash
python app.py -v
```

### MCP smoke test

```bash
python mcp_client.py
```

or:

```bash
python gatebot.py
```

### Graded capability interface

The final assignment interface is:

```bash
python demo.py --cap R1
```

The same interface will be used for R2-R6 and the custom capabilities.

## Inbox

The supplied `inbox.json` contains 100 messages.

Each message contains:

- `id`
- `thread_id`
- `from`
- `to`
- `subject`
- `timestamp`
- `body`
- `unread`

The inbox includes normal work messages, automated notifications, messages requiring earlier-thread context, standing preferences, commitments, phishing and social-engineering attempts, and messages containing instructions aimed at the assistant.

## Safety Design

InboxHero treats all email content as untrusted data.

Instructions inside an email are not treated as system instructions and cannot directly control the agent.

Examples include requests to:

- forward mailbox contents
- expose credentials or secrets
- bypass approval
- change configuration
- delete messages
- hide actions from the user

Irreversible actions are limited to:

```text
send
delete
```

Both actions are reachable only through the application safety gate.

The gate supports:

- explicit human approval
- dry-run mode
- logging of the proposal
- logging of the human decision
- logging of the outcome

Sending a message writes one JSON file to `outbox/`.

## Retrieval

The primary retrieval method for grounded replies is thread-based retrieval.

For a target message, InboxHero retrieves earlier messages from the same thread and uses only those messages as grounding context.

Keyword search is also available for cross-thread retrieval.

Grounded replies record the message IDs actually used to produce the draft.

## Persistent Memory

InboxHero stores persistent preferences in `memory_store.json`.

The stored information survives process exit and restart.

Example:

```text
meeting_start = 11:00
```

A preference from the inbox can therefore affect later processing.

## Required Assignment Capabilities

The project implements the following required capabilities:

| ID | Capability |
|---|---|
| R1 | Zero the inbox |
| R2 | Grounded reply |
| R3 | Gate the irreversible |
| R4 | Persistent preference |
| R5 | Refuse embedded instructions |
| R6 | Dashboard |

Final commands, evidence and capability details are documented in:

```text
CAPABILITIES.md
capabilities.json
```

## Custom Capabilities

The project will include 3–5 additional capabilities beyond R1-R6.

The final capabilities will be documented in:

```text
CAPABILITIES.md
capabilities.json
```

They will include their own commands and observable output.

## Dashboard

The InboxHero dashboard contains exactly three panes:

1. Pending Actions
2. Flagged
3. Commitments

Commitments include their supporting message IDs.

The dashboard also surfaces conflicts between commitments with the same date and time.

The generated files are:

```text
dashboard.html
dashboard.json
```

## Traceability

Important decisions and actions are recorded in:

```text
trace.jsonl
```

The trace records events such as:

- decisions
- message reads
- refusals
- flagged messages
- drafts
- safety-gate decisions
- irreversible actions
- run summaries
- commitment extraction

This provides evidence for reproducing and reviewing a completed run.

## Final Report

### 1. What did InboxHero refuse to automate, and why?

To be completed after the final implementation and demonstration run.

### 2. Where does untrusted text enter, and what would an attacker have to defeat?

To be completed after the final implementation and demonstration run.

### 3. Who is accountable for a wrong send, and how is it traceable?

To be completed after the final implementation and demonstration run.

### 4. How does the project map to Agents, Tasks, Crew or a router?

To be completed after the final architecture is finalized.

## Development History

The project is developed incrementally.

Major changes are committed and pushed to GitHub throughout development so the repository contains the implementation history.

## Final Submission

The final submission will contain:

```text
demo.py
CAPABILITIES.md
capabilities.json
README.md
inbox.json
outbox/
trace.jsonl
.env.example
```

It will not contain:

```text
.env
venviiit/
__pycache__/
```
