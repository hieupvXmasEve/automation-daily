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


def build_scan_rows(
    matches: list[ScanMatchCandidate],
    scanned_text: str,
    scan_source: str,
    scanned_at: str,
) -> list[MarketplaceScanResultRow]:
    return [
        MarketplaceScanResultRow(
            shop_id=match.dataset.shop_id,
            source_row_number=match.row.row_number,
            scanned_at=scanned_at,
            scan_source=scan_source,
            scanned_text=scanned_text,
            marketplace=match.dataset.marketplace,
            shop_label=match.dataset.shop_label,
            compare_field=match.dataset.compare_field,
            matched_value=match.row.compare_value,
            source_order_reference=match.row.source_order_reference,
            source_reference_field=match.row.source_reference_field,
            source_file=match.dataset.source_file_name,
            status="matched",
            notes="Matched from imported shop file.",
            raw_data=match.row.raw_data,
        )
        for match in matches
    ]


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

    existing_keys = {row.dedupe_key() for row in existing_rows}
    candidate_rows = build_scan_rows(matches, sanitized, scan_source, scanned_at)
    new_rows: list[MarketplaceScanResultRow] = []
    skipped_count = 0
    for row in candidate_rows:
        key = row.dedupe_key()
        if key in existing_keys:
            skipped_count += 1
            continue
        existing_keys.add(key)
        new_rows.append(row)

    if not new_rows:
        return MarketplaceScanEvent(
            status="duplicate",
            message=f"All {skipped_count} matching rows for {sanitized} already exist in the preview table.",
        )

    if skipped_count:
        return MarketplaceScanEvent(
            status="matched",
            message=f"Added {len(new_rows)} matching rows for {sanitized}. Skipped {skipped_count} rows already in the preview table.",
            scan_rows=new_rows,
        )

    return MarketplaceScanEvent(
        status="matched",
        message=f"Added {len(new_rows)} matching rows for {sanitized}.",
        scan_rows=new_rows,
    )
