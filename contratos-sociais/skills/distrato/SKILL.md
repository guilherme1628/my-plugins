---
name: distrato
description: This skill should be used when the user asks to "generate a distrato", "dissolve a company", "create a distrato social", "close a company", "encerrar atividades", "encerramento de empresa", or any company dissolution task for Brazilian companies.
---

# Distrato Social

Generate Brazilian company dissolution documents (distrato social) from an existing contrato social JSON.

**CRITICAL CONSTRAINT**: Data from the contrato social must be used verbatim. Gender agreement, singular/plural, and values by extenso must be correct.

All output documents are in **Brazilian Portuguese**. These instructions are in English.

---

## Step 1: Lookup the Company

Run the shared search script to find the company's contract JSON:

```bash
python3 $CLAUDE_PLUGIN_ROOT/scripts/find_company.py "<company_name>" --jsons-dir "<jsons-directory>" --summary
```

- **Not found**: Ask the user to provide the contract PDF, then invoke the convert-contrato skill to create the JSON first.
- **Multiple matches**: Present the list to the user and ask which company they mean.
- **Single match**: Load the full JSON (run again without `--summary`) and proceed.

After loading, confirm with the user: company name, CNPJ, number of clauses, number of partners.

---

## Step 2: Extract Data from JSON

Extract the following fields from the contrato social JSON and prepare the distrato input data.

### Direct Extraction (from JSON top-level fields)

| Distrato Field | JSON Source | Notes |
|----------------|-------------|-------|
| `empresa.nome` | `empresa.nome` | Direct copy |
| `empresa.cnpj` | `empresa.cnpj` | Direct copy |
| `empresa.endereco` | `empresa.endereco` | Normalize per Step 2.5 |
| `socios[].nome` | `socios[].nome` | Direct copy |
| `socios[].cpf` | `socios[].cpf` | Direct copy |
| `socios[].nacionalidade` | `socios[].nacionalidade` | Direct copy |
| `socios[].estado_civil` | `socios[].estado_civil` | Direct copy |
| `socios[].profissao` | `socios[].profissao` | Direct copy |
| `socios[].data_nascimento` | `socios[].data_nascimento` | Direct copy |
| `socios[].endereco` | `socios[].endereco` (object) | Normalize and flatten to string |
| `socios[].doc_identidade` | `socios[].documento_identidade` | Map `rg` and `orgao_emissor` |
| `socios[].quotas` | `socios[].cotas.quantidade` | Numeric value |
| `socios[].percentual` | `socios[].participacao` | Direct copy |
| `cidade` | `assinatura.cidade` | Direct copy |

### Computed from Partner Data

| Distrato Field | Computation |
|----------------|-------------|
| `socios[].valor` | `socios[].cotas.quantidade * parseFloat(socios[].cotas.valor_unitario)` formatted as `R$ X.XXX,XX` |
| `capitalSocial.valor` | Sum of all `socios[].valor` |

### Extracted from Clause Text (search `contrato_consolidado`)

| Distrato Field | Search Strategy | Clause Category |
|----------------|-----------------|-----------------|
| `objetoSocial` | Find clause with `categoria: "Objeto Social"`. Extract `texto_original`. Strip the preamble text (e.g., "A sociedade tem por objeto social") and keep only the activity description. | "Objeto Social" |
| `dataInicioAtividades` | Search clause text for patterns: `"início de suas atividades em DD/MM/AAAA"`, `"iniciou suas atividades em DD/MM/AAAA"`, `"atividades a partir de DD/MM/AAAA"`. Also check "Prazo de Duração" clause. | "Prazo" or other |
| `capitalSocial.extenso` | Find clause with `categoria: "Capital Social"`. Extract the extenso from parenthetical: `R$ X (EXTENSO)`. | "Capital Social" |

### Extracted from Clause Text (NIRE and Session Date)

| Distrato Field | Search Strategy |
|----------------|-----------------|
| `nire` | Search ALL clause texts for pattern: `NIRE[:\s]*[\d.]+` or `nº [\d.]+` near "Junta Comercial". Also check preamble text of the original contrato social (first clause or header area). |
| `juntaComercial` | Search for "Junta Comercial" + state name. Common pattern: `"Junta Comercial do Estado de [estado] – [sigla]"` |
| `dataSessao` | Search for "sessão de DD/MM/AAAA" near NIRE or Junta Comercial reference |

### Must Ask User (not in JSON)

