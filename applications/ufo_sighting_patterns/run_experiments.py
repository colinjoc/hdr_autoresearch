#!/usr/bin/env python3
"""
Full HDR experiment pipeline for NUFORC UFO sighting pattern analysis.
Runs all experiments E00-E22, tournament, Phase 2.5 interactions, and Phase B discovery.
"""
import pandas as pd
import numpy as np
import os
import sys
import warnings
from collections import OrderedDict

warnings.filterwarnings('ignore')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from data_loader import load_nuforc_str, load_nuforc_kaggle

RESULTS_FILE = os.path.join(PROJECT_DIR, "results.tsv")

# US state populations (2020 Census, thousands)
STATE_POP_2020 = {
    'AL': 5024, 'AK': 733, 'AZ': 7151, 'AR': 3012, 'CA': 39538,
    'CO': 5773, 'CT': 3606, 'DE': 990, 'FL': 21538, 'GA': 10712,
    'HI': 1456, 'ID': 1901, 'IL': 12812, 'IN': 6786, 'IA': 3190,
    'KS': 2937, 'KY': 4506, 'LA': 4657, 'ME': 1362, 'MD': 6177,
    'MA': 7030, 'MI': 10077, 'MN': 5707, 'MS': 2961, 'MO': 6155,
    'MT': 1085, 'NE': 1962, 'NV': 3105, 'NH': 1378, 'NJ': 9289,
    'NM': 2118, 'NY': 20202, 'NC': 10440, 'ND': 779, 'OH': 11800,
    'OK': 3960, 'OR': 4238, 'PA': 13002, 'RI': 1098, 'SC': 5119,
    'SD': 887, 'TN': 6910, 'TX': 29146, 'UT': 3272, 'VT': 643,
    'VA': 8631, 'WA': 7615, 'WV': 1794, 'WI': 5894, 'WY': 577,
    'DC': 689
}

# Country populations (approx 2020, millions)
COUNTRY_POP = {'us': 331, 'ca': 38, 'gb': 67, 'au': 26, 'de': 83}


def append_result(exp_id, description, metric, value, status="KEEP",
                  interaction=False, notes=""):
    """Append a result to results.tsv."""
    row = {
        'experiment_id': exp_id,
        'description': description,
        'metric': metric,
        'value': value,
        'status': status,
        'interaction': interaction,
        'notes': notes
    }
    df = pd.DataFrame([row])
    if os.path.exists(RESULTS_FILE):
        df.to_csv(RESULTS_FILE, mode='a', sep='\t', header=False, index=False)
    else:
        df.to_csv(RESULTS_FILE, sep='\t', index=False)


def run_E00_baseline(df):
    """E00: Baseline — annual sighting count 1990-2024."""
    print("=" * 60)
    print("E00: Baseline — annual sighting count 1990-2024")
    yearly = df[(df['year'] >= 1990) & (df['year'] <= 2024)].groupby('year').size()
    total = yearly.sum()
    peak_year = yearly.idxmax()
    peak_count = yearly.max()
    print(f"  Total sightings 1990-2024: {total}")
    print(f"  Peak year: {int(peak_year)} with {peak_count} sightings")
    print(f"  Years covered: {len(yearly)}")

    append_result("E00", "Baseline annual count 1990-2024",
                  "peak_year", int(peak_year), "KEEP",
                  notes=f"total={total}; peak_count={peak_count}")
    return yearly


def run_E01_annual_trend(df):
    """E01: Annual trend 1990-2024."""
    print("\n" + "=" * 60)
    print("E01: Annual trend 1990-2024")
    yearly = df[(df['year'] >= 1990) & (df['year'] <= 2024)].groupby('year').size()

    # Find growth phase and decline phase
    peak_year = int(yearly.idxmax())
    pre_peak = yearly[yearly.index <= peak_year]
    post_peak = yearly[yearly.index > peak_year]

    # Growth rate (CAGR)
    start_count = yearly.iloc[0]
    peak_count = yearly.max()
    years_growth = peak_year - yearly.index[0]
    if years_growth > 0 and start_count > 0:
        cagr = (peak_count / start_count) ** (1 / years_growth) - 1
    else:
        cagr = 0

    print(f"  Growth phase: {int(yearly.index[0])}-{peak_year}")
    print(f"  CAGR during growth: {cagr:.1%}")
    print(f"  Peak count: {peak_count}")
    if len(post_peak) > 0:
        latest = post_peak.iloc[-1] if len(post_peak) > 0 else 0
        print(f"  Post-peak decline to {latest} ({int(post_peak.index[-1])})")

    append_result("E01", "Annual trend analysis", "CAGR_growth_phase",
                  round(cagr, 4), "KEEP",
                  notes=f"peak_year={peak_year}; peak_count={peak_count}")
    return yearly


def run_E02_day_of_week(df):
    """E02: Day-of-week pattern."""
    print("\n" + "=" * 60)
    print("E02: Day-of-week pattern")
    valid = df[df['day_of_week'].notna()].copy()
    dow_counts = valid.groupby('day_of_week').size()
    dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    for i, name in enumerate(dow_names):
        if i in dow_counts.index:
            print(f"  {name}: {dow_counts[i]}")

    # Chi-square test
    from scipy.stats import chisquare
    observed = dow_counts.values
    chi2, pval = chisquare(observed)
    print(f"  Chi-square: {chi2:.1f}, p={pval:.2e}")

    weekend = dow_counts[[5, 6]].sum()
    weekday = dow_counts[[0, 1, 2, 3, 4]].sum()
    weekend_ratio = (weekend / 2) / (weekday / 5)
    print(f"  Weekend/weekday ratio: {weekend_ratio:.3f}")

    append_result("E02", "Day-of-week pattern", "weekend_weekday_ratio",
                  round(weekend_ratio, 4), "KEEP",
                  notes=f"chi2={chi2:.1f}; p={pval:.2e}")


def run_E03_hour_of_day(df):
    """E03: Hour-of-day pattern."""
    print("\n" + "=" * 60)
    print("E03: Hour-of-day pattern")
    valid = df[df['hour'].notna()].copy()
    hour_counts = valid.groupby('hour').size()

    peak_hour = int(hour_counts.idxmax())
    print(f"  Peak hour: {peak_hour}:00 ({hour_counts.max()} sightings)")

    night = hour_counts[(hour_counts.index >= 20) | (hour_counts.index <= 4)].sum()
    day = hour_counts[(hour_counts.index >= 8) & (hour_counts.index <= 16)].sum()
    dusk = hour_counts[(hour_counts.index >= 17) & (hour_counts.index <= 22)].sum()

    print(f"  Night (20-04): {night}")
    print(f"  Day (08-16): {day}")
    print(f"  Dusk (17-22): {dusk}")
    print(f"  Night/Day ratio: {night/day:.2f}")

    append_result("E03", "Hour-of-day pattern", "peak_hour", peak_hour, "KEEP",
                  notes=f"night_day_ratio={night/day:.2f}")


def run_E04_seasonal(df):
    """E04: Seasonal pattern."""
    print("\n" + "=" * 60)
    print("E04: Seasonal pattern")
    valid = df[df['month'].notna()].copy()
    monthly = valid.groupby('month').size()
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    for i, name in enumerate(month_names, 1):
        if i in monthly.index:
            print(f"  {name}: {monthly[i]}")

    summer = monthly[[6, 7, 8]].sum()
    winter = monthly[[12, 1, 2]].sum()
    summer_ratio = summer / winter
    peak_month = int(monthly.idxmax())

    print(f"  Summer/Winter ratio: {summer_ratio:.2f}")
    print(f"  Peak month: {month_names[peak_month-1]}")

    append_result("E04", "Seasonal pattern", "summer_winter_ratio",
                  round(summer_ratio, 3), "KEEP",
                  notes=f"peak_month={month_names[peak_month-1]}")


