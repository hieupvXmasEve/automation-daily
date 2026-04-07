from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..excel_loader import load_excel_orders
from ..exporters import export_comparison_csv, export_comparison_excel, export_comparison_pdf
from ..matcher import VALID_STATUSES, compare_orders
from ..models import ComparisonRecord, ExcelOrder, PdfOrder
from ..pdf_loader import load_pdf_orders


VALID_EXPORT_FORMATS = ("csv", "excel", "pdf")


@dataclass(slots=True)
class CompareRunRequest:
    excel_path: Path
    pdf_path: Path
    formats: tuple[str, ...] = VALID_EXPORT_FORMATS
    out_dir: Path | None = None
    only_statuses: tuple[str, ...] | None = None


@dataclass(slots=True)
class CompareRunResult:
    output_dir: Path
    excel_orders: list[ExcelOrder]
    pdf_orders: list[PdfOrder]
    comparison_rows: list[ComparisonRecord]
    exported_rows: list[ComparisonRecord]
    summary: dict[str, int]
    exported_paths: list[Path]


def run_compare(request: CompareRunRequest) -> CompareRunResult:
    _validate_input_file(request.excel_path, "Excel")
    _validate_input_file(request.pdf_path, "PDF")

    formats = _normalize_choices(request.formats, VALID_EXPORT_FORMATS, "format")
    only_statuses = _normalize_choices(request.only_statuses, VALID_STATUSES, "status")
    output_dir = request.out_dir or Path("output") / datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_orders = load_excel_orders(request.excel_path)
    pdf_orders = load_pdf_orders(request.pdf_path)
    comparison_rows, summary = compare_orders(excel_orders, pdf_orders)
    exported_rows = comparison_rows
    if only_statuses is not None:
        exported_rows = [row for row in comparison_rows if row.status in set(only_statuses)]

    exported_paths = _export_reports(output_dir, formats, exported_rows, excel_orders, pdf_orders, summary)
    return CompareRunResult(
        output_dir=output_dir,
        excel_orders=excel_orders,
        pdf_orders=pdf_orders,
        comparison_rows=comparison_rows,
        exported_rows=exported_rows,
        summary=summary,
        exported_paths=exported_paths,
    )


def _validate_input_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{label} file not found: {path}")


def _normalize_choices(
    values: tuple[str, ...] | list[str] | None,
    valid_values: tuple[str, ...],
    label: str,
) -> tuple[str, ...] | None:
    if values is None:
        return None
    unique_values = tuple(dict.fromkeys(values))
    invalid = [value for value in unique_values if value not in valid_values]
    if invalid:
        raise ValueError(f"Unsupported {label} values: {', '.join(invalid)}")
    return unique_values


def _export_reports(
    output_dir: Path,
    formats: tuple[str, ...] | None,
    comparison_rows: list[ComparisonRecord],
    excel_orders: list[ExcelOrder],
    pdf_orders: list[PdfOrder],
    summary: dict[str, int],
) -> list[Path]:
    if not formats:
        return []

    exported_paths: list[Path] = []
    if "csv" in formats:
        csv_path = output_dir / "comparison.csv"
        export_comparison_csv(csv_path, comparison_rows)
        exported_paths.append(csv_path)
    if "excel" in formats:
        excel_path = output_dir / "comparison.xlsx"
        export_comparison_excel(excel_path, comparison_rows, excel_orders, pdf_orders)
        exported_paths.append(excel_path)
    if "pdf" in formats:
        pdf_path = output_dir / "comparison.pdf"
        export_comparison_pdf(pdf_path, comparison_rows, summary)
        exported_paths.append(pdf_path)
    return exported_paths
