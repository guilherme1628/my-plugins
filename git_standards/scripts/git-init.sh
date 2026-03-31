#!/bin/bash
# git-init.sh — Bootstrap a new repo with Gitflow branch structure
# Usage: git-init.sh [project-name]
#   If project-name is given, creates the directory and inits inside it.
#   If omitted, initializes the current directory.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}▸${NC} $1"; }
ok()    { echo -e "${GREEN}✔${NC} $1"; }
error() { echo -e "${RED}✖${NC} $1" >&2; exit 1; }

# ── Setup directory ─────────────────────────────────────────────

if [[ -n "${1:-}" ]]; then
  mkdir -p "$1"
  cd "$1"
  info "Created directory: $1"
fi

# ── Guard: already a git repo with commits ──────────────────────

if git rev-parse HEAD &>/dev/null 2>&1; then
  error "This repo already has commits. Use this script on new projects only."
fi

# ── Init repo ───────────────────────────────────────────────────

if ! git rev-parse --git-dir &>/dev/null 2>&1; then
  git init -b main
  ok "Initialized git repo with 'main' branch"
else
  info "Git repo already initialized"
fi

# ── Create .gitignore ──────────────────────────────────────────

if [[ ! -f .gitignore ]]; then
  cat > .gitignore <<'EOF'
# Environment
.env
.env.*
!.env.example

# Dependencies
node_modules/
vendor/

# Build output
dist/
build/
.next/
out/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
EOF
  ok "Created .gitignore"
fi

# ── Initial commit on main ──────────────────────────────────────

git add .gitignore
git commit -m "chore: initial project setup" --quiet
ok "Initial commit on main"

# ── Create develop branch ──────────────────────────────────────

git checkout -b develop --quiet
ok "Created 'develop' branch from main"

# ── Summary ─────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Gitflow structure ready:${NC}"
echo -e "  ${GREEN}main${NC}    ← production (1 commit)"
echo -e "  ${GREEN}develop${NC} ← integration (current branch)"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "  1. git checkout -b feature/<name>    # start a feature"
echo "  2. Write code, commit with:  feat: description"
echo "  3. Push branch, open PR to develop"
echo ""
echo -e "${CYAN}Branch protection (GitHub):${NC}"
echo "  Settings → Branches → Add rule for 'main':"
echo "  ☑ Require pull request  ☑ Require approval  ☑ Require CI  ☐ Force push"
