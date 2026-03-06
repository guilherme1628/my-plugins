---
name: create-service-manifest
description: Generate a .service.json manifest for integra-contador-tui from a CLI SDK source. Use when user wants to add a new service, wrap a CLI, or create a manifest for the TUI.
---

# Create Service Manifest

Generate a `.service.json` manifest file for the integra-contador-tui application from a CLI SDK's source code, help output, or documentation.

## What is a Service Manifest?

The integra-contador-tui is a Rust TUI that wraps CLI tools. Each service is defined by a JSON manifest (`services/<name>.service.json`) that describes:
- Service identity (name, description, category)
- Operations (CLI subcommands) exposed as TUI forms
- Form fields with types, validations, and placeholders
- Mapping from form fields to CLI flags
- Output handling (PDF files, JSON exports, clipboard)
- Response display formatting (currency, numbers, dot-paths)
- Dynamic triggers (blur events that run lookups and modify other fields)

Dropping a `.service.json` in the `services/` directory is all it takes to add a new service — no Rust code changes needed.

## Your Task

Given source code, `--help` output, or documentation for a CLI tool, generate a complete `.service.json` manifest.

## Step-by-Step Process

### 1. Discover the CLI Interface

From the provided SDK source, extract:
- **Available subcommands** (these become operations)
- **CLI flags** for each subcommand (these become fields + args)
- **Which flags are required vs optional**
- **Flag types** (string, number, date, file path, enum/choices)
- **Output behavior** (does it produce files? what format? where?)
- **JSON response structure** (what fields does it return?)

### 2. Map to Manifest Structure

#### Service Block

```json
{
  "service": {
    "id": "kebab-case-id",
    "name": "Nome do Servico",
    "description": "Descricao curta em pt-BR",
    "prefix": "shortprefix",
    "category": "CATEGORY_NAME"
  }
}
```

Rules:
- `id`: unique kebab-case identifier
- `name`: user-facing name in pt-BR, shown in TUI menu
- `description`: short pt-BR description shown next to name
- `prefix`: short prefix used in CLI subcommands (e.g. `sicalc`, `parc`, `sitfis`)
- `category`: grouping for the main menu (e.g. `"SERPRO"`, `"EMISSOR NACIONAL"`)

#### Runner Block (only if NOT using default bun runtime)

If the CLI uses a different runtime than `bun run cli`, add:

```json
{
  "service": {
    "runner": {
      "command": "python",
      "args": ["cli.py"],
      "cwd": "/path/to/project",
      "env": { "API_KEY": "xxx" }
    }
  }
}
```

The default runtime (when `runner` is omitted) is `bun run cli` in `INTEGRA_CLI_DIR`.

#### Operations

Each CLI subcommand becomes an operation:

```json
{
  "id": "subcommand-name",
  "command": "prefix-subcommand-name",
  "name": "Nome da Operacao",
  "description": "Descricao em pt-BR",
  "fields": [...],
  "args": [...],
  "output": {...},
  "response": {...}
}
```

The `command` is what gets passed as the first argument to the CLI runner. Convention: `{prefix}-{subcommand}`.

#### Fields (Form Inputs)

Map each CLI flag to a form field:

```json
{
  "label": "Nome do Campo",
  "placeholder": "ex: valor esperado",
  "required": true,
  "type": "text",
  "validation": "cpf_cnpj"
}
```

**Field types:**
- `"text"` — free text input (default)
- `"select"` — dropdown, requires `"options": ["OPT1", "OPT2"]`

**Validation rules** (apply based on data type):

| CLI flag accepts     | Use validation | Behavior                          |
|----------------------|----------------|-----------------------------------|
| CPF or CNPJ          | `cpf_cnpj`     | Accepts 11 or 14 digits          |
| CNPJ only            | `cnpj`         | Accepts 14 digits only           |
| Date (YYYY-MM-DD)    | `date`         | Auto-formats with dashes          |
| Integer              | `number`       | Digits only                       |
| Decimal (money etc)  | `decimal`      | Digits and decimal point          |
| Enum/choices         | (use select)   | Use `type: "select"` instead      |
| Free text            | (none)         | No validation                     |

**Placeholder conventions:**
- Show example: `"ex: 12345678901"`
- Show format: `"AAAA-MM-DD"`
- Mark optional: `"ex: SP (opcional)"`

#### Args (Field-to-Flag Mapping)

Map each field to its CLI flag:

