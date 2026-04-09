from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from shopee_compare.mobile_qr_scanner_component import JS, render_mobile_qr_scanner


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

    def test_render_mobile_qr_scanner_disables_style_isolation(self) -> None:
        captured: dict[str, object] = {}

        def fake_component(name: str, **kwargs):
            captured["name"] = name
            captured["kwargs"] = kwargs

            def renderer(**renderer_kwargs):
                captured["renderer_kwargs"] = renderer_kwargs
                return renderer_kwargs

            return renderer

        with patch("shopee_compare.mobile_qr_scanner_component.st.components.v2.component", side_effect=fake_component):
            render_mobile_qr_scanner(enabled=True, key="scanner-test")

        self.assertEqual(captured["name"], "mobile_qr_scanner")
        self.assertIs(captured["kwargs"]["isolate_styles"], False)
        self.assertEqual(captured["renderer_kwargs"]["key"], "scanner-test")
        self.assertEqual(captured["renderer_kwargs"]["height"], 820)
        self.assertTrue(captured["renderer_kwargs"]["data"]["enabled"])


if __name__ == "__main__":
    unittest.main()
