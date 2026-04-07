---
title: "TikTok PDF Order Audit Tab"
description: "Add a Streamlit tab that parses TikTok Shop label PDFs by order id instead of raw PDF page count, then shows reviewable order details and exports."
status: completed
priority: P1
effort: 3h
branch: main
tags: [feature, python, streamlit, pdf, tiktok]
blockedBy: []
blocks: []
created: 2026-04-07
---

# TikTok PDF Order Audit Tab

## Overview

Add one TikTok-specific PDF audit flow to the existing Streamlit tool. The flow must group pages by `Order ID`, expose the real order count, list only the key fields needed for manual checking, and let ops export the parsed rows.

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Parse And Normalize TikTok PDF Orders](./phase-01-parse-and-normalize-tiktok-pdf-orders.md) | Completed |
| 2 | [Expose TikTok PDF Audit In Streamlit](./phase-02-expose-tiktok-pdf-audit-in-streamlit.md) | Completed |
| 3 | [Test, Verify, And Sync Docs](./phase-03-test-verify-and-sync-docs.md) | Completed |

## Dependency Graph

- Phase 2 blocked by Phase 1
- Phase 3 blocked by Phases 1 and 2

## Test Matrix

- Parser regression with the provided TikTok PDF fixture, including multi-page orders
- Streamlit workflow payload assertions for count, summary, and export data
- Verification: `python3 -m compileall .`
- Verification: `python3 -m unittest discover -s tests -v` -> 15 tests passed on 2026-04-07

## Success Criteria

- One uploaded TikTok PDF returns the real order count based on unique `order_id`
- Multi-page labels collapse into one order row with source page list preserved
- Streamlit shows summary metrics, review table, and download action without replacing current Shopee flows
- Export contains only key review columns
