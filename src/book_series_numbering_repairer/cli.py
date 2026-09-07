from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .core import analyze, render_json, render_markdown
from .preview import render_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic, reviewable report from explicit JSON input."
    )
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    parser.add_argument("--order", choices=("reading", "publication"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.suffix.lower() == ".csv":
            with args.input.open(encoding="utf-8-sig", newline="") as source:
                data = {"entries": list(csv.DictReader(source))}
        else:
            data = json.loads(args.input.read_text(encoding="utf-8"))
        if args.order:
            if not isinstance(data, dict):
                raise ValueError("input must be a JSON object")
            data["order_mode"] = args.order
        report = analyze(data)
        rendered = {"json": render_json, "markdown": render_markdown, "html": render_html}[
            args.format
        ](report)
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
