from __future__ import annotations

import streamlit as st

from shopee_compare.streamlit_existing_tabs import render_compare_tab, render_extract_tab, render_tiktok_audit_tab
from shopee_compare.streamlit_marketplace_qr_scan_tab import render_marketplace_qr_scan_tab


st.set_page_config(page_title="Marketplace Ops Internal App", layout="wide")


def main() -> None:
    st.title("Marketplace Ops Internal App")
    st.caption("Internal Streamlit UI for compare, item export, TikTok audit, and mobile QR scan.")

    compare_tab, extract_tab, tiktok_tab, qr_tab = st.tabs(
        ["Compare Orders", "Extract Item Rows", "TikTok PDF Audit", "Mobile QR Scan"]
    )
    with compare_tab:
        render_compare_tab()
    with extract_tab:
        render_extract_tab()
    with tiktok_tab:
        render_tiktok_audit_tab()
    with qr_tab:
        render_marketplace_qr_scan_tab()

if __name__ == "__main__":
    main()
