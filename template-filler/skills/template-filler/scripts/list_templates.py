#!/usr/bin/env python3
"""
List Templates Script
Lists all available Google Docs templates from the Templates/ folder.
"""

import os
import sys
from pathlib import Path

# Add plugin root to path (scripts/ -> skill/ -> skills/ -> plugin root)
plugin_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(plugin_root))

from template_filler.core.google_drive_manager import GoogleDriveManager


def main():
    """List all available templates."""
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path or not os.path.exists(credentials_path):
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS not configured")
        print("Set it in your environment or .env file")
        return 1

    try:
        root_folder_id = os.getenv('TEMPLATE_FILLER_DRIVE_FOLDER_ID')
        if root_folder_id == 'your_google_drive_folder_id':
            root_folder_id = None

        manager = GoogleDriveManager(credentials_path, root_folder_id)
        templates = manager.list_templates()

        if not templates:
            print("No templates found in Templates/ folder")
            return 0

        print(f"Found {len(templates)} template(s):")
        print()

        for template in templates:
            print(f"• {template['name']}")
            print(f"  ID: {template['id']}")
            print(f"  Type: {template['type']}")
            print(f"  Modified: {template['modified'][:10]}")
            print()

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
