import os
import pandas as pd

COUNTRIES = {"PL": "Polska", "FR": "Francja", "FI": "Finlandia"}

DATASETS = {
    "price_to_income": {
        "raw_file": "data/raw/price_to_income_tipsho60_raw.csv",
        "filters": {"unit": "PTIR_LT_AVG"},
    },
    "youth_unemp": {
        "raw_file": "data/raw/youth_unemp_tipslm80_raw.csv",
        "filters": {"unit": "PC_ACT"},
    },
    "gini": {
        "raw_file": "data/raw/gini_ilc_di12_raw.csv",
        "filters": {"age": "TOTAL"},
    },
}


def clean_dataset(raw_file: str, filters: dict) -> pd.DataFrame:
    df = pd.read_csv(raw_file)
    geo_col = [c for c in df.columns if c.startswith("geo")][0]

    for col, val in filters.items():
        if col in df.columns:
            df = df[df[col] == val]

    if df.groupby(geo_col).size().max() > 1:
        raise ValueError(f"More than 1 row per country remaining in {raw_file} after filtering.")

    year_cols = sorted([c for c in df.columns if str(c).strip().isdigit()])
    df_long = df.melt(
        id_vars=[geo_col],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )
    df_long["year"] = df_long["year"].astype(int)
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")
    df_long["country_code"] = df_long[geo_col]
    df_long["country"] = df_long[geo_col].map(COUNTRIES)

    return df_long[["year", "country_code", "country", "value"]]


def main():
    os.makedirs("data/clean", exist_ok=True)
    cleaned = {}

    for name, cfg in DATASETS.items():
        df = clean_dataset(cfg["raw_file"], cfg["filters"])
        valid_years = sorted(
            df.dropna(subset=["value"])
            .groupby("year")
            .filter(lambda g: len(g) == len(COUNTRIES))["year"]
            .unique()
        )
        print(f"[{name}] Complete years (no NaN for PL/FR/FI): {valid_years[0]}-{valid_years[-1]} ({len(valid_years)} years)")
        cleaned[name] = df.dropna(subset=["value"])

    common_years = sorted(
        set.intersection(*[
            set(
                df.groupby("year")
                .filter(lambda g: len(g) == len(COUNTRIES))["year"]
                .unique()
            )
            for df in cleaned.values()
        ])
    )

    start_yr, end_yr = common_years[0], common_years[-1]
    print(f"\nCommon complete year range: {start_yr}-{end_yr} ({len(common_years)} years)")

    merged = None
    for name, df in cleaned.items():
        df_cut = df[df["year"].isin(common_years)].sort_values(["country_code", "year"]).copy()
        out_path = f"data/clean/{name}_{start_yr}_{end_yr}.csv"
        df_cut.to_csv(out_path, index=False)
        print(f"Saved: {out_path} ({len(df_cut)} rows)")

        df_renamed = df_cut.rename(columns={"value": name})
        merged = df_renamed if merged is None else merged.merge(df_renamed, on=["year", "country_code", "country"])

    merged_path = f"data/clean/all_indicators_{start_yr}_{end_yr}.csv"
    merged.to_csv(merged_path, index=False)
    print(f"Saved merged dataset: {merged_path} ({len(merged)} rows)")


if __name__ == "__main__":
    main()