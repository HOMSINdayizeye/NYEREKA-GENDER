"""Quarterly reports and follow-up tracking exports."""
from __future__ import annotations

import datetime as dt
import pandas as pd
import streamlit as st

from src.analytics import top_advocacy_priorities
from src.exporters import text_to_pdf_bytes
from src.loaders import has_processed_data, load_districts, load_indicators
from src.theme import apply_theme, kpi_card, render_source_links

st.set_page_config(page_title="Reports | NYEREKA", page_icon=" ", layout="wide")
apply_theme("Generating Reports (Quarterly)", "Quarterly reporting, follow-up tracking, and export-ready outputs.")

if not has_processed_data():
    st.error("Processed files are missing. Build them first:")
    st.code("python scripts/build_indicators.py", language="bash")
    st.stop()

indicators = load_indicators().dropna(subset=["value_pct"]).copy()
districts = load_districts()

if indicators.empty:
    st.error("No indicators available.")
    st.stop()

with st.sidebar:
    st.header("Quarterly Report Setup")
    quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"], index=1)
    report_year = st.selectbox("Report Year", sorted(indicators["year"].dropna().astype(int).unique().tolist(), reverse=True))

    district_map = {
        f"{row.district_name} ({row.province_name})": int(row.district_code)
        for _, row in districts.sort_values("district_name").iterrows()
    }
    district_label = st.selectbox("District", options=list(district_map.keys()), index=0)
    district_code = district_map[district_label]

    theme_options = sorted(indicators["theme"].dropna().unique().tolist())
    selected_theme = st.selectbox("Theme", options=theme_options)
    sex_focus = st.selectbox("Sex focus", ["All", "Female", "Male"], index=0)

report_df = indicators[
    (indicators["year"] == report_year)
    & (indicators["theme"] == selected_theme)
    & (indicators["geo_level"] == "district")
    & (indicators["district_code"] == district_code)
].copy()

if sex_focus != "All":
    report_df = report_df[(report_df["sex"] == sex_focus) | (report_df["sex"] == "All")]

priorities = top_advocacy_priorities(report_df, n=6)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Quarter", f"{quarter} {report_year}", "Reporting window")
with c2:
    kpi_card("District", district_label.split(" (")[0], "Target district")
with c3:
    kpi_card("Theme", selected_theme, "Priority policy area")
with c4:
    kpi_card("Indicators", f"{report_df['indicator_id'].nunique():,}", "Included in report")

st.markdown("### Quarterly Indicator Summary")
summary_cols = [
    "indicator_name",
    "sex",
    "value_pct",
    "dataset_name",
    "weight_var",
    "caveat",
]
st.dataframe(report_df[summary_cols].sort_values(["indicator_name", "sex"]), use_container_width=True, hide_index=True)

st.markdown("### Priority Gaps")
if priorities.empty:
    st.info("No paired male/female priorities for this filter. Adjust theme or sex focus.")
else:
    pshow = priorities[["indicator_name", "Female", "Male", "gap_f_minus_m", "priority_score", "dataset_name"]].copy()
    pshow.columns = ["Indicator", "Female", "Male", "Gap (F-M)", "Priority", "Source"]
    st.dataframe(pshow.round(2), use_container_width=True, hide_index=True)

st.markdown("### Source Access Links")
source_table = (
    report_df[["dataset_name", "year", "source_url"]]
    .drop_duplicates()
    .sort_values(["year", "dataset_name"], ascending=[False, True])
)
if source_table.empty:
    st.info("No source links available for this report filter.")
else:
    st.dataframe(
        source_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "source_url": st.column_config.LinkColumn("Open Source", display_text="Open in new tab"),
        },
    )
    render_source_links(source_table, meta_cols=["year"])

st.markdown("### Follow-up Tracker")
followups = pd.DataFrame(
    [
        {
            "Action": f"Validate {selected_theme} numbers with district statistics office",
            "Owner": "Data Officer",
            "Deadline": f"End of {quarter}",
            "Status": "Pending",
        },
        {
            "Action": "Hold stakeholder review meeting (district + ministry)",
            "Owner": "Advocacy Lead",
            "Deadline": f"Mid-{quarter}",
            "Status": "Pending",
        },
        {
            "Action": "Submit policy brief with budget ask",
            "Owner": "Program Lead",
            "Deadline": f"End of {quarter}",
            "Status": "Pending",
        },
    ]
)
st.dataframe(followups, use_container_width=True, hide_index=True)

st.markdown("### Export")
report_export = report_df.copy()
report_export["quarter"] = quarter
report_export["report_year"] = report_year

brief_lines = [
    f"NYEREKA Quarterly Report - {quarter} {report_year}",
    f"District: {district_label}",
    f"Theme: {selected_theme}",
    f"Sex focus: {sex_focus}",
    f"Generated: {dt.date.today().isoformat()}",
    "",
    "Key priorities:",
]

if priorities.empty:
    brief_lines.append("- No paired sex priority indicators found for this configuration.")
else:
    for row in priorities.itertuples():
        brief_lines.append(
            f"- {row.indicator_name}: Female {row.Female:.2f}% vs Male {row.Male:.2f}% (Gap {row.gap_f_minus_m:.2f} pp)"
        )

brief_lines.append("")
brief_lines.append("Follow-ups:")
for item in followups["Action"].tolist():
    brief_lines.append(f"- {item}")

brief_text = "\n".join(brief_lines)
brief_pdf = text_to_pdf_bytes(
    f"NYEREKA Quarterly Report - {district_label}",
    brief_text,
)

st.download_button(
    "Download Quarterly Data (CSV)",
    data=report_export.to_csv(index=False),
    file_name=f"nyereka_quarterly_{report_year}_{quarter}_{district_code}.csv",
    mime="text/csv",
)
st.download_button(
    "Download Quarterly Brief (PDF)",
    data=brief_pdf,
    file_name=f"nyereka_quarterly_brief_{report_year}_{quarter}_{district_code}.pdf",
    mime="application/pdf",
)
