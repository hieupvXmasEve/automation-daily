from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .excel_loader import load_excel_orders
from .exporters import (
    export_comparison_csv,
    export_comparison_excel,
    export_comparison_pdf,
)
from .matcher import VALID_STATUSES, compare_orders
from .order_item_export import build_order_item_export_frame, export_order_item_report
from .pdf_loader import load_pdf_orders


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shopee-compare",
        description="Compare Shopee Excel orders against shipping label PDFs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare_parser = subparsers.add_parser("compare", help="Compare one Excel file with one PDF file.")
    compare_parser.add_argument("--excel", required=True, type=Path, help="Path to Shopee order Excel file.")
    compare_parser.add_argument("--pdf", required=True, type=Path, help="Path to label PDF file.")
    compare_parser.add_argument(
        "--formats",
        nargs="+",
        choices=("csv", "excel", "pdf"),
        default=["csv", "excel", "pdf"],
        help="Export formats to generate.",
    )
    compare_parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory. Defaults to output/<timestamp>.",
    )
    compare_parser.add_argument(
        "--only",
        nargs="+",
        choices=VALID_STATUSES,
        default=None,
        help="Export only selected comparison statuses.",
    )
    compare_parser.set_defaults(handler=handle_compare)

    extract_items_parser = subparsers.add_parser(
        "extract-items",
        help="Export Shopee Excel rows into item-level order lines.",
    )
    extract_items_parser.add_argument("--excel", required=True, type=Path, help="Path to Shopee order Excel file.")
    extract_items_parser.add_argument(
        "--format",
        choices=("excel", "csv"),
        default="excel",
        help="Output format to generate.",
    )
    extract_items_parser.add_argument(
        "--out-file",
        type=Path,
        default=None,
        help="Output file path. Defaults to output/<timestamp>/order-items.<ext>.",
    )
    extract_items_parser.set_defaults(handler=handle_extract_items)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)


def handle_compare(args: argparse.Namespace) -> int:
    excel_path: Path = args.excel
    pdf_path: Path = args.pdf
    if not excel_path.is_file():
        raise SystemExit(f"Excel file not found: {excel_path}")
    if not pdf_path.is_file():
        raise SystemExit(f"PDF file not found: {pdf_path}")

    output_dir = args.out_dir or Path("output") / datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[1/4] Validate input files")
    print(f"  Excel: {excel_path}")
    print(f"  PDF  : {pdf_path}")

    print("[2/4] Parse sources")
    excel_orders = load_excel_orders(excel_path)
    pdf_orders = load_pdf_orders(pdf_path)
    print(f"  Excel orders     : {len(excel_orders)}")
    print(f"  PDF labels/pages : {len(pdf_orders)}")

    print("[3/4] Compare orders")
    comparison_rows, summary = compare_orders(excel_orders, pdf_orders)
    exported_rows = comparison_rows
    if args.only:
        exported_rows = [row for row in comparison_rows if row.status in set(args.only)]
    print(f"  Matched          : {summary['matched']}")
    print(f"  Mismatch         : {summary['mismatch']}")
    print(f"  Missing in Excel : {summary['missing_in_excel']}")
    print(f"  Missing in PDF   : {summary['missing_in_pdf']}")

    print("[4/4] Export reports")
    exported_paths: list[Path] = []
    formats = list(dict.fromkeys(args.formats))
    if "csv" in formats:
        csv_path = output_dir / "comparison.csv"
        export_comparison_csv(csv_path, exported_rows)
        exported_paths.append(csv_path)
    if "excel" in formats:
        excel_output = output_dir / "comparison.xlsx"
        export_comparison_excel(excel_output, exported_rows, excel_orders, pdf_orders)
        exported_paths.append(excel_output)
    if "pdf" in formats:
        pdf_output = output_dir / "comparison.pdf"
        export_comparison_pdf(pdf_output, exported_rows, summary)
        exported_paths.append(pdf_output)

    for path in exported_paths:
        print(f"  {path.suffix[1:].upper():5}: {path}")

    print("Done.")
    return 0


def handle_extract_items(args: argparse.Namespace) -> int:
    excel_path: Path = args.excel
    if not excel_path.is_file():
        raise SystemExit(f"Excel file not found: {excel_path}")

    suffix = ".xlsx" if args.format == "excel" else ".csv"
    output_path = args.out_file or Path("output") / datetime.now().strftime("%Y%m%d-%H%M%S") / f"order-items{suffix}"

    print("[1/3] Validate input file")
    print(f"  Excel: {excel_path}")

    print("[2/3] Build item rows")
    export_frame = build_order_item_export_frame(excel_path)
    print(f"  Item rows: {len(export_frame)}")

    print("[3/3] Export report")
    export_order_item_report(output_path, export_frame)
    print(f"  FILE : {output_path}")
    print("Done.")
    return 0
