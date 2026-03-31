---
allowed-tools: Bash(git push:*), Bash(git branch:*), Bash(git log:*), Bash(git diff:*), Bash(gh pr create:*), Bash(gh pr view:*)
description: Push current branch and open a pull request to the correct target
---

## Context
- Current branch: !`git branch --show-current`
- Current status: !`git status --short`
- Commits not yet pushed: !`git log @{u}..HEAD --oneline 2>/dev/null || git log --oneline -10`

## Your task

Push the current branch to remote and open a pull request. Follow these exact steps:

1. **Verify you are NOT on main or develop.** If you are, stop and tell the user — PRs come from feature/hotfix/release branches only.

2. **Verify there are no uncommitted changes.** If there are, warn the user to commit first.

3. **Push the branch to remote** (set upstream on first push):
   ```
   git push -u origin <current-branch>
   ```

4. **Determine the correct PR target:**
   - `feature/*` → target is `develop`
   - `hotfix/*` → target is `main`
   - `release/*` → target is `main`

5. **Analyze all commits on this branch** (not just the latest — ALL commits since branching):
   ```
   git log <target>..HEAD --oneline
   ```

6. **Open a pull request** using `gh pr create`:
   - Title: conventional commit format summarizing the work (e.g., `feat: implement user authentication`)
   - Body: summary bullets + test plan
   - Base: the correct target branch

   ```
   gh pr create --base <target> --title "<title>" --body "<body>"
   ```

   Use this body format:
   ```
   ## Summary
   - <1-3 bullet points describing what changed and why>

   ## Test plan
   - [ ] <testing checklist items>
   ```

7. **Return the PR URL** so the user can see it.

**Reminder to user:** 4 gates must be green before merge — peer review, CI passes, no conflicts, clean history.
