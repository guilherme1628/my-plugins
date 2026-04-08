---
name: alteracao
description: This skill should be used when the user asks to "create a contract amendment", "generate alteracao contratual", "modify a contract clause", "remove a partner", "add a partner", "transfer quotas", "change company address", "change company name", "change objeto social", "increase capital", or any contract modification task for Brazilian companies. Covers all types of alteracoes contratuais for Junta Comercial registration.
---

# Alteracao Contratual

Generate Brazilian contract amendments by surgically modifying specific clauses from an existing contract clause map (structured JSON) while preserving everything else character-for-character.

**CRITICAL CONSTRAINT**: Unchanged clauses must be preserved verbatim. A single misplaced comma can void the document at the Junta Comercial.

All output documents are in **Brazilian Portuguese**. These instructions are in English.

---

## Step 1: Lookup the Company

Run the search script to find the company's contract JSON:

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/find_company.py "<company_name>" --jsons-dir "<jsons-directory>" --summary
```

- **Not found**: Ask the user to provide the contract PDF, then invoke the convert-contrato skill to create the JSON first.
- **Multiple matches**: Present the list to the user and ask which company they mean.
- **Single match**: Load the full JSON (run again without `--summary`) and proceed.

After loading, confirm with the user: company name, CNPJ, number of clauses, number of partners.

---

## Step 2: Understand the Instruction

Parse the user's request and determine what changes are needed.

1. Read `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/clause-categories.md` to map the instruction to affected clause categories.
2. Identify ALL affected clauses -- changes often cascade:
   - Removing a partner affects: quadro societario, capital social, and possibly administracao.
   - Adding a partner affects: quadro societario, capital social, and possibly administracao.
   - Changing the company name affects: nome empresarial, and any clause that references it.
3. Use the dependency matrix in `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/clause-categories.md` Section 3 to check for secondary impacts.
4. If the user's instruction is ambiguous or missing details (e.g., "remove partner X" but no destination for quotas), ask before proceeding.

---

## Step 3: Display Current State

Before making any changes, show the user:

- The exact `texto_original` of each clause that will be modified (copied from the JSON).
- Which clauses will remain unchanged.
- What information is still needed (new address, new partner details, quota distribution, etc.).

**Ask for explicit confirmation before proceeding.**

Collect any missing details: full qualification of new partners, new addresses, capital amounts, integration method, etc.

---

## Step 3.5: Normalize Addresses

Before modifying clauses, normalize ALL addresses in the input data to the standard format defined in `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/alteracao-format.md` Section 9.

**Standard format**: `Logradouro, número, complemento, Bairro, Cidade-UF, CEP: XX.XXX-XXX`

Apply to:
- Partner addresses in the `socios` array (used in the qualification block and preamble)
- Company address in the `empresa` object (used in the preamble)
- Any new address provided by the user (alteration clause + consolidated clause)
- Address in the sede clause of `clausulasConsolidadas` (if being modified)

**Rules**:
- No "bairro:" prefix -- just the bairro name
- Cidade-UF with hyphen, no spaces (e.g., `São Paulo-SP`)
- CEP with `CEP:` prefix and dot separator (e.g., `CEP: 05.442-000`)
- Title case (never ALL CAPS)
- Standard abbreviations: `Conj.`, `Cj.`, `Apto.`, `Av.`

---

## Step 4: Modify Clauses

**LOW FREEDOM -- this step is critical.**

For each affected clause:

1. Take the `texto_original` from the JSON as the starting point.
2. Rewrite ONLY the parts that change, preserving:
   - The exact formatting style (numbering, capitalization, punctuation).
   - The legal language patterns of the original contract.
   - The clause title style (ordinal, roman numeral, or descriptive -- match the original).
3. Read `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/alteracao-format.md` for standard alteration clause patterns.
4. Apply these rules:
   - **Values by extenso**: `R$ 50.000,00 (cinquenta mil reais)`.
   - **Quantities by extenso**: `50.000 (cinquenta mil) quotas`.
   - **Retroqualification**: After first full mention, use `retroqualificado(a)`.
   - **Gender agreement**: Match `brasileiro/brasileira`, `portador/portadora`, etc.
   - **Singular/plural**: Use singular preamble/closing for single-partner companies (see `alteracao-format.md` Section 10).
5. **NEVER touch clauses that are not affected by the change.**

Present the modified clause texts to the user for review BEFORE assembling the document.

---

## Step 5: Assemble the Document

Follow the structure defined in `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/alteracao-format.md`:

1. **Header** -- Company name (caps), CNPJ, NIRE (if available).
2. **Title** -- `Xa ALTERACAO CONTRATUAL` (determine X from `versao_alteracao` in the JSON + 1).
3. **Partner qualification blocks** -- Full qualification of each partner using data from the JSON `socios` array. Use the template from `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/alteracao-format.md` Section 4.
4. **Preamble** -- Standard deliberation text connecting partners to the alterations.
5. **Numbered alteration clauses** -- Roman numerals (I, II, III...) with descriptive titles.
6. **Inalteradas statement** -- `"Ficam inalteradas as demais clausulas e condicoes do contrato social."`
7. **Consolidated contract** -- ALL clauses in order:
   - **Unchanged clauses**: Copy `texto_original` and all `paragrafos` CHARACTER-FOR-CHARACTER from the JSON. Do not reformat, re-punctuate, or "fix" anything.
   - **Modified clauses**: Insert the new text as approved in Step 4.
8. **Signature block** -- City with current date (e.g., "São Paulo-SP, 02 de fevereiro de 2026"), signature lines for all partners with CPF in single-column layout.

Generate the document as a **Word file (.docx)** following the formatting specification in `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/docx-format.md`:

1. **Page setup**: A4, margins as specified, Arial 12pt, 1.35 line spacing.
2. **Header**: Document title with horizontal line separator.
3. **Footer**: Page number right-aligned.
4. **Text formatting**:
   - Partner names and company names in **bold**.
   - Clause titles in **bold**.
   - Body text justified.
   - Document title and consolidation title centered.
   - **Alteration clause titles (I, II, III...) left-aligned.**
5. **Quadro societário**: Use the 4-column table format (SÓCIO | % | QUOTAS | VALOR) with:
   - `columnWidths` at table level: [3450, 1255, 2353, 2347] DXA
   - `TableLayoutType.FIXED`
   - Thin borders on header row only, top border on TOTAL row.
6. **Signature block**: Use **single-column** table (one signature per row, centered).
7. **Date**: Use the generation date formatted in Portuguese (e.g., "02 de fevereiro de 2026").
8. **Dynamic spacing**: Calculate optimal margins/line spacing/paragraph spacing to minimize awkward page breaks.
9. **Security**: Last clause must have `keepNext: true` to stay with closing + signatures (prevents blank signature pages).

Generate the `.docx` file using the docx-js library (`npm install docx`).

**Reference script**: `$CLAUDE_PLUGIN_ROOT/skills/alteracao/scripts/generate-docx.js` contains a complete working implementation. You can either:
- Use it directly: `node scripts/generate-docx.js input.json output.docx`
- Reference it for the correct docx-js patterns and dynamic spacing calculation

---

## Step 6: Generate Plain Text (Optional)

If the user requests a plain text version, also save as `.txt` file without formatting.

---

## Step 7: Update Database (Optional)

Ask the user: "Deseja salvar o contrato consolidado atualizado no banco de dados JSON?"

If yes:
1. Create a new JSON following the schema in `$CLAUDE_PLUGIN_ROOT/references/schema.md`.
2. Set `tipo_documento` to `"Alteracao Contratual"`.
3. Set `versao_alteracao` to the correct ordinal (e.g., `"4a Alteracao"`).
4. Include the updated `contrato_consolidado` with all clauses (unchanged copied verbatim, modified with new text).
5. Save to the jsons directory with the standard filename pattern.

---

## Workflow Summary

1. **Lookup** → Find company JSON
2. **Understand** → Parse user instruction, identify affected clauses
3. **Display** → Show current state, get confirmation
4. **Modify** → Rewrite affected clauses only
5. **Assemble** → Build Word document (.docx) with professional formatting
6. **Plain text (optional)** → Generate .txt if requested
7. **Database (optional)** → Update JSON database

---

## Critical Rules

These rules are non-negotiable and must be followed in every alteracao:

1. **VERBATIM PRESERVATION** -- Unchanged clauses are copied character-by-character from the JSON `contrato_consolidado`. Zero tolerance for modifications.
2. **VALUES BY EXTENSO** -- Every monetary value must be followed by its written form: `R$ 10.000,00 (dez mil reais)`.
3. **QUANTITIES BY EXTENSO** -- Every quota quantity must be followed by its written form: `10.000 (dez mil) quotas`.
4. **RETROQUALIFICATION** -- After the first full mention of a partner in the qualification block, subsequent references use only `[NOME], retroqualificado(a)`.
5. **GENDER AGREEMENT** -- All gendered terms must match the partner: `brasileiro/brasileira`, `portador/portadora`, `inscrito/inscrita`, `domiciliado/domiciliada`, `nascido/nascida`.
6. **DOCUMENT LANGUAGE** -- The entire output document is in Brazilian Portuguese. No exceptions.
7. **CPF/CNPJ FORMAT** -- Always formatted with standard punctuation: `XXX.XXX.XXX-XX` / `XX.XXX.XXX/XXXX-XX`.
8. **CLAUSE STYLE MATCHING** -- The consolidated contract must use the same clause title style as the original (ordinal words, roman numerals, or descriptive headings).
9. **ADDRESS NORMALIZATION** -- All addresses must follow the standard format: `Logradouro, número, complemento, Bairro, Cidade-UF, CEP: XX.XXX-XXX`. No "bairro:" prefix, no ALL CAPS, CEP with dot separator.
10. **SINGULAR/PLURAL** -- Use singular forms (preamble, closing, qualification ending) when there is only one partner. Use plural when there are multiple partners. The generate-docx.js script handles this automatically.

---

## Resources

### $CLAUDE_PLUGIN_ROOT/scripts/
- `find_company.py` -- Searches the jsons directory by company name; prioritizes the latest version (highest-numbered alteracao).

### scripts/
- `generate-docx.js` -- Complete DOCX generator with dynamic spacing, security measures, and proper formatting. Can be used directly or as reference.
- `docx-helpers.js` -- Shared DOCX helpers (text formatting, tables, spacing, gender logic). Used by all generators.

### references/
- `alteracao-format.md` -- Standard document format: header, preamble, clause patterns, signature block.
- `clause-categories.md` -- Maps user instructions to affected clauses, including cascading dependencies.
- `docx-format.md` -- Word document formatting specification: page setup, typography, tables for quadro societário and signatures.

### $CLAUDE_PLUGIN_ROOT/references/
- `schema.md` -- JSON schema for contract data (clause structure, partner fields, etc.).
