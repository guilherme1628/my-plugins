#!/usr/bin/env python3
"""
Generate Document Script
Generates a final document from a template and collected data.
"""

import os
import sys
import json
from pathlib import Path

# Add plugin root to path (scripts/ -> skill/ -> skills/ -> plugin root)
plugin_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(plugin_root))

from template_filler.core.google_drive_manager import GoogleDriveManager
from template_filler.core.document_generator import DocumentGenerator
from template_filler.core.data_collector import DataCollector, CollectionResult


def main(template_id: str = None, data_source: str = None, custom_name: str = None):
    """
    Generate document from template and data.

    Args:
        template_id: Google Drive template ID
        data_source: Either a file path or JSON string with field data
        custom_name: Optional custom name for the document
    """
    if not template_id or not data_source:
        if len(sys.argv) < 3:
            print("Usage: generate_document.py <template_id> <data_source> [custom_name]")
            print()
            print("data_source can be:")
            print("  - Path to a JSON file with collected data")
            print("  - JSON string with field data")
            return 1
        template_id = sys.argv[1]
        data_source = sys.argv[2]
        custom_name = sys.argv[3] if len(sys.argv) > 3 else None

    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path or not os.path.exists(credentials_path):
        print("ERROR: GOOGLE_APPLICATION_CREDENTIALS not configured")
        return 1

    try:
        root_folder_id = os.getenv('TEMPLATE_FILLER_DRIVE_FOLDER_ID')
        if root_folder_id == 'your_google_drive_folder_id':
            root_folder_id = None

        manager = GoogleDriveManager(credentials_path, root_folder_id)
        generator = DocumentGenerator(manager)
        collector = DataCollector()

        # Determine if data_source is file or JSON string
        data_path = Path(data_source)
        if data_path.exists():
            # Load from file
            collection_result = collector.load_from_file(data_path)
        else:
            # Try to parse as JSON
            try:
                field_data = json.loads(data_source)
                # Create a CollectionResult from the data
                collection_result = CollectionResult(
                    template_id=template_id,
                    template_name=field_data.get("template_name", "Unknown"),
                    data=field_data,
                    collected_at=""
                )
            except json.JSONDecodeError:
                print(f"ERROR: data_source is neither a file nor valid JSON: {data_source}")
                return 1

        # Generate document
        result = generator.generate_document(
            template_id=template_id,
            collection_result=collection_result,
            custom_name=custom_name
        )

        # Output result as JSON
        output = {
            "success": True,
            "document_info": {
                "id": result.document_id,
                "name": result.document_name,
                "url": result.document_url,
                "preview_url": result.document_url.replace('/edit', '/preview') if result.document_url else None
            },
            "template_info": {
                "id": template_id,
                "name": result.template_name
            },
            "generation_details": {
                "generated_at": result.generated_at,
                "custom_name_used": custom_name is not None
            }
        }

        print(json.dumps(output, indent=2, ensure_ascii=False))
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
