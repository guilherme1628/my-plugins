# Resume or Initialize Session

## Purpose
Start a new session or restore context from a previous one. Auto-detects first-time vs returning.

## Workflow

1. **Detect capabilities** (run in parallel where possible):
   - **Serena**: Check if `check_onboarding_performed` tool is available. Store result.
   - **OpenSpec**: Run `which openspec` or `openspec list` — if exit code 0, available. Store result.
   - **Episodic memory**: Check if `mcp__plugin_episodic-memory_episodic-memory__search` tool is available. Store result.

2. **Check for existing session state**
   - Look for `.session/state.md` in the project root
   - IF not found: Go to step 3 (Initialize)
   - IF found: Go to step 4 (Resume)

3. **Initialize (first time)**
   - Create `.session/` directory
   - Add `.session/` to `.gitignore` if not already there
   - Load context in parallel:
     * **Git**: `git branch --show-current`, `git log -5 --oneline`, `git status`
     * **Key files**: Glob for README*, package.json, CLAUDE.md, Cargo.toml, pyproject.toml — read the first few found
     * **Episodic memory** (if available): Search past conversations for this project directory name
     * **Serena** (if available): Run `check_onboarding_performed`, if yes use `get_symbols_overview` on key files
     * **OpenSpec** (if available): Run `openspec list` to find active proposals
   - Write `.session/state.md` with status ACTIVE, detected capabilities, branch, and loaded context summary
   - Present brief project summary to user
   - Ask: "What are we working on?"
   - STOP here

4. **Resume (returning)**
   - Read `.session/state.md` — parse status, active task, blockers, next actions, capabilities
   - Load context in parallel:
     * **Git**: `git branch --show-current`, `git log -5 --oneline`, `git status`
     * **Branch check**: Compare current branch with branch in state file. If mismatch, alert user.
     * **Episodic memory** (if available): Search past conversations for this project
     * **Serena** (if available): Run `check_onboarding_performed`, load relevant memories with `list_memories`
     * **OpenSpec** (if available): If proposal noted in state, read `openspec/changes/{proposal}/proposal.md`
   - Update `.session/state.md`: status ACTIVE, update timestamp
   - Present summary:
     * Last session ended: {date}
     * Working on: {task or "nothing active"}
     * Status: {brief}
     * Blockers: {list or "none"}
     * Next action: {from state}
   - Ask: "Ready to continue with {next_action}? Or would you like to do something else?"

## Report
- Session: {initialized | resumed}
- Capabilities: serena={yes|no}, openspec={yes|no}, episodic_memory={yes|no}
- Branch: {branch}
- Status: ACTIVE
- Next: {action}
