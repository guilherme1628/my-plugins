#!/bin/bash
# git-fix.sh — Adjust an existing repo to follow Gitflow branch structure
# Usage: git-fix.sh
#   Run from inside an existing git repo. Non-destructive: creates missing
#   branches, renames master→main (with confirmation), and audits branch names.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

info()  { echo -e "${CYAN}▸${NC} $1"; }
ok()    { echo -e "${GREEN}✔${NC} $1"; }
warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✖${NC} $1" >&2; exit 1; }
skip()  { echo -e "${DIM}–${NC} $1"; }

fixes=0
warnings=0

# ── Guard: must be inside a git repo ──────────────────────────────

git rev-parse --git-dir &>/dev/null 2>&1 || error "Not a git repository."
git rev-parse HEAD &>/dev/null 2>&1 || error "Repo has no commits. Use 'gi' (git-init.sh) instead."

echo -e "\n${BOLD}Gitflow Health Check${NC}"
echo -e "${DIM}$(git rev-parse --show-toplevel)${NC}\n"

# ── 1. Ensure 'main' branch exists ───────────────────────────────

has_main=$(git branch --list main | tr -d ' ')
has_master=$(git branch --list master | tr -d ' ')

if [[ -n "$has_main" ]]; then
  ok "Branch 'main' exists"
elif [[ -n "$has_master" ]]; then
  warn "Found 'master' but no 'main'"
  echo -ne "    Rename master → main? [y/N] "
  read -r answer
  if [[ "$answer" =~ ^[Yy]$ ]]; then
    current=$(git branch --show-current)
    if [[ "$current" == "master" ]]; then
      git branch -m master main
    else
      git branch -m master main
    fi
    ok "Renamed master → main"
    ((fixes++))

    # Check if remote tracking exists
    if git config --get branch.main.remote &>/dev/null 2>&1 || \
       git ls-remote --heads origin master &>/dev/null 2>&1; then
      warn "Remote still has 'master'. You'll need to update it manually:"
      echo -e "    ${DIM}git push origin main${NC}"
      echo -e "    ${DIM}git push origin --delete master${NC}"
      echo -e "    ${DIM}# Then update default branch in repo settings${NC}"
      ((warnings++))
    fi
  else
    warn "Skipped rename. Gitflow expects 'main' as production branch."
    ((warnings++))
  fi
else
  warn "Neither 'main' nor 'master' found. Create a 'main' branch manually."
  ((warnings++))
fi

# ── 2. Ensure 'develop' branch exists ────────────────────────────

has_develop=$(git branch --list develop | tr -d ' ')
main_ref=$(git branch --list main | tr -d ' ')

if [[ -n "$has_develop" ]]; then
  ok "Branch 'develop' exists"
else
  if [[ -n "$main_ref" ]]; then
    git branch develop main
    ok "Created 'develop' from main"
    ((fixes++))
  else
    warn "Cannot create 'develop' — no 'main' branch found"
    ((warnings++))
  fi
fi

# ── 3. Audit branch names ────────────────────────────────────────

echo ""
info "Auditing branch names..."

bad_branches=()
while IFS= read -r branch; do
  branch=$(echo "$branch" | sed 's/^[* ]*//' | tr -d ' ')
  # Skip expected branches
  [[ "$branch" == "main" || "$branch" == "master" || "$branch" == "develop" ]] && continue
  # Check for valid prefixes
  if [[ ! "$branch" =~ ^(feature|hotfix|release)/ ]]; then
    bad_branches+=("$branch")
  fi
done < <(git branch)

if [[ ${#bad_branches[@]} -eq 0 ]]; then
  ok "All branches follow naming conventions"
else
  warn "${#bad_branches[@]} branch(es) don't follow Gitflow naming:"
  for b in "${bad_branches[@]}"; do
    echo -e "    ${YELLOW}→${NC} $b"
  done
  echo -e "    ${DIM}Expected: feature/<name>, hotfix/<name>, release/<version>${NC}"
  ((warnings++))
fi

# ── 4. Check current branch ──────────────────────────────────────

current=$(git branch --show-current)
if [[ "$current" == "main" || "$current" == "develop" ]]; then
  warn "You're on '$current' — switch to a feature branch before making changes"
  echo -e "    ${DIM}git checkout -b feature/<name>${NC}"
  ((warnings++))
else
  ok "Current branch: $current"
fi

# ── 5. Check .gitignore for .session/ ─────────────────────────────

if [[ -f .gitignore ]]; then
  if grep -q '\.session' .gitignore 2>/dev/null; then
    ok ".session/ is in .gitignore"
  else
    echo '.session/' >> .gitignore
    ok "Added .session/ to .gitignore"
    ((fixes++))
  fi
else
  skip "No .gitignore found (not adding one — use 'gi' for that)"
fi

# ── Summary ──────────────────────────────────────────────────────

echo ""
if [[ $fixes -eq 0 && $warnings -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}All good!${NC} Repo follows Gitflow conventions."
else
  [[ $fixes -gt 0 ]] && echo -e "${GREEN}${BOLD}$fixes fix(es) applied${NC}"
  [[ $warnings -gt 0 ]] && echo -e "${YELLOW}${BOLD}$warnings warning(s)${NC} — manual action needed (see above)"
fi
echo ""