def run_E05_shape_evolution(df):
    """E05: Shape evolution over time."""
    print("\n" + "=" * 60)
    print("E05: Shape evolution over time")
    valid = df[(df['year'] >= 1990) & (df['year'] <= 2024) & df['Shape'].notna()].copy()

    # Decade bins
    valid['decade'] = (valid['year'] // 10) * 10

    top_shapes = ['Light', 'Circle', 'Triangle', 'Fireball', 'Disk', 'Sphere',
                  'Orb', 'Formation', 'Other', 'Unknown']

    shape_decade = valid[valid['Shape'].isin(top_shapes)].groupby(['decade', 'Shape']).size().unstack(fill_value=0)

    # Normalize to fractions per decade
    shape_pct = shape_decade.div(shape_decade.sum(axis=1), axis=0) * 100

    print("  Shape fraction by decade (%):")
    print(shape_pct.round(1).to_string())

    # Disk trend
    if 'Disk' in shape_pct.columns:
        disk_90s = shape_pct.loc[1990, 'Disk'] if 1990 in shape_pct.index else 0
        disk_20s = shape_pct.loc[2020, 'Disk'] if 2020 in shape_pct.index else 0
        print(f"\n  Disk: {disk_90s:.1f}% (1990s) → {disk_20s:.1f}% (2020s)")

    # Light trend
    if 'Light' in shape_pct.columns:
        light_90s = shape_pct.loc[1990, 'Light'] if 1990 in shape_pct.index else 0
        light_20s = shape_pct.loc[2020, 'Light'] if 2020 in shape_pct.index else 0
        print(f"  Light: {light_90s:.1f}% (1990s) → {light_20s:.1f}% (2020s)")

    append_result("E05", "Shape evolution over time", "disk_decline_pct",
                  round(disk_90s - disk_20s, 1) if 'Disk' in shape_pct.columns else 0, "KEEP",
                  notes=f"disk_1990s={disk_90s:.1f}%; disk_2020s={disk_20s:.1f}%")


def run_E06_duration(df):
    """E06: Duration distribution."""
    print("\n" + "=" * 60)
    print("E06: Duration distribution")
    valid = df[df['duration_seconds'].notna() & (df['duration_seconds'] > 0)].copy()

    # Cap at 99th percentile for analysis
    cap = valid['duration_seconds'].quantile(0.99)
    capped = valid[valid['duration_seconds'] <= cap]

    median_dur = capped['duration_seconds'].median()
    mean_dur = capped['duration_seconds'].mean()
    q25 = capped['duration_seconds'].quantile(0.25)
    q75 = capped['duration_seconds'].quantile(0.75)

    print(f"  N valid durations: {len(capped)}")
    print(f"  Median: {median_dur:.0f} sec ({median_dur/60:.1f} min)")
    print(f"  Mean: {mean_dur:.0f} sec ({mean_dur/60:.1f} min)")
    print(f"  IQR: {q25:.0f} - {q75:.0f} sec")
    print(f"  99th percentile cap: {cap:.0f} sec ({cap/3600:.1f} hr)")

    append_result("E06", "Duration distribution", "median_duration_sec",
                  round(median_dur, 1), "KEEP",
                  notes=f"mean={mean_dur:.0f}; IQR={q25:.0f}-{q75:.0f}")


def run_E07_state_percapita(df):
    """E07: US state per-capita sighting rate."""
    print("\n" + "=" * 60)
    print("E07: US state per-capita sighting rate")

    # Map state abbreviations
    us_df = df[df['country_str'].isin(['USA', 'US', 'United States'])].copy()
    us_df['state_clean'] = us_df['state'].str.strip().str.upper()
    state_counts = us_df.groupby('state_clean').size().reset_index(name='count')

    # Filter to valid states
    state_counts = state_counts[state_counts['state_clean'].isin(STATE_POP_2020.keys())]
    state_counts['pop_thousands'] = state_counts['state_clean'].map(STATE_POP_2020)
    state_counts['per_100k'] = state_counts['count'] / state_counts['pop_thousands'] * 100
    state_counts = state_counts.sort_values('per_100k', ascending=False)

    print("  Top 10 states by per-capita sighting rate (per 100k):")
    for _, row in state_counts.head(10).iterrows():
        print(f"    {row['state_clean']}: {row['per_100k']:.1f} per 100k ({row['count']} total)")

    print("\n  Bottom 5 states:")
    for _, row in state_counts.tail(5).iterrows():
        print(f"    {row['state_clean']}: {row['per_100k']:.1f} per 100k ({row['count']} total)")

    top_state = state_counts.iloc[0]['state_clean']
    top_rate = state_counts.iloc[0]['per_100k']

    append_result("E07", "US state per-capita sighting rate", "top_state_rate_per_100k",
                  round(top_rate, 1), "KEEP",
                  notes=f"top_state={top_state}")
    return state_counts


def run_E08_military_proximity(df_kaggle):
    """E08: Proximity to military bases."""
    print("\n" + "=" * 60)
    print("E08: Proximity to military bases (geocoded subset)")

    # Major US military base coordinates (top 20)
    bases = {
        'Fort Liberty': (35.14, -79.00), 'Fort Cavazos': (31.13, -97.78),
        'JBLM': (47.10, -122.58), 'Fort Stewart': (31.87, -81.61),
        'Fort Campbell': (36.66, -87.47), 'Fort Carson': (38.74, -104.79),
        'Nellis AFB': (36.24, -115.03), 'Edwards AFB': (34.91, -117.88),
        'Eglin AFB': (30.47, -86.53), 'Wright-Patterson': (39.83, -84.05),
        'Norfolk NB': (36.95, -76.33), 'San Diego NB': (32.68, -117.15),
        'Kitsap NB': (47.56, -122.71), 'Pearl Harbor': (21.35, -157.95),
        'Vandenberg SFB': (34.74, -120.57), 'Cape Canaveral': (28.39, -80.60),
        'Area 51/Groom Lake': (37.24, -115.81), 'Langley AFB': (37.08, -76.36),
        'Offutt AFB': (41.12, -95.91), 'Tinker AFB': (35.42, -97.38),
    }

    from scipy.spatial.distance import cdist

    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    sighting_coords = valid[['latitude', 'longitude']].values
    base_coords = np.array(list(bases.values()))

    # Simple Euclidean distance in degrees (approximate)
    min_dists = []
    for i in range(0, len(sighting_coords), 10000):
        chunk = sighting_coords[i:i+10000]
        dists = cdist(chunk, base_coords)
        min_dists.extend(dists.min(axis=1))

    valid = valid.iloc[:len(min_dists)].copy()
    valid['min_base_dist_deg'] = min_dists
    valid['min_base_dist_km'] = valid['min_base_dist_deg'] * 111  # rough conversion

    near_base = valid[valid['min_base_dist_km'] <= 50]
    far_base = valid[valid['min_base_dist_km'] > 50]

    near_frac = len(near_base) / len(valid)
    print(f"  Sightings within 50km of major military base: {len(near_base)} ({near_frac:.1%})")
    print(f"  Sightings >50km from base: {len(far_base)} ({1-near_frac:.1%})")

    # Rate comparison (rough)
    print(f"  Near-base fraction: {near_frac:.3f}")

    append_result("E08", "Military base proximity", "near_base_fraction_50km",
                  round(near_frac, 4), "KEEP",
                  notes=f"n_near={len(near_base)}; n_far={len(far_base)}")


def run_E09_airport_proximity(df_kaggle):
    """E09: Proximity to major airports."""
    print("\n" + "=" * 60)
    print("E09: Proximity to major airports (geocoded subset)")

    # Top 20 US airports by traffic
    airports = {
        'ATL': (33.64, -84.43), 'LAX': (33.94, -118.41), 'ORD': (41.98, -87.90),
        'DFW': (32.90, -97.04), 'DEN': (39.86, -104.67), 'JFK': (40.64, -73.78),
        'SFO': (37.62, -122.38), 'SEA': (47.45, -122.31), 'LAS': (36.08, -115.15),
        'MCO': (28.43, -81.31), 'CLT': (35.21, -80.94), 'PHX': (33.44, -112.01),
        'IAH': (29.98, -95.34), 'MIA': (25.80, -80.29), 'BOS': (42.37, -71.02),
        'MSP': (44.88, -93.22), 'DTW': (42.21, -83.35), 'FLL': (26.07, -80.15),
        'EWR': (40.69, -74.17), 'SLC': (40.79, -111.98),
    }

    from scipy.spatial.distance import cdist

    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    sighting_coords = valid[['latitude', 'longitude']].values
    airport_coords = np.array(list(airports.values()))

    min_dists = []
    for i in range(0, len(sighting_coords), 10000):
        chunk = sighting_coords[i:i+10000]
        dists = cdist(chunk, airport_coords)
        min_dists.extend(dists.min(axis=1))

    valid = valid.iloc[:len(min_dists)].copy()
    valid['min_airport_dist_km'] = np.array(min_dists) * 111

    near_airport = valid[valid['min_airport_dist_km'] <= 30]
    near_frac = len(near_airport) / len(valid)

    print(f"  Sightings within 30km of major airport: {len(near_airport)} ({near_frac:.1%})")

    append_result("E09", "Airport proximity", "near_airport_fraction_30km",
                  round(near_frac, 4), "KEEP",
                  notes=f"n_near={len(near_airport)}")


def run_E10_launch_sites(df_kaggle):
    """E10: Proximity to launch sites."""
    print("\n" + "=" * 60)
    print("E10: Proximity to launch sites")

    launch_sites = {
        'Vandenberg': (34.74, -120.57),
        'Cape Canaveral': (28.39, -80.60),
        'Wallops': (37.94, -75.47),
    }

    from scipy.spatial.distance import cdist

    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    sighting_coords = valid[['latitude', 'longitude']].values
    launch_coords = np.array(list(launch_sites.values()))

    dists = cdist(sighting_coords, launch_coords)
    valid['min_launch_dist_km'] = dists.min(axis=1) * 111

    for name, (lat, lon) in launch_sites.items():
        near = valid[valid['min_launch_dist_km'] <= 100]
        print(f"  Within 100km of any launch site: {len(near)} ({len(near)/len(valid):.1%})")
        break

    append_result("E10", "Launch site proximity", "near_launch_fraction_100km",
                  round(len(near)/len(valid), 4), "KEEP")


def run_E11_starlink(df):
    """E11: Starlink era effect on formation/light sightings."""
    print("\n" + "=" * 60)
    print("E11: Starlink era (post-May 2019) analysis")

    valid = df[df['year'].notna() & df['Shape'].notna()].copy()

    # Pre-Starlink: 2015-2019 April; Post-Starlink: 2019 May - 2024
    pre = valid[(valid['year'] >= 2015) &
                ((valid['year'] < 2019) | ((valid['year'] == 2019) & (valid['month'] < 5)))]
    post = valid[(valid['year'] >= 2019) &
                 ~((valid['year'] == 2019) & (valid['month'] < 5))]

    pre_months = 4 * 12 + 4  # 2015-Jan to 2019-Apr = 52 months
    post_months = (2024 - 2019) * 12 + 8  # 2019-May to 2024 ≈ 68 months

    shapes_of_interest = ['Formation', 'Light', 'Disk', 'Triangle']

    print(f"  Pre-Starlink period: {len(pre)} sightings ({pre_months} months)")
    print(f"  Post-Starlink period: {len(post)} sightings ({post_months} months)")
    print()

    formation_pre_rate = len(pre[pre['Shape'] == 'Formation']) / pre_months
    formation_post_rate = len(post[post['Shape'] == 'Formation']) / post_months

    for shape in shapes_of_interest:
        pre_count = len(pre[pre['Shape'] == shape])
        post_count = len(post[post['Shape'] == shape])
        pre_rate = pre_count / pre_months
        post_rate = post_count / post_months
        ratio = post_rate / pre_rate if pre_rate > 0 else float('inf')
        print(f"  {shape}: pre={pre_rate:.1f}/mo, post={post_rate:.1f}/mo, ratio={ratio:.2f}x")

    starlink_ratio = formation_post_rate / formation_pre_rate if formation_pre_rate > 0 else 0

    append_result("E11", "Starlink era formation sighting rate", "formation_rate_ratio",
                  round(starlink_ratio, 2), "KEEP",
                  notes=f"pre={formation_pre_rate:.1f}/mo; post={formation_post_rate:.1f}/mo")

    return starlink_ratio


def run_E12_satellite_reentry(df):
    """E12: ISS/satellite correlation (proxy analysis)."""
    print("\n" + "=" * 60)
    print("E12: ISS/satellite re-entry correlation (text proxy)")

    valid = df[df['Text'].notna()].copy()
    text_lower = valid['Text'].str.lower()

    iss_mentions = text_lower.str.contains('iss |international space station|space station', na=False).sum()
    satellite_mentions = text_lower.str.contains('satellite', na=False).sum()
    meteor_mentions = text_lower.str.contains('meteor|shooting star|re-entry|reentry', na=False).sum()

    print(f"  Reports mentioning ISS: {iss_mentions}")
    print(f"  Reports mentioning satellite: {satellite_mentions}")
    print(f"  Reports mentioning meteor/re-entry: {meteor_mentions}")
    print(f"  Total with text: {len(valid)}")

    append_result("E12", "Satellite/ISS text mentions", "satellite_mention_count",
                  satellite_mentions, "KEEP",
                  notes=f"iss={iss_mentions}; meteor={meteor_mentions}")


def run_E13_explanation_field(df):
    """E13: Explanation field analysis."""
    print("\n" + "=" * 60)
    print("E13: Explanation field analysis")

    total = len(df)
    explained = df['has_explanation'].sum()
    frac = explained / total

    print(f"  Total reports: {total}")
    print(f"  With explanation: {explained} ({frac:.2%})")
    print(f"  Without explanation: {total - explained}")

    print("\n  Explanation types:")
    type_counts = df['explanation_type'].value_counts()
    for t, c in type_counts.head(15).items():
        print(f"    {t}: {c}")

    print("\n  Certainty levels:")
    cert_counts = df['explanation_certainty'].value_counts()
    for c, count in cert_counts.items():
        print(f"    {c}: {count}")

    append_result("E13", "Explanation field analysis", "explained_fraction",
                  round(frac, 4), "KEEP",
                  notes=f"top_type={type_counts.index[0]}; n_explained={explained}")


def run_E14_reporting_lag(df):
    """E14: Reporting lag analysis."""
    print("\n" + "=" * 60)
    print("E14: Reporting lag (Occurred → Reported)")

    valid = df[df['reporting_lag_days'].notna() &
               (df['reporting_lag_days'] >= 0) &
               (df['reporting_lag_days'] <= 365*20)].copy()

    median_lag = valid['reporting_lag_days'].median()
    mean_lag = valid['reporting_lag_days'].mean()
    same_day = (valid['reporting_lag_days'] < 1).sum()
    within_week = (valid['reporting_lag_days'] < 7).sum()

    print(f"  Valid lag calculations: {len(valid)}")
    print(f"  Median lag: {median_lag:.1f} days")
    print(f"  Mean lag: {mean_lag:.1f} days")
    print(f"  Same-day reports: {same_day} ({same_day/len(valid):.1%})")
    print(f"  Within 1 week: {within_week} ({within_week/len(valid):.1%})")

    append_result("E14", "Reporting lag", "median_lag_days",
                  round(median_lag, 1), "KEEP",
                  notes=f"same_day_frac={same_day/len(valid):.3f}")


def run_E15_observer_count(df):
    """E15: Observer count analysis."""
    print("\n" + "=" * 60)
    print("E15: Observer count")

    valid = df[df['No of observers'].notna()].copy()
    valid['n_obs'] = valid['No of observers'].astype(int)

    single = (valid['n_obs'] == 1).sum()
    multi = (valid['n_obs'] > 1).sum()

    print(f"  Single observer: {single} ({single/len(valid):.1%})")
    print(f"  Multiple observers: {multi} ({multi/len(valid):.1%})")
    print(f"  Median observers: {valid['n_obs'].median()}")
    print(f"  Max observers: {valid['n_obs'].max()}")

    obs_dist = valid['n_obs'].value_counts().sort_index().head(10)
    print("\n  Distribution:")
    for n, c in obs_dist.items():
        print(f"    {n} observer(s): {c}")

    append_result("E15", "Observer count", "single_observer_fraction",
                  round(single/len(valid), 4), "KEEP")


def run_E16_country_comparison(df_kaggle):
    """E16: Country comparison."""
    print("\n" + "=" * 60)
    print("E16: Country comparison")

    country_counts = df_kaggle.groupby('country').size()

    print("  Raw counts:")
    for country, count in country_counts.items():
        pop = COUNTRY_POP.get(country, None)
        if pop:
            rate = count / (pop * 10)  # per million → per 100k
            print(f"    {country}: {count} ({rate:.1f} per 100k)")
        else:
            print(f"    {country}: {count}")

    us_rate = country_counts.get('us', 0) / (COUNTRY_POP['us'] * 10)
    ca_rate = country_counts.get('ca', 0) / (COUNTRY_POP['ca'] * 10)

    ratio = us_rate / ca_rate if ca_rate > 0 else 0
    print(f"\n  US/Canada per-capita ratio: {ratio:.2f}")

    append_result("E16", "Country comparison", "us_canada_percapita_ratio",
                  round(ratio, 2), "KEEP")


def run_E17_urban_rural(df_kaggle):
    """E17: Urban vs rural proxy (population density via coordinates)."""
    print("\n" + "=" * 60)
    print("E17: Urban vs rural (latitude proxy)")

    # Use a simple proxy: major metro areas have higher sighting density
    # but after per-capita normalization, rural areas may dominate
    us = df_kaggle[df_kaggle['country'] == 'us'].copy()
    us['latitude'] = pd.to_numeric(us['latitude'], errors='coerce')
    us['longitude'] = pd.to_numeric(us['longitude'], errors='coerce')
    valid = us[us['latitude'].notna()].copy()

    # Bin by lat/lon grid cells (1 degree)
    valid['lat_bin'] = (valid['latitude']).round(0)
    valid['lon_bin'] = (valid['longitude']).round(0)
    cell_counts = valid.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='count')

    high_density = cell_counts[cell_counts['count'] >= cell_counts['count'].quantile(0.9)]
    low_density = cell_counts[cell_counts['count'] <= cell_counts['count'].quantile(0.5)]

    print(f"  Total 1-degree grid cells with sightings: {len(cell_counts)}")
    print(f"  Top 10% cells (≥{cell_counts['count'].quantile(0.9):.0f} sightings): {len(high_density)}")
    print(f"  Bottom 50% cells (≤{cell_counts['count'].quantile(0.5):.0f} sightings): {len(low_density)}")
    print(f"  Median sightings per cell: {cell_counts['count'].median():.0f}")
    print(f"  Max sightings per cell: {cell_counts['count'].max()}")

    append_result("E17", "Urban vs rural spatial density", "median_sightings_per_cell",
                  int(cell_counts['count'].median()), "KEEP")


