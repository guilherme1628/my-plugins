#!/usr/bin/env python3
"""
Parse Template Script
Extracts and analyzes field placeholders from a Google Docs template.
"""

import os
import sys
import json
from pathlib import Path

# Add plugin root to path (scripts/ -> skill/ -> skills/ -> plugin root)
plugin_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(plugin_root))

from template_filler.core.google_drive_manager import GoogleDriveManager
from template_filler.core.template_parser import TemplateParser


def main(template_id: str = None):
    """Parse template and extract fields."""
    if not template_id:
        if len(sys.argv) < 2:
            print("Usage: parse_template.py <template_id>")
            return 1
        template_id = sys.argv[1]

    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path or not os.path.exists(credentials_path):
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS not configured")
        return 1

    try:
        root_folder_id = os.getenv('TEMPLATE_FILLER_DRIVE_FOLDER_ID')
        if root_folder_id == 'your_google_drive_folder_id':
            root_folder_id = None

        manager = GoogleDriveManager(credentials_path, root_folder_id)
        parser = TemplateParser(manager)

        # Extract fields
        fields = parser.extract_fields(template_id, interactive=False)
        summary = parser.get_template_summary(template_id)

        # Output as JSON
        result = {
            "template_id": template_id,
            "fields": [
                {
                    "name": field.name,
                    "type": field.field_type,
                    "format": field.format_spec or "",
                    "required": not field.optional,
                    "description": field.description or "",
                    "example": field.example or ""
                }
                for field in fields
            ],
            "total_fields": summary['total_fields'],
            "required_fields": summary['required_fields'],
            "optional_fields": summary['optional_fields'],
            "field_types": summary['field_types'],
            "validation": summary['validation']
        }

        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
