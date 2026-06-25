"""
create_notebook.py (v2)
Generates EDA notebook and saves all EDA figures to outputs/figures/
"""

import os

try:
    import nbformat as nbf
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "nbformat"], check=True)
    import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell("""# Nepal Monsoon Rainfall Extremes - Exploratory Data Analysis

**Project:** GEV Extreme Value Analysis of Daily Rainfall (1990-2023)
**Author:** Prabin Pokhrel
**Dataset:** 11 Nepal stations, 136,598 daily records, 34 years
"""))

cells.append(nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

RAW_PATH       = "../data/raw/nepal_gsod_raw.csv"
PROCESSED_PATH = "../data/processed/annual_maxima.csv"
FIG_DIR        = "../outputs/figures"
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams["figure.dpi"] = 120
sns.set_style("whitegrid")
print("Libraries loaded.")
"""))

cells.append(nbf.v4.new_markdown_cell("## 1. Dataset Overview"))

cells.append(nbf.v4.new_code_cell("""df = pd.read_csv(RAW_PATH, parse_dates=["DATE"])
print(f"Shape        : {df.shape}")
print(f"Stations     : {sorted(df['STATION_NAME'].unique())}")
print(f"Date range   : {df['DATE'].min().date()} to {df['DATE'].max().date()}")
print(f"Zero days    : {(df['PRCP'] == 0).sum():,}")
print(f"Wet days>1mm : {(df['PRCP'] > 1).sum():,}")
print(f"Wet fraction : {(df['PRCP'] > 1).mean():.2%}")
df.describe().round(2)
"""))

cells.append(nbf.v4.new_markdown_cell("## 2. Mean Annual Rainfall by Station\n\nPokhara receives ~4,088mm annually, over 4x more than Jumla (~881mm)."))

cells.append(nbf.v4.new_code_cell("""annual = df.groupby(["STATION_NAME", df["DATE"].dt.year])["PRCP"].sum().reset_index()
annual.columns = ["STATION_NAME", "YEAR", "ANNUAL_TOTAL_MM"]
mean_annual = annual.groupby("STATION_NAME")["ANNUAL_TOTAL_MM"].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 5))
colors = ["#e63946" if s == "Pokhara" else "#457b9d" for s in mean_annual.index]
bars = ax.bar(mean_annual.index, mean_annual.values, color=colors, edgecolor="white", width=0.6)
for bar, val in zip(bars, mean_annual.values):
    ax.text(bar.get_x() + bar.get_width()/2, val + 30, f"{val:.0f}",
            ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("Mean Annual Rainfall (mm)", fontsize=12)
ax.set_title("Mean Annual Rainfall by Station (1990-2023)", fontsize=13, fontweight="bold")
ax.tick_params(axis="x", rotation=30)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_fig1_annual_totals.png", dpi=150, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 3. Monsoon Seasonality\n\nJune-September accounts for 75-85% of annual rainfall. July is peak month everywhere."))

