---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git branch:*)
description: Create a release branch from develop for production preparation
---

## Context
- Current branch: !`git branch --show-current`
- Current status: !`git status --short`
- Recent tags: !`git tag --sort=-v:refname | head -5`

## Your task

The user wants to prepare a release. Execute the Gitflow release workflow using these exact steps:

1. **Switch to develop:**
   ```
   git checkout develop
   ```

2. **Pull latest from remote:**
   ```
   git pull origin develop
   ```

3. **Create the release branch:**
   ```
   git checkout -b release/<version>
   ```

Use the argument provided by the user as `<version>`. If no argument was provided, show the recent tags (from context above) and ask the user for the version number following semver (e.g., `1.2.0`, `2.0.0-rc1`).

After creating the branch, confirm:
- Which branch was created
- That only bug fixes are allowed on release branches — no new features
- Final QA happens here
- When ready, use `/finish-release` to merge to main, tag, and sync develop

Do NOT proceed if:
- There are uncommitted changes (warn the user to commit or stash first)
- The develop branch does not exist
