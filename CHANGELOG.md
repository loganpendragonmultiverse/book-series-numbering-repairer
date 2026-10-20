# Changelog

## 1.2.2

- Correct the testing guide to describe the actual CI checks and explicitly state that dependency auditing is not part of these workflows. Runtime behavior is unchanged.

## 1.2.1 - 2026-10-20

- Reject duplicate/blank CSV headers, ragged records and malformed quoting without discarding data.
- Preserve exact long-decimal and fractional ordering without rounding collisions.
- Reject malformed numeric/title fields and bound numeric parsing work.
- Create output exclusively and include project authority documents in wheels.

## 1.2.0 — 2026-10-15

- Compare normalized positions numerically, including signed zero and fractional aliases.
- Group entries by explicit series and report within-series normalized-position collisions.
- Preserve series through CSV input, JSON reports, and editable HTML downloads.

## 1.1.0 - 2026-09-07

- Reject invalid numeric orders and add CSV input, explicit reading/publication order and an editable local HTML preview.
- Added regression coverage for the audited behavior and invalid inputs.

## 1.0.0 - 2026-07-26

- Released the first complete Book Series Numbering Repairer command-line workflow.
- Added deterministic reporting, representative examples, cross-platform tests, and explicit limitations.
