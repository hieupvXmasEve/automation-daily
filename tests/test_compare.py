from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from shopee_compare.models import ExcelOrder, OrderItem, PdfItem, PdfOrder
from shopee_compare.excel_loader import load_excel_orders
from shopee_compare.matcher import compare_orders
from shopee_compare.pdf_loader import load_pdf_orders


ROOT = Path(__file__).resolve().parent.parent


def _fixture_path(pattern: str) -> Path:
    matches = sorted((ROOT / "shopee").glob(pattern))
    if not matches:
        raise FileNotFoundError(f"Missing fixture matching {pattern}")
    return matches[0]


EXCEL_PATH = _fixture_path("*.xlsx")
PDF_PATH = _fixture_path("*.pdf")


class CompareWorkflowTests(unittest.TestCase):
    def test_load_excel_orders(self) -> None:
        orders = load_excel_orders(EXCEL_PATH)
        self.assertGreater(len(orders), 0)
        target = orders[0]
        self.assertTrue(target.order_id)
        self.assertGreater(target.total_quantity, 0)
        self.assertGreater(len(target.items), 0)
        self.assertTrue(all(item.sku is None or item.sku for item in target.items))

    def test_load_pdf_orders(self) -> None:
        orders = load_pdf_orders(PDF_PATH)
        self.assertGreater(len(orders), 0)
        first = orders[0]
        self.assertTrue(first.order_id)
        self.assertTrue(first.waybill)
        self.assertGreater(first.total_quantity or 0, 0)
        self.assertGreater(first.items[0].quantity, 0)

    def test_compare_summary(self) -> None:
        excel_orders = load_excel_orders(EXCEL_PATH)
        pdf_orders = load_pdf_orders(PDF_PATH)
        comparison_rows, summary = compare_orders(excel_orders, pdf_orders)
        self.assertEqual(len(comparison_rows), len(excel_orders))
        self.assertEqual(summary["excel_orders"], len(excel_orders))
        self.assertEqual(summary["pdf_orders"], len(pdf_orders))
        self.assertEqual(
            summary["matched"] + summary["mismatch"] + summary["missing_in_excel"] + summary["missing_in_pdf"],
            len(comparison_rows),
        )
        self.assertGreater(summary["missing_in_pdf"] + summary["mismatch"], 0)
        flagged_row = next(
            row for row in comparison_rows if row.missing_excel_items and row.status in {"mismatch", "missing-in-pdf"}
        )
        self.assertIn("- x", flagged_row.missing_excel_items)
        self.assertTrue(any("\n" in row.missing_excel_items for row in comparison_rows if row.missing_excel_items))

    def test_compare_detects_missing_pdf_items(self) -> None:
        excel_orders = [
            ExcelOrder(
                order_id="ORDER-1",
                waybill="WB-1",
                order_datetime="2026-04-02 15:40",
                order_status="Đã giao",
                recipient_name="User",
                phone=None,
                city=None,
                district=None,
                ward=None,
                address=None,
                total_quantity=5,
                line_item_count=3,
                item_summary="",
                items=[
                    OrderItem(name="Khăn Tắm Dài", variant="Xanh", quantity=2),
                    OrderItem(name="Khăn Tay Mềm", variant="Hồng", quantity=2, sku="SKU-HONG"),
                    OrderItem(name="Khăn Gội Nhanh", variant="Xám", quantity=1, sku="SKU-XAM"),
                ],
            )
        ]
        pdf_orders = [
            PdfOrder(
                order_id="ORDER-1",
                waybill="WB-1",
                order_datetime="2026-04-02 15:40",
                recipient_name="User",
                recipient_address="Addr",
                total_quantity=5,
                item_summary="Khăn Tắm Dài Xanh x2; Khăn Tay Mềm Hồng x1",
                item_lines=["1. Khăn Tắm Dài Xanh, SL: 2", "2. Khăn Tay Mềm Hồng, SL: 1"],
                items=[
                    PdfItem(raw_text="Khăn Tắm Dài Xanh", quantity=2, line_number=1),
                    PdfItem(raw_text="Khăn Tay Mềm Hồng", quantity=1, line_number=2),
                ],
                template_ok=True,
                template_issues=[],
                page_number=1,
                max_weight_grams=None,
                cod_amount_vnd=None,
            )
        ]
        comparison_rows, summary = compare_orders(excel_orders, pdf_orders)
        self.assertEqual(summary["mismatch"], 1)
        row = comparison_rows[0]
        self.assertEqual(row.status, "mismatch")
        self.assertIn(row.item_match_status, {"partial", "partial-and-unclear"})
        self.assertEqual(row.missing_excel_items, "[SKU- - Hồng - x2]\n[SKU- - Xám - x1]")

    def test_compare_marks_layout_clipped_items_as_unclear(self) -> None:
        excel_orders = [
            ExcelOrder(
                order_id="ORDER-2",
                waybill="WB-2",
                order_datetime="2026-04-03 01:50",
                order_status="Đã giao",
                recipient_name="User",
                phone=None,
                city=None,
                district=None,
                ward=None,
                address=None,
                total_quantity=1,
                line_item_count=1,
                item_summary="",
                items=[
                    OrderItem(
                        name="Khăn tay nén HNEN 28x42cm du lịch Mollis Cotton siêu mềm mịn thấm hút tốt gọn nhẹ dùng một lần đi du lịch cho người lớn",
                        variant="HNEN: Hồng",
                        quantity=1,
                        sku="HNEN01350408",
                    )
                ],
            )
        ]
        pdf_orders = [
            PdfOrder(
                order_id="ORDER-2",
                waybill="WB-2",
                order_datetime="2026-04-03 01:50",
                recipient_name="User",
                recipient_address="Addr",
                total_quantity=1,
                item_summary="Khăn tay nén HNEN 28x42cm du lịch Mollis Cotton siêu mềm mịn thấm hút tốt gọn nhẹ dùng một lần đi du lịch cho ngườilớn HNEN:Hồng x1",
                item_lines=[
                    "1. Khăn tay nén HNEN 28x42cm du lịch Mollis Cotton siêu mềm mịn thấm hút tốt gọn nhẹ dùng một lần đi du lịch cho ngườilớn HNEN:Hồng SL:1"
                ],
                items=[
                    PdfItem(
                        raw_text="Khăn tay nén HNEN 28x42cm du lịch Mollis Cotton siêu mềm mịn thấm hút tốt gọn nhẹ dùng một lần đi du lịch cho ngườilớn HNEN:Hồng",
                        quantity=1,
                        line_number=1,
                        layout_clipped=True,
                    )
                ],
                template_ok=True,
                template_issues=[],
                page_number=31,
                max_weight_grams=None,
                cod_amount_vnd=None,
            )
        ]

        comparison_rows, summary = compare_orders(excel_orders, pdf_orders)
        self.assertEqual(summary["mismatch"], 1)
        row = comparison_rows[0]
        self.assertEqual(row.status, "mismatch")
        self.assertEqual(row.item_match_status, "partial-and-unclear")
        self.assertEqual(row.missing_excel_items, "[HNEN - HNEN: Hồng - x1]")
        self.assertIn("HNEN:Hồng", row.unclear_pdf_items)

    def test_cli_exports_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "report"
            command = [
                sys.executable,
                "main.py",
                "compare",
                "--excel",
                str(EXCEL_PATH),
                "--pdf",
                str(PDF_PATH),
                "--formats",
                "csv",
                "excel",
                "pdf",
                "--out-dir",
                str(output_dir),
            ]
            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue((output_dir / "comparison.csv").is_file())
            self.assertTrue((output_dir / "comparison.xlsx").is_file())
            self.assertTrue((output_dir / "comparison.pdf").is_file())
            self.assertGreater((output_dir / "comparison.csv").stat().st_size, 0)
            self.assertGreater((output_dir / "comparison.xlsx").stat().st_size, 0)
            self.assertGreater((output_dir / "comparison.pdf").stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
