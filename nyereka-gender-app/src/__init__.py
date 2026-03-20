"""
NYEREKA Gender - Source Package
"""

from .loaders import load_studies, load_resources, load_quality, load_all_data
from .filters import filter_by_category, filter_by_year, filter_by_search, apply_all_filters
from .link_checker import check_url_accessibility, validate_resource_links
from .quality_badges import calculate_quality_score, get_quality_badge, get_badge_with_emoji
from .insights import get_category_insights, generate_advocacy_brief, generate_policy_recommendation

__all__ = [
    "load_studies",
    "load_resources",
    "load_quality",
    "load_all_data",
    "filter_by_category",
    "filter_by_year",
    "filter_by_search",
    "apply_all_filters",
    "check_url_accessibility",
    "validate_resource_links",
    "calculate_quality_score",
    "get_quality_badge",
    "get_badge_with_emoji",
    "get_category_insights",
    "generate_advocacy_brief",
    "generate_policy_recommendation"
]
