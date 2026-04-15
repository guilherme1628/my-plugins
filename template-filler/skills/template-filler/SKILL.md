---
name: template-filler
description: Automate professional document generation from local .docx templates with typed placeholder replacement, CNPJ lookup integration, and contractor memory. Use when generating contracts, invoices, or proposals from Word templates while preserving formatting.
---

# Template Filler Skill (Local)

Generate professional documents from **local .docx templates** by replacing typed `{{field:type:format}}` placeholders with actual data. Integrates with ReceitaWS for automatic Brazilian company (CNPJ) lookup and maintains persistent contractor memory. No Google Cloud / Google Drive setup required.

## When to Use This Skill

- Generate contracts, invoices, or proposals from a local Word template
- Fill repeat documents for the same client faster (contractor memory)
- Look up Brazilian company data by CNPJ automatically
- Produce professional documents while preserving original formatting

## Placeholder Syntax

Templates use `{{field_name:type:format}}` placeholders:

| Type | Example | Renders |
|---|---|---|
| `text` | `{{cliente_nome:text}}` | `Acme LTDA` |
| `text` + mask | `{{cnpj:text:##.###.###/####-##}}` | `12.345.678/0001-90` |
| `text_uppercase` | `{{cliente_nome:text_uppercase}}` | `ACME LTDA` |
| `date` | `{{data_inicio:date:dd/mm/yyyy}}` | `01/05/2026` |
| `date` long | `{{data:date:dd de MMMM de yyyy}}` | `15 de abril de 2026` |
| `currency_number` | `{{valor:currency_number:##.###,##}}` | `1.500,00` |
| `currency_text` | `{{valor_extenso:currency_text}}` | `mil e quinhentos reais` |

Mask characters: `#` = digit from input, `@` = letter from input, anything else = literal.

**Auto-fallback**: `{{foo_extenso:currency_text}}` resolves from `foo` if `foo_extenso` is not in the data — you only need to provide `valor`, not both `valor` and `valor_extenso`.

## Directory Layout

```
~/Documents/template_filler_data/        ← default data root (override with $TEMPLATE_FILLER_DIR)
├── templates/                           ← drop .docx templates here (name starts with TEMPLATE_)
│   └── TEMPLATE_Contrato-Prestacao-Servicos.docx
├── contratada_*.json                    ← reusable "your firm" data
├── terms_*.json                         ← optional reusable contract terms
└── generated/                           ← default output for generate_contract.py
```

## Scripts

All scripts live in `$CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/` and return JSON or plain text.

### list_templates.py
Lists `.docx` files in the templates folder.
```bash
python3 list_templates.py
```

### parse_template.py
Extracts typed placeholders from a local `.docx`.
```bash
python3 parse_template.py /path/to/TEMPLATE_Contrato.docx
```
Output: JSON `{template, total_fields, fields: [{name, type, format, required}, ...]}`

### lookup_cnpj.py
Fetches Brazilian company data via ReceitaWS (no API key).
```bash
python3 lookup_cnpj.py 12345678000190
```

### manage_contractors.py
Persistent contractor memory (list, search, get).
```bash
python3 manage_contractors.py list
python3 manage_contractors.py search "Petrobras"
```

### fill_docx.py
Low-level template filler. Takes a template and a flat JSON data dict.
```bash
python3 fill_docx.py <template.docx> <data.json> [output.docx]
```

### generate_contract.py
End-to-end orchestrator. Merges contratada JSON + ReceitaWS lookup + contract terms, then fills the template.
```bash
python3 generate_contract.py \
    --template TEMPLATE_Contrato-Prestacao-Servicos \
    --contratante 41618108000120 \
    --contratada ~/Documents/template_filler_data/contratada_ecab.json \
    --terms /tmp/terms.json
```

Flags:
- `--template` — name fragment (resolves against templates folder) or full path
- `--contratante` — CNPJ (digits or formatted)
- `--contratada` — JSON file with your firm's fields (`contratada_*`)
- `--terms` — JSON file with contract-specific fields (`valor`, `multa`, `data_inicio`, `local`, `indice_correcao`, ...)
- `--output` — optional explicit output path
- `--dry-run` — print merged data without writing the file

## Typical Workflow

1. **One-time setup**: drop your template into `~/Documents/template_filler_data/templates/` and create a `contratada_*.json` with your firm's data.
2. **For each new contract**, you only need:
   - Client CNPJ (address comes from ReceitaWS)
   - Contract terms: `valor`, `data_inicio`, `multa`, `indice_correcao`, `local`
3. Run `generate_contract.py` — output lands in `~/Documents/template_filler_data/generated/`.

## Data File Shapes

### contratada_*.json (your firm — reusable)
```json
{
  "contratada_razaoSocial": "...",
  "contratada_cnpj": "...",
  "contratada_logradouro": "...",
  "contratada_cidade": "...",
  "contratada_uf": "...",
  "contratada_cep": "...",
  "contratada_crc": "111084/O",
  "contratada_crc_uf": "MG",
  "contratada_representanteLegal_nome": "...",
  "contratada_representanteLegal_cpf": "...",
  "contratada_representanteLegal_profissao": "Contador"
}
```

### terms.json (contract-specific)
```json
{
  "valor": 450.00,
  "multa": 450.00,
  "data_inicio": "2026-05-01",
  "data": "2026-04-15",
  "local": "São Paulo",
  "indice_correcao": "IGPM"
}
```

`data` defaults to today if omitted.

## Install Dependencies

```bash
pip install -r $CLAUDE_PLUGIN_ROOT/requirements.txt
```

Requires: `python-docx`, `num2words`, `requests`.

## Notes & Limitations

- **Run collapsing**: when a placeholder spans multiple formatting runs inside a paragraph, the filler collapses them into the first run. Mixed bold/italic *inside the same paragraph* will normalize to the first run's formatting. Separate paragraphs are unaffected.
- **Templates must be `.docx`** (not legacy `.doc`).
- ReceitaWS is rate-limited to ~3 req/min on the free tier — contractor memory exists to avoid redundant lookups.
