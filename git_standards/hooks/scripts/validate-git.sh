#!/bin/bash
# Git Standards Validator — PreToolUse hook for Bash tool
# Enforces: conventional commits, branch naming, push protection, staging discipline
# Design: fail-open (if this script errors, the command is allowed)
# Requires: jq, git, GNU grep with PCRE (-P flag)

trap 'exit 0' ERR

input=$(cat 2>/dev/null) || exit 0
command=$(echo "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0

# Exit early if empty or not a git command
[[ -z "$command" ]] && exit 0
echo "$command" | grep -qE '\bgit\b' || exit 0

# ── Helpers ─────────────────────────────────────────────────────

deny() {
  jq -n --arg msg "$1" \
    '{hookSpecificOutput:{permissionDecision:"deny"},systemMessage:$msg}'
  exit 0
}

# ── Repository state ────────────────────────────────────────────

current_branch=""
has_commits=true

if git rev-parse --git-dir &>/dev/null; then
  current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  git rev-parse HEAD &>/dev/null || has_commits=false
fi

# ================================================================
# 1. DIRECT COMMIT TO PROTECTED BRANCHES
# ================================================================

if echo "$command" | grep -qE 'git\s+commit'; then
  if [[ "$has_commits" == "true" && "$current_branch" == "main" ]]; then
    deny "$(cat <<'MSG'
BRANCH PROTECTION: Direct commits to 'main' are forbidden.

main only receives merges from release/ or hotfix/ branches.

Create a branch first:
  git checkout develop && git checkout -b feature/<name>
  git checkout -b hotfix/<name>  (for urgent production fixes)
MSG
)"
  fi

  if [[ "$has_commits" == "true" && "$current_branch" == "develop" ]]; then
    deny "$(cat <<'MSG'
BRANCH PROTECTION: Direct commits to 'develop' are forbidden.

Create a feature branch first:
  git checkout -b feature/<description>
MSG
)"
  fi
fi

# ================================================================
# 2. COMMIT MESSAGE — Conventional Commits
# ================================================================

if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qE '\-m\s'; then
  if ! echo "$command" | grep -qP '(feat|fix|refactor|docs|style|test|chore)(\([a-zA-Z0-9._-]+\))?\s*:\s+\S'; then
    deny "$(cat <<'MSG'
COMMIT MESSAGE: Must use Conventional Commits format.

Format: type: description
        type(scope): description

Types: feat | fix | refactor | docs | style | test | chore

Examples:
  feat: implement JWT authentication
  fix: resolve payment rounding error
  refactor: extract validation into service class
  docs: add setup instructions to README
  chore: update dependencies to latest versions
MSG
)"
  fi
fi

# ================================================================
# 3. BRANCH NAMING
# ================================================================

new_branch=""

if echo "$command" | grep -qP 'git\s+checkout\s+-b\s+\S'; then
  new_branch=$(echo "$command" | grep -oP '(?<=checkout\s-b\s)\S+' | head -1)
elif echo "$command" | grep -qP 'git\s+switch\s+-c\s+\S'; then
  new_branch=$(echo "$command" | grep -oP '(?<=switch\s-c\s)\S+' | head -1)
elif echo "$command" | grep -qP 'git\s+branch\s+(?!-)\S'; then
  new_branch=$(echo "$command" | grep -oP '(?<=branch\s)(?!-)\S+' | head -1)
fi

if [[ -n "$new_branch" && "$new_branch" != "main" && "$new_branch" != "develop" ]]; then

  # Validate naming convention
  if ! echo "$new_branch" | grep -qP '^(feature|hotfix|release)/[a-z0-9][a-z0-9.-]*$'; then
    deny "$(cat <<MSG
BRANCH NAMING: '$new_branch' does not follow convention.

Format: type/description
Types:  feature/ | hotfix/ | release/
Rules:  lowercase, hyphens and dots only

Examples:
  feature/user-authentication
  hotfix/payment-bug
  release/1.2.0
