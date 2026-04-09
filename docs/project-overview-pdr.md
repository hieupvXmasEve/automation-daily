# Product Development Requirements

## Problem

Ops needs one local tool to verify Shopee order exports against printed labels and to resolve QR codes against imported marketplace shop files during mobile warehouse handling.

## Users

- Warehouse staff
- Operations staff
- Shop owner/admin

## Inputs

- Shopee Excel export
- Shipping label PDF
- Marketplace shop files in `csv` or `xlsx`
- Decoded QR text from a mobile browser camera or manual fallback input

## Outputs

- CSV comparison report
- Excel workbook report
- PDF printable report
- Excel scan review table filtered by shop when needed

## Functional Requirements

- Run locally from terminal
- Run locally from an internal web UI
- Accept explicit file paths
- Compare orders by order id
- Highlight missing and mismatched orders
- Export reports to a chosen directory
- Import multiple shop files in one Streamlit session
- Let the user choose one compare field per imported shop file
- Scan QR codes from a phone browser camera
- Resolve the scanned text to the matching shop and source row
- Prevent duplicate scan rows from being appended twice
- Filter review rows by shop and export them to Excel

## Non-Functional Requirements

- Offline-friendly
- CLI remains available
- Web UI stays internal-only and local-first
- Clear error messages
- Deterministic output for the same input
- Mobile camera path requires a secure browser context
- Imported shop registry and scan rows stay session-local

## V1 Out Of Scope

- OCR
- Persistent multi-user storage
- Native mobile app or scanner-hardware SDK integration
- Direct Shopee API integration
- Public deployment or authentication system
