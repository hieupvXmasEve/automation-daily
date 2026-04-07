# CLI Design Guidelines

## Goal

Build a terminal-first tool for warehouse/ops use. Fast input. Low ceremony. Clear file outputs.

## Interaction Model

- One primary command: `compare`
- Required inputs: `--excel`, `--pdf`
- Optional outputs: `--formats csv excel pdf`
- Optional filters: `--only matched|mismatch|missing-in-excel|missing-in-pdf`
- Default output folder: `output/{timestamp}`

## UX Rules

- Print a compact preflight summary before processing
- Fail fast on unreadable files with direct error messages
- Show a final terminal summary:
  total excel orders, total pdf labels, matched, mismatched, missing
- Print exact paths of exported files
- Keep text ASCII-friendly where possible, but preserve Vietnamese data content

## Matching Rules

- Primary key: `Mã đơn hàng`
- Secondary validation: `Mã vận đơn`
- Derived checks:
  - total quantity from Excel vs total quantity from PDF
  - order datetime from Excel vs PDF order date/time
  - item summary similarity as informational note

## Output Rules

- CSV: flat comparison table, UTF-8 with BOM for Excel compatibility
- Excel: workbook with sheets `comparison`, `excel_orders`, `pdf_orders`
- PDF: concise printable audit summary and comparison rows

## Non-Goals For V1

- OCR for scanned PDFs
- GUI/TUI menu
- Auto-download from Shopee
- Pixel-perfect regeneration of original shipping labels
