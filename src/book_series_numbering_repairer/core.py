from __future__ import annotations

import json
from collections import Counter
from decimal import Decimal
from typing import Any

PROJECT = "book-series-numbering-repairer"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _series_numbering(data: dict[str, Any]) -> dict[str, Any]:
    entries = _require(data, "entries")
    normalized = []
    for original, item in enumerate(entries):
        raw = str(_require(item, "number")).strip().lower().replace("book", "").strip()
        if raw in {"prequel", "zero", "0"}:
            order = Decimal(0)
        elif "/" in raw:
            numerator, denominator = raw.split("/", 1)
            order = Decimal(numerator) / Decimal(denominator)
        else:
            order = Decimal(raw)
        normalized.append(
            {
                **item,
                "normalized_order": str(order.normalize()),
                "display": f"Book {order.normalize()}: {item.get('title', 'Untitled')}",
                "source_index": original,
            }
        )
    normalized.sort(key=lambda item: (Decimal(item["normalized_order"]), item["source_index"]))
    return {
        "entries": normalized,
        "ambiguous_orders": [
            str(order)
            for order, count in Counter(item["normalized_order"] for item in normalized).items()
            if count > 1
        ],
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_series_numbering(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
