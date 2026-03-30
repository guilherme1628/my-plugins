# Team Handoff

## Purpose
Capture team outcomes, run a retrospective, update session state with lessons learned, and shut down the team. Must be run while the team is still alive (before manual shutdown).

## Workflow

### Step 1: Verify Team Exists
- Read `.session/active-team.md`
- IF not found: warn "No active team found. Was `/team-kickoff` used to start it?" and STOP
- Parse team name, goal, roles, tasks from shadow log

### Step 2: Gather Team State (run in parallel)
- `TaskList` — get current task statuses (may be partially available)
- `git diff --stat` — files changed since team started
- `git log --oneline` — commits made during team session
- Read `.session/state.md` — current session context
- Read `.session/active-team.md` — the planned team structure

### Step 3: Compare Plan vs Reality
Using shadow log (what was planned) + git state (what actually happened):

- **Completed tasks**: which planned tasks got done?
- **Incomplete tasks**: which are still in progress or stuck?
- **Unplanned work**: any files changed that weren't in the scope?
- **Files changed**: full list with diffs summary

### Step 4: Infer Retrospective
From the conversation history, task states, and git state, build:

- **What worked**: tasks that completed cleanly, good coordination examples
- **What failed**: stuck agents, zombie agents, manual interventions needed, duplicate work, file conflicts
- **Decisions made**: any API contracts, architecture choices, or conventions the agents established
- **Lessons**: concrete, actionable rules for future teams. Format each as: "When {situation}, do {action} because {reason}."

Examples of good lessons:
- "When spawning fetch-only agents, use background subagents instead of team agents — cheaper, no coordination overhead."
- "When using 3+ agents writing code, always assign file ownership — prevents overwrite conflicts."
- "When an agent needs to shut down, never use claude-code-guide type — it can't process shutdown requests."

### Step 5: Present Retrospective
Display to the user:

```
## Team Handoff: {team-name}

**Goal**: {what was planned}
**Outcome**: {what actually happened — 1-2 sentences}

### Results
| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| {task} | completed/incomplete/stuck | {agent} | {notes} |

### Files Changed
{git diff --stat output}

### What Worked
- {item}

### What Failed
- {item}

### Lessons for Next Time
- {lesson}

### Cost Estimate
{N} agents x ~{estimate} = ~{total}x single agent
```

Ask: **"Anything to add or correct before I save?"**

IF user adds corrections → incorporate them
IF user says "looks good", "save", "go" → continue

### Step 6: Update Session State

**Append to `.session/team-history.md`** (create if doesn't exist):

```
## Team: {name} — {YYYY-MM-DD}
**Goal**: {goal}
**Outcome**: {1-2 sentence summary}
**Team**: {N} agents ({role1}, {role2}, {role3})
**Files changed**: {count} files
**Lessons**:
- {lesson 1}
- {lesson 2}
**Cost**: ~{N}x single agent
```

**Update `.session/state.md`**:
- Add completed work to "Completed This Session" section
- Update "Active Work" if the team's goal was the active task
- Note any incomplete work in "Next Actions"

### Step 7: Shutdown Team
- Send `{"type": "shutdown_request"}` to all teammates via SendMessage
- Wait up to 30 seconds for shutdown confirmations
- IF any agent doesn't shut down: note it in the report, don't block
  - Log: "Agent {name} did not shut down. This is a known issue with {type} agent types."

### Step 8: Cleanup
- Delete `.session/active-team.md` (team is no longer active)
- Report to user:
  - "Team `{name}` dissolved."
  - "{N} tasks completed, {M} lessons saved to `.session/team-history.md`."
  - "Uncommitted changes: {yes/no}"
  - IF uncommitted: "Consider committing before moving on."

## Important Notes
- This command MUST be run while agents are still alive for best results.
- If run after agents are gone, it falls back to the shadow log + git diff (less detailed but still useful).
- The retrospective is inferred from conversation + git, not manually written — but the user can correct it.
- Lessons are append-only in team-history.md — they accumulate across sessions.