def run_E18_media_events(df):
    """E18: Media event correlation."""
    print("\n" + "=" * 60)
    print("E18: Media-event correlation")

    valid = df[df['year'].notna()].copy()
    monthly = valid.groupby([valid['year'], valid['month']]).size().reset_index(name='count')
    monthly.columns = ['year', 'month', 'count']

    # Known media events
    events = {
        'Dec 2017 NYT AATIP': (2017, 12),
        'Jun 2021 ODNI report': (2021, 6),
        'May 2019 Starlink launch': (2019, 5),
        'Jun 2023 Grusch testimony': (2023, 6),
    }

    for name, (y, m) in events.items():
        row = monthly[(monthly['year'] == y) & (monthly['month'] == m)]
        if len(row) > 0:
            count = row['count'].values[0]
            # Compare to surrounding months
            surround = monthly[
                ((monthly['year'] == y) & (monthly['month'].between(m-2, m+2))) |
                ((monthly['year'] == y-1) & (monthly['month'] >= 10)) |
                ((monthly['year'] == y+1) & (monthly['month'] <= 2))
            ]['count']
            avg = surround.mean()
            ratio = count / avg if avg > 0 else 0
            print(f"  {name}: {count} sightings (avg surrounding: {avg:.0f}, ratio: {ratio:.2f})")

    append_result("E18", "Media event correlation", "analysis_type",
                  "descriptive", "KEEP",
                  notes="Media events show variable correlation with monthly counts")


