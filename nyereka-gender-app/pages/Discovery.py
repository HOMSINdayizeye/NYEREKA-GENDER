"""Smart search and filtering across indicators and data sources."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analytics import direction_for, district_vs_national
from src.loaders import has_processed_data, load_districts, load_indicators, load_sources
from src.theme import apply_theme, kpi_card, render_source_links

st.set_page_config(page_title="Discovery | NYEREKA", page_icon=" ", layout="wide")
apply_theme("Smart Search and Filtering", "Search indicators, inspect summaries, and generate recommendation-ready insights.")

# ── Sidebar styling ────────────────────────────────────────────────────────────
st.markdown("""<style>
[data-testid="stSidebar"] { background-color: #1D3557 !important; }
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.95) !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: rgba(255,255,255,0.95) !important; }
[data-testid="stSidebar"] .stMarkdown p { color: rgba(255,255,255,0.9) !important; }
[data-testid="stSidebar"] label { color: rgba(255,255,255,0.95) !important; font-weight: 500 !important; }
[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.95) !important; }
[data-testid="stSidebar"] .stMultiSelect label { color: rgba(255,255,255,0.95) !important; }
[data-testid="stSidebar"] .stCheckbox label { color: rgba(255,255,255,0.9) !important; }

/* ── Search text input fix ── */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    color: #1D3557 !important;
    background-color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
    border-radius: 6px !important;
    caret-color: #1D3557 !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
    color: #6c757d !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    color: #1D3557 !important;
    background-color: #ffffff !important;
    border-color: #A8DADC !important;
    outline: none !important;
}

/* ── Select boxes ── */
[data-testid="stSidebar"] [data-baseweb="select"] { color: white !important; }
[data-testid="stSidebar"] div[data-baseweb="select"] > div { color: white !important; background-color: transparent !important; }
[data-testid="stSidebar"] [class*="singleValue"] { color: white !important; }
[data-testid="stSidebar"] span[data-text="true"] { color: white !important; }
</style>""", unsafe_allow_html=True)

# ── Discovery page styling ─────────────────────────────────────────────────────
st.markdown("""<style>
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
    .rec-card {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #dc3545;
    }
    .rec-card.alt { border-left-color: #ffc107; }
    .rec-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 8px; }
    .rec-meta { font-size: 0.8rem; color: #666; }
    .rec-gap { font-weight: bold; color: #dc3545; }
    .rec-gap.positive { color: #28a745; }
</style>""", unsafe_allow_html=True)

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
    st.markdown("<div class='sidebar-title'>Search Controls</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'><div class='sidebar-section-title'>Search</div>", unsafe_allow_html=True)
    query = st.text_input("Search keyword", placeholder="e.g. unemployment, violence")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'><div class='sidebar-section-title'>Filters</div>", unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'><div class='sidebar-section-title'>Recommendation</div>", unsafe_allow_html=True)
    district_label_map = {
        f"{row.district_name} ({row.province_name})": int(row.district_code)
        for _, row in districts.sort_values("district_name").iterrows()
    }
    selected_district_label = st.selectbox("Recommendation district", options=list(district_label_map.keys()))
    selected_district = district_label_map[selected_district_label]
    st.markdown("</div>", unsafe_allow_html=True)

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
    st.markdown(f'<div class="kpi-tile"><div class="kpi-tile-label">MATCHED ROWS</div><div class="kpi-tile-value">{len(flt):,}</div><div class="kpi-tile-sub">Filtered observations</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-tile alt1"><div class="kpi-tile-label">INDICATORS</div><div class="kpi-tile-value">{flt["indicator_id"].nunique():,}</div><div class="kpi-tile-sub">Distinct definitions</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-tile alt2"><div class="kpi-tile-label">DATASETS</div><div class="kpi-tile-value">{flt["dataset_name"].nunique():,}</div><div class="kpi-tile-sub">Sources included</div></div>', unsafe_allow_html=True)
with c4:
    mean_val = flt["value_pct"].mean() if not flt.empty else 0
    st.markdown(f'<div class="kpi-tile alt3"><div class="kpi-tile-label">MEAN VALUE</div><div class="kpi-tile-value">{mean_val:.1f}%</div><div class="kpi-tile-sub">Average across rows</div></div>', unsafe_allow_html=True)

st.markdown("### Resource Summaries and Insights")
summary = (
    flt.groupby(["indicator_name", "theme", "dataset_name"], as_index=False)
    .agg(avg_value=("value_pct", "mean"), latest_year=("year", "max"), records=("value_pct", "count"))
    .sort_values(["theme", "indicator_name"])
)
with st.expander("View Summary Table"):
    st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("### Smart Search Results")
show_cols = [
    "indicator_name", "theme", "dataset_name", "year", "geo_level",
    "district_name", "province_name", "sex", "value_pct", "weight_var", "caveat",
]
with st.expander(f"View {len(flt)} Search Results"):
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
        recommend_rows.append({
            "Indicator": row["indicator_name"],
            "Theme": row["theme"],
            "District": selected_district_label,
            "District Value": round(district_v, 2),
            "National Value": round(national_v, 2),
            "Gap": round(diff, 2),
            "Action": "Priority follow-up recommended",
        })

if recommend_rows:
    rec_df = pd.DataFrame(recommend_rows).sort_values("Gap")
    cols = st.columns(min(2, len(rec_df)))
    for idx, row in rec_df.iterrows():
        with cols[idx % 2]:
            gap_class = "rec-card" if row["Gap"] < 0 else "rec-card alt"
            gap_color = "#dc3545" if row["Gap"] < 0 else "#ffc107"
            st.markdown(
                f"""
                <div class="{gap_class}">
                    <div class="rec-title">{row['Indicator']}</div>
                    <div class="rec-meta">
                        <strong>Theme:</strong> {row['Theme']}<br>
                        <strong>District:</strong> {row['District']}<br>
                        <strong>District Value:</strong> {row['District Value']}% | <strong>National:</strong> {row['National Value']}%<br>
                        <span class="rec-gap" style="color:{gap_color};">Gap: {row['Gap']:+.2f} pp</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.success("No high-priority underperformance found for current search/filter combination.")

st.markdown("### Source Links")
source_table = (
    sources[["dataset_name", "year", "theme", "source_url"]]
    .drop_duplicates()
    .sort_values(["year", "dataset_name"], ascending=[False, True])
)
with st.expander(f"View {len(source_table)} Source Links"):
    st.dataframe(
        source_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "source_url": st.column_config.LinkColumn("Open Source", display_text="Open in new tab"),
        },
    )
render_source_links(source_table, meta_cols=["year", "theme"])
