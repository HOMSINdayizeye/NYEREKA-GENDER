"""Data quality indicators and caveat transparency."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.loaders import has_processed_data, load_indicators, load_quality_summary
from src.theme import apply_theme, kpi_card, render_source_links

st.set_page_config(page_title="Data Quality | NYEREKA", page_icon=" ", layout="wide")
apply_theme("Data Quality Indicators", "Quality scores, weighting methods, caveats, and follow-up checklist.")

# Sidebar styling
st.markdown("""<style>
[data-testid="stSidebar"] { background-color: #1D3557 !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.95) !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: rgba(255,255,255,0.95) !important; }
[data-testid="stSidebar"] .stMarkdown p { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] label { color: rgba(255,255,255,0.95) !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.95) !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stMultiSelect label { color: rgba(255,255,255,0.95) !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stCheckbox label { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] { color: white !important; }
[data-testid="stSidebar"] div[data-baseweb="select"] > div { color: white !important; background-color: transparent !important; }
[data-testid="stSidebar"] [class*="StyledContent"] { color: white !important; }
[data-testid="stSidebar"] [class*="singleValue"] { color: white !important; }
[data-testid="stSidebar"] span[data-text="true"] { color: white !important; }
</style>""", unsafe_allow_html=True)

if not has_processed_data():
    st.error("Processed files are missing. Build them first:")
    st.code("python scripts/build_indicators.py", language="bash")
    st.stop()

indicators = load_indicators()
quality = load_quality_summary()

if indicators.empty:
    st.error("No indicator data found.")
    st.stop()

indicators = indicators.dropna(subset=["value_pct"]).copy()

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Datasets Rated", f"{quality['dataset_name'].nunique():,}", "Quality-scored data sources")
with c2:
    kpi_card("Average Quality", f"{quality['quality_score'].mean():.1f}", "Composite score")
with c3:
    high_count = (quality["quality_badge"] == "High").sum()
    kpi_card("High Quality", f"{high_count:,}", "Datasets in high tier")
with c4:
    weighted_share = (indicators["weight_var"] != "unweighted").mean() * 100
    kpi_card("Weighted Indicators", f"{weighted_share:.1f}%", "Indicators using survey weights")

st.markdown("### Dataset Quality Badges")
fig = px.bar(
    quality.sort_values("quality_score", ascending=True),
    x="quality_score",
    y="dataset_name",
    color="quality_badge",
    orientation="h",
    color_discrete_map={"High": "#16a34a", "Medium": "#f59e0b", "Limited": "#dc2626"},
    title="Quality score by dataset",
)
fig.update_layout(height=420, yaxis_title="", xaxis_title="Quality score")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    quality[["dataset_name", "year", "quality_badge", "quality_score", "freshness", "coverage", "weighted_methods", "source_url"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "source_url": st.column_config.LinkColumn("Open Source", display_text="Open in new tab"),
    },
)

st.markdown("#### Source Access Links")
render_source_links(quality[["dataset_name", "year", "source_url"]].drop_duplicates(), meta_cols=["year"])

st.markdown("### Indicator-level Caveats")
caveat_df = (
    indicators[["indicator_name", "dataset_name", "weight_var", "denominator_rule", "caveat", "geo_level", "sex", "source_url"]]
    .drop_duplicates()
    .sort_values(["dataset_name", "indicator_name"])
)
st.dataframe(
    caveat_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "source_url": st.column_config.LinkColumn("Open Source", display_text="Open in new tab"),
    },
)

st.markdown("### Follow-up Data Quality Checklist")
followups = [
    "Re-run `python scripts/build_indicators.py` after any new raw data download.",
    "Validate district-level results against published tables before final submission.",
    "For DHS GBV indicators, keep `d005` as weight variable (do not replace with `v005`).",
    "Document denominator filters for each KPI in the final report appendix.",
    "Flag EC owner-sex indicator as low-confidence due to high missingness.",
]
for item in followups:
    st.markdown(f"- [ ] {item}")
