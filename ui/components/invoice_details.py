from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
from shared import fmt_money, status


def render_invoice_details(invoice: dict[str, Any]) -> None:
    st.subheader(invoice.get("invoice_number") or "Invoice details")
    cols = st.columns(4)
    values = [("Vendor", invoice.get("vendor_name") or "Unknown"), ("PO", invoice.get("po_number") or "—"), ("Total", fmt_money(invoice.get("total_amount"), invoice.get("currency"))), ("Status", status(invoice.get("validation_status") or invoice.get("status")))]
    for col, (label, value) in zip(cols, values):
        col.metric(label, value)
    st.caption(f"Recommendation · {status(invoice.get('recommendation'))}")
    lines = invoice.get("line_items") or []
    if lines:
        st.subheader("Line items")
        st.dataframe(pd.DataFrame(lines), use_container_width=True, hide_index=True)
