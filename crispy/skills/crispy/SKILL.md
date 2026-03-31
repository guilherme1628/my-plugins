---
name: crispy
description: Structured 7-stage research-plan-implement workflow for feature development. Use when planning and implementing features, tasks, or tickets. Produces focused artifacts at each stage with human checkpoints.
---

# Crispy — Structured Feature Workflow

Orchestrates 7 focused stages from ticket to pull request. Each stage has its own context, produces one artifact, and tracks progress via tasks.

## When to Use

Any time you're about to implement a feature, task, or ticket that touches multiple files or requires design decisions. NOT for trivial one-file changes.

## Stage Pipeline

```
Ticket/Task → [Questions] → [Research] → [Design] → [Outline] → [Plan] → [Implement] → [PR]
```

## How to Start

### 1. Get the ticket

Ask the user: **"What are we building? Paste the ticket, describe the feature, or point me to an issue."**

If the user provides a ticket URL, fetch it. If they describe it, capture it verbatim.

### 2. Create the artifacts directory

Create `.crispy/` in the project root if it doesn't exist. Write the ticket to `.crispy/ticket.md`.

### 3. Create the task pipeline

Use TaskCreate to create these 7 tasks:

1. `Crispy: Questions — generate research questions`
2. `Crispy: Research — gather codebase facts`
3. `Crispy: Design — interactive design discussion`
4. `Crispy: Outline — structure and phases`
5. `Crispy: Plan — tactical implementation doc`
6. `Crispy: Implement — execute in worktree`
7. `Crispy: PR — create pull request`

### 4. Begin Stage 1

Immediately invoke the `crispy-questions` skill to start the pipeline.

## Stage Artifacts

Each stage reads previous artifacts and writes one:

| Stage | Reads | Writes |
|-------|-------|--------|
| Questions | `.crispy/ticket.md` | `.crispy/questions.md` |
| Research | `.crispy/questions.md` (NOT ticket) | `.crispy/research.md` |
| Design | `ticket.md` + `research.md` | `.crispy/design.md` |
| Outline | `ticket.md` + `research.md` + `design.md` | `.crispy/outline.md` |
| Plan | all above | `.crispy/plan.md` |
| Implement | `plan.md` | code changes in worktree |
| PR | all artifacts + code | pull request |

## Rules

1. Never skip stages — each builds on the previous
2. Never combine stages into one context window
3. Research MUST run as a subagent without the ticket
4. Design and Outline MUST be interactive — get human approval before proceeding
5. Each skill marks its task complete before handing off
6. If the user says "skip to X", mark intermediate stages as completed and proceed
