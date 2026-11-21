from __future__ import annotations
import pandas as pd
import streamlit as st
from shared import setup_page, header, status
from api_client import upload_invoice, get_upload_status, clear_pending_queue, AgentAPIError

setup_page("Upload Center")
header("Upload center", "Add invoice files and follow each file through the processing queue.", "INTAKE")
with st.container(border=True):
    file = st.file_uploader("Choose invoice files", type=["pdf", "docx", "png", "jpg", "jpeg", "tif", "tiff"])
    if file:
        st.caption(f"Ready to process · {file.name} · {file.size:,} bytes")
    if file and st.button("Start processing", type="primary", use_container_width=True):
        try:
            result = upload_invoice(file.name, file.getvalue())
            st.session_state["last_upload"] = result
            st.success(result.get("message") or "File accepted for processing")
        except AgentAPIError as exc: st.error(str(exc))

st.subheader("Processing queue")
a, b = st.columns([1, 5])
with a:
    if st.button("Refresh queue", icon="↻", use_container_width=True): st.rerun()
try:
    files = get_upload_status().get("files") or []
except AgentAPIError as exc:
    st.error(str(exc)); st.stop()
if not files:
    st.info("The queue is clear. Uploaded files will appear here.")
else:
    st.dataframe(pd.DataFrame([{"File": f.get("file_name") or "Unknown file", "Stage": f.get("stage_label") or f.get("stage") or "Queued", "Status": status(f.get("status")), "Invoice": f.get("invoice_number") or "Pending", "Updated": f.get("updated_at") or "—", "Message": f.get("message") or f.get("error") or ""} for f in files]), use_container_width=True, hide_index=True)
with st.expander("Queue actions"):
    st.caption("Remove files that are waiting to be processed.")
    if st.button("Clear pending uploads"):
        try:
            st.success(clear_pending_queue().get("message") or "Pending queue cleared")
            st.rerun()
        except AgentAPIError as exc: st.error(str(exc))
