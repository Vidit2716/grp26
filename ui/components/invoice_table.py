from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
from shared import fmt_money, status


def render_invoice_table(invoices: list[dict[str, Any]]) -> str | None:
    if not invoices:
        st.info("No invoices available.")
        return None
    rows = [{
        "Invoice": x.get("invoice_number") or "Pending",
        "Vendor": x.get("vendor_name") or "Unknown",
        "PO": x.get("po_number") or "—",
        "Date": x.get("invoice_date") or "—",
        "Total": fmt_money(x.get("total_amount"), x.get("currency")),
        "Status": status(x.get("validation_status")),
        "Recommendation": status(x.get("recommendation")),
    } for x in invoices]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    choices = [(i, x) for i, x in enumerate(invoices) if x.get("invoice_id")]
    if not choices:
        return None
    selected_id = st.session_state.get("selected_invoice")
    index = next((j for j, (_, x) in enumerate(choices) if str(x.get("invoice_id")) == selected_id), 0)
    selected = st.selectbox("Open invoice", range(len(choices)), index=index, format_func=lambda j: f"{choices[j][1].get('invoice_number') or choices[j][1].get('file_name') or 'Invoice'} · {choices[j][1].get('vendor_name') or 'Unknown vendor'}", key="invoice_table_choice")
    invoice_id = str(choices[selected][1]["invoice_id"])
    st.session_state["selected_invoice"] = invoice_id
    return invoice_id
