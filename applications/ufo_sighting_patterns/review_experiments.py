#!/usr/bin/env python3
"""
Phase 2.75 mandated experiments (E30-E34).
Addresses issues raised in paper_review.md blind review.
"""
import pandas as pd
import numpy as np
import os
import sys
import warnings

warnings.filterwarnings('ignore')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from run_experiments import append_result, STATE_POP_2020

# US internet adoption (% population) from World Bank IT.NET.USER.ZS
US_INTERNET_PCT = {
    1990: 0.79, 1991: 1.16, 1992: 1.72, 1993: 2.27, 1994: 4.86,
    1995: 9.24, 1996: 16.40, 1997: 21.60, 1998: 30.10, 1999: 35.80,
    2000: 43.08, 2001: 49.08, 2002: 58.79, 2003: 61.70, 2004: 64.76,
    2005: 67.97, 2006: 68.93, 2007: 75.00, 2008: 74.00, 2009: 71.00,
    2010: 71.69, 2011: 69.73, 2012: 74.70, 2013: 71.40, 2014: 73.00,
    2015: 74.55, 2016: 85.54, 2017: 87.27, 2018: 88.50, 2019: 89.43,
    2020: 90.34, 2021: 91.27, 2022: 92.73, 2023: 93.53, 2024: 94.69,
}


def run_E30_internet_correlation(df):
    """E30: Correlate annual sighting counts with US internet adoption.

    Tests the claim that sighting volume growth 'mirrors internet adoption'.
    Uses World Bank data (IT.NET.USER.ZS) for US internet usage %.
    Computes Pearson correlation for the growth phase (1990-2014).
    """
    from scipy.stats import pearsonr, spearmanr

    print("\n" + "=" * 60)
    print("E30: Internet adoption correlation")

    yearly = df[(df['year'] >= 1990) & (df['year'] <= 2024)].groupby('year').size()

    # Growth phase: 1990-2014
    growth_years = range(1990, 2015)
    sighting_counts = [yearly.get(y, 0) for y in growth_years]
    internet_pcts = [US_INTERNET_PCT.get(y, np.nan) for y in growth_years]

    # Remove any NaN pairs
    valid = [(s, i) for s, i in zip(sighting_counts, internet_pcts) if not np.isnan(i)]
    s_vals = [v[0] for v in valid]
    i_vals = [v[1] for v in valid]

    r_growth, p_growth = pearsonr(s_vals, i_vals)
    rho_growth, p_rho = spearmanr(s_vals, i_vals)

    print(f"  Growth phase 1990-2014:")
    print(f"    Pearson r = {r_growth:.4f}, p = {p_growth:.2e}")
    print(f"    Spearman rho = {rho_growth:.4f}, p = {p_rho:.2e}")

    # Full period 1990-2024: divergence expected post-2014
    all_years = range(1990, 2025)
    s_all = [yearly.get(y, 0) for y in all_years]
    i_all = [US_INTERNET_PCT.get(y, np.nan) for y in all_years]
    valid_all = [(s, i) for s, i in zip(s_all, i_all) if not np.isnan(i)]
    s_full = [v[0] for v in valid_all]
    i_full = [v[1] for v in valid_all]

    r_full, p_full = pearsonr(s_full, i_full)

    print(f"  Full period 1990-2024:")
    print(f"    Pearson r = {r_full:.4f}, p = {p_full:.2e}")
    print(f"    (Divergence post-2014 expected to weaken correlation)")

    append_result("E30", "Internet adoption correlation (growth 1990-2014)",
                  "pearson_r", round(r_growth, 4), "KEEP",
                  notes=f"p={p_growth:.2e}; spearman_rho={rho_growth:.4f}; full_period_r={r_full:.4f}")

    return {
        'pearson_r': r_growth,
        'p_value': p_growth,
        'spearman_rho': rho_growth,
        'full_period_r': r_full,
    }


