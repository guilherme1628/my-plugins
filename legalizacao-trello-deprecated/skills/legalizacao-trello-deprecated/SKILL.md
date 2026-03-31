---
name: legalizacao-trello-deprecated
description: "DEPRECATED: Company legalizations via Trello. Use legalizacao-ecab instead. Only use when user explicitly wants Trello integration."
---

# Legalizacao Workflow (DEPRECATED - Use legalizacao-ecab)

Manage company legalization processes in Brazil through Trello integration.

> **This skill is deprecated.** Use `legalizacao-ecab` for the ECAB system instead. This version is kept for reference only.

## Overview

This skill handles three types of company legalizations:
- **ABERTURA** - Opening a new company
- **ALTERACAO** - Modifying an existing company
- **BAIXA** - Closing a company

All tasks are created in the dedicated LEGALIZACAO Trello board with automatic checklists and progress tracking.

## Prerequisites

Environment variables must be set:
```bash
export TRELLO_API_KEY="ae931c700aea370ecf73a316472195fb"
export TRELLO_TOKEN="6ba9880184261c278d88534de39a383b711140947982f75438a83fd353991045"
```

## CLI Commands

Run from `<skill-dir>/scripts/`:

```bash
node index.js collect ABERTURA    # Collect data interactively
node index.js create ABERTURA     # Create task from collected data
node index.js list                # List saved drafts
node index.js report              # Generate status report
node index.js requirements ABERTURA  # Show requirements
node index.js clean               # Clean all drafts
```

## Board Structure

```
LEGALIZACAO Board
+-- RECEBIDAS      (New legalizacoes - entry point)
+-- ANALISE        (Under review)
+-- EM ANDAMENTO   (In progress)
+-- CONCLUIDO      (Completed)
```

## Task Format

- Title: `[TYPE] - Company Name`
- Category: ECAB
- Priority: Urgente/Importante/Normal
- Due date: As specified
- Checklist: Auto-generated based on type

## Data Storage

Draft data is persisted in `~/.legalizacao-data/drafts.json` between sessions.
