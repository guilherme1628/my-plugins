#!/bin/bash
# git-protect.sh — Configure GitHub branch protection rules via gh CLI
# Usage: git-protect.sh [branch]
#   Default branch: main
#   Requires: gh CLI authenticated with admin access to the repo

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

# ── Guards ──────────────────────────────────────────────────────

git rev-parse --git-dir &>/dev/null 2>&1 || error "Not a git repository."
command -v gh &>/dev/null || error "GitHub CLI (gh) is required. Install: https://cli.github.com"
gh auth status &>/dev/null 2>&1 || error "Not authenticated. Run: gh auth login"

# ── Determine repo and branch ──────────────────────────────────

BRANCH="${1:-main}"
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null) || error "Could not determine repository. Is this repo connected to GitHub?"

echo -e "\n${BOLD}Branch Protection Setup${NC}"
echo -e "${DIM}Repo:   $REPO${NC}"
echo -e "${DIM}Branch: $BRANCH${NC}\n"

# ── Check if rules already exist ───────────────────────────────

existing=$(gh api "repos/$REPO/branches/$BRANCH/protection" 2>/dev/null && echo "yes" || echo "no")

if [[ "$existing" == "yes" ]]; then
  warn "Branch protection already exists for '$BRANCH'"
  echo -ne "    Overwrite? [y/N] "
  read -r answer
  [[ "$answer" =~ ^[Yy]$ ]] || { info "Skipped. Existing rules preserved."; exit 0; }
fi

# ── Apply protection rules ─────────────────────────────────────

info "Applying branch protection rules..."

gh api "repos/$REPO/branches/$BRANCH/protection" \
  --method PUT \
  --input - <<'JSON' >/dev/null
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_linear_history": false,
  "required_conversation_resolution": false
}
JSON

ok "Branch protection applied to '$BRANCH'"

# ── Summary ──────────────────────────────────────────────────────

echo -e "\n${BOLD}Rules now active:${NC}"
echo -e "  ${GREEN}✔${NC} Require pull request before merging"
echo -e "  ${GREEN}✔${NC} Require at least 1 approval"
echo -e "  ${GREEN}✔${NC} Dismiss stale reviews on new pushes"
echo -e "  ${GREEN}✔${NC} Require status checks to pass (strict)"
echo -e "  ${GREEN}✔${NC} Enforce rules for admins too"
echo -e "  ${GREEN}✔${NC} Block force pushes"
echo -e "  ${GREEN}✔${NC} Block branch deletion"

echo -e "\n${BOLD}Next steps:${NC}"
echo -e "  1. Add required CI status checks in repo settings"
echo -e "  2. Run again for develop: ${DIM}git-protect.sh develop${NC}"
echo ""
