"""
Data Loaders - Load and preprocess data
"""
import pandas as pd
from pathlib import Path


def get_data_path(filename: str) -> Path:
    """Get path to data file."""
    return Path(__file__).parent.parent / "data" / "sample" / filename


def load_studies() -> pd.DataFrame:
    """Load studies data."""
    try:
        return pd.read_csv(get_data_path("studies.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_resources() -> pd.DataFrame:
    """Load study resources data."""
    try:
        return pd.read_csv(get_data_path("study_resources.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_quality() -> pd.DataFrame():
    """Load quality report data."""
    try:
        return pd.read_csv(get_data_path("quality_report.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_all_data() -> tuple:
    """Load all data files and return as tuple."""
    return load_studies(), load_resources(), load_quality()


def preprocess_studies(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess studies data."""
    if df.empty:
        return df
    
    # Ensure year is integer
    df["year"] = df["year"].astype(int)
    
    # Clean category names
    df["category"] = df["category"].str.strip()
    
    return df


def preprocess_resources(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess resources data."""
    if df.empty:
        return df
    
    # Ensure file size is numeric
    df["file_size_mb"] = pd.to_numeric(df["file_size_mb"], errors="coerce")
    
    return df


def preprocess_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess quality data."""
    if df.empty:
        return df
    
    # Ensure scores are numeric
    numeric_cols = ["quality_score", "source_authority", "freshness", "coverage", "documentation"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df
