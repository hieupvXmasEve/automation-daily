from __future__ import annotations

import streamlit as st

from .marketplace_scan_models import ImportedShopDataset, MarketplaceImportPreview, MarketplaceScanResultRow
from .mobile_qr_scanner_component import render_mobile_qr_scanner
from .streamlit_workflows import (
    build_imported_shop_from_preview,
    build_marketplace_scan_export,
    build_marketplace_scan_frame,
    load_marketplace_import_preview_upload,
    run_marketplace_qr_scan_action,
)


PREVIEW_KEY = "marketplace_qr_import_preview"
SHOPS_KEY = "marketplace_qr_imported_shops"
ROWS_KEY = "marketplace_qr_scan_rows"
EVENT_KEY = "marketplace_qr_last_event"
MARKETPLACE_OPTIONS = ["shopee", "lazada", "tiktok", "website"]


def render_marketplace_qr_scan_tab() -> None:
    _ensure_state()
    st.caption("Open this tab from a secure URL. On phone, use the rear camera. On desktop, choose webcam or Continuity Camera.")
    _render_import_section()
    st.divider()
    _render_scanner_section()
    st.divider()
    _render_results_section()


def _ensure_state() -> None:
    st.session_state.setdefault(PREVIEW_KEY, None)
    st.session_state.setdefault(SHOPS_KEY, [])
    st.session_state.setdefault(ROWS_KEY, [])
    st.session_state.setdefault(EVENT_KEY, None)


def _render_import_section() -> None:
    st.subheader("1. Import Shop Files")
    with st.form("marketplace-import-form"):
        marketplace = st.selectbox("Marketplace", MARKETPLACE_OPTIONS, index=0)
        shop_label = st.text_input("Shop label")
        upload = st.file_uploader("Order file", type=["csv", "xlsx"], key="marketplace-import-file")
        submitted = st.form_submit_button("Load Fields", use_container_width=True)
    if submitted:
        if upload is None or not shop_label.strip():
            st.error("Upload a file and enter a shop label.")
        else:
            try:
                st.session_state[PREVIEW_KEY] = load_marketplace_import_preview_upload(upload, marketplace, shop_label)
                st.success("Fields loaded. Choose one compare field below.")
            except Exception as exc:
                st.error(str(exc))

    preview = st.session_state.get(PREVIEW_KEY)
    if preview:
        _render_preview_form(preview)

    imported_shops = st.session_state[SHOPS_KEY]
    if imported_shops:
        st.dataframe([shop.summary_row() for shop in imported_shops], use_container_width=True, height=220)
        if st.button("Clear Imported Shops", use_container_width=True):
            st.session_state[SHOPS_KEY] = []
            st.session_state[ROWS_KEY] = []
            st.session_state[EVENT_KEY] = None
            st.rerun()


def _render_preview_form(preview: MarketplaceImportPreview) -> None:
    st.write(f"Preview: `{preview.source_file_name}` with `{preview.row_count}` rows.")
    st.dataframe(preview.frame.head(10), use_container_width=True, height=220)
    with st.form("marketplace-import-save-form"):
        compare_field = st.selectbox("Compare field", preview.available_fields, index=0)
        submitted = st.form_submit_button("Save Imported Shop", use_container_width=True)
    if submitted:
        try:
            imported_shop = build_imported_shop_from_preview(preview, compare_field)
            st.session_state[SHOPS_KEY] = _upsert_shop(st.session_state[SHOPS_KEY], imported_shop)
            st.session_state[PREVIEW_KEY] = None
            st.success(f"Imported {imported_shop.shop_label}.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))


def _render_scanner_section() -> None:
    st.subheader("2. Scan QR")
    imported_shops = st.session_state[SHOPS_KEY]
    result = render_mobile_qr_scanner(enabled=bool(imported_shops), key="marketplace-mobile-qr-scanner")
    status = getattr(result, "status", None)
    if isinstance(status, dict) and status.get("kind") == "error":
        st.warning(status.get("message", "Camera unavailable."))
    scan_payload = getattr(result, "scan", None)
    if isinstance(scan_payload, dict) and scan_payload.get("text"):
        _apply_scan(scan_payload["text"], scan_payload.get("source", "camera"))
    with st.form("marketplace-manual-scan-form"):
        manual_text = st.text_input("Manual fallback text", placeholder="Paste QR text if camera is blocked")
        submitted = st.form_submit_button("Submit Fallback Text", use_container_width=True)
    if submitted:
        _apply_scan(manual_text, "manual")
    event = st.session_state.get(EVENT_KEY)
    if event:
        _render_event_feedback(event)


def _render_event_feedback(event: dict[str, str]) -> None:
    status = event["status"]
    if status == "matched":
        st.success(event["message"])
    elif status == "duplicate":
        st.info(event["message"])
    else:
        st.warning(event["message"])


def _apply_scan(scanned_text: str, scan_source: str) -> None:
    result = run_marketplace_qr_scan_action(st.session_state[SHOPS_KEY], st.session_state[ROWS_KEY], scanned_text, scan_source)
    if result["scan_row"] is not None:
        st.session_state[ROWS_KEY].append(result["scan_row"])
    st.session_state[EVENT_KEY] = {"status": result["status"], "message": result["message"]}


def _render_results_section() -> None:
    st.subheader("3. Review Table")
    rows: list[MarketplaceScanResultRow] = st.session_state[ROWS_KEY]
    imported_shops: list[ImportedShopDataset] = st.session_state[SHOPS_KEY]
    top_metrics = st.columns(3)
    top_metrics[0].metric("Imported shops", len(imported_shops))
    top_metrics[1].metric("Matched scans", len(rows))
    top_metrics[2].metric("Unique shops hit", len({row.shop_id for row in rows}))
    filter_options = {"All shops": None} | {shop.shop_label: shop.shop_id for shop in imported_shops}
    selected_label = st.selectbox("Filter by shop", list(filter_options), index=0)
    selected_shop_id = filter_options[selected_label]
    frame = build_marketplace_scan_frame(rows, shop_id=selected_shop_id)
    st.dataframe(frame, use_container_width=True, height=320)
    actions = st.columns(2)
    if actions[0].button("Clear Scan Table", use_container_width=True):
        st.session_state[ROWS_KEY] = []
        st.session_state[EVENT_KEY] = None
        st.rerun()
    export = build_marketplace_scan_export(rows, shop_id=selected_shop_id)
    actions[1].download_button(
        label=f"Download {export['file_name']}",
        data=export["data"],
        file_name=export["file_name"],
        mime=export["mime"],
        use_container_width=True,
        disabled=export["row_count"] == 0,
    )


def _upsert_shop(existing: list[ImportedShopDataset], candidate: ImportedShopDataset) -> list[ImportedShopDataset]:
    kept = [shop for shop in existing if shop.shop_id != candidate.shop_id]
    kept.append(candidate)
    return kept
