---
name: legalizacao-ecab
description: Create company legalizations (ABERTURA, ALTERACAO, BAIXA) in the ECAB system. Use when user mentions legalizacao, company opening, alteration, closure, or Brazilian company registration processes and wants to use the ECAB system (not Trello).
---

# Legalizacao ECAB Workflow

Create company legalizations in the ECAB system via its Supabase edge function.

## Types

- **ABERTURA** — New company (no `cliente_id` needed)
- **ALTERACAO** — Modify existing company (requires `cliente_id`)
- **BAIXA** — Close existing company (requires `cliente_id`)

## Quick Start (Agent Workflow)

All commands are non-interactive. Run from `<skill-dir>/scripts/`.

### 1. Search for client (ALTERACAO/BAIXA)

```bash
node index.js search "MerchX"
```

Returns JSON:
```json
[{ "id": 504, "razao_social": "MERCHX DESIGN & COMERCIO LTDA", "nome_fantasia": "MERCHX", "documento": "52299040000180" }]
```

The `id` is the `clienteId` needed below.

### 2. Create legalizacao

Pass the data as a JSON argument — no interactive prompts, no draft step:

**ALTERACAO:**
```bash
node index.js create ALTERACAO '{"basic":{"companyName":"MerchX","clienteId":"504","priority":"normal"},"alteration":{"type":"1","details":"Alterar endereco para Rua X, 123, Bairro, Cidade-UF, CEP: XX.XXX-XXX"}}'
```

**BAIXA:**
```bash
node index.js create BAIXA '{"basic":{"companyName":"Company","clienteId":"80","priority":"normal"},"closure":{"reason":"Encerramento de atividades"}}'
```

**ABERTURA:**
```bash
node index.js create ABERTURA '{"basic":{"companyName":"New Corp","priority":"normal"},"company":{"activities":"Comercio","socialCapital":"10000"},"partners":[{"name":"John","participation":"100"}]}'
```

Returns JSON with the created legalizacao:
```json
{
  "id": "uuid",
  "nome_empresa": "MerchX",
  "prioridade": "normal",
  "data_vencimento": null,
  "checklist_items": 4
}
```

## JSON Schemas

### ALTERACAO

```json
{
  "basic": {
    "companyName": "Company Name",
    "clienteId": "504",
    "priority": "normal",
    "deadline": "15/03/2026"
  },
  "alteration": {
    "type": "1,7",
    "details": "Description of changes",
    "hasContratoSocial": "s",
    "hasDocsSocios": "s",
    "observations": "Optional notes"
  }
}
```

Alteration types: `1` endereco, `2` objeto social, `3` capital social, `4` inclusao socio, `5` exclusao socio, `6` transferencia cotas, `7` nome empresarial, `8` outro.

### BAIXA

```json
{
  "basic": {
    "companyName": "Company Name",
    "clienteId": "80",
    "priority": "normal"
  },
  "closure": {
    "reason": "Encerramento de atividades",
    "hasDebts": "n",
    "hasCertidoes": "s",
    "hasContratoSocial": "s",
    "lastBalanceDate": "31/12/2025",
    "observations": ""
  }
}
```

### ABERTURA

```json
{
  "basic": {
    "companyName": "Company Name",
    "priority": "normal",
    "deadline": ""
  },
  "company": {
    "activities": "Comercio de roupas",
    "iptu": "12345",
    "socialCapital": "50000"
  },
  "partners": [
    {
      "name": "Partner Name",
      "birthCity": "Sao Paulo",
      "birthState": "SP",
      "maritalStatus": "Solteiro",
      "marriageRegime": "",
      "profession": "Empresario",
      "participation": "50",
      "documents": { "rg": "12345", "cpf": "123.456.789-00", "residenceProof": "Conta de luz" }
    }
  ]
}
```

## Other Commands

```bash
node index.js requirements ALTERACAO   # Show required fields and alteration types
node index.js list                     # List saved drafts
node index.js clean                    # Clean all drafts
```

## Batch Operations

For multiple legalizacoes, run `create` for each:

```bash
node index.js search "Sylvia"    # get id
node index.js search "Kiji"      # get id
node index.js search "MerchX"    # get id

node index.js create ALTERACAO '{"basic":{"companyName":"Sylvia","clienteId":"857","priority":"normal"},"alteration":{"type":"7","details":"Alterar razao social para Sylvia Almeida Gestao LTDA"}}'
node index.js create ALTERACAO '{"basic":{"companyName":"Kiji Cottons","clienteId":"80","priority":"normal"},"alteration":{"type":"1","details":"Alterar endereco para Rua X, 123"}}'
node index.js create ALTERACAO '{"basic":{"companyName":"MerchX","clienteId":"504","priority":"normal"},"alteration":{"type":"1","details":"Alterar endereco para Rua Y, 456"}}'
```

## Interactive Mode (Human Use)

Humans can still use the interactive `collect` flow:

```bash
node index.js collect ABERTURA    # Interactive prompts
node index.js collect ALTERACAO   # Interactive prompts (asks for cliente_id)
node index.js collect BAIXA       # Interactive prompts
node index.js create ABERTURA     # Creates from saved draft
```

## Direct API Access

For full control, use the API directly:

```bash
# Search clients
curl -s -H "X-API-Key: <key>" "https://<url>/functions/v1/create-legalizacao?q=MerchX"

# Create legalizacao
curl -s -X POST -H "Content-Type: application/json" -H "X-API-Key: <key>" \
  "https://<url>/functions/v1/create-legalizacao" \
  -d '{"tipo":"alteracao","nome_empresa":"MerchX","prioridade":"normal","cliente_id":504,"notas":"..."}'
```

API fields: `tipo` (abertura/alteracao/baixa, lowercase), `nome_empresa`, `prioridade` (default: normal), `cliente_id` (required for alteracao/baixa), `data_vencimento` (YYYY-MM-DD), `notas`, `responsavel_id`.

## Error Recovery

| Error | Fix |
|-------|-----|
| 400 `"cliente_id is required"` | Search client first, pass `clienteId` in JSON |
| 400 `"q must be at least 2 characters"` | Use 2+ char search query |
| 401 | Check `LEGALIZACAO_API_KEY` in `scripts/.env` |
| `"basic" object required` | JSON must have `{"basic":{"companyName":"..."},...}` |

## Prerequisites

Credentials in `scripts/.env` (loaded automatically):
```
ECAB_SUPABASE_URL=https://<project>.supabase.co
LEGALIZACAO_API_KEY=<key>
```
