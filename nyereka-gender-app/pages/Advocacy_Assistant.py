"""Advocacy assistant with recommendations and follow-up actions."""
from __future__ import annotations

import datetime as dt
import streamlit as st

from src.analytics import top_advocacy_priorities
from src.exporters import text_to_pdf_bytes
from src.loaders import has_processed_data, load_districts, load_indicators
from src.theme import apply_theme, kpi_card, render_source_links

st.set_page_config(page_title="Advocacy Assistant | NYEREKA", page_icon=" ", layout="wide")
apply_theme("Advocacy Assistant", "Generate recommendations, follow-ups, and downloadable advocacy briefs.")

if not has_processed_data():
    st.error("Processed files are missing. Build them first:")
    st.code("python scripts/build_indicators.py", language="bash")
    st.stop()

indicators = load_indicators().dropna(subset=["value_pct"]).copy()
districts = load_districts()

if indicators.empty:
    st.error("No indicators found.")
    st.stop()

THEME_RECOMMENDATIONS = {
    "Employment": [
        "Scale district women-focused TVET and placement programs.",
        "Create wage-employment incentives for firms hiring women in formal jobs.",
        "Expand childcare support for working mothers in low-income sectors.",
    ],
    "Education": [
        "Target girls' attendance support in underperforming sectors and cells.",
        "Fund retention packages: sanitary kits, transport, and mentoring.",
        "Prioritize school-to-work transition pathways for adolescent girls.",
    ],
    "Health": [
        "Strengthen outreach for women's health insurance enrollment.",
        "Link community health workers with vulnerable households for referrals.",
        "Track district-level maternal and reproductive health service gaps quarterly.",
    ],
    "GBV": [
        "Increase confidential GBV reporting channels and survivor case management.",
        "Expand legal aid and psychosocial services at district level.",
        "Integrate GBV prevention messaging in schools and community forums.",
    ],
    "Finance": [
        "Promote women-owned savings and transaction accounts.",
        "Subsidize mobile-money onboarding for low-income women groups.",
        "Expand district-level financial literacy and digital finance training.",
    ],
    "Leadership": [
        "Support women leadership pipelines in local enterprises and cooperatives.",
        "Set district targets for women in managerial and decision-making roles.",
        "Publicly track women leadership indicators in quarterly reviews.",
    ],
}

with st.sidebar:
    st.header("Brief Configuration")
    district_label_map = {
        f"{row.district_name} ({row.province_name})": int(row.district_code)
        for _, row in districts.sort_values("district_name").iterrows()
    }
    default_label = next((k for k, v in district_label_map.items() if v == 24), list(district_label_map.keys())[0])
    district_label = st.selectbox("District", options=list(district_label_map.keys()), index=list(district_label_map.keys()).index(default_label))
    district_code = district_label_map[district_label]

    theme_options = sorted(indicators["theme"].dropna().unique().tolist())
    issue_theme = st.selectbox("Issue Theme", options=theme_options)

    audience = st.selectbox("Target Audience", ["District Leaders", "Ministry Officials", "Development Partners", "Civil Society Coalition"])
    quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"], index=1)

focus = indicators[(indicators["geo_level"] == "district") & (indicators["district_code"] == district_code)]
focus_theme = focus[focus["theme"] == issue_theme]
priorities = top_advocacy_priorities(focus_theme, n=5)

c1, c2, c3 = st.columns(3)
with c1:
    kpi_card("District", district_label.split(" (")[0], "Advocacy target")
with c2:
    kpi_card("Theme", issue_theme, "Policy focus area")
with c3:
    kpi_card("Priority Signals", f"{len(priorities):,}", "Detected female disadvantage indicators")

st.markdown("### Priority Evidence")
if priorities.empty:
    st.info("No paired male/female indicators in this theme for selected district. Try another theme.")
else:
    evidence = priorities[["indicator_name", "Female", "Male", "gap_f_minus_m", "dataset_name", "year"]].copy()
    evidence.columns = ["Indicator", "Female", "Male", "Gap (F-M)", "Source", "Year"]
    st.dataframe(evidence.round(2), use_container_width=True, hide_index=True)

st.markdown("### System Recommendations")
for idx, item in enumerate(THEME_RECOMMENDATIONS.get(issue_theme, ["No recommendation template for this theme yet."]), start=1):
    st.markdown(f"{idx}. {item}")

st.markdown("### Follow-ups")
follow_ups = [
    f"Validate {issue_theme} indicators with district planning office before end of {quarter}.",
    "Schedule one policy review meeting with district + ministry focal points.",
    "Prepare one-page budget ask linked directly to the top 3 indicator gaps.",
    "Set quarterly monitoring checkpoints and assign responsible officers.",
]
for i, item in enumerate(follow_ups, start=1):
    st.checkbox(f"Follow-up {i}: {item}", key=f"fu_{i}")

st.markdown("### Generated Advocacy Brief")
today = dt.date.today().isoformat()
priority_text = "\n".join(
    [
        f"- {row.indicator_name}: Female {row.Female:.2f}% vs Male {row.Male:.2f}% (gap {row.gap_f_minus_m:.2f} pp)"
        for row in priorities.itertuples()
    ]
) or "- No paired sex indicators detected for this theme/district combination."

recommendation_text = "\n".join([f"- {r}" for r in THEME_RECOMMENDATIONS.get(issue_theme, [])])
follow_text = "\n".join([f"- {f}" for f in follow_ups])

brief = f"""
ADVOCACY BRIEF
Date: {today}
District: {district_label}
Theme: {issue_theme}
Audience: {audience}
Quarter: {quarter}

1) Key evidence
{priority_text}

2) Recommendations
{recommendation_text}

3) Follow-ups
{follow_text}
""".strip()

st.text_area("Brief preview", value=brief, height=300)
brief_pdf = text_to_pdf_bytes(
    f"NYEREKA Advocacy Brief - {district_label}",
    brief,
)
st.download_button(
    "Download advocacy brief (PDF)",
    data=brief_pdf,
    file_name=f"nyereka_brief_{district_code}_{issue_theme.lower()}.pdf",
    mime="application/pdf",
)

if not priorities.empty:
    st.markdown("### Evidence Source Links")
    source_df = priorities[["dataset_name", "year"]].drop_duplicates().copy()
    source_df["source_url"] = source_df["dataset_name"].map(
        {
            ds: url
            for ds, url in (
                indicators[["dataset_name", "source_url"]]
                .drop_duplicates()
                .itertuples(index=False, name=None)
            )
        }
    )
    render_source_links(source_df.dropna(subset=["source_url"]), meta_cols=["year"])