def run_E31_starlink_its(df):
    """E31: Interrupted time series for Starlink formation effect.

    Tests whether post-Starlink formation fraction shift is significant
    after controlling for pre-existing trend. Reports both absolute and
    fractional rates.
    """
    import statsmodels.api as sm

    print("\n" + "=" * 60)
    print("E31: Starlink interrupted time series")

    valid = df[df['year'].notna() & df['Shape'].notna()].copy()
    valid = valid[valid['year'] >= 2015].copy()

    # Build monthly series
    monthly = valid.groupby([valid['year'].astype(int), valid['month'].astype(int)]).agg(
        total=('Shape', 'size'),
        formation=('Shape', lambda x: (x == 'Formation').sum())
    ).reset_index()
    monthly.columns = ['year', 'month', 'total', 'formation']
    monthly['formation_frac'] = monthly['formation'] / monthly['total']
    monthly['formation_rate'] = monthly['formation']  # absolute count per month

    # Time index (months since start)
    monthly = monthly.sort_values(['year', 'month']).reset_index(drop=True)
    monthly['t'] = range(len(monthly))

    # Starlink intervention: May 2019
    monthly['post_starlink'] = ((monthly['year'] > 2019) |
                                 ((monthly['year'] == 2019) & (monthly['month'] >= 5))).astype(int)
    monthly['t_post'] = monthly['t'] * monthly['post_starlink']

    # ITS model: fraction ~ t + post_starlink + t_post
    X = sm.add_constant(monthly[['t', 'post_starlink', 't_post']])
    y = monthly['formation_frac']

    model = sm.OLS(y, X).fit()

    print(f"  ITS model: formation_fraction ~ time + post_starlink + time*post_starlink")
    print(model.summary2().tables[1])
    print(f"\n  R-squared: {model.rsquared:.4f}")

    intercept_shift = model.params['post_starlink']
    intercept_p = model.pvalues['post_starlink']
    slope_change = model.params['t_post']
    slope_p = model.pvalues['t_post']

    print(f"\n  Intercept shift (post-Starlink): {intercept_shift:.4f}, p={intercept_p:.4f}")
    print(f"  Slope change (post-Starlink): {slope_change:.6f}, p={slope_p:.4f}")

    # Compute absolute and fractional rate ratios
    pre = monthly[monthly['post_starlink'] == 0]
    post = monthly[monthly['post_starlink'] == 1]

    abs_pre = pre['formation'].sum() / len(pre)
    abs_post = post['formation'].sum() / len(post)
    frac_pre = pre['formation_frac'].mean()
    frac_post = post['formation_frac'].mean()

    abs_ratio = abs_post / abs_pre if abs_pre > 0 else 0
    frac_ratio = frac_post / frac_pre if frac_pre > 0 else 0

    print(f"\n  Absolute formation rate: pre={abs_pre:.1f}/mo, post={abs_post:.1f}/mo, ratio={abs_ratio:.2f}x")
    print(f"  Fractional formation rate: pre={frac_pre:.4f}, post={frac_post:.4f}, ratio={frac_ratio:.2f}x")

    append_result("E31", "Starlink ITS (formation fraction)",
                  "intercept_shift_p", round(intercept_p, 4), "KEEP",
                  notes=f"shift={intercept_shift:.4f}; abs_ratio={abs_ratio:.2f}; frac_ratio={frac_ratio:.2f}")

    return {
        'intercept_shift': intercept_shift,
        'intercept_shift_pvalue': intercept_p,
        'slope_change': slope_change,
        'slope_change_pvalue': slope_p,
        'absolute_rate_ratio': abs_ratio,
        'fractional_rate_ratio': frac_ratio,
        'r_squared': model.rsquared,
    }


