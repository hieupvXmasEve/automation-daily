from __future__ import annotations

import argparse
from pathlib import Path

from .matcher import VALID_STATUSES
from .services import CompareRunRequest, ExtractItemsRunRequest, run_compare, run_extract_items


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
    request = CompareRunRequest(
        excel_path=args.excel,
        pdf_path=args.pdf,
        formats=tuple(args.formats),
        out_dir=args.out_dir,
        only_statuses=tuple(args.only) if args.only else None,
    )

    print("[1/4] Validate input files")
    print(f"  Excel: {request.excel_path}")
    print(f"  PDF  : {request.pdf_path}")

    result = run_compare(request)

    print("[2/4] Parse sources")
    print(f"  Excel orders     : {len(result.excel_orders)}")
    print(f"  PDF labels/pages : {len(result.pdf_orders)}")

    print("[3/4] Compare orders")
    summary = result.summary
    print(f"  Matched          : {summary['matched']}")
    print(f"  Mismatch         : {summary['mismatch']}")
    print(f"  Missing in Excel : {summary['missing_in_excel']}")
    print(f"  Missing in PDF   : {summary['missing_in_pdf']}")

    print("[4/4] Export reports")
    for path in result.exported_paths:
        print(f"  {path.suffix[1:].upper():5}: {path}")

    print("Done.")
    return 0


def handle_extract_items(args: argparse.Namespace) -> int:
    request = ExtractItemsRunRequest(
        excel_path=args.excel,
        export_format=args.format,
        output_path=args.out_file,
    )

    print("[1/3] Validate input file")
    print(f"  Excel: {request.excel_path}")

    result = run_extract_items(request)

    print("[2/3] Build item rows")
    print(f"  Item rows: {result.row_count}")

    print("[3/3] Export report")
    print(f"  FILE : {result.output_path}")
    print("Done.")
    return 0
