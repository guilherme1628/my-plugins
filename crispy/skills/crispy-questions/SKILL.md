---
name: crispy-questions
description: "Stage 1 of Crispy: Generate targeted research questions from a ticket. Decomposes the task into codebase questions that will guide objective research."
---

# Crispy Stage 1 — Questions

Generate focused research questions that will guide codebase exploration. The goal is to decompose the ticket into questions that touch all relevant parts of the codebase WITHOUT revealing implementation intent.

## Inputs

Read `.crispy/ticket.md` for the task description.

## Process

### 1. Mark task in progress

Update the "Crispy: Questions" task to `in_progress`.

### 2. Analyze the ticket

Identify:
- Which systems/modules will be touched
- What existing patterns need to be understood
- What data flows are involved
- What boundaries exist (APIs, services, database)

### 3. Generate 5-10 research questions

Each question should cause a researcher to explore a specific vertical slice of the codebase. Questions must be:

- **Objective** — ask "how does X work?" not "how should we change X?"
- **Specific** — target a concrete part of the codebase
- **Independent** — each question can be answered without the others

Good questions:
- "How do API endpoints handle authentication and authorization?"
- "Trace the data flow for tenant-scoped queries from API to database"
- "What patterns does the codebase use for background job processing?"

Bad questions (these leak implementation intent):
- "How should we add a new endpoint for X?"
- "What's the best way to implement Y?"
- "Where should we put the new Z feature?"

### 4. Present questions to the user

Show the questions and ask: **"Do these cover the right areas? Want to add, remove, or refine any?"**

Incorporate feedback.

### 5. Write artifact

Write the final questions to `.crispy/questions.md` with this structure:

```markdown
# Research Questions

Generated from: [ticket summary]

1. [question]
2. [question]
...
```

### 6. Complete and hand off

Mark the "Crispy: Questions" task as `completed`.

Tell the user: **"Questions ready. Running research next — this will use a subagent with a fresh context window so the research stays objective."**

Then invoke the `crispy-research` skill.
