#!/usr/bin/env python3
"""
analysis.py — Lapsed Irish planning permissions (PL-4)
Reproduces E00 baseline and all Phase 1/2/2.5 experiments.

Key design choice: NumResidentialUnits is only populated from 2017 onward in
the national register. For 2014-2016, we identify residential permissions via
description-keyword matching. For 2017-2019, we use NumResidentialUnits > 0
as the primary filter. The "broad residential" flag uses either signal.
"""
import os, sys, warnings, re, json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ── paths ──────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "raw"
NPR  = DATA / "national_planning_points.csv"
BCMS_PATH = Path("/home/col/generalized_hdr_autoresearch/applications/ie_commencement_notices/data/raw/bcms_notices.csv")
BHQ15_PATH = Path("/home/col/generalized_hdr_autoresearch/applications/ie_housing_pipeline/data/raw/BHQ15.json")
RESULTS_TSV = ROOT / "results.tsv"
TOURNAMENT_CSV = ROOT / "tournament_results.csv"
DISCO = ROOT / "discoveries"
DISCO.mkdir(exist_ok=True)

SEED = 42
np.random.seed(SEED)

RESIDENTIAL_KEYWORDS = r'dwell|house|resid|apart|flat|storey|bedroom|domestic|bungalow|semi[\-\s]?det|terrace|cottage|dormer|granny|annex'

DUBLIN_LAS = {
    'Dublin City Council', 'Fingal County Council',
    'South Dublin County Council', 'Dun Laoghaire Rathdown County Council',
}

# ── helpers ────────────────────────────────────────────────────
def wilson_ci(successes, total, alpha=0.05):
    if total == 0:
        return (np.nan, np.nan)
    z = stats.norm.ppf(1 - alpha / 2)
    p_hat = successes / total
    denom = 1 + z**2 / total
    centre = (p_hat + z**2 / (2 * total)) / denom
    spread = z * np.sqrt(p_hat * (1 - p_hat) / total + z**2 / (4 * total**2)) / denom
    return (max(0, centre - spread), min(1, centre + spread))


def normalise_app_number(s):
    if pd.isna(s):
        return ""
    s = str(s).upper().strip()
    s = re.sub(r'^(PL|ABP|REG)[\s\-]*', '', s)
    s = re.sub(r'[\s\-/\\\.]+', '', s)
    parts = re.split(r'(\d+)', s)
    return ''.join(p.lstrip('0') or '0' if p.isdigit() else p for p in parts)


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


def append_result(results, **kwargs):
    results.append(kwargs)


def save_results(results):
    df = pd.DataFrame(results)
    col_order = ['experiment_id', 'description', 'metric', 'value', 'ci_lower',
                 'ci_upper', 'n', 'status', 'interaction', 'notes']
    for c in col_order:
        if c not in df.columns:
            df[c] = ""
    df = df[col_order]
    df.to_csv(RESULTS_TSV, sep='\t', index=False)


# ══════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════
print("Loading national planning register...")
npr = pd.read_csv(NPR, encoding='utf-8-sig', low_memory=False)
print(f"  {len(npr)} rows, {len(npr.columns)} columns")

date_cols = ['GrantDate', 'ExpiryDate', 'ReceivedDate', 'DecisionDate',
             'WithdrawnDate', 'AppealDecisionDate', 'FIRequestDate', 'FIRecDate']
for col in date_cols:
    if col in npr.columns:
        npr[col] = pd.to_datetime(npr[col], format='mixed', errors='coerce')

npr['grant_year'] = npr['GrantDate'].dt.year
npr['NumResidentialUnits'] = pd.to_numeric(npr['NumResidentialUnits'], errors='coerce').fillna(0).astype(int)
npr['FloorArea'] = pd.to_numeric(npr['FloorArea'], errors='coerce')
npr['AreaofSite'] = pd.to_numeric(npr['AreaofSite'], errors='coerce')

# Residential flag: NumResidentialUnits > 0 OR description matches residential keywords
npr['desc_residential'] = npr['Development Description'].str.contains(
    RESIDENTIAL_KEYWORDS, case=False, na=False, regex=True
)
npr['is_residential'] = (npr['NumResidentialUnits'] > 0) | npr['desc_residential']

print("Loading BCMS...")
bcms = pd.read_csv(BCMS_PATH, encoding='utf-8-sig', low_memory=False)
print(f"  {len(bcms)} BCMS rows")
bcms['CN_Commencement_Date'] = pd.to_datetime(bcms['CN_Commencement_Date'], format='mixed', errors='coerce')
bcms['CN_Date_Granted'] = pd.to_datetime(bcms['CN_Date_Granted'], format='mixed', errors='coerce')

# ══════════════════════════════════════════════════════════════
# BUILD COHORT
# ══════════════════════════════════════════════════════════════
print("\nBuilding cohort...")
granted_decisions = {'CONDITIONAL', 'GRANT PERMISSION', 'GRANT OUTLINE PERMISSION'}

