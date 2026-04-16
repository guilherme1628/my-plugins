#!/bin/bash
# Injects Orchestra availability reminder at session start.

if [[ -d "$HOME/.orchestra" ]]; then
  SERVICE_DIR=""
  if [[ -f "$PWD/CLAUDE.md" ]]; then
    SERVICE_NAME="$(grep -m1 '^# ' "$PWD/CLAUDE.md" 2>/dev/null | sed 's/^# //' | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g; s/-\{2,\}/-/g; s/^-//; s/-$//')"
    if [[ -n "$SERVICE_NAME" && -d "$HOME/.orchestra/services/$SERVICE_NAME" ]]; then
      SERVICE_DIR="$HOME/.orchestra/services/$SERVICE_NAME"
    fi
  fi

  if [[ -n "$SERVICE_DIR" ]]; then
    cat <<REMINDER
# Orchestra — Multi-Session Coordination

This project is registered as an Orchestra service. Use \`/orchestra-join\` to join a session and start listening for tasks.

Quick commands: \`orch status <session>\`, \`orch join <session>\`, \`orch check <session>\`
REMINDER
  else
    cat <<REMINDER
# Orchestra — Multi-Session Coordination

Orchestra is available for coordinating work across Claude Code sessions.

- **To orchestrate**: \`/orchestra-conduct\` — break down goals and delegate to services
- **To join as worker**: \`/orchestra-join\` — listen for tasks from an orchestrator

Quick commands: \`orch new <session>\`, \`orch status <session>\`, \`orch join <session>\`
REMINDER
  fi
fi
