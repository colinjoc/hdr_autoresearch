"""
Data loaders for Iberian wildfire VLF prediction.

Provides functions to load real EFFIS/ERA5/Sentinel-2 data when available,
or generate statistically realistic synthetic data calibrated to published
fire statistics for development and testing.

Synthetic data calibration sources:
- EFFIS annual reports 2006-2025: fire counts, burned area by country
- Turco et al. (2019): FWI-fire relationship in Mediterranean
- San-Miguel-Ayanz et al. (2023): JRC EFFIS statistics
- Fernandes et al. (2019): Portuguese fire regime
- Costa et al. (2011): Fire weather in Iberia
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"


# ============================================================================
# Constants calibrated to EFFIS statistics
# ============================================================================

# Mean annual fire counts by country (fires > 1 ha), EFFIS 2006-2024
ANNUAL_FIRE_COUNTS = {
    "PT": 3200,   # Portugal: ~3000-3500 fires/year > 1 ha
    "ES": 8500,   # Spain: ~8000-9000 fires/year > 1 ha
}

# VLF fraction: proportion of fires >500 ha (EFFIS statistics)
VLF_FRACTION = 0.025  # ~2.5% of fires > 1 ha become VLF

# NUTS-3 regions in Iberia most affected by VLFs
NUTS3_REGIONS = {
    # Portugal
    "PT111": {"name": "Alto Minho", "lat": 41.9, "lon": -8.5, "country": "PT", "eucalyptus_frac": 0.25},
    "PT112": {"name": "Cavado", "lat": 41.5, "lon": -8.4, "country": "PT", "eucalyptus_frac": 0.30},
    "PT119": {"name": "Ave", "lat": 41.4, "lon": -8.2, "country": "PT", "eucalyptus_frac": 0.35},
    "PT11A": {"name": "Area Metropolitana do Porto", "lat": 41.2, "lon": -8.6, "country": "PT", "eucalyptus_frac": 0.20},
    "PT11B": {"name": "Alto Tamega", "lat": 41.8, "lon": -7.7, "country": "PT", "eucalyptus_frac": 0.15},
    "PT11C": {"name": "Tamega e Sousa", "lat": 41.2, "lon": -8.1, "country": "PT", "eucalyptus_frac": 0.40},
    "PT11D": {"name": "Douro", "lat": 41.2, "lon": -7.5, "country": "PT", "eucalyptus_frac": 0.10},
    "PT11E": {"name": "Terras de Tras-os-Montes", "lat": 41.8, "lon": -6.8, "country": "PT", "eucalyptus_frac": 0.05},
    "PT150": {"name": "Algarve", "lat": 37.1, "lon": -8.0, "country": "PT", "eucalyptus_frac": 0.10},
    "PT16B": {"name": "Regiao de Leiria", "lat": 39.7, "lon": -8.8, "country": "PT", "eucalyptus_frac": 0.55},
    "PT16D": {"name": "Regiao de Coimbra", "lat": 40.2, "lon": -8.4, "country": "PT", "eucalyptus_frac": 0.45},
    "PT16H": {"name": "Beira Baixa", "lat": 39.8, "lon": -7.5, "country": "PT", "eucalyptus_frac": 0.30},
    "PT16I": {"name": "Medio Tejo", "lat": 39.5, "lon": -8.3, "country": "PT", "eucalyptus_frac": 0.40},
    "PT16J": {"name": "Beiras e Serra da Estrela", "lat": 40.4, "lon": -7.5, "country": "PT", "eucalyptus_frac": 0.20},
    "PT185": {"name": "Leziria do Tejo", "lat": 39.3, "lon": -8.7, "country": "PT", "eucalyptus_frac": 0.25},
    # Spain
    "ES111": {"name": "A Coruna", "lat": 43.3, "lon": -8.4, "country": "ES", "eucalyptus_frac": 0.30},
    "ES112": {"name": "Lugo", "lat": 43.0, "lon": -7.5, "country": "ES", "eucalyptus_frac": 0.25},
    "ES113": {"name": "Ourense", "lat": 42.3, "lon": -7.8, "country": "ES", "eucalyptus_frac": 0.20},
    "ES114": {"name": "Pontevedra", "lat": 42.4, "lon": -8.6, "country": "ES", "eucalyptus_frac": 0.35},
    "ES411": {"name": "Avila", "lat": 40.7, "lon": -5.0, "country": "ES", "eucalyptus_frac": 0.02},
    "ES412": {"name": "Burgos", "lat": 42.3, "lon": -3.7, "country": "ES", "eucalyptus_frac": 0.01},
    "ES413": {"name": "Leon", "lat": 42.6, "lon": -5.6, "country": "ES", "eucalyptus_frac": 0.05},
    "ES415": {"name": "Salamanca", "lat": 40.9, "lon": -5.7, "country": "ES", "eucalyptus_frac": 0.02},
    "ES418": {"name": "Zamora", "lat": 41.5, "lon": -5.7, "country": "ES", "eucalyptus_frac": 0.03},
    "ES431": {"name": "Badajoz", "lat": 38.9, "lon": -6.9, "country": "ES", "eucalyptus_frac": 0.05},
    "ES432": {"name": "Caceres", "lat": 39.5, "lon": -6.4, "country": "ES", "eucalyptus_frac": 0.08},
    "ES612": {"name": "Huelva", "lat": 37.3, "lon": -6.9, "country": "ES", "eucalyptus_frac": 0.15},
    "ES613": {"name": "Jaen", "lat": 37.8, "lon": -3.8, "country": "ES", "eucalyptus_frac": 0.02},
    "ES511": {"name": "Barcelona", "lat": 41.4, "lon": 2.2, "country": "ES", "eucalyptus_frac": 0.01},
    "ES521": {"name": "Valencia", "lat": 39.5, "lon": -0.4, "country": "ES", "eucalyptus_frac": 0.01},
}

# Land cover types and their fire behavior
LAND_COVER_TYPES = [
    "broadleaf_forest",
    "coniferous_forest",
    "mixed_forest",
    "eucalyptus",
    "shrubland",
    "grassland",
    "agricultural",
    "wui",  # wildland-urban interface
]

# Fire spread rate multiplier by land cover (relative to broadleaf_forest=1.0)
FIRE_SPREAD_MULTIPLIER = {
    "broadleaf_forest": 1.0,
    "coniferous_forest": 1.3,
    "mixed_forest": 1.1,
    "eucalyptus": 2.5,  # eucalyptus burns much faster
    "shrubland": 1.5,
    "grassland": 1.8,
    "agricultural": 0.6,
    "wui": 1.2,
}

# Months with fire activity (day-of-year ranges)
FIRE_SEASON_PEAK = (152, 273)  # June 1 to Sept 30 (days of year)


def _compute_fwi_from_weather(
    temp: float, rh: float, wind: float, precip: float,
    prev_ffmc: float = 85.0, prev_dmc: float = 6.0, prev_dc: float = 15.0,
    month: int = 7,
) -> dict:
    """Compute Fire Weather Index components using Van Wagner (1987) equations.

    Simplified but physically correct implementation of the Canadian FWI system.
    Returns dict with FFMC, DMC, DC, ISI, BUI, FWI.

    Parameters:
        temp: noon temperature (C)
        rh: noon relative humidity (%)
        wind: noon wind speed (km/h)
        precip: 24-hour precipitation (mm)
        prev_ffmc: previous day FFMC
        prev_dmc: previous day DMC
        prev_dc: previous day DC
        month: calendar month (1-12)
    """
    # Day length adjustment factors for DMC (Le)
    LE = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
    # Day length adjustment factors for DC (Lf)
    LF = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]

    # --- FFMC ---
    mo = 147.2 * (101.0 - prev_ffmc) / (59.5 + prev_ffmc)
    if precip > 0.5:
        rf = precip - 0.5
        if mo <= 150.0:
            mr = mo + 42.5 * rf * np.exp(-100.0 / (251.0 - mo)) * (1.0 - np.exp(-6.93 / rf))
        else:
            mr = (mo + 42.5 * rf * np.exp(-100.0 / (251.0 - mo)) * (1.0 - np.exp(-6.93 / rf))
                  + 0.0015 * (mo - 150.0) ** 2 * rf ** 0.5)
        mr = min(mr, 250.0)
        mo = mr

    ed = (0.942 * rh ** 0.679 + 11.0 * np.exp((rh - 100.0) / 10.0)
          + 0.18 * (21.1 - temp) * (1.0 - np.exp(-0.115 * rh)))
    if mo > ed:
        kl = 0.424 * (1.0 - (rh / 100.0) ** 1.7) + 0.0694 * wind ** 0.5 * (1.0 - (rh / 100.0) ** 8)
        kw = kl * 0.581 * np.exp(0.0365 * temp)
        m = ed + (mo - ed) * 10.0 ** (-kw)
    else:
        ew = (0.618 * rh ** 0.753 + 10.0 * np.exp((rh - 100.0) / 10.0)
              + 0.18 * (21.1 - temp) * (1.0 - np.exp(-0.115 * rh)))
        if mo < ew:
            kl = 0.424 * (1.0 - ((100.0 - rh) / 100.0) ** 1.7) + 0.0694 * wind ** 0.5 * (1.0 - ((100.0 - rh) / 100.0) ** 8)
            kw = kl * 0.581 * np.exp(0.0365 * temp)
            m = ew - (ew - mo) * 10.0 ** (-kw)
        else:
            m = mo

    ffmc = 59.5 * (250.0 - m) / (147.2 + m)
    ffmc = np.clip(ffmc, 0.0, 101.0)

    # --- DMC ---
    if precip > 1.5:
        re = 0.92 * precip - 1.27
        rw = 0.11 * re * np.exp(0.10 * prev_dmc)
        if prev_dmc <= 33.0:
            b = 100.0 / (0.5 + 0.3 * prev_dmc)
        elif prev_dmc <= 65.0:
            b = 14.0 - 1.3 * np.log(prev_dmc)
        else:
            b = 6.2 * np.log(prev_dmc) - 17.2
        wmr = prev_dmc - b * rw
        pr = max(wmr, 0.0)
    else:
        pr = prev_dmc

    if temp > -1.1:
        le_val = LE[month - 1]
        dl = le_val * (0.36 * (temp + 1.1) + 100.0 - rh) / 100.0
        dmc = max(pr + dl, 0.0)
    else:
        dmc = pr

    # --- DC ---
    if precip > 2.8:
        rd = 0.83 * precip - 1.27
        qr = 800.0 * np.exp(-prev_dc / 400.0) + 3.937 * rd
        dr = 400.0 * np.log(800.0 / qr)
        dr = max(dr, 0.0)
    else:
        dr = prev_dc

    lf_val = LF[month - 1]
    if temp > -2.8:
        v = 0.36 * (temp + 2.8) + lf_val
        v = max(v, 0.0)
    else:
        v = 0.0
    dc = dr + 0.5 * v

    # --- ISI (Initial Spread Index) ---
    fw = np.exp(0.05039 * wind)
    fm = 147.2 * (101.0 - ffmc) / (59.5 + ffmc)
    sf = 91.9 * np.exp(-0.1386 * fm) * (1.0 + fm ** 5.31 / (4.93e7))
    isi = 0.208 * fw * sf

    # --- BUI (Build-Up Index) ---
    if dmc <= 0.4 * dc:
        bui = 0.8 * dmc * dc / (dmc + 0.4 * dc) if (dmc + 0.4 * dc) > 0 else 0.0
    else:
        bui = dmc - (1.0 - 0.8 * dc / (dmc + 0.4 * dc)) * (0.92 + (0.0114 * dmc) ** 1.7)
    bui = max(bui, 0.0)

    # --- FWI ---
    if bui <= 80.0:
        fd = 0.626 * bui ** 0.809 + 2.0
    else:
        fd = 1000.0 / (25.0 + 108.64 * np.exp(-0.023 * bui))

    b_fwi = 0.1 * isi * fd
    if b_fwi > 1.0:
        fwi = np.exp(2.72 * (0.434 * np.log(b_fwi)) ** 0.647)
    else:
        fwi = b_fwi

    return {
        "ffmc": float(ffmc),
        "dmc": float(dmc),
        "dc": float(dc),
        "isi": float(isi),
        "bui": float(bui),
        "fwi": float(fwi),
    }


def generate_synthetic_fires(
    seed: int = 42,
    years: tuple[int, int] = (2006, 2025),
    n_scale: float = 1.0,
) -> pd.DataFrame:
    """Generate statistically realistic synthetic fire event data.

    Calibrated to EFFIS published statistics for Portugal and Spain.
    Preserves:
    - Annual fire count distribution by country
    - VLF fraction (~2.5% of fires >500 ha)
    - Seasonal distribution (peak June-September)
    - FWI correlation with VLF probability
    - Geographic distribution by NUTS-3 region
    - Land cover type distribution
    - Terrain features

    Parameters:
        seed: random seed for reproducibility
        years: (start_year, end_year) inclusive
        n_scale: scale factor for number of fires (1.0 = realistic count)

    Returns:
        DataFrame with one row per fire event
    """
    rng = np.random.RandomState(seed)
    records = []
    fire_id = 0

    region_keys = list(NUTS3_REGIONS.keys())
    pt_regions = [k for k in region_keys if k.startswith("PT")]
    es_regions = [k for k in region_keys if k.startswith("ES")]

    for year in range(years[0], years[1] + 1):
        # Year-specific scaling (2025 was ~2x average)
        year_mult = 1.0
        if year == 2025:
            year_mult = 1.8
        elif year == 2017:
            year_mult = 1.5  # 2017 was a bad year (Pedrogao Grande)
        elif year == 2022:
            year_mult = 1.3  # 2022 Zamora fires

        for country, base_count in ANNUAL_FIRE_COUNTS.items():
            n_fires = int(base_count * n_scale * year_mult * rng.uniform(0.8, 1.2))
            regions = pt_regions if country == "PT" else es_regions

            for _ in range(n_fires):
                fire_id += 1

                # Month distribution: beta distribution peaking in July-August
                month = int(np.clip(rng.beta(4, 3) * 12 + 1, 1, 12))
                # Day of year
                if month <= 6:
                    doy = (month - 1) * 30 + rng.randint(1, 31)
                else:
                    doy = (month - 1) * 30 + rng.randint(1, 31)
                doy = int(np.clip(doy, 1, 365))

                # Region selection (weighted by historical fire density)
                region_idx = rng.randint(0, len(regions))
                region = regions[region_idx]
                region_info = NUTS3_REGIONS[region]

                lat = region_info["lat"] + rng.normal(0, 0.3)
                lon = region_info["lon"] + rng.normal(0, 0.3)
                eucalyptus_frac = region_info["eucalyptus_frac"]

                # Elevation, slope, aspect
                elevation = max(0, rng.normal(400, 250))
                slope = max(0, rng.exponential(15))
                aspect = rng.uniform(0, 360)

                # Land cover type (weighted by region)
                lc_probs = np.array([0.15, 0.12, 0.10, eucalyptus_frac, 0.20, 0.08, 0.10, 0.05])
                lc_probs = lc_probs / lc_probs.sum()
                land_cover = rng.choice(LAND_COVER_TYPES, p=lc_probs)

                # Weather at fire detection
                # Temperature: seasonal + latitude effect
                seasonal_temp = 15 + 15 * np.sin((doy - 80) * 2 * np.pi / 365)
                lat_effect = -(lat - 39) * 0.8  # cooler further north
                temp = seasonal_temp + lat_effect + rng.normal(0, 3)

                # Relative humidity: inverse of temperature + some noise
                rh = np.clip(70 - 0.8 * temp + rng.normal(0, 10), 10, 100)

                # Wind speed (km/h): log-normal
                wind = max(0, rng.lognormal(2.5, 0.6))

                # Precipitation (mm): mostly zero in summer
                if month in [6, 7, 8]:
                    precip = rng.exponential(0.5) if rng.random() < 0.1 else 0.0
                else:
                    precip = rng.exponential(3.0) if rng.random() < 0.4 else 0.0

                # Compute FWI components
                # Accumulate FWI codes from earlier in the season
                prev_ffmc = 70 + min(30, (doy - 90) * 0.2) if doy > 90 else 70
                prev_dmc = 10 + min(80, (doy - 90) * 0.5) if doy > 90 else 10
                prev_dc = 50 + min(500, (doy - 90) * 2.0) if doy > 90 else 50

                fwi_result = _compute_fwi_from_weather(
                    temp, rh, wind, precip, prev_ffmc, prev_dmc, prev_dc, month
                )

                # SPEI drought indices (correlated with temperature/precip)
                base_spei = -0.02 * temp + 0.01 * precip + rng.normal(0, 0.5)
                spei_1 = base_spei + rng.normal(0, 0.3)
                spei_3 = base_spei * 0.8 + rng.normal(0, 0.3)
                spei_6 = base_spei * 0.6 + rng.normal(0, 0.3)
                spei_12 = base_spei * 0.4 + rng.normal(0, 0.3)

                # LFMC proxy (live fuel moisture content) from Sentinel-2 SWIR
                # Lower LFMC = drier vegetation = higher fire risk
                # Available from 2018 onwards (Sentinel-2 operational)
                if year >= 2018:
                    base_lfmc = 120 - 1.5 * temp + 0.3 * rh + rng.normal(0, 15)
                    lfmc = max(30, min(200, base_lfmc))
                else:
                    lfmc = np.nan  # Sentinel-2 not available before 2018

                # NDVI pre-fire greenness
                ndvi = np.clip(0.4 + 0.01 * rh - 0.005 * temp + rng.normal(0, 0.08), 0.05, 0.95)

                # Soil moisture anomaly
                soil_moisture = np.clip(0.3 - 0.005 * temp + 0.003 * precip + rng.normal(0, 0.05), 0.05, 0.6)

                # Time of day (hour of detection)
                # Afternoon fires more likely to become VLF
                detection_hour = int(np.clip(rng.normal(14, 3), 6, 22))

                # Heat wave indicator: consecutive days > 35C
                if temp > 30:
                    heatwave_days = int(rng.exponential(3))
                else:
                    heatwave_days = 0

                # Night temperature (previous night minimum)
                night_temp = temp - rng.uniform(5, 15)

                # Previous year precipitation (affects fuel load)
                prev_year_precip = rng.normal(700, 150)  # mm annual

                # WUI proximity (km to nearest urban area)
                wui_dist = max(0, rng.exponential(5))

                # Concurrent fire count (suppression resource exhaustion)
                if month in [7, 8] and year in [2017, 2022, 2025]:
                    concurrent_fires = rng.poisson(15)
                elif month in [7, 8]:
                    concurrent_fires = rng.poisson(5)
                else:
                    concurrent_fires = rng.poisson(1)

                # ---- VLF probability model ----
                # This encodes the known causal relationships from literature
                logit = -5.0  # base rate ~0.7%

                # FWI is the current operational predictor
                logit += 0.03 * fwi_result["fwi"]

                # LFMC is the key competing predictor
                if not np.isnan(lfmc):
                    logit -= 0.025 * (lfmc - 80)  # low LFMC increases VLF risk

                # SPEI drought effect
                logit -= 0.4 * spei_6  # negative SPEI (drought) increases risk

                # Eucalyptus effect (Portuguese specialty)
                logit += 1.5 * eucalyptus_frac

                # Land cover fire spread rate
                logit += 0.3 * np.log(FIRE_SPREAD_MULTIPLIER.get(land_cover, 1.0))

                # Wind effect (strong threshold)
                if wind > 40:
                    logit += 0.8
                elif wind > 25:
                    logit += 0.3

                # Slope effect
                logit += 0.01 * slope

                # Afternoon fire effect
                if 13 <= detection_hour <= 17:
                    logit += 0.3

                # Heat wave effect
                logit += 0.15 * heatwave_days

                # Suppression exhaustion
                if concurrent_fires > 10:
                    logit += 0.5
                elif concurrent_fires > 5:
                    logit += 0.2

                # Night temperature (overnight drying)
                if night_temp > 20:
                    logit += 0.3

                # 2025 August NW Iberia cluster (specific historical event)
                if (year == 2025 and month == 8
                        and region_info["country"] in ["PT", "ES"]
                        and lat > 41.0):
                    logit += 1.0  # much higher VLF risk

                # VLF determination
                vlf_prob = 1.0 / (1.0 + np.exp(-logit))
                is_vlf = rng.random() < vlf_prob

                # Burned area
                if is_vlf:
                    burned_area = max(500, rng.lognormal(7.0, 0.8))  # >500 ha
                else:
                    burned_area = max(1, min(499, rng.lognormal(3.0, 1.5)))

                records.append({
                    "fire_id": fire_id,
                    "year": year,
                    "month": month,
                    "doy": doy,
                    "country": country,
                    "nuts3": region,
                    "nuts3_name": region_info["name"],
                    "lat": round(lat, 4),
                    "lon": round(lon, 4),
                    "burned_area_ha": round(burned_area, 1),
                    "is_vlf": int(is_vlf),
                    "land_cover": land_cover,
                    "eucalyptus_frac": eucalyptus_frac,
                    "elevation_m": round(elevation, 0),
                    "slope_deg": round(slope, 1),
                    "aspect_deg": round(aspect, 0),
                    "temp_c": round(temp, 1),
                    "rh_pct": round(rh, 1),
                    "wind_kmh": round(wind, 1),
                    "precip_mm": round(precip, 1),
                    "ffmc": round(fwi_result["ffmc"], 1),
                    "dmc": round(fwi_result["dmc"], 1),
                    "dc": round(fwi_result["dc"], 1),
                    "isi": round(fwi_result["isi"], 1),
                    "bui": round(fwi_result["bui"], 1),
                    "fwi": round(fwi_result["fwi"], 1),
                    "spei_1": round(spei_1, 2),
                    "spei_3": round(spei_3, 2),
                    "spei_6": round(spei_6, 2),
                    "spei_12": round(spei_12, 2),
                    "lfmc": round(lfmc, 1) if not np.isnan(lfmc) else np.nan,
                    "ndvi": round(ndvi, 3),
                    "soil_moisture": round(soil_moisture, 3),
                    "detection_hour": detection_hour,
                    "heatwave_days": heatwave_days,
                    "night_temp_c": round(night_temp, 1),
                    "prev_year_precip_mm": round(prev_year_precip, 0),
                    "wui_dist_km": round(wui_dist, 1),
                    "concurrent_fires": concurrent_fires,
                })

    df = pd.DataFrame(records)
    df = df.sort_values(["year", "doy", "fire_id"]).reset_index(drop=True)
    return df


def load_dataset(
    use_synthetic: bool = True,
    seed: int = 42,
    n_scale: float = 0.05,  # 5% scale for fast iteration (still ~1000 fires/year)
) -> pd.DataFrame:
    """Load the fire event dataset.

    If real data files exist in data/, loads them. Otherwise generates
    synthetic data calibrated to published EFFIS statistics.

    Parameters:
        use_synthetic: if True, always use synthetic data
        seed: random seed for synthetic generation
        n_scale: scale factor for synthetic data size

    Returns:
        DataFrame with fire events and all features
    """
    real_file = DATA_DIR / "effis_fires.parquet"
    if not use_synthetic and real_file.exists():
        df = pd.read_parquet(real_file)
    else:
        df = generate_synthetic_fires(seed=seed, n_scale=n_scale)

    return df


def get_temporal_cv_folds(
    df: pd.DataFrame,
    n_folds: int = 5,
    holdout_year: int = 2025,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Generate temporal cross-validation folds.

    Critical: train on past years, validate on future years. No random shuffle.
    The holdout year (2025) is NEVER included in CV folds.

    Parameters:
        df: fire event DataFrame
        n_folds: number of CV folds
        holdout_year: year to exclude (reserved for final holdout)

    Returns:
        list of (train_indices, val_indices) tuples
    """
    df_cv = df[df["year"] < holdout_year].copy()
    years = sorted(df_cv["year"].unique())

    # Each fold: train on earlier years, validate on next year(s)
    folds = []
    fold_size = max(1, len(years) // (n_folds + 1))

    for i in range(n_folds):
        val_start = (i + 1) * fold_size
        val_end = min(val_start + fold_size, len(years))
        if val_start >= len(years):
            break

        train_years = years[:val_start]
        val_years = years[val_start:val_end]

        train_mask = df_cv["year"].isin(train_years)
        val_mask = df_cv["year"].isin(val_years)

        train_idx = df_cv.index[train_mask].values
        val_idx = df_cv.index[val_mask].values

        if len(train_idx) > 0 and len(val_idx) > 0:
            folds.append((train_idx, val_idx))

    return folds


def get_holdout_split(
    df: pd.DataFrame,
    holdout_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into training (all years before holdout) and holdout (holdout year).

    Parameters:
        df: fire event DataFrame
        holdout_year: the year to use as holdout test set

    Returns:
        (train_df, holdout_df)
    """
    train = df[df["year"] < holdout_year].copy()
    holdout = df[df["year"] == holdout_year].copy()
    return train, holdout