cohort_mask = (
    (npr['Application Type'].str.strip().str.upper() == 'PERMISSION') &
    (npr['Decision'].str.strip().str.upper().isin(granted_decisions)) &
    (npr['grant_year'] >= 2014) &
    (npr['grant_year'] <= 2019) &
    (npr['is_residential']) &
    (npr['WithdrawnDate'].isna())
)
cohort = npr[cohort_mask].copy()
print(f"  Cohort: {len(cohort)} residential PERMISSION rows granted 2014-2019")
print(f"  By year: {cohort.groupby('grant_year').size().to_dict()}")

# ── BCMS join ──────────────────────────────────────────────────
print("\nJoining to BCMS...")

cohort['app_num_clean'] = cohort['Application Number'].astype(str).str.strip()
bcms['app_num_clean'] = bcms['CN_Planning_Permission_Number'].astype(str).str.strip()

# Deduplicate BCMS: earliest commencement per permission number
bcms_dedup = bcms.dropna(subset=['CN_Commencement_Date']).sort_values('CN_Commencement_Date')
bcms_dedup = bcms_dedup.drop_duplicates(subset=['app_num_clean'], keep='first')
bcms_match_set_exact = set(bcms_dedup['app_num_clean'].unique())

cohort['bcms_matched_exact'] = cohort['app_num_clean'].isin(bcms_match_set_exact)

# Commencement date map (exact)
bcms_date_map = bcms_dedup.set_index('app_num_clean')['CN_Commencement_Date'].to_dict()
cohort['commencement_date'] = cohort['app_num_clean'].map(bcms_date_map)

# Normalised match
cohort['app_num_norm'] = cohort['app_num_clean'].apply(normalise_app_number)
bcms_dedup_norm = bcms_dedup.copy()
bcms_dedup_norm['app_num_norm'] = bcms_dedup_norm['app_num_clean'].apply(normalise_app_number)
bcms_dedup_norm = bcms_dedup_norm.drop_duplicates(subset=['app_num_norm'], keep='first')
bcms_match_set_fuzzy = set(bcms_dedup_norm['app_num_norm'].unique())

cohort['bcms_matched_fuzzy'] = cohort['app_num_norm'].isin(bcms_match_set_fuzzy)
bcms_date_map_fuzzy = bcms_dedup_norm.set_index('app_num_norm')['CN_Commencement_Date'].to_dict()
cohort['commencement_date_fuzzy'] = cohort['app_num_norm'].map(bcms_date_map_fuzzy)
cohort['commencement_date'] = cohort['commencement_date'].fillna(cohort['commencement_date_fuzzy'])
cohort['bcms_matched'] = cohort['bcms_matched_exact'] | cohort['bcms_matched_fuzzy']

# Features
cohort['lapsed'] = (~cohort['bcms_matched']).astype(int)
cohort['one_off'] = cohort['One-Off House'].str.strip().str.upper().isin(['YES', 'SINGLE HOUSE'])
cohort['dublin'] = cohort['Planning Authority'].apply(is_dublin)
cohort['size_band'] = cohort['NumResidentialUnits'].apply(size_band)
cohort['has_nru'] = cohort['NumResidentialUnits'] > 0
cohort['expiry_passed'] = cohort['ExpiryDate'] < pd.Timestamp('2026-04-14')
cohort['decision_lag'] = (cohort['DecisionDate'] - cohort['ReceivedDate']).dt.days
cohort['fi_requested'] = cohort['FIRequestDate'].notna()
cohort['days_to_commence'] = (cohort['commencement_date'] - cohort['GrantDate']).dt.days
cohort['shd_era'] = cohort['grant_year'].between(2017, 2021)
cohort['appealed'] = cohort['Appeal Reference Number'].notna() & (cohort['Appeal Reference Number'].str.strip() != '')

exact_n = cohort['bcms_matched_exact'].sum()
fuzzy_only_n = (cohort['bcms_matched_fuzzy'] & ~cohort['bcms_matched_exact']).sum()
total_matched = cohort['bcms_matched'].sum()
n_total = len(cohort)
n_lapsed = cohort['lapsed'].sum()
lapse_rate = n_lapsed / n_total

print(f"  Exact match: {exact_n} ({exact_n/n_total:.1%})")
print(f"  Fuzzy adds: {fuzzy_only_n}")
print(f"  Total matched: {total_matched} ({total_matched/n_total:.1%})")
print(f"  Unmatched: {n_lapsed} ({lapse_rate:.1%})")

# ══════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════
results = []

ci_lo, ci_hi = wilson_ci(n_lapsed, n_total)
print(f"\n=== E00 ===  Lapse rate = {lapse_rate:.3f} [{ci_lo:.3f}, {ci_hi:.3f}]  N={n_total}")
append_result(results, experiment_id='E00',
              description='Headline lapse rate (2014-2019 residential PERMISSION, desc+NRU filter, fuzzy match)',
              metric='lapse_rate', value=round(lapse_rate, 4),
              ci_lower=round(ci_lo, 4), ci_upper=round(ci_hi, 4),
              n=n_total, status='BASELINE', interaction='False',
              notes=f'seed={SEED}; exact_match={exact_n}; fuzzy_only={fuzzy_only_n}')

# ══════════════════════════════════════════════════════════════
# Phase 1: Tournament
# ══════════════════════════════════════════════════════════════
print("\n=== Phase 1: Tournament ===")
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score
import lifelines

