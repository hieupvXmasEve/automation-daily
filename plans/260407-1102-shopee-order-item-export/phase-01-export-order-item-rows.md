# Phase 01: Export Order Item Rows

## Context Links

- `docs/README.md`
- `docs/code-standards.md`
- `shopee_compare/cli.py`
- `shopee_compare/excel_loader.py`

## Overview

- Priority: High
- Status: Complete
- Description: Add a new command to flatten Shopee Excel orders into item-level rows for operations.

## Key Insights

- The Shopee file already uses header row 1.
- Required source fields are `Mã đơn hàng`, `SKU phân loại hàng`, `Số lượng`, `Ngày đặt hàng`.
- `Total Order` is derived per row as `row_quantity/total_order_quantity`.

## Requirements

- Validate required columns before export.
- Keep original item row order from the Excel file.
- Export columns:
  - `Mã đơn hàng`
  - `Mã vật tư`
  - `Số lượng`
  - `Total Order`
  - `Ngày đặt hàng`

## Architecture

- Reuse `pandas.read_excel`
- Build a normalized flat frame in a dedicated module
- Add a CLI subcommand that writes `.xlsx` or `.csv`

## Related Code Files

- Modify: `shopee_compare/cli.py`
- Modify: `docs/README.md`
- Create: `shopee_compare/order_item_export.py`
- Create: `tests/test_extract_items.py`

## Implementation Steps

1. Add a flat export builder with required column validation.
2. Compute `sku_index` and `total_sku_rows` per order.
3. Add CLI subcommand and file writer.
4. Cover extraction and command export with tests.

## Todo List

- [x] Build export frame generator
- [x] Add CLI command
- [x] Add tests
- [x] Update docs

## Success Criteria

- Command exits `0`
- Output file exists and contains expected columns
- Sample order with two SKU rows of quantity `1` yields `0.5`, `0.5`
- Result: done

## Risk Assessment

- Risk: Misread meaning of `Total Order`
- Mitigation: Use explicit per-SKU position format and note assumption

## Security Considerations

- Local file read only
- No external network or secret handling

## Next Steps

- Run tests
- Update docs for command usage
- None
