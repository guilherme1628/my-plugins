---
name: crispy-research
description: "Stage 2 of Crispy: Objective codebase research via subagent. Gathers facts about how the code works today without opinions or implementation suggestions."
---

# Crispy Stage 2 — Research

Gather objective facts about the codebase by sending a subagent to answer the research questions. The subagent MUST NOT see the ticket — this keeps the research free of opinions.

## Inputs

Read `.crispy/questions.md` for the research questions.

## Process

### 1. Mark task in progress

Update the "Crispy: Research" task to `in_progress`.

### 2. Spawn research subagent

Use the Agent tool to spawn a subagent with this prompt:

```
Read the file .crispy/questions.md. It contains research questions about a codebase.

For EACH question:
1. Search the codebase thoroughly (use Grep, Glob, Read)
2. Document ONLY facts about how the code works TODAY
3. Include file paths, function signatures, and relevant code snippets
4. Note patterns, conventions, and architectural decisions you observe

Rules:
- NO opinions or suggestions
- NO implementation ideas or recommendations
- NO "you should" or "consider" language
- ONLY describe what IS, not what COULD BE
- If you can't find an answer, say "Not found in codebase"

Write your findings to .crispy/research.md with this structure:

# Codebase Research

## Q1: [question text]
### Findings
[factual findings with file paths and code references]

## Q2: [question text]
### Findings
[factual findings]

... (repeat for all questions)

## Patterns Observed
[list recurring patterns, conventions, and architectural decisions found across questions]
```

### 3. Review research quality

After the subagent completes, read `.crispy/research.md` and verify:
- Each question has concrete findings (not vague summaries)
- File paths and code references are included
- No opinions or implementation suggestions leaked in
- The "Patterns Observed" section captures reusable conventions

If quality is poor, tell the user and offer to re-run with refined questions.

### 4. Complete and hand off

Mark the "Crispy: Research" task as `completed`.

Tell the user: **"Research complete. Next is the design discussion — this is where we align on WHAT to build and HOW. I'll present what I found and ask for your input."**

Then invoke the `crispy-design` skill.
