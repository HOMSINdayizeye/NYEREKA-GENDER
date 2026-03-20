"""
Page: Data Quality - Quality Indicators
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Quality - NYEREKA Gender", page_icon=" ")

st.title(" Data Quality Indicators")

st.markdown("""
This page displays data quality indicators and limitations for each resource.
Use this information to understand the reliability of the data.
""")

# Load data
@st.cache_data
def load_data():
    try:
        resources = pd.read_csv("data/sample/study_resources.csv")
        quality = pd.read_csv("data/sample/quality_report.csv")
        return resources, quality
    except FileNotFoundError:
        st.error("Data files not found.")
        return pd.DataFrame(), pd.DataFrame()

resources, quality = load_data()

# Quality badge legend
st.sidebar.subheader("Quality Badges")
st.sidebar.info("""
**🟢 High Quality**: Official source, recent data, comprehensive coverage

**🟡 Medium Quality**: Reliable source, older data, partial coverage

**🔴 Limited**: Older data, narrow scope, incomplete documentation
""")

# Quality overview
st.subheader("Quality Overview")

if not quality.empty:
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_quality = len(quality[quality["quality_badge"] == "High"])
        st.metric("High Quality Resources", high_quality)
    
    with col2:
        medium_quality = len(quality[quality["quality_badge"] == "Medium"])
        st.metric("Medium Quality Resources", medium_quality)
    
    with col3:
        avg_score = quality["quality_score"].mean()
        st.metric("Average Quality Score", f"{avg_score:.1f}")
    
    st.markdown("---")
    
    # Quality details table
    st.subheader("Resource Quality Details")
    
    # Merge with resource info
    if not resources.empty:
        merged = resources.merge(quality, on="resource_id")
        
        # Display with color-coded badges
        for idx, row in merged.iterrows():
            badge_color = "🟢" if row["quality_badge"] == "High" else "🟡" if row["quality_badge"] == "Medium" else "🔴"
            
            with st.expander(f"{badge_color} {row['resource_title']} (Score: {row['quality_score']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Quality Badge:** {badge_color} {row['quality_badge']}")
                    st.markdown(f"**Quality Score:** {row['quality_score']}/100")
                    st.markdown(f"**Source Authority:** {row['source_authority']}/100")
                    st.markdown(f"**Freshness:** {row['freshness']}/100")
                
                with col2:
                    st.markdown(f"**Coverage:** {row['coverage']}/100")
                    st.markdown(f"**Documentation:** {row['documentation']}/100")
                    st.markdown(f"**Validation Status:** {row['validation_status']}")
                    st.markdown(f"**Last Validated:** {row['last_validated']}")
                
                st.markdown("---")
                st.markdown(f"** Caveats:** {row['caveats']}")
else:
    st.info("No quality data available")

# Quality factors explanation
st.markdown("---")
st.subheader("Understanding Quality Scores")

st.markdown("""
The quality score is calculated based on four factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Freshness | 30% | How recent the data is |
| Source Authority | 30% | Credibility of the data source |
| Coverage | 20% | Geographic and demographic coverage |
| Documentation | 20% | Quality of metadata and documentation |

**Note:** Higher scores indicate better overall quality, but users should 
consider the specific caveats for each resource when using the data for advocacy.
""")
