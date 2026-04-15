# Hypothesis Tracker Protocols

This file is the source protocol for the Hypothesis Tracker workflow.

The installer does not copy this file wholesale into the target workspace.
Instead, it appends a short `CLAUDE.md` hint that points Claude Code to:

- `./.claude/skills/hypothesis-tracker-trade.md`
- `./.claude/skills/hypothesis-tracker-status.md`
- `./.claude/skills/hypothesis-tracker-new.md`
- `./config/hypothesis-tracker.yaml`
- `./config/hypothesis-tracker-rules.md`

Recommended commands:

- `/ht-trade`
- `/ht-status`
- `/ht-new`

Compatibility aliases may still exist inside the skills, but they should not be the default recommendation in shared docs or injected workspace hints because they are more likely to conflict with other systems.
