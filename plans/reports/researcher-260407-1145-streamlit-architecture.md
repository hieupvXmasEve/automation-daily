---
title: "Streamlit Architecture Boundary for Shopee Compare"
date: "2026-04-07 11:49 ICT"
status: "research"
---

# Research Report: Streamlit Architecture Boundary

## Summary
Best boundary: move the compare/extract orchestration out of `shopee_compare/cli.py` into shared service modules, but keep loaders, matcher, and exporters path-based.
CLI stays a thin adapter. Streamlit gets a second adapter that materializes uploads into a temp workspace, calls the same services, then exposes downloads.

This is the lowest-risk reuse path.
It preserves current CLI/test contracts, avoids a file-like refactor in loaders/exporters, and fits the existing layering in `docs/system-architecture.md`.

## Evidence
- `shopee_compare/cli.py:77-150` currently owns validation, output-dir choice, load/compare/export orchestration, and status filtering.
- `shopee_compare/exporters/pdf_exporter.py:19-29` and `shopee_compare/order_item_export.py:66-99` are already output-path based, so they fit a temp-workspace adapter.
- `tests/test_compare.py:179-210` and `tests/test_extract_items.py:50-85` lock the CLI/file-artifact contract; keep them as regression tests.
- `docs/system-architecture.md:5-19` already models CLI as orchestration only, not domain logic.

## Recommendation
| Rank | Boundary | Trade-offs | Risk | Fit |
|---|---|---|---|---|
| 1 | Shared service modules + Streamlit temp-workspace adapter | Smallest change, highest reuse, no test breakage | Low | Best |
| 2 | Refactor loaders/exporters to accept file-like objects | Cleaner long term, but wider churn | Medium | Good later |
| 3 | Duplicate compare/export logic in Streamlit | Fast start, but doubles maintenance | High | Poor |

### Move out of `cli.py`
- `handle_compare` and `handle_extract_items` orchestration.
- Source loading, compare execution, `--only` filtering, and export calls.
- Result shaping for UI display, not `print()` calls.
- Output path creation helper, but not CLI argument parsing.

### Keep in `cli.py`
- `argparse` wiring.
- Console progress text and exit-code conversion.
- CLI defaults for timestamped output dirs.

### Suggested service modules
- `shopee_compare/services/compare_service.py`
  - `run_compare(...) -> CompareRunResult`
  - returns rows, summary, and exported artifact paths.
- `shopee_compare/services/extract_items_service.py`
  - `run_extract_items(...) -> ExtractItemsRunResult`
  - returns row count and output path.
- `shopee_compare/services/upload_workspace.py`
  - writes Streamlit uploads to a per-run temp dir.
  - owns cleanup helpers only; no UI code.

## Temp-File Strategy
- Use one `tempfile.TemporaryDirectory(prefix="shopee-compare-")` per Streamlit run or per submit action.
- Copy `st.file_uploader()` bytes into named files inside that dir: `input.xlsx`, `input.pdf`.
- Call the shared services with those paths; keep the current path-based loaders/exporters untouched.
- Read generated CSV/XLSX/PDF files back to bytes for `st.download_button`, then clean up the temp dir in `finally`.
- Store only uploaded bytes and small metadata in `st.session_state`, not temp paths or open handles.

Why this is safest:
- `st.file_uploader` returns `UploadedFile`, a file-like `BytesIO` object; docs say uploaded data live in RAM until rerun and are deleted when no longer needed.
- `st.download_button` keeps download data in memory while the user is connected, so bytes are already the right handoff format.
- Python `tempfile.TemporaryDirectory` gives automatic cleanup and cross-platform safety; `NamedTemporaryFile` is only needed if a downstream library must reopen the same handle.

## New Tests
- Add service-level tests that call the new compare/extract functions directly with the current Shopee fixtures and a temp output dir.
- Add upload-workspace tests with fake `UploadedFile`-like objects or `BytesIO`:
  - writes both files with the expected suffixes/names.
  - cleans the temp dir on success and on exception.
- Add Streamlit-handoff tests:
  - generated CSV/XLSX/PDF bytes are readable after the temp dir is removed.
  - `CompareRunResult` exposes summary counts and filtered rows without parsing stdout.
- Keep current CLI subprocess tests unchanged; they remain the compatibility gate.

## Adoption Risk
- Low for the recommended boundary: all changes sit above current loaders/matcher/exporters.
- Medium only if you later switch to file-like loaders or in-memory exporters.
- High if Streamlit gets its own copy of compare/export logic.

## Sources
- Streamlit `st.file_uploader`: https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader
- Streamlit `st.download_button`: https://docs.streamlit.io/develop/api-reference/widgets/st.download_button
- Streamlit Session State: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
- Streamlit file uploader storage/delete behavior: https://docs.streamlit.io/knowledge-base/using-streamlit/where-file-uploader-store-when-deleted
- Python `tempfile`: https://docs.python.org/3.12/library/tempfile.html
- Repo contract/docs: `shopee_compare/cli.py`, `shopee_compare/exporters/*`, `shopee_compare/order_item_export.py`, `docs/system-architecture.md`, `tests/test_compare.py`, `tests/test_extract_items.py`

## Unresolved Questions
- Should Streamlit cache uploaded bytes in `st.session_state` or `st.cache_data` if the user needs multiple reruns without re-uploading?
- Are the generated comparison artifacts always small enough to keep the download handoff in memory, or do we need a per-session workspace later?
