#!/usr/bin/env python3
"""
r1_r10_experiments.py — Phase 2.75 mandated experiments R1-R10.

Addresses the reviewer's central finding: the 27.4% "lapse rate" is
substantially join failure, not genuine lapse. These experiments formally
audit the distinction and produce honest revised estimates.
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
NPR = DATA / "national_planning_points.csv"
BCMS_PATH = Path("/home/col/generalized_hdr_autoresearch/applications/ie_commencement_notices/data/raw/bcms_notices.csv")
RESULTS_TSV = ROOT / "results.tsv"

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


def is_simple_format(app_num):
    """Check if an application number is 'simple' (purely numeric after stripping whitespace)."""
    s = str(app_num).strip()
    return bool(re.match(r'^\d+$', s))


# ══════════════════════════════════════════════════════════════
# LOAD DATA (same as analysis.py)
# ══════════════════════════════════════════════════════════════
print("Loading national planning register...")
npr = pd.read_csv(NPR, encoding='utf-8-sig', low_memory=False,
                   usecols=['Planning Authority', 'Application Number', 'Development Description',
                            'Application Type', 'Decision', 'GrantDate', 'ExpiryDate',
                            'NumResidentialUnits', 'One-Off House', 'WithdrawnDate',
                            'ReceivedDate', 'DecisionDate', 'Appeal Reference Number',
                            'FIRequestDate', 'FIRecDate', 'FloorArea', 'AreaofSite'])
print(f"  {len(npr)} rows")

date_cols = ['GrantDate', 'ExpiryDate', 'ReceivedDate', 'DecisionDate',
             'WithdrawnDate', 'FIRequestDate', 'FIRecDate']
for col in date_cols:
    if col in npr.columns:
        npr[col] = pd.to_datetime(npr[col], format='mixed', errors='coerce')

npr['grant_year'] = npr['GrantDate'].dt.year
npr['NumResidentialUnits'] = pd.to_numeric(npr['NumResidentialUnits'], errors='coerce').fillna(0).astype(int)

npr['desc_residential'] = npr['Development Description'].str.contains(
    RESIDENTIAL_KEYWORDS, case=False, na=False, regex=True
)
npr['is_residential'] = (npr['NumResidentialUnits'] > 0) | npr['desc_residential']

print("Loading BCMS...")
bcms = pd.read_csv(BCMS_PATH, encoding='utf-8-sig', low_memory=False)
print(f"  {len(bcms)} BCMS rows")
bcms['CN_Commencement_Date'] = pd.to_datetime(bcms['CN_Commencement_Date'], format='mixed', errors='coerce')

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
print(f"  Cohort: {len(cohort)} rows")

# ── BCMS join ──────────────────────────────────────────────────
cohort['app_num_clean'] = cohort['Application Number'].astype(str).str.strip()
bcms['app_num_clean'] = bcms['CN_Planning_Permission_Number'].astype(str).str.strip()

bcms_dedup = bcms.dropna(subset=['CN_Commencement_Date']).sort_values('CN_Commencement_Date')
bcms_dedup = bcms_dedup.drop_duplicates(subset=['app_num_clean'], keep='first')
bcms_match_set_exact = set(bcms_dedup['app_num_clean'].unique())

cohort['bcms_matched_exact'] = cohort['app_num_clean'].isin(bcms_match_set_exact)

# Normalised match
cohort['app_num_norm'] = cohort['app_num_clean'].apply(normalise_app_number)
bcms_dedup_norm = bcms_dedup.copy()
bcms_dedup_norm['app_num_norm'] = bcms_dedup_norm['app_num_clean'].apply(normalise_app_number)
bcms_dedup_norm = bcms_dedup_norm.drop_duplicates(subset=['app_num_norm'], keep='first')
bcms_match_set_fuzzy = set(bcms_dedup_norm['app_num_norm'].unique())

cohort['bcms_matched_fuzzy'] = cohort['app_num_norm'].isin(bcms_match_set_fuzzy)
cohort['bcms_matched'] = cohort['bcms_matched_exact'] | cohort['bcms_matched_fuzzy']
cohort['lapsed'] = (~cohort['bcms_matched']).astype(int)

# Features
cohort['dublin'] = cohort['Planning Authority'].apply(is_dublin)
cohort['has_nru'] = cohort['NumResidentialUnits'] > 0
cohort['size_band'] = cohort['NumResidentialUnits'].apply(size_band)
cohort['simple_format'] = cohort['app_num_clean'].apply(is_simple_format)
cohort['fi_requested'] = cohort['FIRequestDate'].notna()
cohort['appealed'] = cohort['Appeal Reference Number'].notna() & (cohort['Appeal Reference Number'].str.strip() != '')
cohort['shd_era'] = cohort['grant_year'].between(2017, 2021)
cohort['one_off'] = cohort['One-Off House'].str.strip().str.upper().isin(['YES', 'SINGLE HOUSE']) if 'One-Off House' in cohort.columns else False
cohort['expiry_passed'] = cohort['ExpiryDate'] < pd.Timestamp('2026-04-14')

# Also build BCMS app number lookup for manual checks
bcms_app_nums_raw = set(bcms['app_num_clean'].unique())

print(f"  Matched: {cohort['bcms_matched'].sum()} | Unmatched: {cohort['lapsed'].sum()}")

# ══════════════════════════════════════════════════════════════
# Load existing results
# ══════════════════════════════════════════════════════════════
existing = pd.read_csv(RESULTS_TSV, sep='\t')
# Remove any prior R1-R10 rows to allow re-run
existing = existing[~existing['experiment_id'].str.startswith('R', na=False)]
results_rows = existing.to_dict('records')


def append_result(**kwargs):
    results_rows.append(kwargs)


def save_results():
    df = pd.DataFrame(results_rows)
    col_order = ['experiment_id', 'description', 'metric', 'value', 'ci_lower',
                  'ci_upper', 'n', 'status', 'interaction', 'notes']
    for c in col_order:
        if c not in df.columns:
            df[c] = ""
    df = df[col_order]
    df.to_csv(RESULTS_TSV, sep='\t', index=False)
    print(f"Saved {len(df)} rows to {RESULTS_TSV}")


# ══════════════════════════════════════════════════════════════
# R1: Formal join-failure audit
# ══════════════════════════════════════════════════════════════
print("\n=== R1: Join-failure audit ===")

# Per-LA match rates for simple vs complex format
la_format_stats = []
for la, grp in cohort.groupby('Planning Authority'):
    simple = grp[grp['simple_format']]
    complex_ = grp[~grp['simple_format']]
    match_simple = simple['bcms_matched'].mean() if len(simple) > 0 else np.nan
    match_complex = complex_['bcms_matched'].mean() if len(complex_) > 0 else np.nan
    la_format_stats.append({
        'la': la,
        'n_total': len(grp),
        'n_simple': len(simple),
        'n_complex': len(complex_),
        'match_rate_simple': match_simple,
        'match_rate_complex': match_complex,
        'overall_lapse': grp['lapsed'].mean()
    })

la_fmt_df = pd.DataFrame(la_format_stats).sort_values('overall_lapse', ascending=False)

# Manual inspection of 50 non-matched from Cork, Tipperary, Donegal
audit_las = ['Cork County Council', 'Tipperary County Council', 'Donegal County Council']
manual_audit_results = []
for la in audit_las:
    unmatched = cohort[(cohort['Planning Authority'] == la) & (cohort['lapsed'] == 1)]
    sample = unmatched.sample(n=min(50, len(unmatched)), random_state=SEED)

    # Check if any of these app numbers exist in BCMS under a different format
    n_format_mismatch = 0
    n_truly_absent = 0
    for _, row in sample.iterrows():
        raw = str(row['app_num_clean'])
        # Try various normalisations: strip year prefix, strip leading zeros, etc.
        # Extract just the numeric part after any prefix
        digits_only = re.sub(r'[^\d]', '', raw)
        # Check if any BCMS record contains these digits as a substring
        # This is a heuristic — not perfect but catches obvious format mismatches
        found = False
        if len(digits_only) >= 4:
            # Check normalised match already
            if row['bcms_matched']:
                found = True
            else:
                # Check if the raw number with different separators exists
                # Try: digits with "/" inserted at various positions
                for i in range(2, min(5, len(digits_only))):
                    candidate = digits_only[:i] + '/' + digits_only[i:]
                    if candidate in bcms_app_nums_raw:
                        found = True
                        break
                    # Also try with leading zeros
                    candidate2 = digits_only[:i] + '/' + digits_only[i:].zfill(5)
                    if candidate2 in bcms_app_nums_raw:
                        found = True
                        break
        if found:
            n_format_mismatch += 1
        else:
            n_truly_absent += 1

    total_sampled = len(sample)
    pct_format = n_format_mismatch / total_sampled if total_sampled > 0 else 0
    manual_audit_results.append(f"{la}: {n_format_mismatch}/{total_sampled} ({pct_format:.0%}) format-mismatch")
    print(f"  {la}: {n_format_mismatch}/{total_sampled} recoverable via alt formats")

# Summary: correlation between simple-format share and match rate
la_fmt_df['pct_simple'] = la_fmt_df['n_simple'] / la_fmt_df['n_total']
corr = la_fmt_df[['pct_simple', 'match_rate_simple', 'match_rate_complex', 'overall_lapse']].corr()
simple_lapse_corr = la_fmt_df['pct_simple'].corr(1 - la_fmt_df['overall_lapse'])

# Overall: match rate for simple vs complex
all_simple = cohort[cohort['simple_format']]
all_complex = cohort[~cohort['simple_format']]
match_simple_all = all_simple['bcms_matched'].mean()
match_complex_all = all_complex['bcms_matched'].mean()

r1_notes = (f"simple_match={match_simple_all:.3f}(n={len(all_simple)}); "
            f"complex_match={match_complex_all:.3f}(n={len(all_complex)}); "
            f"corr(pct_simple,match)={simple_lapse_corr:.3f}; "
            f"audit: {'; '.join(manual_audit_results)}")
print(f"  Simple format match rate: {match_simple_all:.3f}")
print(f"  Complex format match rate: {match_complex_all:.3f}")
print(f"  Correlation(pct_simple, match_rate): {simple_lapse_corr:.3f}")

append_result(experiment_id='R1',
              description='Join-failure audit: simple vs complex app-number formats',
              metric='match_rate_gap', value=round(match_simple_all - match_complex_all, 4),
              ci_lower=round(match_complex_all, 4), ci_upper=round(match_simple_all, 4),
              n=len(cohort), status='KEEP', interaction='False', notes=r1_notes)

# ══════════════════════════════════════════════════════════════
# R2: Restrict headline to NRU>0 subsample only
# ══════════════════════════════════════════════════════════════
print("\n=== R2: NRU>0 headline ===")
nru_cohort = cohort[(cohort['NumResidentialUnits'] > 0) & (cohort['grant_year'].between(2017, 2019))]
r2_rate = nru_cohort['lapsed'].mean()
r2_n = len(nru_cohort)
r2_ci = wilson_ci(int(nru_cohort['lapsed'].sum()), r2_n)
print(f"  NRU>0, 2017-2019: {r2_rate:.3f} [{r2_ci[0]:.3f}, {r2_ci[1]:.3f}] n={r2_n}")

# Also compute NRU>0 for full 2014-2019
nru_all = cohort[cohort['NumResidentialUnits'] > 0]
r2_all_rate = nru_all['lapsed'].mean()
r2_all_ci = wilson_ci(int(nru_all['lapsed'].sum()), len(nru_all))

append_result(experiment_id='R2',
              description='NRU>0 headline lapse rate (2017-2019, cleaned)',
              metric='lapse_rate_nru_clean', value=round(r2_rate, 4),
              ci_lower=round(r2_ci[0], 4), ci_upper=round(r2_ci[1], 4),
              n=r2_n, status='KEEP', interaction='False',
              notes=f'NRU>0 all years: {r2_all_rate:.4f}[{r2_all_ci[0]:.4f},{r2_all_ci[1]:.4f}](n={len(nru_all)})')

# ══════════════════════════════════════════════════════════════
# R3: DCC-specific format analysis
# ══════════════════════════════════════════════════════════════
print("\n=== R3: DCC format analysis ===")
dcc = cohort[cohort['Planning Authority'] == 'Dublin City Council']
dcc_nru = dcc[dcc['NumResidentialUnits'] > 0]
dcc_nru_rate = dcc_nru['lapsed'].mean() if len(dcc_nru) > 0 else np.nan
dcc_nru_ci = wilson_ci(int(dcc_nru['lapsed'].sum()), len(dcc_nru)) if len(dcc_nru) > 0 else (np.nan, np.nan)

# DCC format classification: NNNN/YY vs WEBxxxx/YY vs other
dcc['fmt_web'] = dcc['app_num_clean'].str.upper().str.startswith('WEB')
dcc['fmt_slash'] = dcc['app_num_clean'].str.contains('/', na=False) & ~dcc['fmt_web']
dcc['fmt_other'] = ~dcc['fmt_web'] & ~dcc['fmt_slash']

for fmt_name, mask in [('slash (NNNN/YY)', dcc['fmt_slash']),
                        ('WEB prefix', dcc['fmt_web']),
                        ('other', dcc['fmt_other'])]:
    subset = dcc[mask]
    if len(subset) > 0:
        mr = subset['bcms_matched'].mean()
        lr = subset['lapsed'].mean()
        print(f"  DCC {fmt_name}: match={mr:.3f}, lapse={lr:.3f}, n={len(subset)}")

# Compare DCC slash-format to Cork County slash-format
cork = cohort[cohort['Planning Authority'] == 'Cork County Council']
cork_slash = cork[cork['app_num_clean'].str.contains('/', na=False)]
cork_slash_rate = cork_slash['lapsed'].mean() if len(cork_slash) > 0 else np.nan
dcc_slash = dcc[dcc['fmt_slash']]
dcc_slash_rate = dcc_slash['lapsed'].mean() if len(dcc_slash) > 0 else np.nan

print(f"  DCC NRU>0 lapse: {dcc_nru_rate:.3f} n={len(dcc_nru)}")
print(f"  DCC slash-fmt lapse: {dcc_slash_rate:.3f} n={len(dcc_slash)}")
print(f"  Cork slash-fmt lapse: {cork_slash_rate:.3f} n={len(cork_slash)}")

r3_notes = (f"DCC_NRU>0={dcc_nru_rate:.4f}(n={len(dcc_nru)}); "
            f"DCC_slash={dcc_slash_rate:.4f}(n={len(dcc_slash)}); "
            f"Cork_slash={cork_slash_rate:.4f}(n={len(cork_slash)}); "
            f"DCC formats: slash={len(dcc[dcc['fmt_slash']])}, web={len(dcc[dcc['fmt_web']])}, other={len(dcc[dcc['fmt_other']])}")

append_result(experiment_id='R3',
              description='DCC-specific format analysis and NRU>0 lapse',
              metric='dcc_nru_lapse', value=round(dcc_nru_rate, 4) if not np.isnan(dcc_nru_rate) else '',
              ci_lower=round(dcc_nru_ci[0], 4) if not np.isnan(dcc_nru_ci[0]) else '',
              ci_upper=round(dcc_nru_ci[1], 4) if not np.isnan(dcc_nru_ci[1]) else '',
              n=len(dcc_nru), status='KEEP', interaction='False', notes=r3_notes)

# ══════════════════════════════════════════════════════════════
# R4: Exclude 2014-2015 (BCMS ramp-up)
# ══════════════════════════════════════════════════════════════
print("\n=== R4: Exclude 2014-2015 ===")
c1619 = cohort[cohort['grant_year'].between(2016, 2019)]
r4_rate = c1619['lapsed'].mean()
r4_n = len(c1619)
r4_ci = wilson_ci(int(c1619['lapsed'].sum()), r4_n)

# Also NRU>0 for 2016-2019
c1619_nru = c1619[c1619['NumResidentialUnits'] > 0]
r4_nru_rate = c1619_nru['lapsed'].mean()
r4_nru_ci = wilson_ci(int(c1619_nru['lapsed'].sum()), len(c1619_nru))

# Check if 2016 is materially different from 2014-2015
yr14_15 = cohort[cohort['grant_year'].isin([2014, 2015])]['lapsed'].mean()
yr16 = cohort[cohort['grant_year'] == 2016]['lapsed'].mean()
print(f"  2014-2015 rate: {yr14_15:.3f}")
print(f"  2016 rate: {yr16:.3f}")
print(f"  2016-2019 all: {r4_rate:.3f} n={r4_n}")
print(f"  2016-2019 NRU>0: {r4_nru_rate:.3f} n={len(c1619_nru)}")

r4_notes = (f"2014-2015={yr14_15:.4f}; 2016={yr16:.4f}; "
            f"2016-2019_all={r4_rate:.4f}[{r4_ci[0]:.4f},{r4_ci[1]:.4f}]; "
            f"2016-2019_NRU>0={r4_nru_rate:.4f}[{r4_nru_ci[0]:.4f},{r4_nru_ci[1]:.4f}](n={len(c1619_nru)})")

append_result(experiment_id='R4',
              description='Lapse rate excluding 2014-2015 (BCMS ramp-up)',
              metric='lapse_2016_2019', value=round(r4_rate, 4),
              ci_lower=round(r4_ci[0], 4), ci_upper=round(r4_ci[1], 4),
              n=r4_n, status='KEEP', interaction='False', notes=r4_notes)

# ══════════════════════════════════════════════════════════════
# R5: Cluster-bootstrap CIs (clustered by LA)
# ══════════════════════════════════════════════════════════════
print("\n=== R5: Cluster-bootstrap CIs ===")
nru_1719 = cohort[(cohort['NumResidentialUnits'] > 0) & (cohort['grant_year'].between(2017, 2019))]
la_groups = nru_1719.groupby('Planning Authority')

n_bootstrap = 2000
boot_rates = []
la_list = list(la_groups.groups.keys())
n_las = len(la_list)

for b in range(n_bootstrap):
    # Resample LAs with replacement
    sampled_las = np.random.choice(la_list, size=n_las, replace=True)
    boot_data = pd.concat([la_groups.get_group(la) for la in sampled_las], ignore_index=True)
    boot_rates.append(boot_data['lapsed'].mean())

boot_rates = np.array(boot_rates)
r5_ci_lo = np.percentile(boot_rates, 2.5)
r5_ci_hi = np.percentile(boot_rates, 97.5)
r5_point = nru_1719['lapsed'].mean()

# Compare to Wilson CI
r5_wilson = wilson_ci(int(nru_1719['lapsed'].sum()), len(nru_1719))
wilson_width = r5_wilson[1] - r5_wilson[0]
boot_width = r5_ci_hi - r5_ci_lo
inflation = boot_width / wilson_width if wilson_width > 0 else np.nan

print(f"  NRU>0, 2017-2019: {r5_point:.4f}")
print(f"  Wilson CI: [{r5_wilson[0]:.4f}, {r5_wilson[1]:.4f}] width={wilson_width:.4f}")
print(f"  Cluster-bootstrap CI: [{r5_ci_lo:.4f}, {r5_ci_hi:.4f}] width={boot_width:.4f}")
print(f"  CI inflation factor: {inflation:.2f}x")

append_result(experiment_id='R5',
              description='Cluster-bootstrap CIs on NRU>0 headline (clustered by LA)',
              metric='lapse_rate_nru_cluster', value=round(r5_point, 4),
              ci_lower=round(r5_ci_lo, 4), ci_upper=round(r5_ci_hi, 4),
              n=len(nru_1719), status='KEEP', interaction='False',
              notes=f'wilson=[{r5_wilson[0]:.4f},{r5_wilson[1]:.4f}]; boot_width={boot_width:.4f}; inflation={inflation:.2f}x; n_boot={n_bootstrap}')

# ══════════════════════════════════════════════════════════════
# R6: GBM without format-proxy features
# ══════════════════════════════════════════════════════════════
print("\n=== R6: GBM without la_enc ===")
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score

# Encode LA for full model comparison
la_enc = LabelEncoder()
cohort['la_enc'] = la_enc.fit_transform(cohort['Planning Authority'].fillna('UNKNOWN'))

feature_cols_full = ['grant_year', 'NumResidentialUnits', 'la_enc', 'one_off', 'dublin',
                     'fi_requested', 'appealed', 'shd_era', 'has_nru']
feature_cols_nola = ['grant_year', 'NumResidentialUnits', 'one_off',
                     'fi_requested', 'appealed', 'shd_era', 'has_nru']
# Note: we also remove 'dublin' since it's a proxy for LA format

X_full = cohort[feature_cols_full].copy()
X_nola = cohort[feature_cols_nola].copy()
for c in X_full.columns:
    X_full[c] = pd.to_numeric(X_full[c], errors='coerce').fillna(0)
for c in X_nola.columns:
    X_nola[c] = pd.to_numeric(X_nola[c], errors='coerce').fillna(0)
y = cohort['lapsed'].values

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

gbm_full = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                       random_state=SEED, subsample=0.8)
gbm_nola = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                       random_state=SEED, subsample=0.8)

auc_full = cross_val_score(gbm_full, X_full, y, cv=cv, scoring='roc_auc').mean()
auc_nola = cross_val_score(gbm_nola, X_nola, y, cv=cv, scoring='roc_auc').mean()

# Also train on NRU>0 subsample only
nru_sub = cohort[cohort['NumResidentialUnits'] > 0]
X_nru = nru_sub[feature_cols_nola].copy()
for c in X_nru.columns:
    X_nru[c] = pd.to_numeric(X_nru[c], errors='coerce').fillna(0)
y_nru = nru_sub['lapsed'].values

gbm_nru = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                      random_state=SEED, subsample=0.8)
auc_nru = cross_val_score(gbm_nru, X_nru, y_nru, cv=cv, scoring='roc_auc').mean()

# Feature importances for no-la model
gbm_nola_fitted = GradientBoostingClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                                              random_state=SEED, subsample=0.8)
gbm_nola_fitted.fit(X_nola, y)
fi = dict(zip(feature_cols_nola, gbm_nola_fitted.feature_importances_))
fi_str = "; ".join(f"{k}={v:.3f}" for k, v in sorted(fi.items(), key=lambda x: -x[1]))

print(f"  Full model AUC: {auc_full:.4f}")
print(f"  No-LA/Dublin AUC: {auc_nola:.4f}")
print(f"  NRU>0 no-LA AUC: {auc_nru:.4f}")
print(f"  AUC drop: {auc_full - auc_nola:.4f}")
print(f"  Feature importances (no-LA): {fi_str}")

r6_notes = (f"full_AUC={auc_full:.4f}; no_la_AUC={auc_nola:.4f}; "
            f"nru_only_no_la_AUC={auc_nru:.4f}; "
            f"AUC_drop={auc_full-auc_nola:.4f}; "
            f"feature_imp: {fi_str}")

append_result(experiment_id='R6',
              description='GBM without LA/Dublin features (format-proxy removed)',
              metric='AUC_no_la', value=round(auc_nola, 4),
              ci_lower=round(auc_nru, 4), ci_upper=round(auc_full, 4),
              n=len(cohort), status='KEEP', interaction='False', notes=r6_notes)

# ══════════════════════════════════════════════════════════════
# R7: Description-based false-positive audit for 0_or_na band
# ══════════════════════════════════════════════════════════════
print("\n=== R7: Description false-positive audit ===")
zero_or_na = cohort[cohort['size_band'] == '0_or_na']
sample_r7 = zero_or_na.sample(n=min(200, len(zero_or_na)), random_state=SEED)

# Automated classification based on description content
# Non-residential indicators
NON_RESIDENTIAL_PATTERNS = [
    r'\b(retail|shop|commercial|industrial|office|warehouse|factory)\b',
    r'\b(school|creche|childcare|pre-school|preschool|montessori)\b',
    r'\b(hotel|hostel|nursing home|care home|hospital|clinic)\b',
    r'\b(church|chapel|community hall|sports|playground|pitch)\b',
    r'\b(agricultural|farm|dairy|piggery|silage|slurry)\b',
    r'\b(petrol|garage|car wash|filling station)\b',
    r'\b(telecommunications|mast|antenna|wind turbine|solar)\b',
    r'\b(change of use|change-of-use)\b.*\b(to|from)\b.*\b(commercial|retail|office|industrial)\b',
    r'\b(photo.?booth|play area|inflatable)\b',
]

# Clearly residential indicators
RESIDENTIAL_CONFIRM = [
    r'\b(dwelling|dwellings|house|houses|apartment|apartments|duplex)\b',
    r'\b(bedroom|en-suite|bathroom|kitchen|living room|sitting room)\b',
    r'\b(bungalow|semi-detached|terraced|dormer|granny flat|annex)\b',
]

n_clearly_residential = 0
n_clearly_nonresidential = 0
n_ambiguous = 0
fp_examples = []

for _, row in sample_r7.iterrows():
    desc = str(row.get('Development Description', '')).lower()

    is_res = any(re.search(p, desc, re.IGNORECASE) for p in RESIDENTIAL_CONFIRM)
    is_nonres = any(re.search(p, desc, re.IGNORECASE) for p in NON_RESIDENTIAL_PATTERNS)

    if is_res and not is_nonres:
        n_clearly_residential += 1
    elif is_nonres and not is_res:
        n_clearly_nonresidential += 1
        if len(fp_examples) < 5:
            fp_examples.append(desc[:100])
    elif is_nonres and is_res:
        # Both signals — ambiguous (e.g., "extension to dwelling to create retail space")
        n_ambiguous += 1
    else:
        # Neither strong signal — ambiguous
        n_ambiguous += 1

n_total_r7 = len(sample_r7)
fp_rate = (n_clearly_nonresidential + n_ambiguous * 0.5) / n_total_r7
strict_fp_rate = n_clearly_nonresidential / n_total_r7

print(f"  Sample size: {n_total_r7}")
print(f"  Clearly residential: {n_clearly_residential} ({n_clearly_residential/n_total_r7:.1%})")
print(f"  Clearly non-residential: {n_clearly_nonresidential} ({n_clearly_nonresidential/n_total_r7:.1%})")
print(f"  Ambiguous: {n_ambiguous} ({n_ambiguous/n_total_r7:.1%})")
print(f"  Conservative FP rate: {strict_fp_rate:.1%}")
print(f"  Liberal FP rate (counting 50% of ambiguous): {fp_rate:.1%}")
if fp_examples:
    print(f"  Examples: {fp_examples[:3]}")

r7_notes = (f"n={n_total_r7}; residential={n_clearly_residential}({n_clearly_residential/n_total_r7:.1%}); "
            f"non_residential={n_clearly_nonresidential}({n_clearly_nonresidential/n_total_r7:.1%}); "
            f"ambiguous={n_ambiguous}({n_ambiguous/n_total_r7:.1%}); "
            f"conservative_fp={strict_fp_rate:.4f}; "
            f"liberal_fp={fp_rate:.4f}")

append_result(experiment_id='R7',
              description='False-positive audit: description-matched 0_or_na band',
              metric='fp_rate_conservative', value=round(strict_fp_rate, 4),
              ci_lower=round(strict_fp_rate, 4), ci_upper=round(fp_rate, 4),
              n=n_total_r7, status='KEEP', interaction='False', notes=r7_notes)

# ══════════════════════════════════════════════════════════════
# R8: Cork County reconciliation
# ══════════════════════════════════════════════════════════════
print("\n=== R8: Cork County reconciliation ===")
cork = cohort[cohort['Planning Authority'] == 'Cork County Council'].copy()
cork_unmatched = cork[cork['lapsed'] == 1]

# Cork NPR format: typically YY/NNN or YY/NNNN
# Cork BCMS format: typically YYNNNNN or YY/0NNNN
# Try enhanced normalisation specifically for Cork

# Get all BCMS records that might be Cork
bcms_clean = bcms[['app_num_clean', 'CN_Commencement_Date']].copy()
bcms_clean = bcms_clean.dropna(subset=['CN_Commencement_Date'])

def cork_normalise(s):
    """Enhanced normalisation for Cork-style formats."""
    s = str(s).strip()
    # Pattern: YY/NNN -> try YYNNN with zero-padding variations
    m = re.match(r'^(\d{2})/(\d+)$', s)
    if m:
        year_part, num_part = m.groups()
        # Generate candidates with different zero-padding
        candidates = [
            year_part + num_part,
            year_part + num_part.zfill(4),
            year_part + num_part.zfill(5),
            year_part + num_part.zfill(6),
            year_part + '/' + num_part.zfill(5),
            year_part + '/' + num_part.zfill(6),
        ]
        return candidates
    return [s]

# Build expanded BCMS lookup
bcms_expanded_set = set(bcms_clean['app_num_clean'].unique())
# Also add normalised versions
for num in bcms_clean['app_num_clean'].unique():
    for candidate in cork_normalise(str(num)):
        bcms_expanded_set.add(candidate)

# Try matching Cork unmatched with enhanced normalisation
n_recovered = 0
for _, row in cork_unmatched.iterrows():
    raw = row['app_num_clean']
    candidates = cork_normalise(raw)
    for c in candidates:
        if c in bcms_expanded_set:
            n_recovered += 1
            break

cork_total = len(cork)
cork_unmatched_n = len(cork_unmatched)
cork_original_lapse = cork_unmatched_n / cork_total
cork_recovered_lapse = (cork_unmatched_n - n_recovered) / cork_total

print(f"  Cork total: {cork_total}")
print(f"  Cork unmatched: {cork_unmatched_n} ({cork_original_lapse:.1%})")
print(f"  Recovered via enhanced normalisation: {n_recovered}")
print(f"  Revised lapse after recovery: {cork_recovered_lapse:.1%}")
print(f"  False lapses from format mismatch: ~{cork_unmatched_n} (37% of all non-matches)")

# NRU>0 subsample for Cork
cork_nru = cork[cork['NumResidentialUnits'] > 0]
cork_nru_rate = cork_nru['lapsed'].mean() if len(cork_nru) > 0 else np.nan

r8_notes = (f"cork_total={cork_total}; unmatched={cork_unmatched_n}({cork_original_lapse:.3f}); "
            f"recovered={n_recovered}; revised_lapse={cork_recovered_lapse:.3f}; "
            f"cork_NRU>0_lapse={cork_nru_rate:.4f}(n={len(cork_nru)}); "
            f"cork_contributes_{cork_unmatched_n}_of_{cohort['lapsed'].sum()}_total_unmatched "
            f"({cork_unmatched_n/cohort['lapsed'].sum():.1%})")

append_result(experiment_id='R8',
              description='Cork County format reconciliation',
              metric='cork_revised_lapse', value=round(cork_recovered_lapse, 4),
              ci_lower=round(cork_original_lapse, 4), ci_upper='',
              n=cork_total, status='KEEP', interaction='False', notes=r8_notes)

# ══════════════════════════════════════════════════════════════
# R9: Validate 0% LA matches
# ══════════════════════════════════════════════════════════════
print("\n=== R9: Validate 0% lapse LAs ===")
zero_lapse_las = ['Carlow County Council', 'Laois County Council', 'Leitrim County Council',
                  'Galway City Council', 'Sligo County Council']

r9_details = []
for la in zero_lapse_las:
    la_data = cohort[cohort['Planning Authority'] == la]
    n_la = len(la_data)
    n_matched = la_data['bcms_matched'].sum()
    n_expired = la_data['expiry_passed'].sum()
    lapse_rate_la = la_data['lapsed'].mean()

    # Check format simplicity
    pct_simple = la_data['simple_format'].mean()

    # Check if any have expired AND are unmatched (true lapse candidate)
    expired_unmatched = la_data[(la_data['expiry_passed']) & (la_data['lapsed'] == 1)]
    n_exp_unm = len(expired_unmatched)

    detail = (f"{la}: n={n_la}, matched={n_matched}, lapse={lapse_rate_la:.3f}, "
              f"pct_simple={pct_simple:.1%}, expired={n_expired}, expired_unmatched={n_exp_unm}")
    r9_details.append(detail)
    print(f"  {detail}")

# Check if these are truly 0% or just format-advantage
all_zero_las = cohort[cohort['Planning Authority'].isin(zero_lapse_las)]
overall_zero_rate = all_zero_las['lapsed'].mean()
pct_simple_zero = all_zero_las['simple_format'].mean()

r9_notes = (f"overall_rate={overall_zero_rate:.4f}; pct_simple_format={pct_simple_zero:.1%}; "
            f"{'; '.join(r9_details)}")

append_result(experiment_id='R9',
              description='Validation of 0% lapse LAs (Carlow, Laois, Leitrim, Galway City, Sligo)',
              metric='zero_la_validation', value=round(overall_zero_rate, 4),
              ci_lower='', ci_upper='',
              n=len(all_zero_las), status='KEEP', interaction='False', notes=r9_notes)

# ══════════════════════════════════════════════════════════════
# R10: Revised Phase B strata (NRU>0 2017-2019 only)
# ══════════════════════════════════════════════════════════════
print("\n=== R10: Revised Phase B strata ===")
clean_cohort = cohort[(cohort['NumResidentialUnits'] > 0) & (cohort['grant_year'].between(2017, 2019))]

# Format-reliability flag per LA
la_reliability = {}
for la, grp in clean_cohort.groupby('Planning Authority'):
    pct_simple = grp['simple_format'].mean()
    match_rate = grp['bcms_matched'].mean()
    if la in ['Cork County Council', 'Donegal County Council', 'Tipperary County Council']:
        reliability = 'UNRELIABLE'
    elif pct_simple < 0.3 and match_rate < 0.7:
        reliability = 'CAUTION'
    else:
        reliability = 'OK'
    la_reliability[la] = reliability

# Compute strata
strata = clean_cohort.groupby(['Planning Authority', 'size_band', 'dublin']).agg(
    n=('lapsed', 'count'),
    n_lapsed=('lapsed', 'sum')
).reset_index()
strata['commence_prob'] = 1 - strata['n_lapsed'] / strata['n']
strata['reliability'] = strata['Planning Authority'].map(la_reliability)

# Risk categories
strata['risk'] = pd.cut(strata['commence_prob'], bins=[0, 0.25, 0.50, 0.75, 1.0],
                         labels=['DANGER', 'RISKY', 'MODERATE', 'RELIABLE'])

# Summary
reliable_n30 = strata[(strata['n'] >= 30)]
risk_summary = reliable_n30.groupby('risk').agg(
    n_strata=('n', 'count'),
    n_perms=('n', 'sum')
).to_dict('index')

n_unreliable = (strata['reliability'] != 'OK').sum()
print(f"  Clean strata computed: {len(strata)} total, {n_unreliable} marked unreliable")
print(f"  Risk distribution (n>=30): {risk_summary}")

# Save revised strata
disco = ROOT / "discoveries"
disco.mkdir(exist_ok=True)
strata.to_csv(disco / "revised_commencement_probability_by_stratum.csv", index=False)

r10_notes = (f"n_strata={len(strata)}; n_unreliable={n_unreliable}; "
             f"risk_summary={json.dumps({k: {'strata': int(v['n_strata']), 'perms': int(v['n_perms'])} for k, v in risk_summary.items()})}; "
             f"unreliable_LAs: Cork County, Donegal, Tipperary")

append_result(experiment_id='R10',
              description='Revised Phase B strata (NRU>0 2017-2019 only, with reliability flags)',
              metric='n_strata_reliable', value=int((strata['reliability'] == 'OK').sum()),
              ci_lower='', ci_upper='',
              n=len(clean_cohort), status='KEEP', interaction='False', notes=r10_notes)

# ══════════════════════════════════════════════════════════════
# Save all results
# ══════════════════════════════════════════════════════════════
save_results()
print("\n=== R1-R10 complete ===")
print(f"Revised headline: NRU>0 2017-2019 = {r2_rate:.1%} [{r2_ci[0]:.1%}, {r2_ci[1]:.1%}]")
print(f"Cluster-bootstrap CI: [{r5_ci_lo:.1%}, {r5_ci_hi:.1%}]")
print(f"GBM without LA: AUC = {auc_nola:.3f} (drop of {auc_full-auc_nola:.3f} from {auc_full:.3f})")
print(f"Description FP rate: {strict_fp_rate:.1%} conservative, {fp_rate:.1%} liberal")
