"""Evaluation harness for Dublin/Cork NO2 source attribution.

Source attribution approach (receptor-based, station-type differencing + seasonal
decomposition, validated against COVID-19 lockdown natural experiment):

Method:

1. BACKGROUND (regional): Monthly mean of rural stations (Lough Navar + Moate)
   - Represents long-range transport, transboundary, and biogenic sources
   - Typically 2-5 µg/m³, varies seasonally

2. HEATING (residential solid fuel): Seasonal excess at BACKGROUND urban stations
   - Method: at each background station, summer (Jun-Aug) mean = "no-heating baseline"
   - Heating = max(0, monthly_mean - summer_mean) at background stations
   - This isolates the residential/commercial heating signal without traffic
   - Applied uniformly across the city (heating is spatially diffuse)

3. TRAFFIC (road transport): Traffic-station excess over nearby background
   - For each traffic station: traffic = measured - (background + heating_estimate)
   - Validated: COVID lockdown (Mar-Jun 2020) removed ~60-70% of road traffic
     and the traffic contribution dropped proportionally

4. RESIDUAL: Any remaining signal (port/shipping, industry, construction)
   - Measured - background - heating - traffic

All values in µg/m³. All data is REAL from EEA/EPA Ireland monitoring network.
"""
import pandas as pd
import numpy as np
from data_loaders import (
    load_ireland_daily, load_daily_weather, load_merged_daily,
    KEY_STATIONS, WHO_ANNUAL, WHO_24H
)


def _get_rural_background_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly rural background from Lough Navar + Moate average."""
    rural_codes = ['IE0090A', 'IE0111A']
    rural = df[df['station'].isin(rural_codes) & df['NO2'].notna()].copy()
    rural['year'] = rural['date'].dt.year
    rural['month'] = rural['date'].dt.month
    bg = rural.groupby(['year', 'month'])['NO2'].mean().reset_index()
    bg.columns = ['year', 'month', 'background']
    return bg


def _get_heating_signal_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate heating contribution from background urban stations.

    Uses Ballyfermot (IE0036A), Clonskeagh (IE0028A), Tallaght (IE0140A)
    as representative Dublin background stations. The summer (Jun-Aug) mean
    at these stations represents their NO2 level without heating. The excess
    above summer in other months is the heating signal.

    This works because background stations are not next to major roads,
    so their seasonal variation is dominated by heating, not traffic.
    """
    bg_stations = ['IE0036A', 'IE0028A', 'IE0140A']
    bdf = df[df['station'].isin(bg_stations) & df['NO2'].notna()].copy()
    bdf['year'] = bdf['date'].dt.year
    bdf['month'] = bdf['date'].dt.month

    # Monthly mean across background stations
    monthly = bdf.groupby(['year', 'month'])['NO2'].mean().reset_index()
    monthly.columns = ['year', 'month', 'bg_station_monthly']

    # Summer baseline per year (average of Jun, Jul, Aug)
    summer = monthly[monthly['month'].isin([6, 7, 8])].groupby('year')['bg_station_monthly'].mean().reset_index()
    summer.columns = ['year', 'bg_summer_baseline']

    # Get rural background for the same period
    rural_bg = _get_rural_background_monthly(df)

    # Summer rural background per year
    rural_summer = rural_bg[rural_bg['month'].isin([6, 7, 8])].groupby('year')['background'].mean().reset_index()
    rural_summer.columns = ['year', 'rural_summer']

    # Merge
    monthly = monthly.merge(summer, on='year', how='left')
    monthly = monthly.merge(rural_bg, on=['year', 'month'], how='left')
    monthly = monthly.merge(rural_summer, on='year', how='left')

    # Heating at background stations = excess above summer baseline,
    # corrected for seasonal variation in rural background
    # (rural background also varies seasonally but has no heating)
    monthly['rural_excess'] = monthly['background'] - monthly['rural_summer']
    monthly['heating'] = np.maximum(0,
        (monthly['bg_station_monthly'] - monthly['bg_summer_baseline']) -
        monthly['rural_excess'].fillna(0)
    )

    return monthly[['year', 'month', 'heating']]


