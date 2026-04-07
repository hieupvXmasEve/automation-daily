# Codebase Summary

## Overview

Small offline Python project with two entrypoints: CLI and internal Streamlit UI.

## Main Modules

- `main.py`: simple terminal entrypoint
- `streamlit_app.py`: internal web entrypoint
- `shopee_compare/cli.py`: CLI command parsing and console rendering
- `shopee_compare/services/`: shared compare/extract workflow orchestration
- `shopee_compare/streamlit_workflows.py`: upload-to-temp and download-payload bridge for Streamlit
- `shopee_compare/excel_loader.py`: Shopee Excel ingestion and aggregation
- `shopee_compare/pdf_loader.py`: PDF page parsing
- `shopee_compare/tiktok_pdf_loader.py`: TikTok Shop PDF parsing and multi-page order grouping
- `shopee_compare/matcher.py`: comparison logic and summary counts
- `shopee_compare/services/tiktok_pdf_service.py`: TikTok PDF audit workflow and export orchestration
- `shopee_compare/exporters/`: CSV, XLSX, PDF exporters
- `tests/test_compare.py`: CLI and comparison workflow coverage
- `tests/test_extract_items.py`: item export coverage
- `tests/test_tiktok_pdf_audit.py`: TikTok PDF aggregation and export coverage
- `tests/test_workflows.py`: shared workflow and upload workspace coverage

## Data Flow

1. CLI or Streamlit collects local file paths/uploads
2. Shared services run compare or item-export workflows
3. Excel rows are normalized to order or item-level records
4. PDF pages are parsed to label-level records
5. Matcher joins by order id
6. Exporters create downloadable artifacts
7. TikTok PDFs can also be parsed into grouped order-level audit rows keyed by `order_id`
