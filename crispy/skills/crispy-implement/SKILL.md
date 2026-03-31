---
name: crispy-implement
description: "Stage 6 of Crispy: Execute the plan in an isolated worktree using a feature branch. Follows git-standards for branching and commits."
---

# Crispy Stage 6 — Implement

Execute the tactical plan in an isolated worktree with a proper feature branch. Each phase is implemented by a subagent with a fresh context window.

## Inputs

Read `.crispy/plan.md` for the implementation steps.
Read `.crispy/outline.md` for the phase checkpoints.
Read `.crispy/design.md` for confirmed patterns and decisions.

## Process

### 1. Mark task in progress

Update the "Crispy: Implement" task to `in_progress`.

### 2. Create feature branch (git-standards)

Follow git-standards Gitflow conventions:

```bash
# Ensure develop is up to date
git checkout develop
git pull origin develop

# Create feature branch with descriptive name
git checkout -b feature/<name-from-ticket>
```

Branch naming rules:
- Lowercase, hyphens between words
- Descriptive: `feature/tenant-scoped-spline-reticulation` not `feature/update`

### 3. Implement phase by phase

For EACH phase in the plan, spawn a subagent using the Agent tool:

```
Read these files for context:
- .crispy/design.md (patterns and decisions)
- .crispy/plan.md (implementation steps for Phase N)

Implement Phase N: [phase goal]

Steps:
[paste the specific steps for this phase from plan.md]

Rules:
- Follow the patterns confirmed in design.md
- Stage SPECIFIC files only (never git add . or git add -A)
- Commit with conventional message format: type: description
- Present tense, under 72 chars
- One commit per logical change

After implementing, run the checkpoint:
[paste checkpoint from outline.md]
```

### 4. Between phases

After each subagent completes:
- Read the changes it made
- Verify the checkpoint passed
- If the checkpoint failed, fix before proceeding to next phase
- Tell the user which phase completed and what's next

### 5. Commit discipline (git-standards)

Every commit must follow conventional commits:
- `feat: implement tenant-scoped spline query endpoint`
- `feat: add spline reticulation worker`
- `test: add integration tests for spline API`
- `refactor: extract spline service from monolith`

Rules:
- Stage specific files: `git add src/api/splines.ts src/services/spline-service.ts`
- NEVER `git add .` or `git add -A`
- One commit per logical change within each phase
- No force push — ever

### 6. Complete and hand off

Mark the "Crispy: Implement" task as `completed`.

Tell the user: **"Implementation complete. All phases passed their checkpoints. Ready to create the PR."**

Then invoke the `crispy-pr` skill.
