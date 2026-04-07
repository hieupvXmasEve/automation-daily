from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from ..order_item_export import build_order_item_export_frame, export_order_item_report


VALID_ITEM_EXPORT_FORMATS = ("excel", "csv")


@dataclass(slots=True)
class ExtractItemsRunRequest:
    excel_path: Path
    export_format: str = "excel"
    output_path: Path | None = None


@dataclass(slots=True)
class ExtractItemsRunResult:
    frame: pd.DataFrame
    output_path: Path
    row_count: int


def run_extract_items(request: ExtractItemsRunRequest) -> ExtractItemsRunResult:
    if not request.excel_path.is_file():
        raise FileNotFoundError(f"Excel file not found: {request.excel_path}")
    if request.export_format not in VALID_ITEM_EXPORT_FORMATS:
        raise ValueError(f"Unsupported output format: {request.export_format}")

    suffix = ".xlsx" if request.export_format == "excel" else ".csv"
    output_path = request.output_path or _default_output_path(suffix)
    frame = build_order_item_export_frame(request.excel_path)
    export_order_item_report(output_path, frame)
    return ExtractItemsRunResult(frame=frame, output_path=output_path, row_count=len(frame.index))


def _default_output_path(suffix: str) -> Path:
    return Path("output") / datetime.now().strftime("%Y%m%d-%H%M%S") / f"order-items{suffix}"
