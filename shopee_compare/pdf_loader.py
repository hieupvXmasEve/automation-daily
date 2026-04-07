from __future__ import annotations

from pathlib import Path
from statistics import median
import re

import pdfplumber

from .models import PdfItem, PdfOrder
from .utils import join_notes, normalize_lines, normalize_text, parse_int, parse_pdf_datetime


HEADER_RE = re.compile(
    r"Mã vận đơn:\s*(?P<waybill>\S+).*?Mã đơn hàng:\s*(?P<order_id>\S+)",
    re.IGNORECASE | re.DOTALL,
)
DATE_TIME_RE = re.compile(
    r"Ngày đặt hàng:\s*(?P<date>\d{2}-\d{2}-\d{4})(?:\s*(?P<time>\d{2}:\d{2}))?",
    re.IGNORECASE | re.DOTALL,
)
TOTAL_QUANTITY_RE = re.compile(r"Tổng SL sản phẩm:\s*(\d+)", re.IGNORECASE)
WEIGHT_RE = re.compile(r"Khối lượng tối đa:\s*(\d+)\s*g", re.IGNORECASE)
COD_RE = re.compile(r"(\d[\d.]*)\s*VND", re.IGNORECASE)


def load_pdf_orders(path: Path) -> list[PdfOrder]:
    orders: list[PdfOrder] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            blocks = _extract_blocks(page)
            layout_flags = _extract_item_layout_flags(page)
            combined = "\n\n".join(blocks)
            header_block = _find_block(blocks, "Mã vận đơn:") or combined
            header_match = HEADER_RE.search(header_block)
            if not header_match:
                raise ValueError(f"Could not parse order header on PDF page {page_number}")

            recipient_block = _find_block(blocks, "Đến:(Chỉ giao giờ hành chính)")
            item_block = _find_block(blocks, "Nội dung hàng")
            date_block = _find_block(blocks, "Ngày đặt hàng:")
            payment_block = _find_block(blocks, "Khối lượng tối đa:") or _find_block(blocks, "Tiền thu Người nhận:")

            order_datetime = _parse_order_datetime(date_block or combined)
            recipient_name, recipient_address = _parse_recipient_block(recipient_block)
            total_quantity, item_summary, item_lines = _parse_item_block(item_block or combined)
            parsed_items = _parse_pdf_items(item_lines, layout_flags)
            template_issues = _validate_template(combined, item_block, total_quantity, item_lines, parsed_items)

            weight_match = WEIGHT_RE.search(payment_block or combined)
            cod_match = COD_RE.search(payment_block or "")

            orders.append(
                PdfOrder(
                    order_id=header_match.group("order_id").strip(),
                    waybill=header_match.group("waybill").strip(),
                    order_datetime=order_datetime,
                    recipient_name=recipient_name,
                    recipient_address=recipient_address,
                    total_quantity=total_quantity,
                    item_summary=item_summary,
                    item_lines=item_lines,
                    items=parsed_items,
                    template_ok=not template_issues,
                    template_issues=template_issues,
                    page_number=page_number,
                    max_weight_grams=parse_int(weight_match.group(1)) if weight_match else None,
                    cod_amount_vnd=parse_int(cod_match.group(1)) if cod_match else None,
                )
            )
    return orders


def _extract_blocks(page: pdfplumber.page.Page) -> list[str]:
    blocks: list[str] = []
    seen: set[str] = set()
    for table in page.extract_tables() or []:
        for row in table:
            for cell in row:
                text = _normalize_block(cell)
                if text and text not in seen:
                    blocks.append(text)
                    seen.add(text)
    if not blocks:
        text = _normalize_block(page.extract_text() or "")
        if text:
            blocks.append(text)
    return blocks


def _find_block(blocks: list[str], marker: str) -> str | None:
    for block in blocks:
        if marker in block:
            return block
    return None


def _parse_order_datetime(text: str) -> str | None:
    match = DATE_TIME_RE.search(text)
    if not match:
        return None
    return parse_pdf_datetime(match.group("date"), match.group("time"))


def _parse_recipient_block(block: str | None) -> tuple[str | None, str | None]:
    if not block:
        return None, None
    cleaned = re.sub(r"^Đến:\(Chỉ giao giờ hành chính\)\s*", "", block, flags=re.IGNORECASE)
    lines = normalize_lines(cleaned)
    if not lines:
        return None, None
    recipient_name = lines[0]
    recipient_address = " ".join(lines[1:]) if len(lines) > 1 else None
    return recipient_name, recipient_address


