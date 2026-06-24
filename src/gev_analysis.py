"""
gev_analysis.py
Fits Generalised Extreme Value (GEV) distribution to annual maximum
daily rainfall at each Nepal station using scipy.stats.genextreme.
Estimates return levels for 10, 25, 50, 100 year return periods.
Bootstrap confidence intervals (n=1000) on all return level estimates.
"""

import os
import warnings
import numpy as np
import pandas as pd
from scipy.stats import genextreme
from scipy.optimize import OptimizeWarning

warnings.filterwarnings("ignore", category=OptimizeWarning)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
RESULTS_DIR   = os.path.join(os.path.dirname(__file__), "..", "outputs", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

RETURN_PERIODS = [2, 5, 10, 25, 50, 100, 200]
N_BOOTSTRAP    = 1000
RANDOM_SEED    = 42


def fit_gev(data):
    """
    Fit GEV distribution to annual maxima series.
    Returns (shape xi, loc mu, scale sigma).
    GEV parameterisation: Gumbel xi=0, Frechet xi>0, Weibull xi<0.
    """
    c, loc, scale = genextreme.fit(data, loc=np.mean(data), scale=np.std(data))
    return c, loc, scale


def return_level(c, loc, scale, T):
    """
    Compute return level x_T for return period T years.
    x_T = loc - scale/xi * (1 - (-log(1-1/T))^(-xi))  for xi != 0
    x_T = loc - scale * log(-log(1-1/T))               for xi = 0
    """
    p = 1.0 - 1.0 / T
    if abs(c) < 1e-6:
        return loc - scale * np.log(-np.log(p))
    else:
        return loc - scale / c * (1.0 - (-np.log(p)) ** (-c))


def bootstrap_ci(data, T, n_boot=N_BOOTSTRAP, ci=0.95, seed=RANDOM_SEED):
    """
    Bootstrap confidence interval for return level at period T.
    Returns (lower, upper) bounds.
    """
    rng = np.random.default_rng(seed)
    boot_levels = []
    n = len(data)
    for _ in range(n_boot):
        sample = rng.choice(data, size=n, replace=True)
        try:
            c, loc, scale = fit_gev(sample)
            rl = return_level(c, loc, scale, T)
            if np.isfinite(rl) and 0 < rl < 2000:
                boot_levels.append(rl)
        except Exception:
            continue
    alpha = (1 - ci) / 2
    return (
        np.percentile(boot_levels, alpha * 100),
        np.percentile(boot_levels, (1 - alpha) * 100)
    )


def analyse_station(station_name, data):
    """
    Full GEV analysis for one station.
    Returns dict of fitted parameters and return levels with CIs.
    """
    data = np.array(data, dtype=float)
    data = data[np.isfinite(data) & (data > 0)]

    if len(data) < 10:
        print(f"  {station_name}: insufficient data ({len(data)} years), skipping.")
        return None

    c, loc, scale = fit_gev(data)

    # GEV type
    if abs(c) < 0.05:
        gev_type = "Gumbel (xi≈0)"
    elif c > 0:
        gev_type = "Frechet (xi>0, heavy tail)"
    else:
        gev_type = "Weibull (xi<0, bounded)"

    result = {
        "station":    station_name,
        "n_years":    len(data),
        "obs_mean":   round(np.mean(data), 2),
        "obs_std":    round(np.std(data), 2),
        "obs_max":    round(np.max(data), 2),
        "gev_xi":     round(c, 4),
        "gev_mu":     round(loc, 4),
        "gev_sigma":  round(scale, 4),
        "gev_type":   gev_type,
    }

    print(f"\n  {station_name}")
    print(f"    GEV params : xi={c:.3f}, mu={loc:.1f}, sigma={scale:.1f}  [{gev_type}]")
    print(f"    Return levels (mm) with 95% CI:")

    for T in RETURN_PERIODS:
        rl = return_level(c, loc, scale, T)
        lo, hi = bootstrap_ci(data, T)
        result[f"RL_{T}yr"]      = round(rl, 1)
        result[f"RL_{T}yr_lo95"] = round(lo, 1)
        result[f"RL_{T}yr_hi95"] = round(hi, 1)
        print(f"      T={T:>3}yr : {rl:6.1f}mm  [{lo:.1f}, {hi:.1f}]")

    return result


def main():
    in_path = os.path.join(PROCESSED_DIR, "annual_maxima.csv")
    df = pd.read_csv(in_path)
    print(f"Loaded {len(df)} station-year records")
    print(f"Running GEV analysis with {N_BOOTSTRAP} bootstrap iterations...\n")
    print("="*65)

    results = []
    for station in sorted(df["STATION_NAME"].unique()):
        series = df[df["STATION_NAME"] == station]["ANN_MAX_PRCP_MM"].values
        res = analyse_station(station, series)
        if res:
            results.append(res)

    results_df = pd.DataFrame(results)

    out_path = os.path.join(RESULTS_DIR, "gev_results.csv")
    results_df.to_csv(out_path, index=False)

    print(f"\n{'='*65}")
    print(f"✓ GEV ANALYSIS COMPLETE")
    print(f"  Stations analysed : {len(results_df)}")
    print(f"  Return periods    : {RETURN_PERIODS}")
    print(f"  Bootstrap n       : {N_BOOTSTRAP}")
    print(f"  Results saved     : {out_path}")
    print(f"\n100-YEAR RETURN LEVELS (mm):")
    print(f"{'='*65}")
    for _, row in results_df.sort_values("RL_100yr", ascending=False).iterrows():
        print(f"  {row['station']:<15} {row['RL_100yr']:>7.1f}mm  "
              f"[{row['RL_100yr_lo95']:.1f}, {row['RL_100yr_hi95']:.1f}]")


if __name__ == "__main__":
    main()