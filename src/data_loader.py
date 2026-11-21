import os
from datetime import date
import eurostat

os.makedirs("data/raw", exist_ok=True)

COUNTRIES = ["PL", "FR", "FI"]

DATASETS = {
    "price_to_income": "tipsho60",
    "youth_unemp": "tipslm80",
    "gini": "ilc_di12",
}

download_date = date.today().isoformat()
log_lines = [f"Download date: {download_date}", f"Countries: {', '.join(COUNTRIES)}", ""]

for name, code in DATASETS.items():
    df = eurostat.get_data_df(code)

    geo_col = [c for c in df.columns if c.startswith("geo")][0]
    df_raw = df[df[geo_col].isin(COUNTRIES)].copy()

    out_path = f"data/raw/{name}_{code}_raw.csv"
    df_raw.to_csv(out_path, index=False)

    year_cols = sorted([c for c in df_raw.columns if str(c).strip().isdigit()])
    meta_cols = [c for c in df_raw.columns if c not in year_cols and c != geo_col]

    summary = [
        f"=== {name} ({code}) ===",
        f"File: {out_path}",
        f"Rows per country: {df_raw.groupby(geo_col).size().to_dict()}",
        f"Year columns in raw table: {year_cols[0]}-{year_cols[-1]} ({len(year_cols)} years)",
        "Metadata columns:",
    ]
    for col in meta_cols:
        summary.append(f"  - {col}: {df_raw[col].unique().tolist()}")
    summary.append("")

    block = "\n".join(summary)
    print(block)
    log_lines.append(block)

with open("data/raw/download_log.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print("Raw data download completed. Log saved to data/raw/download_log.txt.")