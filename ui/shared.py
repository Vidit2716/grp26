from __future__ import annotations

from typing import Any
import html

import streamlit as st

from api_client import get_dashboard_summary, get_invoices, get_upload_status

STATUS_META = {
    "approved": ("Approved", "success"), "complete": ("Complete", "success"),
    "manual_review": ("Human review", "warning"), "failed": ("Failed", "error"),
    "invalid_erp": ("Invalid ERP", "error"), "processing": ("Processing", "info"),
    "queued": ("Queued", "info"), "waiting": ("Waiting", "warning"),
}

APP_CSS = """
<style>
:root { color-scheme: light dark; }
.block-container { max-width: 1440px; padding-top: 2.1rem; padding-bottom: 3.5rem; }
[data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.18); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 { letter-spacing: -.04em; }
h1, h2, h3 { letter-spacing: -.035em; }
h1 { font-weight: 680; }
[data-testid="stMetric"] { padding: .5rem .1rem .8rem; }
[data-testid="stMetricLabel"] { font-size: .82rem; }
[data-testid="stMetricValue"] { font-weight: 680; letter-spacing: -.04em; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(128,128,128,.22); border-radius: 12px; }
div[data-testid="stDataFrame"] { border-radius: 10px; }
.page-eyebrow { color: var(--primary-color); font-size: .72rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; margin-bottom: .4rem; }
.page-subtitle { color: var(--text-color); opacity: .68; margin: .35rem 0 1.5rem; max-width: 70rem; }
.hero { padding: 1.25rem 0 1.45rem; margin: .4rem 0 1.4rem; border-bottom: 1px solid rgba(128,128,128,.2); }
.hero h2 { margin: 0; font-size: 1.45rem; letter-spacing: -.04em; }
.hero p { margin: .45rem 0 0; color: var(--text-color); opacity: .7; }
.answer { padding: 1rem 1.1rem; border-radius: 10px; border: 1px solid rgba(128,128,128,.24); border-left: 3px solid var(--primary-color); background: color-mix(in srgb, var(--secondary-background-color) 55%, transparent); line-height: 1.65; }
.quiet { opacity: .68; font-size: .88rem; }
.stButton button, .stDownloadButton button { border-radius: 8px; }
</style>
"""


def setup_page(title: str, icon: str = "🧾") -> None:
    """Apply app-wide styling. Page config and navigation are owned by app.py."""
    st.markdown(APP_CSS, unsafe_allow_html=True)


def header(title: str, subtitle: str, eyebrow: str) -> None:
    st.markdown(
        f'<div class="page-eyebrow">{html.escape(eyebrow)}</div>'
        f'<h1>{html.escape(title)}</h1>'
        f'<div class="page-subtitle">{html.escape(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def status(value: Any) -> str:
    key = str(value or "unknown").lower().replace(" ", "_")
    return STATUS_META.get(key, (str(value or "Unknown").replace("_", " ").title(), "info"))[0]


def load_overview():
    return get_dashboard_summary(), get_invoices(), get_upload_status().get("files", [])


def fmt_money(value: Any, currency: Any = "") -> str:
    if value is None or value == "":
        return "—"
    try:
        return f"{currency or ''} {float(value):,.2f}".strip()
    except (TypeError, ValueError):
        return f"{currency or ''} {value}".strip()
