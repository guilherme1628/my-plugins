#!/bin/bash
# Injects a reminder about the Crispy workflow at session start.

cat <<'REMINDER'
# Crispy — Structured Feature Workflow

For non-trivial features, use `/crispy` to run the 7-stage pipeline:
**Questions → Research → Design → Outline → Plan → Implement → PR**

Each stage produces a focused artifact in `.crispy/` and tracks progress via tasks.
Key principle: don't outsource the thinking — align on design BEFORE writing code.
REMINDER
