---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git merge:*), Bash(git push:*), Bash(git tag:*), Bash(git branch:*), Bash(git log:*)
description: Merge release to main, tag the version, sync develop, delete release branch
---

## Context
- Current branch: !`git branch --show-current`
- Current status: !`git status --short`
- Local branches: !`git branch`
- Recent tags: !`git tag --sort=-v:refname | head -5`

## Your task

The release has passed QA and is ready for production. Execute the complete release finish sequence:

1. **Verify you are on a release/ branch** (or identify which release to finish). Extract the version from the branch name (e.g., `release/1.2.0` → `1.2.0`).

2. **Verify there are no uncommitted changes.** If there are, warn the user to commit first.

3. **Merge to main:**
   ```
   git checkout main
   git pull origin main
   git merge release/<version>
   git push origin main
   ```

4. **Tag the release** (permanently marks this commit as a version):
   ```
   git tag v<version>
   git push origin v<version>
   ```

5. **Sync develop with main** (so develop has any release branch bug fixes):
   ```
   git checkout develop
   git pull origin develop
   git merge main
   git push origin develop
   ```

6. **Delete the release branch:**
   ```
   git branch -d release/<version>
   git push origin --delete release/<version>
   ```

7. **Confirm to the user:**
   - Main is at v<version>, deployed
   - Tag v<version> is created and pushed
   - Develop is synced with main
   - Release branch is deleted
   - The cycle restarts — new features branch from develop

If there are merge conflicts at any step, stop and help the user resolve them before continuing.
