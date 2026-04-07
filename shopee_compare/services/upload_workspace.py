from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator


@dataclass(slots=True)
class UploadWorkspace:
    root: Path

    def write_bytes(self, file_name: str, data: bytes) -> Path:
        path = self.root / file_name
        path.write_bytes(data)
        return path

    def write_upload(self, upload: object, fallback_name: str) -> Path:
        getvalue = getattr(upload, "getvalue", None)
        if getvalue is None:
            raise TypeError("Upload must expose getvalue().")

        upload_name = getattr(upload, "name", "") or fallback_name
        suffix = Path(upload_name).suffix or Path(fallback_name).suffix
        file_name = f"{Path(fallback_name).stem}{suffix}"
        return self.write_bytes(file_name, getvalue())


@contextmanager
def temporary_upload_workspace(prefix: str = "shopee-compare-") -> Iterator[UploadWorkspace]:
    with TemporaryDirectory(prefix=prefix) as root:
        yield UploadWorkspace(root=Path(root))