```json
{
  "args": [
    { "flag": "-c", "field": "CPF/CNPJ" },
    { "flag": "--periodo", "field": "Periodo", "optional": true }
  ]
}
```

Rules:
- `field` must EXACTLY match a field's `label`
- Add `"optional": true` for non-required fields (skips flag when empty)
- Required fields should NOT have `optional: true`

#### Output (File Handling)

**No file output:**
```json
{ "output": { "type": "none" } }
```

**File output with auto-open:**
```json
{
  "output": {
    "type": "file",
    "format": "pdf",
    "subdir": "pdfs",
    "flag": "-o",
    "flagMode": "dir",
    "autoOpen": true
  }
}
```

**File output with custom filename:**
```json
{
  "output": {
    "type": "file",
    "format": "pdf",
    "subdir": "pdfs",
    "flag": "--output",
    "flagMode": "fullpath",
    "filenamePattern": "report-{CPF/CNPJ:digits}.pdf",
    "autoOpen": true
  }
}
```

**Clipboard copy from response:**
```json
{ "output": { "type": "none", "clipboard": "codigoBarras" } }
```

| `flagMode`  | Behavior                                       |
|-------------|------------------------------------------------|
| `dir`       | Pass directory path; CLI decides filename       |
| `fullpath`  | Pass full path; TUI builds filename from pattern|

**Filename pattern interpolation:**
- `{FieldLabel}` — raw field value
- `{FieldLabel:digits}` — digits only (strips dots, dashes, slashes)

#### Response (Display Formatting)

**Simple field display:**
```json
{
  "response": {
    "displayFields": [
      { "key": "protocolo", "label": "Protocolo" },
      { "key": "calculo.valorTotal", "label": "Valor Total", "format": "currency" },
      { "key": "count", "label": "Total", "format": "number" }
    ]
  }
}
```

**With success message and clipboard:**
```json
{
  "response": {
    "successMessage": "pdfPath",
    "clipboard": "codigoBarras",
    "displayFields": [...]
  }
}
```

**Conditional display by status:**
```json
{
  "response": {
    "statusBranches": [
      {
        "field": "status",
        "value": "PROCESSANDO",
        "displayFields": [
          { "key": "status", "label": "Status" },
          { "key": "tempoEspera", "label": "Tempo Espera (ms)", "format": "number" }
        ]
      },
      {
        "field": "status",
        "value": "CONCLUIDO",
        "displayFields": [
          { "key": "outputPath", "label": "Arquivo" }
        ]
      }
    ]
  }
}
```

**Display formats:**

| Format     | Use for                | Example output    |
|------------|------------------------|-------------------|
| `currency` | Money values           | `R$ 1234.56`      |
| `number`   | Integers/counts        | `42`               |
| (none)     | Strings, booleans      | `Sim` / `Nao`     |

**Dot-paths:** Use `"key": "parent.child"` for nested JSON fields.

#### Triggers (Dynamic Field Lookups)

When a field's value should trigger a CLI lookup (e.g. validating a code, fetching metadata):

```json
{
  "label": "Codigo Receita",
  "required": true,
  "type": "text",
  "trigger": {
    "on": "blur",
    "command": "sicalc-consultar-receita",
    "triggerDescription": "Consultando codigo de receita...",
    "triggerResultDisplay": "receita.descricao",
    "args": [
      { "flag": "-c", "field": "CPF/CNPJ" },
      { "flag": "-r", "field": "Codigo Receita" }
    ],
    "dedupeFields": ["CPF/CNPJ", "Codigo Receita"],
    "effects": [
      {
        "field": "Periodo Apuracao",
        "setRequired": "receita.exigePeriodoApuracao",
        "setPlaceholderTrue": "AAAA-MM-DD (OBRIGATORIO)",
        "setPlaceholderFalse": "AAAA-MM-DD (opcional)"
      }
    ]
  }
}
```

Use triggers when:
- A field value determines whether another field is required
- A field value should show a description/name from the backend
- You need to validate a code against a remote API

**Trigger fields:**
- `on`: always `"blur"` (fires when user tabs away)
- `command`: CLI subcommand to run
- `triggerDescription`: loading message in pt-BR
- `triggerResultDisplay`: dot-path to show inline after lookup
- `dedupeFields`: fields that form the cache key (avoid re-running same lookup)
- `effects`: modify other fields based on response JSON

### 3. Language and Style Rules

