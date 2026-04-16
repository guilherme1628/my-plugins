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

Use the **Monitor** tool to watch the session inbox:

```bash
inotifywait -m -e close_write --format '%f' --include '\.md$' ~/.orchestra/sessions/<session-name>/inbox/
```

This blocks at the OS level with **zero token cost** until a task file arrives. Each new `.md` file triggers a notification with the filename.

### 4. When a task notification arrives

For each notification (a filename like `003.md`):

1. **Read the task file**: Use the Read tool on `~/.orchestra/sessions/<session-name>/inbox/<filename>`
2. **Check the `to:` field** in the frontmatter. If it does NOT match your service name, **ignore it** and continue listening.
3. **If it matches you**, read the task body (everything after the `---` frontmatter closing).

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

If the response is long (multi-line), write the outbox file directly:

```bash
cat > ~/.orchestra/sessions/<session-name>/outbox/<task-id>.md <<'EOF'
---
id: <task-id>
from: <your-service-name>
to: orchestrator
status: completed
created: <timestamp>
---

<your detailed response here>
EOF
```

Then update the inbox status and log:
```bash
sed -i 's/^status:.*/status: completed/' ~/.orchestra/sessions/<session-name>/inbox/<task-id>.md
echo "[$(date -u +%Y-%m-%dT%H:%M:%S)] <your-service-name> replied to task <task-id>" >> ~/.orchestra/sessions/<session-name>/log.md
```

### 7. Continue listening

After replying, the Monitor is still running. The next inotifywait notification arrives when another task is posted. Repeat from step 4.

## Rules

1. **Never stop listening** unless the user explicitly asks you to leave the session
2. **Filter by `to:` field** — only process tasks addressed to your service name
3. **Full project context** — use all your project files, CLAUDE.md, memory, and tools. That is the whole point of Orchestra
4. **Ask before changing code** — surface coding tasks to the user for confirmation
5. **Be concise in replies** — the orchestrator needs actionable information, not essays
6. **One task at a time** — finish and reply before picking up the next task
