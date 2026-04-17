---
name: orchestra-join
description: "Join an Orchestra session as a worker. Registers this project as a service, starts listening for tasks via inotifywait, and processes them with full project context."
---

# Orchestra Join — Worker Mode

Join an orchestration session, listen for tasks, execute them with your full project context, and reply with results.

## When to Use

When the user says "join an orchestra session", "listen for orchestra tasks", or invokes `/orchestra-join`.
You must be in a project directory with a CLAUDE.md file.

## Arguments

The session name can be passed as an argument: `/orchestra-join tax-automation`

## Process

### 1. Get the session name

If an argument was provided, use it. Otherwise ask: **"Which orchestra session should I join?"**

List available sessions if helpful:
```bash
ls ~/.orchestra/sessions/
```

### 2. Join the session

Run:
```bash
orch join <session-name>
```

This reads your CLAUDE.md to derive your service name and capabilities, registers you in the session manifest, and creates your global service entry.

**Read the output carefully** — it tells you your service name. Remember it for filtering tasks.

### 3. Start listening for tasks

Use the **Monitor** tool to watch the session inbox with a filtered pipeline. Replace `<session-name>` and `<your-service-name>` with actual values:

```bash
INBOX="$HOME/.orchestra/sessions/<session-name>/inbox" && inotifywait -m -e close_write --format '%f' --include '\.md$' "$INBOX" | while read -r file; do to=$(awk '/^---$/{c++;next} c==1 && /^to:/{sub(/^[^:]+:[[:space:]]*/,"");print;exit}' "$INBOX/$file"); status=$(awk '/^---$/{c++;next} c==1 && /^status:/{sub(/^[^:]+:[[:space:]]*/,"");print;exit}' "$INBOX/$file"); [ "$to" = "<your-service-name>" ] && [ "$status" = "pending" ] && echo "$file"; done
```

This filters at the bash level — Monitor only notifies you when:
- The task is addressed to your service name (`to:` field matches)
- The task is still pending (ignores `sed -i` status updates that re-trigger `close_write`)

Zero token cost while idle. You only wake up for real work.

### 4. When a task notification arrives

For each notification (a filename like `003.md`):

1. **Read the task file**: Use the Read tool on `~/.orchestra/sessions/<session-name>/inbox/<filename>`
2. Read the task body (everything after the `---` frontmatter closing). The Monitor already filtered for your service name and pending status.

### 5. Execute the task

Read the task body carefully. Then:

- **If it is a question or information request**: Answer it directly using your project knowledge. Read relevant files, check configurations, trace code paths — whatever is needed. Then reply immediately.
- **If it requires code changes**: Tell the user what the task is asking and what you plan to do. **Wait for the user to confirm** before making changes. Follow your project's normal workflows (crispy for features, git-standards for commits).
- **If it is unclear**: Tell the user you received an ambiguous task and ask for guidance.

### 6. Reply with the result

After completing the task, run:

```bash
orch reply <session-name> <task-id> "<your response>"
```

This writes the outbox file, updates the inbox status to completed, and appends to the log — all in one command. The status update won't trigger a false notification because the Monitor filters for `status: pending` only.

For long multi-line responses, write the outbox file directly with the Write tool, then run `orch reply` with a short summary (it will overwrite, but that's fine — or just write the outbox file and update inbox/log manually).

### 7. Continue listening

After replying, the Monitor is still running. The next inotifywait notification arrives when another task is posted. Repeat from step 4.

### 8. Leaving the session

When the user says "leave the session", "stop listening", or the work is done:

1. Stop the Monitor tool watching the inbox.
2. Sweep any completed tasks into the archive so the active dirs stay lean:
   ```bash
   orch archive <session-name>
   ```
   With no task-id, this moves every pair whose inbox status is `completed` (and has a matching outbox reply) into `archive/`. Full history stays in `log.md`.
3. Run:
   ```bash
   orch leave <session-name>
   ```
   This removes your service from the session manifest and appends a log entry. The global service registration in `~/.orchestra/services/` is preserved so you can rejoin this or another session later.
4. Confirm to the user that you have detached.

## Rules

1. **Never stop listening** unless the user explicitly asks you to leave the session
2. **Filter by `to:` field** — only process tasks addressed to your service name
3. **Full project context** — use all your project files, CLAUDE.md, memory, and tools. That is the whole point of Orchestra
4. **Ask before changing code** — surface coding tasks to the user for confirmation
5. **Be concise in replies** — the orchestrator needs actionable information, not essays
6. **One task at a time** — finish and reply before picking up the next task