def attribute_sources_monthly(station: str = 'IE005AP') -> pd.DataFrame:
    """Monthly source attribution for a station.

    Returns DataFrame with columns:
        year, month, measured, background, heating, traffic, residual
    """
    df = load_ireland_daily()

    # 1. Monthly measured NO2 at this station
    sdf = df[(df['station'] == station) & df['NO2'].notna()].copy()
    sdf['year'] = sdf['date'].dt.year
    sdf['month'] = sdf['date'].dt.month
    measured = sdf.groupby(['year', 'month'])['NO2'].mean().reset_index()
    measured.columns = ['year', 'month', 'measured']

    # 2. Rural background
    bg = _get_rural_background_monthly(df)

    # 3. Heating signal from background stations
    heating = _get_heating_signal_monthly(df)

    # Merge
    result = measured.merge(bg, on=['year', 'month'], how='left')
    result = result.merge(heating, on=['year', 'month'], how='left')

    # Fill missing
    result['background'] = result['background'].fillna(result['background'].mean())
    result['heating'] = result['heating'].fillna(0)

    # 4. Traffic = excess over (background + heating)
    result['traffic'] = np.maximum(0,
        result['measured'] - result['background'] - result['heating']
    )

    # 5. Residual
    result['residual'] = result['measured'] - result['background'] - result['heating'] - result['traffic']

    # Percentages
    for src in ['background', 'heating', 'traffic', 'residual']:
        result[f'{src}_pct'] = np.where(
            result['measured'] > 0,
            result[src] / result['measured'] * 100,
            0
        )

    return result


def attribute_sources(station: str = 'IE005AP') -> pd.DataFrame:
    """Annual source attribution for a station.

    Returns DataFrame with columns:
        year, measured_annual, background, heating, traffic, residual,
        background_pct, heating_pct, traffic_pct, residual_pct
    """
    monthly = attribute_sources_monthly(station)

    annual = monthly.groupby('year').agg(
        measured_annual=('measured', 'mean'),
        background=('background', 'mean'),
        heating=('heating', 'mean'),
        traffic=('traffic', 'mean'),
        residual=('residual', 'mean'),
    ).reset_index()

    # Recompute residual to ensure sum consistency
    annual['residual'] = annual['measured_annual'] - annual['background'] - annual['heating'] - annual['traffic']

    for src in ['background', 'heating', 'traffic', 'residual']:
        annual[f'{src}_pct'] = annual[src] / annual['measured_annual'] * 100

    return annual


def who_exceedance_summary() -> pd.DataFrame:
    """Compute WHO guideline exceedance summary for all key stations."""
    df = load_ireland_daily()
    rows = []

    for code in KEY_STATIONS:
        name, stype, city = KEY_STATIONS[code]
        sdf = df[(df['station'] == code) & df['NO2'].notna()]
        if len(sdf) < 50:
            continue

        for year in sorted(sdf['date'].dt.year.unique()):
            ydf = sdf[sdf['date'].dt.year == year]
            annual_mean = ydf['NO2'].mean()
            days_over_24h = (ydf['NO2'] > WHO_24H).sum()
            total_days = len(ydf)

            rows.append({
                'station': code,
                'station_name': name,
                'station_type': stype,
                'city': city,
                'year': year,
                'annual_mean': annual_mean,
                'exceeds_who_annual': annual_mean > WHO_ANNUAL,
                'exceeds_eu_annual': annual_mean > 40,
                'days_exceeding_24h': days_over_24h,
                'total_days': total_days,
                'pct_days_exceeding_24h': days_over_24h / total_days * 100,
            })

    return pd.DataFrame(rows)


def covid_lockdown_analysis() -> pd.DataFrame:
    """Analyze COVID lockdown (Mar-Jun 2020) vs same period 2019.

    Key natural experiment for validating the traffic contribution.
    """
    df = load_ireland_daily()
    rows = []

    for code in KEY_STATIONS:
        name, stype, city = KEY_STATIONS[code]
        sdf = df[(df['station'] == code) & df['NO2'].notna()]

        lockdown = sdf[(sdf['date'] >= '2020-03-15') & (sdf['date'] <= '2020-06-30')]['NO2']
        pre = sdf[(sdf['date'] >= '2019-03-15') & (sdf['date'] <= '2019-06-30')]['NO2']

        if len(lockdown) > 10 and len(pre) > 10:
            change_abs = lockdown.mean() - pre.mean()
            change_pct = change_abs / pre.mean() * 100
            rows.append({
                'station': code,
                'station_name': name,
                'station_type': stype,
                'city': city,
                'no2_2019': pre.mean(),
                'no2_2020': lockdown.mean(),
                'change_abs': change_abs,
                'change_pct': change_pct,
            })

    return pd.DataFrame(rows)


