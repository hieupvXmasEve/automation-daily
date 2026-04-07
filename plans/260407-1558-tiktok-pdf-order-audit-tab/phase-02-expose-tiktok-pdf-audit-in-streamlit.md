# Phase 02: Expose TikTok PDF Audit In Streamlit

## Context Links

- [Plan Overview](./plan.md)
- [Phase 01](./phase-01-parse-and-normalize-tiktok-pdf-orders.md)

## Overview

Priority: High
Status: Completed
Goal: add one new Streamlit tab for TikTok PDF upload, count metrics, detailed order review, and export.

## Requirements

- Add one separate tab so existing Shopee flows stay intact
- Show total pages, unique orders, multi-page orders, and total product quantity
- Show a compact table with the key order fields only
- Provide download action for CSV/XLSX

## Implementation Steps

1. Add TikTok PDF uploader and run action.
2. Persist the result in `st.session_state`.
3. Render metrics, review table, and download buttons.

## Todo List

- [x] Add Streamlit tab
- [x] Add result rendering
- [x] Add download actions

## Success Criteria

- Internal users can audit a TikTok PDF without counting pages manually
