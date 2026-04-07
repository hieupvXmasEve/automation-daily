# Tech Stack

## Overview

CLI Python app to compare Shopee order exports (`.xlsx`) against shipping label PDFs and export a comparison report as CSV, Excel, or PDF.

## Chosen Stack

- Python `3.11.10` pinned via `pyenv`
- `pandas` for resilient Excel ingestion and aggregation
- `pdfplumber` for text extraction from label PDFs
- `openpyxl` for Excel workbook export
- Standard library `argparse`, `csv`, `pathlib`, `zipfile`, `re`, `json`, `unittest`
- Custom lightweight PDF writer in pure Python for offline PDF report export

## Why This Stack

- Existing machine already has `pandas`, `openpyxl`, `pdfplumber`
- No network/package install required to get the MVP running
- `pandas` reads the Shopee workbook correctly even when direct `openpyxl` read-only parsing is unreliable
- Pure-Python PDF export avoids dependency on `reportlab`, `weasyprint`, or system binaries

## Architecture

- `excel_loader`: read Shopee `.xlsx`, normalize headers, aggregate line items into order-level records
- `pdf_loader`: parse each PDF page into one label/order record
- `matcher`: compare by order id, validate waybill and item count
- `exporters`: write comparison report as CSV, XLSX, PDF
- `cli`: terminal entrypoint, output directory handling, summary rendering

## Constraints

- PDF text extraction depends on current Shopee label text layout
- Recipient/address text in Shopee exports is masked, so comparison focuses on stable keys:
  `Mã đơn hàng`, `Mã vận đơn`, order datetime, total quantity, item summary
- PDF report export will be summary-style, not a visual copy of the original shipping label
