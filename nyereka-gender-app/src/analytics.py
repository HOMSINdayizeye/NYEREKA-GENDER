"""Analytical helpers for NYEREKA indicator exploration and advocacy logic."""
from __future__ import annotations

import pandas as pd

INDICATOR_DIRECTION = {
    "lfs_unemployment_rate": "lower_better",
    "dhs_emotional_violence_partner": "lower_better",
    "dhs_physical_violence_partner": "lower_better",
    "dhs_sexual_violence_partner": "lower_better",
    "finscope_women_not_involved_decisions": "lower_better",
}


def direction_for(indicator_id: str) -> str:
    return INDICATOR_DIRECTION.get(indicator_id, "higher_better")


def gender_gap_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    pair = df[df["sex"].isin(["Male", "Female"])].copy()
    if pair.empty:
        return pd.DataFrame()

    group_cols = [
        "indicator_id",
        "indicator_name",
        "theme",
        "dataset_name",
        "year",
        "geo_level",
        "province_code",
        "province_name",
        "district_code",
        "district_name",
    ]

    piv = (
        pair.pivot_table(
            index=group_cols,
            columns="sex",
            values="value_pct",
            aggfunc="mean",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    # Ensure both columns exist (even if data is missing for one sex)
    for col in ["Female", "Male"]:
        if col not in piv.columns:
            piv[col] = pd.NA

    if "Female" in piv.columns and "Male" in piv.columns:
        piv["gap_f_minus_m"] = piv["Female"] - piv["Male"]
    else:
        piv["gap_f_minus_m"] = pd.NA

    piv["direction"] = piv["indicator_id"].map(direction_for)

    def priority_score(row: pd.Series) -> float:
        if pd.isna(row.get("gap_f_minus_m")):
            return 0.0
        gap = float(row["gap_f_minus_m"])
        if row["direction"] == "higher_better":
            return max(0.0, -gap)
        return max(0.0, gap)

    piv["priority_score"] = piv.apply(priority_score, axis=1)
    return piv


def top_advocacy_priorities(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    gaps = gender_gap_table(df)
    if gaps.empty:
        return gaps
    return gaps.sort_values(["priority_score", "year"], ascending=[False, False]).head(n)


def district_vs_national(indicators: pd.DataFrame, indicator_id: str, district_code: int, sex: str = "All") -> pd.DataFrame:
    subset = indicators[indicators["indicator_id"] == indicator_id].copy()
    if sex != "All":
        subset = subset[subset["sex"] == sex]

    district_row = subset[(subset["geo_level"] == "district") & (subset["district_code"] == district_code)]
    national_row = subset[subset["geo_level"] == "national"]

    rows = []
    if not district_row.empty:
        latest = district_row.sort_values("year", ascending=False).iloc[0]
        rows.append({"scope": "Selected district", "value_pct": latest["value_pct"], "year": int(latest["year"])})
    if not national_row.empty:
        latest = national_row.sort_values("year", ascending=False).iloc[0]
        rows.append({"scope": "National", "value_pct": latest["value_pct"], "year": int(latest["year"])})

    return pd.DataFrame(rows)
