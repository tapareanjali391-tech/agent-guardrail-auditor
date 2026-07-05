# Agent Guardrail Auditor

As LLM agents gain the ability to take autonomous real-world actions — browsing websites, submitting forms, making purchases, and sending communications — the cost of an unchecked mistake scales with every step the agent takes without oversight. A single runaway loop can spam applications, spend money, or leak credentials before a human notices. This project is a lightweight Python framework that wraps an agent's action loop with programmatic guardrails: every proposed action is evaluated against authored safety policies before execution, and untrusted context is scanned for prompt-injection attempts before it reaches the agent. It is a research/portfolio artifact demonstrating safety-engineering thinking, not a production system.

## Architecture

```
  Incoming Context (web pages, tool outputs, retrieved documents)
                          │
                          ▼
               ┌──────────────────────┐
               │ PromptInjectionDet.  │──► quarantine suspicious content
               └──────────┬───────────┘
                          │ clean content only
                          ▼
                    ┌──────────┐
                    │  Agent   │
                    └────┬─────┘
                         │ proposes action
                         ▼
               ┌─────────────────────┐
               │    ActionAuditor    │
               │    Policy Check     │
               └─────────┬───────────┘
                         ▼
           ALLOW  │  BLOCK  │  ESCALATE_TO_HUMAN
                         │
                         ▼
                  audit_log.json
```

| Module | Role |
|--------|------|
| `Policy` | Defines scope (`read_only`, `requires_confirmation`, `blocked`) and regex patterns for risky actions |
| `ActionAuditor` | Evaluates proposed actions, enforces rate limits, logs every decision to `audit_log.json` |
| `PromptInjectionDetector` | Scans untrusted context for hijack patterns and quarantines suspicious content |

## Demo Results

The included `demo.py` simulates an autonomous job-application agent across six scenarios:

| # | Scenario | Verdict |
|---|----------|---------|
| 1 | Read job posting | **ALLOW** |
| 2 | Submit application with fabricated experience | **BLOCK** |
| 3 | Submit honest application | **ESCALATE_TO_HUMAN** |
| 4 | Exceed hourly application rate limit | **ESCALATE_TO_HUMAN** |
| 5 | Purchase premium job-board subscription | **BLOCK** |
| 6 | Prompt injection in scraped HTML | **QUARANTINED** |

## Why this matters for AI safety

**Scalable oversight.** As agents operate at high volume, reviewing every action manually is impractical. Policy-based auditing automates the routine cases and routes only the ambiguous or high-risk decisions to humans — letting oversight scale with autonomy rather than against it.

**Corrigibility.** A system that can be stopped or redirected before irreversible actions is more corrigible than one that acts first and logs later. `BLOCK` and `ESCALATE_TO_HUMAN` verdicts create explicit intervention points where a human (or a higher-authority controller) can override or correct the agent's trajectory.

**Defense against prompt injection.** Agents that browse the open web ingest untrusted content that may contain instructions designed to hijack their behavior. Scanning and quarantining suspicious patterns before they enter the agent's context is a first-line defense — complementary to capability restrictions and sandboxing.

## Limitations

This is a **rule/pattern-based auditor**, not a learned classifier. Policies must be manually authored and maintained; they will miss novel attack patterns, paraphrased risks, and adversarially crafted inputs that do not match known keywords. The prompt-injection detector relies on regex heuristics, which attackers can evade with encoding tricks, indirect phrasing, or multi-step social engineering.

A production system would require adversarial red-teaming, continuous policy updates, structured action schemas (rather than free-text matching), and likely a fine-tuned classifier for detecting injection attempts instead of keyword matching alone. It would also need persistent distributed rate limiting, cryptographic provenance for tool outputs, real human-approval workflows, and formal guarantees that blocked actions cannot execute via alternate code paths.

## Setup & Run

Requires Python 3.10+ (stdlib only — no dependencies).

```bash
cd agent-guardrail-auditor
python demo.py
```

This runs all six scenarios, prints verdicts to the console, and writes an audit trail to `audit_log.json`.

## Project Structure

```
agent-guardrail-auditor/
├── agent_guardrail/
│   ├── __init__.py
│   ├── policy.py
│   ├── auditor.py
│   └── injection_detector.py
├── demo.py
├── audit_log.json          # example output from demo run
├── .gitignore
└── README.md
```
