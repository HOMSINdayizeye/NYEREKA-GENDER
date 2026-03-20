"""Build processed indicator tables from raw NYEREKA data sources."""
from __future__ import annotations

import datetime as dt
import zipfile
from pathlib import Path
from typing import Callable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "nyereka-gender-app"
RAW_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = APP_ROOT / "data" / "processed"
TMP_DIR = Path("/tmp/nyereka_gender_build")

PROVINCE_MAP = {
    1: "Kigali City",
    2: "Southern Province",
    3: "Western Province",
    4: "Northern Province",
    5: "Eastern Province",
}

DISTRICT_MAP = {
    11: "Nyarugenge",
    12: "Gasabo",
    13: "Kicukiro",
    21: "Nyanza",
    22: "Gisagara",
    23: "Nyaruguru",
    24: "Huye",
    25: "Nyamagabe",
    26: "Ruhango",
    27: "Muhanga",
    28: "Kamonyi",
    31: "Karongi",
    32: "Rutsiro",
    33: "Rubavu",
    34: "Nyabihu",
    35: "Ngororero",
    36: "Rusizi",
    37: "Nyamasheke",
    41: "Rulindo",
    42: "Gakenke",
    43: "Musanze",
    44: "Burera",
    45: "Gicumbi",
    51: "Rwamagana",
    52: "Nyagatare",
    53: "Gatsibo",
    54: "Kayonza",
    55: "Kirehe",
    56: "Ngoma",
    57: "Bugesera",
}

SOURCE_MAP = {
    "LFS2024": "https://microdata.statistics.gov.rw/index.php/catalog/114",
    "EICV7": "https://microdata.statistics.gov.rw/index.php/catalog/119",
    "PHC2022": "https://microdata.statistics.gov.rw/index.php/catalog/109",
    "DHS2019_20": "https://microdata.statistics.gov.rw/index.php/catalog/98",
    "FinScope2024": "https://microdata.statistics.gov.rw/index.php/catalog/120",
    "EC2023": "https://microdata.statistics.gov.rw/index.php/catalog/112",
}


def district_to_province(code: int | None) -> int | None:
    if code is None:
        return None
    return int(code) // 10


def weighted_pct(df: pd.DataFrame, positive: pd.Series, weight_col: str) -> float | None:
    if df.empty or weight_col not in df.columns:
        return None
    mask = positive.notna() & df[weight_col].notna()
    if not mask.any():
        return None
    weights = df.loc[mask, weight_col].astype(float)
    if weights.sum() == 0:
        return None
    values = positive.loc[mask].astype(float)
    return float((values * weights).sum() / weights.sum() * 100)


def add_record(
    records: list[dict],
    *,
    dataset_id: str,
    dataset_name: str,
    year: int,
    theme: str,
    indicator_id: str,
    indicator_name: str,
    sex: str,
    geo_level: str,
    province_code: int | None,
    district_code: int | None,
    value_pct: float | None,
    n_unweighted: int,
    weight_var: str,
    denominator_rule: str,
    caveat: str,
) -> None:
    if value_pct is None:
        return
    records.append(
        {
            "dataset_id": dataset_id,
            "dataset_name": dataset_name,
            "source_url": SOURCE_MAP[dataset_id],
            "year": year,
            "theme": theme,
            "indicator_id": indicator_id,
            "indicator_name": indicator_name,
            "sex": sex,
            "geo_level": geo_level,
            "province_code": province_code,
            "province_name": PROVINCE_MAP.get(province_code, "National" if geo_level == "national" else "Unknown"),
            "district_code": district_code,
            "district_name": DISTRICT_MAP.get(district_code, "National" if geo_level == "national" else "All districts"),
            "value_pct": round(value_pct, 3),
            "n_unweighted": int(n_unweighted),
            "weight_var": weight_var,
            "denominator_rule": denominator_rule,
            "caveat": caveat,
            "updated_at": dt.date.today().isoformat(),
        }
    )


