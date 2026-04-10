"""Source attribution model for Dublin/Cork NO2.

This is the ONLY file modified during HDR Phase 2 experiments.
The evaluate.py harness calls functions from here.

Current approach: Receptor-based station-type differencing
- Background = rural station mean (Lough Navar + Moate)
- Heating = seasonal excess at urban background stations above their summer baseline
- Traffic = total - background - heating (validated against COVID lockdown)

Phase 2 improvements are tracked in research_queue.md and results.tsv.
"""
import pandas as pd
import numpy as np
from data_loaders import load_ireland_daily, load_daily_weather, KEY_STATIONS


# ============================================================================
# Model parameters (tunable in HDR Phase 2)
# ============================================================================

# Rural background stations
RURAL_STATIONS = ['IE0090A', 'IE0111A']

# Urban background stations used for heating signal estimation
HEATING_REF_STATIONS = ['IE0036A', 'IE0028A', 'IE0140A']

# Summer months (no-heating baseline)
SUMMER_MONTHS = [6, 7, 8]

# COVID traffic reduction factor (fraction of traffic removed during lockdown)
# Used for validation only, not for attribution
COVID_TRAFFIC_REDUCTION = 0.70


# ============================================================================
# Source attribution functions
# ============================================================================

def estimate_background(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly rural background estimate."""
    rural = df[df['station'].isin(RURAL_STATIONS) & df['NO2'].notna()].copy()
    rural['year'] = rural['date'].dt.year
    rural['month'] = rural['date'].dt.month
    bg = rural.groupby(['year', 'month'])['NO2'].mean().reset_index()
    bg.columns = ['year', 'month', 'background']
    return bg


def estimate_heating(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly heating contribution estimated from background urban stations.

    Method: The seasonal excess at background stations (above their summer baseline)
    represents the heating signal, corrected for seasonal variation in rural background.
    """
    bdf = df[df['station'].isin(HEATING_REF_STATIONS) & df['NO2'].notna()].copy()
    bdf['year'] = bdf['date'].dt.year
    bdf['month'] = bdf['date'].dt.month

    monthly = bdf.groupby(['year', 'month'])['NO2'].mean().reset_index()
    monthly.columns = ['year', 'month', 'bg_station_monthly']

    # Summer baseline per year
    summer = monthly[monthly['month'].isin(SUMMER_MONTHS)].groupby('year')[
        'bg_station_monthly'].mean().reset_index()
    summer.columns = ['year', 'bg_summer_baseline']

    # Rural background seasonal correction
    rural_bg = estimate_background(df)
    rural_summer = rural_bg[rural_bg['month'].isin(SUMMER_MONTHS)].groupby('year')[
        'background'].mean().reset_index()
    rural_summer.columns = ['year', 'rural_summer']

    monthly = monthly.merge(summer, on='year', how='left')
    monthly = monthly.merge(rural_bg, on=['year', 'month'], how='left')
    monthly = monthly.merge(rural_summer, on='year', how='left')

    # Heating = excess above summer, minus rural seasonal variation
    monthly['rural_excess'] = monthly['background'] - monthly['rural_summer']
    monthly['heating'] = np.maximum(0,
        (monthly['bg_station_monthly'] - monthly['bg_summer_baseline']) -
        monthly['rural_excess'].fillna(0)
    )

    return monthly[['year', 'month', 'heating']]


def attribute_station(df: pd.DataFrame, station: str) -> pd.DataFrame:
    """Full source attribution for a single station, monthly resolution.

    Returns: year, month, measured, background, heating, traffic, residual
    """
    sdf = df[(df['station'] == station) & df['NO2'].notna()].copy()
    sdf['year'] = sdf['date'].dt.year
    sdf['month'] = sdf['date'].dt.month
    measured = sdf.groupby(['year', 'month'])['NO2'].mean().reset_index()
    measured.columns = ['year', 'month', 'measured']

    bg = estimate_background(df)
    heating = estimate_heating(df)

    result = measured.merge(bg, on=['year', 'month'], how='left')
    result = result.merge(heating, on=['year', 'month'], how='left')

    result['background'] = result['background'].fillna(result['background'].mean())
    result['heating'] = result['heating'].fillna(0)

    # Traffic = residual after removing background and heating
    result['traffic'] = np.maximum(0,
        result['measured'] - result['background'] - result['heating']
    )

    result['residual'] = (result['measured'] - result['background'] -
                          result['heating'] - result['traffic'])

    return result
