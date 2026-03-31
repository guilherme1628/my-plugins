---
name: crispy-outline
description: "Stage 4 of Crispy: Create a high-level structure outline with vertical phases and checkpoints. Like C header files — signatures and types, not full implementation."
---

# Crispy Stage 4 — Structure Outline

Create a high-level outline of HOW we get from current state to desired end state. This is NOT the detailed plan — it's the phases, order, and checkpoints. Think "C header files" — just signatures and types, enough to see if the approach is right.

## Inputs

Read:
- `.crispy/ticket.md` — the task
- `.crispy/research.md` — codebase facts
- `.crispy/design.md` — approved design

## Process

### 1. Mark task in progress

Update the "Crispy: Outline" task to `in_progress`.

### 2. Create vertical phases

Break the work into vertical slices, NOT horizontal layers. Each phase should be independently testable.

**Vertical (correct):**
- Phase 1: Mock API endpoint + basic frontend wiring → verify request/response cycle
- Phase 2: Real service layer + database migration → verify data persistence
- Phase 3: Full integration + error handling → verify end-to-end

**Horizontal (wrong):**
- Phase 1: All database changes
- Phase 2: All service layer changes
- Phase 3: All API changes
- Phase 4: All frontend changes

### 3. For each phase, include

- **Goal** — one sentence: what this phase accomplishes
- **Files to create/modify** — list them
- **Key signatures** — new types, function signatures, API shapes (not full implementation)
- **Checkpoint** — how to verify this phase works before moving on

### 4. Present to user and iterate

Show the outline and ask: **"Does this order make sense? Any phases to swap, split, or merge? Any checkpoints you want to add?"**

The user may:
- Swap phase order ("Do the database migration first, I want to validate the schema")
- Add a testing phase ("Add a checkpoint after phase 2 to run integration tests")
- Split a large phase ("Phase 3 is too big, split the error handling into its own phase")
- Merge small phases ("Phases 2 and 3 can be one, they're trivial")

### 5. Write artifact

Write the approved outline to `.crispy/outline.md`:

```markdown
# Structure Outline

## Phase 1: [goal]
**Files:** [list]
**Key signatures:**
- `functionName(param: Type): ReturnType`
- `interface NewEntity { ... }`
**Checkpoint:** [how to verify]

## Phase 2: [goal]
**Files:** [list]
**Key signatures:**
- ...
**Checkpoint:** [how to verify]

...
```

Keep it under ~100 lines. This is the "2-page review" — concise enough for a teammate to review in 5 minutes.

### 6. Complete and hand off

Mark the "Crispy: Outline" task as `completed`.

Tell the user: **"Outline approved. Now I'll expand this into the detailed tactical plan for implementation."**

Then invoke the `crispy-plan` skill.
