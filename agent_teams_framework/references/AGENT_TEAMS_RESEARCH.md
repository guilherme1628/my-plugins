# Claude Code Agent Teams: Comprehensive Technical Research Report

**Researcher**: functionality-researcher@agent-teams-research
**Date**: 2026-03-30
**Status**: Research Complete
**Source**: Official Claude Code v2.1.32+ documentation + active system exploration

---

## Executive Summary

Agent Teams enable coordinated multi-agent development in Claude Code, with each teammate operating in a separate 1M-token context window. The system uses shared task lists with file-based locking, peer-to-peer messaging, and automatic task dependency resolution. Teams are experimental (research preview status), disabled by default, and require explicit enablement via environment variable.

Key finding: Agent Teams are substantially different from subagents. Teams provide true parallelism with independent agent autonomy, while subagents remain subordinate to a main conversation and cannot message each other directly.

---

## 1. Team Lifecycle & Configuration

### 1.1 Enablement & Requirements

**Activation Methods:**
- Environment variable: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Settings persistence: `~/.claude/settings.json` with `env` object
  ```json
  {
    "env": {
      "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
    }
  }
  ```

**Version & Model Requirements:**
- Minimum Claude Code version: **2.1.32** (released 2026-02-05)
- Required model: **Opus 4.6** (recommended for team lead)
- Teammate models: Any available (Sonnet, Haiku supported; specified per team)
- Status: **Experimental / Research Preview** — known limitations around session resumption, task coordination, shutdown behavior

### 1.2 Team Configuration File Structure

**Location**: `~/.claude/teams/{team-name}/config.json`

**Config File Schema**:
```json
{
  "name": "agent-teams-research",
  "description": "Human-readable team purpose",
  "createdAt": 1774876199859,
  "leadAgentId": "team-lead@agent-teams-research",
  "leadSessionId": "419e1e5f-847a-49dc-a2a6-db78ada23e8c",
  "members": [
    {
      "agentId": "team-lead@agent-teams-research",
      "name": "team-lead",
      "agentType": "coordinator",
      "model": "claude-opus-4-6[1m]",
      "joinedAt": 1774876199859,
      "tmuxPaneId": "",
      "cwd": "/path/to/project",
      "subscriptions": [],
      "backendType": "in-process"
    },
    {
      "agentId": "functionality-researcher@agent-teams-research",
      "name": "functionality-researcher",
      "agentType": "claude-code-guide",
      "model": "haiku",
      "prompt": "System prompt for this teammate...",
      "color": "blue",
      "planModeRequired": false,
      "joinedAt": 1774876229297,
      "tmuxPaneId": "in-process",
      "cwd": "/path/to/project",
      "subscriptions": [],
      "backendType": "in-process"
    }
  ]
}
```

**Key Fields**:
- `leadAgentId`: Fixed for team lifetime; cannot be promoted or transferred
- `agentType`: Defines teammate role and system behavior
- `tmuxPaneId`: Empty string for in-process mode, or tmux pane identifier for split-pane mode
- `backendType`: Currently "in-process" for in-process mode; "tmux" or "iterm2" for split-pane
- `planModeRequired`: Forces teammate into read-only plan mode until lead approves

### 1.3 Task List File Structure

**Location**: `~/.claude/tasks/{team-name}/`

**Task File Schema** (`{task-id}.json`):
```json
{
  "id": "1",
  "subject": "Research Agent Teams core functionality",
  "description": "Detailed task requirements...",
  "status": "pending|in_progress|completed",
  "owner": "functionality-researcher",
  "blocks": ["3"],
  "blockedBy": ["2"],
  "activeForm": "Researching Agent Teams functionality",
  "metadata": {}
}
```

**Task Status Workflow**:
- `pending` → `in_progress` → `completed`
- Blocked tasks cannot transition from `pending` until blocking tasks complete
- Dependencies auto-resolve: completing a blocking task unblocks dependents automatically

**Task Claiming Mechanism**:
- File-based locking prevents race conditions
- `.lock` files in task directory indicate claimed status
- `.highwatermark` files track task progress [UNCERTAIN: exact purpose]

---

## 2. Agent Spawning & Types

