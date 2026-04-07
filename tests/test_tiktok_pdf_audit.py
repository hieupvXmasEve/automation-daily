from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from shopee_compare.services import TikTokPdfAuditRunRequest, run_tiktok_pdf_audit
from shopee_compare.tiktok_pdf_loader import TikTokPdfPageRecord, aggregate_tiktok_orders, load_tiktok_pdf_orders


TIKTOK_PDF_PATH = Path.home() / "Downloads" / "3.TikTok PPM (B4716) - 10- đơn  - 07.04.2026.pdf"


class TikTokPdfAuditTests(unittest.TestCase):
    def test_aggregate_tiktok_orders_merges_multi_page_records(self) -> None:
        orders = aggregate_tiktok_orders(
            [
                TikTokPdfPageRecord(
                    order_id="ORDER-1",
                    page_number=5,
                    waybill="WB-1",
                    package_id="PKG-1",
                    order_datetime="2026-04-07 13:23",
                    recipient_name="Tung",
                    recipient_region="Ho Chi Minh",
                    total_quantity=None,
                    weight_kg=1.5,
                    product_text="Khăn tắm combo 2",
                ),
                TikTokPdfPageRecord(
                    order_id="ORDER-1",
                    page_number=6,
                    waybill=None,
                    package_id="PKG-1",
                    order_datetime=None,
                    recipient_name=None,
                    recipient_region=None,
                    total_quantity=2,
                    weight_kg=None,
                    product_text="Thảm chân combo 3",
                ),
            ]
        )

        self.assertEqual(len(orders), 1)
        order = orders[0]
        self.assertEqual(order.page_numbers, [5, 6])
        self.assertEqual(order.page_count, 2)
        self.assertEqual(order.total_quantity, 2)
        self.assertEqual(order.product_summary, "Khăn tắm combo 2 | Thảm chân combo 3")

    @unittest.skipUnless(TIKTOK_PDF_PATH.is_file(), "Local TikTok PDF fixture not available")
    def test_load_tiktok_pdf_orders_groups_unique_orders(self) -> None:
        parsed = load_tiktok_pdf_orders(TIKTOK_PDF_PATH)

        self.assertEqual(parsed.pdf_page_count, 12)
        self.assertEqual(len(parsed.page_records), 12)
        self.assertEqual(len(parsed.orders), 10)
        self.assertEqual(sum(order.page_count > 1 for order in parsed.orders), 2)

        merged_order = next(order for order in parsed.orders if order.order_id == "583426120334673830")
        self.assertEqual(merged_order.page_numbers, [5, 6])
        self.assertEqual(merged_order.total_quantity, 2)
        self.assertIn("Thảm chân", merged_order.product_summary)

    @unittest.skipUnless(TIKTOK_PDF_PATH.is_file(), "Local TikTok PDF fixture not available")
    def test_run_tiktok_pdf_audit_exports_review_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_tiktok_pdf_audit(
                TikTokPdfAuditRunRequest(
                    pdf_path=TIKTOK_PDF_PATH,
                    export_format="excel",
                    output_path=Path(tmp_dir) / "tiktok-pdf-orders.xlsx",
                )
            )

            self.assertTrue(result.output_path.is_file())
            self.assertEqual(result.summary["pdf_pages"], 12)
            self.assertEqual(result.summary["unique_orders"], 10)
            self.assertEqual(result.summary["multi_page_orders"], 2)
            self.assertEqual(result.row_count, 10)
            self.assertGreater(result.output_path.stat().st_size, 0)
            self.assertIn("pages", result.frame.columns)


if __name__ == "__main__":
    unittest.main()