def iter_geo_groups(df: pd.DataFrame, district_col: str, province_col: str):
    for (p, d), group in df.groupby([province_col, district_col], dropna=False):
        district_code = int(float(d)) if pd.notna(d) else None
        province_code = int(float(p)) if pd.notna(p) else district_to_province(district_code)
        yield "district", province_code, district_code, group

    for p, group in df.groupby(province_col, dropna=False):
        province_code = int(float(p)) if pd.notna(p) else None
        yield "province", province_code, None, group

    yield "national", None, None, df


def compute_binary_indicator(
    records: list[dict],
    *,
    df: pd.DataFrame,
    dataset_id: str,
    dataset_name: str,
    year: int,
    theme: str,
    indicator_id: str,
    indicator_name: str,
    weight_col: str,
    district_col: str,
    province_col: str,
    denominator: Callable[[pd.DataFrame], pd.Series],
    positive: Callable[[pd.DataFrame], pd.Series],
    sex_col: str | None = None,
    sex_map: dict[int, str] | None = None,
    caveat: str = "",
) -> None:
    if sex_col and sex_map:
        sex_items = list(sex_map.items())
    else:
        sex_items = [(None, "All")]

    for sex_code, sex_label in sex_items:
        sex_df = df if sex_code is None else df[df[sex_col] == sex_code]
        for geo_level, province_code, district_code, geo_df in iter_geo_groups(sex_df, district_col, province_col):
            den_mask = denominator(geo_df)
            den_df = geo_df[den_mask]
            if den_df.empty:
                continue
            value = weighted_pct(den_df, positive(den_df), weight_col)
            add_record(
                records,
                dataset_id=dataset_id,
                dataset_name=dataset_name,
                year=year,
                theme=theme,
                indicator_id=indicator_id,
                indicator_name=indicator_name,
                sex=sex_label,
                geo_level=geo_level,
                province_code=province_code,
                district_code=district_code,
                value_pct=value,
                n_unweighted=len(den_df),
                weight_var=weight_col,
                denominator_rule="valid denominator subset",
                caveat=caveat,
            )


def extract_from_zip(zip_name: str, member_name: str) -> Path:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TMP_DIR / Path(member_name).name
    if out_path.exists():
        return out_path
    zip_path = RAW_DIR / zip_name
    if not zip_path.exists():
        raise FileNotFoundError(f"Missing archive: {zip_path}")
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member_name) as src, open(out_path, "wb") as dst:
            dst.write(src.read())
    return out_path


def load_stata(path: Path, columns: list[str], encoding: str | None = None) -> pd.DataFrame:
    # pandas auto-falls back to latin-1 when needed for some Stata files.
    return pd.read_stata(path, columns=columns, convert_categoricals=False)


def build_lfs(records: list[dict]) -> None:
    path = RAW_DIR / "RW_LFS2024.dta"
    cols = ["province", "code_dis", "A01", "weight2", "status1", "C01"]
    df = load_stata(path, cols)
    df = df.rename(columns={"code_dis": "district", "province": "province"})

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="LFS2024",
        dataset_name="Rwanda Labour Force Survey 2024",
        year=2024,
        theme="Employment",
        indicator_id="lfs_unemployment_rate",
        indicator_name="Unemployment rate",
        weight_col="weight2",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["status1"].isin([1, 2]),
        positive=lambda x: x["status1"] == 2,
        sex_col="A01",
        sex_map={1: "Male", 2: "Female"},
        caveat="Based on labour-force denominator where status1 in {employed, unemployed}.",
    )

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="LFS2024",
        dataset_name="Rwanda Labour Force Survey 2024",
        year=2024,
        theme="Employment",
        indicator_id="lfs_wage_work_last7d",
        indicator_name="Worked for wage/salary in last 7 days",
        weight_col="weight2",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["C01"].isin([1, 2]),
        positive=lambda x: x["C01"] == 1,
        sex_col="A01",
        sex_map={1: "Male", 2: "Female"},
        caveat="Direct indicator from C01. Includes all ages present in survey rows.",
    )