### 2.1 Available Agent Types

**Built-in Agent Types** (for main session / team leads):
- `coordinator` — Team lead agent for orchestration
- `general-purpose` — Full tool access, complex reasoning
- `claude-code-guide` — Specialized for Claude Code feature guidance

**Subagent Types** (for agents spawned within a session):
- `Explore` — Read-only, fast (Haiku), file search & codebase analysis
- `Plan` — Read-only research agent during plan mode
- `General-purpose` — Both exploration and modification
- `Bash` — Terminal command execution
- `statusline-setup` — Configuration helper
- `Claude Code Guide` — Feature documentation

**Agent Type Determination**:
- Explicitly specified at team creation: `"Create a team with 4 teammates...Use Sonnet for each teammate"`
- Claude infers from task description if not specified
- Each agent has isolated tool access defined by type

### 2.2 Subagent Spawning Parameters

**Agent Tool Parameters** (called from tasks or subagent code):
```javascript
Agent({
  agent_type: "explore|plan|general-purpose|custom-name",
  description: "What this agent should do",
  prompt: "System prompt override",
  model: "sonnet|opus|haiku",
  run_in_background: true|false,
  mode: "auto|plan|acceptEdits|bypassPermissions|default|dontAsk",
  isolation: "worktree",
  maxTurns: 10
})
```

**Parameter Details**:

#### agent_type (subagent_type)
- Controls which subagent template is used
- Available options: built-in types above, or custom project/user subagent names
- Determines default tool access and prompt

#### description
- Claude uses this to determine when to delegate
- Example: "Expert code reviewer. Use proactively after code changes."
- Clear descriptions improve delegation accuracy

#### prompt
- Override or extend the agent type's default system prompt
- Appended to built-in prompts; replaces custom agent prompts if set

#### model
- Explicit model selection: `"sonnet"`, `"opus"`, `"haiku"`, or full ID `"claude-opus-4-6"`
- Can also be set via `CLAUDE_CODE_SUBAGENT_MODEL` environment variable
- Defaults to inheriting parent conversation's model
- Resolution order: env var > invocation param > agent definition > parent model

#### run_in_background
- `true`: Agent runs concurrently; permissions pre-approved at spawn time
- `false` (default): Agent blocks; permission prompts go to user interactively
- Background agents auto-deny operations not in pre-approved set
- Useful for parallel exploration without blocking main conversation

#### mode (permissionMode)
- `default` — Standard prompts for permission
- `acceptEdits` — Auto-approve file edit operations
- `bypassPermissions` — Skip permission checks entirely [UNCERTAIN: relationship to parent mode]
- `dontAsk` — Auto-deny permission prompts (pre-approved tools still work)
- `plan` — Read-only exploration mode
- `auto` — Inherit parent's mode (classification-based permissions)
- Parent mode sometimes takes precedence:
  - If parent uses `bypassPermissions`, cannot be overridden
  - If parent uses `auto`, subagent inherits auto mode

#### isolation: "worktree"
- Creates temporary git worktree for subagent's exclusive use
- Provides filesystem isolation; prevents merge conflicts
- Automatic cleanup if agent makes no changes [UNCERTAIN: cleanup timing]
- Changes must be explicitly merged back [UNCERTAIN: merge mechanism]

#### maxTurns
- Maximum agentic turns before agent stops
- Prevents infinite loops
- No default specified [UNCERTAIN: default limit]

### 2.3 Agent Tool Access Matrix

| Tool | Explore | Plan | General-purpose | Coordinator |
|------|---------|------|-----------------|-------------|
| Read | ✓ | ✓ | ✓ | ✓ |
| Edit | ✗ | ✗ | ✓ | ✓ |
| Write | ✗ | ✗ | ✓ | ✓ |
| Bash | ✓ (RO) | ✗ | ✓ | ✓ |
| Glob | ✓ | ✓ | ✓ | ✓ |
| Grep | ✓ | ✓ | ✓ | ✓ |
| Agent/Task | ✗ | ✗ | ✓ | ✓ |
| SendMessage | ✗ | ✗ | ✓ | ✓ |

---

## 3. Communication Patterns

