from __future__ import annotations

import csv
from pathlib import Path

from ..models import ComparisonRecord


def export_comparison_csv(path: Path, comparison_rows: list[ComparisonRecord]) -> None:
    rows = [record.to_row() for record in comparison_rows]
    fieldnames = list(rows[0].keys()) if rows else ["order_id", "status", "notes"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
