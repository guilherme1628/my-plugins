---
name: git-workflow
description: Professional Gitflow playbook — branch structure, conventional commits, feature/hotfix/release workflows, code review gates, and naming conventions. Use when doing ANY git work.
metadata:
  filePattern: ".gitignore,*.git*"
  bashPattern: "git\\s"
  priority: 90
---

# Git Workflow Playbook

This is the complete professional Gitflow playbook. Follow it every time you touch git — no exceptions.

---

## 1. Branch Structure

Five branch types. Each has one job.

| Branch | Purpose | Lifetime | Created from | Merges to |
|--------|---------|----------|-------------|-----------|
| `main` | Production. Always stable, always deployable. | Permanent | — | — |
| `develop` | Integration. Finished features collect here. | Permanent | `main` (once) | — |
| `feature/<name>` | New work. One branch per feature. | Temporary | `develop` | `develop` via PR |
| `hotfix/<name>` | Urgent production fix. | Temporary | `main` | `main` AND `develop` |
| `release/<version>` | Release prep. Final QA happens here. | Temporary | `develop` | `main` AND `develop` |

**Key rule:** `main` and `develop` are permanent. Everything else is temporary — delete after merge.

---

## 2. Naming Conventions

### Branch Names

Format: `type/short-description`

- Lowercase only
- Hyphens between words (no spaces, no underscores)
- Always prefixed with branch type

```
feature/user-authentication
feature/payment-gateway
hotfix/payment-bug
hotfix/login-validation
release/1.2.0
release/2.0.0-rc1
```

Never name a branch `fix`, `update`, or `my-branch`. The name must tell you what it does at a glance.

### Commit Messages (Conventional Commits — MANDATORY)

Format: `type: description` or `type(scope): description`

**Seven types:**

| Type | When to use | Example |
|------|------------|---------|
| `feat` | New feature | `feat: implement JWT authentication for API endpoints` |
| `fix` | Bug fix | `fix: resolve login validation issue on mobile Safari` |
| `refactor` | Code improvement, no behavior change | `refactor: extract payment logic into dedicated service class` |
| `docs` | Documentation only | `docs: add setup instructions to README for local development` |
| `style` | Formatting only (whitespace, semicolons) | `style: fix indentation in auth middleware` |
| `test` | Adding or fixing tests | `test: add unit tests for payment calculation edge cases` |
| `chore` | Maintenance (deps, config, CI) | `chore: update dependencies to latest versions` |

**Rules:**
- Present tense: "add feature" not "added feature"
- Under 72 characters
- Specific: describe WHAT changed, not "update" or "fix stuff"
- The type tells you what KIND of change; the description tells you WHAT specifically changed
- If someone reads it 6 months from now with no other context, they should understand exactly what changed

**Anatomy:**
```
fix: resolve login validation issue
│    │
│    └─ description: specific, present tense, under 72 chars
└─ type: what kind of change
```

### Tag Names

Format: `v<semver>` — e.g., `v1.2.0`, `v2.0.0-rc1`

### PR Titles

Follow the same conventional commit format as the main change:
```
feat: implement user authentication system
fix: resolve payment calculation rounding error
```

---

## 3. Workflows

### 3a. Start a Feature

```bash
# 1. Switch to develop
git checkout develop

# 2. Pull latest (teammates may have merged since you last pulled)
git pull origin develop

# 3. Create feature branch (-b creates and switches in one command)
git checkout -b feature/<name>
```

You are now isolated. Main and develop are untouched. Work freely, break things safely.

### 3b. Start a Hotfix (Production Emergency)

```bash
# 1. Switch to main
git checkout main

# 2. Pull latest
git pull origin main

# 3. Create hotfix branch
git checkout -b hotfix/<name>
```

Hotfix branches go straight from main. NEVER from develop — develop may have unfinished unreleased work.

### 3c. Start a Release

```bash
# 1. Switch to develop
git checkout develop

# 2. Pull latest
git pull origin develop

# 3. Create release branch
git checkout -b release/<version>
```

Only bug fixes allowed on release branches. No new features.

### 3d. Commit Work

```bash
# 1. Stage SPECIFIC files (never git add . or git add -A)
git add src/auth/login.ts src/auth/middleware.ts

# 2. Commit with conventional message
git commit -m "feat: implement JWT authentication for API endpoints"
```

