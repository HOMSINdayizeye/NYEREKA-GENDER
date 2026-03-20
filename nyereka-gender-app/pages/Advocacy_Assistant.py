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

# Advocacy Assistant styling
st.markdown("""<style>
    .rec-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 16px;
        color: white;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .rec-card-num {
        background: rgba(255,255,255,0.2);
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
    .follow-card {
        background: white;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #43e97b;
    }
    .follow-card.unchecked { border-left-color: #6c757d; }
    .follow-card.checked { border-left-color: #28a745; background: #f0fff4; }
    [data-testid="stCheckbox"] { margin-bottom: 0; }
    .brief-preview {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        border: 1px solid #e2e8f0;
    }
</style>""", unsafe_allow_html=True)

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
recommendations = THEME_RECOMMENDATIONS.get(issue_theme, ["No recommendation template for this theme yet."])
cols = st.columns(min(3, len(recommendations)))
for idx, item in enumerate(recommendations):
    with cols[idx % 3]:
        st.markdown(
            f"""
            <div class="rec-card">
                <span class="rec-card-num">{idx + 1}</span>{item}
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("### Follow-ups")
follow_ups = [
    f"Validate {issue_theme} indicators with district planning office before end of {quarter}.",
    "Schedule one policy review meeting with district + ministry focal points.",
    "Prepare one-page budget ask linked directly to the top 3 indicator gaps.",
    "Set quarterly monitoring checkpoints and assign responsible officers.",
]

# Create styled follow-up cards in 2 columns
cols = st.columns(2)
for i, item in enumerate(follow_ups):
    with cols[i % 2]:
        is_checked = st.session_state.get(f"fu_{i+1}", False)
        card_class = "follow-card checked" if is_checked else "follow-card unchecked"
        status = "Done" if is_checked else "Pending"
        status_color = "#28a745" if is_checked else "#6c757d"
        st.markdown(
            f"""
            <div class="{card_class}" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600; font-size:0.85rem;">Action {i+1}</div>
                    <div style="font-size:0.9rem; margin-top:4px;">{item}</div>
                </div>
                <div style="text-align:right;">
                    <span style="background:{status_color}; color:white; padding:4px 10px; border-radius:12px; font-size:0.7rem; font-weight:bold;">{status.upper()}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.checkbox(f"Mark complete", key=f"fu_{i+1}")

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

st.markdown("### Generated Advocacy Brief")
st.markdown(f"<div class='brief-preview'>{brief.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
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