def _parse_item_block(block: str) -> tuple[int | None, str, list[str]]:
    quantity_match = TOTAL_QUANTITY_RE.search(block)
    quantity = parse_int(quantity_match.group(1)) if quantity_match else None
    body = re.split(r"Người gửi phải cam kết", block, maxsplit=1, flags=re.IGNORECASE)[0]
    body = re.sub(
        r"Nội dung hàng\s*\(Tổng SL sản phẩm:\s*\d+\)\s*",
        "",
        body,
        flags=re.IGNORECASE,
    )
    segments = [normalize_text(part) for part in re.split(r"(?=\d+\.\s)", body)]
    item_lines = [segment for segment in segments if segment]
    if quantity is None:
        detected = [parse_int(match.group(1)) for match in re.finditer(r"SL:\s*(\d+)", body, flags=re.IGNORECASE)]
        quantity = sum(value for value in detected if value is not None) or None
    summary = join_notes(item_lines)
    return quantity, summary, item_lines


def _normalize_block(value: object) -> str | None:
    if value is None:
        return None
    lines: list[str] = []
    for raw_line in str(value).splitlines():
        line = normalize_text(raw_line)
        if line:
            lines.append(line)
    if not lines:
        return None
    return "\n".join(lines)


def _parse_pdf_items(item_lines: list[str], layout_flags: dict[int, bool]) -> list[PdfItem]:
    items: list[PdfItem] = []
    for line_number, line in enumerate(item_lines, start=1):
        quantity_match = re.search(r"SL\s*:?\s*(\d+)", line, flags=re.IGNORECASE)
        quantity = parse_int(quantity_match.group(1)) if quantity_match else None
        raw_text = re.sub(r"^\d+\.\s*", "", line).strip()
        raw_text = re.sub(r"\s*SL\s*:?\s*\d+\s*$", "", raw_text, flags=re.IGNORECASE).strip(" ,")
        items.append(
            PdfItem(
                raw_text=raw_text or line,
                quantity=quantity or 0,
                line_number=line_number,
                layout_clipped=layout_flags.get(line_number, False),
            )
        )
    return items


def _extract_item_layout_flags(page: pdfplumber.page.Page) -> dict[int, bool]:
    lines = _extract_left_column_lines(page)
    if not lines:
        return {}

    header_index = next((idx for idx, line in enumerate(lines) if line["text"].startswith("Nội dung hàng")), None)
    note_index = next((idx for idx, line in enumerate(lines) if line["text"].startswith("Người gửi phải cam kết")), None)
    if header_index is None or note_index is None or note_index <= header_index:
        return {}

    content_lines = lines[header_index + 1 : note_index]
    item_starts = [line for line in content_lines if re.match(r"^\d+\.", line["text"])]
    if not item_starts:
        return {}

    line_tops = [line["top"] for line in content_lines]
    gaps = [round(curr - prev, 2) for prev, curr in zip(line_tops, line_tops[1:]) if curr - prev > 0.5]
    line_gap = median(gaps) if gaps else 7.5

    flags: dict[int, bool] = {}
    for idx, start in enumerate(item_starts):
        start_top = start["top"]
        next_top = item_starts[idx + 1]["top"] if idx + 1 < len(item_starts) else lines[note_index]["top"]
        item_lines = [line for line in content_lines if start_top <= line["top"] < next_top]
        if not item_lines:
            continue
        last_top = item_lines[-1]["top"]
        flags[idx + 1] = (next_top - last_top) < (line_gap * 0.9)
    return flags


def _extract_left_column_lines(page: pdfplumber.page.Page) -> list[dict[str, object]]:
    words = [
        word
        for word in page.extract_words(use_text_flow=True, keep_blank_chars=False)
        if word["x0"] < 210
    ]
    if not words:
        return []

    lines: list[dict[str, object]] = []
    current_words: list[dict[str, object]] = []
    current_top: float | None = None
    for word in words:
        top = float(word["top"])
        if current_top is None or abs(top - current_top) <= 1.2:
            current_words.append(word)
            current_top = top if current_top is None else current_top
            continue
        lines.append(_build_line(current_words, current_top))
        current_words = [word]
        current_top = top

    if current_words and current_top is not None:
        lines.append(_build_line(current_words, current_top))
    return lines


def _build_line(words: list[dict[str, object]], top: float) -> dict[str, object]:
    ordered = sorted(words, key=lambda word: float(word["x0"]))
    return {
        "top": top,
        "text": " ".join(str(word["text"]) for word in ordered).strip(),
    }


def _validate_template(
    combined: str,
    item_block: str | None,
    total_quantity: int | None,
    item_lines: list[str],
    parsed_items: list[PdfItem],
) -> list[str]:
    issues: list[str] = []
    required_markers = [
        "Mã vận đơn:",
        "Mã đơn hàng:",
        "Nội dung hàng",
        "Người gửi phải cam kết",
    ]
    for marker in required_markers:
        if marker not in combined:
            issues.append(f"missing marker `{marker}`")
    if item_block is None:
        issues.append("missing item block")
    if total_quantity is None:
        issues.append("missing `Tổng SL sản phẩm`")
    if not item_lines:
        issues.append("no item lines detected")
    if any(item.quantity <= 0 for item in parsed_items):
        issues.append("missing `SL:` in at least one item line")
    return issues