def build_eicv(records: list[dict]) -> None:
    path = extract_from_zip("Microdata (2).zip", "Cross_Section/CS_S0_S1_S2_S3_S4_S6A_S6B_S6C_Person.dta")
    cols = ["province", "district", "s1q1", "weight", "s4aq7", "s6aq5", "s3q2"]
    df = load_stata(path, cols, encoding="latin1")

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="EICV7",
        dataset_name="EICV7 Cross-Section Person File",
        year=2024,
        theme="Education",
        indicator_id="eicv_school_attendance_12m",
        indicator_name="Attended school in the last 12 months",
        weight_col="weight",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["s4aq7"].isin([1, 2]),
        positive=lambda x: x["s4aq7"] == 1,
        sex_col="s1q1",
        sex_map={1: "Male", 2: "Female"},
        caveat="Education variable from EICV7 person module.",
    )

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="EICV7",
        dataset_name="EICV7 Cross-Section Person File",
        year=2024,
        theme="Employment",
        indicator_id="eicv_nonfarm_wage_work",
        indicator_name="Worked for salary/wages in non-farm sector",
        weight_col="weight",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["s6aq5"].isin([1, 2]),
        positive=lambda x: x["s6aq5"] == 1,
        sex_col="s1q1",
        sex_map={1: "Male", 2: "Female"},
        caveat="Employment variable from EICV7 labour module.",
    )

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="EICV7",
        dataset_name="EICV7 Cross-Section Person File",
        year=2024,
        theme="Health",
        indicator_id="eicv_health_insurance",
        indicator_name="Covered by health insurance",
        weight_col="weight",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["s3q2"].isin([1, 2]),
        positive=lambda x: x["s3q2"] == 1,
        sex_col="s1q1",
        sex_map={1: "Male", 2: "Female"},
        caveat="Insurance indicator from EICV7 social protection module.",
    )


def build_phc(records: list[dict]) -> None:
    path = extract_from_zip("PHC5_Public_microdata.zip", "PHC5_Public_microdata.dta")
    cols = ["ml01", "ml02", "p03", "Pop_weight", "p29", "p49", "p50a"]
    df = load_stata(path, cols, encoding="latin1")
    df = df.rename(columns={"ml01": "province", "ml02": "district"})

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="PHC2022",
        dataset_name="Population and Housing Census 2022",
        year=2022,
        theme="Education",
        indicator_id="phc_current_school_attendance",
        indicator_name="Currently attending school",
        weight_col="Pop_weight",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["p29"].isin([1, 2, 3]),
        positive=lambda x: x["p29"] == 2,
        sex_col="p03",
        sex_map={1: "Male", 2: "Female"},
        caveat="Excludes code 99 (not started).",
    )

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="PHC2022",
        dataset_name="Population and Housing Census 2022",
        year=2022,
        theme="Employment",
        indicator_id="phc_employee_status",
        indicator_name="Employee status in employment",
        weight_col="Pop_weight",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["p49"].isin([1, 2, 3, 4, 5, 6, 7]),
        positive=lambda x: x["p49"] == 1,
        sex_col="p03",
        sex_map={1: "Male", 2: "Female"},
        caveat="Employment status from PHC economic activity module.",
    )

    female_df = df[df["p03"] == 2]
    for geo_level, province_code, district_code, geo_df in iter_geo_groups(female_df, "district", "province"):
        den_df = geo_df[geo_df["p50a"].isin([1, 2])]
        if den_df.empty:
            continue
        val = weighted_pct(den_df, den_df["p50a"] == 1, "Pop_weight")
        add_record(
            records,
            dataset_id="PHC2022",
            dataset_name="Population and Housing Census 2022",
            year=2022,
            theme="Health",
            indicator_id="phc_women_ever_given_birth",
            indicator_name="Women ever given birth",
            sex="Female",
            geo_level=geo_level,
            province_code=province_code,
            district_code=district_code,
            value_pct=val,
            n_unweighted=len(den_df),
            weight_var="Pop_weight",
            denominator_rule="Female respondents with valid p50a",
            caveat="Includes women represented in census microdata sample.",
        )


