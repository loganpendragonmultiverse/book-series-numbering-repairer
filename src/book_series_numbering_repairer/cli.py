from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from .core import analyze, render_json, render_markdown
from .preview import render_html


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        headers = next(reader, None)
        if not headers or any(not field.strip() for field in headers):
            raise ValueError("CSV requires nonempty column headers")
        if len(headers) != len({field.strip() for field in headers}):
            raise ValueError("CSV column headers must be unique")
        rows = []
        for row in reader:
            if not row:
                continue
            if len(row) != len(headers):
                raise ValueError(
                    f"CSV row ending at line {reader.line_num} has {len(row)} cells; expected {len(headers)}"
                )
            rows.append(dict(zip(headers, row, strict=True)))
        return rows


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
            data = {"entries": _csv_rows(args.input)}
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
            if args.output.exists() or args.output.is_symlink():
                raise ValueError(f"output already exists: {args.output}")
            with args.output.open("x", encoding="utf-8", newline="") as handle:
                handle.write(rendered)
        else:
            sys.stdout.write(rendered)
    except (OSError, UnicodeError, ValueError, TypeError, csv.Error, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
