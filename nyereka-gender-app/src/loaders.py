"""Data loading helpers for NYEREKA dashboard."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
PROCESSED_DIR = APP_ROOT / "data" / "processed"


def processed_path(filename: str) -> Path:
    return PROCESSED_DIR / filename


def has_processed_data() -> bool:
    required = [
        processed_path("indicators.csv"),
        processed_path("indicator_catalog.csv"),
        processed_path("sources.csv"),
        processed_path("quality_summary.csv"),
        processed_path("districts.csv"),
    ]
    return all(p.exists() for p in required)


def load_indicators() -> pd.DataFrame:
    try:
        df = pd.read_csv(processed_path("indicators.csv"))
        for col in ["year", "province_code", "district_code", "value_pct", "n_unweighted"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def load_indicator_catalog() -> pd.DataFrame:
    try:
        return pd.read_csv(processed_path("indicator_catalog.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_sources() -> pd.DataFrame:
    try:
        return pd.read_csv(processed_path("sources.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_quality_summary() -> pd.DataFrame:
    try:
        return pd.read_csv(processed_path("quality_summary.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_districts() -> pd.DataFrame:
    try:
        df = pd.read_csv(processed_path("districts.csv"))
        for col in ["district_code", "province_code"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def load_all() -> dict[str, pd.DataFrame]:
    return {
        "indicators": load_indicators(),
        "catalog": load_indicator_catalog(),
        "sources": load_sources(),
        "quality": load_quality_summary(),
        "districts": load_districts(),
    }
