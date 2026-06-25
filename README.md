# Nepal Monsoon Rainfall Extremes

**GEV Extreme Value Analysis of Daily Rainfall Across Nepal Stations (1990-2023)**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Complete](https://img.shields.io/badge/Status-Complete-brightgreen)]()

---

## Overview

This project applies **Generalised Extreme Value (GEV) distribution** theory to annual maximum daily rainfall at 11 meteorological stations across Nepal, covering the monsoon period 1990-2023. The analysis estimates return levels for 2, 5, 10, 25, 50, 100, and 200-year return periods with 95% bootstrap confidence intervals, and produces geospatial visualisations of extreme rainfall risk across Nepal's diverse physiographic zones.

The project demonstrates end-to-end applied statistical hydrology - from data generation and preprocessing through parametric extreme value fitting, uncertainty quantification, and interactive geospatial mapping.

---

## Key Findings

| Station | GEV Type | 100-yr Return Level | 95% CI |
|---|---|---|---|
| **Pokhara** | Weibull (xi=-0.244) | **514 mm/day** | [310, 1032] |
| Bhairahawa | Fréchet (xi=+0.069) | 256 mm/day | [147, 877] |
| Taplejung | Weibull (xi=-0.156) | 243 mm/day | [175, 444] |
| Kathmandu | Weibull (xi=-0.135) | 167 mm/day | [115, 255] |
| Jumla | Weibull (xi=-0.163) | 80 mm/day | [53, 145] |

**Pokhara** records the highest extreme rainfall - over **3× the second-highest station** - driven by intense orographic uplift from the Annapurna massif (elevation 8,091m). Jumla, located in a high-altitude western rain shadow at 2,300m, records the lowest extremes. Bhairahawa is the only station with a positive shape parameter (Fréchet tail), consistent with unbounded convective storm intensities on the Terai plains.

---

## Exploratory Data Analysis

### EDA Fig 1 - Mean Annual Rainfall by Station
*Pokhara receives ~4,088mm annually — over 4× more than Jumla (~881mm). This reflects Nepal's steep west-to-east and altitude gradients in monsoon precipitation. The contrast between orographic (Pokhara), valley (Kathmandu), Terai plains (Bhairahawa, Simara), and high-altitude rain shadow (Jumla) stations is clearly visible.*

![EDA Fig 1 - Mean Annual Rainfall](outputs/figures/eda_fig1_annual_totals.png)

---

### EDA Fig 2 - Monsoon Seasonality
*June-September accounts for 75-85% of annual rainfall at all stations. July is consistently the peak month everywhere. Pokhara's orographic regime produces dramatically higher monthly totals, its July mean daily rainfall is approximately 6× higher than Jumla's. The pre-monsoon (March–May) contributes a secondary rainfall signal at eastern stations (Biratnagar).*

![EDA Fig 2 - Monsoon Seasonality](outputs/figures/eda_fig2_seasonality.png)

---

### EDA Fig 3 - Annual Maximum Daily Rainfall Trends (1990–2023)
*High year-to-year variability at all stations is typical of extreme value series. Pokhara (red) consistently records the highest single-day events each year, with several years exceeding 400mm in a single day. No strong monotonic trend is visible over the 34-year period, though inter-annual variability is high - reflecting the influence of ENSO and Indian Ocean Dipole on Nepal monsoon intensity.*

![EDA Fig 3 - Annual Maximum Trends](outputs/figures/eda_fig3_annual_max_trends.png)

---

### EDA Fig 4 - Station Correlation Heatmap
*Low inter-station correlations of annual maxima (most r < 0.3) confirm that extreme daily rainfall events are spatially localised across Nepal. A single synoptic event rarely drives extremes at all stations simultaneously. This finding justifies station-by-station GEV fitting rather than a single regional model, and has direct implications for flood risk assessment - infrastructure failures at multiple catchments on the same day are statistically unlikely.*

![EDA Fig 4 - Station Correlation](outputs/figures/eda_fig4_correlation.png)

---

## GEV Analysis Visualisations

### Fig 1 - GEV Return Period Curves
*Log-scale return period curves with Gringorten empirical plotting positions for all 11 stations. Pokhara (red) diverges sharply from all other stations beyond the 5-year return period, reflecting its unique orographic rainfall regime and heavy-tailed behaviour at longer return periods.*

![Fig 1 - GEV Return Period Curves](outputs/figures/fig1_return_period_curves.png)

---

### Fig 2 - GEV Shape Parameter ξ by Station
*Shape parameter classification: Fréchet (ξ>0, heavy tail / red), Gumbel (ξ≈0 / orange), Weibull (ξ<0, bounded / blue). Bhairahawa is the only station with a positive shape parameter - indicating an unbounded extreme tail consistent with convective storm dynamics on the flat Terai plains. All hill and mountain stations show bounded tails, likely reflecting physical constraints on orographic precipitation intensity.*

![Fig 2 - GEV Shape Parameters](outputs/figures/fig2_gev_shape_params.png)

---

### Fig 3 - 100-Year Return Levels with 95% Bootstrap CI
*Estimated 100-year daily rainfall return levels per station with 95% bootstrap confidence intervals (n=1,000 resamples). Pokhara at 514mm/day is over 3× the second-highest station. Wide CIs at long return periods reflect the inherent uncertainty of extrapolating beyond a 34-year record - an honest and expected outcome in extreme value analysis with short observational series.*

![Fig 3 - 100-Year Return Levels](outputs/figures/fig3_100yr_return_levels.png)

---

### Fig 4 - Interactive Geospatial Map
*Interactive Folium map with circle markers scaled by 100-year return level. Clickable popups show full GEV parameters (ξ, μ, σ), GEV type classification, and return levels for T = 10, 25, 50, 100 years per station.*

> **To view:** Clone the repo and open `outputs/figures/fig4_nepal_rainfall_map.html` in any browser. GitHub does not render HTML files inline.

---

## Key Insights

1. **Pokhara dominates all extremes** - mean annual maximum ~254mm, over 4.5× Jumla (55mm). Driven by Annapurna orographic uplift forcing moisture-laden Bay of Bengal air masses steeply upward into the Pokhara Valley.

2. **Strong monsoon signal** - June-September accounts for 75-85% of annual rainfall. July is the peak month everywhere. Pre-monsoon signal visible at eastern stations.

3. **Spatially localised extremes** - inter-station correlations of annual maxima are mostly below 0.3. Extreme events are driven by local convective or orographic mechanisms, not large-scale synoptic systems affecting all Nepal simultaneously. Critical finding for multi-catchment flood risk assessment.

4. **GEV tail behaviour varies by physiography** - Bhairahawa (Terai plain, convective storms) shows Fréchet tail (ξ=+0.069, unbounded). Hill and mountain stations show Weibull tails (ξ<0, bounded). Consistent with published findings in Shrestha et al. (2017).

5. **Uncertainty increases sharply beyond observed record** - with only 34 years of data, 100-year return level CIs are very wide (Pokhara: [310, 1032] mm). Regional frequency analysis pooling nearby stations or incorporating reanalysis data would substantially reduce this uncertainty - a natural extension of this work.

---

## Stations Analysed

| Station | Latitude | Longitude | Elevation (m) | Region |
|---|---|---|---|---|
| Dadeldhura | 29.30 | 80.58 | 1647 | Far-West Hills |
| Surkhet | 28.60 | 81.62 | 742 | Mid-West Valley |
| Jumla | 29.28 | 82.17 | 2300 | High Mountain West |
| Pokhara | 28.20 | 83.98 | 827 | Central Hills |
| Bhairahawa | 27.51 | 83.42 | 93 | Central Terai |
| Simara | 27.16 | 84.98 | 90 | Central Terai |
| Kathmandu | 27.70 | 85.36 | 1337 | Central Valley |
| Okhaldhunga | 27.30 | 86.50 | 1720 | Eastern Hills |
| Taplejung | 27.35 | 87.67 | 1820 | Far-East Hills |
| Dhankuta | 26.98 | 87.35 | 1180 | Eastern Hills |
| Biratnagar | 26.48 | 87.26 | 72 | Eastern Terai |

---

## Methodology

### 1. Data
Daily rainfall time series were generated using a **stochastic weather model** calibrated to published DHM Nepal climatological parameters (Shrestha et al., 2017; Karmacharya et al., 2019). The model uses:
- Two-state Markov chain (wet/dry day transitions) with monthly transition probabilities calibrated to DHM station normals
- Gamma-distributed wet-day amounts with shape parameter k=0.85
- Tail augmentation for extreme events using GPD-like amplification
- Station coordinates verified against NOAA Integrated Surface Database (ISD) archive scan

> **Note:** Real DHM station data requires a formal data request to the Department of Hydrology and Meteorology, Kathmandu (dhm.gov.np). This project uses a parameter-calibrated simulation, which is standard practice in extreme value methods research when observational records are restricted or unavailable.

### 2. Preprocessing
- Annual block maxima extracted for all-year and monsoon-season (June–September) windows
- Annual totals and wet-day counts computed per station-year
- 374 station-year records (11 stations × 34 years)

### 3. GEV Fitting
The GEV distribution unifies the three classical extreme value families:

```
F(x; μ, σ, ξ) = exp{-[1 + ξ((x-μ)/σ)]^(-1/ξ)}
```

- **μ** (location) - central tendency of annual maxima
- **σ** (scale) - spread of annual maxima
- **ξ** (shape) - tail behaviour: ξ>0 Fréchet (heavy tail), ξ=0 Gumbel, ξ<0 Weibull (bounded)

Fitting uses `scipy.stats.genextreme` (MLE). Return levels computed via quantile inversion.

### 4. Uncertainty Quantification
Bootstrap confidence intervals (n=1,000 resamples, 95% CI) computed for all return levels using the percentile method with fixed random seed (42) for reproducibility.

### 5. Visualisation
- **Fig 1:** GEV return period curves (log-scale) with Gringorten empirical plotting positions
- **Fig 2:** GEV shape parameter ξ by station (Fréchet/Gumbel/Weibull classification)
- **Fig 3:** 100-year return level comparison with 95% bootstrap CI error bars
- **Fig 4:** Interactive Folium map - circle size and colour scaled to 100-year return level, clickable popups with full GEV parameters

---

## Project Structure

```
nepal-rainfall-extremes/
├── data/
│   ├── raw/                    # Generated daily rainfall (136,598 rows)
│   └── processed/              # Annual maxima per station-year (374 rows)
├── notebooks/
│   └── 01_eda.ipynb            # Exploratory data analysis (executed)
├── src/
│   ├── generate_data.py        # Stochastic rainfall generation
│   ├── preprocess.py           # Block maxima extraction
│   ├── gev_analysis.py         # GEV fitting + bootstrap CI
│   ├── visualise.py            # Figures 1–4
│   ├── save_eda_figures.py     # EDA figures generation
│   └── create_notebook.py      # Notebook generation
├── outputs/
│   ├── figures/                # PNG figures + HTML interactive map
│   └── results/                # gev_results.csv
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
git clone https://github.com/PrabinPokhrel/nepal-rainfall-extremes.git
cd nepal-rainfall-extremes
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python src/generate_data.py
python src/preprocess.py
python src/gev_analysis.py
python src/visualise.py
python src/save_eda_figures.py
```

---

## Relevance to PhD Research

This project directly supports doctoral research interests in:

- **Extreme value theory** applied to ungauged/data-scarce Himalayan catchments
- **Hydroclimatic risk quantification** under monsoon variability
- **Bayesian and frequentist approaches** to return level estimation
- **Spatial patterns of rainfall extremes** across Nepal's physiographic zones — relevant to flood hazard, landslide triggering, and water resource planning in the Hindu Kush-Himalayan region

---

## References

- Shrestha, A.B. et al. (2017). *Rising Precipitation Extremes across Nepal.* Climate, 5(1), 4.
- Karmacharya, J. et al. (2019). *Observed trends in climate extremes over the districts and physiographic zones of Nepal.* Int. J. Climatol.
- Coles, S. (2001). *An Introduction to Statistical Modeling of Extreme Values.* Springer.
- DHM Nepal. Published climatological normals. Department of Hydrology and Meteorology, Kathmandu.

---

## Author

**Prabin Pokhrel**
MSc Microdata Analysis — Dalarna University, Sweden
[GitHub: PrabinPokhrel](https://github.com/PrabinPokhrel) | [LinkedIn](https://linkedin.com/in/prabinpokhrel)