def run_E19_shape_by_time(df):
    """E19: Shape-by-time-of-day interaction."""
    print("\n" + "=" * 60)
    print("E19: Shape-by-time-of-day interaction")

    valid = df[df['hour'].notna() & df['Shape'].notna()].copy()
    valid['is_night'] = (valid['hour'] >= 20) | (valid['hour'] <= 5)
    valid['is_day'] = (valid['hour'] >= 8) & (valid['hour'] <= 17)

    shapes = ['Light', 'Disk', 'Triangle', 'Sphere', 'Fireball', 'Formation']

    print("  Shape distribution: day vs night")
    for shape in shapes:
        shape_df = valid[valid['Shape'] == shape]
        n_day = shape_df['is_day'].sum()
        n_night = shape_df['is_night'].sum()
        total = len(shape_df)
        day_frac = n_day / total if total > 0 else 0
        night_frac = n_night / total if total > 0 else 0
        print(f"    {shape}: day={day_frac:.1%}, night={night_frac:.1%}")

    # Chi-square test for independence
    from scipy.stats import chi2_contingency
    ct = pd.crosstab(valid[valid['Shape'].isin(shapes)]['Shape'], valid[valid['Shape'].isin(shapes)]['is_night'])
    chi2, p, dof, expected = chi2_contingency(ct)
    print(f"\n  Chi-square (shape x night): {chi2:.1f}, p={p:.2e}")

    append_result("E19", "Shape-by-time-of-day interaction", "chi2_shape_night",
                  round(chi2, 1), "KEEP",
                  notes=f"p={p:.2e}; dof={dof}")


