from __future__ import annotations

import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

from shared import setup_page, header, status
from api_client import get_reports, get_report, get_report_html, AgentAPIError


setup_page("Reports")
header(
    "Generated reports",
    "Open the audit reports created from the original invoice filename.",
    "REPORTS",
)

try:
    reports = get_reports()
except AgentAPIError as exc:
    st.error(str(exc))
    st.stop()

if not reports:
    st.info("No reports have been generated yet. Process an invoice to create a report.")
    st.stop()

rows = [
    {
        "Report": r.get("report_name") or "—",
        "Source invoice": r.get("source_file") or "—",
        "Invoice": r.get("invoice_number") or "—",
        "Vendor": r.get("vendor_name") or "—",
        "Status": status(r.get("validation_status")),
        "Recommendation": status(r.get("recommendation")),
        "Updated": r.get("updated_at") or "—",
    }
    for r in reports
]
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

options = list(range(len(reports)))
choice = st.selectbox(
    "Open report",
    options,
    format_func=lambda i: f"{reports[i].get('report_name') or 'Report'} · {reports[i].get('source_file') or 'invoice'}",
)
selected = reports[choice]
invoice_id = str(selected["invoice_id"])

st.divider()
left, right = st.columns([1.6, 1])

with left:
    st.subheader(selected.get("report_name") or "Generated report")
    try:
        html = get_report_html(invoice_id)
        components.html(html, height=680, scrolling=True)
    except AgentAPIError as exc:
        st.error(f"HTML report is unavailable: {exc}")

with right:
    st.subheader("Report files")
    st.caption(f"Generated from: {selected.get('source_file') or 'invoice'}")

    try:
        report_json = get_report(invoice_id)
        json_bytes = json.dumps(report_json, indent=2, default=str).encode("utf-8")
        st.download_button(
            "Download JSON report",
            data=json_bytes,
            file_name=selected.get("report_name") or "invoice_report.json",
            mime="application/json",
            use_container_width=True,
        )
    except Exception as exc:
        st.error(f"JSON report is unavailable: {exc}")

    try:
        html = get_report_html(invoice_id)
        html_name = (selected.get("report_name") or "invoice_report.json").rsplit(".", 1)[0] + ".html"
        st.download_button(
            "Download HTML report",
            data=html.encode("utf-8"),
            file_name=html_name,
            mime="text/html",
            use_container_width=True,
        )
    except AgentAPIError as exc:
        st.error(f"HTML report is unavailable: {exc}")
