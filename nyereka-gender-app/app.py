"""NYEREKA Gender main landing page."""
from __future__ import annotations

import streamlit as st

from src.loaders import has_processed_data, load_all
from src.theme import apply_theme, kpi_card, render_source_links

st.set_page_config(
    page_title="NYEREKA Gender Intelligence Hub",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Design CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1D3557 !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.75) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.75) !important;
}

/* Remove bullets from sidebar nav */
[data-testid="stSidebarNav"] ul {
    list-style: none !important;
    padding-left: 0 !important;
}
[data-testid="stSidebarNav"] li::before {
    display: none !important;
}
[data-testid="stSidebarNav"] a {
    color: rgba(255,255,255,0.65) !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    border-radius: 4px !important;
    border-left: 3px solid transparent !important;
    display: block;
}
[data-testid="stSidebarNav"] a:hover {
    color: #fff !important;
    background: rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    color: #A8DADC !important;
    background: rgba(168,218,220,0.12) !important;
    border-left-color: #A8DADC !important;
}

/* ── KPI metric cards ── */
[data-testid="metric-container"] {
    background-color: #ffffff !important;
    border: 0.5px solid #dee2e6 !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
}
[data-testid="metric-container"] label {
    font-size: 10px !important;
    font-weight: 500 !important;
    color: #6c757d !important;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 500 !important;
    color: #1D3557 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
    color: #adb5bd !important;
}

/* ── Headings ── */
h1, h2, h3 {
    color: #1D3557 !important;
    font-weight: 500 !important;
}

/* ── Links ── */
a {
    color: #E63946 !important;
    font-weight: 500;
    text-decoration: none;
}
a:hover {
    color: #1D3557 !important;
    text-decoration: underline;
}

/* ── Source cards (override old purple gradient) ── */
.source-card {
    background: #ffffff !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin-bottom: 10px !important;
    box-shadow: none !important;
    border: 0.5px solid #dee2e6 !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    transition: border-color 0.15s !important;
}
.source-card:hover {
    transform: none !important;
    border-color: #A8DADC !important;
}
.source-name {
    font-weight: 500 !important;
    color: #1D3557 !important;
    font-size: 13px !important;
}
.source-meta {
    font-size: 11px !important;
    color: #6c757d !important;
    margin-top: 3px !important;
}
.source-link {
    background: #1D3557 !important;
    color: #A8DADC !important;
    padding: 6px 14px !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em;
}
.source-link:hover {
    background: #E63946 !important;
    color: #fff !important;
    opacity: 1 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 0.5px solid #dee2e6 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #ffffff !important;
    color: #1D3557 !important;
    border: 0.5px solid #dee2e6 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
}
.stButton > button:hover {
    border-color: #1D3557 !important;
    color: #E63946 !important;
}
.stButton > button:disabled {
    color: #adb5bd !important;
    border-color: #f1f3f5 !important;
}

/* ── Page padding ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

apply_theme(
    "NYEREKA Gender Intelligence Hub",
    "Evidence platform for Rwanda gender advocacy using DHS, LFS, EICV, PHC, FinScope, and Establishment Census microdata.",
)

if not has_processed_data():
    st.error("Processed indicator files are missing.")
    st.code("cd nyereka-gender-app && python scripts/build_indicators.py", language="bash")
    st.stop()

bundle = load_all()
indicators = bundle["indicators"]
sources = bundle["sources"]
quality = bundle["quality"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Indicators", f"{indicators['indicator_id'].nunique():,}", "Curated KPI definitions")
with col2:
    kpi_card("Datasets", f"{indicators['dataset_name'].nunique():,}", "Integrated microdata sources")
with col3:
    kpi_card("District Coverage", f"{indicators['district_code'].dropna().nunique():.0f}", "Rwanda districts with metrics")
with col4:
    kpi_card("Latest Year", f"{int(indicators['year'].max())}", "Most recent source in pipeline")

st.markdown("### Data Sources and Access Paths")
source_table = (
    sources[["dataset_name", "year", "theme", "source_url"]]
    .drop_duplicates()
    .sort_values(["year", "dataset_name"], ascending=[False, True])
)
st.dataframe(
    source_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "source_url": st.column_config.LinkColumn("Open Source", display_text="Open in new tab"),
    },
)

# ── Paginated Direct Source Links ─────────────────────────────────────────────
st.markdown("### Direct Source Links")
ITEMS_PER_PAGE = 5
total_items = len(source_table)
total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

if "source_page" not in st.session_state:
    st.session_state.source_page = 1

col_prev, col_info, col_next = st.columns([1, 2, 1])
with col_prev:
    if st.button("← Previous", disabled=st.session_state.source_page <= 1):
        st.session_state.source_page -= 1
with col_info:
    st.markdown(
        f"<div style='text-align:center; padding:8px; font-size:13px; color:#6c757d;'>"
        f"Page <b style='color:#1D3557;'>{st.session_state.source_page}</b> of {total_pages}</div>",
        unsafe_allow_html=True,
    )
with col_next:
    if st.button("Next →", disabled=st.session_state.source_page >= total_pages):
        st.session_state.source_page += 1

start_idx = (st.session_state.source_page - 1) * ITEMS_PER_PAGE
end_idx   = min(start_idx + ITEMS_PER_PAGE, total_items)
current_page_df = source_table.iloc[start_idx:end_idx]

for _, row in current_page_df.iterrows():
    name  = str(row.get("dataset_name", "Source"))
    url   = str(row.get("source_url", "#"))
    year  = row.get("year", "")
    theme = row.get("theme", "")
    meta  = f"{year} · {theme}" if year and theme else f"{year}{theme}"
    st.markdown(
        f"""
        <div class="source-card">
            <div>
                <div class="source-name">{name}</div>
                <div class="source-meta">{meta}</div>
            </div>
            <a class="source-link" href="{url}" target="_blank">Open</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Quality Snapshot ──────────────────────────────────────────────────────────
st.markdown("### Quality Snapshot")
st.dataframe(
    quality[["dataset_name", "quality_badge", "quality_score", "freshness", "coverage", "weighted_methods"]],
    use_container_width=True,
    hide_index=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding-bottom:20px; border-bottom:0.5px solid rgba(255,255,255,0.12); margin-bottom:16px;">
        <div style="font-size:13px; font-weight:600; color:#A8DADC; letter-spacing:0.1em; text-transform:uppercase;">NYEREKA</div>
        <div style="font-size:11px; color:rgba(255,255,255,0.4); margin-top:3px;">Gender Intelligence Hub</div>
    </div>
    """, unsafe_allow_html=True)
    st.header("Navigation")
    st.caption("Use the pages in the sidebar to explore gender data.")
