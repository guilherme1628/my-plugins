---
name: converter
description: Convert Brazilian corporate contracts (contratos sociais, alteracoes contratuais) from PDF/DOCX to structured JSON.
argument-hint: "<file-or-folder> [--jsons-dir <path>]"
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

# /converter

Convert Brazilian corporate contract documents to structured JSON.

## Invocation

Load the `convert-contrato` skill by reading `$CLAUDE_PLUGIN_ROOT/skills/convert-contrato/SKILL.md` and follow its workflow.

## Arguments

- **Single file**: `/converter path/to/contract.pdf` -- convert one file.
- **Directory**: `/converter path/to/folder/` -- batch-convert all PDF/DOCX files in the directory.
- **`--jsons-dir <path>`**: Specify the output directory for JSON files. If not provided, ask the user.

## Workflow

1. Parse the argument to determine single-file or batch mode.
2. If no `--jsons-dir` is provided, ask the user where to save the JSONs.
3. Follow the convert-contrato skill workflow exactly.
4. Report results when done.
