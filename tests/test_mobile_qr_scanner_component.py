from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from shopee_compare.mobile_qr_scanner_component import JS


class MobileQrScannerComponentTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is required for JS syntax verification")
    def test_component_javascript_is_valid_module_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "mobile-qr-scanner-component.mjs"
            script_path.write_text(JS, encoding="utf-8")
            result = subprocess.run(
                ["node", "--check", str(script_path)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
