"""
Page: Discovery - Smart Search & Filtering
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Discovery - NYEREKA Gender", page_icon="🔎")

st.title("🔎 Smart Search & Filtering")

st.markdown("""
This page allows you to search and filter gender-related resources 
by category, year, source, and other criteria.
""")

# Load data
@st.cache_data
def load_data():
    try:
        studies = pd.read_csv("data/sample/studies.csv")
        resources = pd.read_csv("data/sample/study_resources.csv")
        return studies, resources
    except FileNotFoundError:
        st.error("Data files not found. Please ensure data files are in the correct location.")
        return pd.DataFrame(), pd.DataFrame()

studies, resources = load_data()

# Search filters
st.sidebar.header("Filters")

# Search box
search_query = st.sidebar.text_input("Search resources", "")

# Category filter
if not studies.empty:
    categories = ["All"] + list(studies["category"].unique())
    selected_category = st.sidebar.selectbox("Category", categories)
else:
    selected_category = "All"

# Year filter
if not studies.empty:
    years = ["All"] + sorted([str(y) for y in studies["year"].unique()])
    selected_year = st.sidebar.selectbox("Year", years)
else:
    selected_year = "All"

# Data type filter
if not resources.empty:
    data_types = ["All"] + list(resources["resource_type"].unique())
    selected_type = st.sidebar.selectbox("Resource Type", data_types)
else:
    selected_type = "All"

# Apply filters
filtered_studies = studies.copy()
if search_query:
    filtered_studies = filtered_studies[
        filtered_studies["study_title"].str.contains(search_query, case=False, na=False) |
        filtered_studies["description"].str.contains(search_query, case=False, na=False)
    ]

if selected_category != "All":
    filtered_studies = filtered_studies[filtered_studies["category"] == selected_category]

if selected_year != "All":
    filtered_studies = filtered_studies[filtered_studies["year"] == int(selected_year)]

# Display results
st.subheader(f"Found {len(filtered_studies)} resources")

if not filtered_studies.empty:
    for idx, row in filtered_studies.iterrows():
        with st.expander(f" {row['study_title']} ({row['year']})"):
            st.markdown(f"**Category:** {row['category']}")
            st.markdown(f"**Institution:** {row['institution']}")
            st.markdown(f"**Coverage:** {row['geographic_coverage']}")
            st.markdown(f"**Description:** {row['description']}")
            
            # Get related resources
            if not resources.empty:
                related = resources[resources["study_id"] == row["study_id"]]
                if not related.empty:
                    st.markdown("**Related Resources:**")
                    for _, res in related.iterrows():
                        if selected_type == "All" or res["resource_type"] == selected_type:
                            st.markdown(f"- [{res['resource_title']}]({res['url']}) ({res['resource_type']}, {res['file_format']})")
else:
    st.info("No resources match your filters. Try adjusting your search criteria.")
