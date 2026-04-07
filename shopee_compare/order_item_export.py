from __future__ import annotations

from pathlib import Path

import pandas as pd

from .utils import is_missing, iso_datetime, normalize_text, parse_int


REQUIRED_ITEM_EXPORT_COLUMNS = {
    "Mã đơn hàng",
    "SKU phân loại hàng",
    "Số lượng",
    "Ngày đặt hàng",
}

PROCESS_DATE_SOURCE_COLUMNS = [
    "Ngày gửi hàng",
    "Ngày xuất hàng",
    "Thời gian giao hàng",
]

ORDER_ITEM_OUTPUT_COLUMNS = [
    "Mã đơn hàng",
    "Mã vật tư",
    "Số lượng",
    "Total Order",
    "Ngày xử lý đơn hàng",
    "Ngày xử lý đơn hàng detail",
    "Ngày đặt hàng",
]


def format_excel_date(value: object) -> str:
    parsed = parse_excel_datetime(value)
    if parsed is None:
        return ""
    return parsed.strftime("%d/%m/%Y")


def format_excel_datetime_detail(value: object) -> str:
    parsed = parse_excel_datetime(value)
    if parsed is None:
        return ""
    return parsed.strftime("%d/%m/%Y %H:%M")


def parse_excel_datetime(value: object) -> pd.Timestamp | None:
    if is_missing(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def resolve_process_datetimes(frame: pd.DataFrame) -> pd.Series:
    resolved = pd.Series([None] * len(frame.index), index=frame.index, dtype="object")
    for column in PROCESS_DATE_SOURCE_COLUMNS:
        if column not in frame.columns:
            continue
        resolved = resolved.where(resolved.notna(), frame[column])
    return resolved


def build_order_item_export_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path)
    missing = REQUIRED_ITEM_EXPORT_COLUMNS - set(frame.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Excel file is missing required columns: {missing_list}")

    prepared = frame.copy()
    prepared["Mã đơn hàng"] = prepared["Mã đơn hàng"].astype("string").fillna("").str.strip()
    prepared = prepared[prepared["Mã đơn hàng"] != ""].copy()

    prepared["Mã vật tư"] = prepared["SKU phân loại hàng"].map(lambda value: normalize_text(value) or "")
    prepared["Số lượng"] = prepared["Số lượng"].map(lambda value: parse_int(value) or 0)
    prepared["Ngày đặt hàng"] = prepared["Ngày đặt hàng"].map(lambda value: iso_datetime(value) or "")

    total_quantity = prepared.groupby("Mã đơn hàng", sort=False)["Số lượng"].transform("sum")
    prepared["Total Order"] = (prepared["Số lượng"] / total_quantity).round(6)
    process_datetimes = resolve_process_datetimes(prepared)
    prepared["Ngày xử lý đơn hàng"] = process_datetimes.map(format_excel_date)
    prepared["Ngày xử lý đơn hàng detail"] = process_datetimes.map(format_excel_datetime_detail)

    return prepared[ORDER_ITEM_OUTPUT_COLUMNS].reset_index(drop=True)


def export_order_item_report(path: Path, frame: pd.DataFrame) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        return path
    if suffix == ".xlsx":
        frame.to_excel(path, index=False)
        return path
    raise ValueError(f"Unsupported output format: {path.suffix or '(missing suffix)'}")