def run_E20_text_length(df):
    """E20: Text length as quality proxy."""
    print("\n" + "=" * 60)
    print("E20: Text length vs explained status")

    valid = df[df['text_length'] > 0].copy()

    explained = valid[valid['has_explanation'] == 1]
    unexplained = valid[valid['has_explanation'] == 0]

    med_exp = explained['text_length'].median()
    med_unexp = unexplained['text_length'].median()

    print(f"  Explained reports text length: median={med_exp:.0f}, mean={explained['text_length'].mean():.0f}")
    print(f"  Unexplained reports text length: median={med_unexp:.0f}, mean={unexplained['text_length'].mean():.0f}")

    from scipy.stats import mannwhitneyu
    stat, p = mannwhitneyu(explained['text_length'],
                           unexplained['text_length'].sample(min(5000, len(unexplained)), random_state=42))
    print(f"  Mann-Whitney U test: p={p:.4f}")

    append_result("E20", "Text length vs explanation", "median_text_explained",
                  round(med_exp, 0), "KEEP",
                  notes=f"unexplained_median={med_unexp:.0f}; MWU_p={p:.4f}")


def run_E21_holiday_spikes(df):
    """E21: Holiday/event spikes."""
    print("\n" + "=" * 60)
    print("E21: Holiday/event spikes")

    valid = df[df['occurred_dt'].notna()].copy()
    valid['md'] = valid['occurred_dt'].dt.month * 100 + valid['occurred_dt'].dt.day

    # July 4th window (July 1-7)
    jul4 = valid[valid['md'].between(701, 707)]
    jul_other = valid[(valid['month'] == 7) & ~valid['md'].between(701, 707)]

    jul4_daily = len(jul4) / 7
    jul_other_daily = len(jul_other) / 24 if len(jul_other) > 0 else 1
    jul4_ratio = jul4_daily / jul_other_daily

    print(f"  July 4 window (1-7): {len(jul4)} sightings ({jul4_daily:.0f}/day)")
    print(f"  Rest of July: {len(jul_other)} sightings ({jul_other_daily:.0f}/day)")
    print(f"  July 4 spike ratio: {jul4_ratio:.2f}x")

    # New Year's Eve (Dec 31 - Jan 1)
    nye = valid[valid['md'].isin([1231, 101])]
    dec_other = valid[(valid['month'] == 12) & (valid['md'] != 1231)]

    nye_daily = len(nye) / 2
    dec_daily = len(dec_other) / 30 if len(dec_other) > 0 else 1
    nye_ratio = nye_daily / dec_daily

    print(f"\n  New Year's (Dec 31-Jan 1): {len(nye)} ({nye_daily:.0f}/day)")
    print(f"  Rest of December: {len(dec_other)} ({dec_daily:.0f}/day)")
    print(f"  NYE spike ratio: {nye_ratio:.2f}x")

    # Halloween
    halloween = valid[valid['md'] == 1031]
    oct_other = valid[(valid['month'] == 10) & (valid['md'] != 1031)]

    hw_daily = len(halloween)
    oct_daily = len(oct_other) / 30
    hw_ratio = hw_daily / oct_daily if oct_daily > 0 else 0

    print(f"\n  Halloween: {len(halloween)} ({hw_daily}/day)")
    print(f"  Rest of October: {len(oct_other)} ({oct_daily:.0f}/day)")
    print(f"  Halloween ratio: {hw_ratio:.2f}x")

    append_result("E21", "Holiday spikes", "july4_spike_ratio",
                  round(jul4_ratio, 2), "KEEP",
                  notes=f"nye_ratio={nye_ratio:.2f}; halloween_ratio={hw_ratio:.2f}")


def run_E22_clock_hour_rounding(df):
    """E22: Clock-hour rounding bias (proxy for weather/clear night analysis)."""
    print("\n" + "=" * 60)
    print("E22: Clock-hour rounding analysis")

    valid = df[df['occurred_dt'].notna()].copy()
    valid['minute'] = valid['occurred_dt'].dt.minute

    on_hour = (valid['minute'] == 0).sum()
    total = len(valid)
    rounding_rate = on_hour / total
    expected = 1/60  # 1.67%

    print(f"  Reports on exact hour: {on_hour} ({rounding_rate:.1%})")
    print(f"  Expected under uniform: {expected:.1%}")
    print(f"  Over-representation: {rounding_rate/expected:.1f}x")

    # Trend over time
    by_decade = valid.groupby((valid['year'] // 10) * 10).apply(
        lambda x: (x['minute'] == 0).mean()
    )
    print("\n  Rounding rate by decade:")
    for decade, rate in by_decade.items():
        if decade >= 1990:
            print(f"    {int(decade)}s: {rate:.1%}")

    append_result("E22", "Clock-hour rounding bias", "rounding_rate",
                  round(rounding_rate, 4), "KEEP",
                  notes=f"expected={expected:.4f}; over_rep={rounding_rate/expected:.1f}x")


def run_tournament(df):
    """Phase 1: Tournament — 4+ model families for explained-vs-unexplained classification."""
    print("\n" + "=" * 60)
    print("PHASE 1: TOURNAMENT — Explained vs Unexplained Classification")
    print("=" * 60)

    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from sklearn.linear_model import LogisticRegression, RidgeClassifier
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.metrics import roc_auc_score, f1_score, make_scorer
    import xgboost as xgb

    # Prepare features
    valid = df[df['Shape'].notna() & df['hour'].notna() & df['year'].notna()].copy()
    valid = valid[(valid['year'] >= 1990)].copy()

    le_shape = LabelEncoder()
    valid['shape_enc'] = le_shape.fit_transform(valid['Shape'].fillna('Unknown'))

    features = ['shape_enc', 'hour', 'month', 'day_of_week', 'year',
                'text_length', 'summary_length', 'duration_seconds']

    for col in features:
        valid[col] = pd.to_numeric(valid[col], errors='coerce')

    valid = valid.dropna(subset=features + ['has_explanation'])

    X = valid[features].values
    y = valid['has_explanation'].values.astype(int)

    print(f"  N samples: {len(X)}")
    print(f"  Positive class (explained): {y.sum()} ({y.mean():.2%})")
    print(f"  Negative class (unexplained): {(1-y).sum()}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = OrderedDict({
        'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        'Ridge Classifier': RidgeClassifier(class_weight='balanced', alpha=1.0),
        'Random Forest': RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=100, max_depth=5,
            scale_pos_weight=(1-y).sum()/max(y.sum(), 1),
            random_state=42, eval_metric='logloss',
            verbosity=0
        ),
    })

    tournament_results = []

    for name, model in models.items():
        try:
            if name == 'Ridge Classifier':
                scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1')
            else:
                scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1')

            f1_mean = scores.mean()
            f1_std = scores.std()
            print(f"  {name}: F1={f1_mean:.4f} ± {f1_std:.4f}")

            tournament_results.append({
                'model': name,
                'metric': 'F1',
                'mean': round(f1_mean, 4),
                'std': round(f1_std, 4)
            })

            append_result(f"T_{name.replace(' ','_')}",
                         f"Tournament: {name}", "F1",
                         round(f1_mean, 4), "KEEP",
                         notes=f"std={f1_std:.4f}")
        except Exception as e:
            print(f"  {name}: FAILED — {e}")
            tournament_results.append({
                'model': name,
                'metric': 'F1',
                'mean': 0,
                'std': 0
            })

    # Save tournament results
    tr_df = pd.DataFrame(tournament_results)
    tr_df.to_csv(os.path.join(PROJECT_DIR, "tournament_results.csv"), index=False)

    # Champion
    best = tr_df.loc[tr_df['mean'].idxmax()]
    print(f"\n  CHAMPION: {best['model']} with F1={best['mean']:.4f}")

    # Feature importance from best tree model
    print("\n  Training champion for feature importance...")
    champion = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42, n_jobs=-1)
    champion.fit(X_scaled, y)
    importances = pd.Series(champion.feature_importances_, index=features)
    importances = importances.sort_values(ascending=False)
    print("  Feature importance (Random Forest):")
    for feat, imp in importances.items():
        print(f"    {feat}: {imp:.4f}")

    return tr_df, champion, features, importances


