---
name: crispy-pr
description: "Stage 7 of Crispy: Create a pull request following git-standards. Includes design context, phase summary, and testing checklist."
---

# Crispy Stage 7 — Pull Request

Create a pull request following git-standards conventions. The PR includes context from the design discussion and outline so reviewers understand the decisions, not just the code.

## Inputs

Read:
- `.crispy/ticket.md` — original task
- `.crispy/design.md` — design decisions and patterns
- `.crispy/outline.md` — phases and checkpoints

## Process

### 1. Mark task in progress

Update the "Crispy: PR" task to `in_progress`.

### 2. Push the feature branch (git-standards)

```bash
git push -u origin feature/<name>
```

### 3. Gather PR context

Run these commands to understand what's being shipped:
- `git log develop..HEAD --oneline` — all commits
- `git diff develop...HEAD --stat` — files changed summary

### 4. Create the PR (git-standards)

PR targets `develop` (features always merge to develop, never main).

PR title follows conventional commit format:
```
feat: implement tenant-scoped spline reticulation
```

PR body structure:

```markdown
## Summary

[2-3 bullet points from design.md — WHAT was built and key decisions]

## Design Decisions

[Pull key resolved decisions from design.md so reviewers see the WHY]

## Implementation Phases

[List phases from outline.md with checkpoints — shows the work was verified incrementally]

## Test Plan

- [ ] [checkpoint from phase 1]
- [ ] [checkpoint from phase 2]
- [ ] [additional verification steps]

## Artifacts

Design discussion, research, and outline available in `.crispy/` directory.
```

Use `gh pr create` with HEREDOC for the body.

### 5. Present PR to user

Show the PR URL and summary. Ask: **"PR created. Want to review it together, or is it ready for team review?"**

### 6. Complete

Mark the "Crispy: PR" task as `completed`.

Tell the user: **"Crispy workflow complete. All 7 stages done. PR is ready for review."**
