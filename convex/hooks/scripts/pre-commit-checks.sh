#!/bin/bash
set -euo pipefail

# PreToolUse hook for Bash tool: validates Convex best practices before git commit.
# Reads Claude Code hook JSON from stdin, outputs JSON on stdout.

input=$(cat)
if [ -z "$input" ]; then
  exit 0
fi

tool_name=$(echo "$input" | jq -r '.tool_name // empty')
command=$(echo "$input" | jq -r '.tool_input.command // empty')

# Only check git commit commands
if [[ "$tool_name" != "Bash" ]] || [[ ! "$command" =~ (^|[[:space:]])git[[:space:]]+commit($|[[:space:]]) ]]; then
  exit 0
fi

# Find convex directory
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
CONVEX_DIR="${PROJECT_DIR}/convex"

if [ ! -d "$CONVEX_DIR" ]; then
  exit 0
fi

# Check for Date.now() in query functions
DATE_NOW_IN_QUERIES=$(
  grep -rn "Date\.now()" "$CONVEX_DIR"/ --include="*.ts" --include="*.js" \
    | grep -B 5 "query({" \
    | grep "Date\.now()" || true
)
if [ -n "$DATE_NOW_IN_QUERIES" ]; then
  echo '{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Commit blocked: Date.now() detected near query() in convex/. Queries must be deterministic for reactivity. Pass time as an argument or use status fields updated by scheduled functions."}'
  exit 0
fi

# Check for .filter() on db.query()
FILTER_ON_QUERIES=$(
  grep -rn "\.query(.*)\s*\.filter(" "$CONVEX_DIR"/ --include="*.ts" --include="*.js" || true
)
if [ -n "$FILTER_ON_QUERIES" ]; then
  echo '{"hookSpecificOutput":{"permissionDecision":"deny"},"systemMessage":"Commit blocked: .filter() detected on db.query() in convex/. Use .withIndex() for indexed access instead of full table scans."}'
  exit 0
fi

# All checks passed
exit 0
