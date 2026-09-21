# InboxHero – IIIT Hyderabad Agentic AI Assignment 6

**Student:** Anurag Chv, evernorth-aai-1155338  
**GitHub Repository:** https://github.com/Anurag-Chv/IIIT-Hyd-Agentic-AI-Assignment-6

## Overview

InboxHero is an agentic email assistant built for Assignment 6 of the IIIT Hyderabad Agentic AI course. The system processes a complete local mock inbox, gives every message exactly one disposition with a reason, performs allowed actions, and stops at a human-review boundary for sensitive or irreversible work.

The project uses a custom Python architecture with MCP-style tool discovery and execution rather than a third-party agent framework. During development, the primary local model is Ollama with `qwen2.5:7b`.

Everything is local. Sending is simulated by writing a JSON file to `outbox/`; there is no connection to a real mailbox.

## Project Structure

- `main.py` – development entry point for inbox processing
- `demo.py` – graded capability entry point for R1-R6 and X1-X3
- `agent.py` – agent loop with planner, LLM, MCP tools and reflection
- `planner.py` – creates a Goal and Plan
- `reflector.py` – reviews the completed agent process
- `workflow.py` – main inbox processing and grounded-reply logic
- `rules.py` – handles obvious messages before the model
- `safety.py` – approval and dry-run gate for irreversible actions
- `actions.py` – simulated send/delete implementations
- `trace.py` – JSONL audit log
- `dashboard.py` – generates the three-pane dashboard
- `memory.py` – persistent memory
- `memory_store.json` – local persistent memory store
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
- `CAPABILITIES.md` – human-readable capability manifest
- `capabilities.json` – machine-readable capability manifest

## Architecture

The project uses a custom Python agent architecture rather than CrewAI, Google ADK, LangGraph, or another third-party agent framework.

The general agent flow is:

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

Inbox processing in `workflow.py` uses a safety-first branch:

```text
Inbox Message
    ↓
Hostile Instruction Check
    ↓
Phishing / Sensitive Check
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

Email text is treated as untrusted data throughout the system.

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

A Google Gemini provider is also supported through the same configuration layer when a `GOOGLE_API_KEY` is supplied.

## Setup

### Windows

```powershell
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

Each capability has its own command:

```bash
python demo.py --cap R1
python demo.py --cap R2 --msg m008
python demo.py --cap R3 --dry-run
python demo.py --cap R4
python demo.py --cap R5
python demo.py --cap R6
python demo.py --cap X1
python demo.py --cap X2
python demo.py --cap X3
```

To run the complete capability sequence:

```bash
python demo.py --all
```

## Inbox

The supplied `inbox.json` contains 100 messages. Each message contains:

- `id`
- `thread_id`
- `from`
- `to`
- `subject`
- `timestamp`
- `body`
- `unread`

The inbox includes normal work messages, automated notifications, messages requiring earlier-thread context, standing preferences, commitments, phishing/social-engineering attempts, and messages containing instructions aimed at the assistant.

## R1–R6: Required Capabilities

| ID | Capability | Tier | Evidence |
|---|---|---|---|
| R1 | Zero the inbox | B | 100 messages receive exactly one disposition; latest full run reported 51 rule-handled and 0 undecided |
| R2 | Grounded reply | B | `m008` is grounded using earlier messages including `m003`; cited IDs are recorded |
| R3 | Gate the irreversible | C | dry-run shows send/delete proposals with 0 outbox writes |
| R4 | Persistent preference | C | `m041` preference survives process exit and affects `m043` |
| R5 | Refuse embedded instructions | C | `m017`, `m024`, `m039`, and `m047` are flagged, refused and left in place |
| R6 | Dashboard | C | `dashboard.html` has exactly three panes; commitments cite source IDs and conflicts are surfaced |

## Custom Capabilities

| ID | Capability | Tier | Observable result |
|---|---|---|---|
| X1 | Security & Secret Scanner | A | finds six security/credential-related messages without printing secret values |
| X2 | Follow-up Tracker | B | identifies `m044` as an unanswered sent message and creates a chase draft |
| X3 | Preference-Aware Scheduler | C | identifies `m043` as a 09:00 proposal that conflicts with the stored 11:00 meeting preference |

The full commands, claims, outputs and evidence are documented in:

```text
CAPABILITIES.md
capabilities.json
```

## Safety Design

InboxHero treats email content as untrusted data. Instructions embedded in message bodies are not treated as system instructions and cannot directly authorize actions.

The hostile-inbox handling specifically refuses requests to forward mailbox contents, expose credentials, bypass approval, change assistant configuration, delete messages, or hide actions from the user.