# Feature matrix
feature_cols_bool = ['one_off', 'dublin', 'fi_requested', 'appealed', 'shd_era', 'has_nru']
la_enc = LabelEncoder()
cohort['la_enc'] = la_enc.fit_transform(cohort['Planning Authority'].fillna('UNKNOWN'))
feature_cols = ['grant_year', 'NumResidentialUnits', 'la_enc'] + feature_cols_bool

X = cohort[feature_cols].copy()
for c in X.columns:
    X[c] = pd.to_numeric(X[c], errors='coerce').fillna(0)
y = cohort['lapsed'].values
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
tournament = []

# T01: Binomial per-year descriptive
yearly = cohort.groupby('grant_year').agg(n=('lapsed', 'count'), n_lapsed=('lapsed', 'sum')).reset_index()
yearly['rate'] = yearly['n_lapsed'] / yearly['n']
yearly_str = "; ".join(f"{int(r['grant_year'])}={r['rate']:.3f}(n={int(r['n'])})" for _, r in yearly.iterrows())
t01_std = yearly['rate'].std()
tournament.append({'model': 'T01_binomial_yearly', 'metric': 'rate_std', 'score': round(t01_std, 4),
                   'auc': np.nan, 'c_index': np.nan, 'notes': yearly_str})
append_result(results, experiment_id='T01', description='Binomial per-year lapse rate',
              metric='rate_std', value=round(t01_std, 4), ci_lower='', ci_upper='',
              n=n_total, status='TOURNAMENT', interaction='False', notes=yearly_str)

# T02: Logistic regression
print("  T02: Logistic...")
lr_model = LogisticRegression(max_iter=2000, solver='lbfgs', random_state=SEED)
lr_aucs = cross_val_score(lr_model, X, y, cv=cv, scoring='roc_auc')
lr_auc = lr_aucs.mean()
tournament.append({'model': 'T02_logistic', 'metric': 'AUC', 'score': round(lr_auc, 4),
                   'auc': round(lr_auc, 4), 'c_index': np.nan, 'notes': f'std={lr_aucs.std():.4f}'})
append_result(results, experiment_id='T02', description='Logistic regression AUC',
              metric='AUC_5fold', value=round(lr_auc, 4),
              ci_lower=round(lr_auc - 2*lr_aucs.std(), 4),
              ci_upper=round(lr_auc + 2*lr_aucs.std(), 4),
              n=n_total, status='TOURNAMENT', interaction='False', notes='')

# T03: Cox PH
print("  T03: Cox PH...")
etl_date = pd.Timestamp('2026-04-14')
cox_cols = ['grant_year', 'NumResidentialUnits', 'one_off', 'dublin', 'fi_requested', 'la_enc']
cox_data = cohort[cox_cols].copy()
cox_data['duration'] = cohort['days_to_commence'].copy()
no_match = cox_data['duration'].isna()
cox_data.loc[no_match, 'duration'] = (etl_date - cohort.loc[no_match.index, 'GrantDate']).dt.days
cox_data['event'] = cohort['bcms_matched'].astype(int)
cox_data = cox_data.dropna(subset=['duration'])
cox_data = cox_data[cox_data['duration'] > 0]
for c in cox_data.columns:
    cox_data[c] = pd.to_numeric(cox_data[c], errors='coerce').fillna(0).astype(float)

try:
    cph = lifelines.CoxPHFitter(penalizer=0.1)
    cph.fit(cox_data, duration_col='duration', event_col='event')
    c_index = cph.concordance_index_
    print(f"    C-index = {c_index:.4f}")
except Exception as e:
    print(f"    Cox failed: {e}")
    c_index = 0.5
tournament.append({'model': 'T03_cox_ph', 'metric': 'C-index', 'score': round(c_index, 4),
                   'auc': np.nan, 'c_index': round(c_index, 4), 'notes': ''})
append_result(results, experiment_id='T03', description='Cox PH C-index',
              metric='C_index', value=round(c_index, 4), ci_lower='', ci_upper='',
              n=len(cox_data), status='TOURNAMENT', interaction='False', notes='')

# T04: GBM
print("  T04: GBM...")
gbm = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                  random_state=SEED, subsample=0.8)
gbm_aucs = cross_val_score(gbm, X, y, cv=cv, scoring='roc_auc')
gbm_auc = gbm_aucs.mean()
tournament.append({'model': 'T04_gbm', 'metric': 'AUC', 'score': round(gbm_auc, 4),
                   'auc': round(gbm_auc, 4), 'c_index': np.nan, 'notes': f'std={gbm_aucs.std():.4f}'})
append_result(results, experiment_id='T04', description='GBM classifier AUC',
              metric='AUC_5fold', value=round(gbm_auc, 4),
              ci_lower=round(gbm_auc - 2*gbm_aucs.std(), 4),
              ci_upper=round(gbm_auc + 2*gbm_aucs.std(), 4),
              n=n_total, status='TOURNAMENT', interaction='False', notes='')

