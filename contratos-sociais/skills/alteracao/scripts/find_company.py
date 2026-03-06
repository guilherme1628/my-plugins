#!/usr/bin/env python3
"""
find_company.py — Search the jsons directory for a company's contract data.

Usage:
    find_company.py <company_name> [--jsons-dir DIR] [--summary]

Searches JSON filenames for matches (case-insensitive, partial match).
If multiple matches are found, lists them to stderr and outputs nothing to stdout.
If a single match is found, outputs the full JSON content to stdout.

When a company has both a Contrato Social and one or more Alteracoes,
the highest-numbered Alteracao is preferred (it contains the most recent
contrato_consolidado).
"""

import argparse
import json
import os
import re
import sys
import unicodedata


def normalize(text: str) -> str:
    """Normalize text for comparison: lowercase, strip accents, collapse whitespace/underscores."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"[_\s]+", " ", text)
    return text.strip()


def extract_company_name_from_filename(filename: str) -> str:
    """
    Extract company name from a JSON filename.

    Filename patterns:
      Pattern A (no C-prefix):  EMPRESA_NAME|CNPJ|tipo|versao.json
      Pattern B (C-prefix):     C{id}|EMPRESA_NAME|tipo|versao.json
      Pattern C (C-prefix alt): C{id}|tipo|null_or_versao|EMPRESA_NAME.json
      Pattern D (C-prefix alt): C{id}|tipo|versao|EMPRESA_NAME.json

    Returns the best guess for the company name.
    """
    base = filename
    if base.endswith(".json"):
        base = base[:-5]

    parts = base.split("|")

    if not parts:
        return ""

    is_c_prefix = bool(re.match(r"^C\d+$", parts[0]))

    if not is_c_prefix:
        # Pattern A: EMPRESA_NAME|CNPJ|tipo|versao
        return parts[0].replace("_", " ").strip()

    # C-prefix patterns: need to figure out which segment has the company name
    # Heuristic: the company name is the segment that is NOT:
    #   - The C{id}
    #   - A known tipo (Contrato Social, Alteracao Contratual, etc.)
    #   - A known versao pattern (Nª Alteração, null, empty)
    #   - A CNPJ (digits only)

    tipo_patterns = [
        "contrato social",
        "alteracao contratual",
        "alteração contratual",
        "altera__o_contratual",
    ]
    versao_pattern = re.compile(
        r"^(\d+[ªa]\s*altera[cç][ãa]o|null|\.?|\d+__altera__o)$", re.IGNORECASE
    )
    cnpj_pattern = re.compile(r"^\d{14}$")

    candidates = []
    for i, part in enumerate(parts):
        if i == 0:
            continue  # skip C{id}
        stripped = part.strip()
        if not stripped or stripped == "." or stripped == "null":
            continue
        if normalize(stripped) in [normalize(t) for t in tipo_patterns]:
            continue
        if versao_pattern.match(stripped):
            continue
        if cnpj_pattern.match(stripped.replace(".", "").replace("/", "").replace("-", "")):
            continue
        candidates.append(stripped)

    if candidates:
        # Prefer the longest candidate (company names are usually the longest)
        return max(candidates, key=len)

    return base


def parse_versao_number(versao_str: str) -> int:
    """
    Extract the numeric version from a versao string like '3ª Alteração'.
    Returns 0 for Contrato Social or unparseable strings.
    """
    if not versao_str:
        return 0
    match = re.search(r"(\d+)", versao_str)
    if match:
        return int(match.group(1))
    return 0


def get_doc_type_and_version(filepath: str) -> tuple:
    """
    Determine document type and version from both filename and JSON content.
    Returns (tipo_documento: str, version_number: int).
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return ("unknown", 0)

    tipo = data.get("tipo_documento", "")
    versao = data.get("versao_alteracao", "")

    if not tipo:
        # Try to infer from filename
        fname = os.path.basename(filepath).lower()
        if "contrato_social" in fname or "contrato social" in fname:
            tipo = "Contrato Social"
        elif "altera" in fname:
            tipo = "Alteração Contratual"

    version_num = parse_versao_number(versao) if versao else 0

    # If tipo indicates alteration but version is 0, try parsing from filename
    if "altera" in tipo.lower() and version_num == 0:
        fname = os.path.basename(filepath)
        match = re.search(r"(\d+)[ªa_]*\s*[Aa]ltera", fname)
        if match:
            version_num = int(match.group(1))

    return (tipo, version_num)


