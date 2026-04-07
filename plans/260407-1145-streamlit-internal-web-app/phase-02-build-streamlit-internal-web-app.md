# Phase 02: Build Streamlit Internal Web App

## Context Links

- [Docs README](../../docs/README.md)
- [Code Standards](../../docs/code-standards.md)
- [CLI Flow Wireframe](../../docs/wireframe/cli-flow.md)
- [Phase 01](./phase-01-extract-shared-workflows.md)
- [Research Report](../reports/researcher-260407-1145-streamlit-ui-flow.md)

## Overview

Priority: High
Status: Completed
Goal: add an internal Streamlit UI for compare and extract-items without duplicating business logic or replacing the CLI.

## Key Insights

- `st.file_uploader` keeps uploaded data in memory for the current session, so uploads should be copied to temp files immediately.
- Streamlit reruns on interaction, so heavy work should run only from an explicit button and persist results in `st.session_state`.
- V1 scope stays narrow: one Excel, one PDF, internal users only, no batch mode, no OCR, no auth redesign.

## Requirements

- Compare mode: upload one Excel and one PDF, choose export formats, run compare, review summary and result rows, download generated CSV/XLSX/PDF.
- Extract-items mode: upload one Excel, run export, review row count and preview rows, download generated CSV/XLSX.
- Keep UI additive; the CLI remains documented and supported.
- Keep modules small; do not let `streamlit_app.py` become a second business-logic hub.

## Architecture

Data flow:
1. `streamlit_app.py` receives uploaded files and user options.
2. `shopee_compare/streamlit_workflows.py` saves uploads into a per-run temp directory and invokes shared workflows from Phase 01.
3. Workflow returns summary data, preview rows, and artifact paths.
4. The app stores the latest payload in `st.session_state`, then renders metrics, tables, and download buttons from that payload.

Components:
- `streamlit_app.py`: layout, widgets, mode switch, result rendering
- `shopee_compare/streamlit_workflows.py`: temp-file handling, workflow invocation, result packaging for the UI
- `shopee_compare/services/upload_workspace.py`: temp upload workspace helper
- `requirements.txt`: Streamlit dependency

## File Ownership

- Owns: `streamlit_app.py`
- Owns: `shopee_compare/streamlit_workflows.py`
- Owns: `shopee_compare/services/upload_workspace.py`
- Owns: `requirements.txt`
- Does not edit CLI/tests/docs files owned by other phases

## Related Code Files

- Create: `streamlit_app.py`
- Create: `shopee_compare/streamlit_workflows.py`
- Create: `shopee_compare/services/upload_workspace.py`
- Modify: `requirements.txt`

## Implementation Steps

1. Add the Streamlit runtime dependency using the smallest repo change that keeps local setup clear.
2. Build compare mode around uploaded Excel/PDF -> shared workflow -> metrics/table/downloads.
3. Build extract-items mode around uploaded Excel -> shared workflow -> preview/download.
4. Persist the latest successful run in `st.session_state` and keep temp artifacts addressable for downloads.

## Todo List

- [x] Add Streamlit dependency
- [x] Add uploaded-file temp storage helper
- [x] Build compare mode UI
- [x] Build extract-items mode UI
- [ ] Manual smoke-check `streamlit run streamlit_app.py`

## Success Criteria

- App starts with `streamlit run streamlit_app.py`
- Compare mode refuses to run without both required files and shows summary plus row review after a successful run
- Extract-items mode produces downloadable CSV/XLSX from Excel only
- Generated downloads match the shared workflow outputs instead of UI-specific reimplementations

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Streamlit reruns trigger duplicate heavy work | Medium | Medium | Run workflows only on explicit button click and reuse `st.session_state` payloads |
| Large downloads increase memory usage | Medium | Medium | Limit v1 to single-file workflows and serve files from temp artifacts |
| Temp files accumulate | Low | Medium | Use per-run temp dirs and best-effort cleanup hooks |

## Security Considerations

- Keep app local/internal only; no remote storage or network calls
- Validate file extensions before saving uploads
- Avoid showing more raw personal data than already present in exported reports

## Rollback Plan

- Remove Streamlit entrypoint and UI helper
- Remove Streamlit dependency change
- Keep shared workflows for CLI reuse if Phase 01 already landed cleanly

## Next Steps

- Unresolved: `streamlit` package is declared in `requirements.txt` but not installed in the current environment, so live app launch was not verified here