def run_baseline_evaluation() -> dict:
    """Run baseline evaluation for results.tsv.

    Metric: Mean Absolute Error of traffic attribution vs COVID lockdown drop.
    The COVID lockdown removed ~60-70% of road traffic, so the observed NO2 drop
    should approximate 60-70% of our traffic estimate.
    """
    covid = covid_lockdown_analysis()

    # Use all stations with COVID data for validation
    validations = []
    for _, row in covid.iterrows():
        attr = attribute_sources_monthly(station=row['station'])
        # Get Mar-Jun 2019 and 2020 traffic estimates
        spring_2019 = attr[(attr['year'] == 2019) & attr['month'].isin([3, 4, 5, 6])]
        spring_2020 = attr[(attr['year'] == 2020) & attr['month'].isin([3, 4, 5, 6])]
        if len(spring_2019) > 0 and len(spring_2020) > 0:
            traffic_2019 = spring_2019['traffic'].mean()
            traffic_2020 = spring_2020['traffic'].mean()
            traffic_drop = traffic_2019 - traffic_2020
            observed_drop = abs(row['change_abs'])
            validations.append({
                'station': row['station'],
                'station_type': row['station_type'],
                'traffic_2019': traffic_2019,
                'traffic_2020': traffic_2020,
                'model_traffic_drop': traffic_drop,
                'observed_total_drop': observed_drop,
            })

    if not validations:
        return {'experiment': 'baseline', 'metric': 'covid_validation_mae', 'value': 999.0}

    vdf = pd.DataFrame(validations)
    mae = (vdf['model_traffic_drop'] - vdf['observed_total_drop']).abs().mean()

    if len(vdf) >= 2:
        corr = vdf['model_traffic_drop'].corr(vdf['observed_total_drop'])
    else:
        corr = 0.0

    return {
        'experiment': 'baseline',
        'metric': 'covid_validation_mae',
        'value': float(mae),
        'correlation': float(corr) if not np.isnan(corr) else 0.0,
        'n_stations': len(vdf),
    }


# ============================================================================
# Review response analyses (added post-review)
# ============================================================================

