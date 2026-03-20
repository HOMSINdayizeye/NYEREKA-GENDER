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

st.markdown("### Presentation Flow")
st.markdown(
    """
1. National snapshot with top gender gaps.
2. District explorer for Huye and peer districts.
3. Advocacy assistant for recommendations and follow-ups.
4. Quarterly report and data-quality transparency.
    """
)

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
st.markdown("#### Direct Source Links")
render_source_links(source_table, meta_cols=["year", "theme"])

st.markdown("### Quality Snapshot")
st.dataframe(
    quality[["dataset_name", "quality_badge", "quality_score", "freshness", "coverage", "weighted_methods"]],
    use_container_width=True,
    hide_index=True,
)

with st.sidebar:
    st.header("Quick Actions")
    st.caption("If raw files change, rebuild indicators before demo.")
    st.code("python scripts/build_indicators.py", language="bash")
    st.caption("Run app")
    st.code("streamlit run app.py", language="bash")
