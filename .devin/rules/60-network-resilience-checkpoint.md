---
trigger: always_on
description: Forces frequent checkpointing and clean automatic recovery after any network disconnection or session interruption. Makes every session resilient so work continues from the last completed step without user re-explanation.
---

# Network Resilience & Checkpoint Rule (mandatory)

You must treat every session as if the network can drop at any moment.

## 1. Checkpoint Discipline (do this continuously)
- After every meaningful unit of work (file edit, test run, decision, or completed sub-task), immediately write a short status update.
- Preferred location: `PROGRESS.md` in the project root or `.devin/progress/STATUS.md`.
- Each checkpoint must contain:
  1. What has been fully completed
  2. Exact next step that remains
  3. Any important decisions or file paths already changed
  4. Timestamp or step number

## 2. Recovery Behavior (on every new message)
When you receive any new user message, first assume it may be a resume after a network interruption.
- Immediately read the latest PROGRESS.md (or .devin/progress/STATUS.md).
- Continue exactly from the last completed checkpoint.
- Do not repeat work that is already marked done.
- Do not ask the user to re-explain the original task.
- Do not start over.

## 3. Writing Style for Checkpoints
Keep checkpoints short, imperative, and machine-readable. Example format:

Checkpoint 2026-08-16 14:05
DONE:

Reviewed and fixed core/validator.py (all lines)
Added missing vPC keepalive validation
NEXT:
Run full multi-switch flow test
Fix any remaining UI button handlers in static/app.js
FILES TOUCHED:
core/validator.py
tests/test_vpc.py
## 4. Additional Hard Rules
- Never leave the project in a half-finished state without a checkpoint.
- Prefer small, complete, reversible steps so a disconnect loses almost no work.
- If you are about to start a long-running command, write a checkpoint first.
- On resume, explicitly state: “Resuming from last checkpoint: [short summary]”.

## 5. Self-Check Before Ending Any Turn
Before you finish your response, verify:
- A current checkpoint exists and is up to date.
- The next action is clearly written so a future resume can continue without help.

Follow this rule on every single turn. No exceptions.