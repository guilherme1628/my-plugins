# Resume or Initialize Session

## Purpose
Start a new session or restore context from a previous one. Auto-detects first-time vs returning.

## Workflow

### 1. Run the pre-flight inspector

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/inspect.sh"
```

Parse the JSON output. Keys you will use:

| Key | Meaning |
|---|---|
| `is_git_repo` | `false` → skip all git steps, no branch-mismatch check |
| `git.branch`, `git.head_sha`, `git.clean`, `git.untracked`, `git.recent_commits`, `git.stashes` | Git state (all null/empty if not a repo) |
| `session_state.exists` | `false` → Initialize path; `true` → Resume path |
| `session_state.branch` | The branch recorded at last pause — compare with `git.branch` |
| `openspec.installed` / `openspec.initialized` / `openspec.changes` | OpenSpec availability and active proposals |
| `crispy.stage` / `crispy.artifacts` | Current crispy pipeline stage (if any) |
| `orchestra.sessions` | Active orchestra sessions |
| `key_files` | Project entry points found at root |

### 2. Probe in-process MCP tools

The script cannot see these — you must check yourself:
- **Serena**: is `check_onboarding_performed` available?
- **Episodic memory**: is `mcp__plugin_episodic-memory_episodic-memory__search` available?

### 3. Branch: Initialize vs Resume

**IF `session_state.exists == false`** → go to (4) Initialize.
**ELSE** → go to (5) Resume.

### 4. Initialize (first time)

- Create `.session/` directory.
- Add `.session/` to `.gitignore` if `is_git_repo` is true and not already ignored.
- Load supplemental context in parallel:
  * Read the first 2-3 `key_files` (short reads — 50 lines).
  * If `crispy.stage != null`: read `.crispy/<stage>.md` to learn active feature.
  * If `openspec.initialized` and `openspec.changes` non-empty: read `openspec/changes/<first>/proposal.md`.
  * Episodic memory (if available): search past conversations for this project's directory name.
  * Serena (if available): run `check_onboarding_performed`, then `get_symbols_overview` on key files.
- Write `.session/state.md` using the schema from `pause-session.md` (status `ACTIVE`, detected capabilities, branch).
- Present a brief project summary.
- Ask: **"What are we working on?"**
- STOP.

### 5. Resume (returning)

- Read `.session/state.md` — parse status, active task, blockers, next actions, stash pointers.
- **Branch mismatch**: if `is_git_repo` and `git.branch != session_state.branch` and both are non-null:
  * Report the mismatch as an alert.
  * Ask whether to switch back, continue on current branch, or update the state file — do not decide unilaterally.
- Load supplemental context in parallel:
  * If `crispy.stage != null`: read `.crispy/<stage>.md` for active work.
  * If state file references an OpenSpec proposal: read it.
  * Episodic memory (if available): semantic search for this project.
  * Serena (if available): `list_memories`, load any that look relevant.
- Update `.session/state.md`: `Status: ACTIVE`, bump `Last Updated` to today.
- Present summary:
  * Last session ended: {last_updated}
  * Working on: {task or "nothing active"}
  * Status: {brief}
  * Blockers: {list or "none"}
  * Stashes: {count + pointers from state file}
  * Next action: {from state}
- Ask: **"Ready to continue with {next_action}? Or would you like to do something else?"**

## Report
- Session: {initialized | resumed}
- Git repo: {yes | no}
- Capabilities: serena={yes|no}, openspec={yes|no}, episodic_memory={yes|no}
- Branch: {branch or "n/a"}
- Status: ACTIVE
- Next: {action}
