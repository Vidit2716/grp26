from __future__ import annotations
import pandas as pd
import streamlit as st


def render_discrepancy_panel(discrepancies: list[dict]) -> None:
    st.subheader("Discrepancies")
    if not discrepancies:
        st.caption("No discrepancies recorded.")
        return
    rows = [{"Type": x.get("discrepancy_type") or x.get("field") or "Discrepancy", "Severity": str(x.get("severity") or "info").title(), "Status": str(x.get("status") or "Unknown").replace("_", " ").title(), "Finding": x.get("message") or "No details provided"} for x in discrepancies]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    with st.expander("View discrepancy evidence"):
        for index, item in enumerate(discrepancies, start=1):
            st.markdown(f"**{index}. {item.get('discrepancy_type') or item.get('field') or 'Discrepancy'}** · {str(item.get('severity') or 'info').title()}")
            if item.get("details"):
                st.json(item["details"])
