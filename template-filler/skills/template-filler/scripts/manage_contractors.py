#!/usr/bin/env python3
"""
Manage Contractors Script
Manages persistent memory of contractors/clients for reuse in documents.
"""

import os
import sys
import json
from pathlib import Path

# Add plugin root to path (scripts/ -> skill/ -> skills/ -> plugin root)
plugin_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(plugin_root))

from template_filler.core.contractor_manager import ContractorManager, Contractor


def main(action: str = None, **kwargs):
    """
    Manage contractors.

    Actions: list, search, get, save, delete, from_cnpj
    """
    if not action:
        if len(sys.argv) < 2:
            print("Usage: manage_contractors.py <action> [options]")
            print("Actions: list, search, get, save, delete")
            return 1
        action = sys.argv[1]

    try:
        manager = ContractorManager()

        if action == "list":
            contractors = manager.list_contractors()
            result = {
                "success": True,
                "action": "list",
                "contractors": [
                    {
                        "id": c.id,
                        "razao_social": c.razao_social,
                        "cnpj": c.cnpj,
                        "cidade": c.cidade,
                        "uf": c.uf,
                        "usage_count": c.usage_count
                    }
                    for c in contractors
                ],
                "total": len(contractors)
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif action == "search":
            query = kwargs.get('query', sys.argv[2] if len(sys.argv) > 2 else "")
            contractors = manager.search_contractors(query)
            result = {
                "success": True,
                "action": "search",
                "query": query,
                "contractors": [
                    {
                        "id": c.id,
                        "razao_social": c.razao_social,
                        "cnpj": c.cnpj,
                        "usage_count": c.usage_count
                    }
                    for c in contractors
                ],
                "total": len(contractors)
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif action == "get":
            contractor_id = kwargs.get('contractor_id', sys.argv[2] if len(sys.argv) > 2 else "")
            contractor = manager.get_contractor(contractor_id)
            if contractor:
                template_fields = contractor.to_template_fields("contratante_")
                result = {
                    "success": True,
                    "action": "get",
                    "contractor": contractor.to_dict(),
                    "template_fields": {
                        "contratante": contractor.to_template_fields("contratante_"),
                        "contratada": contractor.to_template_fields("contratada_"),
                        "generic": contractor.to_template_fields("")
                    }
                }
            else:
                result = {
                    "success": False,
                    "error": f"Contractor {contractor_id} not found"
                }
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            result = {
                "success": False,
                "error": f"Unknown action: {action}"
            }
            print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
            return 1

        return 0

    except Exception as e:
        error_output = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_output, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
