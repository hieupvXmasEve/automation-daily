from __future__ import annotations

from csv import reader
import hashlib
from pathlib import Path

import pandas as pd

from .marketplace_scan_models import ImportedShopDataset, ImportedShopRow, MarketplaceImportPreview
from .utils import is_missing, normalize_lookup_text, normalize_text


LAZADA_HEADER_MARKERS = {"orderItemId", "orderNumber", "trackingCode"}
REFERENCE_FIELD_ALIASES = (
    "Mã đơn hàng",
    "Mã vận đơn",
    "order_id",
    "orderNumber",
    "lazadaId",
    "orderItemId",
    "trackingCode",
    "package_id",
    "waybill",
)


def load_marketplace_import_preview(path: Path, marketplace: str, shop_label: str) -> MarketplaceImportPreview:
    frame = _load_table(path, marketplace)
    if frame.empty:
        raise ValueError("Imported file has no data rows.")
    fields = [column for column in frame.columns if normalize_text(column)]
    if not fields:
        raise ValueError("Imported file has no usable columns.")
    return MarketplaceImportPreview(
        marketplace=marketplace,
        shop_label=shop_label.strip(),
        source_file_name=path.name,
        frame=frame,
        available_fields=fields,
        row_count=len(frame.index),
    )


def build_imported_shop_dataset(preview: MarketplaceImportPreview, compare_field: str) -> ImportedShopDataset:
    if compare_field not in preview.available_fields:
        raise ValueError(f"Compare field not found: {compare_field}")

    rows: list[ImportedShopRow] = []
    lookup: dict[str, list[ImportedShopRow]] = {}
    for row_number, (_, raw_row) in enumerate(preview.frame.iterrows(), start=1):
        compare_value = normalize_text(raw_row.get(compare_field))
        normalized = normalize_lookup_text(compare_value)
        if not compare_value or not normalized:
            continue
        reference_value, reference_field = _resolve_reference(raw_row, row_number)
        imported_row = ImportedShopRow(
            row_number=row_number,
            compare_value=compare_value,
            normalized_compare_value=normalized,
            source_order_reference=reference_value,
            source_reference_field=reference_field,
        )
        rows.append(imported_row)
        lookup.setdefault(normalized, []).append(imported_row)

    if not rows:
        raise ValueError(f"Field '{compare_field}' has no usable values.")

    shop_id = _build_shop_id(preview.marketplace, preview.shop_label, preview.source_file_name, compare_field)
    return ImportedShopDataset(
        shop_id=shop_id,
        marketplace=preview.marketplace,
        shop_label=preview.shop_label,
        source_file_name=preview.source_file_name,
        compare_field=compare_field,
        available_fields=list(preview.available_fields),
        row_count=len(rows),
        rows=rows,
        lookup=lookup,
    )


def _build_shop_id(marketplace: str, shop_label: str, source_file_name: str, compare_field: str) -> str:
    base = f"{marketplace}|{shop_label}|{source_file_name}|{compare_field}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:10]
    prefix = normalize_lookup_text(f"{marketplace}-{shop_label}")[:24] or "shop"
    return f"{prefix}-{digest}"


def _load_table(path: Path, marketplace: str) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        header = _detect_csv_header_row(path) if marketplace == "lazada" else 0
        frame = pd.read_csv(path, dtype="string", header=header)
    elif suffix in {".xlsx", ".xlsm", ".xls"}:
        frame = pd.read_excel(path, dtype="string")
    else:
        raise ValueError(f"Unsupported import file type: {path.suffix or '(missing suffix)'}")
    prepared = frame.copy()
    prepared.columns = _unique_columns(prepared.columns)
    prepared = _drop_empty_unnamed_columns(prepared)
    return prepared.fillna("")


def _detect_csv_header_row(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for index, row in enumerate(reader(handle)):
            values = {cell.strip() for cell in row if cell.strip()}
            if len(values & LAZADA_HEADER_MARKERS) >= 2:
                return index
    return 0


def _unique_columns(columns: pd.Index) -> list[str]:
    counts: dict[str, int] = {}
    result: list[str] = []
    for index, column in enumerate(columns, start=1):
        base = normalize_text(column) or f"column_{index}"
        seen = counts.get(base, 0)
        counts[base] = seen + 1
        result.append(base if seen == 0 else f"{base}_{seen + 1}")
    return result


def _drop_empty_unnamed_columns(frame: pd.DataFrame) -> pd.DataFrame:
    keep_columns: list[str] = []
    for column in frame.columns:
        if not column.lower().startswith("unnamed:"):
            keep_columns.append(column)
            continue
        if any(not is_missing(value) for value in frame[column].tolist()):
            keep_columns.append(column)
    return frame[keep_columns].copy()


def _resolve_reference(raw_row: pd.Series, row_number: int) -> tuple[str, str]:
    for alias in REFERENCE_FIELD_ALIASES:
        if alias not in raw_row.index:
            continue
        value = normalize_text(raw_row.get(alias))
        if value:
            return value, alias
    return f"row-{row_number}", "row_number"

