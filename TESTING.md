# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI runs the supported OS/Python matrix and CodeQL analysis. The current workflows do not run a dependency audit.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Reject invalid numeric orders and add CSV input, explicit reading/publication order and an editable local HTML preview.

## 1.2.1 acceptance

Run full lint, typing, coverage and build commands above. Regression cases cover
long decimals, equivalent repeating fractions, close unequal values, signed zero,
malformed numeric/title fields and numeric work bounds. Install each wheel/sdist
and run the full suite from outside the checkout against site-packages. Execute
all report formats on the installed example. In a browser, edit series and order
fields, download JSON, and reimport it with the installed CLI. Confirm large
integer positions survive without rounding. Check all four installed documents.

`tests/test_output_links.py` checks refusal of existing dangling-link metadata
on every platform and actual dangling symlinks where creation is supported.