MSG
)"
  fi

  # Validate branch origin
  if [[ -n "$current_branch" ]]; then
    if echo "$new_branch" | grep -qP '^feature/' && [[ "$current_branch" != "develop" ]]; then
      deny "$(cat <<MSG
BRANCH ORIGIN: Feature branches must be created from 'develop'.
You are currently on '$current_branch'.

Run first:
  git checkout develop
  git pull origin develop
Then create your branch:
  git checkout -b $new_branch
MSG
)"
    fi

    if echo "$new_branch" | grep -qP '^hotfix/' && [[ "$current_branch" != "main" ]]; then
      deny "$(cat <<MSG
BRANCH ORIGIN: Hotfix branches must be created from 'main'.
You are currently on '$current_branch'.

Run first:
  git checkout main
  git pull origin main
Then create your branch:
  git checkout -b $new_branch
MSG
)"
    fi

    if echo "$new_branch" | grep -qP '^release/' && [[ "$current_branch" != "develop" ]]; then
      deny "$(cat <<MSG
BRANCH ORIGIN: Release branches must be created from 'develop'.
You are currently on '$current_branch'.

Run first:
  git checkout develop
  git pull origin develop
Then create your branch:
  git checkout -b $new_branch
MSG
)"
    fi
  fi
fi

# ================================================================
# 4. PUSH PROTECTION
# ================================================================

if echo "$command" | grep -qE 'git\s+push'; then

  # Block force push (including --force-with-lease)
  if echo "$command" | grep -qP 'git\s+push\b.*\s(--force\b|-f\b|--force-with-lease\b)'; then
    deny "$(cat <<'MSG'
FORCE PUSH: Force push is forbidden (including --force-with-lease).

It rewrites history and can destroy other developers' commits.
Resolve conflicts with merge or rebase locally instead.
MSG
)"
  fi

  # Block push targeting main (standalone arg or refspec target, not inside a branch path)
  if echo "$command" | grep -qP 'git\s+push\b.*(\s+main(\s|$)|:main(\s|$))'; then
    deny "$(cat <<'MSG'
PUSH PROTECTION: Direct push to 'main' is forbidden.

main only receives merges from release/ or hotfix/ branches via pull request.

Workflow: develop -> release/<version> -> PR -> main
MSG
)"
  fi

  # Block push targeting develop (standalone arg or refspec target, not inside a branch path)
  if echo "$command" | grep -qP 'git\s+push\b.*(\s+develop(\s|$)|:develop(\s|$))'; then
    deny "$(cat <<'MSG'
PUSH PROTECTION: Direct push to 'develop' is forbidden.

Push your feature branch and open a pull request instead.

Workflow: feature/<name> -> git push -> PR -> develop
MSG
)"
  fi

  # Block bare push (no branch specified) when on protected branch
  if echo "$command" | grep -qP 'git\s+push(\s+-u)?\s+\w+\s*$' ||
     echo "$command" | grep -qP 'git\s+push\s*$'; then
    if [[ "$current_branch" == "main" || "$current_branch" == "develop" ]]; then
      deny "$(cat <<MSG
PUSH PROTECTION: You are on '$current_branch'. Direct push is forbidden.

Switch to a feature/hotfix/release branch first.
MSG
)"
    fi
  fi
fi

# ================================================================
# 5. STAGING DISCIPLINE
# ================================================================

if echo "$command" | grep -qP 'git\s+add\s+(-A|--all)\b'; then
  deny "$(cat <<'MSG'
STAGING: 'git add -A' / 'git add --all' stages everything blindly.

Stage specific files instead:
  git add src/auth/login.ts src/auth/middleware.ts

This prevents accidentally committing .env files, credentials, or unrelated changes.
MSG
)"
fi

if echo "$command" | grep -qP 'git\s+add\s+\.\s*(&&|;|\||$)'; then
  deny "$(cat <<'MSG'
STAGING: 'git add .' stages all changes in the directory blindly.

Stage specific files instead:
  git add src/auth/login.ts src/auth/middleware.ts

This prevents accidentally committing .env files, credentials, or unrelated changes.
MSG
)"
fi

# All checks passed
exit 0
