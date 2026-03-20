"""District-level dashboard with modern interactive filters."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import district_vs_national, gender_gap_table, top_advocacy_priorities
from src.loaders import has_processed_data, load_districts, load_indicators
from src.theme import apply_theme, kpi_card

st.set_page_config(page_title="Dashboard | NYEREKA", page_icon=" ", layout="wide")
apply_theme("District Gender Intelligence Dashboard", "Interactive district analysis with adaptive filters and gap prioritization.")

# Sidebar styling
st.markdown("""<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fc 0%, #e8ecf1 100%);
        border-right: 1px solid #d0d5dd;
    }
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 20px;
        padding: 15px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .sidebar-section {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
    }
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #64748b;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #f1f5f9;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiselect label,
    [data-testid="stSidebar"] .stCheckbox label {
        font-size: 0.85rem;
        color: #475569;
        font-weight: 500;
    }
</style>""", unsafe_allow_html=True)

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

with st.sidebar:
    st.markdown("<div class='sidebar-title'>Filters</div>", unsafe_allow_html=True)
    district_options = districts.sort_values("district_name")
    district_label_to_code = {
        f"{row.district_name} ({row.province_name})": int(row.district_code)
        for _, row in district_options.iterrows()
    }
    default_label = next((k for k, v in district_label_to_code.items() if v == 24), list(district_label_to_code.keys())[0])
    selected_district_label = st.selectbox("District", options=list(district_label_to_code.keys()), index=list(district_label_to_code.keys()).index(default_label))
    selected_district = district_label_to_code[selected_district_label]
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><div class='sidebar-section-title'>Categories</div>", unsafe_allow_html=True)
    all_themes = sorted(indicators["theme"].dropna().unique().tolist())
    selected_themes = st.multiselect("Themes", options=all_themes, default=all_themes)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><div class='sidebar-section-title'>Demographics</div>", unsafe_allow_html=True)
    all_sexes = ["All", "Female", "Male"]
    selected_sex = st.selectbox("Sex Focus", options=all_sexes, index=0)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'><div class='sidebar-section-title'>Time</div>", unsafe_allow_html=True)
    years = sorted(indicators["year"].dropna().astype(int).unique().tolist())
    selected_years = st.multiselect("Years", options=years, default=years)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    latest_only = st.checkbox("Use latest value per indicator", value=True)
    st.markdown("</div>", unsafe_allow_html=True)

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

# Styled KPI section
st.markdown("""
<style>
    .kpi-row { display: flex; gap: 16px; margin-bottom: 20px; }
    .kpi-tile {
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .kpi-tile.alt1 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .kpi-tile.alt2 { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .kpi-tile.alt3 { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
    .kpi-tile-label { font-size: 0.75rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-tile-value { font-size: 1.6rem; font-weight: bold; margin: 8px 0; }
    .kpi-tile-sub { font-size: 0.8rem; opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-tile"><div class="kpi-tile-label">DISTRICT</div><div class="kpi-tile-value">{selected_district_label.split(" (")[0]}</div><div class="kpi-tile-sub">Selected area</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-tile alt1"><div class="kpi-tile-label">INDICATORS</div><div class="kpi-tile-value">{selected_district_df["indicator_id"].nunique():,}</div><div class="kpi-tile-sub">Available metrics</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-tile alt2"><div class="kpi-tile-label">THEMES</div><div class="kpi-tile-value">{selected_district_df["theme"].nunique():,}</div><div class="kpi-tile-sub">Evidence areas</div></div>', unsafe_allow_html=True)
with c4:
    top_issue = priorities.iloc[0]["indicator_name"] if not priorities.empty else "No data"
    st.markdown(f'<div class="kpi-tile alt3"><div class="kpi-tile-label">TOP PRIORITY</div><div class="kpi-tile-value" style="font-size:1rem;">{top_issue[:25]}{"..." if len(top_issue) > 25 else ""}</div><div class="kpi-tile-sub">Largest gender gap</div></div>', unsafe_allow_html=True)

st.markdown("### Smart Summary & Insights")
if priorities.empty:
    st.info("Not enough paired male/female indicators in current filters to compute priority insights.")
else:
    show = priorities[["indicator_name", "theme", "Female", "Male", "gap_f_minus_m", "priority_score"]].copy()
    show.columns = ["Indicator", "Theme", "Female", "Male", "Female-Male Gap", "Priority Score"]
    
    # Add color-coded priority badges
    def get_priority_badge(gap):
        try:
            if gap is None:
                return "Low", "#6c757d"
            gap_val = float(gap)
            gap_val = abs(gap_val)
        except (ValueError, TypeError):
            return "Low", "#6c757d"
        if gap_val >= 15:
            return "High", "#dc3545"
        elif gap_val >= 8:
            return "Medium", "#ffc107"
        else:
            return "Low", "#6c757d"
    
    show["Priority"], show["Color"] = zip(*show["Female-Male Gap"].apply(get_priority_badge))
    
    # Display indicators in a organized table format
    st.markdown("""<style>
    .indicator-table { 
        width: 100%; 
        border-collapse: separate; 
        border-spacing: 0 8px;
    }
    .indicator-table th {
        background: #f0f2f6;
        padding: 12px;
        text-align: left;
        font-size: 0.75rem;
        text-transform: uppercase;
        color: #666;
    }
    .indicator-table td {
        background: white;
        padding: 14px 12px;
        border: 1px solid #e0e0e0;
        font-size: 0.85rem;
    }
    .indicator-table tr td:first-child {
        border-radius: 8px 0 0 8px;
        font-weight: 600;
    }
    .indicator-table tr td:last-child {
        border-radius: 0 8px 8px 0;
    }
    .badge-high { background: #dc3545; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .badge-medium { background: #ffc107; color: black; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    .badge-low { background: #6c757d; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
</style>""", unsafe_allow_html=True)
    
    # Build table rows
    table_html = "<table class='indicator-table'><thead><tr><th>Indicator</th><th>Female (%)</th><th>Male (%)</th><th>Gap (pp)</th><th>Priority</th></tr></thead><tbody>"
    for _, row in show.iterrows():
        badge_text, badge_color = row["Priority"], row["Color"]
        badge_class = "badge-high" if badge_text == "High" else "badge-medium" if badge_text == "Medium" else "badge-low"
        try:
            female_val = f"{float(row['Female']):.1f}" if pd.notna(row['Female']) else "N/A"
            male_val = f"{float(row['Male']):.1f}" if pd.notna(row['Male']) else "N/A"
            gap_val = f"{float(row['Female-Male Gap']):+.1f}" if pd.notna(row['Female-Male Gap']) else "N/A"
        except (ValueError, TypeError):
            female_val = male_val = gap_val = "N/A"
        
        table_html += f"<tr><td>{row['Indicator']}</td><td><b>{female_val}</b></td><td><b>{male_val}</b></td><td>{gap_val}</td><td><span class='{badge_class}'>{badge_text}</span></td></tr>"
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

# Tabs with styled containers
st.markdown("""<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .tab-content {
        background: white;
        border-radius: 0 0 12px 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>""", unsafe_allow_html=True)

snapshot_tab, ranking_tab, compare_tab = st.tabs(["District Snapshot", "District Ranking", "District vs National"])

with snapshot_tab:
    st.markdown("**Female vs Male Gap Analysis**")
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
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
    st.markdown("**Compare Across All Districts**")
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
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
    st.markdown("**District vs National Comparison**")
    st.markdown("<hr style='margin: 10px 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
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

st.markdown("---")
st.markdown("*All values are computed from processed microdata indicators with documented weighting and caveats.*")