def build_finscope(records: list[dict]) -> None:
    path = RAW_DIR / "FinScope 2024 Rwanda.dta"
    cols = ["a1", "a2", "b2", "pop_wt", "e2a", "e1", "e20_10", "qf4_05"]
    df = load_stata(path, cols)
    df = df.rename(columns={"a1": "province", "a2": "district"})

    female_df = df[df["b2"] == 2]
    for indicator_id, indicator_name, col, positive_set, theme, caveat in [
        (
            "finscope_women_own_money",
            "Women with own money",
            "e2a",
            {1},
            "Finance",
            "Indicator computed among female respondents only.",
        ),
        (
            "finscope_women_not_involved_decisions",
            "Women not involved in household money decisions",
            "e1",
            {4},
            "Leadership",
            "From household decision-making question e1.",
        ),
    ]:
        for geo_level, province_code, district_code, geo_df in iter_geo_groups(female_df, "district", "province"):
            den_df = geo_df[geo_df[col].notna()]
            if den_df.empty:
                continue
            val = weighted_pct(den_df, den_df[col].isin(positive_set), "pop_wt")
            add_record(
                records,
                dataset_id="FinScope2024",
                dataset_name="FinScope Rwanda 2024",
                year=2024,
                theme=theme,
                indicator_id=indicator_id,
                indicator_name=indicator_name,
                sex="Female",
                geo_level=geo_level,
                province_code=province_code,
                district_code=district_code,
                value_pct=val,
                n_unweighted=len(den_df),
                weight_var="pop_wt",
                denominator_rule=f"Respondents with valid {col}",
                caveat=caveat,
            )

    compute_binary_indicator(
        records,
        df=df,
        dataset_id="FinScope2024",
        dataset_name="FinScope Rwanda 2024",
        year=2024,
        theme="Finance",
        indicator_id="finscope_mobile_money_use",
        indicator_name="Currently use mobile money operator",
        weight_col="pop_wt",
        district_col="district",
        province_col="province",
        denominator=lambda x: x["qf4_05"].isin([1, 2]),
        positive=lambda x: x["qf4_05"] == 1,
        sex_col="b2",
        sex_map={1: "Male", 2: "Female"},
        caveat="Based on qf4_05 usage indicator.",
    )

    for geo_level, province_code, district_code, geo_df in iter_geo_groups(df, "district", "province"):
        den_df = geo_df[geo_df["e20_10"].isin([1, 2, 3, 4])]
        if den_df.empty:
            continue
        val = weighted_pct(den_df, den_df["e20_10"].isin([3, 4]), "pop_wt")
        add_record(
            records,
            dataset_id="FinScope2024",
            dataset_name="FinScope Rwanda 2024",
            year=2024,
            theme="Leadership",
            indicator_id="finscope_disagree_income_control_norm",
            indicator_name="Disagree women should hand income to male member",
            sex="All",
            geo_level=geo_level,
            province_code=province_code,
            district_code=district_code,
            value_pct=val,
            n_unweighted=len(den_df),
            weight_var="pop_wt",
            denominator_rule="Respondents with valid e20_10",
            caveat="Agreement/disagreement social norm indicator.",
        )


