# Phase 01: Normalize Marketplace Imports And Shop Registry

## Context Links

- [Code Standards](../../docs/code-standards.md)
- [Codebase Summary](../../docs/codebase-summary.md)
- [Design Guidelines](../../docs/design-guidelines.md)
- [Plan Overview](./plan.md)

## Overview

Priority: High
Status: Complete
Goal: turn uploaded shop files into one normalized registry that the scan workflow can search safely and consistently.

## Key Insights

- Current codebase has Shopee-specific parsing and one TikTok PDF parser, but no shared marketplace import contract.
- The app is local and session-based, so imported shops can live in `st.session_state` without adding persistence infrastructure.
- `data-example/lazada/orders.csv` shows Lazada exports can contain preamble rows before the real header, so import cannot assume header row `0` for every marketplace.
- Camera-based scanning changes the frontend, not the import contract; the compare dataset still needs one stable normalized lookup key per row.

## Requirements

- Accept repeated imports from multiple shops in one session
- Store per import: marketplace, shop label, source file name, compare field, available fields, row count
- Read both `.csv` and `.xlsx` where practical
- Normalize compare values so browser-decoded QR text and file values use the same matching rule
- Fail fast when the selected compare field is empty or missing across all rows

## Architecture

- Add one normalized dataset contract, for example `ImportedShopDataset`, with:
  - shop id
  - marketplace
  - shop label
  - source file name
  - available field list
  - selected compare field
  - normalized lookup rows
- Add one tabular import helper that:
  - reads CSV/XLSX
  - applies marketplace-specific header detection only where needed
  - preserves original columns for preview
  - builds normalized text keys with existing text utilities
  - preserves row identifiers and display fields needed after a successful scan
- Keep v1 matching rule exact-after-normalization:
  - trim
  - collapse whitespace
  - lowercase/ascii-fold
  - strip scanner control/newline noise

## Related Code Files

- Modify: `shopee_compare/utils.py`
- Modify: `shopee_compare/streamlit_workflows.py`
- Create: `shopee_compare/marketplace_scan_models.py`
- Create: `shopee_compare/marketplace_scan_importer.py`
- Modify: `tests/test_workflows.py`

## Implementation Steps

1. Add normalized dataclasses for imported shops and import preview payloads.
2. Implement CSV/XLSX import with one lightweight marketplace preset layer.
3. Return field options and a small preview frame so UI can ask the user to confirm the compare field before saving the shop.
4. Reject imports that do not produce at least one non-empty normalized compare value.

## Todo List

- [x] Define imported shop models
- [x] Implement generic tabular import
- [x] Add Lazada header-row detection
- [x] Add import preview and field option payload

## Success Criteria

- One imported shop produces a stable dataset id, field list, row count, and normalized lookup rows
- Shopee and generic CSV/XLSX inputs load without marketplace-specific hacks in the UI layer
- Lazada sample loads with the correct header row

## Risk Assessment

- Risk: column names vary across marketplace exports
- Mitigation: let the user choose the compare field from detected columns instead of hardcoding one field
- Risk: normalized values collide across rows in the same shop file
- Mitigation: preserve source row metadata so ambiguous hits can be reported, not silently auto-picked

## Security Considerations

- Keep uploads inside the existing temp workspace flow
- Do not persist full source files outside the active session
- Preserve only the minimum display fields needed for review

## Next Steps

- Phase 02 adds the browser camera scanner bridge and match service on top of the imported shop registry
