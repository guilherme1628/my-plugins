---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git merge:*), Bash(git push:*), Bash(git branch:*), Bash(git log:*)
description: Merge hotfix to main AND develop, push both, delete hotfix branch
---

## Context
- Current branch: !`git branch --show-current`
- Current status: !`git status --short`
- Local branches: !`git branch`

## Your task

The hotfix has been reviewed and is ready to merge. Execute the complete hotfix finish sequence:

1. **Verify you are on a hotfix/ branch** (or identify which hotfix to finish). If not on a hotfix branch and none is obvious, ask the user.

2. **Verify there are no uncommitted changes.** If there are, warn the user to commit first.

3. **Store the hotfix branch name** for later deletion.

4. **Merge to main:**
   ```
   git checkout main
   git pull origin main
   git merge hotfix/<name>
   git push origin main
   ```

5. **CRITICAL — Merge the SAME fix to develop** (prevents the bug from reappearing in the next release):
   ```
   git checkout develop
   git pull origin develop
   git merge main
   git push origin develop
   ```

6. **Delete the hotfix branch** (it served its purpose):
   ```
   git branch -d hotfix/<name>
   git push origin --delete hotfix/<name>
   ```

7. **Confirm to the user:**
   - Main is updated and pushed (production is fixed)
   - Develop has the same fix (consistency maintained)
   - Hotfix branch is deleted (clean branch list)

**NEVER skip step 5.** Without it, develop diverges from main and the exact same bug reappears in the next release.

If there are merge conflicts at any step, stop and help the user resolve them before continuing.
