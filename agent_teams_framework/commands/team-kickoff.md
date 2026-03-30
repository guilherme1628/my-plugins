# Team Kickoff

## Purpose
Guided setup for an Agent Teams session. Gathers project context, auto-fills a team checklist, presents it for approval, writes a shadow log, and spawns the team.

## Arguments
- `$ARGUMENTS` — optional freeform brief describing what the team should accomplish

## Workflow

### Step 1: Gather Context (run in parallel)
- Read `.session/state.md` (if exists) for current project state
- Read `.session/team-history.md` (if exists) for past team lessons
- Run `git status`, `git log -5 --oneline`, `git branch --show-current`
- Glob for key files: `README*`, `package.json`, `CLAUDE.md`, `Cargo.toml`, `pyproject.toml`, `tsconfig.json` — read first few found
- Parse `$ARGUMENTS` as the user's brief (may be empty)

### Step 2: If No Brief Provided
- Present a short summary of the current project state
- Ask: "What do you want the team to accomplish?"
- Wait for response before continuing

### Step 3: Auto-Fill Checklist
From gathered context + user's brief, generate ALL of the following:

| Field | How to Fill |
|-------|------------|
| **Goal** | Extract from user's brief — one sentence |
| **Scope** | Infer directories/files involved from the goal + git state |
| **Team size** | Default 3. Increase only if goal clearly requires 4-5 distinct domains. Never exceed 5. |
| **Roles** | Infer from goal. Common patterns: implementer+tester+reviewer, frontend+backend+QA, researcher+implementer+tester |
| **File ownership** | Map each role to directories/files from scope. No overlap. |
| **Communication rules** | Start with these defaults, add goal-specific rules: (1) Agree on interfaces/contracts before implementing. (2) Don't message during implementation unless blocked. (3) Report completion to team lead when done. |
| **Success criteria** | Concrete, verifiable. "Tests pass" not "code works." |
| **Model selection** | Default: Opus for lead (already running), Sonnet for implementers, Haiku for researchers/read-only roles. |
| **Worktree** | Yes if 2+ agents write to overlapping areas. No for read-only agents. |
| **Cost estimate** | "{N} agents at ~{N}x single-agent token cost. With model routing: ~{reduced}x." |

### Step 4: Check Past Lessons
IF `.session/team-history.md` exists:
- Scan for lessons from this project or similar team patterns
- Include relevant warnings in the checklist presentation
- Example: "Past lesson: claude-code-guide agents can't shut down. Use general-purpose instead."

### Step 5: Anti-Pattern Check
Before presenting, validate the checklist against these rules. If any trigger, add a warning:

| Anti-Pattern | Check | Warning |
|-------------|-------|---------|
| Solo work disguised as team | Goal is simple, < 15 min for one agent | "This might not need a team. Consider a single agent or subagent." |
| Too many agents | Team size > 5 | "Teams > 5 have diminishing returns. Brooks's Law applies to agents too." |
| No file ownership | Roles overlap on same files | "Multiple agents writing to the same files will cause conflicts." |
| Research-only team | All roles are research/read-only | "Use parallel subagents instead — cheaper, no coordination overhead." |
| Planning with a team | Goal is to plan/design, not implement | "Use a solo agent to plan, then a team to execute." |
| claude-code-guide in team | Any role uses claude-code-guide subagent_type | "claude-code-guide agents can't process shutdown requests. Use general-purpose or Explore instead." |

### Step 6: Present Checklist + Confirm
Display the filled checklist as a clear, readable table. Include:
- The auto-filled fields
- Any anti-pattern warnings
- Any relevant past lessons
- The cost estimate

Then ask: **"Ready to go? Or describe changes."**

IF user says "go", "yes", "let's go", "proceed", or similar → continue to Step 7
IF user describes changes → apply changes, re-present checklist, ask again

### Step 7: Write Shadow Log
Write `.session/active-team.md` with the approved checklist:

```
# Active Team
**Name**: {team-name}
**Created**: {YYYY-MM-DD HH:MM}
**Goal**: {goal}

## Roles
| Role | Agent Name | Subagent Type | Model | Worktree | Files Owned |
|------|-----------|---------------|-------|----------|-------------|
| {role} | {name} | {type} | {model} | {yes/no} | {files} |

## Tasks
| # | Subject | Owner | Blocked By | Description |
|---|---------|-------|------------|-------------|
| 1 | {subject} | {role} | — | {description} |
| 2 | {subject} | {role} | #1 | {description} |

## Communication Rules
1. {rule}
2. {rule}

## Success Criteria
- {criterion}
```

### Step 8: Spawn Team
Execute in this order:

1. **TeamCreate** — use a slug from the goal as team name
2. **TaskCreate** — one per task from the checklist, with detailed descriptions
3. **TaskUpdate** — set up blockedBy dependencies
4. **Spawn agents** — one per role, using the Agent tool with:
   - `team_name`: the team name
   - `name`: the role name (slug)
   - `subagent_type`: from checklist (default `general-purpose` for implementers, `Explore` for researchers)
   - `model`: from checklist
   - `isolation`: `"worktree"` if checklist says yes
   - `prompt`: a role-specific brief containing:
     - Project summary (2-3 sentences from session state + key files)
     - Their assigned tasks
     - Their file ownership (what they can write to)
     - Communication rules
     - Success criteria
     - Relevant past lessons from team-history.md

5. **Report** to user:
   - "Team `{name}` is live with {N} agents."
   - List each agent with their role and first task
   - "Run `/team-handoff` when the team is done."

## Important Notes
- Each agent brief should be CONCISE — 10-20 lines max. Agents can explore the codebase themselves.
- Never use `claude-code-guide` as subagent_type for team agents.
- Default to `general-purpose` for agents that need to write code.
- Default to `Explore` for agents that only need to read/research.
- Always set `run_in_background: true` for team agents spawned after the first.
