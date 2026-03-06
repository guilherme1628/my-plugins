---
name: convert-contrato
description: This skill should be used when the user asks to "convert a contract", "convert contrato social", "extract contract data from PDF", "convert PDF to JSON", "batch convert contracts", "process contract files", or mentions converting Brazilian corporate documents (contratos sociais, alteracoes contratuais) from PDF/DOCX to structured JSON.
---

# Convert Contrato

Convert Brazilian corporate contract PDFs/DOCXs into structured JSON with clause-level parsing. Replaces legacy OCR + GPT pipelines -- Claude reads the files natively.

## Critical Rules

**LOW FREEDOM -- these are non-negotiable:**

- Extract ALL clauses and paragraphs in full. Never summarize or truncate.
- Never use `[...]` or `...` to abbreviate any text.
- Maintain original wording exactly as written in the document.
- Output must be valid JSON matching the schema exactly.
- Every `texto_original` field must contain the complete text, no matter how long.

## Single File Mode

**Steps:**

1. **Read** the PDF or DOCX using the Read tool.
2. **Classify** the document:
   - `Contrato Social` -- original articles of incorporation
   - `Alteracao Contratual` -- amendment to an existing contract
   - `Other` -- not a corporate contract. Report to user and stop.
3. **Load schema** -- Read `$CLAUDE_PLUGIN_ROOT/references/schema.md` for the full extraction schema and field definitions.
4. **Extract** all structured data following the schema. Pay special attention to:
   - Full clause text (never truncate)
   - All partner data (socios) with CPF, address, participation
   - Quadro societario extraction method (text vs image)
   - Versao da alteracao identification (1a, 2a, 3a...)
5. **Save JSON** to the jsons directory with this filename format:
   ```
   {empresa_nome}|{cnpj}|{tipo_documento}|{versao_alteracao}.json
   ```
   - `empresa_nome`: company name from the document
   - `cnpj`: full CNPJ with punctuation (XX.XXX.XXX/XXXX-XX)
   - `tipo_documento`: "Contrato Social" or "Alteracao Contratual"
   - `versao_alteracao`: "1a Alteracao", "2a Alteracao", etc. or "null"
6. **Report** summary: company name, document type, number of clauses, number of partners.

## Batch Mode

**Steps:**

1. **Generate manifest** by running:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/convert-contrato/scripts/batch_convert.py <folder> --jsons-dir "<jsons-directory>"
   ```
   This outputs a JSON array of `{"path", "filename"}` objects to stdout, and a summary to stderr.

2. **Process each file** from the manifest. Use the Task tool to dispatch parallel agents -- each agent:
   - Reads the file
   - Loads the schema from `$CLAUDE_PLUGIN_ROOT/references/schema.md`
   - Extracts structured data per schema
   - Saves JSON to the jsons directory

3. **Collect results** and report:
   - N files converted successfully
   - N files failed (with reasons)
   - N files skipped (already converted)

## Output Path

- **Default:** The user should specify the jsons output directory.
- **Override:** Pass `--output ./custom-dir/` when invoking.

## Resources

### $CLAUDE_PLUGIN_ROOT/references/schema.md
Complete JSON schema with all field definitions, valid categories, format rules, and a validation checklist. **Always load this before extraction.**

### scripts/batch_convert.py
Scans directories for PDF/DOCX files, cross-references against existing JSONs in the jsons directory using fuzzy name matching, and outputs a manifest of files still needing conversion.

Usage: `python3 $CLAUDE_PLUGIN_ROOT/skills/convert-contrato/scripts/batch_convert.py <scan-dir> [--jsons-dir <path>]`
