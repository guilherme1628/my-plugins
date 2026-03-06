# Field Types Reference

This document describes the supported field types in Template_Filler templates.

## Overview

Templates use placeholders in the format `{{field_name}}` which get replaced with actual data during document generation.

## Supported Field Types

### 1. Text (text)

Simple text fields for names, descriptions, etc.

**Format**: `{{field_name}}`

**Examples**:
- `{{nome_cliente}}` → "ACME Corp"
- `{{descricao_servico}}` → "Consultoria de TI"
- `{{endereco}}` → "Rua Exemplo, 123"

**Validation**: Non-empty string

---

### 2. Date (date)

Date fields with configurable formatting.

**Format**: `{{data_campo}}`
**Format spec**: `{{data_campo:DD/MM/YYYY}}`

**Default format**: DD/MM/YYYY

**Examples**:
- `{{data_contrato}}` → "15/01/2024"
- `{{data_vencimento}}` → "30/06/2024"
- `{{data_inicio:YYYY-MM-DD}}` → "2024-01-15"

**Validation**: Valid date string in specified format

---

### 3. Currency (currency)

Monetary values with proper formatting.

**Format**: `{{valor_campo}}`
**Format spec**: `{{valor_campo:BRL}}`

**Default format**: R$ #.###,##

**Examples**:
- `{{valor_contrato}}` → "R$ 10.000,00"
- `{{valor_mensal}}` → "R$ 1.500,50"
- `{{taxa}}` → "R$ 250,00"

**Validation**: Positive number with proper currency formatting

---

### 4. Currency Text (currency_text)

Monetary values written out in full (por extenso).

**Format**: `{{valor_campo_extenso}}`
**Linked to**: Currency field with same base name

**Examples**:
- `{{valor_contrato_extenso}}` → "dez mil reais"
- `{{valor_mensal_extenso}}` → "um mil e quinhentos reais e cinquenta centavos"

**Note**: Automatically generated from corresponding currency field using `num2words` library.

---

### 5. CNPJ (cnpj)

Brazilian company tax ID with formatting.

**Format**: `{{cnpj_campo}}`

**Output format**: ##.###.###/####-##

**Examples**:
- `{{cnpj_contratante}}` → "12.345.678/0001-90"
- `{{cnpj}}` → "33.000.167/0001-01"

**Validation**: Valid CNPJ with 14 digits, properly formatted

---

### 6. CPF (cpf)

Brazilian individual tax ID with formatting.

**Format**: `{{cpf_campo}}`

**Output format**: ###.###.###-##

**Examples**:
- `{{cpf_responsavel}}` → "123.456.789-00"
- `{{cpf}}` → "987.654.321-99"

**Validation**: Valid CPF with 11 digits, properly formatted

---

### 7. CEP (cep)

Brazilian postal code with formatting.

**Format**: `{{cep_campo}}`

**Output format**: #####-###

**Examples**:
- `{{cep}}` → "01310-100"
- `{{cep_empresa}}` → "20040-020"

**Validation**: Valid CEP with 8 digits, properly formatted

---

### 8. Phone (phone)

Brazilian phone number with formatting.

**Format**: `{{telefone_campo}}`

**Output formats**:
- Landline: (##) ####-####
- Mobile: (##) #####-####

**Examples**:
- `{{telefone}}` → "(11) 3456-7890"
- `{{celular}}` → "(21) 98765-4321"

**Validation**: Valid Brazilian phone number

---

### 9. Email (email)

Email address validation.

**Format**: `{{email_campo}}`

**Examples**:
- `{{email_contato}}` → "contato@empresa.com.br"
- `{{email}}` → "joao.silva@example.com"

**Validation**: Valid email format

---

## Optional Fields

Fields can be marked as optional by adding `?` at the end:

**Format**: `{{campo_opcional?}}`

**Behavior**:
- If data is provided, it's inserted normally
- If no data provided, the placeholder is removed
- No validation error for missing optional fields

**Examples**:
- `{{observacoes?}}` - Optional observations field
- `{{complemento?}}` - Optional address complement
- `{{nome_fantasia?}}` - Optional company trade name

---

## Field Naming Conventions

### Common Prefixes

- `contratante_*` - Contractor/client company data
- `contratada_*` - Contracted/service provider data
- `responsavel_*` - Responsible person data
- `endereco_*` - Address-related fields
- `data_*` - Date fields
- `valor_*` - Monetary value fields

### Examples

```
{{contratante_razaoSocial}}
{{contratante_cnpj}}
{{contratante_endereco_logradouro}}
{{contratante_endereco_numero}}
{{contratante_endereco_cidade}}
{{contratante_endereco_uf}}

{{valor_total}}
{{valor_total_extenso}}
{{valor_parcela}}

{{data_inicio}}
{{data_vencimento}}
{{data_assinatura}}

{{responsavel_nome}}
{{responsavel_cpf}}
{{responsavel_email}}
```

---

## Auto-detection

The Template Parser automatically detects field types based on field names:

- Fields containing `cnpj` → CNPJ type
- Fields containing `cpf` → CPF type
- Fields containing `cep` → CEP type
- Fields containing `telefone` or `celular` → Phone type
- Fields containing `email` → Email type
- Fields containing `data_` or `_data` → Date type
- Fields containing `valor` → Currency type
- Fields ending with `_extenso` → Currency Text type
- Everything else → Text type

This can be overridden by specifying format specs in the template.

---

## Custom Formatting

Use format specifications to override auto-detection:

**Syntax**: `{{field_name:format_spec}}`

**Examples**:
- `{{data:YYYY-MM-DD}}` - ISO date format
- `{{valor:USD}}` - US Dollar currency
- `{{numero:###.###-#}}` - Custom number format

---

## Integration with ReceitaWS

When using `lookup_cnpj` tool, the following fields are automatically populated:

**Company Data**:
- `razaoSocial` / `razao_social`
- `cnpj`
- `nomeFantasia` / `nome_fantasia`

**Address Data**:
- `logradouro`
- `numero`
- `bairro` / `complemento`
- `cidade` / `municipio`
- `uf`
- `cep`

**Contact Data**:
- `telefone`
- `email`

These can be used with any prefix (contratante_, contratada_, etc.).
