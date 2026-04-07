from __future__ import annotations

import streamlit as st

from shopee_compare.streamlit_workflows import run_compare_uploads, run_extract_upload


COMPARE_RESULT_KEY = "compare_result"
EXTRACT_RESULT_KEY = "extract_result"

st.set_page_config(page_title="Shopee Compare Internal App", layout="wide")


def main() -> None:
    st.title("Shopee Compare Internal App")
    st.caption("Internal Streamlit UI for compare reports and item-row export.")

    compare_tab, extract_tab = st.tabs(["Compare Orders", "Extract Item Rows"])
    with compare_tab:
        render_compare_tab()
    with extract_tab:
        render_extract_tab()


def render_compare_tab() -> None:
    with st.form("compare-form"):
        excel_file = st.file_uploader("Shopee Excel export", type=["xlsx"], key="compare-excel")
        pdf_file = st.file_uploader("Shipping label PDF", type=["pdf"], key="compare-pdf")
        formats = st.multiselect("Export formats", ["csv", "excel", "pdf"], default=["csv", "excel", "pdf"])
        only_statuses = st.multiselect(
            "Only export statuses",
            ["matched", "mismatch", "missing-in-excel", "missing-in-pdf"],
        )
        submitted = st.form_submit_button("Run Compare", use_container_width=True)

    if submitted:
        if excel_file is None or pdf_file is None:
            st.error("Upload both Excel and PDF files before running compare.")
        else:
            result = run_compare_action(excel_file, pdf_file, formats, only_statuses)
            if result:
                st.session_state[COMPARE_RESULT_KEY] = result

    result = st.session_state.get(COMPARE_RESULT_KEY)
    if result is not None:
        render_compare_result(result)


def render_extract_tab() -> None:
    with st.form("extract-form"):
        excel_file = st.file_uploader("Shopee Excel export", type=["xlsx"], key="extract-excel")
        export_format = st.selectbox("Output format", ["excel", "csv"], index=0)
        submitted = st.form_submit_button("Export Item Rows", use_container_width=True)

    if submitted:
        if excel_file is None:
            st.error("Upload an Excel file before exporting item rows.")
        else:
            result = run_extract_action(excel_file, export_format)
            if result:
                st.session_state[EXTRACT_RESULT_KEY] = result

    result = st.session_state.get(EXTRACT_RESULT_KEY)
    if result:
        st.metric("Item rows", result["row_count"])
        st.dataframe(result["frame"], use_container_width=True, height=420)
        st.download_button(
            label=f"Download {result['file_name']}",
            data=result["data"],
            file_name=result["file_name"],
            mime=result["mime"],
            use_container_width=True,
        )


def run_compare_action(excel_file: object, pdf_file: object, formats: list[str], only_statuses: list[str]) -> dict[str, object]:
    progress_text = st.empty()
    progress_bar = st.progress(0)
    try:
        progress_text.info("Running compare workflow")
        progress_bar.progress(30)
        result = run_compare_uploads(excel_file, pdf_file, formats, only_statuses)
        progress_bar.progress(100)
        progress_text.success("Compare completed")
    except Exception as exc:
        progress_text.empty()
        progress_bar.empty()
        st.error(str(exc))
        return {}
    return result


def run_extract_action(excel_file: object, export_format: str) -> dict[str, object]:
    progress_text = st.empty()
    progress_bar = st.progress(0)
    try:
        progress_text.info("Building item export")
        progress_bar.progress(30)
        result = run_extract_upload(excel_file, export_format)
        progress_bar.progress(100)
        progress_text.success("Item export completed")
    except Exception as exc:
        progress_text.empty()
        progress_bar.empty()
        st.error(str(exc))
        return {}
    return result


def render_compare_result(result: dict[str, object]) -> None:
    if not result:
        return

    summary = result["summary"]
    top_metrics = st.columns(3)
    bottom_metrics = st.columns(3)
    top_metrics[0].metric("Excel orders", summary["excel_orders"])
    top_metrics[1].metric("PDF labels", summary["pdf_orders"])
    top_metrics[2].metric("Matched", summary["matched"])
    bottom_metrics[0].metric("Mismatch", summary["mismatch"])
    bottom_metrics[1].metric("Missing in Excel", summary["missing_in_excel"])
    bottom_metrics[2].metric("Missing in PDF", summary["missing_in_pdf"])

    overview_tab, table_tab, downloads_tab = st.tabs(["Overview", "Comparison table", "Downloads"])
    with overview_tab:
        st.write(f"Export filter: `{result['filter_label']}`")
        st.write(f"Rows shown: `{len(result['frame'].index)}`")
    with table_tab:
        st.dataframe(result["frame"], use_container_width=True, height=480)
    with downloads_tab:
        for file_name, payload in result["downloads"].items():
            st.download_button(
                label=f"Download {file_name}",
                data=payload["data"],
                file_name=file_name,
                mime=payload["mime"],
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
