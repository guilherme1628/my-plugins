#!/usr/bin/env python3
"""
batch_convert.py - Prepare a work manifest for batch contract conversion.

Scans a directory for PDF/DOCX/DOC files, checks which ones already have
corresponding JSONs in the jsons directory, and outputs a JSON manifest
of files still needing conversion.

Usage:
    python3 batch_convert.py <scan-dir> [--jsons-dir <path>]

Output (stdout): JSON array of objects with "path" and "filename" keys.
Summary (stderr): Total / Already converted / To process counts.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path


def normalize_name(name: str) -> str:
    """
    Normalize a name for fuzzy comparison:
    - Strip file extension
    - Replace underscores, hyphens, dots with spaces
    - Collapse multiple spaces
    - NFKD unicode normalization, strip accents
    - Uppercase
    """
    # Strip extension
    name = Path(name).stem

    # Replace common separators with space
    name = re.sub(r'[_\-\.]+', ' ', name)

    # Unicode NFKD normalization -> strip combining marks (accents)
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))

    # Uppercase and collapse whitespace
    name = name.upper().strip()
    name = re.sub(r'\s+', ' ', name)

    return name


def extract_empresa_names_from_jsons(jsons_dir: Path) -> set[str]:
    """
    Build a set of normalized empresa names from existing JSON filenames.

    JSON filenames follow two patterns:
      1) EMPRESA_NAME|CNPJ|tipo_documento|versao.json
      2) C{id}|EMPRESA_NAME|tipo_documento|versao.json
      3) C{id}|tipo_documento|versao|EMPRESA_NAME.json  (variant)

    We extract the empresa name part and normalize it.
    We also try to read the empresa.nome field from inside the JSON content.
    """
    names = set()

    if not jsons_dir.is_dir():
        return names

    for json_file in jsons_dir.glob('*.json'):
        fname = json_file.stem  # without .json
        parts = fname.split('|')

        # Extract empresa name from filename patterns
        if len(parts) >= 2:
            first_part = parts[0].strip()

            if re.match(r'^C\d+$', first_part):
                # Pattern: C{id}|...
                # The empresa name could be in parts[1] or parts[-1]
                for part in parts[1:]:
                    part = part.strip()
                    if part and part.lower() not in ('null', '', 'contrato social',
                                                      'alteracao contratual',
                                                      'alteração contratual'):
                        # Check if it looks like a version string (e.g. "1a Alteracao")
                        if not re.match(r'^\d+', part) and len(part) > 3:
                            normalized = normalize_name(part)
                            if normalized:
                                names.add(normalized)
            else:
                # Pattern: EMPRESA_NAME|CNPJ|tipo|versao
                normalized = normalize_name(first_part)
                if normalized:
                    names.add(normalized)

        # Also try to read empresa.nome from JSON content
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                empresa = data.get('empresa', {})
                if isinstance(empresa, dict):
                    nome = empresa.get('nome', '')
                    if nome:
                        normalized = normalize_name(nome)
                        if normalized:
                            names.add(normalized)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            pass

    return names


def is_already_converted(filename: str, known_names: set[str]) -> bool:
    """
    Check if a PDF/DOCX file has already been converted by matching its
    normalized filename against the set of known empresa names.

    Uses substring matching in both directions: checks if the file's
    normalized name is contained in any known name, or vice versa.
    """
    normalized = normalize_name(filename)

    if not normalized:
        return False

    # Exact match
    if normalized in known_names:
        return True

    # Extract meaningful words from the filename (at least 4 chars)
    file_words = [w for w in normalized.split() if len(w) >= 4]

    if not file_words:
        return False

    # Check substring containment both ways
    for known in known_names:
        # File name contained in a known name
        if normalized in known:
            return True
        # Known name contained in file name
        if known in normalized:
            return True

        # Word overlap: if most meaningful words from the filename appear in a known name
        if len(file_words) >= 2:
            matching_words = sum(1 for w in file_words if w in known)
            if matching_words >= len(file_words) * 0.7:
                return True

    return False


def scan_directory(scan_dir: Path) -> list[Path]:
    """
    Recursively scan for PDF, DOCX, and DOC files, excluding the jsons
    subdirectory itself.
    """
    files = []
    extensions = ('*.pdf', '*.docx', '*.doc', '*.PDF', '*.DOCX', '*.DOC')

    for ext in extensions:
        for f in scan_dir.rglob(ext):
            # Skip files inside a 'jsons' directory
            if 'jsons' in f.parts:
                continue
            # Skip macOS resource fork files
            if '.__' in f.name or '__MACOSX' in str(f):
                continue
            files.append(f)

    # Deduplicate (case-insensitive glob might return duplicates)
    seen = set()
    unique = []
    for f in files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(f)

    return sorted(unique, key=lambda p: p.name.upper())


def main():
    parser = argparse.ArgumentParser(
        description='Prepare a work manifest for batch contract conversion.'
    )
    parser.add_argument(
        'directory',
        type=str,
        help='Directory to scan for PDF/DOCX/DOC files'
    )
    parser.add_argument(
        '--jsons-dir',
        type=str,
        default='./jsons/',
        help='Directory containing existing JSON conversions (default: ./jsons/)'
    )

    args = parser.parse_args()

    scan_dir = Path(args.directory).resolve()
    jsons_dir = Path(args.jsons_dir).resolve()

    if not scan_dir.is_dir():
        print(f"Error: '{scan_dir}' is not a valid directory", file=sys.stderr)
        sys.exit(1)

    # Step 1: Build set of known empresa names from existing JSONs
    print(f"Scanning JSONs in: {jsons_dir}", file=sys.stderr)
    known_names = extract_empresa_names_from_jsons(jsons_dir)
    print(f"Found {len(known_names)} unique empresa names in existing JSONs", file=sys.stderr)

    # Step 2: Scan for candidate files
    print(f"Scanning files in: {scan_dir}", file=sys.stderr)
    candidates = scan_directory(scan_dir)
    total = len(candidates)

    # Step 3: Filter out already-converted files
    to_process = []
    already_converted = 0

    for filepath in candidates:
        if is_already_converted(filepath.name, known_names):
            already_converted += 1
        else:
            to_process.append({
                "path": str(filepath.resolve()),
                "filename": filepath.name
            })

    # Step 4: Output manifest to stdout
    print(json.dumps(to_process, indent=2, ensure_ascii=False))

    # Step 5: Print summary to stderr
    print(
        f"\nTotal: {total} files | Already converted: {already_converted} | To process: {len(to_process)}",
        file=sys.stderr
    )


if __name__ == '__main__':
    main()
