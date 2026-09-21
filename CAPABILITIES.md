# CAPABILITIES.md

**Student:** Anurag Chv, evernorth-aai-1155338  
**Repository:** https://github.com/Anurag-Chv/IIIT-Hyd-Agentic-AI-Assignment-6

Run everything through one entry point:

```text
python demo.py --cap R1
python demo.py --all
```

---

## The system, in one paragraph

InboxHero is a single Python pipeline with no agent framework. It loads the local inbox, sends obvious noise through rules before the model, uses Ollama with `qwen2.5:7b` for the remaining triage/drafting work, keeps persistent state in small JSON files, and builds a static HTML dashboard. The latest full R1 run processed 100 messages, with 51 handled by rules and 60 reported as never reaching the model because the system also short-circuits safety/persistent-preference cases. No real email service is connected; an approved send writes one JSON file into `outbox/`.

## Design choices you were asked to state

- **Framework: none.** The implementation is a small linear workflow with a rule path and a model path. A framework was not needed for the current scope, and keeping the orchestration explicit makes the safety boundaries easy to inspect.

- **Retrieval: thread-walk.** R2 walks the target message's `thread_id` from the start of the thread to the target message and records every earlier message actually read. The inbox structure already provides the relationship needed for this task, so the implementation does not require embeddings for the grounded-reply demonstration.

- **Reversible vs irreversible.** `send` and `delete` are treated as irreversible. `draft`, `label`, `archive` and `defer` are treated as reversible in the manifest; delete is irreversible because the mock inbox has no trash/recovery mechanism. The R3 dry-run demonstrates that irreversible proposals do not execute or create outbox files.

- **Where the gate sits.** The only functions that can perform `send` or `delete` call `require_approval()` first. Email bodies are treated as untrusted data, and hostile messages are detected and refused without reaching an irreversible action. This means a message may be classified or flagged, but it cannot directly bypass the gate.

- **Escalation line.** Sensitive credentials, phishing indicators, hostile instructions, legal items and other high-risk requests are routed to human review rather than automatically executed. Ordinary informational mail can be archived or deferred by rule/model without a confirmation prompt. The trade-off is that some borderline messages may be escalated for safety rather than fully automated.

## Capabilities

| id | name | tier | one-line claim |
|----|------|------|----------------|
| R1 | Zero the inbox | B | every message gets exactly one disposition and reason, with none undecided |
| R2 | Grounded reply | B | drafts use earlier thread messages and record the IDs actually read |
| R3 | Gate the irreversible | C | send/delete require approval or `--dry-run`, with no outbox write in dry-run |
| R4 | Persistent preference | C | the meeting-start preference survives process exit and affects later scheduling |
| R5 | Refuse embedded instructions | C | hostile instructions are detected, refused, flagged and left in place |
| R6 | Dashboard | C | produces exactly three panes with cited commitments and surfaced conflicts |
| X1 | Security & Secret Scanner | A | finds credential/security-related messages without printing secret values |
| X2 | Follow-up Tracker | B | finds unanswered sent messages waiting 3+ days and drafts a chase |
| X3 | Preference-Aware Scheduler | C | applies the persisted scheduling preference to meeting proposals |

The exact command, observable outcome and evidence for each capability are in `capabilities.json`. This Markdown file explains the same design for a human reader; the JSON is the machine-readable manifest.

## Final Report

### 1. What did you refuse to automate, and why?

InboxHero refuses to automatically execute high-risk actions such as sending or deleting messages, handling requests involving sensitive credentials, or obeying instructions embedded inside email text. These cases are routed to human review because the consequence is harder to reverse or because the email itself may be attempting to control the assistant. The R3 gate is the explicit control for irreversible actions, while R5 leaves hostile messages in place after refusal. This keeps ordinary inbox work automated without giving untrusted content authority over external effects.

### 2. Where does untrusted text enter, and what would an attacker have to defeat?

Untrusted email text enters when messages are loaded from `inbox.json` and when message bodies are inserted into model prompts for classification or grounded drafting. The prompts explicitly label email text as untrusted and instruct the model not to follow instructions found inside the messages. An attacker would therefore need to bypass both the untrusted-data handling and the action gate before causing a `send` or `delete`. The hostile-message examples `m017`, `m024`, `m039` and `m047` demonstrate the refusal path.

### 3. How are you accountable if a wrong send happens?

Every irreversible proposal passes through `require_approval()`, which records the proposed action, human response and outcome in `trace.jsonl`. A successful mock send also creates a single message-specific file in `outbox/`, giving a concrete artifact to inspect. The capability runner records R3 events and reports the number of new outbox files produced during the run. This makes the decision path and resulting side effect traceable rather than relying only on the final inbox state.

### 4. How would this map to Agents, Tasks, Crew/router, and what would change with a framework?

The current system can be mapped to an Agent responsible for inbox decisions, Tasks for triage/retrieval/drafting/dashboard work, and a router that chooses the rule path or model path. A Crew-style framework could split those responsibilities into separate agents and tasks, while a graph framework could make the routing, safety gate and persistence transitions explicit nodes. For this assignment, the same behavior is implemented directly in Python so the control flow and irreversible boundary remain visible in a small codebase. Moving to a framework would mainly change orchestration and observability structure rather than the underlying safety rules or mailbox logic.
