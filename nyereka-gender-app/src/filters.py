"""
Search and Filtering Logic
"""
import pandas as pd
from typing import List, Optional


def filter_by_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """Filter dataframe by category."""
    if category == "All" or not category:
        return df
    return df[df["category"] == category]


def filter_by_year(df: pd.DataFrame, year: str) -> pd.DataFrame:
    """Filter dataframe by year."""
    if year == "All" or not year:
        return df
    try:
        return df[df["year"] == int(year)]
    except ValueError:
        return df


def filter_by_resource_type(df: pd.DataFrame, resource_type: str) -> pd.DataFrame:
    """Filter dataframe by resource type."""
    if resource_type == "All" or not resource_type:
        return df
    return df[df["resource_type"] == resource_type]


def filter_by_search(df: pd.DataFrame, query: str, columns: List[str]) -> pd.DataFrame:
    """Filter dataframe by search query."""
    if not query:
        return df
    
    query = query.lower()
    mask = pd.Series([False] * len(df))
    
    for col in columns:
        if col in df.columns:
            mask |= df[col].astype(str).str.lower().str.contains(query, na=False)
    
    return df[mask]


def filter_by_quality(df: pd.DataFrame, min_score: int = 0, badge: Optional[str] = None) -> pd.DataFrame:
    """Filter dataframe by quality criteria."""
    if min_score > 0:
        df = df[df["quality_score"] >= min_score]
    
    if badge and badge != "All":
        df = df[df["quality_badge"] == badge]
    
    return df


def filter_by_geographic_coverage(df: pd.DataFrame, coverage: str) -> pd.DataFrame:
    """Filter dataframe by geographic coverage."""
    if coverage == "All" or not coverage:
        return df
    return df[df["geographic_coverage"] == coverage]


def get_unique_values(df: pd.DataFrame, column: str) -> List[str]:
    """Get unique values from a column."""
    if column in df.columns:
        return sorted(df[column].dropna().unique().tolist())
    return []


def apply_all_filters(
    studies_df: pd.DataFrame,
    resources_df: pd.DataFrame,
    quality_df: pd.DataFrame,
    category: str = "All",
    year: str = "All",
    resource_type: str = "All",
    search_query: str = "",
    min_quality: int = 0,
    quality_badge: Optional[str] = None
) -> tuple:
    """Apply all filters to dataframes and return filtered results."""
    
    # Filter studies
    filtered_studies = studies_df.copy()
    
    if search_query:
        filtered_studies = filter_by_search(
            filtered_studies, 
            search_query, 
            ["study_title", "description", "institution"]
        )
    
    filtered_studies = filter_by_category(filtered_studies, category)
    filtered_studies = filter_by_year(filtered_studies, year)
    
    # Filter resources
    filtered_resources = resources_df.copy()
    filtered_resources = filter_by_resource_type(filtered_resources, resource_type)
    
    # Filter by study IDs
    if not filtered_studies.empty:
        study_ids = filtered_studies["study_id"].tolist()
        filtered_resources = filtered_resources[filtered_resources["study_id"].isin(study_ids)]
    
    # Filter quality
    filtered_quality = quality_df.copy()
    filtered_quality = filter_by_quality(filtered_quality, min_quality, quality_badge)
    
    return filtered_studies, filtered_resources, filtered_quality
