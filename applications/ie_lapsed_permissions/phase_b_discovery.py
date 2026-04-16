#!/usr/bin/env python3
"""
phase_b_discovery.py — Phase B: commencement probability by stratum

For a prospective developer choosing a site, predict P(commencement within
the observation window) given LA + scheme size + type + dublin flag.

Output: discoveries/commencement_probability_by_stratum.csv
"""
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw"
NPR = DATA / "national_planning_points.csv"
BCMS_PATH = Path("/home/col/generalized_hdr_autoresearch/applications/ie_commencement_notices/data/raw/bcms_notices.csv")
DISCO = ROOT / "discoveries"
DISCO.mkdir(exist_ok=True)

RESIDENTIAL_KEYWORDS = r'dwell|house|resid|apart|flat|storey|bedroom|domestic|bungalow|semi[\-\s]?det|terrace|cottage|dormer|granny|annex'

DUBLIN_LAS = {
    'Dublin City Council', 'Fingal County Council',
    'South Dublin County Council', 'Dun Laoghaire Rathdown County Council',
}

GRANTED = {'CONDITIONAL', 'GRANT PERMISSION', 'GRANT OUTLINE PERMISSION'}


def normalise_app_number(s):
    if pd.isna(s):
        return ""
    s = str(s).upper().strip()
    s = re.sub(r'^(PL|ABP|REG)[\s\-]*', '', s)
    s = re.sub(r'[\s\-/\\\.]+', '', s)
    parts = re.split(r'(\d+)', s)
    return ''.join(p.lstrip('0') or '0' if p.isdigit() else p for p in parts)


def wilson_ci(k, n, alpha=0.05):
    if n == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - alpha / 2)
    p_hat = k / n
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    spread = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return (max(0, centre - spread), min(1, centre + spread))


def is_dublin(pa):
    if pd.isna(pa):
        return False
    pa_str = str(pa).strip()
    for d in DUBLIN_LAS:
        if d.lower() in pa_str.lower() or pa_str.lower() in d.lower():
            return True
    return False


def size_band(n):
    if pd.isna(n) or n <= 0:
        return '0_or_na'
    elif n == 1:
        return '1'
    elif n <= 4:
        return '2-4'
    elif n <= 49:
        return '5-49'
    else:
        return '50+'


