# Book Series Numbering Repairer

[![CI](https://github.com/loganpendragonmultiverse/book-series-numbering-repairer/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/book-series-numbering-repairer/actions/workflows/ci.yml)

Normalize prequels, novellas, decimals, fractions, and alternate series numbering. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Three-minute start

```bash
python -m pip install .
series-numbering examples/sample.json
series-numbering examples/sample.json --format json --output report.json
```

The example documents the v1 input shape. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

Normalization produces a reviewable order from explicit numbers; it does not decide canon or publication order.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.1.0: reviewed improvements

Reject invalid numeric orders and add CSV input, explicit reading/publication order and an editable local HTML preview.

```bash
series-numbering examples/sample.json --format html --output preview.html
```

CSV input supports title, number, reading_order and publication_order columns. JSON accepts `order_mode` (`reading` or `publication`) and `special_labels`, an explicit label-to-number mapping. `--order publication` requires publication_order for every entry. Reading order uses reading_order when supplied and falls back to number. Fractions must have finite operands and a nonzero denominator; numeric ties preserve source order. The HTML preview edits fields and downloads a new JSON input. Run the CLI again to validate and reorder those edits. No canonical reading or publication order is inferred.

## Explicit series groups (1.2)

Each entry may supply a series string, also supported as a CSV column and an
editable field in the HTML preview. Names are trimmed and case-sensitive.
Missing or blank series values share one unnamed group, preserving legacy inputs.
Groups appear in first-supplied order; entries sort by the selected reading or
publication position within each group, preserving source order for ties.
The collisions array identifies a series, normalized_order, and source_indices.
The legacy ambiguous_orders list now includes only positions that collide within
a series. Equal positions in distinct series are valid and do not collide.
Series names and orders are supplied by you; no canon or file renames are inferred.

## Exact numeric positions (1.2.1)

Positions compare as exact rational numbers. Distinct long decimal strings stay
distinct; equivalent fractions collide. Finite decimal results use normalized
decimal text, and repeating results use reduced fractions such as `1/3` instead
of rounded approximations. Source order still breaks exact ties.

Numeric operands may contain at most 256 characters with decimal exponent
magnitudes up to 1000. Boolean or structured numeric values and non-string titles
fail clearly. The editable HTML preview preserves numeric fields as strings to
avoid browser rounding; download its JSON and rerun the CLI to validate changes.
Existing report files are protected by exclusive creation.

Installed packages include project documents and `examples/sample.json` under
`share/doc/book-series-numbering-repairer/` inside the Python environment. Locate
its root with `python -c "import sys; print(sys.prefix)"`.

CSV imports require nonempty, unique headers and the same number of cells in
every nonblank record. Quoted commas and multiline fields remain supported.
Ambiguous or malformed CSV fails before report generation instead of discarding
an earlier column or inventing a missing cell.

Existing output paths, including dangling symbolic links, are refused before
exclusive file creation. This protects ordinary output collisions; it does not
promise protection against hostile concurrent file-system changes.
