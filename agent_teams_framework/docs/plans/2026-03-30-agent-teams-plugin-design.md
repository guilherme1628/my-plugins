# Agent Teams Framework — Plugin Design

**Date**: 2026-03-30
**Status**: Approved via brainstorming session

## What It Is

A Claude Code plugin with two commands that automate team lifecycle:
- `/team-kickoff [brief]` — gathers context, auto-fills a checklist, spawns the team
- `/team-handoff` — captures outcomes, lessons, updates session state, shuts down team

## Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Playbook vs package | Plugin with commands | Commands act at the right moment; markdown sits unread |
| Checklist interaction | Hybrid: auto-fill + show + "go or change" | Respects user's time, still provides checkpoint |
| Context input | Session state + git + user brief | "Where are we" + "where are we going" |
| Edit flow | Freeform — say "go" or describe changes | No rigid editing protocol |
| Retrospective | Full, saved to .session/team-history.md | Compound learning loop |
| Separate /team-review | Merged into /team-handoff | Two teardown commands is ceremony |
| Skill/hook injection | None — command-only | User keeps full control |
| Task persistence | Shadow log in .session/active-team.md | Task JSON files are deleted after completion |

## Plugin Structure

```
agent_teams_framework/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── team-kickoff.md
│   └── team-handoff.md
├── references/
│   ├── klaassen-swarm-orchestration.md
│   ├── mejba-agent-teams-playbook.md
│   └── osmani-code-agent-orchestra.md
└── README.md
```

## /team-kickoff Flow

### Step 1: Gather Context (parallel)
- Read `.session/state.md` (if exists)
- Read `.session/team-history.md` (if exists — past lessons)
- `git status` + `git log -5` + `git branch --show-current`
- Glob for key files (package.json, CLAUDE.md, tsconfig.json, etc.)
- Parse user's brief from command arguments

### Step 2: Auto-Fill Checklist
From gathered context + brief, generate:

| Field | Source | Example |
|-------|--------|---------|
| Goal | User brief | "Add full-text search to API" |
| Scope | Brief + git state | `src/api/`, `src/db/`, `tests/` |
| Team size | Inferred from goal | 3 agents |
| Roles | Inferred from goal | backend, schema, tester |
| File ownership | Inferred from scope | backend owns `src/api/`, schema owns `src/db/` |
| Communication rules | Defaults + goal-specific | "Agree on search query interface before implementing" |
| Success criteria | Inferred from goal | "Search endpoint returns results, tests pass" |
| Model selection | Defaults | Opus lead, Sonnet devs, Haiku research |
| Worktree | Auto-detect | Yes if multiple agents writing code |
| Cost estimate | Team size based | "3 agents ~ 3-4x single agent tokens" |

### Step 3: Surface Past Lessons
If `.session/team-history.md` exists, scan for relevant lessons:
- Same project → always show
- Similar patterns (e.g., past "3-agent parallel" lessons) → show

### Step 4: Present + Confirm
Display filled checklist as a clear table. Show relevant past lessons.
Ask: "Ready to go? Or describe changes."

User says "go" or describes freeform changes.

### Step 5: Write Shadow Log
Write `.session/active-team.md` with:
- Team name, goal, timestamp
- All tasks with subjects, descriptions, owners
- Roles and file ownership map
- Dependencies between tasks

### Step 6: Spawn Team
- `TeamCreate` with team name
- `TaskCreate` per role with detailed descriptions
- `TaskUpdate` for dependencies
- Spawn agents with role-specific context briefs containing:
  - Project summary (from session state + key files)
  - Their specific scope and file ownership
  - Communication rules
  - Success criteria
  - Relevant past lessons

## /team-handoff Flow

### Step 1: Gather Team State (parallel)
- `TaskList` — current task statuses (if still available)
- Read `.session/active-team.md` — shadow log (reliable fallback)
- `git diff --stat` — files changed
- `git log --oneline` — commits during session
- Read `.session/state.md` — current session context

### Step 2: Build Retrospective
- **Outcomes**: what was built (from tasks + git)
- **Decisions**: API contracts, arch choices agents made
- **Files changed**: list with ownership attribution
- **What worked**: clean task completions, good coordination
- **What failed**: stuck tasks, manual interventions, zombie agents
- **Lessons**: concrete rules for future teams
- **Cost estimate**: team size x approximate tokens

### Step 3: Update Session State
- Append entry to `.session/team-history.md`:
  ```
  ## Team: {name} — {date}
  **Goal**: {what they were asked to do}
  **Outcome**: {what actually happened}
  **Team**: {N} agents ({roles})
  **Files changed**: {list}
  **Lessons**:
  - {lesson 1}
  - {lesson 2}
  **Cost**: ~{N}x single agent
  ```
- Update `.session/state.md` with completed work
- Delete `.session/active-team.md` (no longer active)
- Warn about uncommitted changes

### Step 4: Shutdown Team
- Send shutdown request to all teammates
- Wait for confirmations (with timeout awareness — some agents don't shut down)
- Report: "Team dissolved. {N} tasks completed. Lessons saved."

## Anti-Patterns (Embedded in /team-kickoff as warnings)

1. **Team for solo work** — if task < 15 min for one agent, don't use a team
2. **Team agents for fetch tasks** — use background subagents instead
3. **claude-code-guide agents in teams** — can't process shutdown, become zombies
4. **No file ownership** — agents overwrite each other's work
5. **Unstructured communication** — agents chat instead of building
6. **Same model for all roles** — Opus everywhere wastes tokens
7. **Planning with teams** — use solo agent to plan, then team to execute
8. **Ignoring past lessons** — team-history.md exists for a reason

## Cost Model (Embedded in /team-kickoff checklist)

| Team Size | Token Multiplier | When Worth It |
|-----------|-----------------|---------------|
| 2 agents | ~2-2.5x | Two clearly independent domains |
| 3 agents | ~3-4x | Frontend + backend + QA |
| 4-5 agents | ~4-6x | Large refactors, multiple modules |
| 5+ agents | ~6x+ | Diminishing returns, avoid |

With model routing (Sonnet/Haiku for workers): reduce by ~40-60%.
