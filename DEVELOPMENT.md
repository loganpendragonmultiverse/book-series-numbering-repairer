# Development contract

Normalize prequels, novellas, decimals, fractions, and alternate series numbering.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, changelog, README claims, repository metadata, release assets, and the Forge catalog together.

## 1.1.0 improvement session

Reject invalid numeric orders and add CSV input, explicit reading/publication order and an editable local HTML preview.

CSV input supports title, number, reading_order and publication_order columns. JSON accepts `order_mode` (`reading` or `publication`) and `special_labels`, an explicit label-to-number mapping. `--order publication` requires publication_order for every entry. Reading order uses reading_order when supplied and falls back to number. Fractions must have finite operands and a nonzero denominator; numeric ties preserve source order. The HTML preview edits fields and downloads a new JSON input. Run the CLI again to validate and reorder those edits. No canonical reading or publication order is inferred.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.
