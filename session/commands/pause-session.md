# Pause Session

## Purpose
Save session state before ending work. Captures progress, blockers, and next actions.

## Workflow

1. **Check session exists**
   - IF `.session/state.md` does not exist:
     * Create `.session/` directory and a minimal state file
     * Continue with step 2

2. **Read current state**
   - Read `.session/state.md` for active task and capabilities

3. **Review current work** (run in parallel):
   - `git status` — check for uncommitted changes
   - `git log --oneline` — find commits made this session (compare with branch info from state)
   - `git diff --stat` — summarize uncommitted changes

4. **Ask about blockers**
   - Ask: "Any blockers or issues to note?"
   - Record response

5. **Build session summary**
   - From git commits: what was accomplished
   - From conversation: what was discussed/decided
   - From user: blockers
   - Determine next actions (prioritized list)

6. **Write `.session/state.md`**

   Format:
   ```
   # Session State
   **Last Updated**: {YYYY-MM-DD}
   **Status**: PAUSED

   ## Capabilities
   - serena: {true|false}
   - openspec: {true|false}
   - episodic_memory: {true|false}

   ## Active Work
   - **Branch**: {branch-name}
   - **Task**: {description or "None"}

   ## Completed This Session
   1. {item}
   2. {item}

   ## Blocking Issues
   {blockers or "None"}

   ## Next Actions
   1. {priority action}
   2. {secondary action}
   ```

7. **Warn about uncommitted changes**
   - IF `git status` shows uncommitted changes:
     * Alert: "You have uncommitted changes. Consider committing before ending."
     * Do NOT auto-commit

8. **Present summary**
   - Brief 2-3 line summary of what was accomplished
   - Next actions
   - "Session paused. Resume with `/resume-session`"

## Report
- State saved to: `.session/state.md`
- Uncommitted changes: {yes|no}
- Resume with: `/resume-session`
