# Phase 01: Extract Shared Workflows

## Context Links

- [Docs README](../../docs/README.md)
- [System Architecture](../../docs/system-architecture.md)
- [Research Report](../reports/researcher-260407-1145-streamlit-ui-flow.md)
- [CLI](../../shopee_compare/cli.py)

## Overview

Priority: High
Status: Completed
Goal: move compare and extract orchestration out of the CLI so both CLI and Streamlit call the same workflow layer.

## Key Insights

- Current core logic is already separated into loaders, matcher, exporters, and item export builder.
- The CLI currently mixes argument parsing, orchestration, and console rendering.
- Lowest-risk path is additive: keep parser surface stable and refactor only the glue code.

## Requirements

- Preserve CLI command names, flags, default output naming, and exit behavior.
- Add one shared compare workflow and one shared extract workflow returning summary data plus artifact paths.
- Keep new modules small; split helpers if a file trends past 200 lines.
- Fail fast on missing files, invalid output selections, and unwritable output locations.

## Architecture

Data flow:
1. CLI or Streamlit passes validated `Path` inputs and output preferences into workflow functions.
2. Workflow loads source records, runs compare or item export, writes artifacts, and returns a result payload.
3. CLI prints compact terminal output from that payload; Streamlit renders metrics, tables, and downloads from the same payload.

Components:
- `shopee_compare/cli.py`: argument parsing and terminal presentation only
- `shopee_compare/services/compare_service.py`: shared compare orchestration
- `shopee_compare/services/extract_items_service.py`: shared extract orchestration
- Existing loaders, matcher, exporters, and `order_item_export.py`: unchanged source-of-truth logic

## File Ownership

- Owns: `shopee_compare/cli.py`
- Owns: `shopee_compare/services/compare_service.py`
- Owns: `shopee_compare/services/extract_items_service.py`
- Owns: `shopee_compare/services/__init__.py`
- Does not touch Streamlit files, tests, or docs

## Related Code Files

- Modify: `shopee_compare/cli.py`
- Create: `shopee_compare/services/compare_service.py`
- Create: `shopee_compare/services/extract_items_service.py`
- Create: `shopee_compare/services/__init__.py`

## Implementation Steps

1. Define workflow input and output contracts for compare and extract-items.
2. Move orchestration from CLI handlers into shared functions.
3. Rewire CLI handlers to call shared workflows and keep existing terminal text concise.
4. Verify default artifact names and format-selection behavior remain unchanged.

## Todo List

- [x] Add shared compare workflow
- [x] Add shared extract workflow
- [x] Rewire CLI handlers
- [x] Smoke-check both CLI commands via `unittest`

## Success Criteria

- `python main.py compare ...` still returns `0` and writes `comparison.csv`, `comparison.xlsx`, `comparison.pdf`
- `python main.py extract-items ...` still returns `0` and writes `order-items.xlsx|csv`
- Shared workflow payload exposes enough data for a web UI without reparsing exported files

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CLI defaults drift during refactor | Medium | High | Keep parser unchanged and reuse current filenames and summary keys |
| Shared workflow module grows too large | Medium | Medium | Split only path/result helpers into one extra module if needed |
| Export side effects change unexpectedly | Low | High | Keep loaders, matcher, and exporters untouched unless a defect is proven |

## Security Considerations

- Treat input paths as local files only
- Keep exports inside caller-provided output dirs
- Do not add network calls or shell interpolation

## Rollback Plan

- Restore direct orchestration inside `shopee_compare/cli.py`
- Remove or stop importing `shopee_compare/services/`
- No data migration or persistent state cleanup required

## Next Steps

- Result: done