def build_ec(records: list[dict]) -> None:
    path = RAW_DIR / "data-rwa-nisr-ec-2023v2.dta"
    cols = ["q1_1", "q1_2", "q4_2", "q13", "Female_worker", "Total_workers"]
    df = pd.read_stata(path, columns=cols, convert_categoricals=False)
    df = df.rename(columns={"q1_1": "province", "q1_2": "district"})

    for geo_level, province_code, district_code, geo_df in iter_geo_groups(df, "district", "province"):
        valid_mgr = geo_df[geo_df["q4_2"].isin([1, 2])]
        if not valid_mgr.empty:
            val = (valid_mgr["q4_2"] == 2).mean() * 100
            add_record(
                records,
                dataset_id="EC2023",
                dataset_name="Establishment Census 2023",
                year=2023,
                theme="Leadership",
                indicator_id="ec_female_managed_establishments",
                indicator_name="Female-managed establishments",
                sex="All",
                geo_level=geo_level,
                province_code=province_code,
                district_code=district_code,
                value_pct=val,
                n_unweighted=len(valid_mgr),
                weight_var="unweighted",
                denominator_rule="Establishments with valid manager sex",
                caveat="Unweighted estimate from establishment records.",
            )

        worker_df = geo_df[(geo_df["Total_workers"] > 0) & geo_df["Female_worker"].notna()]
        if not worker_df.empty:
            val = float(worker_df["Female_worker"].sum() / worker_df["Total_workers"].sum() * 100)
            add_record(
                records,
                dataset_id="EC2023",
                dataset_name="Establishment Census 2023",
                year=2023,
                theme="Employment",
                indicator_id="ec_female_worker_share",
                indicator_name="Female share of establishment workers",
                sex="All",
                geo_level=geo_level,
                province_code=province_code,
                district_code=district_code,
                value_pct=val,
                n_unweighted=len(worker_df),
                weight_var="unweighted",
                denominator_rule="Total_workers > 0",
                caveat="Unweighted aggregate ratio from establishment workforce counts.",
            )

        valid_owner = geo_df[geo_df["q13"].isin([1, 2])]
        if not valid_owner.empty:
            val = (valid_owner["q13"] == 2).mean() * 100
            add_record(
                records,
                dataset_id="EC2023",
                dataset_name="Establishment Census 2023",
                year=2023,
                theme="Leadership",
                indicator_id="ec_female_owned_establishments",
                indicator_name="Female-owned establishments",
                sex="All",
                geo_level=geo_level,
                province_code=province_code,
                district_code=district_code,
                value_pct=val,
                n_unweighted=len(valid_owner),
                weight_var="unweighted",
                denominator_rule="Records with non-missing owner sex (q13)",
                caveat="Interpret carefully: owner sex has high missingness in raw data.",
            )


def build_dhs(records: list[dict]) -> None:
    path = extract_from_zip(
        "Microdata for Demographic and Health Survey 20219-2020 (2).zip",
        "Microdata/RWIR81FL.DTA",
    )
    cols = ["v024", "v005", "v155", "v170", "v481", "d005", "d104", "d106", "d108"]
    df = load_stata(path, cols)
    df = df.rename(columns={"v024": "province"})

    for indicator_id, indicator_name, col, positive_set, weight_col, theme, caveat in [
        (
            "dhs_women_bank_account",
            "Women with bank account",
            "v170",
            {1},
            "v005",
            "Finance",
            "Weighted with v005; province and national levels only.",
        ),
        (
            "dhs_women_health_insurance",
            "Women covered by health insurance",
            "v481",
            {1},
            "v005",
            "Health",
            "Weighted with v005; province and national levels only.",
        ),
        (
            "dhs_women_literacy",
            "Women literate (read part/whole sentence)",
            "v155",
            {1, 2},
            "v005",
            "Education",
            "Literacy indicator from v155 with valid response codes.",
        ),
        (
            "dhs_emotional_violence_partner",
            "Any emotional violence by partner",
            "d104",
            {1},
            "d005",
            "GBV",
            "Domestic violence module indicator; weighted with d005.",
        ),
        (
            "dhs_physical_violence_partner",
            "Any physical violence by partner",
            "d106",
            {1},
            "d005",
            "GBV",
            "Domestic violence module indicator; weighted with d005.",
        ),
        (
            "dhs_sexual_violence_partner",
            "Any sexual violence by partner",
            "d108",
            {1},
            "d005",
            "GBV",
            "Domestic violence module indicator; weighted with d005.",
        ),
    ]:
        for geo_level, province_code, _, geo_df in iter_geo_groups(df.assign(district=pd.NA), "district", "province"):
            if geo_level == "district":
                continue
            den_df = geo_df[geo_df[col].notna()]
            if den_df.empty:
                continue
            val = weighted_pct(den_df, den_df[col].isin(positive_set), weight_col)
            add_record(
                records,
                dataset_id="DHS2019_20",
                dataset_name="DHS 2019-2020 Individual Recode",
                year=2020,
                theme=theme,
                indicator_id=indicator_id,
                indicator_name=indicator_name,
                sex="Female",
                geo_level=geo_level,
                province_code=province_code,
                district_code=None,
                value_pct=val,
                n_unweighted=len(den_df),
                weight_var=weight_col,
                denominator_rule=f"Rows with non-missing {col}",
                caveat=caveat,
            )