### 3.1 Messaging Architecture

**Components**:
- **Mailbox system**: Asynchronous message queue for agent communication
- **Direct messaging**: Teammates message each other and lead without intermediaries
- **Automatic delivery**: Messages delivered automatically; no polling required
- **Idle notifications**: Agents notify lead when finishing/going idle

**Message Flow**:
```
Teammate A → [Mailbox] → Teammate B (direct)
Teammate A → [Mailbox] → Team Lead (automatic)
Team Lead → [Mailbox] → Teammate C (explicit)
```

### 3.2 SendMessage Tool

**Function Signature**:
```javascript
SendMessage({
  to: "teammate-name|team-lead|*",
  summary: "5-10 word preview of message",
  message: "Full message content (plain text or structured JSON)"
})
```

**to Parameter**:
- `"team-lead"` — Message team lead
- `"teammate-name"` — Message specific teammate by name
- `"*"` — Broadcast to all teammates (use sparingly; costs scale with team size)
- [UNCERTAIN]: Can subagents message each other directly within same team?

**Message Delivery**:
- Team lead: automatic notifications when received
- Teammates: notified in their session via message queue
- No HTTP/webhook infrastructure required; file-based coordination

**Constraints**:
- Messages sent while agent is idle auto-resume in background
- Peer DM visibility unclear [UNCERTAIN]: Do team lead broadcasts reach only teammates or all agents?

### 3.3 Idle State Management

**Idle Conditions**:
- Agent completes current request/tool call
- Agent awaits next instruction
- Agent executes shutdown request

**Idle Behavior**:
- Agent automatically notifies team lead
- Available to receive messages
- Can self-claim next task if in task list coordination mode
- Timeout behavior not documented [UNCERTAIN]

---

## 4. Task Coordination

### 4.1 Task Operations

**TaskCreate Parameters**:
```javascript
TaskCreate({
  subject: "Brief imperative title",
  description: "Detailed task requirements and context",
  activeForm: "Present continuous form (optional)",
  metadata: {}
})
```

Returns: `{ id: "1", ... }` newly created task object

**TaskUpdate Parameters**:
```javascript
TaskUpdate({
  taskId: "1",
  status: "pending|in_progress|completed|deleted",
  subject: "New title (optional)",
  description: "New description (optional)",
  activeForm: "New active form (optional)",
  owner: "agent-name (optional)",
  addBlockedBy: ["2", "3"],
  addBlocks: ["3"]
})
```

**TaskList** (no parameters):
- Returns all tasks with owner, status, blockedBy/blocks
- Sorted by ID (lowest first recommended)
- Teams prefer working in ID order

**TaskGet Parameters**:
```javascript
TaskGet({
  taskId: "1"
})
```

Returns: Full task object including description, dependencies, owner

### 4.2 Dependency Resolution

**Blocking Mechanism**:
- Tasks with non-empty `blockedBy` array cannot be claimed from `pending` state
- Claiming algorithm: agents select first `pending` task with empty `blockedBy`
- Automatic unblocking: when blocking task reaches `completed`, dependents unblock

**Dependency Flow**:
```
Task 1 (completed) → unblocks → Task 3 (auto-transitions from pending to claimable)
                                     ↓
                              Task 3 claimed → in_progress
```

**Race Condition Prevention**:
- File-based locking (.lock files) prevents duplicate task claims
- Multiple simultaneous task claims handled via atomic file operations

### 4.3 Task Ownership & Claiming

**Claiming Behavior**:
- Agents autonomously claim next available unblocked task
- `owner` field identifies which agent claimed task
- Lead can explicitly assign tasks: `"Give task 5 to researcher"`

**Workflow**:
1. Agent finishes task → marks as `completed`
2. Agent calls `TaskList()` → retrieves pending unblocked tasks
3. Agent claims first available task → sets `owner` to self, status to `in_progress`
4. Task locked via `.lock` file to prevent race conditions

---

## 5. Worktree Isolation

### 5.1 How isolation: "worktree" Works

**Creation**:
- Parameter `isolation: "worktree"` in Agent tool invocation
- Creates temporary git worktree at `.claude/worktrees/{worktree-name}/`
- Worktree branched from HEAD of current branch
- Isolated filesystem: changes don't affect main workspace

