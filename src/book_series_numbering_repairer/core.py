from __future__ import annotations

import json
from collections import Counter
from decimal import Decimal, DecimalException
from typing import Any

PROJECT = "book-series-numbering-repairer"


def _require(data: dict[str, Any], key: str) -> Any:
    if not isinstance(data, dict):
        raise ValueError("input and entry records must be JSON objects")
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _series_numbering(data: dict[str, Any]) -> dict[str, Any]:
    entries = _require(data, "entries")
    if not isinstance(entries, list):
        raise ValueError("entries must be an array")
    mode = data.get("order_mode", "reading")
    if mode not in {"reading", "publication"}:
        raise ValueError("order_mode must be reading or publication")
    labels = data.get("special_labels", {})
    if not isinstance(labels, dict) or not all(isinstance(key, str) for key in labels):
        raise ValueError("special_labels must map labels to explicit numeric orders")
    normalized = []
    for original, item in enumerate(entries):
        key = "publication_order" if mode == "publication" else "reading_order"
        if not isinstance(item, dict):
            raise ValueError(f"entries[{original}] must be an object")
        value = item.get(key)
        if value is None or value == "":
            if mode == "publication":
                raise ValueError(f"entries[{original}].publication_order is required")
            value = _require(item, "number")
        raw = str(labels.get(str(value), value)).strip().lower()
        if raw.startswith("book "):
            raw = raw[5:].strip()
        try:
            if raw in {"prequel", "zero", "0"}:
                order = Decimal(0)
            elif "/" in raw:
                numerator, denominator = raw.split("/", 1)
                top, bottom = Decimal(numerator), Decimal(denominator)
                if not top.is_finite() or not bottom.is_finite() or bottom == 0:
                    raise ValueError("fraction must be finite with a nonzero denominator")
                order = top / bottom
            else:
                order = Decimal(raw)
            if not order.is_finite():
                raise ValueError("number must be finite")
        except (DecimalException, ValueError) as exc:
            raise ValueError(
                f"entries[{original}].number must be a finite number or valid fraction"
            ) from exc
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
        "order_mode": mode,
        "special_labels": labels,
        "ambiguous_orders": [
            str(order)
            for order, count in Counter(item["normalized_order"] for item in normalized).items()
            if count > 1
        ],
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
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
