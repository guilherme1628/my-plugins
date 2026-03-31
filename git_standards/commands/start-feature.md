---
allowed-tools: Bash(git checkout:*), Bash(git pull:*), Bash(git branch:*)
description: Create a feature branch from develop following Gitflow workflow
---

## Context
- Current branch: !`git branch --show-current`
- Current status: !`git status --short`

## Your task

The user wants to start a new feature. Execute the Gitflow feature branch workflow using these exact steps:

1. **Switch to develop:**
   ```
   git checkout develop
   ```

2. **Pull latest from remote** (teammates may have merged since last pull):
   ```
   git pull origin develop
   ```

3. **Create the feature branch** (the -b flag creates and switches in one command):
   ```
   git checkout -b feature/<name>
   ```

Use the argument provided by the user as `<name>`. If no argument was provided, ask the user for a short, descriptive name using lowercase and hyphens (e.g., `user-authentication`, `payment-gateway`, `search-filter`).

After creating the branch, confirm:
- Which branch was created
- That the user is now isolated — main and develop are untouched
- Remind them: commit with conventional messages (`feat: description`), stage specific files only

Do NOT proceed if:
- There are uncommitted changes (warn the user to commit or stash first)
- The develop branch does not exist (suggest running `git-fix.sh`)
