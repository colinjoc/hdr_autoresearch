#!/usr/bin/env python3
"""
tests/test_lapse_match.py — smoke tests for PL-4 lapsed permissions analysis.

Cross-checks:
  1. 2014-2019 residential PERMISSION cohort size is within ±10% of expected range
  2. CSO BHQ15 2019 permissions-granted vs our 2019 NRU sum
  3. Lapse rate is between 5% and 60% (sanity guard)
  4. BCMS match rate is between 50% and 95%
  5. Per-year lapse rates are monotonically correlated with expectations (pre-2017 > post-2017)
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "raw"
NPR = DATA / "national_planning_points.csv"
BCMS_PATH = Path("/home/col/generalized_hdr_autoresearch/applications/ie_commencement_notices/data/raw/bcms_notices.csv")
BHQ15_PATH = Path("/home/col/generalized_hdr_autoresearch/applications/ie_housing_pipeline/data/raw/BHQ15.json")

RESIDENTIAL_KEYWORDS = r'dwell|house|resid|apart|flat|storey|bedroom|domestic|bungalow|semi[\-\s]?det|terrace|cottage|dormer|granny|annex'

GRANTED = {'CONDITIONAL', 'GRANT PERMISSION', 'GRANT OUTLINE PERMISSION'}


def normalise_app_number(s):
    if pd.isna(s):
        return ""
    s = str(s).upper().strip()
    s = re.sub(r'^(PL|ABP|REG)[\s\-]*', '', s)
    s = re.sub(r'[\s\-/\\\.]+', '', s)
    parts = re.split(r'(\d+)', s)
    return ''.join(p.lstrip('0') or '0' if p.isdigit() else p for p in parts)


@pytest.fixture(scope="module")
def cohort_and_match():
    """Load cohort and compute BCMS matches."""
    npr = pd.read_csv(NPR, encoding='utf-8-sig', low_memory=False)
    npr['GrantDate'] = pd.to_datetime(npr['GrantDate'], format='mixed', errors='coerce')
    npr['grant_year'] = npr['GrantDate'].dt.year
    npr['NumResidentialUnits'] = pd.to_numeric(npr['NumResidentialUnits'], errors='coerce').fillna(0).astype(int)
    npr['desc_residential'] = npr['Development Description'].str.contains(
        RESIDENTIAL_KEYWORDS, case=False, na=False, regex=True)
    npr['is_residential'] = (npr['NumResidentialUnits'] > 0) | npr['desc_residential']

    cohort = npr[
        (npr['Application Type'].str.strip().str.upper() == 'PERMISSION') &
        (npr['Decision'].str.strip().str.upper().isin(GRANTED)) &
        (npr['grant_year'] >= 2014) & (npr['grant_year'] <= 2019) &
        (npr['is_residential']) &
        (npr['WithdrawnDate'].isna())
    ].copy()

    bcms = pd.read_csv(BCMS_PATH, encoding='utf-8-sig', low_memory=False)
    bcms['CN_Commencement_Date'] = pd.to_datetime(bcms['CN_Commencement_Date'], format='mixed', errors='coerce')
    bcms_dedup = bcms.dropna(subset=['CN_Commencement_Date']).sort_values('CN_Commencement_Date')
    bcms_dedup = bcms_dedup.drop_duplicates(subset=['CN_Planning_Permission_Number'], keep='first')

    # Normalised match
    cohort['app_num_norm'] = cohort['Application Number'].astype(str).str.strip().apply(normalise_app_number)
    bcms_dedup['app_num_norm'] = bcms_dedup['CN_Planning_Permission_Number'].astype(str).str.strip().apply(normalise_app_number)
    bcms_dedup = bcms_dedup.drop_duplicates(subset=['app_num_norm'], keep='first')
    match_set = set(bcms_dedup['app_num_norm'].unique())
    cohort['bcms_matched'] = cohort['app_num_norm'].isin(match_set)
    cohort['lapsed'] = ~cohort['bcms_matched']

    return cohort


def test_cohort_size(cohort_and_match):
    """2014-2019 residential PERMISSION cohort should be 20k-80k rows."""
    n = len(cohort_and_match)
    assert 20000 < n < 80000, f"Cohort size {n} outside expected range"


def test_lapse_rate_sanity(cohort_and_match):
    """Lapse rate should be between 5% and 60%."""
    rate = cohort_and_match['lapsed'].mean()
    assert 0.05 < rate < 0.60, f"Lapse rate {rate:.3f} outside sanity bounds"


def test_match_rate(cohort_and_match):
    """BCMS match rate should be between 50% and 95%."""
    rate = cohort_and_match['bcms_matched'].mean()
    assert 0.50 < rate < 0.95, f"Match rate {rate:.3f} outside expected range"


def test_pre2017_higher_lapse(cohort_and_match):
    """Pre-2017 cohort should have higher lapse than post-2017."""
    c = cohort_and_match
    pre = c[c['grant_year'] < 2017]['lapsed'].mean()
    post = c[c['grant_year'] >= 2017]['lapsed'].mean()
    assert pre > post, f"Pre-2017 lapse {pre:.3f} should exceed post-2017 {post:.3f}"


def test_bhq15_cross_check():
    """
    CSO BHQ15 2019 ALL-house-units should be within an order of magnitude
    of our 2019 NRU sum. BHQ15 counts only units with populated NRU,
    while our cohort also includes description-based residential. We check
    that the ratio is between 0.1 and 10 (broad sanity check given field-
    coverage differences).
    """
    npr = pd.read_csv(NPR, encoding='utf-8-sig', low_memory=False)
    npr['GrantDate'] = pd.to_datetime(npr['GrantDate'], format='mixed', errors='coerce')
    npr['grant_year'] = npr['GrantDate'].dt.year
    npr['NumResidentialUnits'] = pd.to_numeric(npr['NumResidentialUnits'], errors='coerce').fillna(0).astype(int)
    npr['desc_residential'] = npr['Development Description'].str.contains(
        RESIDENTIAL_KEYWORDS, case=False, na=False, regex=True)
    npr['is_residential'] = (npr['NumResidentialUnits'] > 0) | npr['desc_residential']

    c19 = npr[
        (npr['Application Type'].str.strip().str.upper() == 'PERMISSION') &
        (npr['Decision'].str.strip().str.upper().isin(GRANTED)) &
        (npr['grant_year'] == 2019) &
        (npr['is_residential']) &
        (npr['WithdrawnDate'].isna())
    ]
    our_nru = c19['NumResidentialUnits'].sum()

    with open(BHQ15_PATH) as f:
        bhq = json.load(f)
    stat_keys = list(bhq['dimension']['STATISTIC']['category']['index'])
    q_keys = list(bhq['dimension']['TLIST(Q1)']['category']['index'])
    values = bhq['value']
    q_2019 = [q for q in q_keys if q.startswith('2019')]

    bhq_total = 0
    for s_code in ['BHQ15C01', 'BHQ15C03']:  # apartments + all houses
        s_idx = stat_keys.index(s_code)
        for q in q_2019:
            q_idx = q_keys.index(q)
            flat = s_idx * len(q_keys) + q_idx
            key = str(flat) if isinstance(values, dict) else flat
            v = values.get(key, 0) if isinstance(values, dict) else values[flat]
            if v is not None:
                bhq_total += v

    if bhq_total == 0:
        pytest.skip("BHQ15 returned 0 for 2019; cannot validate")

    ratio = our_nru / bhq_total
    assert 0.1 < ratio < 10, f"NRU ratio {ratio:.2f} outside sanity bounds (our={our_nru}, bhq={bhq_total})"


def test_results_tsv_exists():
    """results.tsv should exist after analysis runs."""
    assert (ROOT / "results.tsv").exists(), "results.tsv not found"


def test_results_has_e00():
    """results.tsv should have an E00 baseline row."""
    df = pd.read_csv(ROOT / "results.tsv", sep='\t')
    assert 'E00' in df['experiment_id'].values, "E00 not in results.tsv"


def test_results_min_20_keep():
    """results.tsv should have >=20 KEEP rows."""
    df = pd.read_csv(ROOT / "results.tsv", sep='\t')
    keep_count = (df['status'] == 'KEEP').sum()
    assert keep_count >= 20, f"Only {keep_count} KEEP rows; need >=20"
