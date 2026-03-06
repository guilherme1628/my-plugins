---
name: template-filler
description: Automate professional document generation from Google Docs templates with placeholder replacement, CNPJ lookup integration, and contractor memory. This skill should be used when users need to generate contracts, invoices, proposals, or any document from templates while maintaining formatting and managing client data efficiently.
---

# Template Filler Skill

Comprehensive toolkit for automated document generation using Google Docs templates with intelligent data collection, Brazilian company data integration (CNPJ lookup), and persistent contractor memory.

## Overview

Template Filler enables automated creation of professional documents (contracts, invoices, proposals) from Google Docs templates by replacing `{{placeholder}}` fields with actual data while preserving 100% of the original formatting. It integrates with ReceitaWS for automatic Brazilian company data lookup and maintains a persistent memory of frequently used contractors to streamline repeat document generation.

## When to Use This Skill

Use template-filler when users ask to:
- Generate documents from templates (contracts, invoices, proposals)
- Create multiple documents with similar structure
- Fill Google Docs templates with data
- Automate contract or invoice generation
- Manage client/contractor information for reuse
- Look up Brazilian company data by CNPJ
- Create professional documents while maintaining formatting

## Core Capabilities

### 1. Template Management
- List all available Google Docs templates from Google Drive
- Parse templates to extract field placeholders (`{{field_name}}`)
- Auto-detect field types (text, date, currency, CNPJ, email, etc.)
- Validate template structure and required fields

### 2. Data Collection
- Intelligent field type detection based on naming conventions
- Support for text, dates, currency, CNPJ, CPF, CEP, phone, email fields
- Optional fields marked with `?` syntax
- Automatic currency-to-text conversion (e.g., "R$ 10.000,00" -> "dez mil reais")

### 3. Brazilian Company Integration (ReceitaWS)
- Automatic CNPJ lookup via ReceitaWS public API
- Retrieves company name, address, contact information
- Extracts 15+ fields ready for template population
- No API key required for ReceitaWS integration

### 4. Contractor Memory
- Persistent storage of frequently used clients/contractors
- Search contractors by name, CNPJ, city, or tags
- Automatic usage tracking (how many times used)
- Reuse saved data for faster document generation
- Reduces redundant CNPJ lookups

### 5. Document Generation
- Preserve 100% of original template formatting
- Replace all `{{placeholder}}` fields with actual data
- Auto-organize documents by type, year, and month
- Generate descriptive filenames automatically
- Store in Google Drive with proper structure

## Workflow Decision Tree

```
START: User wants to generate a document
|
+- Has CNPJ? -----------------+
|                              |
NO                            YES
|                              |
+- First time client? --+     +- Check contractor memory
|                        |     |
YES                     NO     +- Found? ----------+
|                        |     |                    |
+- Manual data entry    |    YES                  NO
|  * Parse template     |     |                    |
|  * Collect all fields |     +- Reuse saved       +- Lookup CNPJ
|  * Generate document  |     |   contractor data  |  (ReceitaWS)
|                        |     |                    |
+- Save to memory? -----+---->+- Ask only for     +- Save to memory
                        |     |   missing fields   |
                        |     |   (value, dates)   |
                        |     |                    |
                        +---->+- Generate doc <----+
                              |
                              +- Update usage count
```

## Available Scripts

All scripts are in `$CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/` and return JSON output.

### list_templates.py
**Purpose**: List all available Google Docs templates

**Usage**:
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/list_templates.py
```

**Output**:
```json
[
  {
    "id": "1abc123...",
    "name": "TEMPLATE_Contrato_Prestacao_Servicos.gdoc",
    "type": "Google Docs",
    "modified": "2025-01-10T15:30:00Z"
  }
]
```

### parse_template.py
**Purpose**: Extract field placeholders from a template

**Usage**:
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/parse_template.py <template_id>
```

**Output**:
```json
{
  "fields": [
    {"name": "contratante_razaoSocial", "type": "text", "required": true},
    {"name": "valor_total", "type": "currency", "required": true}
  ],
  "total_fields": 25
}
```

### lookup_cnpj.py
**Purpose**: Fetch Brazilian company data via CNPJ

**Usage**:
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/lookup_cnpj.py <cnpj>
```

**Output**:
```json
{
  "success": true,
  "company_info": {
    "nome": "EMPRESA EXEMPLO LTDA",
    "cnpj": "12.345.678/0001-90"
  },
  "template_fields": {
    "contratante_razaoSocial": "EMPRESA EXEMPLO LTDA",
    "contratante_cnpj": "12.345.678/0001-90",
    "contratante_endereco_logradouro": "Rua Exemplo, 123"
  }
}
```

### manage_contractors.py
**Purpose**: Manage persistent contractor/client memory

**Actions**: list, search, get

**Usage**:
```bash
# List all
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/manage_contractors.py list

