---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git branch:*)
description: Create a hotfix branch from main for urgent production fixes
---

## Context
- Current branch: !`git branch --show-current`
- Current status: !`git status --short`

## Your task

The user needs to fix a production emergency. Execute the Gitflow hotfix workflow using these exact steps:

1. **Switch to main** (hotfixes always branch from production):
   ```
   git checkout main
   ```

2. **Pull latest from remote:**
   ```
   git pull origin main
   ```

3. **Create the hotfix branch:**
   ```
   git checkout -b hotfix/<name>
   ```

Use the argument provided by the user as `<name>`. If no argument was provided, ask the user for a short, descriptive name (e.g., `payment-bug`, `login-validation`, `token-expiry`).

After creating the branch, confirm:
- Which branch was created
- That this branches from main, NOT develop (develop may have unfinished unreleased work)
- Remind them: apply the minimal fix, one commit, one purpose. No new features in a hotfix.
- Remind them: commit with `fix: description` format
- Remind them: after merge to main, they MUST also merge to develop (use `/finish-hotfix`)

Do NOT proceed if:
- There are uncommitted changes (warn the user to commit or stash first)
