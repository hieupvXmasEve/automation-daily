from __future__ import annotations

from datetime import datetime
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

from ..models import ComparisonRecord


FONT_CANDIDATES = (
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/SFNSMono.ttf",
)


def export_comparison_pdf(
    path: Path,
    comparison_rows: list[ComparisonRecord],
    summary: dict[str, int],
) -> None:
    lines = _build_lines(comparison_rows, summary)
    pages = _render_pages(lines)
    if not pages:
        raise ValueError("No PDF pages were generated")
    first, *rest = pages
    first.save(path, "PDF", resolution=150.0, save_all=True, append_images=rest)


def _build_lines(comparison_rows: list[ComparisonRecord], summary: dict[str, int]) -> list[str]:
    lines = [
        "Shopee Order Comparison Report",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Summary",
        f"- Excel orders     : {summary['excel_orders']}",
        f"- PDF labels       : {summary['pdf_orders']}",
        f"- Matched          : {summary['matched']}",
        f"- Mismatch         : {summary['mismatch']}",
        f"- Missing in Excel : {summary['missing_in_excel']}",
        f"- Missing in PDF   : {summary['missing_in_pdf']}",
        "",
        "Rows",
    ]
    for row in comparison_rows:
        note = row.notes or "-"
        line = (
            f"{row.status.upper()} | {row.order_id} | "
            f"EX:{row.excel_waybill or '-'} | "
            f"PDF:{row.pdf_waybill or '-'} | "
            f"QTY:{row.excel_total_quantity if row.excel_total_quantity is not None else '-'}"
            f"/{row.pdf_total_quantity if row.pdf_total_quantity is not None else '-'} | "
            f"{note}"
        )
        lines.extend(textwrap.wrap(line, width=92) or [""])
    return lines


def _render_pages(lines: list[str]) -> list[Image.Image]:
    font = _load_font()
    title_font = _load_font(size=26)
    page_width, page_height = 1240, 1754
    margin = 70
    line_height = 34
    title_gap = 20

    pages: list[Image.Image] = []
    image = Image.new("RGB", (page_width, page_height), "white")
    draw = ImageDraw.Draw(image)
    y = margin

    for index, line in enumerate(lines):
        current_font = title_font if index == 0 else font
        current_height = line_height + (title_gap if index == 0 else 0)
        if y + current_height > page_height - margin:
            pages.append(image)
            image = Image.new("RGB", (page_width, page_height), "white")
            draw = ImageDraw.Draw(image)
            y = margin
        draw.text((margin, y), line, fill="black", font=current_font)
        y += current_height

    pages.append(image)
    return pages


def _load_font(size: int = 20) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()