- ALL user-facing strings (name, description, labels, placeholders) MUST be in **Brazilian Portuguese (pt-BR)**
- Use descriptive labels: `"Codigo Receita"` not `"code"`
- Use helpful placeholders: `"ex: 12345678901"`, `"AAAA-MM-DD"`
- Mark optional placeholders: `"ex: SP (opcional)"`

### 4. Validation Checklist

Before outputting the manifest, verify:

- [ ] `service.id` is unique kebab-case
- [ ] `service.category` is set
- [ ] Every `args[].field` exactly matches a `fields[].label`
- [ ] Required fields have matching `args` WITHOUT `optional: true`
- [ ] Optional fields have matching `args` WITH `optional: true`
- [ ] `type: "select"` fields have `options` array
- [ ] Date fields have `validation: "date"`
- [ ] CPF/CNPJ fields have `validation: "cpf_cnpj"` or `"cnpj"`
- [ ] Numeric fields have `validation: "number"` or `"decimal"`
- [ ] `response.displayFields[].key` paths match actual CLI JSON output
- [ ] `output.flag` matches the CLI's expected output flag
- [ ] All strings are in pt-BR
- [ ] File is valid JSON (no trailing commas, no comments)

## Real Examples

Below are real manifests from the project for reference.

### Example 1: SICALC (complex — triggers, PDF output, clipboard)

```json
{
  "service": {
    "id": "sicalc",
    "name": "SICALC",
    "description": "Calculo de tributos (DARF)",
    "prefix": "sicalc",
    "category": "SERPRO"
  },
  "operations": [
    {
      "id": "consultar-receita",
      "command": "sicalc-consultar-receita",
      "name": "Consultar Receita",
      "description": "Consultar requisitos de codigo de receita",
      "fields": [
        {
          "label": "CPF/CNPJ",
          "placeholder": "ex: 12345678901",
          "required": true,
          "type": "text",
          "validation": "cpf_cnpj"
        },
        {
          "label": "Codigo Receita",
          "placeholder": "ex: 0211",
          "required": true,
          "type": "text"
        }
      ],
      "args": [
        { "flag": "-c", "field": "CPF/CNPJ" },
        { "flag": "-r", "field": "Codigo Receita" }
      ],
      "output": { "type": "none" },
      "response": {
        "displayFields": [
          { "key": "receita.codigoReceita", "label": "Codigo" },
          { "key": "receita.descricao", "label": "Descricao" },
          { "key": "receita.exigeCodigoExtensao", "label": "Exige Extensao" },
          { "key": "receita.exigeNumeroReferencia", "label": "Exige Referencia" },
          { "key": "receita.exigePeriodoApuracao", "label": "Exige Periodo" }
        ]
      }
    },
    {
      "id": "consolidar-darf",
      "command": "sicalc-consolidar-darf",
      "name": "Consolidar DARF",
      "description": "Gerar PDF do DARF com calculo",
      "fields": [
        {
          "label": "CPF/CNPJ",
          "placeholder": "ex: 12345678901",
          "required": true,
          "type": "text",
          "validation": "cpf_cnpj"
        },
        {
          "label": "Codigo Receita",
          "placeholder": "ex: 0211",
          "required": true,
          "type": "text",
          "trigger": {
            "on": "blur",
            "command": "sicalc-consultar-receita",
            "triggerDescription": "Consultando codigo de receita...",
            "triggerResultDisplay": "receita.descricao",
            "args": [
              { "flag": "-c", "field": "CPF/CNPJ" },
              { "flag": "-r", "field": "Codigo Receita" }
            ],
            "dedupeFields": ["CPF/CNPJ", "Codigo Receita"],
            "effects": [
              {
                "field": "Periodo Apuracao",
                "setRequired": "receita.exigePeriodoApuracao",
                "setPlaceholderTrue": "AAAA-MM-DD (OBRIGATORIO)",
                "setPlaceholderFalse": "AAAA-MM-DD (opcional)"
              }
            ]
          }
        },
        {
          "label": "Data Consolidacao",
          "placeholder": "AAAA-MM-DD",
          "required": true,
          "type": "text",
          "validation": "date"
        },
        {
          "label": "Valor Principal (R$)",
          "placeholder": "ex: 100.00",
          "required": true,
          "type": "text",
          "validation": "decimal"
        },
        {
          "label": "Periodo Apuracao",
          "placeholder": "AAAA-MM-DD (opcional)",
          "required": false,
          "type": "text",
          "validation": "date"
        }
      ],
      "args": [
        { "flag": "-c", "field": "CPF/CNPJ" },
        { "flag": "-r", "field": "Codigo Receita" },
        { "flag": "-d", "field": "Data Consolidacao" },
        { "flag": "-v", "field": "Valor Principal (R$)" },
        { "flag": "--periodo", "field": "Periodo Apuracao", "optional": true }
      ],
      "output": {
        "type": "file",
        "format": "pdf",
        "subdir": "pdfs",
        "flag": "-o",
        "flagMode": "dir",
        "autoOpen": true
      },
      "response": {
        "successMessage": "pdfPath",
        "clipboard": "codigoBarras",
        "displayFields": [
          { "key": "calculo.valorPrincipal", "label": "Valor Principal", "format": "currency" },
          { "key": "calculo.valorMulta", "label": "Multa", "format": "currency" },
          { "key": "calculo.valorJuros", "label": "Juros", "format": "currency" },
          { "key": "calculo.valorTotal", "label": "Valor Total", "format": "currency" },
          { "key": "codigoBarras", "label": "Codigo de Barras" }
        ]
      }
    }
  ]
}
```

