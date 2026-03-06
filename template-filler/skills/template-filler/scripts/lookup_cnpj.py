#!/usr/bin/env python3
"""
Lookup CNPJ Script
Fetches company data from ReceitaWS API using CNPJ.
"""

import os
import sys
import json
from pathlib import Path

# Add plugin root to path (scripts/ -> skill/ -> skills/ -> plugin root)
plugin_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(plugin_root))

from template_filler.integrations.receitaws import ReceitaWSClient, ReceitaWSError


def main(cnpj: str = None):
    """Lookup company data by CNPJ."""
    if not cnpj:
        if len(sys.argv) < 2:
            print("Usage: lookup_cnpj.py <cnpj>")
            return 1
        cnpj = sys.argv[1]

    try:
        client = ReceitaWSClient()

        # Get company data
        company_data = client.get_company_data(cnpj)
        template_fields = client.extract_template_fields(company_data)

        # Output as JSON
        result = {
            "success": True,
            "cnpj_consulted": cnpj,
            "company_info": {
                "nome": company_data.get("nome", ""),
                "fantasia": company_data.get("fantasia", ""),
                "cnpj": company_data.get("cnpj", ""),
                "situacao": company_data.get("situacao", ""),
                "atividade_principal": company_data.get("atividade_principal", [{}])[0].get("text", "") if company_data.get("atividade_principal") else ""
            },
            "address_info": {
                "logradouro": company_data.get("logradouro", ""),
                "numero": company_data.get("numero", ""),
                "bairro": company_data.get("bairro", ""),
                "municipio": company_data.get("municipio", ""),
                "uf": company_data.get("uf", ""),
                "cep": company_data.get("cep", "")
            },
            "template_fields": template_fields,
            "fields_extracted": len(template_fields)
        }

        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    except ReceitaWSError as e:
        error_output = {
            "success": False,
            "error": f"ReceitaWS Error: {str(e)}"
        }
        print(json.dumps(error_output, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1
    except Exception as e:
        error_output = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_output, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