# T05: Random Forest
print("  T05: RF...")
rf = RandomForestClassifier(n_estimators=300, max_depth=8, random_state=SEED, n_jobs=-1)
rf_aucs = cross_val_score(rf, X, y, cv=cv, scoring='roc_auc')
rf_auc = rf_aucs.mean()
tournament.append({'model': 'T05_random_forest', 'metric': 'AUC', 'score': round(rf_auc, 4),
                   'auc': round(rf_auc, 4), 'c_index': np.nan, 'notes': f'std={rf_aucs.std():.4f}'})
append_result(results, experiment_id='T05', description='Random forest AUC',
              metric='AUC_5fold', value=round(rf_auc, 4),
              ci_lower=round(rf_auc - 2*rf_aucs.std(), 4),
              ci_upper=round(rf_auc + 2*rf_aucs.std(), 4),
              n=n_total, status='TOURNAMENT', interaction='False', notes='')

# Champion
classifiers = [t for t in tournament if t['metric'] == 'AUC']
champion = max(classifiers, key=lambda x: x['score']) if classifiers else tournament[0]
print(f"\n  CHAMPION: {champion['model']} AUC={champion['score']}")
pd.DataFrame(tournament).to_csv(TOURNAMENT_CSV, index=False)

# ══════════════════════════════════════════════════════════════
# Phase 2: Experiments
# ══════════════════════════════════════════════════════════════
print("\n=== Phase 2 ===")

# E01: match rate
append_result(results, experiment_id='E01', description='BCMS exact match rate',
              metric='exact_match_rate', value=round(exact_n/n_total, 4),
              ci_lower='', ci_upper='', n=n_total, status='KEEP', interaction='False',
              notes=f'fuzzy_rate={total_matched/n_total:.4f}; fuzzy_only={fuzzy_only_n}')

# E02: normalisation delta
lapse_exact = 1 - exact_n/n_total
lapse_fuzzy = lapse_rate
append_result(results, experiment_id='E02', description='Fuzzy-match normalisation gain on lapse rate',
              metric='delta_lapse', value=round(lapse_exact - lapse_fuzzy, 4),
              ci_lower='', ci_upper='', n=n_total, status='KEEP', interaction='False',
              notes=f'lapse_exact={lapse_exact:.4f}; lapse_fuzzy={lapse_fuzzy:.4f}')

# E03: one-off vs multi-unit
oneoff = cohort[cohort['one_off']]
multi = cohort[~cohort['one_off']]
lr_oo = oneoff['lapsed'].mean() if len(oneoff) > 0 else np.nan
lr_mu = multi['lapsed'].mean()
ci_oo = wilson_ci(int(oneoff['lapsed'].sum()), len(oneoff)) if len(oneoff) > 0 else (np.nan, np.nan)
ci_mu = wilson_ci(int(multi['lapsed'].sum()), len(multi))
append_result(results, experiment_id='E03', description='One-off vs multi-unit lapse rate',
              metric='lapse_rate_multi', value=round(lr_mu, 4),
              ci_lower=round(ci_mu[0], 4), ci_upper=round(ci_mu[1], 4), n=len(multi),
              status='KEEP', interaction='False',
              notes=f'one_off_lapse={lr_oo:.4f}(n={len(oneoff)})')

# E04: OUTLINE PERMISSION lapse rate
outline = npr[
    (npr['Application Type'].str.strip().str.upper() == 'OUTLINE PERMISSION') &
    (npr['Decision'].str.strip().str.upper().isin(granted_decisions)) &
    (npr['grant_year'] >= 2014) & (npr['grant_year'] <= 2019) &
    (npr['is_residential'])
].copy()
outline['app_num_norm'] = outline['Application Number'].astype(str).str.strip().apply(normalise_app_number)
outline['bcms_matched'] = outline['app_num_norm'].isin(bcms_match_set_fuzzy)
lr_outline = 1 - outline['bcms_matched'].mean() if len(outline) > 0 else np.nan
append_result(results, experiment_id='E04', description='Outline Permission lapse rate',
              metric='lapse_rate_outline', value=round(lr_outline, 4) if not np.isnan(lr_outline) else '',
              ci_lower='', ci_upper='', n=len(outline), status='KEEP', interaction='False',
              notes='Outline not in main PERMISSION cohort')

# E05: RETENTION lapse rate
retention = npr[
    (npr['Application Type'].str.strip().str.upper() == 'RETENTION') &
    (npr['Decision'].str.strip().str.upper().isin(granted_decisions)) &
    (npr['grant_year'] >= 2014) & (npr['grant_year'] <= 2019) &
    (npr['is_residential'])
].copy()
retention['app_num_norm'] = retention['Application Number'].astype(str).str.strip().apply(normalise_app_number)
retention['bcms_matched'] = retention['app_num_norm'].isin(bcms_match_set_fuzzy)
lr_ret = 1 - retention['bcms_matched'].mean() if len(retention) > 0 else np.nan
append_result(results, experiment_id='E05', description='Retention lapse rate',
              metric='lapse_rate_retention', value=round(lr_ret, 4) if not np.isnan(lr_ret) else '',
              ci_lower='', ci_upper='', n=len(retention), status='KEEP', interaction='False',
              notes='RETENTION backward-looking')

