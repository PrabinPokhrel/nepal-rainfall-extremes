"""
save_eda_figures.py
Generates and saves 4 EDA figures to outputs/figures/
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

RAW_PATH       = "data/raw/nepal_gsod_raw.csv"
PROCESSED_PATH = "data/processed/annual_maxima.csv"
FIG_DIR        = "outputs/figures"

plt.rcParams["figure.dpi"] = 120
sns.set_style("whitegrid")

df      = pd.read_csv(RAW_PATH, parse_dates=["DATE"])
ann_max = pd.read_csv(PROCESSED_PATH)

# ── Fig 1: Mean annual rainfall ──────────────────────────────
annual = df.groupby(["STATION_NAME", df["DATE"].dt.year])["PRCP"].sum().reset_index()
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
plt.close()
print("✓ Saved eda_fig1_annual_totals.png")

# ── Fig 2: Monsoon seasonality ───────────────────────────────
df["MONTH"] = df["DATE"].dt.month
monthly = df.groupby(["STATION_NAME", "MONTH"])["PRCP"].mean().reset_index()
key_stations = ["Pokhara", "Kathmandu", "Biratnagar", "Jumla"]
month_names  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig, axes = plt.subplots(2, 2, figsize=(14, 8))
axes = axes.flatten()
for i, station in enumerate(key_stations):
    data  = monthly[monthly["STATION_NAME"] == station]
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
plt.close()
print("✓ Saved eda_fig2_seasonality.png")

# ── Fig 3: Annual maxima trends ──────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
for station in sorted(ann_max["STATION_NAME"].unique()):
    data  = ann_max[ann_max["STATION_NAME"] == station].sort_values("YEAR")
    color = "#e63946" if station == "Pokhara" else None
    lw    = 2.5 if station == "Pokhara" else 1.0
    alpha = 1.0 if station == "Pokhara" else 0.55
    ax.plot(data["YEAR"], data["ANN_MAX_PRCP_MM"],
            label=station, lw=lw, alpha=alpha, color=color)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Annual Maximum Daily Rainfall (mm)", fontsize=12)
ax.set_title("Annual Maximum Daily Rainfall - All Stations (1990-2023)",
             fontsize=13, fontweight="bold")
ax.legend(loc="upper left", fontsize=8, ncol=2)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_fig3_annual_max_trends.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Saved eda_fig3_annual_max_trends.png")

# ── Fig 4: Correlation heatmap ───────────────────────────────
pivot = ann_max.pivot(index="YEAR", columns="STATION_NAME", values="ANN_MAX_PRCP_MM")
corr  = pivot.corr()

fig, ax = plt.subplots(figsize=(11, 9))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlBu_r",
            center=0, vmin=-1, vmax=1, linewidths=0.5,
            ax=ax, annot_kws={"size": 9})
ax.set_title("Pearson Correlation of Annual Maximum Daily Rainfall Between Stations",
             fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_fig4_correlation.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ Saved eda_fig4_correlation.png")

print("\n✓ ALL EDA FIGURES SAVED")
print(f"  Location: {FIG_DIR}/")