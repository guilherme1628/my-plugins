# Template_Filler Workflow Guide

Complete workflow for generating documents using Template_Filler.

## Overview

Template_Filler follows a 4-step workflow:

1. **List Templates** - Find available templates
2. **Parse Template** - Extract required fields
3. **Collect Data** - Gather information (manual or via API)
4. **Generate Document** - Create final document

## Workflow Diagrams

### Basic Workflow

```
┌─────────────────┐
│ List Templates  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Select Template │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse Template  │ → Extract fields: {{field1}}, {{field2}}, etc.
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Collect Data    │ → Get values for each field
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ Generate Document│ → Replace {{fields}} with actual data
└──────────────────┘
         │
         ▼
┌─────────────────┐
│ Final Document  │ → Saved to Google Drive
└─────────────────┘
```

### Enhanced Workflow (with ReceitaWS & Contractor Memory)

```
┌──────────────────┐
│ List Templates   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Select Template  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Parse Template   │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│ Check Contractor Memory  │ ─┐
└─────────┬────────────────┘  │
          │ Not found         │ Found
          ▼                   │
┌──────────────────────┐     │
│ Lookup CNPJ          │     │
│ (ReceitaWS API)      │     │
└─────────┬────────────┘     │
          │                   │
          ▼                   │
┌──────────────────────┐     │
│ Save to Contractor   │     │
│ Memory               │     │
└─────────┬────────────┘     │
          │◄─────────────────┘
          ▼
┌──────────────────────┐
│ Collect Remaining    │
│ Data (values, dates) │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Generate Document    │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Update Contractor    │
│ Usage Count         │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│ Final Document       │
└──────────────────────┘
```

## Detailed Workflows

### 1. First-Time Contract Generation

**Scenario**: Creating a contract for a new client (CNPJ: 12.345.678/0001-90)

**Step-by-step**:

```bash
# 1. List available templates
python3 scripts/list_templates.py

# Output:
# Found 3 template(s):
# • TEMPLATE_Contrato_Prestacao_Servicos.gdoc
#   ID: 1abc...
#   Type: Google Docs
#   Modified: 2025-01-10

# 2. Parse the contract template
python3 scripts/parse_template.py 1abc...

# Output (JSON):
# {
#   "template_id": "1abc...",
#   "fields": [
#     {"name": "contratante_razaoSocial", "type": "text", "required": true},
#     {"name": "contratante_cnpj", "type": "cnpj", "required": true},
#     {"name": "valor_total", "type": "currency", "required": true},
#     {"name": "valor_total_extenso", "type": "currency_text", "required": true},
#     {"name": "data_inicio", "type": "date", "required": true}
#   ],
#   "total_fields": 25
# }

# 3. Lookup company data via CNPJ
python3 scripts/lookup_cnpj.py 12345678000190

# Output (JSON):
# {
#   "success": true,
#   "company_info": {
#     "nome": "EMPRESA EXEMPLO LTDA",
#     "cnpj": "12.345.678/0001-90",
#     "cidade": "São Paulo"
#   },
#   "template_fields": {
#     "contratante_razaoSocial": "EMPRESA EXEMPLO LTDA",
#     "contratante_cnpj": "12.345.678/0001-90",
#     "contratante_endereco_logradouro": "Rua Exemplo, 123",
#     ...
#   },
#   "fields_extracted": 15
# }

# 4. Build complete data JSON (combining CNPJ data + manual fields)
# Create data.json:
{
  "template_id": "1abc...",
  "template_name": "TEMPLATE_Contrato_Prestacao_Servicos",
  "contratante_razaoSocial": "EMPRESA EXEMPLO LTDA",
  "contratante_cnpj": "12.345.678/0001-90",
  "contratante_endereco_logradouro": "Rua Exemplo, 123",
  "contratante_cidade": "São Paulo",
  "valor_total": "R$ 10.000,00",
  "valor_total_extenso": "dez mil reais",
  "data_inicio": "01/02/2025",
  "data_vencimento": "31/12/2025"
}

# 5. Generate document
python3 scripts/generate_document.py 1abc... data.json "Contrato_EMPRESA_EXEMPLO"

# Output (JSON):
# {
#   "success": true,
#   "document_info": {
#     "id": "doc_456...",
#     "name": "Contrato_EMPRESA_EXEMPLO_2025-01-13",
#     "url": "https://docs.google.com/document/d/doc_456.../edit"
#   }
# }
```

### 2. Repeat Contract for Known Client

**Scenario**: Creating another contract for the same client

```bash
# 1. Search contractor memory
python3 scripts/manage_contractors.py search "EMPRESA EXEMPLO"

# Output:
# {
#   "success": true,
#   "contractors": [
#     {
#       "id": "12345678000190",
#       "razao_social": "EMPRESA EXEMPLO LTDA",
#       "usage_count": 1
#     }
#   ]
# }

# 2. Get contractor details with template fields
python3 scripts/manage_contractors.py get 12345678000190

# Output includes:
# {
#   "template_fields": {
#     "contratante": {
#       "contratante_razaoSocial": "EMPRESA EXEMPLO LTDA",
#       "contratante_cnpj": "12.345.678/0001-90",
#       ...
#     }
#   }
# }

# 3. Build data.json with contractor fields + new contract data
{
  "contratante_razaoSocial": "EMPRESA EXEMPLO LTDA",  # from contractor memory
  "contratante_cnpj": "12.345.678/0001-90",          # from contractor memory
  "valor_total": "R$ 15.000,00",                     # new value
  "data_inicio": "01/03/2025"                        # new date
}

# 4. Generate document
python3 scripts/generate_document.py 1abc... data.json

# Contractor usage_count automatically increments to 2
```