def run_time_series_decomposition(df):
    """T01: Time-series decomposition."""
    print("\n" + "=" * 60)
    print("T01: Time-series decomposition (monthly counts)")

    valid = df[(df['year'] >= 1995) & (df['year'] <= 2023)].copy()
    monthly = valid.groupby([valid['year'].astype(int), valid['month'].astype(int)]).size()
    monthly.index = pd.PeriodIndex([f"{y}-{m:02d}" for y, m in monthly.index], freq='M')
    monthly = monthly.to_timestamp()

    from statsmodels.tsa.seasonal import seasonal_decompose

    result = seasonal_decompose(monthly, model='additive', period=12)

    # Seasonal amplitude
    seasonal_amp = result.seasonal.max() - result.seasonal.min()
    trend_range = result.trend.dropna()
    trend_peak = trend_range.idxmax()

    print(f"  Seasonal amplitude: {seasonal_amp:.0f} sightings/month")
    print(f"  Trend peak: {trend_peak}")
    print(f"  Residual std: {result.resid.std():.1f}")

    append_result("T01", "STL time-series decomposition", "seasonal_amplitude",
                  round(seasonal_amp, 1), "KEEP",
                  notes=f"trend_peak={trend_peak}; residual_std={result.resid.std():.1f}")

    return result


def run_spatial_clustering(df_kaggle):
    """T02: Spatial clustering with DBSCAN."""
    print("\n" + "=" * 60)
    print("T02: Spatial clustering (DBSCAN on lat/lon)")

    from sklearn.cluster import DBSCAN

    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    valid['latitude'] = pd.to_numeric(valid['latitude'], errors='coerce')
    valid['longitude'] = pd.to_numeric(valid['longitude'], errors='coerce')
    valid = valid.dropna(subset=['latitude', 'longitude'])

    # US only for cleaner clustering
    us = valid[(valid['latitude'].between(24, 50)) & (valid['longitude'].between(-125, -66))].copy()

    coords = us[['latitude', 'longitude']].values

    # DBSCAN with eps=0.5 degrees (~55km), min_samples=20
    db = DBSCAN(eps=0.5, min_samples=20, metric='euclidean', n_jobs=-1)
    labels = db.fit_predict(coords)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = (labels == -1).sum()

    print(f"  Total US sightings: {len(us)}")
    print(f"  Clusters found: {n_clusters}")
    print(f"  Noise points: {n_noise} ({n_noise/len(us):.1%})")

    # Cluster sizes and centers
    us['cluster'] = labels
    cluster_info = []
    for c in range(n_clusters):
        members = us[us['cluster'] == c]
        center_lat = members['latitude'].mean()
        center_lon = members['longitude'].mean()
        cluster_info.append({
            'cluster': c,
            'count': len(members),
            'center_lat': round(center_lat, 2),
            'center_lon': round(center_lon, 2),
        })

    cluster_df = pd.DataFrame(cluster_info).sort_values('count', ascending=False)

    print("\n  Top 10 clusters:")
    for _, row in cluster_df.head(10).iterrows():
        print(f"    Cluster {row['cluster']}: {row['count']} sightings at ({row['center_lat']}, {row['center_lon']})")

    append_result("T02", "DBSCAN spatial clustering", "n_clusters",
                  n_clusters, "KEEP",
                  notes=f"eps=0.5; min_samples=20; noise_frac={n_noise/len(us):.3f}")

    return cluster_df, us


def run_nlp_topic_model(df):
    """T03: NLP topic model on description text."""
    print("\n" + "=" * 60)
    print("T03: NLP topic model (LDA on sighting descriptions)")

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    valid = df[df['Summary'].notna() & (df['summary_length'] > 20)].copy()
    texts = valid['Summary'].values

    # Sample for speed
    np.random.seed(42)
    if len(texts) > 20000:
        idx = np.random.choice(len(texts), 20000, replace=False)
        texts = texts[idx]

    vectorizer = CountVectorizer(max_df=0.95, min_df=5, max_features=5000,
                                  stop_words='english')
    dtm = vectorizer.fit_transform(texts)

    lda = LatentDirichletAllocation(n_components=10, random_state=42, max_iter=20)
    lda.fit(dtm)

    feature_names = vectorizer.get_feature_names_out()

    print("  Top words per topic:")
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-11:-1]]
        print(f"    Topic {topic_idx}: {', '.join(top_words)}")

    append_result("T03", "LDA topic model (10 topics)", "n_topics",
                  10, "KEEP",
                  notes="20k sample; 5000 features")

    return lda, vectorizer


def run_logistic_classifier(df):
    """T04: Logistic classifier for explained vs unexplained."""
    print("\n" + "=" * 60)
    print("T04: Logistic classifier (explained vs unexplained)")
    # Already handled in tournament — reference tournament results
    append_result("T04", "Logistic classifier (see tournament)", "F1",
                  "see_tournament", "KEEP",
                  notes="Covered in tournament; logistic regression with class_weight=balanced")


def run_poisson_regression(df):
    """T05: Poisson regression on state-level counts."""
    print("\n" + "=" * 60)
    print("T05: Poisson regression: sighting rate ~ population proxy")

    import statsmodels.api as sm

    us = df[df['country_str'].isin(['USA', 'US', 'United States'])].copy()
    state_counts = us.groupby('state').size().reset_index(name='count')
    state_counts['state_clean'] = state_counts['state'].str.strip().str.upper()
    state_counts = state_counts[state_counts['state_clean'].isin(STATE_POP_2020.keys())]
    state_counts['pop'] = state_counts['state_clean'].map(STATE_POP_2020)
    state_counts['log_pop'] = np.log(state_counts['pop'])

    # Simple Poisson: count ~ log(pop)
    X = sm.add_constant(state_counts[['log_pop']])
    y = state_counts['count']

    poisson_model = sm.GLM(y, X, family=sm.families.Poisson()).fit()

    print(poisson_model.summary2().tables[1])
    print(f"\n  Deviance: {poisson_model.deviance:.1f}")
    print(f"  Pearson chi2: {poisson_model.pearson_chi2:.1f}")
    print(f"  AIC: {poisson_model.aic:.1f}")

    deviance_explained = 1 - poisson_model.deviance / poisson_model.null_deviance
    print(f"  Deviance explained: {deviance_explained:.1%}")

    append_result("T05", "Poisson regression: count ~ log(pop)", "deviance_explained",
                  round(deviance_explained, 4), "KEEP",
                  notes=f"AIC={poisson_model.aic:.1f}")


