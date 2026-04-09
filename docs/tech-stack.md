# Tech Stack

## Overview

Python app with CLI and internal Streamlit entrypoints to compare Shopee order exports (`.xlsx`) against shipping label PDFs, audit TikTok label PDFs, and run a mobile browser QR scan workflow across imported marketplace shop files.

## Chosen Stack

- Python `3.11.10` pinned via `pyenv`
- `pandas` for resilient Excel ingestion and aggregation
- `pdfplumber` for text extraction from label PDFs
- `openpyxl` for Excel workbook export
- `streamlit` for the internal upload/review/download UI
- `streamlit.components.v2` for the custom mobile QR scanner bridge
- Vendored browser-side `html5-qrcode` bundle for live QR decoding in the mobile web flow
- Standard library `argparse`, `csv`, `pathlib`, `zipfile`, `re`, `json`, `unittest`
- Custom lightweight PDF writer in pure Python for offline PDF report export

## Why This Stack

- Existing machine already has `pandas`, `openpyxl`, `pdfplumber`
- No external service dependency at runtime
- `pandas` reads the Shopee workbook correctly even when direct `openpyxl` read-only parsing is unreliable
- Pure-Python PDF export avoids dependency on `reportlab`, `weasyprint`, or system binaries
- `st.camera_input` is the wrong primitive for continuous scanning because it captures still images, so the mobile QR path uses a custom browser component instead
- Browser-side QR decode keeps raw video frames out of Python and reduces backend complexity

## Architecture

- `excel_loader`: read Shopee `.xlsx`, normalize headers, aggregate line items into order-level records
- `pdf_loader`: parse each PDF page into one label/order record
- `matcher`: compare by order id, validate waybill and item count
- `exporters`: write comparison report as CSV, XLSX, PDF
- `services`: shared compare/extract orchestration for CLI and Streamlit
- `cli`: terminal entrypoint, console summary rendering
- `marketplace_scan_importer`: read marketplace CSV/XLSX, detect headers, and build per-shop lookup registries
- `marketplace_qr_scan_matcher`: normalize scanned text, resolve hits, and block duplicates
- `mobile_qr_scanner_component`: browser camera UI and QR decode bridge for Streamlit V2
- `streamlit_app`: internal web entrypoint for upload/review/download and mobile scan

## Constraints

- PDF text extraction depends on current Shopee label text layout
- Recipient/address text in Shopee exports is masked, so comparison focuses on stable keys:
  `Mã đơn hàng`, `Mã vận đơn`, order datetime, total quantity, item summary
- PDF report export will be summary-style, not a visual copy of the original shipping label
- Streamlit scope stays local/internal only; no auth or hosted multi-user support
- Mobile browser camera access requires a secure context, so plain LAN HTTP is not a reliable rollout path
- Current mobile QR implementation uses a vendored local browser bundle, so scan-time browser network access is not required once the app page is loaded
