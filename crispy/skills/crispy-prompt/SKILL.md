---
name: crispy-prompt
description: Lightweight crispy flow for small-to-medium tasks. Runs research and planning via subagents with fresh context windows, then summarizes before implementation. No artifacts, no ceremony — just structured thinking.
---

# Crispy Prompt — Lightweight Structured Flow

A condensed version of the full `/crispy` pipeline. Uses subagents for unbiased research and planning (fresh context windows), but keeps everything in-conversation with a single human checkpoint before implementation.

## When to Use

Small-to-medium tasks that benefit from structured thinking but don't warrant the full 7-stage crispy ceremony. If the task is complex enough to need interactive design discussion or multi-phase implementation, use full `/crispy` instead.

## Input

The user provides the task inline with the command, e.g.:
```
/crispy-prompt add retry logic to the API client
```

If no description is provided, ask: **"What are we building?"**

Capture the task description as `TASK`.

## Flow

### Step 1 — Generate Research Questions

Analyze `TASK` and generate 3-5 objective research questions. These should:
- Target the specific parts of the codebase the task will touch
- Ask "how does X work?" not "how should we change X?"
- Be concrete enough for a researcher to answer by reading code

Do NOT show these to the user — this is internal to the flow.

### Step 2 — Research Subagent

Spawn a subagent using the **Agent tool** with `subagent_type: "Explore"`. The subagent gets ONLY the research questions — NOT the task description. This keeps research objective.

Prompt the subagent:

```
Answer these research questions about the codebase. For each question:
1. Search thoroughly (Grep, Glob, Read)
2. Document ONLY facts — how the code works TODAY
3. Include file paths, function signatures, and relevant snippets
4. Note patterns and conventions you observe

Rules:
- NO opinions or suggestions
- NO "you should" or "consider" language
- ONLY describe what IS, not what COULD BE
- If you can't find an answer, say "Not found in codebase"

Questions:
{paste the 3-5 questions here}

Report your findings concisely — under 400 words total.
```

### Step 3 — Plan Subagent

Spawn a second subagent using the **Agent tool** with `subagent_type: "Plan"`. This subagent gets the task AND the research findings.

Prompt the subagent:

```
Given this task and codebase research, create a concise implementation plan.

## Task
{TASK}

## Codebase Research
{paste research findings}

Produce a plan with:
1. Files to create or modify (with paths)
2. What changes to make in each file (specific, not vague)
3. Patterns from the research to follow
4. Order of operations
5. How to verify it works

Keep it tactical and concise — under 300 words. No preamble.
```

### Step 4 — Summary Checkpoint

Present a summary to the user combining research and plan:

```markdown
## Research Summary
[2-3 bullet points: what exists today, key patterns found, relevant files]

## Plan
[the plan from Step 3, formatted cleanly]

## Estimated Scope
[number of files, rough size of changes: small/medium]
```

Then ask: **"Want me to go ahead, adjust anything, or dive deeper with full `/crispy`?"**

### Step 5 — Implement

Only after user approval:

1. Create a feature branch following git-standards (if not already on one)
2. Implement the plan
3. Stage and present changes for review

Do NOT commit automatically — let the user decide when to commit.

## Rules

1. **Always use subagents** for research and planning — fresh context windows prevent anchoring bias
2. **Never skip the summary** — the user checkpoint before implementation is non-negotiable
3. **No `.crispy/` artifacts** — everything lives in the conversation
4. **Keep it fast** — this is the lightweight path; don't over-elaborate
5. **Escape hatch** — if the user wants more depth at the summary checkpoint, suggest full `/crispy`
