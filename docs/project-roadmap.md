# Project Roadmap

## Done In V1

- Terminal command `compare`
- Terminal command `extract-items`
- Shared workflow services for compare and extract flows
- Internal Streamlit web app for compare and item export
- TikTok Shop PDF audit tab that counts unique orders by `order_id`
- Mobile QR scan tab for phone browsers with multi-shop import, compare-field selection, deduped results, shop filters, and Excel export
- Excel aggregation by order id
- Item-level Shopee Excel export for warehouse/ops use
- PDF page parser
- Multi-page TikTok label collapsing with CSV/XLSX export
- Marketplace CSV/XLSX import registry with Lazada header detection and exact-after-normalization QR matching
- CSV, XLSX, PDF export
- Integration tests with sample files

## Next Likely Steps

- Add folder mode for batch compare
- Add configurable compare rules
- Add JSON export
- Add richer mismatch diagnostics for product lines
- Add OCR fallback for scanned PDFs
- Add a documented HTTPS/LAN deployment recipe for phone camera access
- Package Streamlit app for non-technical staff
