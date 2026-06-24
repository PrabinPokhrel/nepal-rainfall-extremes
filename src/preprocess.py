"""
preprocess.py
Extracts annual maximum daily rainfall per station.
Filters monsoon season (June-September) and computes Block Maxima
for GEV fitting in the next step.
"""

import os
import pandas as pd
import numpy as np

RAW_PATH       = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "nepal_gsod_raw.csv")
PROCESSED_DIR  = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def load_raw(path):
    df = pd.read_csv(path, parse_dates=["DATE"])
    print(f"Loaded {len(df):,} rows from {path}")
    print(f"  Stations : {sorted(df['STATION_NAME'].unique())}")
    print(f"  Dates    : {df['DATE'].min().date()} to {df['DATE'].max().date()}")
    return df


def preprocess(df):
    # 1. Remove trace/missing values
    df = df[df["PRCP"] >= 0].copy()
    df["PRCP"] = pd.to_numeric(df["PRCP"], errors="coerce")
    df = df.dropna(subset=["PRCP"])

    # 2. Add time columns
    df["YEAR"]  = df["DATE"].dt.year
    df["MONTH"] = df["DATE"].dt.month

    # 3. Annual maximum daily rainfall (all year) — Block Maxima for GEV
    annual_max = (
        df.groupby(["STATION_NAME", "YEAR"])["PRCP"]
        .max()
        .reset_index()
        .rename(columns={"PRCP": "ANN_MAX_PRCP_MM"})
    )

    # 4. Monsoon season (June-September) annual maximum
    monsoon = df[df["MONTH"].isin([6, 7, 8, 9])].copy()
    monsoon_max = (
        monsoon.groupby(["STATION_NAME", "YEAR"])["PRCP"]
        .max()
        .reset_index()
        .rename(columns={"PRCP": "MONSOON_MAX_PRCP_MM"})
    )

    # 5. Annual total rainfall
    annual_total = (
        df.groupby(["STATION_NAME", "YEAR"])["PRCP"]
        .sum()
        .reset_index()
        .rename(columns={"PRCP": "ANN_TOTAL_PRCP_MM"})
    )

    # 6. Wet day count per year (PRCP > 1mm)
    wet_days = (
        df[df["PRCP"] > 1.0]
        .groupby(["STATION_NAME", "YEAR"])["PRCP"]
        .count()
        .reset_index()
        .rename(columns={"PRCP": "WET_DAYS"})
    )

    # 7. Merge all into one summary table
    summary = annual_max.copy()
    summary = summary.merge(monsoon_max,  on=["STATION_NAME", "YEAR"], how="left")
    summary = summary.merge(annual_total, on=["STATION_NAME", "YEAR"], how="left")
    summary = summary.merge(wet_days,     on=["STATION_NAME", "YEAR"], how="left")

    # 8. Add station metadata
    meta = (
        df.groupby("STATION_NAME")[["LATITUDE", "LONGITUDE", "ELEVATION"]]
        .first()
        .reset_index()
    )
    summary = summary.merge(meta, on="STATION_NAME", how="left")

    return summary


def print_summary(df):
    print(f"\n{'='*65}")
    print(f"ANNUAL MAXIMUM DAILY RAINFALL SUMMARY (mm)")
    print(f"{'='*65}")
    stats = (
        df.groupby("STATION_NAME")["ANN_MAX_PRCP_MM"]
        .agg(["mean", "std", "min", "max", "count"])
        .round(1)
    )
    stats.columns = ["Mean", "Std", "Min", "Max", "Years"]
    print(stats.to_string())
    print(f"{'='*65}")


def main():
    df_raw     = load_raw(RAW_PATH)
    df_summary = preprocess(df_raw)

    out_path = os.path.join(PROCESSED_DIR, "annual_maxima.csv")
    df_summary.to_csv(out_path, index=False)

    print_summary(df_summary)

    print(f"\n✓ Saved {len(df_summary):,} rows → {out_path}")
    print(f"  Columns : {list(df_summary.columns)}")


if __name__ == "__main__":
    main()