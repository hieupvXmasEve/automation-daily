from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from shopee_compare.marketplace_scan_importer import build_imported_shop_dataset, load_marketplace_import_preview
from shopee_compare.services import (
    MarketplaceQrScanRequest,
    build_scan_rows_frame,
    export_scan_rows_excel,
    run_marketplace_qr_scan,
)


class MarketplaceQrScanServiceTests(unittest.TestCase):
    def test_lazada_csv_header_detection_and_dataset_build(self) -> None:
        csv_content = (
            "meta,meta,meta\n"
            "Total Order,orderNumber,trackingCode,itemName\n"
            "1,ORDER-1,TRACK-001,Product A\n"
            "1,ORDER-2,TRACK-002,Product B\n"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_path = Path(tmp_dir) / "lazada.csv"
            source_path.write_text(csv_content, encoding="utf-8-sig")
            preview = load_marketplace_import_preview(source_path, marketplace="lazada", shop_label="Lazada Mall")
            dataset = build_imported_shop_dataset(preview, "trackingCode")

        self.assertIn("trackingCode", preview.available_fields)
        self.assertEqual(dataset.row_count, 2)
        self.assertIn("track001", dataset.lookup)
        self.assertEqual(dataset.rows[0].source_order_reference, "ORDER-1")

    def test_run_marketplace_qr_scan_handles_match_duplicate_and_not_found(self) -> None:
        frame = pd.DataFrame(
            [
                {"Mã đơn hàng": "SHOP-1-001", "Mã vận đơn": "QR-001"},
                {"Mã đơn hàng": "SHOP-1-002", "Mã vận đơn": "QR-002"},
            ]
        )
        preview = load_marketplace_import_preview_from_frame(frame, "shopee", "Shopee A", "orders.xlsx")
        dataset = build_imported_shop_dataset(preview, "Mã vận đơn")

        matched = run_marketplace_qr_scan(
            MarketplaceQrScanRequest(imported_shops=[dataset], existing_rows=[], scanned_text="QR-001", scan_source="manual")
        )
        duplicate = run_marketplace_qr_scan(
            MarketplaceQrScanRequest(
                imported_shops=[dataset],
                existing_rows=[matched.scan_row] if matched.scan_row else [],
                scanned_text="QR-001",
                scan_source="manual",
            )
        )
        not_found = run_marketplace_qr_scan(
            MarketplaceQrScanRequest(imported_shops=[dataset], existing_rows=[], scanned_text="QR-999", scan_source="manual")
        )

        self.assertEqual(matched.status, "matched")
        self.assertIsNotNone(matched.scan_row)
        self.assertEqual(duplicate.status, "duplicate")
        self.assertEqual(not_found.status, "not-found")

    def test_run_marketplace_qr_scan_marks_ambiguous_cross_shop_match(self) -> None:
        frame_a = pd.DataFrame([{"order_id": "A-001", "trackingCode": "SAME-QR"}])
        frame_b = pd.DataFrame([{"order_id": "B-001", "trackingCode": "SAME-QR"}])
        dataset_a = build_imported_shop_dataset(
            load_marketplace_import_preview_from_frame(frame_a, "lazada", "Lazada A", "a.csv"),
            "trackingCode",
        )
        dataset_b = build_imported_shop_dataset(
            load_marketplace_import_preview_from_frame(frame_b, "website", "Website B", "b.csv"),
            "trackingCode",
        )

        event = run_marketplace_qr_scan(
            MarketplaceQrScanRequest(
                imported_shops=[dataset_a, dataset_b],
                existing_rows=[],
                scanned_text="SAME-QR",
                scan_source="camera",
            )
        )

        self.assertEqual(event.status, "ambiguous")
        self.assertIsNone(event.scan_row)

    def test_export_scan_rows_excel_builds_expected_frame(self) -> None:
        frame = pd.DataFrame([{"order_id": "A-001", "trackingCode": "QR-001"}])
        dataset = build_imported_shop_dataset(
            load_marketplace_import_preview_from_frame(frame, "website", "Website A", "orders.csv"),
            "trackingCode",
        )
        event = run_marketplace_qr_scan(
            MarketplaceQrScanRequest(imported_shops=[dataset], existing_rows=[], scanned_text="QR-001", scan_source="camera")
        )
        self.assertIsNotNone(event.scan_row)

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "scan.xlsx"
            result = export_scan_rows_excel(output_path, [event.scan_row] if event.scan_row else [])

            self.assertTrue(output_path.is_file())
            self.assertEqual(list(result.frame.columns), list(build_scan_rows_frame([event.scan_row]).columns))
            self.assertGreater(output_path.stat().st_size, 0)


def load_marketplace_import_preview_from_frame(
    frame: pd.DataFrame,
    marketplace: str,
    shop_label: str,
    file_name: str,
):
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir) / file_name
        if path.suffix == ".csv":
            frame.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            frame.to_excel(path, index=False)
        return load_marketplace_import_preview(path, marketplace=marketplace, shop_label=shop_label)


if __name__ == "__main__":
    unittest.main()
