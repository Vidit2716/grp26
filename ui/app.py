from __future__ import annotations

import streamlit as st

from shared import APP_CSS, header, load_overview, status, fmt_money
import pandas as pd
from api_client import AgentAPIError

st.set_page_config(page_title="AI Invoice Auditor", page_icon="🧾", layout="wide")
st.markdown(APP_CSS, unsafe_allow_html=True)


def dashboard() -> None:
    header("Audit overview", "A clear view of invoice intake, decisions, and work in progress.", "WORKSPACE")
    try:
        summary, invoices, uploads = load_overview()
    except AgentAPIError as exc:
        st.error(f"Could not load dashboard: {exc}")
        return
    columns = st.columns(5)
    metrics = [
        ("Invoices", summary.get("total_invoices", len(invoices))),
        ("Approved", summary.get("approved_invoices", summary.get("approved", 0))),
        ("Human review", summary.get("review_invoices", summary.get("manual_review", 0))),
        ("Open discrepancies", summary.get("open_discrepancies", summary.get("total_discrepancies", 0))),
        ("Files in queue", len(uploads)),
    ]
    for col, (label, value) in zip(columns, metrics):
        col.metric(label, value or 0)
    st.markdown('<div class="hero"><h2>From intake to audit decision</h2><p>Track extraction, validation, review, and reporting in one place.</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 1.5])
    with left:
        st.subheader("Processing queue")
        if uploads:
            st.dataframe(pd.DataFrame([{"File": x.get("file_name") or "—", "Stage": x.get("stage_label") or status(x.get("stage")), "Status": status(x.get("status")), "Updated": x.get("updated_at") or "—"} for x in uploads]), use_container_width=True, hide_index=True)
        else:
            st.caption("No files in the processing queue.")
    with right:
        st.subheader("Recent invoices")
        if invoices:
            st.dataframe(pd.DataFrame([{"Invoice": x.get("invoice_number") or "Pending", "Vendor": x.get("vendor_name") or "Unknown", "PO": x.get("po_number") or "—", "Total": fmt_money(x.get("total_amount"), x.get("currency")), "Status": status(x.get("validation_status")), "Updated": x.get("updated_at") or "—"} for x in invoices[:12]]), use_container_width=True, hide_index=True)
        else:
            st.caption("Processed invoices will appear here.")
    a, b = st.columns([1, 5])
    with a:
        if st.button("Refresh overview", icon="↻"):
            st.rerun()


pages = [
    st.Page(dashboard, title="Dashboard", icon="📊", default=True),
    st.Page("pages/1_Invoices.py", title="Invoices", icon="🗂️"),
    st.Page("pages/2_Human_Review.py", title="Human review", icon="👤"),
    st.Page("pages/3_Upload_Center.py", title="Upload center", icon="⬆️"),
    st.Page("pages/4_Ask_AI.py", title="Ask AI", icon="🤖"),
    st.Page("pages/5_Reports.py", title="Reports", icon="📄"),
]
navigation = st.navigation(pages, position="sidebar")
with st.sidebar:
    st.markdown("### AI Invoice Auditor")
    st.caption("Invoice operations")
    st.divider()
    try:
        from api_client import health
        result = health()
        st.caption("● Services online" if result.get("status") == "healthy" else "● Service attention needed")
    except Exception:
        st.caption("● Agent API unavailable")
navigation.run()