### 3. Batch Document Generation

**Scenario**: Generate 10 invoices for different clients

```python
#!/usr/bin/env python3
# batch_generate.py

import json
import subprocess

template_id = "1xyz..."  # Invoice template

clients = [
    {"id": "11111111000190", "valor": "R$ 1.000,00"},
    {"id": "22222222000190", "valor": "R$ 2.000,00"},
    # ... 8 more
]

for client in clients:
    # Get contractor data
    result = subprocess.run(
        ["python3", "scripts/manage_contractors.py", "get", client["id"]],
        capture_output=True, text=True
    )
    contractor_data = json.loads(result.stdout)

    # Build data
    data = {
        **contractor_data["template_fields"]["contratante"],
        "valor": client["valor"],
        "data_emissao": "13/01/2025"
    }

    # Generate document
    subprocess.run([
        "python3", "scripts/generate_document.py",
        template_id,
        json.dumps(data)
    ])
```

## Integration Patterns

### Pattern 1: AI-Driven Conversational Collection

Claude asks questions and builds data incrementally:

```
User: "I need a contract for Petrobras"

Claude:
[calls manage_contractors.py search "Petrobras"]
→ Found existing contractor

[calls manage_contractors.py get 33000167000101]
→ Gets all company data

"I found Petrobras in our memory:
 - Razão Social: PETROLEO BRASILEIRO S A PETROBRAS
 - CNPJ: 33.000.167/0001-01
 - Address: AV REPUBLICA DO CHILE, 65, CENTRO

 I just need a few more details:
 - What's the contract value?"

User: "R$ 50.000,00"

Claude: "And the start date?"

User: "01/02/2025"

Claude:
[builds complete data object]
[calls generate_document.py with full data]

"✅ Contract generated successfully!
 URL: https://docs.google.com/document/d/..."
```

### Pattern 2: Direct API Integration

External system calls scripts directly:

```bash
curl -X POST https://your-api.com/generate \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "1abc...",
    "cnpj": "12345678000190",
    "additional_data": {
      "valor": "R$ 10.000,00",
      "data_inicio": "01/02/2025"
    }
  }'

# API backend runs:
# 1. lookup_cnpj.py 12345678000190
# 2. Merges CNPJ data with additional_data
# 3. generate_document.py with complete data
# 4. Returns document URL
```

### Pattern 3: Scheduled Batch Processing

Cron job generates monthly invoices:

```bash
# crontab entry
0 9 1 * * /path/to/generate_monthly_invoices.sh

# generate_monthly_invoices.sh
#!/bin/bash
for client_id in $(cat client_ids.txt); do
    python3 scripts/generate_document.py \
        $INVOICE_TEMPLATE_ID \
        "$(python3 scripts/manage_contractors.py get $client_id | jq '.template_fields.contratante + {valor: "R$ 1.000,00", data: "'$(date +%d/%m/%Y)'"}')"
done
```

## Error Handling

### Common Issues

1. **Missing Required Fields**
   - Check template parsing output
   - Ensure all required fields have data
   - Use optional fields (`{{field?}}`) when appropriate

2. **CNPJ Not Found**
   - ReceitaWS may be rate-limited
   - CNPJ might be invalid
   - Fallback to manual entry

3. **Document Generation Fails**
   - Check Google Drive permissions
   - Verify template exists and is accessible
   - Check credentials are valid

4. **Format Validation Errors**
   - Ensure CNPJ has 14 digits
   - Check date format matches expected
   - Verify currency values are properly formatted

## Best Practices

1. **Always use contractor memory for repeat clients**
   - Saves API calls to ReceitaWS
   - Ensures data consistency
   - Tracks usage frequency

2. **Validate data before generation**
   - Parse template first to see required fields
   - Check all required fields have values
   - Validate format (CNPJ, dates, currency)

3. **Use descriptive custom names**
   - Makes documents easier to find
   - Include client name and date
   - Follow consistent naming pattern

4. **Handle errors gracefully**
   - Check script exit codes
   - Parse error messages from JSON output
   - Implement retry logic for transient failures

5. **Monitor API quotas**
   - ReceitaWS has rate limits
   - Google Drive API has daily quotas
   - Cache results when possible

## Performance Tips

1. **Batch operations**
   - Generate multiple documents in parallel
   - Reuse GoogleDriveManager instance
   - Cache template parsing results

2. **Contractor memory**
   - Reduces ReceitaWS API calls
   - Faster data retrieval
   - Better for frequent clients

3. **Minimize API calls**
   - Parse template once, generate many documents
   - Use contractor memory instead of CNPJ lookup
   - Cache frequently used data
