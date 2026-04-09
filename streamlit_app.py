from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="Marketplace Ops Internal App", layout="wide")


def main() -> None:
    pg = st.navigation([
        st.Page("pages/compare-orders.py", title="Compare Orders", icon="🔍"),
        st.Page("pages/extract-items.py", title="Extract Item Rows", icon="📦"),
        st.Page("pages/tiktok-pdf-audit.py", title="TikTok PDF Audit", icon="🎵"),
        st.Page("pages/mobile-qr-scan.py", title="Mobile QR Scan", icon="📷"),
    ])
    pg.run()


if __name__ == "__main__":
    main()
