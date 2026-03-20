"""
Insights - Generate insights and recommendations for advocacy
"""
import pandas as pd
from typing import Dict, List, Optional


# Category-specific insights
CATEGORY_INSIGHTS = {
    "Education": {
        "key_indicators": [
            "Primary completion rate",
            "Secondary completion rate",
            "Tertiary enrollment",
            "STEM enrollment by gender"
        ],
        "common_gaps": [
            "Rural vs urban disparities",
            "Economic barriers",
            "Safety concerns",
            "Household responsibilities"
        ],
        "recommendations": [
            "Advocate for increased education budget",
            "Propose scholarship programs",
            "Support mentorship initiatives",
            "Launch community awareness campaigns"
        ]
    },
    "Health": {
        "key_indicators": [
            "Maternal mortality ratio",
            "Access to reproductive health",
            "HIV prevalence",
            "Mental health services"
        ],
        "common_gaps": [
            "Rural healthcare access",
            "Service quality",
            "Health worker availability",
            "Affordability"
        ],
        "recommendations": [
            "Advocate for health infrastructure",
            "Support health worker training",
            "Promote health education",
            "Push for universal health coverage"
        ]
    },
    "Employment": {
        "key_indicators": [
            "Labor force participation",
            "Unemployment rate",
            "Wage gap",
            "Formal vs informal employment"
        ],
        "common_gaps": [
            "Sector segregation",
            "Career advancement",
            "Work-life balance",
            "Access to credit"
        ],
        "recommendations": [
            "Promote women's employment policies",
            "Support vocational training",
            "Advocate for entrepreneurship support",
            "Push for equal pay legislation"
        ]
    },
    "Violence": {
        "key_indicators": [
            "Prevalence rates",
            "Reporting rates",
            "Service access",
            "Legal outcomes"
        ],
        "common_gaps": [
            "Underreporting",
            "Service availability",
            "Legal support",
            "Shelter capacity"
        ],
        "recommendations": [
            "Advocate for GBV prevention programs",
            "Support service expansion",
            "Push for legal reform",
            "Promote awareness campaigns"
        ]
    },
    "Leadership": {
        "key_indicators": [
            "Political representation",
            "Senior management positions",
            "Board representation",
            "Entrepreneurship"
        ],
        "common_gaps": [
            "Senior position gaps",
            "Industry barriers",
            "Network access",
            "Family responsibilities"
        ],
        "recommendations": [
            "Advocate for gender quotas",
            "Create mentorship programs",
            "Push for family-friendly policies",
            "Support leadership training"
        ]
    }
}


def get_category_insights(category: str) -> Dict:
    """Get insights for a specific category."""
    return CATEGORY_INSIGHTS.get(category, {})


def generate_advocacy_brief(
    issue_area: str,
    target_audience: str,
    target_district: str,
    data_sources: List[str]
) -> str:
    """
    Generate an advocacy brief.
    
    Args:
        issue_area: The issue area (e.g., Education, Health)
        target_audience: Who the brief is for
        target_district: Target geographic area
        data_sources: List of data sources used
    
    Returns:
        Formatted advocacy brief string
    """
    insights = get_category_insights(issue_area)
    
    brief = f"""
# ADVOCACY BRIEF: {issue_area} Gender Analysis

## Target Audience: {target_audience}
## Target Area: {target_district}

---

## Issue Summary

{issue_area} remains a key area requiring attention for gender equality in Rwanda.
The following brief summarizes evidence-based recommendations.

---

## Key Findings
"""
    
    if insights and "key_indicators" in insights:
        brief += "\n**Key Indicators:**\n"
        for indicator in insights["key_indicators"]:
            brief += f"- {indicator}\n"
    
    brief += "\n## Common Gaps\n"
    
    if insights and "common_gaps" in insights:
        for gap in insights["common_gaps"]:
            brief += f"- {gap}\n"
    
    brief += "\n## Data Sources\n"
    for source in data_sources:
        brief += f"- {source}\n"
    
    brief += "\n## Recommendations\n"
    
    if insights and "recommendations" in insights:
        for i, rec in enumerate(insights["recommendations"], 1):
            brief += f"{i}. {rec}\n"
    
    brief += f"""
---

## Expected Outcomes

- Improved gender outcomes in {issue_area}
- Better resource allocation
- Increased accountability
- Enhanced policy implementation

---

*Generated by NYEREKA Gender Data Portal*
"""
    
    return brief


def generate_policy_recommendation(
    category: str,
    gap: str,
    evidence: str
) -> str:
    """
    Generate a policy recommendation based on evidence.
    
    Args:
        category: Issue category
        gap: Identified gap
        evidence: Supporting evidence
    
    Returns:
        Formatted recommendation
    """
    return f"""
## Recommendation for {category}

**Gap Identified:** {gap}

**Evidence:** {evidence}

**Recommended Actions:**
1. Conduct further research to quantify the gap
2. Engage stakeholders in solution design
3. Develop targeted intervention programs
4. Monitor and evaluate implementation

**Success Metrics:**
- Define measurable outcomes
- Set baseline and targets
- Establish monitoring framework
"""


def get_district_summary(district: str, studies_df: pd.DataFrame) -> Dict:
    """
    Get summary of data available for a specific district.
    
    Args:
        district: District name
        studies_df: Studies dataframe
    
    Returns:
        Dictionary with district-specific information
    """
    if studies_df.empty:
        return {}
    
    district_studies = studies_df[
        studies_df["geographic_coverage"].str.contains(district, case=False, na=False) |
        (studies_df["geographic_coverage"] == "National")
    ]
    
    return {
        "district": district,
        "total_studies": len(district_studies),
        "categories": district_studies["category"].unique().tolist(),
        "years": sorted(district_studies["year"].unique().tolist())
    }


def generate_comparative_analysis(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    label1: str,
    label2: str
) -> str:
    """
    Generate comparative analysis between two datasets.
    
    Args:
        df1: First dataframe
        df2: Second dataframe
        label1: Label for first dataset
        label2: Label for second dataset
    
    Returns:
        Comparative analysis text
    """
    analysis = f"## Comparative Analysis\n\n"
    analysis += f"### {label1}\n"
    analysis += f"- Records: {len(df1)}\n"
    
    if not df1.empty and "year" in df1.columns:
        analysis += f"- Year range: {df1['year'].min()} - {df1['year'].max()}\n"
    
    if not df1.empty and "category" in df1.columns:
        analysis += f"- Categories: {', '.join(df1['category'].unique())}\n"
    
    analysis += f"\n### {label2}\n"
    analysis += f"- Records: {len(df2)}\n"
    
    if not df2.empty and "year" in df2.columns:
        analysis += f"- Year range: {df2['year'].min()} - {df2['year'].max()}\n"
    
    if not df2.empty and "category" in df2.columns:
        analysis += f"- Categories: {', '.join(df2['category'].unique())}\n"
    
    return analysis


def get_resource_recommendations(
    category: str,
    min_quality: int = 70
) -> List[Dict]:
    """
    Get recommended resources for a specific category.
    
    Args:
        category: Issue category
        min_quality: Minimum quality score
    
    Returns:
        List of recommended resources with metadata
    """
    # This would typically query the database
    # Returning placeholder for now
    return [
        {
            "title": f"Primary data source for {category}",
            "source": "NISR",
            "type": "Official Statistics",
            "quality": "High"
        }
    ]
