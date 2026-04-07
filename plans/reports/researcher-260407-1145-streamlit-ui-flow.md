---
title: researcher-260407-1145-streamlit-ui-flow
date: 2026-04-07 11:48 +07
scope: automation-daily
---

# Research Report: Streamlit UI flow for Shopee compare

## Summary
Best low-risk path: keep the current CLI logic as the source of truth, add one Streamlit entrypoint, and extract only orchestration into a shared workflow module. Do not move parsing, matching, or exporting logic into Streamlit code.

Use uploaded files -> per-session temp paths -> existing loaders/matcher/exporters -> session_state -> metrics, tables, and download buttons. This preserves offline behavior, keeps the CLI intact, and avoids duplicate compare logic.

## Evidence
- Repo flow already cleanly splits loader -> matcher -> exporter: [cli.py](/Users/hunt2412/hieupvdev/project/automation-daily/shopee_compare/cli.py), [excel_loader.py](/Users/hunt2412/hieupvdev/project/automation-daily/shopee_compare/excel_loader.py), [pdf_loader.py](/Users/hunt2412/hieupvdev/project/automation-daily/shopee_compare/pdf_loader.py), [matcher.py](/Users/hunt2412/hieupvdev/project/automation-daily/shopee_compare/matcher.py), [exporters](/Users/hunt2412/hieupvdev/project/automation-daily/shopee_compare/exporters).
- Current outputs already fit a UI: summary counts, row-level records, item export DataFrame, and generated files.
- PDR says GUI was out of scope; this is a scoped internal extension, not a replacement of the CLI.
- Official Streamlit docs used only, no third-party tutorials.

## Recommendation
| Rank | Option | Verdict | Why |
|---|---|---|---|
| 1 | Shared workflow module + thin Streamlit app | Recommend | lowest drift, no logic rewrite, reusable by CLI/UI |
| 2 | Streamlit app directly orchestrating loaders/exporters | Acceptable | zero core refactor, but duplicated workflow glue |
| 3 | Rebuild compare logic inside Streamlit | Reject | highest risk, unnecessary duplication |

## Concrete Screen Structure
1. Sidebar
- `st.file_uploader` for one `.xlsx`
- `st.file_uploader` for one `.pdf`
- mode switch: `Compare` / `Extract items`
- export format toggles
- `Run` button
2. Processing strip
- `st.spinner("Running compare...")`
- `st.progress` with 4 coarse steps: save uploads, parse, compare, export
- stage text in `st.empty()`
3. Results area
- top KPI row with `st.metric`: Excel orders, PDF labels/pages, matched, mismatch, missing-in-excel, missing-in-pdf
- tabs: `Overview`, `Comparison table`, `Item export`, `Downloads`
- `st.dataframe` for read-only review; status filter outside the table
- row detail in an expander or selectbox, not an editable grid
4. Downloads
- `st.download_button` for CSV/XLSX/PDF
- `st.download_button` for order-item CSV/XLSX in extract mode

## File Handling Pattern
- `st.file_uploader` returns an in-memory uploaded file for the current session only.
- Copy each upload to a per-session temp dir immediately.
- Pass temp file `Path`s into the existing loaders/exporters.
- Keep the last run in `st.session_state` so reruns do not lose results.

## Minimal Modules To Add/Change
- Add `streamlit_app.py`: UI only, no business logic rewrite
- Add `shopee_compare/workflows.py`: shared `run_compare(...)` and `run_extract_items(...)` orchestration returning rows/summary/artifacts
- Change `shopee_compare/cli.py` to call the shared workflow module
- Optional: add `requirements-ui.txt` or pin `streamlit` in `requirements.txt`
- No change needed in loaders, matcher, or exporters for v1

## Risks / Trade-offs
| Risk | Impact | Mitigation |
|---|---|---|
| Uploaded files live only in session memory | lost on rerun/disconnect | copy to per-session temp dir immediately |
| `st.download_button` keeps data in memory | bad for very large exports | keep v1 files small; use temp files + bytes |
| Tabs rerun all content | wasted compute if heavy code sits inside tabs | compute once before tabs, render only precomputed data |
| CLI/UI drift | inconsistent results | shared workflow module |
| GUI scope creep | extra features slow delivery | keep v1 to 1 Excel + 1 PDF, no OCR/batch mode |

## Why This Is The Best Fit
- Existing code is already modular enough for a thin UI wrapper.
- Streamlit widgets match the current workflow: upload -> process -> inspect -> download.
- `st.metric` fits summary KPIs.
- `st.dataframe` fits read-only order review better than `st.data_editor`.
- `st.download_button` is enough for the generated artifacts already produced by the CLI.

## Sources
- Streamlit file upload docs: https://github.com/streamlit/docs/blob/main/content/develop/api-reference/widgets/file_uploader.md
- Streamlit progress docs: https://docs.streamlit.io/1.35.0/develop/api-reference/status/st.progress
- Streamlit spinner docs: https://docs.streamlit.io/1.45.0/develop/api-reference/status/st.spinner
- Streamlit download button docs: https://docs.streamlit.io/1.37.0/develop/api-reference/widgets/st.download_button
- Streamlit tabs docs: https://github.com/streamlit/docs/blob/main/content/develop/concepts/app-design/layouts-and-containers.md
- Streamlit metric/dataframe/data_editor docs: https://github.com/streamlit/docs/blob/main/content/menu.md
- Local repo context: [README.md](/Users/hunt2412/hieupvdev/project/automation-daily/docs/README.md), [project-overview-pdr.md](/Users/hunt2412/hieupvdev/project/automation-daily/docs/project-overview-pdr.md), [cli flow wireframe](/Users/hunt2412/hieupvdev/project/automation-daily/docs/wireframe/cli-flow.md), [test_compare.py](/Users/hunt2412/hieupvdev/project/automation-daily/tests/test_compare.py), [test_extract_items.py](/Users/hunt2412/hieupvdev/project/automation-daily/tests/test_extract_items.py)

## Unresolved Questions
- Should v1 expose `extract-items` in the Streamlit UI, or compare-only first?
- Should Streamlit be an optional UI dependency or added to the base requirements?
