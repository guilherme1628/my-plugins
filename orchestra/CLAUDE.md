# Orchestra

Event-driven multi-session coordination plugin for Claude Code. Lets independent sessions communicate via a filesystem message bus using inotifywait.

## Structure

- `bin/orch` — Bash CLI (new, join, leave, post, reply, archive, check, status, results, log)
- `skills/orchestra-conduct/` — Orchestrator skill (discover, delegate, collect)
- `skills/orchestra-join/` — Worker skill (join, listen, execute, reply)
- `hooks/` — SessionStart injection
- `.claude-plugin/plugin.json` — Plugin metadata

## Mailbox

All state lives in `~/.orchestra/`:
- `sessions/<name>/` — per-session: manifest.json, inbox/, outbox/, archive/{inbox,outbox}/, log.md, .counter
- `services/<name>/service.md` — global service registry

## Key Patterns

- Tasks are markdown files with YAML frontmatter (id, from, to, status, created)
- Workers filter inbox by `to:` field matching their service name
- inotifywait + Monitor = zero-cost idle, instant wakeup on file events
- `close_write` event ensures file is fully written before processing
- Append-only log.md for audit trail

## Dependencies

- `inotifywait` (inotify-tools package on Linux)
- `jq` (for manifest.json manipulation)
- `bash` 4+
