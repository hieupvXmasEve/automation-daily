# Journal

## Context

Bootstrapped a new Python CLI for comparing Shopee Excel orders against label PDFs.

## What Happened

- Inspected sample Excel and PDF
- Confirmed `pandas` reads the Shopee workbook correctly
- Confirmed `pdfplumber` can parse one order per PDF page
- Built package structure, loaders, matcher, exporters, CLI
- Added `unittest` coverage and operational docs

## Decisions

- Pin runtime with `pyenv` at `3.11.10`
- Use pure local stack, no new network dependency required
- Use Pillow for Unicode-safe PDF report rendering

## Next

- Extend compare rules if recipient/product-level validation becomes mandatory