def find_matching_files(query: str, jsons_dir: str) -> list:
    """
    Find all JSON files whose filename contains the query (case-insensitive,
    accent-insensitive, partial match).

    Returns list of (filepath, company_name) tuples.
    """
    norm_query = normalize(query)
    matches = []

    for filename in os.listdir(jsons_dir):
        if not filename.endswith(".json"):
            continue
        norm_filename = normalize(filename)
        if norm_query in norm_filename:
            filepath = os.path.join(jsons_dir, filename)
            company_name = extract_company_name_from_filename(filename)
            matches.append((filepath, company_name))

    return matches


def group_by_company(matches: list) -> dict:
    """
    Group matched files by normalized company name.
    Returns dict: { normalized_name: [(filepath, display_name, tipo, version)] }
    """
    groups = {}
    for filepath, company_name in matches:
        key = normalize(company_name)
        tipo, version = get_doc_type_and_version(filepath)
        if key not in groups:
            groups[key] = []
        groups[key].append((filepath, company_name, tipo, version))
    return groups


def pick_best_file(files: list) -> str:
    """
    From a list of (filepath, company_name, tipo, version) for the SAME company,
    pick the best file: highest version Alteracao > Contrato Social.
    """
    alteracoes = [(fp, cn, t, v) for fp, cn, t, v in files if "altera" in t.lower()]
    contratos = [(fp, cn, t, v) for fp, cn, t, v in files if "contrato" in t.lower() and "altera" not in t.lower()]

    if alteracoes:
        # Pick the one with the highest version number
        best = max(alteracoes, key=lambda x: x[3])
        return best[0]
    elif contratos:
        return contratos[0][0]
    else:
        # Fallback: just return the first file
        return files[0][0]


def format_summary(data: dict) -> dict:
    """Build summary dict from JSON data."""
    empresa = data.get("empresa", {})
    nome = empresa.get("nome", "N/A") if isinstance(empresa, dict) else "N/A"
    cnpj = empresa.get("cnpj", "N/A") if isinstance(empresa, dict) else "N/A"

    clausulas = data.get("contrato_consolidado", [])
    if not isinstance(clausulas, list):
        clausulas = []

    socios = data.get("sócios", data.get("socios", []))
    if not isinstance(socios, list):
        socios = []

    clause_titles = []
    for cl in clausulas:
        if isinstance(cl, dict):
            titulo = cl.get("titulo", "")
            if titulo:
                clause_titles.append(titulo)

    return {
        "empresa": nome,
        "cnpj": cnpj,
        "qtd_clausulas": len(clausulas),
        "qtd_socios": len(socios),
        "clausulas": clause_titles,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Search the jsons directory for a company's contract data."
    )
    parser.add_argument(
        "company",
        help="Company name or partial name to search for.",
    )
    parser.add_argument(
        "--jsons-dir",
        default=None,
        help="Directory containing the JSON files. Required.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Output only a summary: empresa, cnpj, qtd_clausulas, qtd_socios, clause titles.",
    )
    args = parser.parse_args()

    if args.jsons_dir is None:
        print("Error: --jsons-dir is required. Provide the path to the JSON contract database.", file=sys.stderr)
        sys.exit(1)

    jsons_dir = os.path.abspath(args.jsons_dir)
    if not os.path.isdir(jsons_dir):
        print(f"Error: directory not found: {jsons_dir}", file=sys.stderr)
        sys.exit(1)

    # Find matching files
    matches = find_matching_files(args.company, jsons_dir)
    if not matches:
        print(f"No matches found for: {args.company}", file=sys.stderr)
        sys.exit(1)

    # Group by company
    groups = group_by_company(matches)

    if len(groups) > 1:
        # Multiple distinct companies matched — list them and exit
        print(f"Multiple companies match '{args.company}':", file=sys.stderr)
        print(file=sys.stderr)
        for i, (key, files) in enumerate(sorted(groups.items()), 1):
            display_name = files[0][1]  # use first file's display name
            versions = []
            for fp, cn, tipo, ver in files:
                if "altera" in tipo.lower():
                    versions.append(f"{tipo} ({ver}ª)")
                else:
                    versions.append(tipo)
            docs = ", ".join(versions) if versions else "?"
            print(f"  [{i}] {display_name}  ({docs})", file=sys.stderr)
        print(file=sys.stderr)
        print("Refine your search to match a single company.", file=sys.stderr)
        sys.exit(2)

    # Single company — pick the best file
    key, files = next(iter(groups.items()))
    best_path = pick_best_file(files)

    try:
        with open(best_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading {best_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if len(files) > 1:
        chosen = os.path.basename(best_path)
        print(f"Found {len(files)} files for this company. Using: {chosen}", file=sys.stderr)

    if args.summary:
        summary = format_summary(data)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
