from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pandas as pd

from shopee_compare.order_item_export import build_order_item_export_frame


ROOT = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT / "shopee" / "Order.all.order_creation_date.20260402_20260406.xlsx"


class ExtractItemsTests(unittest.TestCase):
    def test_build_order_item_export_frame(self) -> None:
        frame = build_order_item_export_frame(EXCEL_PATH)
        self.assertEqual(
            list(frame.columns),
            [
                "Mã đơn hàng",
                "Mã vật tư",
                "Số lượng",
                "Total Order",
                "Ngày xử lý đơn hàng",
                "Ngày xử lý đơn hàng detail",
                "Ngày đặt hàng",
            ],
        )
        self.assertGreater(len(frame.index), 0)

        target = frame[frame["Mã đơn hàng"] == "260402PGQ537AC"]
        self.assertEqual(target["Mã vật tư"].tolist(), ["FM5APA5065I0", "FM5APA6179I0"])
        self.assertEqual(target["Số lượng"].tolist(), [1, 1])
        self.assertEqual(target["Total Order"].tolist(), [0.5, 0.5])
        self.assertEqual(target["Ngày xử lý đơn hàng"].tolist(), ["02/04/2026", "02/04/2026"])
        self.assertEqual(
            target["Ngày xử lý đơn hàng detail"].tolist(),
            ["02/04/2026 10:48", "02/04/2026 10:48"],
        )
        self.assertEqual(target["Ngày đặt hàng"].tolist(), ["2026-04-02 03:17", "2026-04-02 03:17"])

        cancelled = frame[frame["Mã đơn hàng"] == "260402PA7QGTBM"].iloc[0]
        self.assertEqual(cancelled["Ngày xử lý đơn hàng"], "")
        self.assertEqual(cancelled["Ngày xử lý đơn hàng detail"], "")

    def test_cli_extract_items_exports_excel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "order-items.xlsx"
            command = [
                sys.executable,
                "main.py",
                "extract-items",
                "--excel",
                str(EXCEL_PATH),
                "--out-file",
                str(output_path),
            ]
            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            self.assertTrue(output_path.is_file())

            exported = pd.read_excel(output_path)
            self.assertEqual(
                list(exported.columns),
                [
                    "Mã đơn hàng",
                    "Mã vật tư",
                    "Số lượng",
                    "Total Order",
                    "Ngày xử lý đơn hàng",
                    "Ngày xử lý đơn hàng detail",
                    "Ngày đặt hàng",
                ],
            )
            self.assertGreater(len(exported.index), 0)


if __name__ == "__main__":
    unittest.main()