| Field | Question to Ask |
|-------|-----------------|
| `dataEncerramentoAtividades` | "Qual a data de encerramento das atividades? (DD/MM/AAAA)" |
| `liquidante` | "Qual sócio será responsável pela liquidação do Ativo e Passivo?" (If single partner, auto-assign. If multi-partner, present list and include "Todos" option. Use `"all"` in the input JSON for all partners.) |
| `nire` (if not found) | "Qual o NIRE da empresa? (Número de Identificação do Registro de Empresas)" |
| `dataSessao` (if not found) | "Qual a data da sessão de arquivamento na Junta Comercial? (DD/MM/AAAA)" |
| `dataInicioAtividades` (if not found) | "Qual a data de início das atividades? (DD/MM/AAAA)" |
| `socios[].naturalidade` (if not in JSON) | "Qual a naturalidade (cidade/UF de nascimento) de [nome do sócio]?" |
| `socios[].valor_extenso` | Construct manually (no auto-generation): "Confirme o valor por extenso do capital de [nome]: R$ X,XX ([extenso])" |
| `capitalSocial.extenso` (if not found) | "Qual o valor do capital social por extenso?" |

---

## Step 2.5: Normalize Addresses

Apply standard format to ALL addresses: `Logradouro, número, complemento, Bairro, Cidade-UF, CEP: XX.XXX-XXX`

**For partner addresses from JSON** (structured object):
```
socios[].endereco.logradouro, socios[].endereco.numero, socios[].endereco.bairro, socios[].endereco.cidade-socios[].endereco.estado, CEP: XX.XXX-XXX
```

Rules: No "bairro:" prefix, Cidade-UF with hyphen, CEP with `CEP:` prefix and dot separator, title case, standard abbreviations (`Conj.`, `Apto.`, `Av.`).

---

## Step 3: Confirm with User

Present the extracted data to the user for confirmation:

1. **Company**: Nome, CNPJ, Sede
2. **Partners**: Name, CPF, qualification summary for each
3. **NIRE**: Value found or "(not found — will ask)"
4. **Capital Social**: Value + extenso
5. **Objeto Social**: Activity description text
6. **Activity dates**: Start date, end date
7. **Liquidation partner**: Who is responsible

Ask: "Os dados estão corretos? Posso prosseguir com a geração do distrato?"

---

## Step 4: Build Input JSON and Generate Document

Assemble the input JSON object with all extracted and confirmed data, then call the generator:

```bash
node $CLAUDE_PLUGIN_ROOT/skills/distrato/scripts/generate-distrato.js <input.json> <output.docx>
```

Read `$CLAUDE_PLUGIN_ROOT/skills/distrato/references/distrato-format.md` for the document structure and clause templates.

If the generator is not available or fails, assemble the document manually following the format reference, using the same docx-js patterns documented in `$CLAUDE_PLUGIN_ROOT/skills/alteracao/references/docx-format.md`.

---

## Step 5: Update Database (Optional)

Ask the user: "Deseja salvar o distrato no banco de dados JSON?"

If yes:
1. Create a new JSON following the schema in `$CLAUDE_PLUGIN_ROOT/references/schema.md`.
2. Set `tipo_documento` to `"Distrato Social"`.
3. Set `versao_alteracao` to `null`.
4. Include the relevant contract data.
5. Save to the jsons directory with the standard filename pattern.

---

## Workflow Summary

1. **Lookup** -> Find company JSON
2. **Extract** -> Pull data from JSON clauses, ask user for missing info
3. **Confirm** -> Present data to user for validation
4. **Generate** -> Build distrato .docx
5. **Database (optional)** -> Save to JSON database

---

## Critical Rules

1. **VERBATIM DATA** -- Company names, partner names, CPF, CNPJ, addresses from JSON must be used exactly as found.
2. **VALUES BY EXTENSO** -- Every monetary value must be followed by its written form: `R$ 10.000,00 (dez mil reais)`.
3. **GENDER AGREEMENT** -- All gendered terms must match the partner: `brasileiro/brasileira`, `sócio/sócia`, `único/única`, etc.
4. **SINGULAR/PLURAL** -- Use correct forms for single vs. multiple partners in preamble, clauses, and closing.
5. **DOCUMENT LANGUAGE** -- Entire output in Brazilian Portuguese.
6. **CPF/CNPJ FORMAT** -- Standard punctuation.
7. **ADDRESS NORMALIZATION** -- Standard format per Step 2.5.

---

## Resources

### $CLAUDE_PLUGIN_ROOT/scripts/
- `find_company.py` -- Searches the jsons directory by company name; prioritizes the latest version.

### scripts/
- `generate-distrato.js` -- Complete distrato DOCX generator. Can be used directly or as reference.

### references/
- `distrato-format.md` -- Document format spec: clause templates, singular/plural/gender variants.

### $CLAUDE_PLUGIN_ROOT/skills/alteracao/scripts/
- `docx-helpers.js` -- Shared DOCX helpers (text formatting, tables, spacing, gender logic).

### $CLAUDE_PLUGIN_ROOT/skills/alteracao/references/
- `docx-format.md` -- Word document formatting specification (page setup, tables, typography). Shared across document types.

### $CLAUDE_PLUGIN_ROOT/references/
- `schema.md` -- JSON schema for contract data.