cells.append(nbf.v4.new_code_cell("""df["MONTH"] = df["DATE"].dt.month
monthly = df.groupby(["STATION_NAME", "MONTH"])["PRCP"].mean().reset_index()
key_stations = ["Pokhara", "Kathmandu", "Biratnagar", "Jumla"]
month_names  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
axes = axes.flatten()
for i, station in enumerate(key_stations):
    data = monthly[monthly["STATION_NAME"] == station]
    color = "#e63946" if station == "Pokhara" else "#457b9d"
    axes[i].bar(data["MONTH"], data["PRCP"], color=color, edgecolor="white", alpha=0.85)
    axes[i].set_title(station, fontsize=12, fontweight="bold")
    axes[i].set_xticks(range(1, 13))
    axes[i].set_xticklabels(month_names, fontsize=8)
    axes[i].set_ylabel("Mean Daily Rainfall (mm)")
    axes[i].axvspan(5.5, 9.5, alpha=0.08, color="blue", label="Monsoon (Jun-Sep)")
    axes[i].legend(fontsize=8)
fig.suptitle("Monthly Rainfall Distribution - Key Nepal Stations", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_fig2_seasonality.png", dpi=150, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 4. Annual Maximum Daily Rainfall Trends\n\nHigh year-to-year variability at all stations. Pokhara consistently records the highest single-day events."))

cells.append(nbf.v4.new_code_cell("""ann_max = pd.read_csv(PROCESSED_PATH)

fig, ax = plt.subplots(figsize=(14, 6))
for station in sorted(ann_max["STATION_NAME"].unique()):
    data = ann_max[ann_max["STATION_NAME"] == station].sort_values("YEAR")
    color = "#e63946" if station == "Pokhara" else None
    lw    = 2.5 if station == "Pokhara" else 1.0
    alpha = 1.0 if station == "Pokhara" else 0.55
    ax.plot(data["YEAR"], data["ANN_MAX_PRCP_MM"], label=station, lw=lw, alpha=alpha, color=color)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Annual Maximum Daily Rainfall (mm)", fontsize=12)
ax.set_title("Annual Maximum Daily Rainfall - All Stations (1990-2023)", fontsize=13, fontweight="bold")
ax.legend(loc="upper left", fontsize=8, ncol=2)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_fig3_annual_max_trends.png", dpi=150, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 5. Station Correlation\n\nLow inter-station correlations (r < 0.3) confirm extreme events are spatially localised."))

cells.append(nbf.v4.new_code_cell("""pivot = ann_max.pivot(index="YEAR", columns="STATION_NAME", values="ANN_MAX_PRCP_MM")
corr  = pivot.corr()

fig, ax = plt.subplots(figsize=(11, 9))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlBu_r",
            center=0, vmin=-1, vmax=1, linewidths=0.5, ax=ax, annot_kws={"size": 9})
ax.set_title("Pearson Correlation of Annual Maximum Daily Rainfall Between Stations",
             fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_fig4_correlation.png", dpi=150, bbox_inches="tight")
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 6. Summary Statistics"))

cells.append(nbf.v4.new_code_cell("""summary = ann_max.groupby("STATION_NAME")["ANN_MAX_PRCP_MM"].agg(
    Mean="mean", Std="std", Min="min", Median="median", Max="max", Years="count"
).round(1).sort_values("Mean", ascending=False)
print("Annual Maximum Daily Rainfall Statistics (mm)")
print("=" * 65)
print(summary.to_string())
print()
cv = (summary["Std"]/summary["Mean"])*100
print(f"Pokhara/Jumla ratio   : {summary.loc['Pokhara','Mean']/summary.loc['Jumla','Mean']:.1f}x")
print(f"Highest variability   : {cv.idxmax()} ({cv.max():.1f}% CV)")
print(f"Lowest variability    : {cv.idxmin()} ({cv.min():.1f}% CV)")
"""))

cells.append(nbf.v4.new_markdown_cell("""## 7. Key Insights

1. **Pokhara dominates all extremes** - mean annual maximum ~254mm, over 4.5x Jumla (55mm). Driven by Annapurna orographic uplift forcing moisture-laden Bay of Bengal air masses steeply upward.

2. **Strong monsoon signal** - June-September accounts for 75-85% of annual rainfall. July is the peak month everywhere.

3. **Spatially localised extremes** - inter-station correlations mostly below 0.3. Extreme events driven by local mechanisms, not synoptic systems affecting all Nepal simultaneously. Supports station-by-station GEV fitting.

4. **GEV tail behaviour varies by physiography** - Bhairahawa (Terai convective) shows Frechet tail (xi=+0.069, unbounded). Hill and mountain stations show Weibull tails (bounded). 

5. **Wide uncertainty at long return periods** - 34 years gives wide CIs for 100-year return levels. Regional frequency analysis pooling nearby stations would substantially reduce uncertainty.

---
*Next: See src/gev_analysis.py for GEV fitting and return period estimation.*
"""))

nb.cells = cells
out_path = os.path.join(os.path.dirname(__file__), "..", "notebooks", "01_eda.ipynb")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print(f"Notebook created: {out_path}")