# Search
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/manage_contractors.py search "Petrobras"

# Get with template fields
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/manage_contractors.py get <contractor_id>
```

### generate_document.py
**Purpose**: Generate final document from template and data

**Usage**:
```bash
# From data file
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/generate_document.py <template_id> data.json

# From JSON string
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/generate_document.py <template_id> '{"field1": "value1"}'

# With custom name
python3 $CLAUDE_PLUGIN_ROOT/skills/template-filler/scripts/generate_document.py <template_id> data.json "Contrato_ClienteXYZ"
```

## Usage Examples

### Example 1: First-Time Client with CNPJ

**User**: "I need to create a contract for CNPJ 12.345.678/0001-90"

**Conversation Flow**:
```
Claude: "I'll create a contract for CNPJ 12.345.678/0001-90. Let me look up the company data..."
[calls lookup_cnpj.py]

Claude: "Found: EMPRESA EXEMPLO LTDA
         Address: Rua Exemplo, 123, Sao Paulo

         I just need a few more details:
         - What's the contract value?"

User: "R$ 10.000,00"

Claude: "And the start date?"

User: "01/02/2025"

Claude: [calls generate_document.py]
        "Contract generated successfully!
         Contrato_EMPRESA_EXEMPLO_2025-01-13
         https://docs.google.com/document/d/..."
```

### Example 2: Repeat Client from Memory

**User**: "Generate another contract for Petrobras"

**Conversation Flow**:
```
Claude: "I found Petrobras in our contractor memory (used 5 times):
         Razao Social: PETROLEO BRASILEIRO S A PETROBRAS
         CNPJ: 33.000.167/0001-01
         Address: AV REPUBLICA DO CHILE, 65, CENTRO, RIO DE JANEIRO

         I just need the contract details:
         - Contract value?"

User: "R$ 50.000,00"

Claude: "Start date?"

User: "01/03/2025"

Claude: [generates document]
        "Contract generated! This is the 6th document for Petrobras.
         https://docs.google.com/document/d/..."
```

## Field Types

For comprehensive field type documentation, consult `$CLAUDE_PLUGIN_ROOT/skills/template-filler/references/field_types.md`. Supported types include:

- **Text**: `{{nome_cliente}}`
- **Date**: `{{data_contrato}}` -> "15/01/2024"
- **Currency**: `{{valor_total}}` -> "R$ 10.000,00"
- **Currency Text**: `{{valor_total_extenso}}` -> "dez mil reais"
- **CNPJ**: `{{cnpj}}` -> "12.345.678/0001-90"
- **CPF**, **CEP**, **Phone**, **Email**: Auto-formatted
- **Optional**: `{{observacoes?}}` - Won't error if missing

## Setup Requirements

Requires Google Cloud setup with Service Account. See `$CLAUDE_PLUGIN_ROOT/skills/template-filler/references/google_drive_setup.md` for detailed instructions.

**Quick setup**:
1. Create Service Account in Google Cloud Console
2. Enable Google Drive API & Google Docs API
3. Download credentials JSON
4. Share Google Drive folder with service account
5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
   ```

**Install Python dependencies**:
```bash
pip install -r $CLAUDE_PLUGIN_ROOT/requirements.txt
```

## Best Practices

1. **Always check contractor memory first** before CNPJ lookup
2. **Parse template before collecting data** to know exactly what's needed
3. **Validate data formats** (CNPJ, dates, currency) before generation
4. **Provide document preview links** so users can verify
5. **Track contractor usage** to identify frequent clients
6. **Use descriptive document names** for easy identification

## Error Handling

Common issues and solutions:

- **CNPJ Not Found**: Fallback to manual entry, offer to save for future use
- **Missing Required Fields**: Parse template first to identify all requirements
- **Google Drive Permissions**: Check folder sharing with service account
- **Rate Limiting**: Use contractor memory to reduce API calls

## Resources

### scripts/
Contains executable Python scripts for all operations:
- `list_templates.py` - List available templates
- `parse_template.py` - Extract template fields
- `lookup_cnpj.py` - Brazilian company data lookup
- `manage_contractors.py` - Contractor memory management
- `generate_document.py` - Document generation

Scripts execute without loading into context but can be read for environment adjustments.

### references/
Documentation for in-depth understanding:
- `field_types.md` - Comprehensive field type reference with validation rules
- `google_drive_setup.md` - Step-by-step Google Cloud and Drive configuration
- `workflow_guide.md` - Detailed workflows, integration patterns, batch processing

Load these references when users need detailed information about specific topics.

### assets/
- `example_data.json` - Example data structure showing all common fields
- `README.md` - Guide for adding custom assets
