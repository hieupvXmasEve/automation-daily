# Phase 03: Modularize Streamlit And Add Mobile QR Scan Tab

## Context Links

- [Design Guidelines](../../docs/design-guidelines.md)
- [System Architecture](../../docs/system-architecture.md)
- [Phase 01](./phase-01-normalize-marketplace-imports-and-shop-registry.md)
- [Phase 02](./phase-02-implement-qr-scan-match-dedupe-and-export-service.md)
- [Plan Overview](./plan.md)

## Overview

Priority: High
Status: Complete
Goal: expose the mobile camera QR workflow in Streamlit without letting the entrypoint file grow past repo limits or mixing UI state with business logic.

## Key Insights

- `streamlit_app.py` is already `196` lines, so adding one more feature directly will break the repo file-size rule.
- Existing UX pattern is explicit submit, session-state persistence, metrics, read-only tables, and download buttons.
- Mobile scanning needs one full-width camera area, large actions, and clear permission/error guidance.
- This feature needs two session collections:
  - imported shop registry
  - deduped scan result rows

## Requirements

- Add one new tab for QR scan workflow
- Keep existing compare, extract, and TikTok tabs stable
- Let users:
  - import a shop file
  - choose marketplace and shop label
  - choose one compare field
  - start the phone camera and scan one code at a time
  - review status feedback
  - filter by shop
  - export the filtered table
  - fall back to manual text input if camera access fails
  - clear scan table or reset imported shops

## Architecture

- Refactor UI so `streamlit_app.py` becomes a thin entrypoint only
- Move existing tab renderers into one dedicated module
- Place the new QR tab renderer in its own module because it will carry separate state and actions
- Keep the camera component wrapper separate from the tab renderer so camera lifecycle code does not leak into page layout code
- Keep all file parsing, matching, and export logic inside workflow/service modules

## Related Code Files

- Modify: `streamlit_app.py`
- Modify: `shopee_compare/streamlit_workflows.py`
- Create: `shopee_compare/streamlit_existing_tabs.py`
- Create: `shopee_compare/streamlit_marketplace_qr_scan_tab.py`
- Modify: `tests/test_workflows.py`

## Implementation Steps

1. Extract current compare/extract/TikTok tab rendering from `streamlit_app.py`.
2. Add QR scan tab renderer with:
   - import form
   - imported shops table
   - camera scanner area
   - manual input fallback
   - status banner
   - filter controls
   - result table
   - export button
3. Render permission denied, insecure-context, and unsupported-browser guidance states.
4. Keep all state keys explicit and namespaced.
5. Add reset actions so local ops can start a clean session without restarting Streamlit.

## Todo List

- [x] Slim down `streamlit_app.py`
- [x] Add mobile QR scan tab renderer
- [x] Add camera guidance and manual fallback UX
- [x] Add session-state keys and reset actions
- [x] Add filtered Excel download button

## Success Criteria

- Streamlit shows four tabs with the new QR scan flow added
- Existing tabs render and behave the same as before
- QR scan tab can import shops, scan codes from the phone camera, show results, filter by shop, and export to Excel
- The tab gives a clear fallback path when camera permission is denied or the page is not served from a secure origin
- `streamlit_app.py` drops below the current near-limit size

## Risk Assessment

- Risk: Streamlit reruns clear intermediate state unexpectedly
- Mitigation: keep registry and result table in explicit `st.session_state` keys and never recompute from widget-local variables only
- Risk: camera state gets out of sync after a Streamlit rerun
- Mitigation: keep camera lifecycle inside the component and communicate only stable status events to Python
- Risk: import and scan actions become confusing in one screen
- Mitigation: separate them into clear sections with independent submit buttons

## Security Considerations

- Keep all data local to the running Streamlit session
- Do not display more columns than needed in the scan review table
- Keep download actions explicit; never auto-write user files outside temp/output flow

## Next Steps

- Phase 04 locks coverage and updates docs
