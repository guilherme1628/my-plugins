#!/usr/bin/env bash
# Session pre-flight inspector.
#
# Emits a single JSON object describing the project environment so that
# /session:resume-session and /session:pause-session can skip mechanical
# probing. MCP tool availability is NOT checked here — only CLI state.
#
# Usage: bash session/scripts/inspect.sh [project_root]
# Exit codes: 0 on success (even in non-repo), 2 on internal failure.

set -u
set -o pipefail

ROOT="${1:-$PWD}"
cd "$ROOT" 2>/dev/null || { echo "{\"error\":\"cannot cd into $ROOT\"}"; exit 2; }

json_escape() {
  # Escapes a single string for JSON. Uses python3 if available, else a
  # conservative bash fallback (handles \, ", common control chars).
  if command -v python3 >/dev/null 2>&1; then
    python3 -c 'import json,sys; sys.stdout.write(json.dumps(sys.stdin.read().rstrip("\n")))'
  else
    local s
    s=$(cat)
    s=${s//\\/\\\\}
    s=${s//\"/\\\"}
    s=${s//$'\n'/\\n}
    s=${s//$'\r'/\\r}
    s=${s//$'\t'/\\t}
    printf '"%s"' "$s"
  fi
}

json_array_of_strings() {
  # Reads lines from stdin, emits a JSON array of escaped strings.
  local first=1
  printf '['
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    if [ $first -eq 1 ]; then first=0; else printf ','; fi
    printf '%s' "$line" | json_escape
  done
  printf ']'
}

# ---- git ---------------------------------------------------------------

is_git_repo=false
branch="null"
head_sha="null"
clean=true
upstream="null"
ahead=0
behind=0
recent_commits="[]"
untracked="[]"
modified="[]"
staged="[]"
stashes=0

if git rev-parse --git-dir >/dev/null 2>&1; then
  is_git_repo=true

  if b=$(git branch --show-current 2>/dev/null) && [ -n "$b" ]; then
    branch=$(printf '%s' "$b" | json_escape)
  fi

  if s=$(git rev-parse --short HEAD 2>/dev/null); then
    head_sha=$(printf '%s' "$s" | json_escape)
  fi

  if u=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null); then
    upstream=$(printf '%s' "$u" | json_escape)
    if counts=$(git rev-list --left-right --count "@{u}...HEAD" 2>/dev/null); then
      behind=$(printf '%s' "$counts" | awk '{print $1}')
      ahead=$(printf '%s' "$counts" | awk '{print $2}')
    fi
  fi

  # Commits as {hash, subject}
  if log_out=$(git log -5 --pretty=format:'%h%x09%s' 2>/dev/null); then
    recent_commits=$(
      printf '['
      first=1
      while IFS=$'\t' read -r h subj; do
        [ -z "$h" ] && continue
        if [ $first -eq 1 ]; then first=0; else printf ','; fi
        printf '{"hash":%s,"subject":%s}' \
          "$(printf '%s' "$h" | json_escape)" \
          "$(printf '%s' "$subj" | json_escape)"
      done <<<"$log_out"
      printf ']'
    )
  fi

  # Porcelain status → untracked / modified / staged
  if status_out=$(git status --porcelain=v1 2>/dev/null); then
    if [ -n "$status_out" ]; then clean=false; fi
    untracked=$(printf '%s\n' "$status_out" | awk '/^\?\?/ {sub(/^\?\? /,""); print}' | json_array_of_strings)
    modified=$(printf '%s\n' "$status_out" | awk '/^.M/ {print substr($0,4)}' | json_array_of_strings)
    staged=$(printf '%s\n' "$status_out" | awk '/^[MADRC]./ {print substr($0,4)}' | json_array_of_strings)
  fi

  stashes=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
fi

# ---- session state ----------------------------------------------------

state_path=".session/state.md"
state_exists=false
state_status="null"
state_branch="null"
state_last_updated="null"
if [ -f "$state_path" ]; then
  state_exists=true
  if v=$(grep -m1 '^\*\*Status\*\*:' "$state_path" 2>/dev/null | sed 's/^\*\*Status\*\*:[[:space:]]*//'); then
    [ -n "$v" ] && state_status=$(printf '%s' "$v" | json_escape)
  fi
  if v=$(grep -m1 '^\*\*Last Updated\*\*:' "$state_path" 2>/dev/null | sed 's/^\*\*Last Updated\*\*:[[:space:]]*//'); then
    [ -n "$v" ] && state_last_updated=$(printf '%s' "$v" | json_escape)
  fi
  if v=$(grep -m1 -E '^\-[[:space:]]*\*\*Branch\*\*:' "$state_path" 2>/dev/null | sed -E 's/^-[[:space:]]*\*\*Branch\*\*:[[:space:]]*//; s/[[:space:]]*\(.*$//'); then
    [ -n "$v" ] && state_branch=$(printf '%s' "$v" | json_escape)
  fi
fi

# ---- openspec ---------------------------------------------------------

openspec_installed=false
openspec_initialized=false
openspec_changes="[]"
if command -v openspec >/dev/null 2>&1; then
  openspec_installed=true
  if out=$(openspec list 2>/dev/null); then
    openspec_initialized=true
    openspec_changes=$(printf '%s\n' "$out" | awk 'NF' | json_array_of_strings)
  fi
fi

# ---- crispy -----------------------------------------------------------

# Crispy uses flat artifacts in .crispy/: ticket → questions → research →
# design → outline → plan. Stage = last artifact that exists.
crispy_stage="null"
crispy_artifacts="[]"
if [ -d ".crispy" ]; then
  artifacts=""
  last=""
  for f in ticket questions research design outline plan; do
    if [ -f ".crispy/$f.md" ]; then
      artifacts="$artifacts$f.md"$'\n'
      last="$f"
    fi
  done
  crispy_artifacts=$(printf '%s' "$artifacts" | json_array_of_strings)
  [ -n "$last" ] && crispy_stage=$(printf '%s' "$last" | json_escape)
fi

# ---- orchestra --------------------------------------------------------

orchestra_sessions="[]"
if [ -d "$HOME/.orchestra/sessions" ]; then
  orchestra_sessions=$(find "$HOME/.orchestra/sessions" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | json_array_of_strings)
fi

# ---- key files --------------------------------------------------------

key_files=$(
  {
    for f in README.md README.rst README.txt CLAUDE.md package.json pyproject.toml Cargo.toml go.mod deno.json build.gradle pom.xml; do
      [ -f "$f" ] && printf '%s\n' "$f"
    done
  } | json_array_of_strings
)

# ---- emit -------------------------------------------------------------

cat <<EOF
{
  "root": $(printf '%s' "$ROOT" | json_escape),
  "is_git_repo": $is_git_repo,
  "git": {
    "branch": $branch,
    "head_sha": $head_sha,
    "upstream": $upstream,
    "ahead": $ahead,
    "behind": $behind,
    "clean": $clean,
    "untracked": $untracked,
    "modified": $modified,
    "staged": $staged,
    "recent_commits": $recent_commits,
    "stashes": $stashes
  },
  "session_state": {
    "exists": $state_exists,
    "path": $(printf '%s' "$state_path" | json_escape),
    "status": $state_status,
    "last_updated": $state_last_updated,
    "branch": $state_branch
  },
  "openspec": {
    "installed": $openspec_installed,
    "initialized": $openspec_initialized,
    "changes": $openspec_changes
  },
  "crispy": {
    "stage": $crispy_stage,
    "artifacts": $crispy_artifacts
  },
  "orchestra": {
    "sessions": $orchestra_sessions
  },
  "key_files": $key_files
}
EOF