# E06: REFUSED excluded
refused_n = npr[
    (npr['Application Type'].str.strip().str.upper() == 'PERMISSION') &
    (npr['Decision'].str.strip().str.upper() == 'REFUSED') &
    (npr['grant_year'] >= 2014) & (npr['grant_year'] <= 2019)
].shape[0]
append_result(results, experiment_id='E06', description='Refused excluded from cohort',
              metric='refused_count', value=refused_n,
              ci_lower='', ci_upper='', n=refused_n, status='KEEP', interaction='False',
              notes='Correctly excluded')

# E07: Dublin vs non-Dublin
dub = cohort[cohort['dublin']]
nondub = cohort[~cohort['dublin']]
lr_dub = dub['lapsed'].mean()
lr_nondub = nondub['lapsed'].mean()
ci_d = wilson_ci(int(dub['lapsed'].sum()), len(dub))
ci_nd = wilson_ci(int(nondub['lapsed'].sum()), len(nondub))
append_result(results, experiment_id='E07', description='Dublin vs non-Dublin lapse',
              metric='lapse_rate_dublin', value=round(lr_dub, 4),
              ci_lower=round(ci_d[0], 4), ci_upper=round(ci_d[1], 4), n=len(dub),
              status='KEEP', interaction='False',
              notes=f'nondub={lr_nondub:.4f}[{ci_nd[0]:.4f},{ci_nd[1]:.4f}](n={len(nondub)}); delta={lr_dub-lr_nondub:.4f}')

# E08: pre-2017 vs 2017+
pre17 = cohort[cohort['grant_year'] < 2017]
post17 = cohort[cohort['grant_year'] >= 2017]
lr_pre = pre17['lapsed'].mean()
lr_post = post17['lapsed'].mean()
ci_pre = wilson_ci(int(pre17['lapsed'].sum()), len(pre17))
ci_post = wilson_ci(int(post17['lapsed'].sum()), len(post17))
append_result(results, experiment_id='E08', description='Pre-2017 vs 2017+ lapse',
              metric='lapse_rate_pre2017', value=round(lr_pre, 4),
              ci_lower=round(ci_pre[0], 4), ci_upper=round(ci_pre[1], 4), n=len(pre17),
              status='KEEP', interaction='False',
              notes=f'post2017={lr_post:.4f}[{ci_post[0]:.4f},{ci_post[1]:.4f}](n={len(post17)})')

# E09: size-stratified
size_stats = cohort.groupby('size_band').agg(n=('lapsed', 'count'), n_lapsed=('lapsed', 'sum')).reset_index()
size_stats['rate'] = size_stats['n_lapsed'] / size_stats['n']
size_str = "; ".join(f"{r['size_band']}={r['rate']:.3f}(n={r['n']})" for _, r in size_stats.iterrows())
append_result(results, experiment_id='E09', description='Size-stratified lapse rates',
              metric='size_rates', value=round(size_stats['rate'].mean(), 4),
              ci_lower='', ci_upper='', n=n_total, status='KEEP', interaction='False', notes=size_str)

# E10: LA top/bottom 5
la_stats = cohort.groupby('Planning Authority').agg(n=('lapsed', 'count'), n_lapsed=('lapsed', 'sum')).reset_index()
la_stats['rate'] = la_stats['n_lapsed'] / la_stats['n']
la_stats = la_stats.sort_values('rate')
la_min30 = la_stats[la_stats['n'] >= 30]
top5 = la_min30.head(5)
bot5 = la_min30.tail(5)
top5_str = "; ".join(f"{r['Planning Authority']}={r['rate']:.3f}(n={int(r['n'])})" for _, r in top5.iterrows())
bot5_str = "; ".join(f"{r['Planning Authority']}={r['rate']:.3f}(n={int(r['n'])})" for _, r in bot5.iterrows())
append_result(results, experiment_id='E10', description='LA top/bottom 5 lapse',
              metric='la_range', value=round(la_min30['rate'].std(), 4),
              ci_lower=round(la_min30['rate'].min(), 4), ci_upper=round(la_min30['rate'].max(), 4),
              n=len(la_min30), status='KEEP', interaction='False',
              notes=f'LOWEST: {top5_str} | HIGHEST: {bot5_str}')

# E11: post-expiry commencements (extension proxy)
matched = cohort[cohort['bcms_matched']].copy()
has_both = matched['commencement_date'].notna() & matched['ExpiryDate'].notna()
post_expiry = matched.loc[has_both, 'commencement_date'] > matched.loc[has_both, 'ExpiryDate']
n_post_exp = post_expiry.sum()
n_with_both = has_both.sum()
ext_proxy = n_post_exp / n_with_both if n_with_both > 0 else np.nan
append_result(results, experiment_id='E11', description='Post-expiry commencements (extension proxy)',
              metric='post_expiry_share', value=round(ext_proxy, 4) if not np.isnan(ext_proxy) else '',
              ci_lower='', ci_upper='', n=n_with_both, status='KEEP', interaction='False',
              notes=f'n_post_expiry={n_post_exp}')

# E12: 2019 vs pre-2019
pre19 = cohort[cohort['grant_year'] < 2019]
yr19 = cohort[cohort['grant_year'] == 2019]
append_result(results, experiment_id='E12', description='2019 vs pre-2019 lapse',
              metric='lapse_2019', value=round(yr19['lapsed'].mean(), 4),
              ci_lower='', ci_upper='', n=len(yr19), status='KEEP', interaction='False',
              notes=f'pre2019={pre19["lapsed"].mean():.4f}(n={len(pre19)})')

