# Phase 01: Parse And Normalize TikTok PDF Orders

## Context Links

- [Code Standards](../../docs/code-standards.md)
- [System Architecture](../../docs/system-architecture.md)
- [Plan Overview](./plan.md)

## Overview

Priority: High
Status: Completed
Goal: parse TikTok Shop label PDFs into normalized order rows keyed by `order_id`, even when one order spans multiple pages.

## Key Insights

- The provided TikTok PDF has 12 pages but only 10 orders because two orders continue onto a second page.
- `Order ID` appears more than once per page, so parsing must dedupe within a page and aggregate across pages.
- Ops needs audit-friendly fields, not a full raw-text dump.

## Requirements

- Read TikTok PDF labels with `pdfplumber`
- Group records by `order_id`
- Keep page numbers or page span so users can cross-check source pages
- Return only key fields needed for manual verification

## Related Code Files

- Modify: `streamlit_app.py`
- Modify: `shopee_compare/streamlit_workflows.py`
- Modify: `shopee_compare/services/__init__.py`
- Create: `shopee_compare/tiktok_pdf_loader.py`
- Create: `shopee_compare/services/tiktok_pdf_service.py`
- Modify: `tests/test_workflows.py`
- Modify: `tests/test_compare.py`

## Implementation Steps

1. Add TikTok PDF dataclasses or row builders if existing models do not fit cleanly.
2. Parse each PDF page, extract key fields, and aggregate all pages under one `order_id`.
3. Build one shared workflow/service result that returns summary counts, preview rows, and export bytes.

## Todo List

- [x] Parse page-level TikTok fields
- [x] Aggregate page groups by order id
- [x] Build review-row export payload

## Success Criteria

- The provided TikTok PDF returns 10 unique orders from 12 pages
- Orders on pages 5-6 and 8-9 are merged correctly

## Risk Assessment

- Risk: text extraction layout shifts across sellers
- Mitigation: keep marker-based parsing explicit and fail fast on missing `Order ID`

## Security Considerations

- Avoid storing uploads outside temp workspaces
- Do not expose more PII than the review flow needs

## Next Steps

- Completed and wired into Streamlit
