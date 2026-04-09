# Internal Tool Design Guidelines

## Goal

Build a local tool for warehouse/ops use. Fast input. Low ceremony. Clear file outputs. Keep both CLI and internal web UI thin over the same compare core.

## Interaction Model

- One primary command: `compare`
- Required inputs: `--excel`, `--pdf`
- Optional outputs: `--formats csv excel pdf`
- Optional filters: `--only matched|mismatch|missing-in-excel|missing-in-pdf`
- Default output folder: `output/{timestamp}`
- One internal web app entrypoint: `streamlit run streamlit_app.py`
- Web app should use explicit submit buttons, read-only tables, metric cards, and download buttons
- Web app now has four operator surfaces:
  - Shopee compare
  - Shopee item export
  - TikTok PDF audit
  - mobile QR scan
- Mobile QR scan should keep import, save-shop, start-camera, rescan, and export as separate explicit actions

## UX Rules

- Print a compact preflight summary before processing
- Fail fast on unreadable files with direct error messages
- Show a final terminal summary:
  total excel orders, total pdf labels, matched, mismatched, missing
- Print exact paths of exported files
- In Streamlit, run heavy work only after explicit submit
- In Streamlit, keep last successful result in session state
- In Streamlit, prefer read-only review via `st.dataframe`
- In mobile scan UX, show secure-origin guidance before users assume the camera is broken
- In mobile scan UX, pause after one successful QR decode and require explicit resume to avoid repeated duplicate fires
- In mobile scan UX, keep a manual text fallback visible when camera access fails
- Keep text ASCII-friendly where possible, but preserve Vietnamese data content

## Matching Rules

- Primary key: `Mã đơn hàng`
- Secondary validation: `Mã vận đơn`
- Derived checks:
  - total quantity from Excel vs total quantity from PDF
  - order datetime from Excel vs PDF order date/time
  - item summary similarity as informational note
- For marketplace QR scan:
  - compare key is the user-selected field per imported shop
  - match rule is exact after normalization
  - one scan can append multiple matched rows into the review table
  - result states are `matched`, `duplicate`, `not-found`

## Output Rules

- CSV: flat comparison table, UTF-8 with BOM for Excel compatibility
- Excel: workbook with sheets `comparison`, `excel_orders`, `pdf_orders`
- PDF: concise printable audit summary and comparison rows
- Mobile QR scan export: one flat `.xlsx` review table with scanned text, shop, compare field, source reference, status, and notes

## Non-Goals For V1

- OCR for scanned PDFs
- Auto-download from Shopee
- Pixel-perfect regeneration of original shipping labels
- Public-facing hosted web product
- Native mobile app rewrite
- Browser image upload as a replacement for live QR camera scan
