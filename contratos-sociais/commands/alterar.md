---
name: alterar
description: Generate a contract amendment (alteracao contratual) for a Brazilian company by modifying specific clauses.
argument-hint: "<company-name> [--jsons-dir <path>]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - Skill
  - AskUserQuestion
---

# /alterar

Generate a contract amendment (alteracao contratual) for a Brazilian company.

## Invocation

Load the `alteracao` skill by reading `$CLAUDE_PLUGIN_ROOT/skills/alteracao/SKILL.md` and follow its workflow.

## Arguments

- **Company name**: `/alterar "Empresa Exemplo Ltda"` -- look up the company and start the amendment workflow.
- **`--jsons-dir <path>`**: Specify the directory containing the JSON contract database. If not provided, ask the user.

## Workflow

1. Parse the company name from the argument.
2. If no `--jsons-dir` is provided, ask the user for the JSON database path.
3. Follow the alteracao skill workflow exactly:
   - Look up the company
   - Understand the user's desired changes
   - Display current clause state
   - Modify affected clauses
   - Assemble the amendment document
   - Optionally update the JSON database
4. Always ask for user confirmation before generating the final document.
