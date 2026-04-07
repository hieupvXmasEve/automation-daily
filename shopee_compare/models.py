from __future__ import annotations

from dataclasses import dataclass, field

from .utils import bool_label, slugify_text


@dataclass(slots=True)
class OrderItem:
    name: str
    variant: str | None
    quantity: int
    sku: str | None = None

    def summary(self) -> str:
        label = self.name
        if self.variant:
            label = f"{label} [{self.variant}]"
        return f"{label} x{self.quantity}"

    def missing_summary(self) -> str:
        sku_label = (self.sku or self.name or "")[:4] or "N/A"
        variant_label = self.variant or self.name
        return f"[{sku_label} - {variant_label} - x{self.quantity}]"

    def match_text(self) -> str:
        label = self.name
        if self.variant:
            label = f"{label} {self.variant}"
        return label

    def match_key(self) -> str:
        return slugify_text(self.match_text())

    def name_key(self) -> str:
        return slugify_text(self.name)

    def variant_key(self) -> str:
        return slugify_text(self.variant)


@dataclass(slots=True)
class PdfItem:
    raw_text: str
    quantity: int
    line_number: int
    layout_clipped: bool = False

    def summary(self) -> str:
        return self.raw_text

    def match_key(self) -> str:
        return slugify_text(self.raw_text)


@dataclass(slots=True)
class ExcelOrder:
    order_id: str
    waybill: str | None
    order_datetime: str | None
    order_status: str | None
    recipient_name: str | None
    phone: str | None
    city: str | None
    district: str | None
    ward: str | None
    address: str | None
    total_quantity: int
    line_item_count: int
    item_summary: str
    items: list[OrderItem] = field(default_factory=list)

    def to_row(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "waybill": self.waybill or "",
            "order_datetime": self.order_datetime or "",
            "order_status": self.order_status or "",
            "recipient_name": self.recipient_name or "",
            "phone": self.phone or "",
            "city": self.city or "",
            "district": self.district or "",
            "ward": self.ward or "",
            "address": self.address or "",
            "total_quantity": self.total_quantity,
            "line_item_count": self.line_item_count,
            "item_summary": self.item_summary,
        }


@dataclass(slots=True)
class PdfOrder:
    order_id: str
    waybill: str | None
    order_datetime: str | None
    recipient_name: str | None
    recipient_address: str | None
    total_quantity: int | None
    item_summary: str
    item_lines: list[str]
    items: list[PdfItem]
    template_ok: bool
    template_issues: list[str]
    page_number: int
    max_weight_grams: int | None
    cod_amount_vnd: int | None

    def to_row(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "waybill": self.waybill or "",
            "order_datetime": self.order_datetime or "",
            "recipient_name": self.recipient_name or "",
            "recipient_address": self.recipient_address or "",
            "total_quantity": self.total_quantity if self.total_quantity is not None else "",
            "item_summary": self.item_summary,
            "visible_item_count": len(self.items),
            "visible_total_quantity": sum(item.quantity for item in self.items),
            "template_ok": bool_label(self.template_ok),
            "template_issues": "; ".join(self.template_issues),
            "page_number": self.page_number,
            "max_weight_grams": self.max_weight_grams if self.max_weight_grams is not None else "",
            "cod_amount_vnd": self.cod_amount_vnd if self.cod_amount_vnd is not None else "",
        }


@dataclass(slots=True)
class ComparisonRecord:
    order_id: str
    status: str
    notes: str
    excel_waybill: str | None
    pdf_waybill: str | None
    waybill_match: bool | None
    excel_order_datetime: str | None
    pdf_order_datetime: str | None
    datetime_match: bool | None
    excel_total_quantity: int | None
    pdf_total_quantity: int | None
    quantity_match: bool | None
    item_match_status: str
    pdf_template_ok: bool | None
    pdf_template_issues: str
    expected_item_count: int | None
    pdf_visible_item_count: int | None
    pdf_visible_quantity: int | None
    missing_excel_items: str
    unclear_pdf_items: str
    excel_status: str | None
    excel_recipient_name: str | None
    pdf_recipient_name: str | None
    pdf_page_number: int | None
    excel_item_summary: str | None
    pdf_item_summary: str | None

    def to_row(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "status": self.status,
            "notes": self.notes,
            "excel_waybill": self.excel_waybill or "",
            "pdf_waybill": self.pdf_waybill or "",
            "waybill_match": bool_label(self.waybill_match),
            "excel_order_datetime": self.excel_order_datetime or "",
            "pdf_order_datetime": self.pdf_order_datetime or "",
            "datetime_match": bool_label(self.datetime_match),
            "excel_total_quantity": self.excel_total_quantity if self.excel_total_quantity is not None else "",
            "pdf_total_quantity": self.pdf_total_quantity if self.pdf_total_quantity is not None else "",
            "quantity_match": bool_label(self.quantity_match),
            "item_match_status": self.item_match_status,
            "pdf_template_ok": bool_label(self.pdf_template_ok),
            "pdf_template_issues": self.pdf_template_issues,
            "expected_item_count": self.expected_item_count if self.expected_item_count is not None else "",
            "pdf_visible_item_count": self.pdf_visible_item_count if self.pdf_visible_item_count is not None else "",
            "pdf_visible_quantity": self.pdf_visible_quantity if self.pdf_visible_quantity is not None else "",
            "missing_excel_items": self.missing_excel_items,
            "unclear_pdf_items": self.unclear_pdf_items,
            "excel_status": self.excel_status or "",
            "excel_recipient_name": self.excel_recipient_name or "",
            "pdf_recipient_name": self.pdf_recipient_name or "",
            "pdf_page_number": self.pdf_page_number if self.pdf_page_number is not None else "",
            "excel_item_summary": self.excel_item_summary or "",
            "pdf_item_summary": self.pdf_item_summary or "",
        }
