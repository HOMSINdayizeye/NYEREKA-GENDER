"""Smart search and filtering across indicators and data sources."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analytics import direction_for, district_vs_national
from src.loaders import has_processed_data, load_districts, load_indicators, load_sources
from src.theme import apply_theme, kpi_card, render_source_links

st.set_page_config(page_title="Discovery | NYEREKA", page_icon=" ", layout="wide")
apply_theme("Smart Search and Filtering", "Search indicators, inspect summaries, and generate recommendation-ready insights.")

if not has_processed_data():
    st.error("Processed files are missing. Build them first:")
    st.code("python scripts/build_indicators.py", language="bash")
    st.stop()

indicators = load_indicators()
districts = load_districts()
sources = load_sources()

if indicators.empty:
    st.error("No indicators found.")
    st.stop()

with st.sidebar:
    st.header("Search Controls")
    query = st.text_input("Search keyword", placeholder="e.g. unemployment, violence, mobile money")

    theme_opts = sorted(indicators["theme"].dropna().unique().tolist())
    selected_themes = st.multiselect("Themes", options=theme_opts, default=theme_opts)

    dataset_opts = sorted(indicators["dataset_name"].dropna().unique().tolist())
    selected_datasets = st.multiselect("Datasets", options=dataset_opts, default=dataset_opts)

    geo_opts = sorted(indicators["geo_level"].dropna().unique().tolist())
    selected_geo = st.multiselect("Geography level", options=geo_opts, default=geo_opts)

    sex_opts = sorted(indicators["sex"].dropna().unique().tolist())
    selected_sex = st.multiselect("Sex", options=sex_opts, default=sex_opts)

    year_opts = sorted(indicators["year"].dropna().astype(int).unique().tolist())
    selected_years = st.multiselect("Years", options=year_opts, default=year_opts)

    district_label_map = {
        f"{row.district_name} ({row.province_name})": int(row.district_code)
        for _, row in districts.sort_values("district_name").iterrows()
    }
    selected_district_label = st.selectbox("Recommendation district", options=list(district_label_map.keys()))
    selected_district = district_label_map[selected_district_label]

flt = indicators.copy()
flt = flt[flt["theme"].isin(selected_themes)]
flt = flt[flt["dataset_name"].isin(selected_datasets)]
flt = flt[flt["geo_level"].isin(selected_geo)]
flt = flt[flt["sex"].isin(selected_sex)]
flt = flt[flt["year"].isin(selected_years)]

if query.strip():
    q = query.lower().strip()
    flt = flt[
        flt["indicator_name"].str.lower().str.contains(q, na=False)
        | flt["theme"].str.lower().str.contains(q, na=False)
        | flt["dataset_name"].str.lower().str.contains(q, na=False)
        | flt["caveat"].str.lower().str.contains(q, na=False)
    ]

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Matched Rows", f"{len(flt):,}", "Filtered indicator observations")
with c2:
    kpi_card("Indicators", f"{flt['indicator_id'].nunique():,}", "Distinct indicator definitions")
with c3:
    kpi_card("Datasets", f"{flt['dataset_name'].nunique():,}", "Sources represented")
with c4:
    mean_val = flt["value_pct"].mean() if not flt.empty else 0
    kpi_card("Mean Value", f"{mean_val:.2f}%", "Across filtered rows")

st.markdown("### Resource Summaries and Insights")
summary = (
    flt.groupby(["indicator_name", "theme", "dataset_name"], as_index=False)
    .agg(avg_value=("value_pct", "mean"), latest_year=("year", "max"), records=("value_pct", "count"))
    .sort_values(["theme", "indicator_name"])
)
st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("### Smart Search Results")
show_cols = [
    "indicator_name",
    "theme",
    "dataset_name",
    "year",
    "geo_level",
    "district_name",
    "province_name",
    "sex",
    "value_pct",
    "weight_var",
    "caveat",
]
st.dataframe(flt[show_cols].sort_values(["indicator_name", "year"], ascending=[True, False]), use_container_width=True, hide_index=True)

st.markdown("### System Recommendations")
recommend_rows: list[dict] = []
for indicator_id, group in flt.groupby("indicator_id"):
    row = group.iloc[0]
    sex = row["sex"] if row["sex"] in ["Female", "Male"] else "All"
    compare = district_vs_national(indicators, indicator_id, selected_district, sex=sex)
    if len(compare) < 2:
        continue
    district_v = float(compare.loc[compare["scope"] == "Selected district", "value_pct"].iloc[0])
    national_v = float(compare.loc[compare["scope"] == "National", "value_pct"].iloc[0])
    diff = district_v - national_v
    direction = direction_for(indicator_id)
    if (direction == "higher_better" and diff < 0) or (direction == "lower_better" and diff > 0):
        recommend_rows.append(
            {
                "Indicator": row["indicator_name"],
                "Theme": row["theme"],
                "District": selected_district_label,
                "District Value": round(district_v, 2),
                "National Value": round(national_v, 2),
                "Gap": round(diff, 2),
                "Action": "Priority follow-up recommended",
            }
        )

if recommend_rows:
    rec_df = pd.DataFrame(recommend_rows).sort_values("Gap")
    st.dataframe(rec_df, use_container_width=True, hide_index=True)
else:
    st.success("No high-priority underperformance found for current search/filter combination.")

st.markdown("### Source Links")
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
render_source_links(source_table, meta_cols=["year", "theme"])
