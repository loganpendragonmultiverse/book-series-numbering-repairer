from __future__ import annotations

import json
from collections import Counter
from decimal import Decimal, DecimalException, localcontext
from fractions import Fraction
from typing import Any

PROJECT = "book-series-numbering-repairer"


def _require(data: dict[str, Any], key: str) -> Any:
    if not isinstance(data, dict):
        raise TypeError("input and entry records must be JSON objects")
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _decimal(raw: str) -> Decimal:
    if len(raw) > 256:
        raise ValueError("numeric operands must contain at most 256 characters")
    value = Decimal(raw)
    if not value.is_finite() or abs(value.adjusted()) > 1000:
        raise ValueError("numeric operands must be finite with exponents within 1000")
    return value


def _canonical(value: Fraction) -> str:
    denominator = value.denominator
    for divisor in (2, 5):
        while denominator % divisor == 0:
            denominator //= divisor
    if denominator != 1:
        return str(value)
    with localcontext() as context:
        context.prec = max(28, len(str(abs(value.numerator))) + len(str(value.denominator)) + 2)
        return str((Decimal(value.numerator) / Decimal(value.denominator)).normalize())


def _series_numbering(data: dict[str, Any]) -> dict[str, Any]:
    entries = _require(data, "entries")
    if not isinstance(entries, list):
        raise TypeError("entries must be an array")
    mode = data.get("order_mode", "reading")
    if not isinstance(mode, str) or mode not in {"reading", "publication"}:
        raise ValueError("order_mode must be reading or publication")
    labels = data.get("special_labels", {})
    if not isinstance(labels, dict) or not all(isinstance(key, str) for key in labels):
        raise ValueError("special_labels must map labels to explicit numeric orders")
    normalized = []
    groups: dict[str, int] = {}
    for original, item in enumerate(entries):
        key = "publication_order" if mode == "publication" else "reading_order"
        if not isinstance(item, dict):
            raise TypeError(f"entries[{original}] must be an object")
        series = item.get("series", "")
        if not isinstance(series, str):
            raise TypeError(f"entries[{original}].series must be text")
        series = series.strip()
        groups.setdefault(series, len(groups))
        value = item.get(key)
        if value is None or value == "":
            if mode == "publication":
                raise ValueError(f"entries[{original}].publication_order is required")
            value = _require(item, "number")
        value = labels.get(str(value), value)
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise TypeError(f"entries[{original}].number must be text or a number")
        title = item.get("title", "Untitled")
        if not isinstance(title, str):
            raise TypeError(f"entries[{original}].title must be text")
        raw = str(value).strip().lower()
        if raw.startswith("book "):
            raw = raw[5:].strip()
        try:
            if raw in {"prequel", "zero", "0"}:
                order = Fraction(0)
            elif "/" in raw:
                numerator, denominator = raw.split("/", 1)
                top, bottom = _decimal(numerator), _decimal(denominator)
                if bottom == 0:
                    raise ValueError("fraction must have a nonzero denominator")
                order = Fraction(top) / Fraction(bottom)
            else:
                order = Fraction(_decimal(raw))
        except (DecimalException, ValueError) as exc:
            raise ValueError(
                f"entries[{original}].number must be a finite number or valid fraction"
            ) from exc
        normalized.append(
            {
                **item,
                "series": series,
                "normalized_order": "-0"
                if order == 0 and raw.startswith("-")
                else _canonical(order),
                "display": f"Book {'-0' if order == 0 and raw.startswith('-') else _canonical(order)}: {title}",
                "source_index": original,
            }
        )
    normalized.sort(
        key=lambda item: (
            groups[item["series"]],
            Fraction(item["normalized_order"]),
            item["source_index"],
        )
    )
    collisions = []
    for series in groups:
        counts = Counter(
            (
                Fraction(0)
                if Fraction(item["normalized_order"]) == 0
                else Fraction(item["normalized_order"])
            )
            for item in normalized
            if item["series"] == series
        )
        for order, count in counts.items():
            if count > 1:
                collisions.append(
                    {
                        "series": series,
                        "normalized_order": _canonical(order),
                        "source_indices": [
                            item["source_index"]
                            for item in normalized
                            if item["series"] == series
                            and Fraction(item["normalized_order"]) == order
                        ],
                    }
                )
    return {
        "entries": normalized,
        "order_mode": mode,
        "special_labels": labels,
        "series_groups": list(groups),
        "collisions": collisions,
        "ambiguous_orders": list(dict.fromkeys(item["normalized_order"] for item in collisions)),
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TypeError("input must be a JSON object")
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
