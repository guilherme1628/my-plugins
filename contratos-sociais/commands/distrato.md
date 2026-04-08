---
name: distrato
description: Generate a distrato social (company dissolution document) for a Brazilian company.
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

# /distrato

Generate a distrato social (company dissolution document) for a Brazilian company.

## Invocation

Load the `distrato` skill by reading `$CLAUDE_PLUGIN_ROOT/skills/distrato/SKILL.md` and follow its workflow.

## Arguments

- **Company name**: `/distrato "Empresa Exemplo Ltda"` -- look up the company and start the distrato workflow.
- **`--jsons-dir <path>`**: Specify the directory containing the JSON contract database. If not provided, ask the user.

## Workflow

1. Parse the company name from the argument.
2. If no `--jsons-dir` is provided, ask the user for the JSON database path.
3. Follow the distrato skill workflow exactly:
   - Look up the company
   - Extract data from contrato social JSON
   - Ask user for missing data (NIRE, session date, activity dates, liquidation partner)
   - Generate the distrato .docx
   - Optionally update the JSON database
4. Always ask for user confirmation before generating the final document.
