from __future__ import annotations
import streamlit as st


def render_dashboard(summary: dict) -> None:
    """Render the reusable dashboard metric strip."""
    columns = st.columns(5)
    metrics = [
        ("Invoices", summary.get("total_invoices", 0)),
        ("Approved", summary.get("approved_invoices", summary.get("approved", 0))),
        ("Human review", summary.get("review_invoices", summary.get("manual_review", 0))),
        ("Open discrepancies", summary.get("open_discrepancies", summary.get("total_discrepancies", 0))),
        ("High severity", summary.get("high_severity_discrepancies", 0)),
    ]
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, value or 0)
