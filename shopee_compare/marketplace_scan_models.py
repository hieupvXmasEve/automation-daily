from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .utils import normalize_lookup_text


SCAN_RESULT_COLUMNS = [
    "scanned_at",
    "scan_source",
    "scanned_text",
    "marketplace",
    "shop_label",
    "compare_field",
    "matched_value",
    "source_order_reference",
    "source_reference_field",
    "source_file",
    "status",
    "notes",
]


@dataclass(slots=True)
class ImportedShopRow:
    row_number: int
    compare_value: str
    normalized_compare_value: str
    source_order_reference: str
    source_reference_field: str


@dataclass(slots=True)
class MarketplaceImportPreview:
    marketplace: str
    shop_label: str
    source_file_name: str
    frame: pd.DataFrame
    available_fields: list[str]
    row_count: int


@dataclass(slots=True)
class ImportedShopDataset:
    shop_id: str
    marketplace: str
    shop_label: str
    source_file_name: str
    compare_field: str
    available_fields: list[str]
    row_count: int
    rows: list[ImportedShopRow]
    lookup: dict[str, list[ImportedShopRow]] = field(default_factory=dict)

    def summary_row(self) -> dict[str, object]:
        return {
            "shop_label": self.shop_label,
            "marketplace": self.marketplace,
            "compare_field": self.compare_field,
            "rows": self.row_count,
            "source_file": self.source_file_name,
        }


@dataclass(slots=True)
class ScanMatchCandidate:
    dataset: ImportedShopDataset
    row: ImportedShopRow


@dataclass(slots=True)
class MarketplaceScanResultRow:
    shop_id: str
    scanned_at: str
    scan_source: str
    scanned_text: str
    marketplace: str
    shop_label: str
    compare_field: str
    matched_value: str
    source_order_reference: str
    source_reference_field: str
    source_file: str
    status: str
    notes: str

    def dedupe_key(self) -> str:
        return f"{self.shop_id}:{self.compare_field}:{normalize_lookup_text(self.matched_value)}"

    def to_row(self) -> dict[str, object]:
        return {
            "scanned_at": self.scanned_at,
            "scan_source": self.scan_source,
            "scanned_text": self.scanned_text,
            "marketplace": self.marketplace,
            "shop_label": self.shop_label,
            "compare_field": self.compare_field,
            "matched_value": self.matched_value,
            "source_order_reference": self.source_order_reference,
            "source_reference_field": self.source_reference_field,
            "source_file": self.source_file,
            "status": self.status,
            "notes": self.notes,
        }


@dataclass(slots=True)
class MarketplaceScanEvent:
    status: str
    message: str
    scan_row: MarketplaceScanResultRow | None = None

