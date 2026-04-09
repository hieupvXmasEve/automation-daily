from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path


VENDORED_QR_LIBRARY_PATH = Path(__file__).with_name("vendor").joinpath("html5-qrcode.bundle.mjs")


@lru_cache(maxsize=1)
def get_vendored_qr_library_url() -> str:
    payload = base64.b64encode(VENDORED_QR_LIBRARY_PATH.read_bytes()).decode("ascii")
    return f"data:text/javascript;base64,{payload}"
