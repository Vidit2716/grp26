from __future__ import annotations
import pandas as pd
import streamlit as st
from shared import setup_page, header, status, fmt_money
from api_client import get_invoices, get_invoice, get_report, AgentAPIError

setup_page("Invoices")
header("Invoices", "Search the audit record and inspect effective values, line items, and report output.", "AUDIT RECORD")
try:
    invoices = get_invoices()
except AgentAPIError as exc:
    st.error(str(exc)); st.stop()
if not invoices:
    st.info("No invoices have been processed yet."); st.stop()

ids = [str(x.get("invoice_id") or i) for i, x in enumerate(invoices)]
labels = {str(x.get("invoice_id") or i): f"{x.get('invoice_number') or x.get('file_name') or 'Invoice'} · {x.get('vendor_name') or 'Unknown vendor'}" for i, x in enumerate(invoices)}
saved = st.session_state.get("invoice_selected_id")
index = ids.index(saved) if saved in ids else 0
query = st.text_input("Filter invoices", placeholder="Invoice number or vendor")
visible = [i for i, x in enumerate(invoices) if not query or query.casefold() in " ".join(str(x.get(k) or "") for k in ("invoice_number", "vendor_name", "file_name", "po_number")).casefold()]
if not visible:
    st.info("No invoices match that filter."); st.stop()
if index not in visible: index = visible[0]
visible_ids = [ids[i] for i in visible]
if st.session_state.get("invoice_choice") not in visible_ids:
    st.session_state["invoice_choice"] = ids[index]
selected_id = st.selectbox("Select invoice", visible_ids, index=visible_ids.index(ids[index]), format_func=lambda value: labels[value], key="invoice_choice")
choice = ids.index(selected_id)
invoice_id = str(invoices[choice].get("invoice_id") or "")
st.session_state["invoice_selected_id"] = invoice_id
try:
    detail = get_invoice(invoice_id)
except AgentAPIError as exc:
    st.error(str(exc)); st.stop()

cols = st.columns(4)
for col, (label, value) in zip(cols, [("Invoice", detail.get("invoice_number") or "Pending"), ("Vendor", detail.get("vendor_name") or "Unknown"), ("Total", fmt_money(detail.get("total_amount"), detail.get("currency"))), ("Open discrepancies", sum(1 for d in detail.get("discrepancies", []) if str(d.get("status", "")).lower() == "open"))]): col.metric(label, value)
left, right = st.columns([1.25, .85], gap="large")
with left:
    st.subheader("Effective values")
    fields = ["invoice_number", "vendor_name", "po_number", "invoice_date", "currency", "subtotal_amount", "tax_amount", "tax_rate", "total_amount", "validation_status", "recommendation", "human_review_required"]
    st.dataframe(pd.DataFrame([{"Field": key.replace("_", " ").title(), "Value": detail.get(key) or "—"} for key in fields]), use_container_width=True, hide_index=True)
    st.subheader("Line items")
    lines = detail.get("line_items") or []
    if lines: st.dataframe(pd.DataFrame(lines), use_container_width=True, hide_index=True)
    else: st.caption("No line items available.")
with right:
    st.subheader("Discrepancies")
    discrepancies = detail.get("discrepancies") or []
    if discrepancies: st.dataframe(pd.DataFrame([{k: d.get(k) for k in ["discrepancy_type", "severity", "message", "status"]} for d in discrepancies]), use_container_width=True, hide_index=True)
    else: st.caption("No recorded discrepancies.")
    st.subheader("Processing")
    st.write(detail.get("processing_stage") or "No live stage record")
    a, b = st.columns(2)
    with a:
        if st.button("Open review", type="primary", use_container_width=True): st.switch_page("pages/2_Human_Review.py")
    with b:
        if st.button("Load JSON report", use_container_width=True):
            try:
                st.session_state["invoice_report"] = get_report(invoice_id)
                st.session_state["invoice_report_id"] = invoice_id
            except AgentAPIError as exc: st.error(str(exc))
    report_state = st.session_state.get("invoice_report") or {}
    if st.session_state.get("invoice_report_id") == invoice_id and report_state: st.json(report_state)
