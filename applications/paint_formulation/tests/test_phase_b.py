"""Tests for phase_b_discovery.py — candidate generation and screening."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import phase_b_discovery  # noqa: E402


def test_voc_model_basic():
    # High-solids (all solids maxed) -> low VOC
    low = phase_b_discovery.estimate_voc_g_per_L({
        "crosslink": 1.0, "cyc_nco_frac": 1.0,
        "matting_agent": 1.0, "pigment_paste": 1.0, "thickness_um": 45,
    })
    # Low-solids -> high VOC
    high = phase_b_discovery.estimate_voc_g_per_L({
        "crosslink": 0.0, "cyc_nco_frac": 0.0,
        "matting_agent": 0.0, "pigment_paste": 0.0, "thickness_um": 45,
    })
    assert low < high, "higher solids should mean lower VOC"
    assert 0 <= low < 400
    assert 0 < high <= 500


def test_cost_model_basic():
    c = phase_b_discovery.estimate_cost_usd_per_kg({
        "crosslink": 0.5, "cyc_nco_frac": 0.5,
        "matting_agent": 0.5, "pigment_paste": 0.5, "thickness_um": 45,
    })
    assert 1 < c < 20


def test_generate_candidates_size():
    cands = phase_b_discovery.generate_candidates()
    assert len(cands) > 2000, f"too few candidates: {len(cands)}"
    # Check all have required keys
    required = {"crosslink", "cyc_nco_frac", "matting_agent",
                "pigment_paste", "thickness_um", "source"}
    for c in cands[:50]:
        assert required.issubset(c.keys())


def test_pareto_front_trivial():
    df = pd.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": [5, 4, 3, 2, 1],
    })
    # Anti-correlated: the point with max x also has min y, so it
    # single-handedly dominates everything else.
    pf = phase_b_discovery.pareto_front(df, "x", "y")
    assert len(pf) == 1
    assert pf.iloc[0]["x"] == 5
    assert pf.iloc[0]["y"] == 1


def test_pareto_front_trade_off():
    # A proper Pareto frontier: correlated x and y
    df = pd.DataFrame({
        "gloss":  [80, 70, 60, 50, 90],
        "voc":    [100, 80, 60, 40, 200],
    })
    # max gloss & min voc: dominance test
    pf = phase_b_discovery.pareto_front(df, "gloss", "voc")
    # (50, 40) dominates no one else on both axes -> on front
    # (60, 60) dominates (70, 80) and (80, 100)? 60 < 70 on gloss so NO
    # frontier = strictly non-dominated points
    # (50,40): min voc, needs to see if anyone has higher gloss AND lower voc -> no -> on front
    # (60,60): higher gloss than 50, lower voc than 70/80/90 -> dominates none on front
    #   need: anyone with gloss>=60 AND voc<=60? Only (60,60) itself. -> on front
    # (70,80): anyone with gloss>=70 AND voc<=80? (90, 200) no, (80,100) no. -> on front
    # (80,100): anyone with gloss>=80 AND voc<=100? (90, 200) no. -> on front
    # (90,200): anyone with gloss>=90 AND voc<=200? None. -> on front
    # So all 5 are on the front.
    assert len(pf) == 5


def test_pareto_with_dominated_points():
    df = pd.DataFrame({
        "gloss": [80, 60, 70, 50, 85],
        "voc": [100, 50, 75, 150, 200],
    })
    # Maximise gloss, minimise voc
    pf = phase_b_discovery.pareto_front(df, "gloss", "voc")
    # Non-dominated: (60, 50), (70, 75), (80, 100), (85, 200)
    # (50, 150) is dominated by (70, 75)
    vocs = sorted(pf["voc"].tolist())
    assert 50 in vocs
    assert 75 in vocs
    assert 100 in vocs
    assert 200 in vocs
    assert 150 not in vocs