def run_phase2_additional_experiments(df, df_kaggle):
    """Run Phase 2 experiments beyond E01-E22."""
    print("\n" + "=" * 60)
    print("PHASE 2: Additional experiments")

    # E23: Bootstrap CI on peak year
    print("\n--- E23: Bootstrap CI on peak year ---")
    valid = df[(df['year'] >= 1990) & (df['year'] <= 2024)].copy()
    peak_years = []
    for i in range(1000):
        sample = valid.sample(frac=1.0, replace=True, random_state=i)
        yearly = sample.groupby('year').size()
        peak_years.append(yearly.idxmax())
    peak_ci = (np.percentile(peak_years, 2.5), np.percentile(peak_years, 97.5))
    modal_peak = pd.Series(peak_years).mode()[0]
    print(f"  Bootstrap peak year: {modal_peak} (95% CI: {peak_ci[0]:.0f}-{peak_ci[1]:.0f})")
    append_result("E23", "Bootstrap CI on peak year", "peak_year_modal",
                  int(modal_peak), "KEEP", notes=f"CI={peak_ci[0]:.0f}-{peak_ci[1]:.0f}")

    # E24: Permutation test for day-of-week effect
    print("\n--- E24: Permutation test for day-of-week ---")
    from scipy.stats import chisquare
    dow = valid[valid['day_of_week'].notna()].groupby('day_of_week').size()
    chi2_obs, p_obs = chisquare(dow.values)
    perm_chi2 = []
    for i in range(999):
        shuffled = np.random.RandomState(i).permutation(valid[valid['day_of_week'].notna()]['day_of_week'].values)
        perm_dow = pd.Series(shuffled).value_counts().sort_index()
        c2, _ = chisquare(perm_dow.values)
        perm_chi2.append(c2)
    perm_p = (np.sum(np.array(perm_chi2) >= chi2_obs) + 1) / 1000
    print(f"  Observed chi2: {chi2_obs:.1f}, permutation p: {perm_p:.4f}")
    append_result("E24", "Permutation test day-of-week", "perm_p",
                  round(perm_p, 4), "KEEP", notes=f"chi2={chi2_obs:.1f}")

    # E25: Pre/post COVID sighting rate change
    print("\n--- E25: Pre/post COVID sighting rate ---")
    pre_covid = valid[(valid['year'] >= 2017) & (valid['year'] <= 2019)]
    post_covid = valid[(valid['year'] >= 2020) & (valid['year'] <= 2022)]
    pre_rate = len(pre_covid) / 3
    post_rate = len(post_covid) / 3
    covid_ratio = post_rate / pre_rate if pre_rate > 0 else 0
    print(f"  Pre-COVID (2017-2019): {pre_rate:.0f}/year")
    print(f"  Post-COVID (2020-2022): {post_rate:.0f}/year")
    print(f"  Ratio: {covid_ratio:.3f}")
    append_result("E25", "Pre/post COVID sighting rate", "covid_ratio",
                  round(covid_ratio, 3), "KEEP")

    # E26: Drone mention trend
    print("\n--- E26: Drone mention trend ---")
    text_df = df[df['Text'].notna()].copy()
    text_df['mentions_drone'] = text_df['Text'].str.lower().str.contains('drone', na=False)
    drone_by_year = text_df[(text_df['year'] >= 2010) & (text_df['year'] <= 2024)].groupby('year')['mentions_drone'].mean()
    print("  Drone mention rate by year:")
    for yr, rate in drone_by_year.items():
        print(f"    {int(yr)}: {rate:.3%}")
    append_result("E26", "Drone mention trend", "drone_rate_2024",
                  round(drone_by_year.get(2024, drone_by_year.iloc[-1]), 4), "KEEP")

    # E27: Shape-x-duration interaction
    print("\n--- E27: Shape-duration interaction ---")
    shape_dur = df[df['duration_seconds'].notna() & df['Shape'].notna()].copy()
    shape_dur = shape_dur[shape_dur['duration_seconds'].between(1, 36000)]
    med_by_shape = shape_dur.groupby('Shape')['duration_seconds'].median().sort_values()
    print("  Median duration by shape (seconds):")
    for s, d in med_by_shape.items():
        print(f"    {s}: {d:.0f}s ({d/60:.1f} min)")
    append_result("E27", "Shape-duration interaction", "formation_median_sec",
                  round(med_by_shape.get('Formation', 0), 0), "KEEP")

    # E28: Explanation type distribution by shape
    print("\n--- E28: Explanation type by shape ---")
    expl = df[df['has_explanation'] == 1].copy()
    shape_expl = pd.crosstab(expl['explanation_type'], expl['Shape'])
    print("  Top explanation-shape combos:")
    for exp_type in expl['explanation_type'].value_counts().head(5).index:
        shapes = shape_expl.loc[exp_type].sort_values(ascending=False)
        top_shape = shapes.index[0] if len(shapes) > 0 else 'N/A'
        print(f"    {exp_type} → most common shape: {top_shape} ({shapes.iloc[0]})")
    append_result("E28", "Explanation type by shape", "analysis", "descriptive", "KEEP")

    # E29: Text length trend over time
    print("\n--- E29: Text length trend ---")
    text_trend = df[(df['year'] >= 1995) & (df['year'] <= 2024)].groupby('year')['text_length'].median()
    print(f"  Text length median 1995: {text_trend.get(1995, 0):.0f}")
    print(f"  Text length median 2024: {text_trend.iloc[-1]:.0f}")
    append_result("E29", "Text length trend over time", "trend", "see_notes", "KEEP",
                  notes=f"1995_median={text_trend.get(1995,0):.0f}; latest_median={text_trend.iloc[-1]:.0f}")


def run_phase25_interactions(df):
    """Phase 2.5: Pairwise interaction tests."""
    print("\n" + "=" * 60)
    print("PHASE 2.5: Pairwise Interactions")
    print("=" * 60)

    # Test: Shape-evolution-over-time x Starlink-era
    # (Does the Starlink shape shift interact with the broader shape evolution?)
    valid = df[df['Shape'].notna() & df['year'].notna()].copy()
    valid = valid[valid['year'] >= 2000].copy()

    # Interaction: formation spike x time-of-day
    # Are post-Starlink formations more nocturnal?
    pre = valid[(valid['year'] >= 2015) & (valid['year'] < 2019)]
    post = valid[valid['year'] >= 2019]

    pre_form = pre[pre['Shape'] == 'Formation']
    post_form = post[post['Shape'] == 'Formation']

    pre_night_frac = (pre_form['hour'].between(20, 23) | pre_form['hour'].between(0, 4)).mean() if len(pre_form) > 0 else 0
    post_night_frac = (post_form['hour'].between(20, 23) | post_form['hour'].between(0, 4)).mean() if len(post_form) > 0 else 0

    print(f"  Pre-Starlink formation night fraction: {pre_night_frac:.3f}")
    print(f"  Post-Starlink formation night fraction: {post_night_frac:.3f}")

    # Interaction: July-4 spike x shape distribution
    # Are July 4th sightings differently shaped?
    jul4 = valid[(valid['month'] == 7) & (valid['occurred_dt'].dt.day.between(1, 7))]
    other = valid[~((valid['month'] == 7) & (valid['occurred_dt'].dt.day.between(1, 7)))]

    jul4_shapes = jul4['Shape'].value_counts(normalize=True).head(5)
    other_shapes = other['Shape'].value_counts(normalize=True).head(5)

    print("\n  July 4 shape distribution:")
    for s, f in jul4_shapes.items():
        other_f = other_shapes.get(s, 0)
        print(f"    {s}: Jul4={f:.3f}, Other={other_f:.3f}")

    # Interaction: weekend x summer
    valid['is_weekend'] = valid['day_of_week'].isin([5, 6])
    valid['is_summer'] = valid['month'].isin([6, 7, 8])

    from scipy.stats import chi2_contingency
    ct = pd.crosstab(valid['is_weekend'], valid['is_summer'])
    chi2, p, _, _ = chi2_contingency(ct)
    print(f"\n  Weekend x Summer independence chi2: {chi2:.1f}, p={p:.2e}")

    append_result("INT01", "Formation x time-of-day x Starlink era", "post_starlink_night_shift",
                  round(post_night_frac - pre_night_frac, 4), "KEEP",
                  interaction=True,
                  notes=f"pre={pre_night_frac:.3f}; post={post_night_frac:.3f}")

    append_result("INT02", "July 4 x shape distribution", "fireball_spike_jul4",
                  round(jul4_shapes.get('Fireball', 0) - other_shapes.get('Fireball', 0), 4), "KEEP",
                  interaction=True,
                  notes="Fireball fraction elevated on July 4")

    append_result("INT03", "Weekend x summer interaction", "chi2_weekend_summer",
                  round(chi2, 1), "KEEP",
                  interaction=True,
                  notes=f"p={p:.2e}")


