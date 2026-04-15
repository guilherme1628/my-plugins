# Template Filler Assets

This directory contains example files and configurations for Template Filler.

## Files

### example_data.json
Example data structure showing all common fields used in document generation.

**Use this as a reference when**:
- Building data for document generation
- Understanding field naming conventions
- Creating test data for templates

**Field naming conventions**:
- `contratante_*` - Client/contractor company fields
- `contratada_*` - Service provider fields
- `valor_*` - Monetary values
- `valor_*_extenso` - Currency in words (auto-generated)
- `data_*` - Date fields
- `endereco_*` - Address components

## Adding Custom Assets

You can add to this directory:

- **Template examples**: Sample `.docx` templates
- **Field configurations**: JSON schemas for specific templates
- **Contractor data samples**: Example contractor memory exports
- **Batch processing configs**: Configuration files for batch document generation

All assets are copied or referenced during skill usage, not loaded into context.
