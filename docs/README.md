# Marketplace Ops Compare + Mobile QR Scan

## Overview

Offline-first Python tool for Shopee order audit plus a local Streamlit workflow for mobile QR scan across imported marketplace shop files.

- CLI remains available for scripted or terminal-first workflows
- Internal Streamlit app adds upload, review, and download flows for office users

## Features

- Read Shopee `.xlsx` exports
- Parse text-based label PDFs page-by-page
- Compare by `Mã đơn hàng`
- Validate `Mã vận đơn`, order datetime, and total quantity
- Export `comparison.csv`, `comparison.xlsx`, `comparison.pdf`
- Export item-level rows from Shopee Excel for warehouse/ops workflows
- Audit TikTok Shop label PDFs by grouped `order_id`
- Import repeated shop files from `Shopee`, `Lazada`, `TikTok`, and `Website`
- Choose one compare field per imported shop file
- Scan QR codes from a phone browser camera, dedupe hits, filter by shop, and export `.xlsx`
- Internal web UI via Streamlit for compare, extract-items, TikTok audit, and mobile QR scan flows

## Requirements

- `pyenv`
- Python `3.11.10`
- Packages in `requirements.txt`

## Setup

From the project root:

```bash
cd /Users/hunt2412/hieupvdev/project/automation-daily
pyenv install 3.11.10
pyenv local 3.11.10
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `.venv` already exists:

```bash
cd /Users/hunt2412/hieupvdev/project/automation-daily
source .venv/bin/activate
pip install -r requirements.txt
```

## Run CLI

```bash
python main.py compare \
  --excel "shopee/Order.all.order_creation_date.20260401_20260403.xlsx" \
  --pdf "shopee/SP Mollis (B4098) - 38 đơn - 03.04.2026.pdf" \
  --formats csv excel pdf

python main.py extract-items \
  --excel "shopee/Order.all.order_creation_date.20260402_20260406.xlsx" \
  --out-file "output/order-items.xlsx"
```

## Run Internal Web App

```bash
cd /Users/hunt2412/hieupvdev/project/automation-daily
source .venv/bin/activate
streamlit run streamlit_app.py
```

If `streamlit` is not found, run setup again and make sure the virtualenv is active.

Internal UI scope:

- Compare mode: upload one Excel + one PDF, review summary/table, download CSV/XLSX/PDF
- Extract-items mode: upload one Excel, preview rows, download CSV/XLSX
- TikTok PDF Audit: upload one TikTok label PDF, group repeated `order_id` values, download CSV/XLSX
- Mobile QR Scan: import one or more shop files, choose a compare field per shop, scan with a phone camera or manual fallback text, review a deduped table, filter by shop, download `.xlsx`

## Mobile QR Scan Notes

- Open the app from a secure URL. `HTTPS` is the reliable path. Plain `http://192.168.x.x:8501` is expected to fail camera access in most mobile browsers.
- On phones, the scanner auto-prefers the rear camera. On desktop browsers, users can keep the default webcam or choose another detected camera such as macOS Continuity Camera.
- The browser decodes the QR locally and only sends decoded text back to Python for matching.
- If one scan matches multiple imported rows, the scanner appends every newly matched row into the review table. A re-scan skips only rows that are already present in the review table.
- The QR decoder bundle is vendored locally inside the app, so the phone browser does not need to fetch `html5-qrcode` from a public CDN at scan time.

## Main Options

- `--excel`: path to Shopee Excel export
- `--pdf`: path to label PDF
- `--formats`: one or more of `csv`, `excel`, `pdf`
- `--out-dir`: target output directory
- `--only`: export only selected statuses: `matched`, `mismatch`, `missing-in-excel`, `missing-in-pdf`

## Extract Items Options

- `extract-items --excel`: path to Shopee Excel export
- `extract-items --format`: `excel` or `csv`
- `extract-items --out-file`: target output file, default `output/<timestamp>/order-items.<ext>`

## Output

- `comparison.csv`: flat comparison table
- `comparison.xlsx`: workbook with `comparison`, `excel_orders`, `pdf_orders`
- `comparison.pdf`: printable summary report
- `order-items.xlsx|csv`: item-level export with `Mã đơn hàng`, `Mã vật tư`, `Số lượng`, `Total Order`, `Ngày xử lý đơn hàng`, `Ngày xử lý đơn hàng detail`, `Ngày đặt hàng`
- `Total Order` trong `extract-items`: `Số lượng` của dòng chia cho tổng `Số lượng` trong cùng `Mã đơn hàng`
- `Ngày xử lý đơn hàng`: lấy `Ngày gửi hàng`, nếu không có thì lấy `Ngày xuất hàng`, nếu vẫn trống thì lấy `Thời gian giao hàng`, format `dd/mm/yyyy`
- `Ngày xử lý đơn hàng detail`: cùng nguồn dữ liệu, format `dd/mm/yyyy hh:mm`

## Current Matching Logic

- Join key: `Mã đơn hàng` lấy từ PDF
- Validation keys:
  - `Mã vận đơn`
  - order datetime
  - total quantity
  - item-level reconciliation giữa Excel và phần `Nội dung hàng` trong PDF

## Important Output Columns

- `excel_total_quantity`: tổng số lượng sản phẩm trong file order
- `pdf_total_quantity`: tổng số lượng khai báo trên phiếu PDF
- `pdf_visible_quantity`: tổng số lượng item parser nhìn thấy trong block `Nội dung hàng`
- `item_match_status`: `complete`, `partial`, `unclear`, `partial-and-unclear`
- `missing_excel_items`: item có trong file order nhưng không thấy đủ/không map chắc chắn từ PDF, mỗi item trên một dòng theo format `[SKU4 - Tên phân loại hàng - xSố lượng]`
- `unclear_pdf_items`: dòng item trong PDF không đủ rõ để map chắc chắn
- `excel_item_summary`: danh sách item đầy đủ từ file order để kho tra lại khi PDF bị cắt
- `pdf_item_summary`: nội dung item nhìn thấy được trong PDF

## Hidden Item Detection

Tool không chỉ đọc text layer. Nó còn kiểm tra layout vùng `Nội dung hàng` trên PDF.

- Nếu item cuối bị đè sang vùng `Người gửi phải cam kết...`, item đó được xem là bị cắt khỏi phiếu
- Item bị đánh dấu cắt layout sẽ luôn bị đưa vào `unclear_pdf_items`, kể cả khi text similarity với Excel vẫn cao
- Khi đó output sẽ lấy item đầy đủ từ Excel và ghi vào `missing_excel_items`
- `unclear_pdf_items` giữ lại phần item nhìn thấy được trên PDF để kho đối chiếu

Status meanings:

- `matched`: order exists in both sources and validations pass
- `mismatch`: order exists in both sources but at least one validation fails
- `missing-in-excel`: found in PDF but not in Excel
- `missing-in-pdf`: found in Excel but not in PDF

## Test

```bash
python -m unittest discover -s tests -v
```

## Limitations

- Streamlit app is local/internal only; no auth, hosting, or multi-user persistence
- PDF parser assumes text-based Shopee labels, not scanned images
- Excel export structure can change; required columns are validated explicitly
- Recipient data in Shopee Excel may be masked, so recipient is exported as reference only, not used as a compare key
- Mobile QR scan needs a secure browser context (`HTTPS` or trusted localhost)
- Imported shop registry and scan review rows live only in the active Streamlit session