**Rules:**
- Stage specific files — prevents accidentally committing .env, credentials, or unrelated changes
- One commit per logical change — atomic commits, not giant dumps
- Small commits are reviewable; giant 40-file commits get rubber-stamped

### 3e. Push and Open PR

```bash
# 1. Push feature branch to remote
git push -u origin feature/<name>
```

Then open a Pull Request on your platform (GitHub/GitLab/Bitbucket).

**PR targets:**
- `feature/*` → PR to `develop`
- `hotfix/*` → PR to `main`
- `release/*` → PR to `main`

### 3f. Code Review (4 Gates — ALL Must Be Green)

Before anything merges, four checks must pass:

1. **Peer review** — at least one teammate reads line by line, checking logic, security, style
2. **CI passes** — automated tests, lint, build must all succeed
3. **No conflicts** — branch must be up to date with target. Resolve conflicts in YOUR branch, never in develop/main
4. **Clean commit history** — conventional commits, meaningful messages, no chains of "fix fix fix"

Two outcomes:
- **Approved** → merge button becomes active → merge safely
- **Changes requested** → fix in your branch, push again, review restarts

Never force merge. Never skip the gates.

### 3g. Finish a Hotfix

After PR is approved and merged to main:

```bash
# 1. Switch to main and pull the merged result
git checkout main
git pull origin main

# 2. Merge the SAME fix into develop (critical — prevents bug reappearing in next release)
git checkout develop
git pull origin develop
git merge main

# 3. Push develop
git push origin develop

# 4. Delete the hotfix branch (it served its purpose)
git branch -d hotfix/<name>
git push origin --delete hotfix/<name>
```

**NEVER skip the merge to develop.** Without it, develop diverges from main and the exact same bug reappears in your next release.

### 3h. Release to Production

```bash
# 1. Switch to main
git checkout main

# 2. Merge develop (all reviewed, tested commits come in)
git merge develop

# 3. Push to remote (triggers production deployment)
git push origin main

# 4. Tag the release
git tag v<version>
git push origin v<version>
```

After the release, the cycle restarts — developers create new feature branches from develop.

---

## 4. Rules (Non-Negotiable)

1. **NEVER commit directly to main or develop** — always use branches + PRs
2. **NEVER force push** — not even `--force-with-lease`. It rewrites history and destroys others' commits
3. **NEVER `git add .` or `git add -A`** — stage specific files only
4. **NEVER name a branch `fix` or `update`** — use the `type/description` format
5. **NEVER write commit messages like "update" or "fix stuff"** — use conventional commits
6. **ALWAYS pull before branching** — stale code creates merge conflicts
7. **ALWAYS delete branches after merging** — clean branch list = clean project
8. **ALWAYS merge hotfixes to BOTH main and develop** — prevents bug regression
9. **Feature branches from develop, hotfix branches from main** — never the other way around
10. **Release branches: bug fixes only** — no new features

---

## 5. .gitignore (Set Up Before First Commit)

Every project must have a .gitignore BEFORE the first commit. These must never be in version control:

```
.env, .env.*          — database passwords, API keys, secrets
node_modules/         — generated from lock file, bloats repo
vendor/               — generated from lock file, bloats repo
dist/, build/, .next/ — build output, regenerated every build
```

---

## 6. Branch Protection (GitHub)

Go to Settings → Branches → Add rule for `main`:

- **Require pull request** — nobody merges directly, not even you
- **Require at least one approval** — second set of eyes on every change
- **Require CI to pass** — broken tests literally cannot enter main
- **Disable force pushes** — history is sacred

Takes 5 minutes to set up. Protects your project forever.

---

## 7. Why This Workflow Matters

**Safety** — production is always protected. Only reviewed, tested code reaches main.

**Clean history** — when something breaks at 2 AM, `fix: resolve payment rounding error` finds the problem in seconds. "update" finds nothing.

**Team collaboration** — multiple developers work in parallel. PRs create space for discussion, knowledge transfer, and mentorship.

**Scalability** — same workflow works for solo developer → team of 50. You don't outgrow it.

This is not overhead. This is how professionals move fast safely.