def compute_quality(indicators: pd.DataFrame) -> pd.DataFrame:
    now_year = dt.date.today().year
    quality_rows = []
    for dataset_name, group in indicators.groupby("dataset_name"):
        year = int(group["year"].max())
        freshness = max(0, 100 - (now_year - year) * 15)
        coverage = 100 if "district" in set(group["geo_level"]) else 70
        weighted_share = (group["weight_var"] != "unweighted").mean() * 100
        score = round(0.4 * freshness + 0.3 * coverage + 0.3 * weighted_share, 1)
        badge = "High" if score >= 80 else "Medium" if score >= 60 else "Limited"
        quality_rows.append(
            {
                "dataset_name": dataset_name,
                "year": year,
                "quality_score": score,
                "quality_badge": badge,
                "freshness": round(freshness, 1),
                "coverage": round(coverage, 1),
                "weighted_methods": round(weighted_share, 1),
                "source_url": group["source_url"].iloc[0],
            }
        )
    return pd.DataFrame(quality_rows).sort_values("quality_score", ascending=False)


def build_sources_table(indicators: pd.DataFrame) -> pd.DataFrame:
    source = (
        indicators[["dataset_id", "dataset_name", "year", "source_url", "theme", "caveat"]]
        .drop_duplicates()
        .sort_values(["year", "dataset_name"], ascending=[False, True])
    )
    return source.rename(columns={"caveat": "notes"})


def build_indicator_catalog(indicators: pd.DataFrame) -> pd.DataFrame:
    return (
        indicators[
            [
                "indicator_id",
                "indicator_name",
                "theme",
                "dataset_name",
                "year",
                "weight_var",
                "denominator_rule",
                "caveat",
            ]
        ]
        .drop_duplicates()
        .sort_values(["theme", "indicator_name"])
    )


def build_district_table() -> pd.DataFrame:
    rows = []
    for code, name in DISTRICT_MAP.items():
        province_code = district_to_province(code)
        rows.append(
            {
                "district_code": code,
                "district_name": name,
                "province_code": province_code,
                "province_name": PROVINCE_MAP[province_code],
            }
        )
    return pd.DataFrame(rows).sort_values(["province_code", "district_code"])


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    builders = [build_lfs, build_eicv, build_phc, build_finscope, build_ec, build_dhs]
    for fn in builders:
        print(f"[build] {fn.__name__}")
        fn(records)

    indicators = pd.DataFrame(records).sort_values(
        ["theme", "indicator_name", "year", "geo_level", "province_code", "district_code", "sex"]
    )
    catalog = build_indicator_catalog(indicators)
    sources = build_sources_table(indicators)
    quality = compute_quality(indicators)
    districts = build_district_table()

    indicators.to_csv(PROCESSED_DIR / "indicators.csv", index=False)
    catalog.to_csv(PROCESSED_DIR / "indicator_catalog.csv", index=False)
    sources.to_csv(PROCESSED_DIR / "sources.csv", index=False)
    quality.to_csv(PROCESSED_DIR / "quality_summary.csv", index=False)
    districts.to_csv(PROCESSED_DIR / "districts.csv", index=False)

    print(f"Saved processed files to: {PROCESSED_DIR}")
    print(f"Indicators rows: {len(indicators)}")


if __name__ == "__main__":
    main()
