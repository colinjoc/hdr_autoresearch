#!/usr/bin/env python3
"""
tests/test_r1_r10.py — Tests for Phase 2.75 mandated experiments R1-R10.
Verifies that each experiment produces a results row and the values are plausible.
"""
import pandas as pd
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_TSV = ROOT / "results.tsv"


@pytest.fixture(scope="module")
def results():
    """Load results.tsv after R1-R10 have been appended."""
    assert RESULTS_TSV.exists(), "results.tsv not found — run r1_r10_experiments.py first"
    return pd.read_csv(RESULTS_TSV, sep='\t')


def test_r1_exists(results):
    assert 'R1' in results['experiment_id'].values, "R1 not in results.tsv"


def test_r2_exists_and_value(results):
    row = results[results['experiment_id'] == 'R2']
    assert len(row) == 1, "R2 not in results.tsv"
    val = float(row.iloc[0]['value'])
    # NRU>0 lapse rate should be 5-20%
    assert 0.03 < val < 0.25, f"R2 NRU>0 headline {val:.3f} outside plausible range"


def test_r3_exists(results):
    assert 'R3' in results['experiment_id'].values, "R3 not in results.tsv"


def test_r4_exists_and_value(results):
    row = results[results['experiment_id'] == 'R4']
    assert len(row) == 1, "R4 not in results.tsv"
    val = float(row.iloc[0]['value'])
    # 2016-2019 rate excluding early BCMS years should be lower than full 27.4%
    assert 0.05 < val < 0.35, f"R4 value {val:.3f} outside plausible range"


def test_r5_exists(results):
    row = results[results['experiment_id'] == 'R5']
    assert len(row) == 1, "R5 not in results.tsv"
    # CI should be wider than IID Wilson CI
    ci_lo = float(row.iloc[0]['ci_lower'])
    ci_hi = float(row.iloc[0]['ci_upper'])
    assert ci_hi > ci_lo, "R5 CI invalid"
    assert ci_hi - ci_lo > 0.005, "R5 cluster-bootstrap CI suspiciously narrow"


def test_r6_exists(results):
    row = results[results['experiment_id'] == 'R6']
    assert len(row) == 1, "R6 not in results.tsv"
    val = float(row.iloc[0]['value'])
    # Without la_enc, AUC should drop substantially
    assert 0.45 < val < 0.85, f"R6 AUC {val:.3f} outside expected range"


def test_r7_exists(results):
    assert 'R7' in results['experiment_id'].values, "R7 not in results.tsv"


def test_r8_exists(results):
    assert 'R8' in results['experiment_id'].values, "R8 not in results.tsv"


def test_r9_exists(results):
    assert 'R9' in results['experiment_id'].values, "R9 not in results.tsv"


def test_r10_exists(results):
    assert 'R10' in results['experiment_id'].values, "R10 not in results.tsv"


def test_all_r_experiments_present(results):
    """All 10 mandated experiments must be present."""
    for rid in [f'R{i}' for i in range(1, 11)]:
        assert rid in results['experiment_id'].values, f"{rid} missing from results.tsv"


def test_nru_headline_is_honest(results):
    """R2 headline (NRU>0) should be lower than original E00 headline."""
    e00 = results[results['experiment_id'] == 'E00']
    r2 = results[results['experiment_id'] == 'R2']
    assert len(e00) == 1 and len(r2) == 1
    assert float(r2.iloc[0]['value']) < float(e00.iloc[0]['value']), \
        "R2 (NRU>0 headline) should be lower than E00 (all-cohort headline)"
