#!/usr/bin/env python3
"""List .docx templates from the local templates folder.

Default location: ~/Documents/template_filler_data/templates/
Override with TEMPLATE_FILLER_DIR env var (points at the parent data dir).
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def templates_dir() -> Path:
    base = os.getenv("TEMPLATE_FILLER_DIR")
    if base:
        return Path(base).expanduser() / "templates"
    return Path.home() / "Documents" / "template_filler_data" / "templates"


def main() -> int:
    tdir = templates_dir()
    if not tdir.exists():
        print(json.dumps({
            "error": f"templates directory not found: {tdir}",
            "hint": "create it and drop TEMPLATE_*.docx files inside",
        }, indent=2))
        return 1

    templates = []
    for path in sorted(tdir.glob("*.docx")):
        if path.name.startswith("~$"):
            continue
        stat = path.stat()
        name_parts = path.stem.split("_")
        template_type = name_parts[1] if len(name_parts) > 1 else "Unknown"
        templates.append({
            "id": str(path),
            "name": path.name,
            "type": template_type,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "size": stat.st_size,
        })

    print(json.dumps({
        "directory": str(tdir),
        "count": len(templates),
        "templates": templates,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
