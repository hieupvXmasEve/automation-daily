# System Architecture

## Components

- `CLI`
  - parses arguments
  - prints progress summary
- `Streamlit App`
  - accepts local uploads
  - shows Shopee compare, item export, TikTok PDF audit, and mobile QR scan actions
  - shows metrics, tables, and download actions
- `Shared Services`
  - validate input paths
  - orchestrate compare, extract, TikTok PDF audit, and marketplace QR scan workflows
  - create output artifacts for CLI and UI
- `Excel Loader`
  - reads Shopee workbook
  - groups line items into order records
- `PDF Loader`
  - parses one order per PDF page
  - extracts order id, waybill, datetime, quantity, recipient
- `TikTok PDF Loader`
  - parses TikTok label pages
  - groups repeated `order_id` values across multiple pages into one order row
  - keeps source page list for manual ops checking
- `Marketplace Importer`
  - reads `csv` or `xlsx` shop files
  - detects Lazada pre-header rows where needed
  - builds one normalized lookup registry per imported shop and compare field
- `Mobile QR Scanner Component`
  - runs in the browser via Streamlit V2 custom components
  - requests rear-camera access on explicit user action
  - decodes QR in the browser and sends decoded text only to Python
- `Marketplace QR Match Service`
  - normalizes scanned text
  - searches across imported shops in session state
  - returns `matched`, `duplicate`, `not-found`, or `ambiguous`
  - prepares filtered Excel export rows
- `Matcher`
  - joins records by order id
  - computes status and summary counts
- `Exporters`
  - write CSV, XLSX, PDF outputs

## Flow

```text
CLI / Streamlit -> shared services -> normalize Excel ----\
                                                           -> compare -> exporters -> files
CLI / Streamlit -> shared services -> normalize PDF   ----/
Streamlit -> shared services -> normalize TikTok PDF -> grouped order audit -> CSV/XLSX
Streamlit mobile tab -> marketplace importer -> imported shop registry -> QR match service -> review table/XLSX
Phone browser camera -> V2 QR component -> decoded QR text -----------/
```

## Design Choices

- `pandas` for Excel robustness
- `pdfplumber` for existing text-based labels
- Pillow-based PDF export to support Vietnamese Unicode without external PDF libraries
- Streamlit stays a thin UI wrapper; compare logic remains outside the UI layer
- TikTok audit groups by `order_id` instead of raw PDF page count because some labels spill onto a second page
- Mobile scan uses a Streamlit V2 component because `st.camera_input` captures still images, not continuous QR scan events
- QR decoding stays in the browser so Python receives decoded text instead of raw video frames
- Mobile rollout must use a secure URL because browser camera APIs do not behave reliably on plain LAN HTTP
