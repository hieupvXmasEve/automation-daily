# Phase 02: Parse And Normalize Sources

## Context Links

- [Tech Stack](../../docs/tech-stack.md)
- Sample Excel: `shopee/Order.all.order_creation_date.20260401_20260403.xlsx`
- Sample PDF: `shopee/SP Mollis (B4098) - 38 đơn - 03.04.2026.pdf`

## Overview

Priority: High
Status: Completed
Goal: convert Excel rows and PDF pages into normalized order records.

## Key Insights

- Excel is line-item based; one order can span many rows.
- PDF is page-based; current sample is one label per page.
- Direct `openpyxl` read-only parsing is unreliable on this Shopee export. `pandas.read_excel` works.

## Requirements

- Normalize order ids, waybills, dates, quantities
- Aggregate Excel line items into order-level records
- Parse PDF item block, order date/time, recipient block, and page number

## Architecture

- `excel_loader.py`: ingest dataframe, clean NaN, group by order id
- `pdf_loader.py`: regex/text parser per page
- `models.py`: dataclasses for source and comparison rows

## Related Code Files

- Create: `shopee_compare/models.py`
- Create: `shopee_compare/excel_loader.py`
- Create: `shopee_compare/pdf_loader.py`

## Implementation Steps

1. Define normalized dataclasses
2. Implement Excel aggregation
3. Implement PDF per-page parsing
4. Validate against sample counts

## Todo List

- [x] Dataclasses defined
- [x] Excel parser implemented
- [x] PDF parser implemented
- [x] Sample counts validated

## Success Criteria

- Excel unique orders count is reproducible
- PDF order count equals page count on sample
- Parsed records contain stable compare keys

## Risk Assessment

- PDF text layout may shift
- Mitigation: isolate regexes and keep parser defensive

## Security Considerations

- Treat all extracted text as plain data
- No eval or shell interpolation from file contents

## Next Steps

- Build matcher and exporters
