#!/usr/bin/env python3
"""End-to-end contract generator.

Orchestrates:
  1. Resolve template (by name or path)
  2. Look up contratante via ReceitaWS
  3. Merge contratada JSON + contract terms
  4. Fill the .docx and write to disk

Usage:
  generate_contract.py \
      --template TEMPLATE_Contrato-Prestacao-Servicos \
      --contratante 41618108000120 \
      --contratada ~/Documents/template_filler_data/contratada_ecab.json \
      --terms terms.json \
      [--output Contrato_Cliente_2026-04-15.docx]
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(PLUGIN_ROOT))

from template_filler.integrations.receitaws import ReceitaWSClient, ReceitaWSError  # noqa: E402

# Reuse fill_docx as a library by importing it
sys.path.insert(0, str(SCRIPT_DIR))
from fill_docx import fill_template  # noqa: E402


def data_dir() -> Path:
    base = os.getenv("TEMPLATE_FILLER_DIR")
    if base:
        return Path(base).expanduser()
    return Path.home() / "Documents" / "template_filler_data"


def resolve_template(name_or_path: str) -> Path:
    p = Path(name_or_path).expanduser()
    if p.exists() and p.suffix == ".docx":
        return p
    templates_dir = data_dir() / "templates"
    candidates = list(templates_dir.glob(f"*{name_or_path}*.docx"))
    candidates = [c for c in candidates if not c.name.startswith("~$")]
    if not candidates:
        raise FileNotFoundError(
            f"No template matching '{name_or_path}' in {templates_dir}"
        )
    if len(candidates) > 1:
        names = ", ".join(c.name for c in candidates)
        raise ValueError(f"Ambiguous template '{name_or_path}': {names}")
    return candidates[0]


def lookup_contratante(cnpj: str) -> dict:
    client = ReceitaWSClient()
    company = client.get_company_data(cnpj)
    addr_parts = [
        company.get("logradouro", ""),
        company.get("numero", ""),
        company.get("complemento", ""),
        company.get("bairro", ""),
    ]
    logradouro = ", ".join(p for p in addr_parts if p)
    return {
        "contratante_razaoSocial": company.get("nome", ""),
        "contratante_cnpj": re.sub(r"\D", "", company.get("cnpj", "")),
        "contratante_logradouro": logradouro,
        "contratante_cidade": company.get("municipio", ""),
        "contratante_uf": company.get("uf", ""),
        "contratante_cep": re.sub(r"\D", "", company.get("cep", "")),
    }


def load_json(path: str) -> dict:
    with open(Path(path).expanduser()) as f:
        return json.load(f)


def default_output_path(template: Path, data: dict) -> Path:
    outdir = data_dir() / "generated"
    razao = data.get("contratante_razaoSocial", "cliente")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", razao).strip("_")[:40].upper() or "CLIENTE"
    today = datetime.now().strftime("%Y-%m-%d")
    stem = template.stem.replace("TEMPLATE_", "")
    return outdir / f"{stem}__{slug}__{today}.docx"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a contract from a local .docx template")
    ap.add_argument("--template", required=True, help="Template name or path")
    ap.add_argument("--contratante", required=True, help="Contratante CNPJ (digits or formatted)")
    ap.add_argument("--contratada", required=True, help="Path to contratada JSON")
    ap.add_argument("--terms", required=True, help="Path to contract terms JSON")
    ap.add_argument("--output", help="Output .docx path (default: auto)")
    ap.add_argument("--dry-run", action="store_true", help="Print merged data without writing file")
    args = ap.parse_args()

    try:
        template_path = resolve_template(args.template)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        contratante_data = lookup_contratante(args.contratante)
    except ReceitaWSError as e:
        print(f"ERROR: ReceitaWS lookup failed: {e}", file=sys.stderr)
        return 1

    contratada_data = load_json(args.contratada)
    terms_data = load_json(args.terms)

    data = {**contratada_data, **contratante_data, **terms_data}
    if "data" not in data:
        data["data"] = datetime.now().strftime("%Y-%m-%d")

    if args.dry_run:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    output = Path(args.output).expanduser() if args.output else default_output_path(template_path, data)
    missing = fill_template(str(template_path), data, str(output))

    print(f"wrote {output}")
    print(f"template: {template_path.name}")
    print(f"contratante: {data.get('contratante_razaoSocial')}")
    if missing:
        print(f"WARNING: {len(missing)} unfilled placeholder(s):")
        for k in sorted(missing):
            print(f"  - {k}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
