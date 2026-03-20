"""District-level dashboard with modern interactive filters."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analytics import district_vs_national, gender_gap_table, top_advocacy_priorities
from src.loaders import has_processed_data, load_districts, load_indicators
from src.theme import apply_theme, kpi_card

st.set_page_config(page_title="Dashboard | NYEREKA", page_icon=" ", layout="wide")
apply_theme("District Gender Intelligence Dashboard", "Interactive district analysis with adaptive filters and gap prioritization.")

if not has_processed_data():
    st.error("Processed files are missing. Build them first:")
    st.code("python scripts/build_indicators.py", language="bash")
    st.stop()

indicators = load_indicators()
districts = load_districts()
if indicators.empty:
    st.error("No indicators found.")
    st.stop()

indicators = indicators.dropna(subset=["value_pct"]).copy()

# Sidebar filters
with st.sidebar:
    st.header("Interactive Filters")
    district_options = districts.sort_values("district_name")
    district_label_to_code = {
        f"{row.district_name} ({row.province_name})": int(row.district_code)
        for _, row in district_options.iterrows()
    }
    default_label = next((k for k, v in district_label_to_code.items() if v == 24), list(district_label_to_code.keys())[0])
    selected_district_label = st.selectbox("District", options=list(district_label_to_code.keys()), index=list(district_label_to_code.keys()).index(default_label))
    selected_district = district_label_to_code[selected_district_label]

    all_themes = sorted(indicators["theme"].dropna().unique().tolist())
    selected_themes = st.multiselect("Themes", options=all_themes, default=all_themes)

    all_sexes = ["All", "Female", "Male"]
    selected_sex = st.selectbox("Sex Focus", options=all_sexes, index=0)

    years = sorted(indicators["year"].dropna().astype(int).unique().tolist())
    selected_years = st.multiselect("Years", options=years, default=years)

    latest_only = st.checkbox("Use latest value per indicator", value=True)

filtered = indicators.copy()
if selected_themes:
    filtered = filtered[filtered["theme"].isin(selected_themes)]
if selected_years:
    filtered = filtered[filtered["year"].isin(selected_years)]
if selected_sex != "All":
    filtered = filtered[(filtered["sex"] == selected_sex) | (filtered["sex"] == "All")]

if latest_only:
    filtered = (
        filtered.sort_values("year", ascending=False)
        .groupby(["indicator_id", "sex", "geo_level", "province_code", "district_code"], as_index=False)
        .head(1)
    )

selected_district_df = filtered[(filtered["geo_level"] == "district") & (filtered["district_code"] == selected_district)]
national_df = filtered[filtered["geo_level"] == "national"]

priorities = top_advocacy_priorities(
    filtered[(filtered["geo_level"] == "district") & (filtered["district_code"] == selected_district)],
    n=5,
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Selected District", selected_district_label.split(" (")[0], "Active comparison district")
with c2:
    kpi_card("Indicators Shown", f"{selected_district_df['indicator_id'].nunique():,}", "After filters")
with c3:
    kpi_card("Themes", f"{selected_district_df['theme'].nunique():,}", "Evidence areas")
with c4:
    top_issue = priorities.iloc[0]["indicator_name"] if not priorities.empty else "No paired sex indicators"
    kpi_card("Top Priority", top_issue, "Largest female disadvantage")

st.markdown("### Smart Summary & Insights")
if priorities.empty:
    st.info("Not enough paired male/female indicators in current filters to compute priority insights.")
else:
    show = priorities[["indicator_name", "theme", "Female", "Male", "gap_f_minus_m", "priority_score"]].copy()
    show.columns = ["Indicator", "Theme", "Female", "Male", "Female-Male Gap", "Priority Score"]
    st.dataframe(show.round(2), use_container_width=True, hide_index=True)

# Tabs
snapshot_tab, ranking_tab, compare_tab = st.tabs(["District Snapshot", "District Ranking", "District vs National"])

with snapshot_tab:
    st.markdown("#### Female vs Male in Selected District")
    gap_df = gender_gap_table(selected_district_df)
    if gap_df.empty:
        st.info("No male/female paired metrics for this district under current filters.")
    else:
        chart_df = gap_df.sort_values("priority_score", ascending=False).head(12)
        fig = px.bar(
            chart_df,
            x="gap_f_minus_m",
            y="indicator_name",
            color="theme",
            orientation="h",
            labels={"gap_f_minus_m": "Female - Male (percentage points)", "indicator_name": "Indicator"},
            title="Gender gap profile (negative = female behind for most positive indicators)",
        )
        fig.update_layout(height=520, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

with ranking_tab:
    st.markdown("#### District-level Visualization")
    rank_pool = filtered[(filtered["geo_level"] == "district")]
    if selected_sex != "All":
        rank_pool = rank_pool[(rank_pool["sex"] == selected_sex) | (rank_pool["sex"] == "All")]

    indicator_choices = sorted(rank_pool["indicator_name"].dropna().unique().tolist())
    if not indicator_choices:
        st.info("No district-level indicators available for current filters.")
    else:
        selected_indicator_name = st.selectbox("Indicator for ranking", options=indicator_choices)
        rank_df = rank_pool[rank_pool["indicator_name"] == selected_indicator_name].copy()
        rank_df = rank_df.sort_values("value_pct", ascending=False)
        fig = px.bar(
            rank_df,
            x="value_pct",
            y="district_name",
            color="theme",
            orientation="h",
            labels={"value_pct": "Percent", "district_name": "District"},
            title=f"District ranking: {selected_indicator_name}",
        )
        fig.update_layout(height=740, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

with compare_tab:
    st.markdown("#### Selected District vs National")
    compare_pool = filtered[(filtered["geo_level"].isin(["district", "national"]))]
    compare_indicator_options = sorted(compare_pool["indicator_name"].dropna().unique().tolist())
    if not compare_indicator_options:
        st.info("No comparison-ready indicators under current filters.")
    else:
        compare_indicator = st.selectbox("Indicator", options=compare_indicator_options)
        compare_id = compare_pool[compare_pool["indicator_name"] == compare_indicator]["indicator_id"].iloc[0]
        compare_df = district_vs_national(compare_pool, compare_id, selected_district, sex=selected_sex)
        if compare_df.empty:
            st.info("No district/national values available for this indicator and sex.")
        else:
            fig = px.bar(compare_df, x="scope", y="value_pct", color="scope", text="value_pct", title=compare_indicator)
            fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig.update_layout(showlegend=False, yaxis_title="Percent")
            st.plotly_chart(fig, use_container_width=True)

            district_value = compare_df.loc[compare_df["scope"] == "Selected district", "value_pct"]
            national_value = compare_df.loc[compare_df["scope"] == "National", "value_pct"]
            if not district_value.empty and not national_value.empty:
                diff = float(district_value.iloc[0] - national_value.iloc[0])
                direction = "above" if diff >= 0 else "below"
                st.markdown(
                    f"<div class='note-box'>Selected district is <b>{abs(diff):.2f} percentage points</b> {direction} national value.</div>",
                    unsafe_allow_html=True,
                )

st.caption("All values are computed from processed microdata indicators with documented weighting and caveats.")