# E13: appealed vs not
appealed = cohort[cohort['appealed']]
not_appealed = cohort[~cohort['appealed']]
lr_app = appealed['lapsed'].mean() if len(appealed) > 0 else np.nan
lr_noapp = not_appealed['lapsed'].mean()
append_result(results, experiment_id='E13', description='Appealed vs non-appealed lapse',
              metric='lapse_appealed', value=round(lr_app, 4) if not np.isnan(lr_app) else '',
              ci_lower='', ci_upper='', n=len(appealed), status='KEEP', interaction='False',
              notes=f'not_appealed={lr_noapp:.4f}(n={len(not_appealed)})')

# E14: apartment-heavy LA (≥10 units)
apt_heavy = cohort[cohort['NumResidentialUnits'] >= 10]
if len(apt_heavy) > 0:
    apt_la = apt_heavy.groupby('Planning Authority').agg(n=('lapsed','count'),n_lapsed=('lapsed','sum')).reset_index()
    apt_la['rate'] = apt_la['n_lapsed'] / apt_la['n']
    apt_la = apt_la.sort_values('rate')
    append_result(results, experiment_id='E14', description='Apartment-heavy LA lapse (≥10 units)',
                  metric='mean_lapse', value=round(apt_la['rate'].mean(), 4),
                  ci_lower='', ci_upper='', n=int(apt_la['n'].sum()), status='KEEP', interaction='False',
                  notes=f'range=[{apt_la["rate"].min():.3f},{apt_la["rate"].max():.3f}]')

# E15: NRU-flagged cohort only (2017-2019, where field is well populated)
nru_cohort = cohort[(cohort['NumResidentialUnits'] > 0) & (cohort['grant_year'] >= 2017)]
lr_nru = nru_cohort['lapsed'].mean()
ci_nru = wilson_ci(int(nru_cohort['lapsed'].sum()), len(nru_cohort))
append_result(results, experiment_id='E15', description='NRU>0 only (2017-2019) lapse rate',
              metric='lapse_rate_nru', value=round(lr_nru, 4),
              ci_lower=round(ci_nru[0], 4), ci_upper=round(ci_nru[1], 4), n=len(nru_cohort),
              status='KEEP', interaction='False',
              notes='NumResidentialUnits populated from 2017; cleaner residential filter')

# E16: excluding 2019 (right-censoring sensitivity)
excl19 = cohort[cohort['grant_year'] <= 2018]
lr_e16 = excl19['lapsed'].mean()
ci_e16 = wilson_ci(int(excl19['lapsed'].sum()), len(excl19))
append_result(results, experiment_id='E16', description='Lapse rate excl 2019 (right-censoring)',
              metric='lapse_2014_2018', value=round(lr_e16, 4),
              ci_lower=round(ci_e16[0], 4), ci_upper=round(ci_e16[1], 4), n=len(excl19),
              status='KEEP', interaction='False', notes=f'delta_from_E00={lr_e16-lapse_rate:.4f}')

# E17: Weibull AFT
print("  E17: AFT...")
from lifelines import WeibullAFTFitter
aft_cols = ['grant_year', 'NumResidentialUnits', 'one_off', 'dublin', 'la_enc']
aft_data = cohort[aft_cols].copy()
aft_data['duration'] = cohort['days_to_commence'].copy()
no_m = aft_data['duration'].isna()
aft_data.loc[no_m, 'duration'] = (etl_date - cohort.loc[no_m.index, 'GrantDate']).dt.days
aft_data['event'] = cohort['bcms_matched'].astype(int)
aft_data = aft_data.dropna(subset=['duration'])
aft_data = aft_data[aft_data['duration'] > 0]
for c in aft_data.columns:
    aft_data[c] = pd.to_numeric(aft_data[c], errors='coerce').fillna(0).astype(float)

try:
    aft = WeibullAFTFitter(penalizer=0.1)
    aft.fit(aft_data, duration_col='duration', event_col='event')
    # The shape parameter lambda_ vs rho — lifelines parameterises as lambda * rho
    aft_summary = aft.summary
    print(f"    AFT fitted. AIC={aft.AIC_:.1f}")
    append_result(results, experiment_id='E17', description='Weibull AFT fitted',
                  metric='AIC', value=round(aft.AIC_, 1),
                  ci_lower='', ci_upper='', n=len(aft_data), status='KEEP', interaction='False',
                  notes='Weibull AFT converged with penalizer=0.1')
except Exception as e:
    print(f"    AFT failed: {e}")
    append_result(results, experiment_id='E17', description='Weibull AFT (failed)',
                  metric='error', value='FAILED', ci_lower='', ci_upper='',
                  n=len(aft_data), status='REVERT', interaction='False', notes=str(e)[:200])

