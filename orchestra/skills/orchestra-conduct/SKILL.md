---
name: orchestra-conduct
description: "Orchestrate work across multiple Claude Code sessions. Discover available services, post tasks to their inboxes, and collect results via inotifywait."
---

# Orchestra Conduct — Orchestrator Mode

Coordinate work across independent Claude Code sessions. You post tasks to specialist services and collect their results.

## When to Use

When the user wants to coordinate work across multiple projects/sessions. Run this from the orchestrator's working directory.

## Arguments

The session name can be passed as an argument: `/orchestra-conduct tax-automation`

## Process

### 1. Get the goal

Ask the user: **"What are we coordinating? Describe the goal and which services are involved."**

### 2. Create or identify the session

If an argument was provided, check if it exists:
```bash
orch status <session-name>
```

If no session exists yet:
```bash
orch new <session-name>
```

### 3. Discover available services

Check which services have joined:
```bash
orch status <session-name>
```

To see what each service can do, read their registrations:
```bash
cat ~/.orchestra/services/*/service.md
```

If needed services have not joined yet, tell the user:
**"The following services need to join: [list]. Open their project terminals and run `/orchestra-join <session-name>`."**

Wait for the user to confirm services have joined. Re-check with `orch status`.

### 4. Plan the work breakdown

Based on the goal and available services, break the work into tasks. Consider:

- **Dependencies**: Which tasks must complete before others can start?
- **Parallelism**: Which tasks can run simultaneously?
- **Service capabilities**: Match tasks to the right service based on their registered capabilities

Present the plan to the user: **"Here is how I will break this down: [task list with service assignments]. Does this look right?"**

### 5. Post tasks

For each task (respecting dependency order):
```bash
orch post <session-name> <service-name> "<task description>"
```

Be specific in task descriptions. Include:
- What exactly needs to be done
- Any constraints or requirements
- What format you need the response in
- References to previous task results if this task depends on them

### 6. Wait for results

Start monitoring the outbox for replies:

Use the **Monitor** tool with:
```bash
inotifywait -m -e close_write --format '%f' --include '\.md$' ~/.orchestra/sessions/<session-name>/outbox/
```

This blocks with **zero token cost** until a result arrives.

### 7. Process results

When a result notification arrives (a filename like `001.md`):

1. **Read the result file**: Use the Read tool on `~/.orchestra/sessions/<session-name>/outbox/<filename>`
2. **Evaluate the response**: Does it satisfy the task? Is there enough information to proceed?
3. **If a follow-up task depends on this result**: Post the next task, including relevant information from the result
4. **If the result is insufficient**: Post a clarification task to the same service
5. **Archive the pair** once you have extracted what you need: `orch archive <session-name> <task-id>`. This moves the inbox/outbox files into `archive/` so the active dirs stay small and future reads or glob/ls calls don't re-surface stale content. The full history stays in `log.md` and under `archive/`.

### 8. Coordinate across results

As results come in:
- Track which tasks are complete and which are outstanding
- Identify when enough results are in to post dependent tasks
- Synthesize information across service responses when needed
- Use `orch check <session>` to see what's still pending
- Use `orch results <session>` to review what's completed

### 9. Report completion

When all tasks are done, summarize for the user:
```bash
orch log <session-name>
```

Present a summary: what was accomplished, any issues encountered, and the final state.

## Rules

1. **One task at a time per service** — do not post a second task to a service until the first is complete
2. **Be specific** — workers have their own project context but no awareness of the broader goal. Give them everything they need
3. **Respect dependencies** — do not post a task that depends on another until the dependency is resolved
4. **Let the user drive** — present plans before executing. The user supervises all terminals
5. **Use the log** — check `orch log` to track what has happened if you lose context
