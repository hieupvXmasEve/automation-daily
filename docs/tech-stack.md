# Tech Stack

## Overview

Python app with CLI and internal Streamlit entrypoints to compare Shopee order exports (`.xlsx`) against shipping label PDFs and export a comparison report as CSV, Excel, or PDF.

## Chosen Stack

- Python `3.11.10` pinned via `pyenv`
- `pandas` for resilient Excel ingestion and aggregation
- `pdfplumber` for text extraction from label PDFs
- `openpyxl` for Excel workbook export
- `streamlit` for the internal upload/review/download UI
- Standard library `argparse`, `csv`, `pathlib`, `zipfile`, `re`, `json`, `unittest`
- Custom lightweight PDF writer in pure Python for offline PDF report export

## Why This Stack

- Existing machine already has `pandas`, `openpyxl`, `pdfplumber`
- No external service dependency at runtime
- `pandas` reads the Shopee workbook correctly even when direct `openpyxl` read-only parsing is unreliable
- Pure-Python PDF export avoids dependency on `reportlab`, `weasyprint`, or system binaries

## Architecture

- `excel_loader`: read Shopee `.xlsx`, normalize headers, aggregate line items into order-level records
- `pdf_loader`: parse each PDF page into one label/order record
- `matcher`: compare by order id, validate waybill and item count
- `exporters`: write comparison report as CSV, XLSX, PDF
- `services`: shared compare/extract orchestration for CLI and Streamlit
- `cli`: terminal entrypoint, console summary rendering
- `streamlit_app`: internal web entrypoint for upload/review/download

## Constraints

- PDF text extraction depends on current Shopee label text layout
- Recipient/address text in Shopee exports is masked, so comparison focuses on stable keys:
  `Mã đơn hàng`, `Mã vận đơn`, order datetime, total quantity, item summary
- PDF report export will be summary-style, not a visual copy of the original shipping label
- Streamlit scope stays local/internal only; no auth or hosted multi-user support
