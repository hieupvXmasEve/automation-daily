# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run Streamlit app
streamlit run streamlit_app.py

# Run CLI
python main.py compare --excel <file.xlsx> --pdf <file.pdf>
python main.py extract-items --excel <file.xlsx>

# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest

# Run a single test file
python -m pytest tests/test_compare.py

# Run a single test
python -m pytest tests/test_compare.py::ClassName::test_method_name
```

## Architecture

The app is an internal Streamlit UI + CLI tool for Vietnamese marketplace ops (Shopee, Lazada, TikTok). Entry points:

- `streamlit_app.py` — Streamlit multi-tab UI
- `main.py` → `shopee_compare/cli.py` — CLI entry point

### Module layout (`shopee_compare/`)

| File/Dir | Purpose |
|---|---|
| `services/` | Orchestration: `compare_service`, `extract_items_service`, `tiktok_pdf_service`, `marketplace_qr_scan_service`, `upload_workspace` |
| `exporters/` | CSV, XLSX, PDF output writers |
| `models.py` | Core dataclasses: `ExcelOrder`, `PdfOrder`, `OrderItem`, `ComparisonRecord` |
| `marketplace_scan_models.py` | QR scan dataclasses: `ImportedShopDataset`, `MarketplaceScanResultRow`, `MarketplaceScanEvent` |
| `excel_loader.py` | Reads Shopee workbook, groups line items into `ExcelOrder` records |
| `pdf_loader.py` | Parses one order per PDF page using `pdfplumber` |
| `tiktok_pdf_loader.py` | Parses TikTok labels — groups repeated `order_id` across multi-page records |
| `marketplace_scan_importer.py` | Reads CSV/XLSX shop files, detects Lazada pre-header rows, builds normalized lookup |
| `marketplace_qr_scan_matcher.py` | Normalizes scanned QR text, searches imported datasets, returns matched rows |
| `mobile_qr_scanner_component.py` | Streamlit V2 custom component for browser-side QR decoding |
| `mobile_qr_scanner_assets.py` | Embedded JS assets for the QR component |
| `matcher.py` | Joins `ExcelOrder` + `PdfOrder` by `order_id`, computes `ComparisonRecord` |
| `streamlit_existing_tabs.py` | UI for Compare, Extract, TikTok tabs |
| `streamlit_marketplace_qr_scan_tab.py` | UI for Mobile QR Scan tab |
| `streamlit_workflows.py` | Thin Streamlit glue — handles file uploads, calls services, returns download payloads |
| `utils.py` | `slugify_text`, `normalize_lookup_text`, `bool_label` |

### Key design rules

- Streamlit is a thin UI wrapper; all logic lives in `services/` and domain modules — never in tab renderers.
- `pdfplumber` parses text-based PDFs; Pillow generates the comparison PDF export (handles Vietnamese Unicode without external PDF libs).
- The mobile QR scan component is a Streamlit **V2 component** with style isolation disabled — `html5-qrcode` resolves DOM nodes via `document.getElementById`, which breaks inside a shadow root.
- QR decoding runs entirely in the browser; Python only receives decoded text strings.
- Mobile rollout requires HTTPS — browser camera APIs are unreliable on plain LAN HTTP.
- TikTok labels can span multiple pages; the loader groups by `order_id`, not page count.
