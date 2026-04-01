---
name: crispy-design
description: "Stage 3 of Crispy: Interactive design discussion with the human. Aligns on architecture, patterns, and open questions BEFORE any planning or coding."
---

# Crispy Stage 3 — Design Discussion

This is the most important stage for human-agent alignment. You brain-dump everything you've found and everything you think the user wants, then let them do "brain surgery" on your understanding before proceeding.

## Inputs

Read:
- `.crispy/ticket.md` — what we're building
- `.crispy/research.md` — what we learned about the codebase

## Process

### 1. Mark task in progress

Update the "Crispy: Design" task to `in_progress`.

### 2. Present the design discussion

Write a ~200-line design document covering:

**Current State** — What exists today (from research). Summarize the relevant parts of the codebase.

**Desired End State** — What the finished feature looks like. Your interpretation of the ticket.

**Patterns to Follow** — Which codebase patterns are relevant. Present ALL patterns you found and let the user confirm or correct.
- This is critical — if you found the wrong pattern, the user must catch it HERE, not after 2,000 lines of code.

**Design Decisions** — List decisions that need to be made. For each, present options with tradeoffs. Do NOT pick one — let the user decide.

**Open Questions** — Things you're unsure about. Ask explicitly.

### 3. Present to user and iterate

Show the design document and ask: **"Does this match your understanding? Any patterns I got wrong? Any decisions you want to make now?"**

This is interactive. Go back and forth. The user may:
- Correct a pattern ("No, we don't do atomic SQL updates that way — use the pattern in `src/db/transactions.ts` instead")
- Make a design decision ("Option B, we need tenant isolation")
- Add context you missed ("There's also a webhook system that needs to be updated")
- Remove scope ("Skip the admin UI for now, we'll do that later")

Keep iterating until the user approves.

### 4. Write artifact

Write the approved design to `.crispy/design.md`:

```markdown
# Design Discussion

## Current State
[summarized codebase context]

## Desired End State
[what we're building]

## Patterns to Follow
[confirmed patterns with file references]

## Resolved Decisions
- [Decision 1]: [chosen option] — [reason]
- [Decision 2]: [chosen option] — [reason]

## Scope
- In scope: [list]
- Out of scope: [list]

## Constraints
[any constraints the user mentioned]
```

### 5. Complete and hand off

Mark the "Crispy: Design" task as `completed`.

Tell the user: **"Design locked. Next I'll create the structure outline — the phases and order of implementation."**

Then invoke the `crispy-outline` skill.
