"""
Tests for the SUMO-based traffic signal HDR harness.

These tests verify:
    1. SUMO environment can be started and stepped
    2. Scenarios are well-formed and produce vehicles
    3. Webster plan computation is sane
    4. Webster baseline controller runs a full episode
    5. Controller contract: reset + act on rich obs dict
    6. Episode metrics are non-negative
    7. Phase-lane mask shape is correct
    8. SOTL controller beats Webster on uniform_med (smoke check)
"""

import os
import sys
from pathlib import Path

# SUMO setup
if "SUMO_HOME" not in os.environ:
    for candidate in ("/usr/share/sumo", "/usr/local/share/sumo"):
        if Path(candidate).exists():
            os.environ["SUMO_HOME"] = candidate
            break

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from evaluate import (  # noqa: E402
    DEFAULT_NET,
    DELTA_TIME,
    MIN_GREEN,
    SCENARIOS,
    SIM_HORIZON,
    WebsterFixedTimeController,
    _make_env,
    build_phase_lane_mask,
    build_rich_obs,
    compute_webster_plan,
    run_episode,
    webster_cycle,
)
from controller import Controller  # noqa: E402


# ─────────────────────────────────────────────────────────────
# 1. SUMO environment boots and steps
# ─────────────────────────────────────────────────────────────

def test_sumo_env_runs_one_scenario():
    """Sanity check: the default net loads and runs a short episode."""
    scen = SCENARIOS["uniform_med"]
    env = _make_env(scen, seed=0, horizon=60)
    try:
        obs, info = env.reset()
        assert obs is not None
        # One step with phase 0
        obs, reward, term, trunc, info = env.step(0)
        assert "system_total_waiting_time" in info
        assert info["step"] > 0
    finally:
        env.close()


# ─────────────────────────────────────────────────────────────
# 2. Scenarios are valid
# ─────────────────────────────────────────────────────────────

def test_all_scenarios_have_valid_files():
    """Every scenario in SCENARIOS must have an existing net and route file."""
    for key, scen in SCENARIOS.items():
        assert Path(scen["net"]).exists(), f"{key}: net missing"
        assert Path(scen["rou"]).exists(), f"{key}: route file missing"


def test_scenarios_generate_vehicles():
    """Each scenario should produce at least some vehicles in a 60s run."""
    for key, scen in SCENARIOS.items():
        env = _make_env(scen, seed=0, horizon=60)
        try:
            env.reset()
            done = False
            seen_any = False
            while not done:
                _, _, term, trunc, info = env.step(0)
                if info.get("system_total_stopped", 0) > 0 or len(env.sumo.vehicle.getIDList()) > 0:
                    seen_any = True
                done = term or trunc
            assert seen_any, f"{key}: no vehicles appeared"
        finally:
            env.close()


# ─────────────────────────────────────────────────────────────
# 3. Webster formula and plan
# ─────────────────────────────────────────────────────────────

def test_webster_cycle_formula_sanity():
    C = webster_cycle([0.2, 0.2, 0.15, 0.15])
    assert 30 <= C <= 150, f"cycle={C}"
    C_heavy = webster_cycle([0.35, 0.35, 0.1, 0.1])
    C_light = webster_cycle([0.05, 0.05, 0.05, 0.05])
    assert C_light < C_heavy


def test_webster_plan_has_expected_shape():
    scen = SCENARIOS["uniform_med"]
    plan = compute_webster_plan(scen)
    assert 20 <= plan.cycle <= 200
    assert plan.y_per_phase.shape == (4,)
    assert plan.green_per_phase.shape == (4,)
    assert (plan.green_per_phase >= MIN_GREEN).all()


def test_webster_asymmetric_gives_longer_major_phase():
    scen = SCENARIOS["asymmetric"]  # NS heavy, EW light
    plan = compute_webster_plan(scen)
    # Phases 0,1 serve NS; phases 2,3 serve EW. NS should get more green.
    ns_total = plan.green_per_phase[0] + plan.green_per_phase[1]
    ew_total = plan.green_per_phase[2] + plan.green_per_phase[3]
    assert ns_total > ew_total, f"ns={ns_total} ew={ew_total}"


# ─────────────────────────────────────────────────────────────
# 4. Webster baseline runs a full episode
# ─────────────────────────────────────────────────────────────