def run_E32_overdispersion(df):
    """E32: Negative binomial vs Poisson for state-level counts.

    Tests whether state-level sighting counts are overdispersed and
    whether Poisson standard errors are valid.
    """
    import statsmodels.api as sm

    print("\n" + "=" * 60)
    print("E32: Overdispersion diagnostic (Poisson vs NB)")

    us = df[df['country_str'].isin(['USA', 'US', 'United States'])].copy()
    state_counts = us.groupby('state').size().reset_index(name='count')
    state_counts['state_clean'] = state_counts['state'].str.strip().str.upper()
    state_counts = state_counts[state_counts['state_clean'].isin(STATE_POP_2020.keys())]
    state_counts['pop'] = state_counts['state_clean'].map(STATE_POP_2020)
    state_counts['log_pop'] = np.log(state_counts['pop'])

    X = sm.add_constant(state_counts[['log_pop']])
    y = state_counts['count']

    # Poisson
    poisson = sm.GLM(y, X, family=sm.families.Poisson()).fit()
    poisson_aic = poisson.aic
    poisson_dev = poisson.deviance
    poisson_pearson = poisson.pearson_chi2
    n = len(y)
    p_params = len(poisson.params)
    dispersion_ratio = poisson_pearson / (n - p_params)

    print(f"  Poisson model:")
    print(f"    AIC = {poisson_aic:.1f}")
    print(f"    Deviance = {poisson_dev:.1f}")
    print(f"    Pearson chi2 = {poisson_pearson:.1f}")
    print(f"    Dispersion ratio (Pearson chi2 / df) = {dispersion_ratio:.1f}")
    print(f"    log(pop) coefficient = {poisson.params['log_pop']:.4f}")
    print(f"    log(pop) z-score = {poisson.tvalues['log_pop']:.1f}")

    # Negative binomial
    nb = sm.GLM(y, X, family=sm.families.NegativeBinomial()).fit()
    nb_aic = nb.aic
    nb_coef = nb.params['log_pop']
    nb_se = nb.bse['log_pop']
    nb_z = nb.tvalues['log_pop']

    print(f"\n  Negative Binomial model:")
    print(f"    AIC = {nb_aic:.1f}")
    print(f"    log(pop) coefficient = {nb_coef:.4f} (SE={nb_se:.4f})")
    print(f"    log(pop) z-score = {nb_z:.1f}")

    print(f"\n  Comparison:")
    print(f"    AIC difference (Poisson - NB) = {poisson_aic - nb_aic:.1f}")
    print(f"    Dispersion ratio = {dispersion_ratio:.1f} (>>1 means overdispersed)")
    if dispersion_ratio > 1.5:
        print(f"    OVERDISPERSED: Poisson SEs are underestimated. Use NB model.")
    else:
        print(f"    Dispersion acceptable for Poisson.")

    append_result("E32", "Overdispersion: Poisson vs NB",
                  "dispersion_ratio", round(dispersion_ratio, 1), "KEEP",
                  notes=f"poisson_aic={poisson_aic:.0f}; nb_aic={nb_aic:.0f}; nb_coef={nb_coef:.4f}")

    return {
        'poisson_aic': poisson_aic,
        'nb_aic': nb_aic,
        'dispersion_ratio': dispersion_ratio,
        'nb_coefficient': nb_coef,
        'nb_se': nb_se,
        'nb_z': nb_z,
        'poisson_coefficient': poisson.params['log_pop'],
        'poisson_z': poisson.tvalues['log_pop'],
    }


