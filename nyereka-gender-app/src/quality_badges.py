"""
Data Quality Indicators - Quality badges and scoring
"""
import pandas as pd
from typing import Optional


# Quality thresholds
QUALITY_THRESHOLDS = {
    "High": 80,
    "Medium": 60,
    "Low": 0
}


# Badge colors for display
BADGE_EMOJI = {
    "High": "🟢",
    "Medium": "🟡",
    "Low": "🔴"
}


def calculate_quality_score(
    source_authority: int,
    freshness: int,
    coverage: int,
    documentation: int
) -> float:
    """
    Calculate overall quality score.
    
    Args:
        source_authority: 0-100 score for source credibility
        freshness: 0-100 score for data recency
        coverage: 0-100 score for geographic/demographic coverage
        documentation: 0-100 score for metadata quality
    
    Returns:
        Weighted quality score (0-100)
    """
    weights = {
        "freshness": 0.3,
        "authority": 0.3,
        "coverage": 0.2,
        "documentation": 0.2
    }
    
    score = (
        (freshness * weights["freshness"]) +
        (source_authority * weights["authority"]) +
        (coverage * weights["coverage"]) +
        (documentation * weights["documentation"])
    )
    
    return round(score, 1)


def get_quality_badge(score: float) -> str:
    """
    Get quality badge based on score.
    
    Args:
        score: Quality score (0-100)
    
    Returns:
        Quality badge string
    """
    if score >= QUALITY_THRESHOLDS["High"]:
        return "High"
    elif score >= QUALITY_THRESHOLDS["Medium"]:
        return "Medium"
    else:
        return "Low"


def get_badge_with_emoji(badge: str) -> str:
    """Get badge with emoji prefix."""
    return f"{BADGE_EMOJI.get(badge, '⚪')} {badge}"


def format_quality_display(score: float, badge: str) -> str:
    """Format quality score for display."""
    emoji = BADGE_EMOJI.get(badge, "⚪")
    return f"{emoji} {badge} ({score}/100)"


def assess_freshness(year: int, current_year: int = 2024) -> int:
    """
    Assess data freshness based on year.
    
    Args:
        year: Data year
        current_year: Reference year
    
    Returns:
        Freshness score (0-100)
    """
    age = current_year - year
    
    if age <= 1:
        return 100
    elif age <= 2:
        return 90
    elif age <= 3:
        return 80
    elif age <= 5:
        return 70
    elif age <= 7:
        return 50
    else:
        return 30


def assess_source_authority(institution: str) -> int:
    """
    Assess source authority based on institution.
    
    Args:
        institution: Source institution name
    
    Returns:
        Authority score (0-100)
    """
    # Government sources get highest score
    government_keywords = ["nisr", "government", "ministry", "national institute", "statistics"]
    
    # Research/NGO sources get medium score
    research_keywords = ["university", "research", "institute", "ngos", "world bank", "unicef", "un women"]
    
    institution_lower = institution.lower()
    
    if any(kw in institution_lower for kw in government_keywords):
        return 100
    elif any(kw in institution_lower for kw in research_keywords):
        return 75
    else:
        return 50


def assess_coverage(geographic_coverage: str, disaggregation: str) -> int:
    """
    Assess data coverage.
    
    Args:
        geographic_coverage: Geographic scope
        disaggregation: Available disaggregation options
    
    Returns:
        Coverage score (0-100)
    """
    score = 50  # Base score
    
    # Geographic coverage scoring
    if geographic_coverage.lower() == "national":
        score += 20
    elif geographic_coverage.lower() == "province":
        score += 15
    elif geographic_coverage.lower() == "district":
        score += 25
    
    # Disaggregation scoring
    if disaggregation and disaggregation != "N/A":
        disagg_options = len([x for x in disaggregation.split(",") if x.strip()])
        score += min(disagg_options * 10, 25)
    
    return min(score, 100)


def assess_documentation(has_description: bool, has_metadata: bool) -> int:
    """
    Assess documentation quality.
    
    Args:
        has_description: Whether description exists
        has_metadata: Whether metadata exists
    
    Returns:
        Documentation score (0-100)
    """
    score = 50
    
    if has_description:
        score += 25
    
    if has_metadata:
        score += 25
    
    return min(score, 100)


def generate_quality_report(
    df: pd.DataFrame,
    year_col: str = "year",
    institution_col: str = "institution",
    coverage_col: str = "geographic_coverage",
    disagg_col: str = "disaggregation"
) -> pd.DataFrame:
    """
    Generate quality report for a dataframe.
    
    Args:
        df: Input dataframe
        year_col: Column name for year
        institution_col: Column name for institution
        coverage_col: Column name for geographic coverage
        disagg_col: Column name for disaggregation
    
    Returns:
        Dataframe with quality scores
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    # Calculate individual scores
    result["freshness"] = result[year_col].apply(assess_freshness)
    result["source_authority"] = result[institution_col].apply(assess_source_authority)
    
    if coverage_col in result.columns and disagg_col in result.columns:
        result["coverage"] = result.apply(
            lambda x: assess_coverage(x[coverage_col], x.get(disagg_col, "")), 
            axis=1
        )
    
    # Calculate overall score
    result["quality_score"] = result.apply(
        lambda x: calculate_quality_score(
            x["source_authority"],
            x["freshness"],
            x.get("coverage", 50),
            x.get("documentation", 50)
        ),
        axis=1
    )
    
    # Add badge
    result["quality_badge"] = result["quality_score"].apply(get_quality_badge)
    
    return result


def get_quality_summary(quality_df: pd.DataFrame) -> dict:
    """
    Get summary statistics for quality data.
    
    Args:
        quality_df: Dataframe with quality information
    
    Returns:
        Dictionary with summary stats
    """
    if quality_df.empty:
        return {}
    
    return {
        "total_resources": len(quality_df),
        "average_score": quality_df["quality_score"].mean(),
        "high_quality_count": len(quality_df[quality_df["quality_badge"] == "High"]),
        "medium_quality_count": len(quality_df[quality_df["quality_badge"] == "Medium"]),
        "low_quality_count": len(quality_df[quality_df["quality_badge"] == "Low"]),
        "average_freshness": quality_df["freshness"].mean(),
        "average_authority": quality_df["source_authority"].mean()
    }
