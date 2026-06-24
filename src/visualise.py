"""
visualise.py
Produces four publication-quality figures:
  Fig 1 - Return period curves for all stations
  Fig 2 - GEV shape parameter (xi) map across Nepal
  Fig 3 - 100-year return level comparison bar chart
  Fig 4 - Interactive Folium map of return levels
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import geopandas as gpd
import folium
from scipy.stats import genextreme

warnings.filterwarnings("ignore")

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), "..", "outputs", "results")
FIGURES_DIR   = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Consistent colour palette per station
STATION_COLORS = {
    "Pokhara":      "#e63946",
    "Simara":       "#f4a261",
    "Bhairahawa":   "#e9c46a",
    "Dadeldhura":   "#2a9d8f",
    "Okhaldhunga":  "#457b9d",
    "Biratnagar":   "#1d3557",
    "Dhankuta":     "#8ecae6",
    "Kathmandu":    "#023047",
    "Taplejung":    "#9b2226",
    "Surkhet":      "#6a994e",
    "Jumla":        "#a7c957",
}

RETURN_PERIODS = [2, 5, 10, 25, 50, 100, 200]


# ── Figure 1: Return Period Curves ──────────────────────────────────────────

def plot_return_curves(gev_df, annual_df):
    fig, ax = plt.subplots(figsize=(13, 7))
    T_range = np.logspace(np.log10(1.5), np.log10(500), 200)

    for _, row in gev_df.iterrows():
        name   = row["station"]
        c      = row["gev_xi"]
        loc    = row["gev_mu"]
        scale  = row["gev_sigma"]
        color  = STATION_COLORS.get(name, "#888888")

        # Fitted GEV curve
        rl = []
        for T in T_range:
            p = 1 - 1/T
            if abs(c) < 1e-6:
                rl.append(loc - scale * np.log(-np.log(p)))
            else:
                rl.append(loc - scale/c * (1 - (-np.log(p))**(-c)))
        ax.plot(T_range, rl, color=color, lw=2, label=name)

        # Empirical points (Gringorten plotting position)
        obs = annual_df[annual_df["STATION_NAME"] == name]["ANN_MAX_PRCP_MM"].sort_values().values
        n   = len(obs)
        i   = np.arange(1, n+1)
        F   = (i - 0.44) / (n + 0.12)
        T_emp = 1 / (1 - F)
        ax.scatter(T_emp, obs, color=color, s=18, alpha=0.5, zorder=5)

    ax.set_xscale("log")
    ax.set_xlabel("Return Period (years)", fontsize=13)
    ax.set_ylabel("Annual Maximum Daily Rainfall (mm)", fontsize=13)
    ax.set_title("GEV Return Period Curves — Nepal Rainfall Stations (1990–2023)",
                 fontsize=14, fontweight="bold")
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.set_xticks([2, 5, 10, 25, 50, 100, 200, 500])
    ax.grid(True, which="both", alpha=0.3, linestyle="--")
    ax.legend(loc="upper left", fontsize=9, ncol=2, framealpha=0.9)

    out = os.path.join(FIGURES_DIR, "fig1_return_period_curves.png")
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Fig 1 saved → {out}")


# ── Figure 2: GEV Shape Parameter Bar Chart ─────────────────────────────────

def plot_shape_params(gev_df):
    df = gev_df.sort_values("gev_xi", ascending=False)
    colors = ["#e63946" if x > 0.05 else "#457b9d" if x < -0.05 else "#f4a261"
              for x in df["gev_xi"]]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.barh(df["station"], df["gev_xi"], color=colors, edgecolor="white", height=0.6)
    ax.axvline(0, color="black", lw=1.2, linestyle="--")
    ax.axvline(-0.05, color="grey", lw=0.8, linestyle=":", alpha=0.6)
    ax.axvline(0.05,  color="grey", lw=0.8, linestyle=":", alpha=0.6)

    for bar, val in zip(bars, df["gev_xi"]):
        ax.text(val + (0.005 if val >= 0 else -0.005),
                bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center",
                ha="left" if val >= 0 else "right", fontsize=9)

    ax.set_xlabel("GEV Shape Parameter ξ (xi)", fontsize=12)
    ax.set_title("GEV Shape Parameter by Station\n"
                 "Red=Fréchet (heavy tail)  |  Blue=Weibull (bounded)  |  Orange=Gumbel",
                 fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    out = os.path.join(FIGURES_DIR, "fig2_gev_shape_params.png")
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Fig 2 saved → {out}")


# ── Figure 3: 100-Year Return Level Bar Chart with CI ───────────────────────

def plot_100yr_levels(gev_df):
    df = gev_df.sort_values("RL_100yr", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(df))
    colors = [STATION_COLORS.get(s, "#888") for s in df["station"]]

    ax.barh(y, df["RL_100yr"], color=colors, edgecolor="white", height=0.6, alpha=0.85)

    # 95% CI error bars
    xerr_lo = df["RL_100yr"] - df["RL_100yr_lo95"]
    xerr_hi = df["RL_100yr_hi95"] - df["RL_100yr"]
    ax.errorbar(df["RL_100yr"], y,
                xerr=[xerr_lo, xerr_hi],
                fmt="none", color="black", capsize=4, lw=1.5)

    ax.set_yticks(y)
    ax.set_yticklabels(df["station"], fontsize=11)
    ax.set_xlabel("100-Year Return Level (mm/day)", fontsize=12)
    ax.set_title("Estimated 100-Year Daily Rainfall Return Levels\n"
                 "Nepal Stations — GEV Fit with 95% Bootstrap CI",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Value labels
    for i, (val, lo, hi) in enumerate(zip(df["RL_100yr"], df["RL_100yr_lo95"], df["RL_100yr_hi95"])):
        ax.text(val + 5, i, f"{val:.0f}mm", va="center", fontsize=9)

    out = os.path.join(FIGURES_DIR, "fig3_100yr_return_levels.png")
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Fig 3 saved → {out}")


# ── Figure 4: Interactive Folium Map ────────────────────────────────────────

def plot_folium_map(gev_df):
    m = folium.Map(location=[28.0, 84.0], zoom_start=7,
                   tiles="CartoDB positron")

    # Colour scale by 100-yr return level
    min_rl = gev_df["RL_100yr"].min()
    max_rl = gev_df["RL_100yr"].max()

    def rl_to_color(rl):
        norm = (rl - min_rl) / (max_rl - min_rl)
        r = int(255 * norm)
        b = int(255 * (1 - norm))
        return f"#{r:02x}33{b:02x}"

    for _, row in gev_df.iterrows():
        color = rl_to_color(row["RL_100yr"])
        popup_html = f"""
        <b>{row['station']}</b><br>
        Lat: {row.get('LATITUDE', 'N/A')}<br>
        <hr>
        <b>GEV Parameters</b><br>
        ξ (shape): {row['gev_xi']}<br>
        μ (location): {row['gev_mu']}mm<br>
        σ (scale): {row['gev_sigma']}mm<br>
        Type: {row['gev_type']}<br>
        <hr>
        <b>Return Levels (mm/day)</b><br>
        10-yr:  {row['RL_10yr']}mm<br>
        25-yr:  {row['RL_25yr']}mm<br>
        50-yr:  {row['RL_50yr']}mm<br>
        100-yr: {row['RL_100yr']}mm<br>
        """
        # Get lat/lon from annual_maxima
        lat = gev_df[gev_df["station"] == row["station"]].get("LATITUDE", pd.Series([28.0])).values[0]
        lon = gev_df[gev_df["station"] == row["station"]].get("LONGITUDE", pd.Series([84.0])).values[0]

        folium.CircleMarker(
            location=[lat, lon],
            radius=12 + (row["RL_100yr"] / max_rl) * 20,
            color="black",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row['station']}: {row['RL_100yr']}mm (100yr)"
        ).add_to(m)

    out = os.path.join(FIGURES_DIR, "fig4_nepal_rainfall_map.html")
    m.save(out)
    print(f"  ✓ Fig 4 saved → {out}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    gev_df    = pd.read_csv(os.path.join(RESULTS_DIR, "gev_results.csv"))
    annual_df = pd.read_csv(os.path.join(PROCESSED_DIR, "annual_maxima.csv"))

    # Merge lat/lon into gev_df for map
    meta = annual_df.groupby("STATION_NAME")[["LATITUDE", "LONGITUDE"]].first().reset_index()
    meta = meta.rename(columns={"STATION_NAME": "station"})
    gev_df = gev_df.merge(meta, on="station", how="left")

    print("Generating figures...\n")
    plot_return_curves(gev_df, annual_df)
    plot_shape_params(gev_df)
    plot_100yr_levels(gev_df)
    plot_folium_map(gev_df)

    print(f"\n✓ ALL FIGURES SAVED → {FIGURES_DIR}")
    print(f"  fig1_return_period_curves.png — GEV curves + empirical points")
    print(f"  fig2_gev_shape_params.png     — Shape parameter by station")
    print(f"  fig3_100yr_return_levels.png  — 100yr levels with 95% CI")
    print(f"  fig4_nepal_rainfall_map.html  — Interactive map (open in browser)")


if __name__ == "__main__":
    main()