def run_E33_cultural_indicators(df):
    """E33: Cultural indicator correlation with shape fractions.

    Since Google Ngrams API is not reliably accessible programmatically,
    we use an internal proxy: the fraction of NUFORC report text that
    mentions 'saucer' or 'flying saucer' vs 'orb' as a cultural indicator,
    and correlate with shape fractions over time.
    """
    print("\n" + "=" * 60)
    print("E33: Cultural indicators vs shape fractions")

    valid = df[(df['year'] >= 1995) & (df['year'] <= 2023) &
               df['Shape'].notna() & df['Text'].notna()].copy()

    text_lower = valid['Text'].str.lower()

    yearly_data = []
    for year in range(1995, 2024):
        yr = valid[valid['year'] == year]
        yr_text = text_lower[valid['year'] == year]
        n = len(yr)
        if n < 50:
            continue

        disk_frac = (yr['Shape'] == 'Disk').mean()
        orb_frac = (yr['Shape'] == 'Orb').mean()
        triangle_frac = (yr['Shape'] == 'Triangle').mean()

        saucer_mentions = yr_text.str.contains('saucer|flying saucer', na=False).mean()
        orb_mentions = yr_text.str.contains(r'\borb\b|\borbs\b', na=False).mean()

        yearly_data.append({
            'year': year, 'n': n,
            'disk_frac': disk_frac, 'orb_frac': orb_frac,
            'triangle_frac': triangle_frac,
            'saucer_mention_rate': saucer_mentions,
            'orb_mention_rate': orb_mentions,
        })

    yd = pd.DataFrame(yearly_data)

    from scipy.stats import pearsonr

    # Correlation: saucer mentions vs disk shape fraction
    r_saucer_disk, p_saucer_disk = pearsonr(yd['saucer_mention_rate'], yd['disk_frac'])
    r_orb_orb, p_orb_orb = pearsonr(yd['orb_mention_rate'], yd['orb_frac'])

    print(f"  'Saucer' mention rate vs Disk shape fraction:")
    print(f"    Pearson r = {r_saucer_disk:.4f}, p = {p_saucer_disk:.4f}")
    print(f"  'Orb' mention rate vs Orb shape fraction:")
    print(f"    Pearson r = {r_orb_orb:.4f}, p = {p_orb_orb:.4f}")

    # Trend: saucer mentions declining?
    r_saucer_time, p_saucer_time = pearsonr(yd['year'], yd['saucer_mention_rate'])
    r_orb_time, p_orb_time = pearsonr(yd['year'], yd['orb_mention_rate'])

    print(f"\n  'Saucer' mention trend over time:")
    print(f"    Pearson r = {r_saucer_time:.4f}, p = {p_saucer_time:.4f}")
    print(f"  'Orb' mention trend over time:")
    print(f"    Pearson r = {r_orb_time:.4f}, p = {p_orb_time:.4f}")

    append_result("E33", "Cultural indicators (text mention vs shape)",
                  "saucer_disk_r", round(r_saucer_disk, 4), "KEEP",
                  notes=f"p={p_saucer_disk:.4f}; orb_orb_r={r_orb_orb:.4f}")

    return {
        'flying_saucer_disk_corr': r_saucer_disk,
        'flying_saucer_disk_p': p_saucer_disk,
        'orb_orb_corr': r_orb_orb,
        'orb_orb_p': p_orb_orb,
        'saucer_time_trend_r': r_saucer_time,
        'orb_time_trend_r': r_orb_time,
        'method': 'text_mention_proxy',
    }


