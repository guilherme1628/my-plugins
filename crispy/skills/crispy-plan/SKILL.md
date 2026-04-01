---
name: crispy-plan
description: "Stage 5 of Crispy: Expand the outline into a detailed tactical plan for the implementing agent. This is a doc FOR the agent, not for human review."
---

# Crispy Stage 5 — Tactical Plan

Expand the approved outline into a detailed, step-by-step plan that the implementing agent can follow. This is a tactical document — the human has already aligned on design and outline. Just spot-check this one.

## Inputs

Read all artifacts:
- `.crispy/ticket.md`
- `.crispy/research.md`
- `.crispy/design.md`
- `.crispy/outline.md`

## Process

### 1. Mark task in progress

Update the "Crispy: Plan" task to `in_progress`.

### 2. Generate the plan as a subagent

Spawn a subagent using the Agent tool with this prompt:

```
Read these files:
- .crispy/ticket.md
- .crispy/research.md
- .crispy/design.md
- .crispy/outline.md

Create a detailed tactical implementation plan. For each phase from the outline, expand it into specific steps:

For each step:
1. The exact file to create or modify
2. What to add/change (specific code patterns from research.md)
3. Follow the patterns confirmed in design.md
4. Include the checkpoint from the outline

Format the plan following the phase structure from the outline.
Each phase should list its steps with enough detail for an agent to implement without ambiguity.

Write the plan to .crispy/plan.md
```

### 3. Present summary to user

After the subagent completes, read `.crispy/plan.md` and present a brief summary:
- Number of phases
- Number of steps per phase
- Total files affected
- Any surprises or deviations from the outline

Ask: **"Want to spot-check anything before I start implementing? The design and outline are already approved — this just expands them."**

### 4. Complete and hand off

Mark the "Crispy: Plan" task as `completed`.

Tell the user: **"Plan ready. Next I'll implement it in a worktree using a feature branch per git-standards."**

Then invoke the `crispy-implement` skill.