# E18: withdrawn count
withdrawn_n = npr[
    (npr['Application Type'].str.strip().str.upper() == 'PERMISSION') &
    (npr['WithdrawnDate'].notna()) &
    (npr['grant_year'] >= 2014) & (npr['grant_year'] <= 2019)
].shape[0]
append_result(results, experiment_id='E18', description='Withdrawn excluded',
              metric='withdrawn_count', value=withdrawn_n,
              ci_lower='', ci_upper='', n=withdrawn_n, status='KEEP', interaction='False',
              notes='Already excluded from cohort')

# E19: normalisation sensitivity
delta_norm = lapse_exact - lapse_fuzzy
append_result(results, experiment_id='E19', description='Normalisation sensitivity (Δlapse)',
              metric='delta_lapse', value=round(delta_norm, 4),
              ci_lower='', ci_upper='', n=n_total, status='KEEP', interaction='False',
              notes=f'exact={lapse_exact:.4f}; fuzzy={lapse_fuzzy:.4f}')

# E20: BHQ15 cross-check
print("  E20: BHQ15...")
try:
    with open(BHQ15_PATH) as f:
        bhq = json.load(f)
    stat_keys = list(bhq['dimension']['STATISTIC']['category']['index'])
    q_keys = list(bhq['dimension']['TLIST(Q1)']['category']['index'])
    values = bhq['value']
    q_2019 = [q for q in q_keys if q.startswith('2019')]
    total_bhq = 0
    # BHQ15C03 = All house units
    s_idx_house = stat_keys.index('BHQ15C03')
    for q in q_2019:
        q_idx = q_keys.index(q)
        flat = s_idx_house * len(q_keys) + q_idx
        key = str(flat) if isinstance(values, dict) else flat
        v = values.get(key, 0) if isinstance(values, dict) else values[flat]
        if v is not None:
            total_bhq += v
    # Also add apartments
    s_idx_apt = stat_keys.index('BHQ15C01')
    total_bhq_apt = 0
    for q in q_2019:
        q_idx = q_keys.index(q)
        flat = s_idx_apt * len(q_keys) + q_idx
        key = str(flat) if isinstance(values, dict) else flat
        v = values.get(key, 0) if isinstance(values, dict) else values[flat]
        if v is not None:
            total_bhq_apt += v

    our_2019_nru = cohort[cohort['grant_year'] == 2019]['NumResidentialUnits'].sum()
    our_2019_n = len(cohort[cohort['grant_year'] == 2019])
    bhq_total = total_bhq + total_bhq_apt
    ratio = our_2019_nru / bhq_total if bhq_total > 0 else np.nan
    append_result(results, experiment_id='E20', description='BHQ15 cross-check (2019)',
                  metric='our_units_vs_cso', value=round(ratio, 4) if not np.isnan(ratio) else '',
                  ci_lower='', ci_upper='', n=int(our_2019_nru), status='KEEP', interaction='False',
                  notes=f'our_nru={our_2019_nru}; bhq_house={total_bhq}; bhq_apt={total_bhq_apt}; our_applications={our_2019_n}')
except Exception as e:
    print(f"  BHQ15 failed: {e}")
    append_result(results, experiment_id='E20', description='BHQ15 cross-check failed',
                  metric='error', value=str(e)[:100], ci_lower='', ci_upper='',
                  n=0, status='REVERT', interaction='False', notes='')

# E21: Per-year lapse rates
for yr in range(2014, 2020):
    c_yr = cohort[cohort['grant_year'] == yr]
    lr_yr = c_yr['lapsed'].mean()
    ci_yr = wilson_ci(int(c_yr['lapsed'].sum()), len(c_yr))
    append_result(results, experiment_id=f'E21_{yr}', description=f'{yr} lapse rate',
                  metric='lapse_rate', value=round(lr_yr, 4),
                  ci_lower=round(ci_yr[0], 4), ci_upper=round(ci_yr[1], 4),
                  n=len(c_yr), status='KEEP', interaction='False', notes='')

# E22: units-weighted lapse
total_units = cohort['NumResidentialUnits'].sum()
lapsed_units = cohort[cohort['lapsed']==1]['NumResidentialUnits'].sum()
lr_uw = lapsed_units / total_units if total_units > 0 else np.nan
ci_uw = wilson_ci(int(lapsed_units), int(total_units))
append_result(results, experiment_id='E22', description='Units-weighted lapse rate',
              metric='lapse_unit_weighted', value=round(lr_uw, 4) if not np.isnan(lr_uw) else '',
              ci_lower=round(ci_uw[0], 4), ci_upper=round(ci_uw[1], 4),
              n=int(total_units), status='KEEP', interaction='False',
              notes=f'app_weighted={lapse_rate:.4f}; delta={lr_uw-lapse_rate:.4f}' if not np.isnan(lr_uw) else '')

# E23: days-to-commence distribution
commenced = cohort[cohort['bcms_matched'] & cohort['days_to_commence'].notna() & (cohort['days_to_commence'] > 0)]
if len(commenced) > 0:
    p25 = commenced['days_to_commence'].quantile(0.25)
    p50 = commenced['days_to_commence'].quantile(0.50)
    p75 = commenced['days_to_commence'].quantile(0.75)
    p90 = commenced['days_to_commence'].quantile(0.90)
    append_result(results, experiment_id='E23', description='Days-to-commence distribution',
                  metric='median_days', value=round(p50, 1),
                  ci_lower=round(p25, 1), ci_upper=round(p75, 1),
                  n=len(commenced), status='KEEP', interaction='False',
                  notes=f'P25={p25:.0f}d P50={p50:.0f}d P75={p75:.0f}d P90={p90:.0f}d ({p50/365:.1f}yr)')

