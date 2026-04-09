from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from shopee_compare.mobile_qr_scanner_assets import get_vendored_qr_library_url
from shopee_compare.streamlit_marketplace_qr_scan_tab import _filter_preview_frame
from shopee_compare.services import (
    CompareRunRequest,
    ExtractItemsRunRequest,
    run_compare,
    run_extract_items,
    temporary_upload_workspace,
)
from shopee_compare.streamlit_workflows import (
    build_imported_shop_from_preview,
    build_marketplace_scan_export,
    load_marketplace_import_preview_upload,
    run_marketplace_qr_scan_action,
    run_tiktok_pdf_audit_upload,
)


ROOT = Path(__file__).resolve().parent.parent
TIKTOK_PDF_PATH = Path.home() / "Downloads" / "3.TikTok PPM (B4716) - 10- đơn  - 07.04.2026.pdf"


def _fixture_path(pattern: str) -> Path | None:
    matches = sorted((ROOT / "shopee").glob(pattern))
    return matches[0] if matches else None


EXCEL_PATH = _fixture_path("*.xlsx")
PDF_PATH = _fixture_path("*.pdf")
COMPARE_FIXTURES_AVAILABLE = EXCEL_PATH is not None and PDF_PATH is not None


class FakeUpload:
    def __init__(self, name: str, data: bytes) -> None:
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


class WorkflowServiceTests(unittest.TestCase):
    @unittest.skipUnless(COMPARE_FIXTURES_AVAILABLE, "Repo compare fixtures not available")
    def test_run_compare_filters_rows_and_keeps_download_bytes_usable(self) -> None:
        assert EXCEL_PATH is not None
        assert PDF_PATH is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_compare(
                CompareRunRequest(
                    excel_path=EXCEL_PATH,
                    pdf_path=PDF_PATH,
                    formats=("csv", "excel", "pdf"),
                    out_dir=Path(tmp_dir) / "compare-output",
                    only_statuses=("mismatch", "missing-in-pdf"),
                )
            )
            artifact_bytes = {path.name: path.read_bytes() for path in result.exported_paths}

        self.assertTrue(result.exported_rows)
        self.assertTrue(all(row.status in {"mismatch", "missing-in-pdf"} for row in result.exported_rows))
        self.assertEqual(set(artifact_bytes), {"comparison.csv", "comparison.xlsx", "comparison.pdf"})
        self.assertTrue(all(len(data) > 0 for data in artifact_bytes.values()))

    @unittest.skipUnless(EXCEL_PATH is not None, "Repo extract-items fixture not available")
    def test_run_extract_items_returns_frame_and_output(self) -> None:
        assert EXCEL_PATH is not None
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "order-items.csv"
            result = run_extract_items(
                ExtractItemsRunRequest(
                    excel_path=EXCEL_PATH,
                    export_format="csv",
                    output_path=output_path,
                )
            )

            self.assertTrue(result.output_path.is_file())
            self.assertEqual(result.output_path, output_path)
            self.assertEqual(result.row_count, len(result.frame.index))
            self.assertGreater(result.row_count, 0)

    def test_upload_workspace_writes_files_and_cleans_up(self) -> None:
        excel_upload = FakeUpload("orders.xlsx", b"excel-bytes")
        pdf_upload = FakeUpload("labels.pdf", b"pdf-bytes")
        with temporary_upload_workspace() as workspace:
            root = workspace.root
            excel_path = workspace.write_upload(excel_upload, "input.xlsx")
            pdf_path = workspace.write_upload(pdf_upload, "input.pdf")
            self.assertTrue(excel_path.is_file())
            self.assertTrue(pdf_path.is_file())
            self.assertEqual(excel_path.read_bytes(), b"excel-bytes")
            self.assertEqual(pdf_path.read_bytes(), b"pdf-bytes")

        self.assertFalse(root.exists())

    def test_marketplace_scan_workflow_preview_scan_and_export(self) -> None:
        upload = FakeUpload(
            "orders.csv",
            "order_id,trackingCode\nWEB-1,QR-001\nWEB-2,QR-002\n".encode("utf-8"),
        )

        preview = load_marketplace_import_preview_upload(upload, "website", "Website A")
        imported_shop = build_imported_shop_from_preview(preview, "trackingCode")
        result = run_marketplace_qr_scan_action([imported_shop], [], "QR-001", "manual")
        export = build_marketplace_scan_export(result["scan_rows"])

        self.assertEqual(result["status"], "matched")
        self.assertEqual(len(result["scan_rows"]), 1)
        self.assertEqual(export["row_count"], 1)
        self.assertGreater(len(export["data"]), 0)

    def test_marketplace_preview_filter_supports_column_and_global_search(self) -> None:
        frame = pd.DataFrame(
            [
                {"order_id": "WEB-1", "trackingCode": "QR-001", "customer": "Alice"},
                {"order_id": "WEB-2", "trackingCode": "QR-002", "customer": "Bob"},
            ]
        )

        by_column = _filter_preview_frame(frame, "trackingCode", "qr-002")
        across_all = _filter_preview_frame(frame, "All columns", "alice")

        self.assertEqual(by_column["order_id"].tolist(), ["WEB-2"])
        self.assertEqual(across_all["order_id"].tolist(), ["WEB-1"])

    def test_vendored_qr_library_url_is_embedded_data_url(self) -> None:
        library_url = get_vendored_qr_library_url()
        self.assertTrue(library_url.startswith("data:text/javascript;base64,"))
        self.assertGreater(len(library_url), 1000)

    @unittest.skipUnless(TIKTOK_PDF_PATH.is_file(), "Local TikTok PDF fixture not available")
    def test_tiktok_pdf_upload_workflow_returns_grouped_order_rows(self) -> None:
        upload = FakeUpload(TIKTOK_PDF_PATH.name, TIKTOK_PDF_PATH.read_bytes())
        result = run_tiktok_pdf_audit_upload(upload, "csv")

        self.assertEqual(result["summary"]["pdf_pages"], 12)
        self.assertEqual(result["summary"]["unique_orders"], 10)
        self.assertEqual(result["row_count"], 10)
        self.assertGreater(len(result["data"]), 0)


if __name__ == "__main__":
    unittest.main()
