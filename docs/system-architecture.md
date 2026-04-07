# System Architecture

## Components

- `CLI`
  - parses arguments
  - prints progress summary
- `Streamlit App`
  - accepts local uploads
  - shows Shopee compare, item export, and TikTok PDF audit actions
  - shows metrics, tables, and download actions
- `Shared Services`
  - validate input paths
  - orchestrate compare, extract, and TikTok PDF audit workflows
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
```

## Design Choices

- `pandas` for Excel robustness
- `pdfplumber` for existing text-based labels
- Pillow-based PDF export to support Vietnamese Unicode without external PDF libraries
- Streamlit stays a thin UI wrapper; compare logic remains outside the UI layer
- TikTok audit groups by `order_id` instead of raw PDF page count because some labels spill onto a second page