# E24: description-only vs NRU-flagged match rates (for 2017-2019 where both available)
c1719 = cohort[cohort['grant_year'].between(2017, 2019)]
desc_only = c1719[c1719['desc_residential'] & ~c1719['has_nru']]
nru_flagged = c1719[c1719['has_nru']]
both = c1719[c1719['desc_residential'] & c1719['has_nru']]
lr_desc_only = desc_only['lapsed'].mean() if len(desc_only) > 0 else np.nan
lr_nru_f = nru_flagged['lapsed'].mean() if len(nru_flagged) > 0 else np.nan
lr_both = both['lapsed'].mean() if len(both) > 0 else np.nan
append_result(results, experiment_id='E24', description='Desc-only vs NRU-flagged lapse (2017-2019)',
              metric='lapse_desc_only', value=round(lr_desc_only, 4) if not np.isnan(lr_desc_only) else '',
              ci_lower='', ci_upper='', n=len(desc_only), status='KEEP', interaction='False',
              notes=f'nru_flagged={lr_nru_f:.4f}(n={len(nru_flagged)}); both={lr_both:.4f}(n={len(both)})')

# E25: temporal split
print("  E25: Temporal split...")
train_m = cohort['grant_year'] <= 2017
test_m = cohort['grant_year'] >= 2018
if train_m.sum() > 100 and test_m.sum() > 100:
    gbm_t = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                        random_state=SEED, subsample=0.8)
    gbm_t.fit(X[train_m], y[train_m])
    auc_t = roc_auc_score(y[test_m], gbm_t.predict_proba(X[test_m])[:, 1])
    append_result(results, experiment_id='E25', description='Temporal GBM (train≤2017 test≥2018)',
                  metric='AUC_temporal', value=round(auc_t, 4),
                  ci_lower='', ci_upper='', n=int(test_m.sum()), status='KEEP', interaction='False',
                  notes=f'train_n={int(train_m.sum())}')

# ══════════════════════════════════════════════════════════════
# Phase 2.5: Pairwise interactions
# ══════════════════════════════════════════════════════════════
print("\n=== Phase 2.5 ===")

# size × dublin
for sb in ['0_or_na', '1', '2-4', '5-49', '50+']:
    for dv in [True, False]:
        cell = cohort[(cohort['size_band'] == sb) & (cohort['dublin'] == dv)]
        if len(cell) >= 10:
            lr_c = cell['lapsed'].mean()
            ci_c = wilson_ci(int(cell['lapsed'].sum()), len(cell))
            label = f"size={sb}_dub={dv}"
            append_result(results, experiment_id=f'IX_{label}',
                          description=f'Interaction: {label}', metric='lapse_rate',
                          value=round(lr_c, 4), ci_lower=round(ci_c[0], 4), ci_upper=round(ci_c[1], 4),
                          n=len(cell), status='KEEP', interaction='True', notes='')

# year × dublin
for yr in range(2014, 2020):
    for dv in [True, False]:
        cell = cohort[(cohort['grant_year'] == yr) & (cohort['dublin'] == dv)]
        if len(cell) >= 10:
            lr_c = cell['lapsed'].mean()
            label = f"yr={yr}_dub={dv}"
            append_result(results, experiment_id=f'IX_{label}',
                          description=f'Interaction: {label}', metric='lapse_rate',
                          value=round(lr_c, 4), ci_lower='', ci_upper='',
                          n=len(cell), status='KEEP', interaction='True', notes='')

# size × year (key cells)
for sb in ['0_or_na', '1', '50+']:
    for yr in [2014, 2016, 2019]:
        cell = cohort[(cohort['size_band'] == sb) & (cohort['grant_year'] == yr)]
        if len(cell) >= 5:
            lr_c = cell['lapsed'].mean()
            label = f"size={sb}_yr={yr}"
            append_result(results, experiment_id=f'IX_{label}',
                          description=f'Interaction: {label}', metric='lapse_rate',
                          value=round(lr_c, 4), ci_lower='', ci_upper='',
                          n=len(cell), status='KEEP', interaction='True', notes='')

# ══════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════
save_results(results)
print(f"\nSaved {len(results)} rows to {RESULTS_TSV}")

# ── Summary ───────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"HEADLINE: Lapse rate = {lapse_rate:.1%} [{ci_lo:.1%}, {ci_hi:.1%}]  N={n_total}")
print(f"  Matched: {total_matched} | Unmatched: {n_lapsed}")
print(f"  Dublin: {lr_dub:.1%} (n={len(dub)}) | non-Dublin: {lr_nondub:.1%} (n={len(nondub)})")
print(f"  Champion: {champion['model']} AUC={champion['score']}")
if len(commenced) > 0:
    print(f"  Median days-to-commence: {p50:.0f}d ({p50/365:.1f}yr)")
print(f"  Per-year: {yearly_str}")
print(f"{'='*60}")