**Workflow**:
```
Main branch (main) ← Clone/branch
        ↓
   Worktree (temp-branch)
        ↓
  Agent makes changes
        ↓
  [Cleanup or merge back?]
```

**Cleanup Behavior**:
- Automatic cleanup if agent makes **no changes**: worktree directory deleted, temp branch removed
- [UNCERTAIN]: What triggers cleanup if changes are made?
- [UNCERTAIN]: Does worktree persist until explicitly merged/deleted?

**Merge/Conflict Handling**:
- [UNCERTAIN]: Can agents automatically merge worktree back to main?
- [UNCERTAIN]: How are merge conflicts resolved?
- [UNCERTAIN]: Is merging manual via lead instruction or automatic?

### 5.2 Use Cases

**Optimal for**:
- Parallel features requiring isolated file modifications
- Reducing merge conflicts from simultaneous edits
- Testing approaches independently before merging

**Limitations**:
- Read-heavy work doesn't benefit (no filesystem conflicts in reads)
- Merge complexity if multiple worktrees modify overlapping files
- Unknown cleanup semantics increase operational uncertainty

---

## 6. Display Modes

### 6.1 In-Process Mode

**Activation**:
- Default mode; no setup required
- Works in any terminal

**Configuration**:
```json
{
  "teammateMode": "in-process"
}
```

Or CLI flag:
```bash
claude --teammate-mode in-process
```

**Behavior**:
- All teammates run inside main terminal
- `Shift+Down` cycles through active teammates
- Type to message current teammate directly
- Press `Enter` to view agent's full session
- Press `Escape` to interrupt current turn
- Press `Ctrl+T` to toggle task list view

**Advantages**:
- No external dependencies
- Works everywhere (VS Code, terminals, remote)

**Disadvantages**:
- Single output stream; can't see all agents simultaneously
- More context switching between teammates

### 6.2 Split-Pane Mode (tmux/iTerm2)

**Activation**:
```json
{
  "teammateMode": "tmux"
}
```

Or CLI flag:
```bash
claude --teammate-mode tmux
```

**Auto Mode** (default):
```json
{
  "teammateMode": "auto"
}
```

- Uses split panes if already in tmux session
- Falls back to in-process otherwise

**Requirements**:
- tmux installed (macOS: `brew install tmux`, Linux: package manager)
- OR iTerm2 with `it2` CLI installed and Python API enabled
- [UNCERTAIN]: Does split-pane work in VS Code integrated terminal? — Documentation says **not supported**

**Behavior**:
- Each teammate gets dedicated pane
- See all agents' output simultaneously
- Click into pane to interact directly with that agent
- Window layout shows all team members at once

**Advantages**:
- Full visibility into parallel work
- Direct interaction without cycling
- Better for large teams (5+ agents)

**Disadvantages**:
- Requires external tooling (tmux/iTerm2)
- Not supported in VS Code, Windows Terminal, Ghostty
- Requires terminal knowledge

### 6.3 Display Mode Detection & Configuration

**Default**: `"auto"` (split panes if in tmux, otherwise in-process)

**Override Method 1 - Global config**:
```json
~/.claude.json
{
  "teammateMode": "in-process"
}
```

**Override Method 2 - Session flag**:
```bash
claude --teammate-mode in-process
```

**Session Priority**: Flag > local `.claude.json` > session settings > default

---

## 7. Auto Mode & Permission Implications

### 7.1 What mode: "auto" Does

**Behavior**:
- Automatic permission classification for tool usage
- Each tool call evaluated against `permissions.allow` and `permissions.deny` rules
- [UNCERTAIN]: Exact decision tree for allow/deny classification
- [UNCERTAIN]: How does auto mode differ from `default` mode with extensive permission rules?

**Use Cases**:
- Replacing tedious interactive permission prompts
- Establishing team-wide permission policies
- Balancing security with developer experience

### 7.2 Mode Parameter Interaction with Parent Permissions