### Example 2: Parcelamentos (select fields, multiple operations)

```json
{
  "service": {
    "id": "parcelamentos",
    "name": "Parcelamentos",
    "description": "Parcelamentos de debitos",
    "prefix": "parc",
    "category": "SERPRO"
  },
  "operations": [
    {
      "id": "consultar-pedidos",
      "command": "parc-consultar-pedidos",
      "name": "Consultar Pedidos",
      "description": "Consultar pedidos de parcelamento",
      "fields": [
        {
          "label": "CNPJ",
          "placeholder": "ex: 12345678000199",
          "required": true,
          "type": "text",
          "validation": "cnpj"
        },
        {
          "label": "Sistema",
          "required": true,
          "type": "select",
          "options": ["PARCSN", "PARCSN-ESP", "PERTSN", "RELPSN"]
        }
      ],
      "args": [
        { "flag": "-c", "field": "CNPJ" },
        { "flag": "--sistema", "field": "Sistema" }
      ],
      "output": { "type": "none" },
      "response": {
        "displayFields": [
          { "key": "sistema", "label": "Sistema" },
          { "key": "dados", "label": "Dados", "format": "json" }
        ]
      }
    }
  ]
}
```

### Example 3: SITFIS (statusBranches, fullpath output)

```json
{
  "service": {
    "id": "sitfis",
    "name": "SITFIS",
    "description": "Relatorio de situacao fiscal",
    "prefix": "sitfis",
    "category": "SERPRO"
  },
  "operations": [
    {
      "id": "obter",
      "command": "sitfis-obter",
      "name": "Obter Relatorio",
      "description": "Obter relatorio por protocolo",
      "fields": [
        {
          "label": "CPF/CNPJ",
          "placeholder": "ex: 12345678901",
          "required": true,
          "type": "text",
          "validation": "cpf_cnpj"
        },
        {
          "label": "Protocolo",
          "placeholder": "protocolo da solicitacao",
          "required": true,
          "type": "text"
        }
      ],
      "args": [
        { "flag": "-c", "field": "CPF/CNPJ" },
        { "flag": "--protocolo", "field": "Protocolo" }
      ],
      "output": {
        "type": "file",
        "format": "pdf",
        "subdir": "pdfs",
        "flag": "--output",
        "flagMode": "fullpath",
        "filenamePattern": "sitfis-{CPF/CNPJ:digits}.pdf",
        "autoOpen": true
      },
      "response": {
        "statusBranches": [
          {
            "field": "status",
            "value": "PROCESSANDO",
            "displayFields": [
              { "key": "status", "label": "Status" },
              { "key": "tempoEspera", "label": "Tempo Espera (ms)", "format": "number" }
            ]
          },
          {
            "field": "status",
            "value": "CONCLUIDO",
            "displayFields": [
              { "key": "status", "label": "Status" },
              { "key": "outputPath", "label": "Arquivo" }
            ]
          },
          {
            "field": "status",
            "value": "ERRO",
            "displayFields": [
              { "key": "error", "label": "Erro" }
            ]
          }
        ]
      }
    }
  ]
}
```

## Output

Return ONLY the complete, valid JSON manifest. No markdown fences, no explanation — just the raw JSON ready to be saved as `services/<id>.service.json`.
