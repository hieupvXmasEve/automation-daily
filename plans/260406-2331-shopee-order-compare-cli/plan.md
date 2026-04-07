---
title: "Shopee Order Compare CLI"
description: "Build a Python terminal app that compares Shopee Excel orders against label PDFs and exports CSV, Excel, and PDF reports."
status: completed
priority: P1
effort: 6h
branch: main
tags: [feature, backend, experimental]
blockedBy: []
blocks: []
created: 2026-04-06
---

# Shopee Order Compare CLI

## Overview

Build an offline Python CLI. Input: Shopee order export `.xlsx` and printed label `.pdf`. Output: comparison report as CSV, Excel, PDF. Use `pyenv` to pin Python runtime. Keep scope terminal-first.

## Cross-Plan Dependencies

| Relationship | Plan | Status |
|-------------|------|--------|
| None | - | - |

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Project Setup](./phase-01-project-setup.md) | Completed |
| 2 | [Parse And Normalize Sources](./phase-02-parse-and-normalize-sources.md) | Completed |
| 3 | [Compare Orders And Export Reports](./phase-03-compare-orders-and-export-reports.md) | Completed |
| 4 | [Test And Document](./phase-04-test-and-document.md) | Completed |

## Dependencies

- Local Python `3.11.10` via `pyenv`
- Existing local packages: `pandas`, `pdfplumber`, `openpyxl`
- Shopee export format remains text-based, not scanned-image PDF

## Success Criteria

- CLI runs with sample files in `shopee/`
- PDF pages parse into order ids and waybills
- Excel orders aggregate correctly from line-item rows
- Comparison report exports to CSV, XLSX, PDF
- Basic automated tests pass with sample data
