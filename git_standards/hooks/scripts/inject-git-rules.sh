#!/bin/bash
# Injects brief git workflow rules at session start.
# Only activates inside git repositories.

if ! git rev-parse --git-dir &>/dev/null; then
  exit 0
fi

cat <<'RULES'
# Git Standards — Active Enforcement

**Use the `git-workflow` skill for the full playbook before doing any git work.**

## Quick Reference
- **main** = production (never commit/push directly)
- **develop** = integration (never commit/push directly)
- **feature/<name>** from develop | **hotfix/<name>** from main | **release/<version>** from develop
- Commits: `type: description` (feat|fix|refactor|docs|style|test|chore) — present tense, under 72 chars
- Stage specific files only — never `git add .` or `git add -A`
- No force push — ever
- Delete branches after merge
- Hotfixes merge to BOTH main AND develop
RULES
