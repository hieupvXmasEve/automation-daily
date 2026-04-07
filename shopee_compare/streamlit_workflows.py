from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from .services import (
    CompareRunRequest,
    ExtractItemsRunRequest,
    run_compare,
    run_extract_items,
    temporary_upload_workspace,
)


DOWNLOAD_MIME_TYPES = {
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pdf": "application/pdf",
}


def run_compare_uploads(
    excel_file: object,
    pdf_file: object,
    formats: list[str],
    only_statuses: list[str],
) -> dict[str, object]:
    with temporary_upload_workspace() as workspace, TemporaryDirectory(prefix="shopee-compare-output-") as output_root:
        excel_path = workspace.write_upload(excel_file, "orders.xlsx")
        pdf_path = workspace.write_upload(pdf_file, "labels.pdf")
        result = run_compare(
            CompareRunRequest(
                excel_path=excel_path,
                pdf_path=pdf_path,
                formats=tuple(formats),
                out_dir=Path(output_root),
                only_statuses=tuple(only_statuses) if only_statuses else None,
            )
        )
        downloads = {path.name: build_download_payload(path) for path in result.exported_paths}

    return {
        "summary": result.summary,
        "frame": pd.DataFrame([row.to_row() for row in result.exported_rows]),
        "downloads": downloads,
        "filter_label": ", ".join(only_statuses) if only_statuses else "all statuses",
    }


def run_extract_upload(excel_file: object, export_format: str) -> dict[str, object]:
    with temporary_upload_workspace() as workspace, TemporaryDirectory(prefix="shopee-items-output-") as output_root:
        excel_path = workspace.write_upload(excel_file, "orders.xlsx")
        output_name = "order-items.xlsx" if export_format == "excel" else "order-items.csv"
        result = run_extract_items(
            ExtractItemsRunRequest(
                excel_path=excel_path,
                export_format=export_format,
                output_path=Path(output_root) / output_name,
            )
        )
        data = result.output_path.read_bytes()

    return {
        "frame": result.frame,
        "row_count": result.row_count,
        "file_name": result.output_path.name,
        "data": data,
        "mime": DOWNLOAD_MIME_TYPES[result.output_path.suffix],
    }


def build_download_payload(path: Path) -> dict[str, object]:
    return {
        "data": path.read_bytes(),
        "mime": DOWNLOAD_MIME_TYPES.get(path.suffix, "application/octet-stream"),
    }
