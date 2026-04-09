from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from .marketplace_scan_importer import build_imported_shop_dataset, load_marketplace_import_preview
from .marketplace_scan_models import ImportedShopDataset, MarketplaceImportPreview, MarketplaceScanResultRow
from .services import (
    CompareRunRequest,
    ExtractItemsRunRequest,
    MarketplaceQrScanRequest,
    TikTokPdfAuditRunRequest,
    build_scan_rows_frame,
    export_scan_rows_excel,
    run_compare,
    run_extract_items,
    run_marketplace_qr_scan,
    run_tiktok_pdf_audit,
    temporary_upload_workspace,
)


DOWNLOAD_MIME_TYPES = {
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pdf": "application/pdf",
}


def run_compare_uploads(
    excel_file: object,
    pdf_file: object,
    formats: list[str],
    only_statuses: list[str],
) -> dict[str, object]:
    with temporary_upload_workspace() as workspace, TemporaryDirectory(prefix="shopee-compare-output-") as output_root:
        excel_path = workspace.write_upload(excel_file, "orders.xlsx")
        pdf_path = workspace.write_upload(pdf_file, "labels.pdf")
        result = run_compare(
            CompareRunRequest(
                excel_path=excel_path,
                pdf_path=pdf_path,
                formats=tuple(formats),
                out_dir=Path(output_root),
                only_statuses=tuple(only_statuses) if only_statuses else None,
            )
        )
        downloads = {path.name: build_download_payload(path) for path in result.exported_paths}

    return {
        "summary": result.summary,
        "frame": pd.DataFrame([row.to_row() for row in result.exported_rows]),
        "downloads": downloads,
        "filter_label": ", ".join(only_statuses) if only_statuses else "all statuses",
    }


def run_extract_upload(excel_file: object, export_format: str) -> dict[str, object]:
    with temporary_upload_workspace() as workspace, TemporaryDirectory(prefix="shopee-items-output-") as output_root:
        excel_path = workspace.write_upload(excel_file, "orders.xlsx")
        output_name = "order-items.xlsx" if export_format == "excel" else "order-items.csv"
        result = run_extract_items(
            ExtractItemsRunRequest(
                excel_path=excel_path,
                export_format=export_format,
                output_path=Path(output_root) / output_name,
            )
        )
        data = result.output_path.read_bytes()

    return {
        "frame": result.frame,
        "row_count": result.row_count,
        "file_name": result.output_path.name,
        "data": data,
        "mime": DOWNLOAD_MIME_TYPES[result.output_path.suffix],
    }


def run_tiktok_pdf_audit_upload(pdf_file: object, export_format: str) -> dict[str, object]:
    with temporary_upload_workspace() as workspace, TemporaryDirectory(prefix="tiktok-pdf-output-") as output_root:
        pdf_path = workspace.write_upload(pdf_file, "tiktok-labels.pdf")
        output_name = "tiktok-pdf-orders.xlsx" if export_format == "excel" else "tiktok-pdf-orders.csv"
        result = run_tiktok_pdf_audit(
            TikTokPdfAuditRunRequest(
                pdf_path=pdf_path,
                export_format=export_format,
                output_path=Path(output_root) / output_name,
            )
        )
        data = result.output_path.read_bytes()

    return {
        "summary": result.summary,
        "frame": result.frame,
        "row_count": result.row_count,
        "file_name": result.output_path.name,
        "data": data,
        "mime": DOWNLOAD_MIME_TYPES[result.output_path.suffix],
    }


def load_marketplace_import_preview_upload(
    upload_file: object,
    marketplace: str,
    shop_label: str,
) -> MarketplaceImportPreview:
    with temporary_upload_workspace() as workspace:
        source_path = workspace.write_upload(upload_file, "marketplace-import")
        return load_marketplace_import_preview(source_path, marketplace=marketplace, shop_label=shop_label)


def build_imported_shop_from_preview(
    preview: MarketplaceImportPreview,
    compare_field: str,
) -> ImportedShopDataset:
    return build_imported_shop_dataset(preview, compare_field)


def run_marketplace_qr_scan_action(
    imported_shops: list[ImportedShopDataset],
    existing_rows: list[MarketplaceScanResultRow],
    scanned_text: str,
    scan_source: str,
) -> dict[str, object]:
    event = run_marketplace_qr_scan(
        MarketplaceQrScanRequest(
            imported_shops=imported_shops,
            existing_rows=existing_rows,
            scanned_text=scanned_text,
            scan_source=scan_source,
        )
    )
    return {
        "status": event.status,
        "message": event.message,
        "scan_row": event.scan_row,
    }


def build_marketplace_scan_export(
    rows: list[MarketplaceScanResultRow],
    shop_id: str | None = None,
) -> dict[str, object]:
    with TemporaryDirectory(prefix="marketplace-qr-output-") as output_root:
        result = export_scan_rows_excel(Path(output_root) / "marketplace-qr-scan-results.xlsx", rows, shop_id=shop_id)
        data = result.output_path.read_bytes()
    return {
        "frame": result.frame,
        "row_count": len(result.frame.index),
        "file_name": result.output_path.name,
        "data": data,
        "mime": DOWNLOAD_MIME_TYPES[result.output_path.suffix],
    }


def build_marketplace_scan_frame(
    rows: list[MarketplaceScanResultRow],
    shop_id: str | None = None,
) -> pd.DataFrame:
    return build_scan_rows_frame(rows, shop_id=shop_id)


def build_download_payload(path: Path) -> dict[str, object]:
    return {
        "data": path.read_bytes(),
        "mime": DOWNLOAD_MIME_TYPES.get(path.suffix, "application/octet-stream"),
    }
