# Codebase Summary

## Overview

Small offline Python CLI project.

## Main Modules

- `main.py`: simple terminal entrypoint
- `shopee_compare/cli.py`: CLI command parsing and orchestration
- `shopee_compare/excel_loader.py`: Shopee Excel ingestion and aggregation
- `shopee_compare/pdf_loader.py`: PDF page parsing
- `shopee_compare/matcher.py`: comparison logic and summary counts
- `shopee_compare/exporters/`: CSV, XLSX, PDF exporters
- `tests/test_compare.py`: integration-style workflow coverage

## Data Flow

1. Read Excel rows
2. Aggregate to order-level records
3. Parse PDF pages to label-level records
4. Join by order id
5. Export reports
