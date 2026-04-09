from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from ..marketplace_qr_scan_matcher import resolve_scan_event
from ..marketplace_scan_models import ImportedShopDataset, MarketplaceScanEvent, MarketplaceScanResultRow, SCAN_RESULT_COLUMNS


@dataclass(slots=True)
class MarketplaceQrScanRequest:
    imported_shops: list[ImportedShopDataset]
    existing_rows: list[MarketplaceScanResultRow]
    scanned_text: str
    scan_source: str = "manual"
    scanned_at: str | None = None


@dataclass(slots=True)
class MarketplaceQrScanExportResult:
    frame: pd.DataFrame
    output_path: Path


def run_marketplace_qr_scan(request: MarketplaceQrScanRequest) -> MarketplaceScanEvent:
    return resolve_scan_event(
        imported_shops=request.imported_shops,
        existing_rows=request.existing_rows,
        scanned_text=request.scanned_text,
        scan_source=request.scan_source,
        scanned_at=request.scanned_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


def build_scan_rows_frame(rows: list[MarketplaceScanResultRow], shop_id: str | None = None) -> pd.DataFrame:
    filtered_rows = [row for row in rows if shop_id in {None, "", row.shop_id}]
    if not filtered_rows:
        return pd.DataFrame(columns=SCAN_RESULT_COLUMNS)
    # Collect dynamic source-file columns from raw_data (preserve insertion order, dedup)
    raw_keys = list(dict.fromkeys(key for row in filtered_rows for key in row.raw_data))
    all_columns = SCAN_RESULT_COLUMNS + raw_keys
    return pd.DataFrame([row.to_row() for row in filtered_rows], columns=all_columns)


def export_scan_rows_excel(
    output_path: Path,
    rows: list[MarketplaceScanResultRow],
    shop_id: str | None = None,
) -> MarketplaceQrScanExportResult:
    frame = build_scan_rows_frame(rows, shop_id=shop_id)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_excel(output_path, index=False)
    return MarketplaceQrScanExportResult(frame=frame, output_path=output_path)
