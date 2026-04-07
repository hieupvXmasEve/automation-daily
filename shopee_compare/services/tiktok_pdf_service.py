from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..tiktok_pdf_loader import TikTokPdfOrder, load_tiktok_pdf_orders


VALID_TIKTOK_EXPORT_FORMATS = ("csv", "excel")
TIKTOK_AUDIT_COLUMNS = [
    "first_page",
    "pages",
    "page_count",
    "order_id",
    "package_id",
    "waybill",
    "order_datetime",
    "recipient_name",
    "recipient_region",
    "total_quantity",
    "weight_kg",
    "product_summary",
]


@dataclass(slots=True)
class TikTokPdfAuditRunRequest:
    pdf_path: Path
    export_format: str = "excel"
    output_path: Path | None = None


@dataclass(slots=True)
class TikTokPdfAuditRunResult:
    output_path: Path
    orders: list[TikTokPdfOrder]
    frame: pd.DataFrame
    row_count: int
    summary: dict[str, int]


def run_tiktok_pdf_audit(request: TikTokPdfAuditRunRequest) -> TikTokPdfAuditRunResult:
    if not request.pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {request.pdf_path}")
    if request.export_format not in VALID_TIKTOK_EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {request.export_format}")

    parsed = load_tiktok_pdf_orders(request.pdf_path)
    frame = pd.DataFrame([order.to_row() for order in parsed.orders], columns=TIKTOK_AUDIT_COLUMNS)
    if not frame.empty:
        frame = frame.sort_values(by=["first_page", "order_id"], kind="stable").reset_index(drop=True)

    suffix = ".xlsx" if request.export_format == "excel" else ".csv"
    output_path = request.output_path or Path("output") / f"tiktok-pdf-orders{suffix}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_export(frame, output_path, request.export_format)

    summary = {
        "pdf_pages": parsed.pdf_page_count,
        "unique_orders": len(parsed.orders),
        "multi_page_orders": sum(order.page_count > 1 for order in parsed.orders),
        "extra_pages": max(parsed.pdf_page_count - len(parsed.orders), 0),
        "total_quantity": sum(order.total_quantity or 0 for order in parsed.orders),
    }
    return TikTokPdfAuditRunResult(
        output_path=output_path,
        orders=parsed.orders,
        frame=frame,
        row_count=len(frame.index),
        summary=summary,
    )


def _write_export(frame: pd.DataFrame, output_path: Path, export_format: str) -> None:
    if export_format == "excel":
        frame.to_excel(output_path, index=False)
        return
    frame.to_csv(output_path, index=False, encoding="utf-8-sig")