**Precedence Rules**:
1. If parent uses `bypassPermissions`: **cannot be overridden** by teammate
2. If parent uses `auto`: teammate **inherits auto mode**, `permissionMode` in agent definition ignored
3. Otherwise: teammate `permissionMode` applies as specified

**Implication**: Permissions are set at spawn time and cannot be relaxed per-teammate after spawning [UNCERTAIN: can permission mode be changed post-spawn?]

### 7.3 Protected Directories

Always prompt for confirmation regardless of mode:
- `.git/` — Version control
- `.claude/` — Agent configuration (except `.claude/commands`, `.claude/agents`, `.claude/skills`)
- `.vscode/` — Editor config
- `.idea/` — JetBrains config

---

## 8. Practical Limitations & Constraints

### 8.1 Context Window Constraints

**Per-Agent Capacity**:
- Each teammate: **1M tokens** of context (~30,000 lines of code)
- Total team capacity scales linearly: 3 agents = 3M tokens, but **agents don't share full contexts**
- Only explicit messages via SendMessage transfer information between agents

**Context Efficiency**:
- Multi-agent approach essential when single-agent context loading consumes 80%+ of capacity
- Agents at 80-90% capacity experience "degraded reasoning"
- Compression/summarization needed if codebases exceed 30K lines

**Information Sharing**:
- Full conversation history does NOT carry over to teammates
- CLAUDE.md files loaded by all agents independently
- MCP servers configured per-agent
- Skills must be explicitly listed

### 8.2 Maximum Concurrent Agents

**Hard Limits**:
- [UNCERTAIN]: Is there a hard limit on number of teammates?

**Practical Limits**:
- **2-3 agents**: Optimal for most workflows (balanced productivity/coordination)
- **5-6 agents**: Upper practical limit before coordination overhead exceeds benefits
- **Beyond 5**: Diminishing returns; each additional agent costs tokens but adds less productivity
- Exception: Large codebases (50K+ lines) justify more agents to distribute context load

**Team Size Heuristics**:
- 5-6 tasks per teammate keeps everyone productive
- 15 independent tasks → recommend 3 teammates
- 3 focused teammates often outperform 5 scattered ones

### 8.3 Cost Implications

**Token Scaling**:
- Each teammate has independent context window (not shared)
- Token cost scales linearly with number of agents: 3 teammates ≈ 3x cost
- Messaging overhead: continuous bidirectional communication between agents
- "High token intensity" — multiple simultaneous model calls

**Cost vs Benefit**:
- Research/review tasks: extra tokens justified by parallel perspective value
- Write-heavy parallel modification: potentially expensive due to merge conflicts
- Sequential tasks: single agent more cost-effective
- See official docs for token cost guidance

### 8.4 Failure Modes & Hanging

**Known Issues**:
- Teammates may stop after encountering errors instead of recovering [UNCERTAIN: recovery mechanism exists?]
- Lead may decide team is finished before tasks actually complete
- In-process teammates not resumable via `/resume` or `/rewind`
- After session resume, lead may message teammates that no longer exist

**Mitigations**:
- Monitor teammate progress; redirect failing approaches
- Explicitly instruct lead to wait for teammates before proceeding
- Check teammate output via `Shift+Down` in in-process mode
- Spawn replacement teammates if one hangs

**Hanging Prevention**:
- [UNCERTAIN]: Are there timeout mechanisms?
- [UNCERTAIN]: Can hung agents be forcefully killed?

### 8.5 Session Resumption Limitations

**Current Restrictions**:
- `/resume` and `/rewind` do **not** restore in-process teammates
- After resuming, lead may reference teammates that no longer exist
- Split-pane teammates: resumption status unclear [UNCERTAIN]

**Workaround**:
- Spawn new teammates after session resume
- Task state persists; newly spawned agents can claim remaining tasks

### 8.6 Task Status Lag

**Issue**:
- Teammates sometimes fail to mark tasks as completed
- Blocks dependent tasks indefinitely
- Can appear stuck even if work is actually done

**Resolution**:
- Manually update task status: `TaskUpdate({ taskId: "3", status: "completed" })`
- Or instruct lead to nudge teammate: "Ask researcher to mark task 2 as complete"

### 8.7 Shutdown Behavior

