"""
NYEREKA Gender Data Portal
Main entry point - Streamlit application
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="NYEREKA Gender",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E5077;
    }
    .highlight {
        background-color: #E8F4FD;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    # Header
    st.markdown('<p class="main-header">🔍 NYEREKA Gender Data Portal</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Welcome section
    st.markdown("""
    ### Welcome to NYEREKA Gender
    
    This application helps CSOs and policy actors discover, interpret, and use 
    gender-related resources with less friction.
    
    **Quick Start**: Use the navigation menu on the left to explore different features.
    """)
    
    # Feature highlights
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### 🔎 Discovery
        Search and filter gender-related resources by category, year, and source.
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Dashboard
        View district-level insights and visualizations.
        """)
    
    with col3:
        st.markdown("""
        ### ⚠️ Data Quality
        Understand data quality indicators and limitations.
        """)
    
    with col4:
        st.markdown("""
        ### 🎯 Advocacy
        Generate recommendations for advocacy and policy.
        """)
    
    st.markdown("---")
    
    # Sidebar navigation info
    st.sidebar.title("Navigation")
    st.sidebar.info(
        "Use the pages in the sidebar to navigate through different features:\n\n"
        "1. **Discovery** - Smart search & filtering\n"
        "2. **Dashboard** - District insights & visualization\n"
        "3. **Data Quality** - Quality indicators\n"
        "4. **Advocacy Assistant** - Recommendations (Key Feature)\n"
        "5. **Reports** - Generate/export insights"
    )
    
    # Team info in sidebar
    st.sidebar.title("Team")
    st.sidebar.markdown("""
    **NYEREKA GENDER Team**
    
    - Amos NDAYIZEYE
    - Amos MUSABYIMANA
    - Abraham TUYISHIME
    """)


if __name__ == "__main__":
    main()
