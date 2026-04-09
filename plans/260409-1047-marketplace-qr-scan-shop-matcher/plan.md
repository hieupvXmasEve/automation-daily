---
title: "Mobile Web Camera QR Shop Matcher"
description: "Use a phone camera in the Streamlit web app to scan QR codes on a secure mobile URL, match them against imported shop files, dedupe results, and export Excel."
status: in_progress
priority: P1
effort: 14h
branch: main
tags: [feature, python, streamlit, qr, mobile-web]
blockedBy: []
blocks: []
created: 2026-04-09
---

# Mobile Web Camera QR Shop Matcher

## Overview

Add one internal mobile-friendly Streamlit workflow that users open on a phone over a secure URL, grant camera access, scan QR codes with the rear camera, resolve the code against imported shop files, keep a deduped review table, filter by shop, and export Excel.

## Scope

- Mobile web camera scan via browser, not scanner keyboard input
- Streamlit V2 custom component plus client-side QR decode
- Secure origin required: HTTPS or trusted localhost; plain LAN HTTP is out
- Supports Shopee, Lazada, TikTok, and Website imports
- Keep optional manual text fallback for unsupported browsers or denied permission
- Export filtered review table to `.xlsx`

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Normalize Marketplace Imports And Shop Registry](./phase-01-normalize-marketplace-imports-and-shop-registry.md) | Complete |
| 2 | [Build Mobile Camera QR Scanner Component And Match Service](./phase-02-implement-qr-scan-match-dedupe-and-export-service.md) | Complete |
| 3 | [Modularize Streamlit And Add Mobile QR Scan Tab](./phase-03-modularize-streamlit-and-add-qr-scan-tab.md) | Complete |
| 4 | [Test, Document, And Secure Mobile Access Rollout](./phase-04-test-document-and-sync-roadmap.md) | In Progress |

## Dependency Graph

- Phase 2 blocked by Phase 1
- Phase 3 blocked by Phases 1 and 2
- Phase 4 blocked by Phases 1, 2, and 3
- No CLI impact planned in v1

## Compatibility Strategy

- Keep `compare`, `extract-items`, and `TikTok PDF Audit` unchanged
- Keep `streamlit run streamlit_app.py` as the entrypoint
- Use `st.components.v2.component`; do not use `st.camera_input` as the primary scanner because it captures still images, not continuous scan events
- Extract UI code so `streamlit_app.py` stays below repo file-size limits
- No full frontend rewrite, OCR pipeline, hosted storage, or database work in v1

## Test Matrix

- Import parsing for Shopee, Lazada, and generic CSV/XLSX inputs
- Python match engine: unique match, duplicate scan, not found, ambiguous cross-shop match
- Browser component contract plus manual Android Chrome and iPhone Safari scan smoke over HTTPS
- Negative smoke on insecure HTTP to confirm user guidance path
- Streamlit workflow payloads for imported shops, scan table updates, filters, and Excel export bytes
- Verification: `python -m compileall .`
- Verification: `python -m unittest discover -s tests -v`

## Success Criteria

- Ops can import multiple shops in one session, each with marketplace, shop label, compare field, and file metadata
- A phone user can open a secure URL, grant camera permission, and see a rear-camera QR scanner
- One scanned QR text resolves to `matched`, `duplicate`, `not-found`, or `ambiguous`
- Duplicate scans do not append a second success row
- Review table filters by shop and exports to Excel
- Existing compare, extract, and TikTok audit flows remain stable

## Assumptions And Open Questions

- Assumption: v1 will use a browser QR library such as `html5-qrcode` inside a locally packaged Streamlit V2 component; Python receives decoded text, not raw video frames
- Assumption: TikTok and Website start with generic CSV/XLSX import unless a real fixture forces marketplace-specific parsing
- Assumption: the app will be exposed to phones through one secure URL path controlled by ops
- Open question: which secure path should be standardized for rollout: LAN reverse proxy with HTTPS, tunnel, or hosted internal domain?