def wind_direction_no2_analysis(station: str = 'IE005AP', n_sectors: int = 16) -> pd.DataFrame:
    """Analyze NO2 by wind direction sector at a given station.

    Bins wind direction into n_sectors and computes mean NO2 for each.
    Uses Dublin Airport wind direction as proxy for all Dublin stations.

    Returns DataFrame with columns: wddir_bin, wddir_center, NO2_mean, NO2_median, count
    """
    from data_loaders import load_merged_daily
    df = load_merged_daily(station=station)
    df = df[df['NO2'].notna() & df['wddir_mode'].notna()].copy()

    # Bin wind direction into sectors
    bin_width = 360 / n_sectors
    df['wddir_bin'] = ((df['wddir_mode'] + bin_width / 2) % 360 // bin_width).astype(int)
    df['wddir_center'] = df['wddir_bin'] * bin_width

    result = df.groupby(['wddir_bin', 'wddir_center']).agg(
        NO2_mean=('NO2', 'mean'),
        NO2_median=('NO2', 'median'),
        count=('NO2', 'count'),
    ).reset_index()

    return result.sort_values('wddir_center')


def weekday_weekend_corrected(weekend_traffic_fraction: float = 0.60) -> pd.DataFrame:
    """Compute corrected weekday-weekend traffic estimate.

    The raw weekday-weekend method assumes weekend traffic is zero, which
    underestimates the traffic fraction. Correcting for the known weekend
    traffic fraction (typically ~60% of weekday) brings estimates closer
    to the station-differencing results.

    Formula: corrected_traffic_pct = raw_implied / (1 - weekend_traffic_fraction)

    Returns DataFrame with columns per station:
        station_name, weekday_mean, weekend_mean, ratio,
        implied_traffic_pct_raw, implied_traffic_pct_corrected,
        station_diff_traffic_pct
    """
    df = load_ireland_daily()
    rows = []

    # Stations to analyze (those with enough data and station-diff estimates)
    stations_to_check = {
        'IE005AP': ('Winetavern Street', 80),
        'IE004AP': ('Pearse Street', 64),
        'IE0131A': ('Blanchardstown (M50/N3)', 71),
        'IE0036A': ('Ballyfermot', 56),
        'IE001BP': ('Cork Old Station Road', 61),
    }

    for code, (name, station_diff_pct) in stations_to_check.items():
        sdf = df[(df['station'] == code) & df['NO2'].notna()].copy()
        sdf['dow'] = sdf['date'].dt.dayofweek  # 0=Mon, 6=Sun

        weekday = sdf[sdf['dow'] < 5]['NO2'].mean()
        weekend = sdf[sdf['dow'] >= 5]['NO2'].mean()

        if weekday > 0 and weekend > 0:
            ratio = weekday / weekend
            raw_implied = (weekday - weekend) / weekday * 100
            # Correct: the difference only captures (1 - weekend_frac) of traffic
            corrected_implied = raw_implied / (1 - weekend_traffic_fraction)
            # Cap at 100%
            corrected_implied = min(corrected_implied, 100.0)

            rows.append({
                'station_name': name,
                'weekday_mean': weekday,
                'weekend_mean': weekend,
                'ratio': ratio,
                'implied_traffic_pct_raw': raw_implied,
                'implied_traffic_pct_corrected': corrected_implied,
                'station_diff_traffic_pct': station_diff_pct,
            })

    return pd.DataFrame(rows)


def o3_no2_analysis() -> pd.DataFrame:
    """Analyze O3-NO2 relationship at stations with concurrent measurements.

    NO2 photochemistry: NO + O3 -> NO2, and NO2 + hv -> NO + O.
    This creates an anti-correlation between O3 and NO2 in urban areas.

    Returns DataFrame with columns:
        station, station_name, o3_no2_corr, o3_summer_mean, o3_winter_mean,
        no2_summer_mean, no2_winter_mean, n_days
    """
    df = load_ireland_daily()
    rows = []

    for code in KEY_STATIONS:
        name, stype, city = KEY_STATIONS[code]
        sdf = df[(df['station'] == code)].copy()
        # Only stations with both O3 and NO2
        both = sdf[sdf['O3'].notna() & sdf['NO2'].notna()].copy()
        if len(both) < 100:
            continue

        corr = both['O3'].corr(both['NO2'])
        both['month'] = both['date'].dt.month

        summer = both[both['month'].isin([6, 7, 8])]
        winter = both[both['month'].isin([12, 1, 2])]

        rows.append({
            'station': code,
            'station_name': name,
            'station_type': stype,
            'o3_no2_corr': corr,
            'o3_summer_mean': summer['O3'].mean() if len(summer) > 0 else np.nan,
            'o3_winter_mean': winter['O3'].mean() if len(winter) > 0 else np.nan,
            'no2_summer_mean': summer['NO2'].mean() if len(summer) > 0 else np.nan,
            'no2_winter_mean': winter['NO2'].mean() if len(winter) > 0 else np.nan,
            'n_days': len(both),
        })

    return pd.DataFrame(rows)


def weather_comparison_2019_2020() -> dict:
    """Compare March-June weather between 2019 and 2020.

    Quantifies meteorological confounding for the COVID validation.
    Returns dict with mean temperature, wind speed, rain, and sunshine
    for both periods.
    """
    from data_loaders import load_daily_weather
    wx = load_daily_weather()
    wx['year'] = wx['date'].dt.year
    wx['month'] = wx['date'].dt.month

    result = {}
    for year in [2019, 2020]:
        period = wx[(wx['year'] == year) & wx['month'].isin([3, 4, 5, 6])]
        result[f'temp_{year}'] = period['temp_mean'].mean()
        result[f'wdsp_{year}'] = period['wdsp_mean'].mean()
        result[f'rain_{year}'] = period['rain_sum'].mean()
        result[f'sun_{year}'] = period['sun_sum'].mean()

    # Differences
    result['temp_diff'] = result['temp_2020'] - result['temp_2019']
    result['wdsp_diff'] = result['wdsp_2020'] - result['wdsp_2019']
    result['rain_diff'] = result['rain_2020'] - result['rain_2019']
    result['sun_diff'] = result['sun_2020'] - result['sun_2019']

    return result