**Normal Flow**:
- `"Ask researcher to shut down"` — lead sends shutdown request
- Teammate approves → exits gracefully
- OR teammate rejects with explanation

**Slow Shutdown**:
- Teammates finish current request/tool call before stopping
- Can take significant time if in middle of long operation

**Lead Shutdown**:
- Only lead can run team cleanup
- Teammates should not cleanup (may leave resources inconsistent)
- Cleanup fails if active teammates still running

### 8.8 Team Isolation Constraints

**One Team Per Session**:
- A lead manages exactly one team
- Cannot spawn sub-teams or nested teams
- Must clean up current team before starting new one

**No Nested Teams**:
- Teammates cannot spawn their own teammate teams
- Only leads can create/manage teams

**Fixed Leadership**:
- Session that creates team is lead for its lifetime
- Cannot promote teammate to lead or transfer leadership

---

## 9. Hooks for Quality Gates

**Supported Events**:
- `TeammateIdle` — When teammate about to go idle
- `TaskCreated` — When task being created
- `TaskCompleted` — When task marked complete

**Exit Code 2 Behavior**:
- Send feedback to agent and keep working
- Prevents idle state, task creation, or completion

**Configuration** (in `settings.json`):
```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "matcher": "researcher",
        "hooks": [
          { "type": "command", "command": "./validate-work.sh" }
        ]
      }
    ]
  }
}
```

---

## 10. Team Lead Behavior & Autonomy

**Lead Responsibilities** (automatically handled):
- Creating teams and spawning teammates
- Breaking work into tasks
- Synthesizing findings
- Approving plans (if `planModeRequired: true` per teammate)
- Handling cleanup

**Autonomous Lead Decisions**:
- Team lead makes approval decisions autonomously for plan mode
- Influenced by user instructions: "only approve plans that include test coverage"

**Lead Limitations**:
- Must wait for teammates to complete before synthesizing
- Can start implementation itself instead of waiting (user must redirect)
- May declare team finished before tasks actually done

---

## 11. Known Experimental Limitations (Official)

From Claude Code v2.1.32+ documentation:

1. **No session resumption with in-process teammates** — `/resume` doesn't restore teammates
2. **Task status lag** — Teammates may fail to mark tasks completed, blocking dependents
3. **Slow shutdown** — Agents finish current request before stopping
4. **One team per session** — Can't manage multiple teams simultaneously
5. **No nested teams** — Teammates cannot spawn their own teams
6. **Fixed leadership** — Session that creates team is lead permanently
7. **Permissions set at spawn** — Cannot set per-teammate modes at creation time
8. **Split panes require tmux/iTerm2** — Not available in VS Code integrated terminal, Windows Terminal, or Ghostty

---

## 12. Comparison: Agent Teams vs Subagents

| Aspect | Agent Teams | Subagents |
|--------|-------------|-----------|
| **Context** | Separate 1M-token windows per agent | Shared context with main conversation |
| **Communication** | Direct peer-to-peer + lead | Only report back to caller |
| **Parallelism** | True parallelism; agents work simultaneously | Sequential invocation; results summarized back |
| **Coordination** | Shared task list; self-claiming | Manual delegation by main agent |
| **Best for** | Research, parallel features, competing hypotheses | Focused tasks with single output |
| **Token cost** | High (~Nx main cost) | Lower; results summarized |
| **Nesting** | No nested teams allowed | Subagents cannot spawn subagents |
| **Data sharing** | Explicit messages only | Full context access |

---

## 13. Checklist: Team Creation Best Practices

- [✓] Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- [✓] Use Claude Code v2.1.32+
- [✓] Specify `agentType` for each teammate
- [✓] Use 3-5 teammates for optimal productivity
- [✓] Create 5-6 tasks per teammate (prevents idle time)
- [✓] Write detailed task descriptions (include context, expectations)
- [✓] Use file locking for task claiming (automatic)
- [✓] Monitor teammate progress; redirect failing approaches
- [✓] Use `Shift+Down` to cycle teammates in in-process mode
- [✓] Save findings in shared documents during work
- [✓] Clean up via lead only; never from teammate session
- [✓] Break work to avoid same-file edits (reduces merge conflicts)
- [✓] Ensure teammates have enough context (via CLAUDE.md or task descriptions)

