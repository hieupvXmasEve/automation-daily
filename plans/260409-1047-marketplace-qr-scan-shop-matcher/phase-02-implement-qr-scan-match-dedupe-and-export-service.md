# Phase 02: Build Mobile Camera QR Scanner Component And Match Service

## Context Links

- [Code Standards](../../docs/code-standards.md)
- [System Architecture](../../docs/system-architecture.md)
- [Phase 01](./phase-01-normalize-marketplace-imports-and-shop-registry.md)
- [Plan Overview](./plan.md)

## Overview

Priority: High
Status: Complete
Goal: build the browser camera QR scanner bridge plus the core service that resolves matches, blocks duplicates, and prepares exportable review rows.

## Key Insights

- `st.camera_input` is a still-image widget, not a continuous QR scanner, so it is the wrong primary tool for mobile scan UX.
- Streamlit V2 components support custom JavaScript without iframes, which is a better fit for browser camera APIs than older iframe-based components.
- Phone camera access in browsers needs a secure context, so plain `http://<LAN-IP>:8501` is not a reliable deployment target.
- Existing services already follow a clean request/result pattern; the QR feature should reuse that instead of pushing matching logic into Streamlit callbacks.
- The table must be append-only for successful unique scans but still surface duplicate, not-found, and ambiguous states immediately.
- "Thuoc shop nao" is a shop-resolution problem, not only a marketplace label problem, so each import must carry an explicit shop label.

## Requirements

- Request camera access from the mobile browser only after explicit user action
- Prefer the rear camera by default
- Decode QR continuously in the browser and send decoded text only to Python
- Pause scanning after one success to prevent repeated fires, then allow resume
- Keep manual text input as fallback when camera access is denied or unsupported
- Normalize the decoded text before lookup
- Search across all imported shops in the current session
- Return explicit statuses:
  - `matched`
  - `duplicate`
  - `not-found`
  - `ambiguous`
- Do not append a second row when the same resolved shop/order pair is scanned again
- Export the review table to Excel

## Architecture

- Add one Streamlit V2 component wrapper, for example `mobile_qr_scanner_component.py`, using `st.components.v2.component(html=..., js=...)`
- Use one client-side browser QR library, preferably `html5-qrcode`; do not depend on experimental `BarcodeDetector` as the primary path
- Keep the browser library pinned locally or vendored; avoid CDN-only runtime dependency because the app is meant to stay offline-friendly
- Add one service module, for example `marketplace_qr_scan_service.py`, with:
  - import-registry builder
  - scan resolver
  - dedupe guard
  - Excel export writer
- Recommended scan result row fields:
  - scanned_at
  - scanned_text
  - scan_source
  - marketplace
  - shop_label
  - compare_field
  - matched_value
  - source_order_reference
  - source_file
  - status
  - notes
- Recommended dedupe key:
  - `shop_id + compare_field + normalized_matched_value`

## Related Code Files

- Modify: `shopee_compare/streamlit_workflows.py`
- Modify: `shopee_compare/services/__init__.py`
- Create: `shopee_compare/mobile_qr_scanner_component.py`
- Create: `shopee_compare/marketplace_qr_scan_matcher.py`
- Create: `shopee_compare/services/marketplace_qr_scan_service.py`
- Modify: `tests/test_workflows.py`
- Create: `tests/test_marketplace_qr_scan_service.py`

## Implementation Steps

1. Add the V2 component wrapper with start, stop, and rescan event flow.
2. Start the browser camera with rear-camera preference and a mobile-friendly scan box.
3. Emit decoded text and scanner state back to Python, then pause scanning after a successful decode.
4. Add scan service request/result dataclasses.
5. Normalize decoded text and resolve candidates across all imported shops.
6. Mark zero-hit scans as `not-found` and multi-shop or multi-row collisions as `ambiguous`.
7. Append only unique resolved matches to the scan table.
8. Export the current review frame to `.xlsx` with stable columns.

## Todo List

- [x] Add V2 camera scanner component
- [x] Add scan service dataclasses
- [x] Implement match resolution and dedupe
- [x] Implement Excel export payload

## Success Criteria

- On a secure mobile URL, the camera opens and produces one decoded QR value on success
- Unique match returns one appendable review row
- Repeated scan of the same match returns `duplicate` and does not append
- Multi-hit scans return `ambiguous` with enough note text for ops review
- Exported Excel file opens with the same rows shown in the table

## Risk Assessment

- Risk: same tracking/order code appears in more than one imported shop
- Mitigation: never auto-pick on multi-hit; surface `ambiguous` and keep the scan table clean
- Risk: mobile browsers differ in camera selection and permission behavior
- Mitigation: default to `facingMode: environment`, but support explicit device selection if needed
- Risk: secure-context failures make camera look broken
- Mitigation: detect insecure context early and return a clear UI status instead of a silent failure

## Security Considerations

- Keep camera permission behind explicit user action
- Send decoded text to Python, not raw video frames, unless debugging forces a temporary exception
- Keep only session-local review rows
- Do not log full raw uploads or hidden columns unnecessarily
- Avoid formula injection by exporting through `pandas`/`openpyxl` with plain cell values only

## Next Steps

- Phase 03 wires the component and service into one mobile-friendly Streamlit tab
