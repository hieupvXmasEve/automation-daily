---
title: "Shopee Compare Internal Streamlit Web App"
description: "Add an internal Streamlit UI on top of the existing Shopee compare CLI without changing CLI behavior."
status: completed
priority: P1
effort: 6h
branch: main
tags: [feature, python, streamlit, internal-tool]
blockedBy: []
blocks: []
created: 2026-04-07
---

# Shopee Compare Internal Streamlit Web App

## Overview

Add one internal Streamlit app for upload -> run -> review -> download while keeping the current CLI fully supported. Reuse loaders, matcher, exporters, and item-export logic. Extract only orchestration into shared workflow code so CLI and web UI stay consistent.

## Cross-Plan Dependencies

| Relationship | Plan | Status |
|-------------|------|--------|
| None | - | - |

## Phases

| Phase | Name | Status |
|-------|------|--------|
| 1 | [Extract Shared Workflows](./phase-01-extract-shared-workflows.md) | Completed |
| 2 | [Build Streamlit Internal Web App](./phase-02-build-streamlit-internal-web-app.md) | Completed |
| 3 | [Test, Document, And Roll Out](./phase-03-test-document-and-roll-out.md) | Completed |

## Dependency Graph

- Phase 2 blocked by Phase 1
- Phase 3 blocked by Phases 1 and 2
- No parallel file overlap planned across phases

## Compatibility Strategy

- Keep `python main.py compare ...` and `python main.py extract-items ...` flags, defaults, outputs, and exit behavior stable
- Keep `streamlit run streamlit_app.py` additive; no CLI replacement
- No parser, matcher, or exporter rewrite unless shared-workflow extraction exposes a defect
- No data migration; all artifacts remain local files

## Test Matrix

- Shared orchestration: compare and extract workflow tests with real fixtures and temp output dirs
- CLI regression: keep existing command tests green after workflow extraction
- Web app smoke: manual run with one Excel and one PDF, verify metrics, table render, and download buttons

## Success Criteria

- Internal users can upload one Excel and one PDF, run compare, review summary plus result rows, and download generated CSV, XLSX, and PDF
- Internal users can upload one Excel, export item rows, review row count, and download generated CSV or XLSX
- CLI behavior stays stable against existing tests and sample files
- Docs explain both entrypoints and roadmap reflects the internal web app track
- Each phase has a rollback path with no cascading damage
- Verification: `python -m compileall .`
- Verification: `python -m unittest discover -s tests -v` -> 11 tests passed on 2026-04-07
