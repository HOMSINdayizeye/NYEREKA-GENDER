"""
Page: Advocacy Assistant - Recommendations (KEY FEATURE)
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Advocacy Assistant - NYEREKA Gender", page_icon="")

st.title(" Advocacy Assistant")
st.markdown("### KEY FEATURE")

st.markdown("""
This is the key feature of NYEREKA Gender. Use the advocacy assistant to:
1. Select an issue area
2. Get relevant data and insights
3. Generate recommendations for advocacy
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

# Issue selection
st.sidebar.subheader("Advocacy Scenario Setup")

issue_area = st.sidebar.selectbox(
    "Select Issue Area",
    ["Education", "Health", "Employment", "Violence Against Women", "Women's Leadership"]
)

target_district = st.sidebar.selectbox(
    "Target District (if applicable)",
    ["All Districts", "Kigali", "Huye", "Musanze", "Rubavu", "Nyamasheke", "Ruhango"]
)

audience = st.sidebar.selectbox(
    "Target Audience",
    ["District Leaders", "Ministry Officials", "Donors", "General Public"]
)

# Generate recommendations based on selection
st.subheader(f"Advocacy Recommendations for {issue_area}")

if issue_area == "Education":
    st.markdown("###  Education Gender Gap Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Key Findings:**
        - Girls' secondary completion rates lag behind boys in most districts
        - Disparity is most pronounced in rural areas
        - Key barriers: economic constraints, safety concerns, household responsibilities
        """)
    
    with col2:
        st.markdown("""
        **Recommended Data Sources:**
        - Rwanda Education Statistics 2022
        - DHS 2020 Education Module
        - District Education Reports
        """)
    
    st.markdown("---")
    st.markdown("### Advocacy Recommendations")
    
    st.success("""
    **1. Budget Advocacy**
    Recommend increasing education budget allocation for vulnerable girls by 15%
    
    **2. Scholarship Programs**
    Propose targeted bursary programs for girls in secondary education
    
    **3. Mentorship Initiatives**
    Establish mentorship programs connecting female students with women leaders
    
    **4. Community Engagement**
    Launch awareness campaigns on importance of girls' education
    """)
    
    # Generate brief
    st.markdown("---")
    st.subheader(" Generated Advocacy Brief")
    
    brief = f"""
    **ADVOCACY BRIEF: Closing the Gender Gap in Secondary Education**
    
    **Issue:** Girls' lower-secondary completion rates are significantly below boys 
    in {target_district if target_district != 'All Districts' else 'most Rwandan districts'}.
    
    **Evidence:** Based on DHS 2020 and Rwanda Education Statistics 2022 data.
    
    **Recommendations for {audience}:**
    1. Increase budget allocation for girls' education
    2. Establish targeted scholarship programs
    3. Create mentorship and support networks
    4. Implement community awareness programs
    
    **Expected Outcome:** Improved completion rates and better future outcomes for girls.
    """
    
    st.markdown(brief)
    
    # Download button
    st.download_button(
        label="Download Advocacy Brief",
        data=brief,
        file_name="advocacy_brief_education.txt",
        mime="text/plain"
    )

elif issue_area == "Health":
    st.markdown("###  Health Indicators Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Key Findings:**
        - Maternal mortality ratio has improved but remains a challenge
        - Access to reproductive health services varies by district
        - Gender-based health disparities exist in some areas
        """)
    
    with col2:
        st.markdown("""
        **Recommended Data Sources:**
        - DHS 2020 Health Module
        - Rwanda Health Survey 2022
        - NISR Health Statistics
        """)
    
    st.markdown("---")
    st.markdown("### Advocacy Recommendations")
    
    st.success("""
    **1. Health Infrastructure**
    Advocate for maternal health facilities in underserved areas
    
    **2. Health Worker Training**
    Support training more female health workers
    
    **3. Health Education**
    Promote reproductive health education in schools
    """)

elif issue_area == "Employment":
    st.markdown("### Employment Gender Gap Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Key Findings:**
        - Women's labor force participation is lower than men's
        - Wage gap persists across sectors
        - Informal sector employment is high among women
        """)
    
    with col2:
        st.markdown("""
        **Recommended Data Sources:**
        - Rwanda Labor Force Survey 2021
        - Youth Employment Report 2023
        - Gender Statistics Report 2021
        """)
    
    st.markdown("---")
    st.markdown("###  Advocacy Recommendations")
    
    st.success("""
    **1. Job Creation**
    Advocate for policies promoting women's employment
    
    **2. Skills Training**
    Support vocational training programs for women
    
    **3. Entrepreneurship**
    Promote women's access to credit and business development
    """)

elif issue_area == "Violence Against Women":
    st.markdown("###  Violence Against Women Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Key Findings:**
        - VAW prevalence remains a concern
        - Underreporting is likely significant
        - Support services are limited in some areas
        """)
    
    with col2:
        st.markdown("""
        **Recommended Data Sources:**
        - VAW Survey 2021
        - Police statistics
        - Service provider reports
        """)
    
    st.markdown("---")
    st.markdown("### Advocacy Recommendations")
    
    st.success("""
    **1. Prevention Programs**
    Advocate for GBV prevention programs in communities
    
    **2. Support Services**
    Support expansion of shelter and counseling services
    
    **3. Legal Reform**
    Push for implementation and enforcement of relevant laws
    """)

elif issue_area == "Women's Leadership":
    st.markdown("###  Women's Leadership Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Key Findings:**
        - Women's representation in leadership positions has improved
        - Gap remains in senior positions
        - Progress varies by sector
        """)
    
    with col2:
        st.markdown("""
        **Recommended Data Sources:**
        - Women's Leadership Study 2022
        - Gender Statistics Report 2021
        - Public Service data
        """)
    
    st.markdown("---")
    st.markdown("###  Advocacy Recommendations")
    
    st.success("""
    **1. Quota Systems**
    Advocate for stronger gender quotas in leadership
    
    **2. Mentorship**
    Create leadership mentorship programs
    
    **3. Policy Reform**
    Push for family-friendly policies in workplace
    """)

# Key resources for advocacy
st.markdown("---")
st.subheader("Key Resources for Advocacy")

if not studies.empty:
    relevant = studies[studies["category"] == issue_area]
    if relevant.empty:
        relevant = studies.head(3)
    
    for idx, row in relevant.iterrows():
        st.markdown(f"- **{row['study_title']}** ({row['year']}) - {row['institution']}")
