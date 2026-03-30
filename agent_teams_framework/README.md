# Agent Teams Framework

A Claude Code plugin for disciplined Agent Teams usage. Two commands that automate the team lifecycle with guided setup, context handoff, and compound learning.

## Prerequisites

- Claude Code v2.1.32+
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings
- The [session plugin](../session) installed (for `.session/state.md` integration)

## Commands

### `/team-kickoff [brief]`

Guided team setup. Gathers project context, auto-fills a checklist, presents it for approval, and spawns the team.

```
/team-kickoff Add full-text search to the API with schema changes and tests
```

What it does:
1. Reads session state, git state, key files, and past team lessons
2. Auto-generates: goal, scope, roles, file ownership, communication rules, cost estimate
3. Shows the checklist — you say "go" or describe changes
4. Writes a shadow log to `.session/active-team.md`
5. Spawns the team with role-specific context briefs

### `/team-handoff`

Captures team outcomes, runs a retrospective, saves lessons, and shuts down the team.

```
/team-handoff
```

What it does:
1. Compares planned tasks (shadow log) vs actual results (git diff)
2. Infers what worked, what failed, and concrete lessons
3. Saves lessons to `.session/team-history.md` (compound learning)
4. Updates `.session/state.md` with completed work
5. Shuts down all agents

**Run this while agents are still alive** for best results.

## Session Files

| File | Purpose | Created By |
|------|---------|-----------|
| `.session/state.md` | Session lifecycle (from session plugin) | `/resume-session` |
| `.session/active-team.md` | Shadow log of current team | `/team-kickoff` |
| `.session/team-history.md` | Append-only lessons from past teams | `/team-handoff` |

## Decision Tree

```
Is your task < 15 min for one agent?
├── Yes → Use a single agent. No team needed.
└── No → Can the work be split into independent domains?
    ├── No → Use a single agent with subagents for focused subtasks.
    └── Yes → Are domains truly parallel (not tightly coupled)?
        ├── No → Use a pipeline (sequential dependencies).
        └── Yes → Do agents need to communicate during work?
            ├── No → Use parallel subagents (run_in_background: true). Cheaper.
            └── Yes → Use Agent Teams via /team-kickoff.
```

## References

Deep-dive material in `references/`:
- `klaassen-swarm-orchestration.md` — Complete API reference + 6 orchestration patterns
- `mejba-agent-teams-playbook.md` — Experience report with 5 costly mistakes
- `osmani-code-agent-orchestra.md` — Strategic framework + quality gate patterns