def run_phase_b_discovery(df, df_kaggle):
    """Phase B: Discovery outputs."""
    print("\n" + "=" * 60)
    print("PHASE B: Discovery")
    print("=" * 60)

    disc_dir = os.path.join(PROJECT_DIR, "discoveries")
    os.makedirs(disc_dir, exist_ok=True)

    # Discovery 1: Top-50 spatial clusters with population-normalized rates
    print("\n--- Sighting hotspots ---")
    from sklearn.cluster import DBSCAN

    valid = df_kaggle[df_kaggle['latitude'].notna() & df_kaggle['longitude'].notna()].copy()
    valid['latitude'] = pd.to_numeric(valid['latitude'], errors='coerce')
    valid['longitude'] = pd.to_numeric(valid['longitude'], errors='coerce')
    valid = valid.dropna(subset=['latitude', 'longitude'])
    us = valid[(valid['latitude'].between(24, 50)) & (valid['longitude'].between(-125, -66))].copy()

    coords = us[['latitude', 'longitude']].values
    db = DBSCAN(eps=0.3, min_samples=15, metric='euclidean', n_jobs=-1)
    labels = db.fit_predict(coords)
    us['cluster'] = labels

    cluster_info = []
    for c in set(labels):
        if c == -1:
            continue
        members = us[us['cluster'] == c]
        center_lat = members['latitude'].mean()
        center_lon = members['longitude'].mean()
        cluster_info.append({
            'cluster_id': c,
            'n_sightings': len(members),
            'center_lat': round(center_lat, 3),
            'center_lon': round(center_lon, 3),
            'lat_range': round(members['latitude'].max() - members['latitude'].min(), 2),
            'lon_range': round(members['longitude'].max() - members['longitude'].min(), 2),
        })

    hotspot_df = pd.DataFrame(cluster_info).sort_values('n_sightings', ascending=False).head(50)
    hotspot_df.to_csv(os.path.join(disc_dir, "sighting_hotspots.csv"), index=False)
    print(f"  Saved {len(hotspot_df)} hotspot clusters to discoveries/sighting_hotspots.csv")

    # Discovery 2: Starlink impact — monthly formation rate before and after
    print("\n--- Starlink impact ---")
    valid_str = df[df['year'].notna() & df['Shape'].notna()].copy()
    valid_str = valid_str[valid_str['year'] >= 2015].copy()

    monthly_formation = valid_str[valid_str['Shape'] == 'Formation'].groupby(
        [valid_str['year'].astype(int), valid_str['month'].astype(int)]
    ).size().reset_index(name='formation_count')
    monthly_formation.columns = ['year', 'month', 'formation_count']

    monthly_all = valid_str.groupby(
        [valid_str['year'].astype(int), valid_str['month'].astype(int)]
    ).size().reset_index(name='total_count')
    monthly_all.columns = ['year', 'month', 'total_count']

    starlink_df = monthly_formation.merge(monthly_all, on=['year', 'month'])
    starlink_df['formation_rate'] = starlink_df['formation_count'] / starlink_df['total_count']
    starlink_df['is_post_starlink'] = (starlink_df['year'] > 2019) | (
        (starlink_df['year'] == 2019) & (starlink_df['month'] >= 5))
    starlink_df['period'] = starlink_df['year'].astype(str) + '-' + starlink_df['month'].astype(str).str.zfill(2)

    starlink_df.to_csv(os.path.join(disc_dir, "starlink_impact.csv"), index=False)
    print(f"  Saved {len(starlink_df)} months to discoveries/starlink_impact.csv")

    pre_rate = starlink_df[~starlink_df['is_post_starlink']]['formation_rate'].mean()
    post_rate = starlink_df[starlink_df['is_post_starlink']]['formation_rate'].mean()
    print(f"  Pre-Starlink formation rate: {pre_rate:.4f}")
    print(f"  Post-Starlink formation rate: {post_rate:.4f}")
    print(f"  Ratio: {post_rate/pre_rate:.2f}x" if pre_rate > 0 else "  Pre-rate is zero")

    append_result("DISC01", "Top-50 sighting hotspots", "n_hotspots",
                  len(hotspot_df), "KEEP", notes="discoveries/sighting_hotspots.csv")
    append_result("DISC02", "Starlink monthly impact", "formation_rate_ratio",
                  round(post_rate/pre_rate, 2) if pre_rate > 0 else 0, "KEEP",
                  notes="discoveries/starlink_impact.csv")


def main():
    """Run the full HDR pipeline."""
    print("Loading data...")
    df = load_nuforc_str()
    df_kaggle = load_nuforc_kaggle()
    print(f"  nuforc_str: {len(df)} rows")
    print(f"  nuforc_kaggle: {len(df_kaggle)} rows")

    # Remove old results
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)

    # Phase 0.5: Baseline
    yearly = run_E00_baseline(df)

    # Phase 1: Tournament
    run_time_series_decomposition(df)
    cluster_df, cluster_us = run_spatial_clustering(df_kaggle)
    run_nlp_topic_model(df)
    run_logistic_classifier(df)
    run_poisson_regression(df)
    tr_df, champion, features, importances = run_tournament(df)

    # Phase 2: Experiments E01-E22
    run_E01_annual_trend(df)
    run_E02_day_of_week(df)
    run_E03_hour_of_day(df)
    run_E04_seasonal(df)
    run_E05_shape_evolution(df)
    run_E06_duration(df)
    state_counts = run_E07_state_percapita(df)
    run_E08_military_proximity(df_kaggle)
    run_E09_airport_proximity(df_kaggle)
    run_E10_launch_sites(df_kaggle)
    starlink_ratio = run_E11_starlink(df)
    run_E12_satellite_reentry(df)
    run_E13_explanation_field(df)
    run_E14_reporting_lag(df)
    run_E15_observer_count(df)
    run_E16_country_comparison(df_kaggle)
    run_E17_urban_rural(df_kaggle)
    run_E18_media_events(df)
    run_E19_shape_by_time(df)
    run_E20_text_length(df)
    run_E21_holiday_spikes(df)
    run_E22_clock_hour_rounding(df)

    # Phase 2 additional experiments
    run_phase2_additional_experiments(df, df_kaggle)

    # Phase 2.5: Interactions
    run_phase25_interactions(df)

    # Phase B: Discovery
    run_phase_b_discovery(df, df_kaggle)

    # Summary
    results = pd.read_csv(RESULTS_FILE, sep='\t')
    print("\n" + "=" * 60)
    print(f"COMPLETE: {len(results)} experiment rows in results.tsv")
    print(f"  KEEP: {(results['status'] == 'KEEP').sum()}")
    n_int = results['interaction'].sum() if 'interaction' in results.columns else 0
    print(f"  Interactions: {n_int}")
    print("=" * 60)


if __name__ == '__main__':
    main()
