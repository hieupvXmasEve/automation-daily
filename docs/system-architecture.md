# System Architecture

## Components

- `CLI`
  - parses arguments
  - creates output directory
  - prints progress summary
- `Excel Loader`
  - reads Shopee workbook
  - groups line items into order records
- `PDF Loader`
  - parses one order per PDF page
  - extracts order id, waybill, datetime, quantity, recipient
- `Matcher`
  - joins records by order id
  - computes status and summary counts
- `Exporters`
  - write CSV, XLSX, PDF outputs

## Flow

```text
Excel -> normalize ----\
                         -> compare -> exporters -> files
PDF   -> normalize ----/
```

## Design Choices

- `pandas` for Excel robustness
- `pdfplumber` for existing text-based labels
- Pillow-based PDF export to support Vietnamese Unicode without external PDF libraries
