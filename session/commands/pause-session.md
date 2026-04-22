# Pause Session

## Purpose
Save session state before ending work. Captures progress, blockers, and next actions.

## Workflow

### 1. Run the pre-flight inspector

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/inspect.sh"
```

Parse the JSON. Relevant keys: `is_git_repo`, `git.branch`, `git.clean`, `git.untracked`, `git.modified`, `git.staged`, `git.stashes`, `git.recent_commits`, `session_state.exists`, `session_state.status`.

### 2. Ensure state file exists

If `session_state.exists == false`:
- Create `.session/` and a minimal state file (see schema below).
- Add `.session/` to `.gitignore` if `is_git_repo` and not already ignored.

### 3. Read current state

Read `.session/state.md` for active task, capabilities, and prior `Completed` entries.

### 4. Build session summary

- **What was accomplished** — from `git.recent_commits` that are newer than the last recorded session (compare subjects to what's already in `Completed Previously`).
- **What was discussed/decided** — from this conversation.
- **Blockers** — scan the conversation for:
  * unresolved errors (look for "error", "failed", "not working")
  * unanswered user questions
  * waiting on external input (approvals, credentials, upstream fixes)
  * If none → "None".
- **Stash pointers** — if `git.stashes > 0`, run `git stash list` and record each with the branch it was taken on and a one-line intent.
- **Next actions** — prioritized list.

### 5. Write `.session/state.md`

Schema:

```markdown
# Session State
**Last Updated**: {YYYY-MM-DD}
**Status**: PAUSED

## Capabilities
- serena: {true|false}
- openspec: {true|false}
- episodic_memory: {true|false}

## Active Work
- **Branch**: {branch-name or "n/a (not a git repo)"} [optional: "(N commits ahead of develop)"]
- **Task**: {description or "None"}

## Completed This Session
1. {item}
2. {item}

## Completed Previously
{preserved from prior state, trimmed to last 8-10 items}

## Blocking Issues
{bullet list or "None"}

## Stash
{for each stash: `stash@{N}` on `{branch}`: {intent}. To resume: `git switch {branch} && git stash pop`}
{or "(none)"}

## Next Actions
1. {priority action}
2. {secondary action}
```

**Demotion rule**: when writing, move items from `Completed This Session` in the *previous* state into `Completed Previously`, keeping the list at ~8-10 entries.

### 6. Warn about uncommitted changes

If `git.clean == false`:
- Alert: "You have uncommitted changes in: {git.modified + git.staged + git.untracked}. Consider committing before ending."
- Do NOT auto-commit.

If not a git repo: skip this step entirely.

### 7. Present summary

- 2-3 line recap of accomplishments.
- Blockers (if any).
- Next actions.
- "Session paused. Resume with `/session:resume-session`."

## Report
- State saved to: `.session/state.md`
- Git repo: {yes | no}
- Uncommitted changes: {yes | no | n/a}
- Stashes: {count}
- Resume with: `/session:resume-session`
