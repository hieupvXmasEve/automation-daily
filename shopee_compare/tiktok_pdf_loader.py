from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
import re

import pdfplumber

from .utils import normalize_lines, normalize_text, parse_float, parse_int


ORDER_ID_RE = re.compile(r"Order ID:\s*(\d+)", re.IGNORECASE)
PACKAGE_ID_RE = re.compile(r"Package ID:\s*(\d+)", re.IGNORECASE)
ORDER_TIME_RE = re.compile(r"Thời gian đặt hàng:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2})")
TOTAL_QTY_RE = re.compile(r"Qty Total:\s*(\d+)", re.IGNORECASE)
WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*KG", re.IGNORECASE)
PHONE_RE = re.compile(r"\(\+84\).*")
WEIGHT_LINE_RE = re.compile(r"^\d+(?:\.\d+)?\s*KG$", re.IGNORECASE)
@dataclass(slots=True)
class TikTokPdfPageRecord:
    order_id: str
    page_number: int
    waybill: str | None
    package_id: str | None
    order_datetime: str | None
    recipient_name: str | None
    recipient_region: str | None
    total_quantity: int | None
    weight_kg: float | None
    product_text: str | None

@dataclass(slots=True)
class TikTokPdfOrder:
    order_id: str
    waybill: str | None
    package_id: str | None
    order_datetime: str | None
    recipient_name: str | None
    recipient_region: str | None
    total_quantity: int | None
    weight_kg: float | None
    page_numbers: list[int] = field(default_factory=list)
    product_segments: list[str] = field(default_factory=list)

    @property
    def first_page(self) -> int:
        return min(self.page_numbers)

    @property
    def page_count(self) -> int:
        return len(self.page_numbers)

    @property
    def pages_label(self) -> str:
        return ", ".join(str(page_number) for page_number in self.page_numbers)

    @property
    def product_summary(self) -> str:
        return " | ".join(self.product_segments)

    def to_row(self) -> dict[str, object]:
        return {
            "first_page": self.first_page,
            "pages": self.pages_label,
            "page_count": self.page_count,
            "order_id": self.order_id,
            "package_id": self.package_id or "",
            "waybill": self.waybill or "",
            "order_datetime": self.order_datetime or "",
            "recipient_name": self.recipient_name or "",
            "recipient_region": self.recipient_region or "",
            "total_quantity": self.total_quantity if self.total_quantity is not None else "",
            "weight_kg": self.weight_kg if self.weight_kg is not None else "",
            "product_summary": self.product_summary,
        }

@dataclass(slots=True)
class TikTokPdfParseResult:
    pdf_page_count: int
    page_records: list[TikTokPdfPageRecord]
    orders: list[TikTokPdfOrder]


def load_tiktok_pdf_orders(path: Path) -> TikTokPdfParseResult:
    page_records: list[TikTokPdfPageRecord] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_records.append(_parse_page(page_number, page.extract_text() or ""))
    return TikTokPdfParseResult(
        pdf_page_count=len(page_records),
        page_records=page_records,
        orders=aggregate_tiktok_orders(page_records),
    )


def aggregate_tiktok_orders(page_records: list[TikTokPdfPageRecord]) -> list[TikTokPdfOrder]:
    grouped: OrderedDict[str, TikTokPdfOrder] = OrderedDict()
    for record in page_records:
        order = grouped.get(record.order_id)
        if order is None:
            grouped[record.order_id] = TikTokPdfOrder(
                order_id=record.order_id,
                waybill=record.waybill,
                package_id=record.package_id,
                order_datetime=record.order_datetime,
                recipient_name=record.recipient_name,
                recipient_region=record.recipient_region,
                total_quantity=record.total_quantity,
                weight_kg=record.weight_kg,
                page_numbers=[record.page_number],
                product_segments=[record.product_text] if record.product_text else [],
            )
            continue

        order.waybill = order.waybill or record.waybill
        order.package_id = order.package_id or record.package_id
        order.order_datetime = order.order_datetime or record.order_datetime
        order.recipient_name = order.recipient_name or record.recipient_name
        order.recipient_region = order.recipient_region or record.recipient_region
        order.total_quantity = order.total_quantity if order.total_quantity is not None else record.total_quantity
        order.weight_kg = order.weight_kg if order.weight_kg is not None else record.weight_kg
        if record.page_number not in order.page_numbers:
            order.page_numbers.append(record.page_number)
        if record.product_text and record.product_text not in order.product_segments:
            order.product_segments.append(record.product_text)

    return list(grouped.values())


def _parse_page(page_number: int, text: str) -> TikTokPdfPageRecord:
    order_id = _required_match(ORDER_ID_RE, text, f"Order ID not found on page {page_number}")
    lines = normalize_lines(text)
    recipient_name, recipient_region = _parse_recipient(lines)
    return TikTokPdfPageRecord(
        order_id=order_id,
        page_number=page_number,
        waybill=_parse_waybill(lines),
        package_id=_optional_match(PACKAGE_ID_RE, text),
        order_datetime=_optional_match(ORDER_TIME_RE, text),
        recipient_name=recipient_name,
        recipient_region=recipient_region,
        total_quantity=parse_int(_optional_match(TOTAL_QTY_RE, text)),
        weight_kg=parse_float(_optional_match(WEIGHT_RE, text)),
        product_text=_parse_product_text(lines),
    )


def _parse_waybill(lines: list[str]) -> str | None:
    for line in lines:
        if line.startswith("Order ID:"):
            break
        if re.fullmatch(r"\d{10,}", line):
            return line
    return None


def _parse_recipient(lines: list[str]) -> tuple[str | None, str | None]:
    marker_index = next((index for index, line in enumerate(lines) if line.startswith("J&T tuyển shipper")), None)
    if marker_index is None:
        return None, None

    recipient_lines: list[str] = []
    for line in lines[marker_index + 1 :]:
        if ORDER_TIME_RE.search(line) or line.startswith("In transit by:") or line.startswith("Product Name"):
            break
        if line in {"COD", "KHÔNG TIỀN MẶT"} or WEIGHT_LINE_RE.fullmatch(line) or PHONE_RE.fullmatch(line):
            continue
        recipient_lines.append(line)

    if not recipient_lines:
        return None, None
    return recipient_lines[0], normalize_text(" ".join(recipient_lines[1:]))


def _parse_product_text(lines: list[str]) -> str | None:
    start_index = next((index for index, line in enumerate(lines) if line.startswith("Product Name SKU Seller SKU Qty")), None)
    if start_index is None:
        return None

    product_lines: list[str] = []
    for line in lines[start_index + 1 :]:
        if line.startswith("Qty Total:") or line.startswith("Order ID:") or line.startswith("Package ID:"):
            break
        product_lines.append(line)
    return normalize_text(" ".join(product_lines))


def _optional_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return normalize_text(match.group(1)) if match else None


def _required_match(pattern: re.Pattern[str], text: str, error_message: str) -> str:
    value = _optional_match(pattern, text)
    if not value:
        raise ValueError(error_message)
    return value
