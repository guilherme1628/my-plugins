#!/bin/bash
# Injects git workflow rules at session start so Claude follows them proactively.
# Only activates inside git repositories.

if ! git rev-parse --git-dir &>/dev/null; then
  exit 0
fi

cat <<'RULES'
# Git Standards — Active Enforcement

This project enforces a strict professional Gitflow workflow. Violations are automatically blocked.

## Branch Structure
- **main** — Production. NEVER commit or push directly. Only receives merges from release/ or hotfix/.
- **develop** — Integration. NEVER commit or push directly. Receives merges from feature/ via PR.
- **feature/<name>** — New work. Branch from develop. Merge to develop via PR.
- **hotfix/<name>** — Urgent production fixes. Branch from main. Merge to BOTH main AND develop.
- **release/<version>** — Release prep. Branch from develop. Merge to main after QA.

## Commit Messages (Conventional Commits — MANDATORY)
Format: `type: description` or `type(scope): description`
Types: feat | fix | refactor | docs | style | test | chore
Rules: present tense, under 72 chars, specific (never "update" or "fix stuff")

## Enforced Rules
1. Commit messages MUST follow conventional commits
2. Branch names MUST use type/description (feature/, hotfix/, release/)
3. Feature branches from develop, hotfix branches from main, release branches from develop
4. No direct push to main or develop — use PRs
5. No force push — ever
6. No `git add .` or `git add -A` — stage specific files
7. Delete branches after merging
RULES
