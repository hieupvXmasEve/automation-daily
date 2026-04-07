# Plan: Shopee Order Item Export

- Status: Complete
- Priority: High
- Goal: Add a CLI flow to export item-level rows from Shopee Excel with `Mã đơn hàng`, `Mã vật tư`, `Số lượng`, `Total Order`, `Ngày đặt hàng`

## Phases

1. [Phase 01](./phase-01-export-order-item-rows.md) - Parse Excel and export item rows

## Dependencies

- Existing `pandas` + `openpyxl` setup
- Fixture file at `shopee/Order.all.order_creation_date.20260402_20260406.xlsx`

## Success Criteria

- Command reads Shopee Excel export without extra config
- Output keeps source row order within each order
- `Total Order` shows row quantity divided by total order quantity
- Tests cover data extraction and file export
- Result: done
