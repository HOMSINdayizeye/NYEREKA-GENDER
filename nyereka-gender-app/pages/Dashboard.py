"""
Page: Dashboard - District Insights & Visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard - NYEREKA Gender", page_icon="")

st.title(" District Insights & Visualization")

st.markdown("""
This dashboard provides visualizations and insights on gender-related 
data across Rwanda's districts.
""")

# Load data
@st.cache_data
def load_data():
    try:
        studies = pd.read_csv("data/sample/studies.csv")
        resources = pd.read_csv("data/sample/study_resources.csv")
        quality = pd.read_csv("data/sample/quality_report.csv")
        return studies, resources, quality
    except FileNotFoundError:
        st.error("Data files not found.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

studies, resources, quality = load_data()

# KPI metrics
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Studies", len(studies))

with col2:
    st.metric("Total Resources", len(resources))

with col3:
    if not quality.empty:
        avg_quality = quality["quality_score"].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.1f}")
    else:
        st.metric("Avg Quality Score", "N/A")

with col4:
    if not studies.empty:
        latest_year = studies["year"].max()
        st.metric("Latest Data Year", latest_year)
    else:
        st.metric("Latest Data Year", "N/A")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Resources by Category")
    if not studies.empty:
        category_counts = studies["category"].value_counts().reset_index()
        category_counts.columns = ["Category", "Count"]
        fig = px.bar(category_counts, x="Category", y="Count", 
                     color="Category", title="Studies by Category")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available")

with col2:
    st.subheader("Resources by Type")
    if not resources.empty:
        type_counts = resources["resource_type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        fig2 = px.pie(type_counts, values="Count", names="Type", 
                      title="Resources by Type")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data available")

st.markdown("---")

# Quality distribution
st.subheader("Data Quality Distribution")
if not quality.empty:
    fig3 = px.histogram(quality, x="quality_score", nbins=10, 
                        title="Quality Score Distribution",
                        labels={"quality_score": "Quality Score"})
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No quality data available")

# District coverage
st.subheader("Geographic Coverage")
if not studies.empty:
    coverage_counts = studies["geographic_coverage"].value_counts()
    st.bar_chart(coverage_counts)
else:
    st.info("No coverage data available")
