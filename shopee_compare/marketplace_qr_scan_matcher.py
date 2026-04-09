from __future__ import annotations

from .marketplace_scan_models import ImportedShopDataset, MarketplaceScanEvent, MarketplaceScanResultRow, ScanMatchCandidate
from .utils import normalize_lookup_text, sanitize_scanned_text


def find_scan_matches(imported_shops: list[ImportedShopDataset], scanned_text: str) -> list[ScanMatchCandidate]:
    normalized = normalize_lookup_text(scanned_text)
    if not normalized:
        return []

    matches: list[ScanMatchCandidate] = []
    for dataset in imported_shops:
        for row in dataset.lookup.get(normalized, []):
            matches.append(ScanMatchCandidate(dataset=dataset, row=row))
    return matches


def resolve_scan_event(
    imported_shops: list[ImportedShopDataset],
    existing_rows: list[MarketplaceScanResultRow],
    scanned_text: str,
    scan_source: str,
    scanned_at: str,
) -> MarketplaceScanEvent:
    sanitized = sanitize_scanned_text(scanned_text)
    if not sanitized:
        return MarketplaceScanEvent(status="not-found", message="QR text is empty.")

    matches = find_scan_matches(imported_shops, sanitized)
    if not matches:
        return MarketplaceScanEvent(status="not-found", message=f"Not found: {sanitized}")
    if len(matches) > 1:
        notes = ", ".join(
            f"{match.dataset.shop_label}:{match.row.source_order_reference}" for match in matches[:3]
        )
        suffix = "..." if len(matches) > 3 else ""
        return MarketplaceScanEvent(
            status="ambiguous",
            message=f"Ambiguous match for {sanitized}: {notes}{suffix}",
        )

    match = matches[0]
    scan_row = MarketplaceScanResultRow(
        shop_id=match.dataset.shop_id,
        scanned_at=scanned_at,
        scan_source=scan_source,
        scanned_text=sanitized,
        marketplace=match.dataset.marketplace,
        shop_label=match.dataset.shop_label,
        compare_field=match.dataset.compare_field,
        matched_value=match.row.compare_value,
        source_order_reference=match.row.source_order_reference,
        source_reference_field=match.row.source_reference_field,
        source_file=match.dataset.source_file_name,
        status="matched",
        notes="Matched from imported shop file.",
    )
    if any(row.dedupe_key() == scan_row.dedupe_key() for row in existing_rows):
        return MarketplaceScanEvent(
            status="duplicate",
            message=f"Duplicate scan ignored for {scan_row.shop_label} / {scan_row.source_order_reference}.",
        )
    return MarketplaceScanEvent(
        status="matched",
        message=f"Matched {scan_row.shop_label} / {scan_row.source_order_reference}.",
        scan_row=scan_row,
    )
