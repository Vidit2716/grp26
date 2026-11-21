from __future__ import annotations
from typing import Any
import streamlit as st


def render_feedback_form(invoice: dict[str, Any]) -> dict[str, Any] | None:
    invoice_id = str(invoice.get("invoice_id") or "unknown")
    if not invoice.get("human_review_required") and str(invoice.get("validation_status") or "").lower() not in {"manual_review", "failed", "invalid_erp"}:
        return None
    st.subheader("Review decision")
    st.caption("Corrections are recorded as human feedback; the original extraction remains available for comparison.")
    corrections: dict[str, Any] = {}
    lines = invoice.get("line_items") or []
    if lines:
        for index, line in enumerate(lines):
            number = line.get("line_number", index + 1)
            with st.expander(f"Line {number} · {line.get('sku') or 'Unknown SKU'}", expanded=False):
                cols = st.columns(3)
                sku = cols[0].text_input("SKU", value=str(line.get("sku") or ""), key=f"feedback_sku_{invoice_id}_{number}")
                quantity = cols[1].number_input("Quantity", value=float(line.get("quantity") or 0), min_value=0.0, key=f"feedback_qty_{invoice_id}_{number}")
                price = cols[2].number_input("Unit price", value=float(line.get("unit_price") or 0), min_value=0.0, key=f"feedback_price_{invoice_id}_{number}")
                corrections[f"line_{number}"] = {"sku": sku, "quantity": quantity, "unit_price": price, "line_total": quantity * price}
    decision = st.radio("Decision", ["manual_review", "approve", "reject"], format_func=lambda x: {"manual_review": "Keep in review", "approve": "Approve", "reject": "Reject"}[x], horizontal=True, key=f"decision_{invoice_id}")
    feedback = st.text_area("Reviewer note", placeholder="Explain the correction or decision…", key=f"feedback_{invoice_id}")
    if st.button("Submit review", type="primary", key=f"submit_hitl_{invoice_id}"):
        return {"corrections": corrections, "decision": decision, "feedback": feedback.strip()}
    return None
