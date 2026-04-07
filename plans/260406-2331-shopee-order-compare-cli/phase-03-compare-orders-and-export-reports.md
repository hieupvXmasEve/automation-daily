# Phase 03: Compare Orders And Export Reports

## Context Links

- [CLI Flow](../../docs/wireframe/cli-flow.md)
- [Phase 02](./phase-02-parse-and-normalize-sources.md)

## Overview

Priority: High
Status: Completed
Goal: compare normalized records and write audit outputs in CSV, Excel, PDF.

## Key Insights

- PDF often contains only a subset of Excel orders.
- Most stable comparison key is order id. Waybill and quantity are validations, not primary joins.

## Requirements

- Join records by order id
- Mark statuses: matched, mismatch, missing-in-excel, missing-in-pdf
- Support selective export formats
- Print concise terminal summary

## Architecture

- `matcher.py`: comparison logic
- `exporters/`: one module per format
- `cli.py`: command parsing, orchestration, output directory creation

## Related Code Files

- Create: `shopee_compare/matcher.py`
- Create: `shopee_compare/cli.py`
- Create: `shopee_compare/exporters/csv_exporter.py`
- Create: `shopee_compare/exporters/excel_exporter.py`
- Create: `shopee_compare/exporters/pdf_exporter.py`

## Implementation Steps

1. Build comparison row model
2. Implement comparison engine
3. Implement exporters
4. Wire everything into CLI command

## Todo List

- [x] Comparison engine implemented
- [x] CSV exporter implemented
- [x] Excel exporter implemented
- [x] PDF exporter implemented
- [x] CLI end-to-end command implemented

## Success Criteria

- Tool creates requested formats in output directory
- Terminal summary matches exported counts
- Output files open successfully

## Risk Assessment

- PDF writing without external libs can become brittle
- Mitigation: keep layout text-only and paginated

## Security Considerations

- Sanitize output filenames
- Never overwrite outside chosen output directory

## Next Steps

- Add automated tests and docs
