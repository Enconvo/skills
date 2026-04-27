# Audit System — moved to `pptx-audit`

The full audit specification, fix strategies, iterative-fix-with-rollback loop, false-positive filters, word-wrap simulation, and key lessons learned have moved to a dedicated skill:

**`~/.claude/skills/pptx-audit/`**

This split happened because instructions alone don't make weaker LLMs run the audit thoroughly. The audit is now a **deterministic Python script** that the agent must invoke and whose JSON output it must paste before delivery — the script does the work, the agent only has to call it.

## Where to find what

| What | Now at |
|---|---|
| Audit invocation gate | `pptx-design/SKILL.md` → "DELIVERY GATE" block at the top |
| 14 check definitions + fix strategies | `pptx-audit/references/audit-checks.md` |
| Deterministic engine | `pptx-audit/scripts/audit.py` |
| When to use / when to skip | `pptx-audit/SKILL.md` |
| Triage rules + false-positive guidance | `pptx-audit/references/audit-checks.md` ("Triage Before Fixing", "False Positive Avoidance") |
| Iterative fix loop with rollback | `pptx-audit/references/audit-checks.md` ("Iterative Fix Loop") |

## Quick command

```bash
python3 ~/.claude/skills/pptx-audit/scripts/audit.py "$PPTX_PATH"
# Exit 0 = passed, 1 = CRITICALs present, 2 = script error
```

Always paste the JSON `summary` block in your reply. Claiming "audit passed" without the JSON is a workflow violation.
