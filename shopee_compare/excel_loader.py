from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import ExcelOrder, OrderItem
from .utils import first_non_empty, iso_datetime, normalize_text, parse_int


REQUIRED_COLUMNS = {
    "Mã đơn hàng",
    "Ngày đặt hàng",
    "Trạng Thái Đơn Hàng",
    "Tên sản phẩm",
    "SKU phân loại hàng",
    "Tên phân loại hàng",
    "Số lượng",
    "Mã vận đơn",
    "Tên Người nhận",
    "Số điện thoại",
    "Tỉnh/Thành phố",
    "TP / Quận / Huyện",
    "Quận",
    "Địa chỉ nhận hàng",
}


def load_excel_orders(path: Path) -> list[ExcelOrder]:
    frame = pd.read_excel(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Excel file is missing required columns: {missing_list}")

    prepared = frame.copy()
    prepared["Mã đơn hàng"] = prepared["Mã đơn hàng"].astype("string").fillna("")
    prepared = prepared[prepared["Mã đơn hàng"].str.strip() != ""]

    orders: list[ExcelOrder] = []
    for order_id, group in prepared.groupby("Mã đơn hàng", sort=False):
        item_totals: dict[tuple[str, str | None, str | None], int] = {}
        total_quantity = 0
        for _, row in group.iterrows():
            quantity = parse_int(row.get("Số lượng")) or 0
            total_quantity += quantity
            item_name = normalize_text(row.get("Tên sản phẩm")) or "Unknown item"
            sku = normalize_text(row.get("SKU phân loại hàng"))
            variant = normalize_text(row.get("Tên phân loại hàng"))
            key = (item_name, sku, variant)
            item_totals[key] = item_totals.get(key, 0) + quantity

        items = [
            OrderItem(name=name, sku=sku, variant=variant, quantity=quantity)
            for (name, sku, variant), quantity in item_totals.items()
        ]

        item_summary = " | ".join(item.summary() for item in items)
        orders.append(
            ExcelOrder(
                order_id=str(order_id).strip(),
                waybill=first_non_empty(group["Mã vận đơn"].tolist()),
                order_datetime=iso_datetime(first_non_empty(group["Ngày đặt hàng"].tolist())),
                order_status=first_non_empty(group["Trạng Thái Đơn Hàng"].tolist()),
                recipient_name=first_non_empty(group["Tên Người nhận"].tolist()),
                phone=first_non_empty(group["Số điện thoại"].tolist()),
                city=first_non_empty(group["Tỉnh/Thành phố"].tolist()),
                district=first_non_empty(group["TP / Quận / Huyện"].tolist()),
                ward=first_non_empty(group["Quận"].tolist()),
                address=first_non_empty(group["Địa chỉ nhận hàng"].tolist()),
                total_quantity=total_quantity,
                line_item_count=len(group.index),
                item_summary=item_summary,
                items=items,
            )
        )
    return orders
