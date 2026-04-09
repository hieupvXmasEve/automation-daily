# Phase 04: Test, Document, And Secure Mobile Access Rollout

## Context Links

- [Docs README](../../docs/README.md)
- [Docs README VI](../../docs/README.vi.md)
- [Project Roadmap](../../docs/project-roadmap.md)
- [Codebase Summary](../../docs/codebase-summary.md)
- [System Architecture](../../docs/system-architecture.md)
- [Phase 01](./phase-01-normalize-marketplace-imports-and-shop-registry.md)
- [Phase 02](./phase-02-implement-qr-scan-match-dedupe-and-export-service.md)
- [Phase 03](./phase-03-modularize-streamlit-and-add-qr-scan-tab.md)

## Overview

Priority: Medium
Status: In Progress
Goal: prove the mobile camera QR workflow is stable, then update product and architecture docs so future work starts from the correct baseline.

## Key Insights

- Current docs still frame the product as Shopee-first and single-workflow-oriented, so they will drift immediately if the new QR scan flow ships without updates.
- Tests must not depend on personal local files in `~/Downloads`; this feature needs repo-local fixtures or temp-generated tables.
- Export validation matters because Excel is part of the requested user-facing outcome, not a side effect.
- Camera scan cannot be fully trusted from Python-only tests; the plan needs an explicit manual mobile smoke matrix over a secure URL.

## Requirements

- Add automated coverage for import parsing, scan matching, dedupe, filter, and export
- Keep existing unittest suite green
- Update docs to explain the new QR scan workflow, secure URL requirement, and marketplace assumptions
- Update roadmap and overview docs to reflect multi-marketplace support in progress

## Architecture

Test matrix:
- importer tests with small synthetic CSV/XLSX fixtures
- service tests for `matched`, `duplicate`, `not-found`, `ambiguous`
- workflow tests for export bytes and filtered row counts
- manual Streamlit smoke on Android Chrome and iPhone Safari over HTTPS with at least two imported shops and one duplicate scan
- manual negative smoke on insecure HTTP so the warning path is verified

Docs impact:
- `docs/README.md`
- `docs/README.vi.md`
- `docs/project-overview-pdr.md`
- `docs/system-architecture.md`
- `docs/codebase-summary.md`
- `docs/design-guidelines.md`
- `docs/project-roadmap.md`
- `docs/tech-stack.md`

## Related Code Files

- Create: `tests/test_marketplace_qr_scan_service.py`
- Modify: `tests/test_workflows.py`
- Modify: `docs/README.md`
- Modify: `docs/README.vi.md`
- Modify: `docs/project-overview-pdr.md`
- Modify: `docs/system-architecture.md`
- Modify: `docs/codebase-summary.md`
- Modify: `docs/design-guidelines.md`
- Modify: `docs/project-roadmap.md`
- Modify: `docs/tech-stack.md`

## Implementation Steps

1. Add focused tests for importer edge cases and scan statuses.
2. Run `python -m compileall .` and `python -m unittest discover -s tests -v`.
3. Run manual mobile smoke over a secure URL: grant permission, scan success, duplicate, denied permission, and insecure HTTP guidance.
4. Update docs after final UI labels, secure access path, and scan statuses settle.
5. Mark roadmap and plan status only after verification passes.

## Todo List

- [x] Add importer and scan service tests
- [x] Run compile verification
- [x] Run full unittest suite
- [ ] Run secure mobile smoke test
- [x] Update docs and roadmap

## Success Criteria

- Automated tests cover the new import and scan paths
- A phone user can scan successfully from a secure mobile URL
- Excel export opens and matches the filtered review table columns
- Docs explain how to import shops, choose compare fields, scan codes, expose the app over a secure URL, and export the result table
- Roadmap reflects the new QR scan feature accurately

## Risk Assessment

- Risk: tests become brittle because Excel fixtures are too large or seller-specific
- Mitigation: keep fixtures tiny and synthetic where possible
- Risk: staff open the app over plain HTTP and conclude the camera feature is broken
- Mitigation: document secure-origin requirements and add in-app guidance for insecure access
- Risk: docs imply OCR/image-upload support that does not exist
- Mitigation: explicitly state browser camera QR scan only

## Security Considerations

- Keep test data synthetic or already-sanitized
- Do not store raw camera frames in fixtures, exports, or logs
- Do not introduce hidden persistence or multi-user assumptions in docs
- Reuse existing temp-workspace pattern for uploaded files

## Next Steps

- Resolve the Website schema question if a real fixture exists; otherwise ship with generic import guidance