def run_E34_state_formation(df):
    """E34: State-level formation analysis for Starlink era.

    Tests whether post-Starlink formation reports concentrate in higher-
    latitude states (better satellite visibility). Uses state field from
    primary dataset (no geocoding needed).
    """
    from scipy.stats import pearsonr

    print("\n" + "=" * 60)
    print("E34: State-level formation analysis (Starlink era)")

    # State centroids (approximate latitude for satellite-viewing proxy)
    STATE_LAT = {
        'AL': 32.8, 'AK': 64.2, 'AZ': 34.0, 'AR': 34.8, 'CA': 36.8,
        'CO': 39.0, 'CT': 41.6, 'DE': 39.0, 'FL': 27.8, 'GA': 32.7,
        'HI': 19.9, 'ID': 44.1, 'IL': 40.6, 'IN': 39.8, 'IA': 42.0,
        'KS': 38.5, 'KY': 37.8, 'LA': 31.2, 'ME': 45.3, 'MD': 39.0,
        'MA': 42.4, 'MI': 44.3, 'MN': 46.4, 'MS': 32.7, 'MO': 38.6,
        'MT': 46.8, 'NE': 41.5, 'NV': 38.8, 'NH': 43.2, 'NJ': 40.1,
        'NM': 34.5, 'NY': 43.0, 'NC': 35.8, 'ND': 47.5, 'OH': 40.4,
        'OK': 35.5, 'OR': 44.0, 'PA': 41.2, 'RI': 41.7, 'SC': 34.0,
        'SD': 44.5, 'TN': 35.5, 'TX': 31.0, 'UT': 39.3, 'VT': 44.0,
        'VA': 37.4, 'WA': 47.4, 'WV': 38.6, 'WI': 44.3, 'WY': 43.0,
        'DC': 38.9,
    }

    us = df[df['country_str'].isin(['USA', 'US', 'United States'])].copy()
    us['state_clean'] = us['state'].str.strip().str.upper()
    us = us[us['state_clean'].isin(STATE_POP_2020.keys())]

    # Post-Starlink formations by state
    post = us[(us['year'] >= 2019) & ((us['year'] > 2019) | (us['month'] >= 5))]
    post_formation = post[post['Shape'] == 'Formation']

    state_formation = post_formation.groupby('state_clean').size().reset_index(name='formation_count')
    state_total = post.groupby('state_clean').size().reset_index(name='total_count')

    state_df = state_formation.merge(state_total, on='state_clean', how='right').fillna(0)
    state_df['formation_frac'] = state_df['formation_count'] / state_df['total_count']
    state_df['pop'] = state_df['state_clean'].map(STATE_POP_2020)
    state_df['latitude'] = state_df['state_clean'].map(STATE_LAT)
    state_df['formation_per_100k'] = state_df['formation_count'] / state_df['pop'] * 100

    state_df = state_df.sort_values('formation_per_100k', ascending=False)

    print("  Top 10 states by post-Starlink formation rate (per 100k):")
    for _, row in state_df.head(10).iterrows():
        print(f"    {row['state_clean']}: {row['formation_per_100k']:.2f}/100k "
              f"({int(row['formation_count'])} formations, lat={row['latitude']:.1f})")

    # Correlation: latitude vs formation fraction
    valid_states = state_df[state_df['total_count'] >= 20]  # minimum sample
    r_lat, p_lat = pearsonr(valid_states['latitude'], valid_states['formation_frac'])

    print(f"\n  Latitude vs formation fraction (n={len(valid_states)} states):")
    print(f"    Pearson r = {r_lat:.4f}, p = {p_lat:.4f}")

    if r_lat > 0:
        print(f"    Higher-latitude states have more formation reports (consistent with satellite visibility)")
    else:
        print(f"    No latitude effect detected")

    top_states = state_df.head(10)[['state_clean', 'formation_per_100k', 'latitude']].to_dict('records')

    append_result("E34", "State-level formation (Starlink era)",
                  "latitude_formation_r", round(r_lat, 4), "KEEP",
                  notes=f"p={p_lat:.4f}; top_state={state_df.iloc[0]['state_clean']}")

    return {
        'top_formation_states': top_states,
        'latitude_correlation': r_lat,
        'latitude_p': p_lat,
        'n_states': len(valid_states),
    }


def run_all_review_experiments(df):
    """Run all Phase 2.75 mandated experiments."""
    results = {}
    results['E30'] = run_E30_internet_correlation(df)
    results['E31'] = run_E31_starlink_its(df)
    results['E32'] = run_E32_overdispersion(df)
    results['E33'] = run_E33_cultural_indicators(df)
    results['E34'] = run_E34_state_formation(df)
    return results


if __name__ == '__main__':
    from data_loader import load_nuforc_str
    print("Loading data...")
    df = load_nuforc_str()
    print(f"  Loaded {len(df)} rows")
    results = run_all_review_experiments(df)
    print("\n" + "=" * 60)
    print("Phase 2.75 experiments complete.")
    for k, v in results.items():
        print(f"  {k}: {v}")