def main():
    print("Phase B: Loading data...")
    npr = pd.read_csv(NPR, encoding='utf-8-sig', low_memory=False)
    npr['GrantDate'] = pd.to_datetime(npr['GrantDate'], format='mixed', errors='coerce')
    npr['grant_year'] = npr['GrantDate'].dt.year
    npr['NumResidentialUnits'] = pd.to_numeric(npr['NumResidentialUnits'], errors='coerce').fillna(0).astype(int)
    npr['desc_residential'] = npr['Development Description'].str.contains(
        RESIDENTIAL_KEYWORDS, case=False, na=False, regex=True)
    npr['is_residential'] = (npr['NumResidentialUnits'] > 0) | npr['desc_residential']

    bcms = pd.read_csv(BCMS_PATH, encoding='utf-8-sig', low_memory=False)
    bcms['CN_Commencement_Date'] = pd.to_datetime(bcms['CN_Commencement_Date'], format='mixed', errors='coerce')
    bcms_dedup = bcms.dropna(subset=['CN_Commencement_Date']).sort_values('CN_Commencement_Date')
    bcms_dedup = bcms_dedup.drop_duplicates(subset=['CN_Planning_Permission_Number'], keep='first')
    bcms_dedup['app_num_norm'] = bcms_dedup['CN_Planning_Permission_Number'].astype(str).str.strip().apply(normalise_app_number)
    bcms_dedup = bcms_dedup.drop_duplicates(subset=['app_num_norm'], keep='first')
    match_set = set(bcms_dedup['app_num_norm'].unique())

    # Build cohort (2014-2019, PERMISSION, residential, granted, not withdrawn)
    cohort = npr[
        (npr['Application Type'].str.strip().str.upper() == 'PERMISSION') &
        (npr['Decision'].str.strip().str.upper().isin(GRANTED)) &
        (npr['grant_year'] >= 2014) & (npr['grant_year'] <= 2019) &
        (npr['is_residential']) &
        (npr['WithdrawnDate'].isna())
    ].copy()

    cohort['app_num_norm'] = cohort['Application Number'].astype(str).str.strip().apply(normalise_app_number)
    cohort['bcms_matched'] = cohort['app_num_norm'].isin(match_set)
    cohort['commenced'] = cohort['bcms_matched'].astype(int)
    cohort['dublin_flag'] = cohort['Planning Authority'].apply(is_dublin)
    cohort['size_band'] = cohort['NumResidentialUnits'].apply(size_band)

    # Commencement date for median time
    bcms_date_map = bcms_dedup.set_index('app_num_norm')['CN_Commencement_Date'].to_dict()
    cohort['commencement_date'] = cohort['app_num_norm'].map(bcms_date_map)
    cohort['days_to_commence'] = (cohort['commencement_date'] - cohort['GrantDate']).dt.days

    print(f"  Cohort: {len(cohort)} rows")

    # Stratify by: planning_authority x size_band x dublin_flag
    strata = cohort.groupby(['Planning Authority', 'size_band', 'dublin_flag']).agg(
        n_permissions=('commenced', 'count'),
        n_commenced=('commenced', 'sum'),
        median_days_to_commence=('days_to_commence', 'median')
    ).reset_index()

    strata['p_commence'] = strata['n_commenced'] / strata['n_permissions']
    strata['p_commence_lower95'] = strata.apply(
        lambda r: wilson_ci(int(r['n_commenced']), int(r['n_permissions']))[0], axis=1)
    strata['p_commence_upper95'] = strata.apply(
        lambda r: wilson_ci(int(r['n_commenced']), int(r['n_permissions']))[1], axis=1)

    def risk_cat(p):
        if p >= 0.75:
            return 'RELIABLE'
        elif p >= 0.5:
            return 'MODERATE'
        elif p >= 0.25:
            return 'RISKY'
        else:
            return 'DANGER'

    strata['risk_category'] = strata['p_commence'].apply(risk_cat)

    # Round
    for c in ['p_commence', 'p_commence_lower95', 'p_commence_upper95']:
        strata[c] = strata[c].round(4)
    strata['median_days_to_commence'] = strata['median_days_to_commence'].round(0)

    # Sort by p_commence
    strata = strata.sort_values('p_commence', ascending=True)

    out_path = DISCO / "commencement_probability_by_stratum.csv"
    strata.to_csv(out_path, index=False)
    print(f"\nSaved {len(strata)} strata to {out_path}")

    # Summary
    print(f"\nRisk distribution (n>=30 strata only):")
    big = strata[strata['n_permissions'] >= 30]
    for cat in ['DANGER', 'RISKY', 'MODERATE', 'RELIABLE']:
        sub = big[big['risk_category'] == cat]
        print(f"  {cat}: {len(sub)} strata, {sub['n_permissions'].sum()} permissions")

    print(f"\nTop-5 DANGER strata (n>=30):")
    danger = big[big['risk_category'] == 'DANGER'].sort_values('p_commence').head(5)
    for _, r in danger.iterrows():
        print(f"  {r['Planning Authority']} | {r['size_band']} | dublin={r['dublin_flag']} | "
              f"p={r['p_commence']:.3f} [{r['p_commence_lower95']:.3f},{r['p_commence_upper95']:.3f}] n={int(r['n_permissions'])}")

    print(f"\nTop-5 RELIABLE strata (n>=30):")
    reliable = big[big['risk_category'] == 'RELIABLE'].sort_values('p_commence', ascending=False).head(5)
    for _, r in reliable.iterrows():
        print(f"  {r['Planning Authority']} | {r['size_band']} | dublin={r['dublin_flag']} | "
              f"p={r['p_commence']:.3f} [{r['p_commence_lower95']:.3f},{r['p_commence_upper95']:.3f}] n={int(r['n_permissions'])}")


if __name__ == '__main__':
    main()
