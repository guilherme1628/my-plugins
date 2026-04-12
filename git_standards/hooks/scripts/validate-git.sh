#!/bin/bash
# Git Standards Validator — PreToolUse hook for Bash tool
# Enforces: conventional commits, branch naming, push protection, staging discipline
# Understands: Gitflow merge/push workflows (finish-hotfix, finish-release)
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
# 3. BRANCH CREATION — Use skills, not raw commands
# ================================================================

if echo "$command" | grep -qP 'git\s+(checkout\s+-b|switch\s+-c|branch\s+(?!-))\s*\S'; then
  deny "$(cat <<'MSG'
WORKFLOW: Do not create branches manually.

Use the proper skill instead:
  /start-feature <name>   — creates feature/<name> from develop
  /start-hotfix <name>    — creates hotfix/<name> from main
  /start-release <version> — creates release/<version> from develop

These skills ensure: latest pull, correct origin, proper naming, and tracking.
MSG
)"
fi

# ================================================================
# 4. AI/AUTHOR MENTIONS IN COMMITS
# ================================================================

if echo "$command" | grep -qE 'git\s+commit' && echo "$command" | grep -qE '\-m\s'; then
  if echo "$command" | grep -qPi '(claude|anthropic|openai|gpt|chatgpt|copilot|ai[- ]?(generated|assisted|authored|powered)|co-authored-by.*claude|co-authored-by.*anthropic|co-authored-by.*noreply@anthropic)'; then
    deny "$(cat <<'MSG'
AI MENTION: Commit messages must not reference AI tools or AI co-authorship.

Remove any mentions of: Claude, Anthropic, OpenAI, GPT, Copilot,
AI-generated, AI-assisted, or Co-Authored-By AI lines.

History must read as human-authored.
MSG
)"
  fi
fi

# ================================================================
# 5. PUSH PROTECTION
# ================================================================

if echo "$command" | grep -qE 'git\s+push'; then

  # Block force push (always forbidden, no exceptions)
  if echo "$command" | grep -qP 'git\s+push\b.*\s(--force\b|-f\b|--force-with-lease\b)'; then
    deny "$(cat <<'MSG'
FORCE PUSH: Force push is forbidden (including --force-with-lease).

It rewrites history and can destroy other developers' commits.
Resolve conflicts with merge or rebase locally instead.
MSG
)"
  fi

  # Push to main — allowed ONLY during finish-hotfix/finish-release workflow
  # (when you're ON main after merging a hotfix/release into it)
  if echo "$command" | grep -qP 'git\s+push\b.*(\s+main(\s|$)|:main(\s|$))'; then
    if [[ "$current_branch" == "main" ]]; then
      # Check if HEAD is a merge commit (legitimate finish workflow)
      if git log -1 --pretty=%P HEAD 2>/dev/null | grep -q ' '; then
        : # Allow — this is a merge commit push (finish-hotfix or finish-release)
      else
        deny "$(cat <<'MSG'
PUSH PROTECTION: Direct push to 'main' is forbidden.

main only receives merges from release/ or hotfix/ branches.
Use /finish-hotfix or /finish-release to push merge results to main.

Workflow: release/<version> or hotfix/<name> → merge to main → push
MSG
)"
      fi
    else
      deny "$(cat <<'MSG'
PUSH PROTECTION: Pushing to 'main' from a non-main branch is forbidden.

main only receives merges from release/ or hotfix/ branches via pull request.

Workflow: develop -> release/<version> -> PR -> main
MSG
)"
    fi
  fi

  # Push to develop — allowed ONLY during finish workflows
  # (when you're ON develop after merging main into it for hotfix/release sync)
  if echo "$command" | grep -qP 'git\s+push\b.*(\s+develop(\s|$)|:develop(\s|$))'; then
    if [[ "$current_branch" == "develop" ]]; then
      # Check if HEAD is a merge commit (legitimate sync from main)
      if git log -1 --pretty=%P HEAD 2>/dev/null | grep -q ' '; then
        : # Allow — this is a merge commit push (syncing develop with main)
      else
        deny "$(cat <<'MSG'
PUSH PROTECTION: Direct push to 'develop' is forbidden.

Push your feature branch and open a pull request instead.
Only merge-commit pushes are allowed (from /finish-hotfix or /finish-release).

Workflow: feature/<name> -> git push -> PR -> develop
MSG
)"
      fi
    else
      deny "$(cat <<'MSG'
PUSH PROTECTION: Pushing to 'develop' from a non-develop branch is forbidden.

Push your feature branch and open a pull request instead.

Workflow: feature/<name> -> git push -> PR -> develop
MSG
)"
    fi
  fi

  # Block bare push when on protected branch (only if NOT a merge commit)
  if echo "$command" | grep -qP 'git\s+push(\s+-u)?\s+\w+\s*$' ||
     echo "$command" | grep -qP 'git\s+push\s*$'; then
    if [[ "$current_branch" == "main" || "$current_branch" == "develop" ]]; then
      # Allow if HEAD is a merge commit (finish workflow)
      if git log -1 --pretty=%P HEAD 2>/dev/null | grep -q ' '; then
        : # Allow — merge commit push
      else
        deny "$(cat <<MSG
PUSH PROTECTION: You are on '$current_branch'. Direct push is forbidden.

Switch to a feature/hotfix/release branch first, or use /finish-hotfix or /finish-release for merge workflows.
MSG
)"
      fi
    fi
  fi
fi

# ================================================================
# 6. STAGING DISCIPLINE
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

# ================================================================
# 7. MERGE PROTECTION — Only allowed merges
# ================================================================

if echo "$command" | grep -qE 'git\s+merge'; then
  merge_target=""
  if echo "$command" | grep -qP 'git\s+merge\s+\S'; then
    merge_target=$(echo "$command" | grep -oP '(?<=merge\s)\S+' | head -1)
  fi

  if [[ -n "$merge_target" ]]; then
    # Block merging INTO main from anything other than hotfix/, release/, or main itself
    if [[ "$current_branch" == "main" ]]; then
      if ! echo "$merge_target" | grep -qP '^(hotfix/|release/)'; then
        deny "$(cat <<MSG
MERGE PROTECTION: Cannot merge '$merge_target' into main.

main only accepts merges from:
  - hotfix/<name>  (urgent production fixes)
  - release/<version>  (prepared releases)

Use a release branch: git checkout -b release/<version> from develop
MSG
)"
      fi
    fi

    # Block merging INTO develop from unexpected sources
    # Allowed: feature/*, main (for hotfix/release sync), hotfix/*, release/*
    if [[ "$current_branch" == "develop" ]]; then
      if ! echo "$merge_target" | grep -qP '^(feature/|hotfix/|release/|main$)'; then
        deny "$(cat <<MSG
MERGE PROTECTION: Cannot merge '$merge_target' into develop.

develop accepts merges from:
  - feature/<name>  (completed features)
  - main  (hotfix/release sync)
  - hotfix/<name> or release/<name>  (direct merge)
MSG
)"
      fi
    fi
  fi
fi

# All checks passed
exit 0
