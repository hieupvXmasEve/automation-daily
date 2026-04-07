from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from shopee_compare.services import (
    CompareRunRequest,
    ExtractItemsRunRequest,
    run_compare,
    run_extract_items,
    temporary_upload_workspace,
)
from shopee_compare.streamlit_workflows import run_tiktok_pdf_audit_upload


ROOT = Path(__file__).resolve().parent.parent
TIKTOK_PDF_PATH = Path.home() / "Downloads" / "3.TikTok PPM (B4716) - 10- đơn  - 07.04.2026.pdf"


def _fixture_path(pattern: str) -> Path:
    matches = sorted((ROOT / "shopee").glob(pattern))
    if not matches:
        raise FileNotFoundError(f"Missing fixture matching {pattern}")
    return matches[0]


EXCEL_PATH = _fixture_path("*.xlsx")
PDF_PATH = _fixture_path("*.pdf")


class FakeUpload:
    def __init__(self, name: str, data: bytes) -> None:
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


class WorkflowServiceTests(unittest.TestCase):
    def test_run_compare_filters_rows_and_keeps_download_bytes_usable(self) -> None:
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

    def test_run_extract_items_returns_frame_and_output(self) -> None:
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
