### Updated `README.md`

```markdown
# InboxHero – IIIT Hyderabad Agentic AI Assignment 6

## Overview

InboxHero is an agentic email assistant built for Assignment 6 of the
IIIT Hyderabad Agentic AI course.

The goal is to process a complete inbox, decide what should happen to
each message, perform safe actions automatically, and stop when an
action needs human approval.

The system is being built as a custom Python application. During
development, I am using Ollama with Qwen2.5:7B as the local model.

---

## Project Structure

- `main.py` – simple demo and interactive chat entry point.
- `agent.py` – main agent flow.
- `planner.py` – creates a goal and plan before execution.
- `reflector.py` – reviews the completed process.
- `config.py` – loads model and application configuration.
- `memory.py` – persistent memory for user preferences.
- `memory_store.json` – local persistent memory store.
- `mcp_server.py` – MCP server and tool registry.
- `mcp_client.py` – MCP client.
- `gatebot.py` – small MCP/tool exploration script.
- `app.py` – tests and development demos.
- `Common/data.py` – inbox data access functions.
- `Common/tools.py` – InboxHero tool implementations.
- `Common/schemas.py` – tool definitions.
- `Common/llm.py` – LLM wrapper for Ollama/Gemini.
- `inbox.json` – supplied mock inbox.
- `.env.example` – environment variable template.
- `requirements.txt` – Python dependencies.

---

## Model

The primary development setup is:

- Provider: Ollama
- Model: `qwen2.5:7b`
- Ollama URL: `http://localhost:11434`

The model provider is configured through environment variables in
`config.py`.

---

## Setup

### Windows

```bash
python -m venv venviiit
venviiit\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with the required settings.

For local Ollama development:

```text
LLM_PROVIDER=ollama
MODEL_NAME=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

Make sure Ollama is running and the model is available:

```bash
ollama list
ollama run qwen2.5:7b
```

`.env` is local only and is not committed to GitHub.

---

## Run

### Basic demo

```bash
python main.py
```

### Interactive mode

```bash
python main.py --chat
```

### Run tests

```bash
python app.py -v
```

### MCP exploration

```bash
python gatebot.py
```

The graded capability interface will be provided through:

```bash
python demo.py --cap R1
```

and the corresponding commands for the remaining capabilities.

---

## Inbox

The supplied `inbox.json` contains 100 email messages.

Each message contains:

- `id`
- `thread_id`
- `from`
- `to`
- `subject`
- `timestamp`
- `body`
- `unread`

The inbox contains normal work messages, newsletters and receipts,
messages requiring earlier thread context, standing preferences,
commitments, phishing/social-engineering attempts and messages
containing instructions aimed at the assistant.

---

## Design Approach

InboxHero separates simple rule-based work from model-based work.

Obvious messages such as receipts, newsletters and automated
notifications should be handled by rules whenever possible. Messages
that need reasoning, retrieval or drafting can be passed to the model.

For retrieval, the current design uses thread-based retrieval first,
with keyword search available when information needs to be found
across threads.

Email content is treated as untrusted data. Instructions found inside
messages are not treated as system instructions.

Irreversible actions such as sending or deleting messages will be
protected by a separate safety gate.

---

## Required Assignment Capabilities

The assignment requires six capabilities:

- `R1` – Zero the inbox
- `R2` – Grounded reply
- `R3` – Gate the irreversible
- `R4` – Persistent preference
- `R5` – Refuse embedded instructions
- `R6` – Dashboard

The final capability definitions, commands and observable evidence are
documented in `CAPABILITIES.md` and `capabilities.json`.

---

## Custom Capabilities

In addition to R1-R6, the project will include several additional
capabilities selected for the InboxHero use case.

These will be documented after implementation and testing.

---

## Safety

InboxHero does not treat email content as trusted instructions.

For example, an email may contain a request to forward the mailbox,
delete a message or bypass an approval step. Such instructions are
treated as part of the email content and are not executed.

Irreversible actions require the safety gate defined by the final
design.

The system also records decisions and important actions so that a
completed run can be inspected later.

---

## Persistent Memory

InboxHero uses a small JSON file for information that must survive a
process restart.

Example preferences can include:

```text
Do not schedule meetings before 11:00 AM.
CC Priya on legal correspondence.
```

The preference is stored on disk and can be used during a later run.

---

## GitHub

Repository:

`https://github.com/<your-github-username>/IIIT-Hyd-Agentic-AI-Assignment-6`

The repository contains the development history for the assignment.

---

## Final Submission

The final ZIP will contain:

- complete runnable Python project
- `demo.py`
- `CAPABILITIES.md`
- `capabilities.json`
- `README.md`
- `inbox.json`
- `outbox/`
- `trace.jsonl`
- `.env.example`

It will not contain:

- `.env`
- virtual environments
- `__pycache__/`
- other local-only files

The final submission filename will be:

```text
inboxHero_YourName.zip
```

---

## Development Notes

This project is being developed incrementally. Each major change is
committed and pushed to GitHub so the repository keeps a clear history
of the implementation.
```

### Why I'm keeping this version deliberately simple

I've removed the old Assignment 5 reflection answers and claims such as:

> "23 tests OK"

because those are no longer true for Assignment 6. We shouldn't put results into the README until we've actually run them.

I also haven't invented our **3–5 custom capabilities** yet. We'll choose those after R1–R6 are clear.