---

## 14. Uncertainties & Gaps [UNCERTAIN Items Summary]

1. **Worktree cleanup semantics**: Exactly when and how are worktrees cleaned up? What triggers merge?
2. **Merge conflict resolution**: How are conflicts from multiple worktrees merged back?
3. **Automatic merge mechanism**: Can agents merge worktrees back, or is this manual?
4. **Timeout mechanisms**: Are there agent timeouts? How are hung agents handled?
5. **Permission mode post-spawn**: Can permission modes be changed after teammate spawn?
6. **maxTurns default**: What's the default limit if not specified?
7. **Peer DM visibility**: Can subagents within same team message each other directly?
8. **Hard concurrency limit**: Is there a maximum number of concurrent teammates?
9. **Task status persistence**: How exactly are `.lock` and `.highwatermark` files used?
10. **Split-pane resumption**: Can split-pane teammates be resumed via `/resume`?
11. **Auto mode decision tree**: Detailed classification logic for auto mode permission decisions?
12. **Nested team restrictions**: Why are nested teams forbidden? Technical constraint or design choice?

---

## 15. References & Sources

### Official Documentation
- [Claude Code Agent Teams Docs](https://code.claude.com/docs/en/agent-teams) — Comprehensive guide
- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents) — Subagent configuration
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference) — Command-line flags

### Community Resources & Research
- [Claude Code Ultimate Guide (GitHub)](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) — Technical deep-dives
- [Alexander Opmeer's Blog](https://alexop.dev) — Agent teams practical patterns
- [Cobus Greyling's Medium](https://cobusgreyling.medium.com) — Agent teams getting started
- [30 Tips for Claude Code Agent Teams](https://getpushtoprod.substack.com/p/30-tips-for-claude-code-agent-teams) — Production patterns

---

## 16. How Teams Actually Work: Real-World Flow

### Scenario: Parallel Code Review

**Setup**:
```
User: "Create a team to review PR #142. Spawn 3 reviewers:
security, performance, test-coverage. Have them review in parallel."
```

**Execution Timeline**:
1. Lead spawns 3 teammates (security-reviewer, perf-reviewer, test-reviewer)
2. Lead creates shared task list:
   - Task 1: Security review (empty blockedBy)
   - Task 2: Performance review (empty blockedBy)
   - Task 3: Test coverage review (empty blockedBy)
3. Each teammate autonomously claims an unblocked task
4. Teammates work in parallel; each has 1M-token context
5. Teammate A: Messages lead with findings → lead sees automatic notification
6. Teammate B: Finishes; calls `TaskList()` and claims next task [UNCERTAIN: what if no tasks left?]
7. Lead: Reviews all findings; synthesizes conclusions
8. Lead: Instructs cleanup → verifies all teammates shut down → runs cleanup

**Token Cost**: ~3x main conversation cost (3 independent 1M-token contexts)

**Key Difference from Subagents**: If this were subagents instead, lead would spawn one at a time, results return sequentially, no direct teammate-to-teammate messaging.

---

## 17. Conclusion

Agent Teams represent a significant architectural shift for Claude Code's parallel work capabilities. By providing true multi-agent autonomy with independent context windows, task-based coordination, and peer-to-peer messaging, they enable genuinely collaborative development workflows.

However, the experimental status and numerous documented limitations (task status lag, resumption issues, shutdown semantics) indicate the feature is still stabilizing. Production use should account for these constraints and include monitoring/intervention points.

**Recommendation**: Use for research, reviews, and parallel features on well-scoped tasks. Avoid for tasks requiring fine-grained synchronization or frequent same-file modifications until stability improves.

**Next Investigation Areas**:
- Actual behavior of worktree cleanup and merge
- Timeout and recovery mechanisms for hung agents
- Full token cost breakdown for real workflows
- Integration with existing Claude Code plugins and skills

---

**Report Status**: ✓ Comprehensive
**Last Updated**: 2026-03-30 10:45 UTC
**Confidence Level**: High (official docs) — [UNCERTAIN] items flagged for future clarification
