# Codebase Summary

## Overview

Small local Python project with two entrypoints: CLI and internal Streamlit UI for Shopee compare, Shopee item export, TikTok PDF audit, and mobile QR scan across imported marketplace shop files.

## Main Modules

- `main.py`: simple terminal entrypoint
- `streamlit_app.py`: internal web entrypoint
- `shopee_compare/cli.py`: CLI command parsing and console rendering
- `shopee_compare/services/`: shared compare/extract workflow orchestration
- `shopee_compare/streamlit_workflows.py`: upload-to-temp and download-payload bridge for Streamlit
- `shopee_compare/excel_loader.py`: Shopee Excel ingestion and aggregation
- `shopee_compare/pdf_loader.py`: PDF page parsing
- `shopee_compare/tiktok_pdf_loader.py`: TikTok Shop PDF parsing and multi-page order grouping
- `shopee_compare/marketplace_scan_models.py`: dataclasses for imported shops, scan candidates, and scan result rows
- `shopee_compare/marketplace_scan_importer.py`: CSV/XLSX marketplace import and normalized lookup registry builder
- `shopee_compare/marketplace_qr_scan_matcher.py`: QR text normalization, candidate search, and dedupe-aware scan resolution
- `shopee_compare/mobile_qr_scanner_component.py`: Streamlit V2 mobile browser camera component
- `shopee_compare/streamlit_existing_tabs.py`: compare, extract-items, and TikTok audit tab renderers
- `shopee_compare/streamlit_marketplace_qr_scan_tab.py`: mobile QR scan tab renderer and session-state UX
- `shopee_compare/matcher.py`: comparison logic and summary counts
- `shopee_compare/services/tiktok_pdf_service.py`: TikTok PDF audit workflow and export orchestration
- `shopee_compare/services/marketplace_qr_scan_service.py`: scan workflow and Excel export orchestration
- `shopee_compare/exporters/`: CSV, XLSX, PDF exporters
- `tests/test_compare.py`: CLI and comparison workflow coverage
- `tests/test_extract_items.py`: item export coverage
- `tests/test_tiktok_pdf_audit.py`: TikTok PDF aggregation and export coverage
- `tests/test_marketplace_qr_scan_service.py`: importer, matcher, dedupe, and Excel export coverage for mobile QR scan
- `tests/test_workflows.py`: shared workflow and upload workspace coverage

## Data Flow

1. CLI or Streamlit collects local file paths/uploads
2. Shared services run compare or item-export workflows
3. Excel rows are normalized to order or item-level records
4. PDF pages are parsed to label-level records
5. Matcher joins by order id
6. Exporters create downloadable artifacts
7. TikTok PDFs can also be parsed into grouped order-level audit rows keyed by `order_id`
8. Mobile QR scan imports shop files into one session-local registry, resolves decoded QR text against the selected compare field, dedupes repeat scans, and exports the filtered review table to Excel