def test_webster_baseline_runs_full_episode():
    scen = SCENARIOS["uniform_med"]
    ctrl = WebsterFixedTimeController(scenario=scen)
    m = run_episode(ctrl, scen, seed=0, horizon=120)
    assert m.awt >= 0
    assert m.aql >= 0
    assert m.phase_switches > 0  # should have cycled


# ─────────────────────────────────────────────────────────────
# 5. Controller contract
# ─────────────────────────────────────────────────────────────

def test_controller_has_required_api():
    c = Controller()
    assert hasattr(c, "reset")
    assert hasattr(c, "act")


def test_controller_reset_and_act_on_rich_obs():
    """Build a tiny env, get one obs via build_rich_obs, call controller.act."""
    scen = SCENARIOS["uniform_med"]
    env = _make_env(scen, seed=0, horizon=30)
    try:
        env.reset()
        ts = env.traffic_signals[env.ts_ids[0]]
        mask = build_phase_lane_mask(ts)
        obs = build_rich_obs(ts, env.sim_step, mask)
        # All expected keys
        for key in ["phase_one_hot", "current_phase", "num_green_phases",
                    "min_green_flag", "time_since_last_phase_change",
                    "lane_density", "lane_queue", "lane_queue_count",
                    "lane_veh_count", "lane_ids", "phase_lane_mask", "t"]:
            assert key in obs, f"missing key {key}"
        c = Controller()
        c.reset(env)
        action = c.act(obs)
        assert isinstance(action, (int, np.integer))
        assert 0 <= int(action) < obs["num_green_phases"]
    finally:
        env.close()


def test_controller_runs_full_episode():
    scen = SCENARIOS["uniform_med"]
    m = run_episode(Controller(), scen, seed=0, horizon=120)
    assert m.awt >= 0
    assert m.aql >= 0


# ─────────────────────────────────────────────────────────────
# 6. Phase-lane mask
# ─────────────────────────────────────────────────────────────

def test_phase_lane_mask_shape_and_coverage():
    scen = SCENARIOS["uniform_med"]
    env = _make_env(scen, seed=0, horizon=20)
    try:
        env.reset()
        ts = env.traffic_signals[env.ts_ids[0]]
        mask = build_phase_lane_mask(ts)
        assert mask.shape == (ts.num_green_phases, len(ts.lanes))
        # Every phase should serve at least one lane
        assert (mask.sum(axis=1) > 0).all()
        # Every lane should be served by at least one phase (no orphans)
        assert (mask.sum(axis=0) > 0).all()
    finally:
        env.close()


# ─────────────────────────────────────────────────────────────
# 7. Metric positivity
# ─────────────────────────────────────────────────────────────

def test_episode_metrics_are_nonnegative():
    scen = SCENARIOS["uniform_med"]
    m = run_episode(WebsterFixedTimeController(scenario=scen), scen, seed=0, horizon=120)
    assert m.awt >= 0
    assert m.aql >= 0
    assert m.peak_queue >= 0
    assert m.phase_switches >= 0


# ─────────────────────────────────────────────────────────────
# 8. SOTL vs Webster smoke check
# ─────────────────────────────────────────────────────────────

def test_sotl_does_not_crash_on_uniform_med():
    """SOTL should complete an episode and produce finite metrics."""
    scen = SCENARIOS["uniform_med"]
    m = run_episode(Controller(), scen, seed=0, horizon=120)
    assert np.isfinite(m.awt)
    assert m.awt < 200  # should not diverge


def test_sotl_beats_or_matches_webster_on_medium_demand():
    """Regression smoke check: SOTL should not be 2× worse than Webster.
    We use a short horizon so this runs fast, and a loose bound since a
    single seed on short horizons is noisy.
    """
    scen = SCENARIOS["uniform_med"]
    wb_awt = run_episode(WebsterFixedTimeController(scenario=scen), scen, seed=0, horizon=180).awt
    sotl_awt = run_episode(Controller(), scen, seed=0, horizon=180).awt
    assert sotl_awt < 2 * wb_awt + 5.0, \
        f"SOTL={sotl_awt} vs Webster={wb_awt} (expected SOTL <= 2x Webster)"