The project treats these actions as irreversible:

```text
send
delete
```

Both are reachable only through the application safety gate. The gate supports explicit human approval and `--dry-run`, and records the proposal, human response, and outcome in `trace.jsonl`.

Sending is simulated by writing one JSON file per message to `outbox/`.

## Reversible vs Irreversible

The main reversible dispositions/actions are:

```text
reply / draft
archive
defer
delegate / escalate for human review
```

`send` and `delete` are irreversible in this project. Delete is treated as irreversible because the mock store has no trash or recovery mechanism.

The escalation boundary is intentionally conservative for sensitive access information, phishing/social-engineering, assistant-directed instructions, money-related requests and legal/sensitive work. This reduces the chance of an irreversible mistake at the cost of some additional human review.

## Retrieval

The primary retrieval method for grounded replies is **thread-walk**.

For a target message, InboxHero retrieves earlier messages from the same `thread_id` and passes those messages as grounding context. Each message actually read is logged, and the final draft records the message IDs used.

Keyword search is also available for cross-thread lookup when thread structure is not sufficient.

## Persistent Memory

Preferences that must survive a process restart are stored in `memory_store.json`.

The demonstrated example is:

```text
meeting_start = 11:00
```

The preference comes from `m041` and is applied later to `m043`, which proposes a 09:00 meeting.

## Dashboard

The generated dashboard contains exactly three panes:

1. Pending Actions
2. Flagged
3. Commitments

The commitments pane cites supporting message IDs. The current demonstrated commitment for the board deck cites both `m038` and `m040`.

The dashboard also surfaces same-date/same-time conflicts, including the demonstrated 2026-09-15 15:00 conflict between the Northwind VC intro call and dental cleaning.

Generated files:

```text
dashboard.html
dashboard.json
```

## Traceability and Accountability

Important decisions and actions are recorded in:

```text
trace.jsonl
```

The trace includes events such as message reads, decisions, refusals, drafts, safety-gate decisions, irreversible actions, commitment extraction and run summaries.

A wrong send is therefore traceable through the message ID, proposed action, gate decision, and resulting outbox record. The application requires a human decision at the irreversible-action boundary; InboxHero does not treat an email's embedded instruction as authorization to send.

## Final Report

### 1. What did InboxHero refuse to automate, and why?

InboxHero refuses to automatically carry out credential-related requests, phishing/social-engineering requests, assistant-directed instructions embedded in email, and irreversible send/delete actions without the safety gate. For example, `m003` and `m008` are escalated rather than automatically redistributing staging access information, while `m017`, `m024`, `m039`, and `m047` are refused as hostile embedded instructions. The reason is that email content is untrusted and these cases can create security, disclosure, or irreversible-action risk. The system instead records the case and leaves a human-review boundary.

### 2. Where does untrusted text enter, and what would an attacker have to defeat?

Untrusted text enters from every `body`, `subject`, sender and other message fields read from `inbox.json`, and those values are also passed into retrieval and model prompts. The prompts explicitly mark message content as untrusted data and instruct the model not to follow instructions contained in the emails. An attacker would therefore need to defeat both the untrusted-data boundary and the application-level action gate before an email could cause a protected send or delete.

### 3. Who is accountable for a wrong send, and how is it traceable?

The system keeps the human in the decision loop for irreversible send/delete actions. A proposed send records the message ID and proposed action, `require_approval()` records the human response, and a successful simulated send creates a message-specific JSON record in `outbox/`. These records are linked by `trace.jsonl`, so a reviewer can reconstruct what was proposed, what approval decision was made, and what outcome occurred.

### 4. How does the project map to Agents, Tasks, Crew or a router?

Conceptually, `agent.py` is the agent loop, `planner.py` and `reflector.py` provide planning and review stages, and the functions in `workflow.py`, retrieval helpers and safety actions act like individual tasks. The rule/safety branches form a simple custom router that decides whether a message is handled by rules, the model, or human review. There is no Crew object because the project does not use a third-party multi-agent framework; a CrewAI-style implementation could provide explicit agent/task/crew abstractions, but it would add another orchestration layer on top of a workflow that currently uses a small custom control flow.

## Development History

The project was developed incrementally and committed to the public GitHub repository throughout the build. The repository therefore contains the implementation history rather than a single final upload.

## Final Submission

The submission package should contain:

```text
demo.py
CAPABILITIES.md
capabilities.json
README.md
inbox.json
outbox/
trace.jsonl
dashboard.html
dashboard.json
.env.example
requirements.txt
```

It should not contain:

```text
.env
venviiit/
__pycache__/
```

The required public repository link is at the top of this README.
