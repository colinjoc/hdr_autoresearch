"""Pytest tests for the ring-road phantom jam simulator.

Tests cover:
1. Simulator availability (pure-Python path)
2. Wave creation in the baseline IDM ring
3. Controller sanity (finite, physically bounded accelerations)
4. Measurement reproducibility across identical seeds
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Ensure the application root is on the path
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from sim_ring_road import RingRoadConfig, simulate, run_sugiyama_baseline
from controllers import (
    IDMController,
    FollowerStopper,
    PIWithSaturation,
    ACCController,
    ConstantVelocityController,
    PlaceholderRLController,
)
from measurements import (
    compute_wave_characteristics,
    compute_mean_velocity_variance,
    compute_throughput,
    compute_fuel_proxy,
)


# -----------------------------------------------------------------------
# 1. test_sumo_or_python_available
# -----------------------------------------------------------------------

def test_sumo_or_python_available():
    """Confirm at least the pure-Python simulator path runs without error."""
    cfg = RingRoadConfig(n_vehicles=5, ring_length=50.0, t_max=2.0)
    df = simulate(cfg)
    assert len(df) > 0
    assert "velocity" in df.columns
    assert "position" in df.columns
    assert df["velocity"].notna().all()
    assert (df["velocity"] >= 0).all(), "Velocities must be non-negative"


# -----------------------------------------------------------------------
# 2. test_ring_road_creates_wave
# -----------------------------------------------------------------------

def test_ring_road_creates_wave():
    """Confirm the baseline IDM ring produces a measurable stop-and-go wave.

    The 22-vehicle / 230-m ring should produce a wave with amplitude > 2 m/s
    after sufficient time.  We run for 300 s and check the last 100 s.
    """
    cfg = RingRoadConfig(
        n_vehicles=22,
        ring_length=230.0,
        t_max=300.0,
        seed=42,
    )
    df = simulate(cfg)

    # Check wave amplitude in the last 100 s
    late = df[df["time"] >= 200.0]
    per_step = late.groupby("time")["velocity"]
    v_range = per_step.max() - per_step.min()
    mean_amplitude = v_range.mean()

    assert mean_amplitude > 2.0, (
        f"Expected stop-and-go wave amplitude > 2 m/s, got {mean_amplitude:.2f} m/s. "
        "The ring-road should reliably produce phantom traffic jams."
    )


# -----------------------------------------------------------------------
# 3. test_controllers_sanity
# -----------------------------------------------------------------------

class TestControllersSanity:
    """Each controller returns finite accelerations within physical limits."""

    CONTROLLERS = [
        IDMController(),
        FollowerStopper(),
        PIWithSaturation(),
        ACCController(),
        ConstantVelocityController(),
        PlaceholderRLController(),
    ]

    # Scenarios: (own_v, lead_v, gap)
    SCENARIOS = [
        (10.0, 10.0, 20.0),   # Normal following
        (0.0, 0.0, 5.0),      # Stopped
        (20.0, 0.0, 3.0),     # Emergency braking
        (5.0, 30.0, 50.0),    # Leader is fast, big gap
        (0.1, 0.1, 0.5),      # Very tight spacing
    ]

    @pytest.mark.parametrize("ctrl", CONTROLLERS,
                             ids=[c.name for c in CONTROLLERS])
    def test_finite_and_bounded(self, ctrl):
        """Acceleration must be finite and within [-9, 3] m/s^2."""
        for own_v, lead_v, gap in self.SCENARIOS:
            a = ctrl(own_v, lead_v, gap, dt=0.1)
            assert np.isfinite(a), (
                f"{ctrl.name} returned non-finite accel={a} "
                f"for (v={own_v}, v_lead={lead_v}, gap={gap})"
            )
            assert -9.0 <= a <= 3.0, (
                f"{ctrl.name} returned accel={a:.2f} outside [-9, 3] "
                f"for (v={own_v}, v_lead={lead_v}, gap={gap})"
            )

    def test_idm_steady_state(self):
        """IDM in steady state produces ~zero acceleration at the correct gap."""
        idm = IDMController()
        v = 10.0  # test at 10 m/s
        gap = idm.steady_state_gap(v)
        a = idm(own_v=v, lead_v=v, gap=gap, dt=0.1)
        assert abs(a) < 0.01, (
            f"IDM should produce ~0 accel at steady-state gap={gap:.2f} m, "
            f"got {a:.4f} m/s^2"
        )

    def test_follower_stopper_reduces_accel_below_safety(self):
        """FollowerStopper should decelerate when gap is below s_st."""
        fs = FollowerStopper()
        # Gap well below the stop threshold
        a = fs(own_v=10.0, lead_v=10.0, gap=2.0, dt=0.1)
        # When gap < s_st, v_cmd = 0, so accel should be negative
        assert a < 0.0, (
            f"FollowerStopper should brake when gap=2 < s_st={fs.s_st}, "
            f"got accel={a:.2f}"
        )

    def test_pi_saturates(self):
        """PIWithSaturation should not exceed its saturation limits."""
        pi = PIWithSaturation()
        pi.reset()
        # Very large gap error (should try to accelerate hard)
        a = pi(own_v=0.0, lead_v=0.0, gap=0.5, dt=0.1)
        assert a <= pi.a_max, (
            f"PI should saturate at a_max={pi.a_max}, got {a:.2f}"
        )
        # Very small gap (should try to decelerate hard)
        pi.reset()
        a = pi(own_v=20.0, lead_v=0.0, gap=0.5, dt=0.1)
        assert a >= pi.a_min, (
            f"PI should saturate at a_min={pi.a_min}, got {a:.2f}"
        )


# -----------------------------------------------------------------------
# 4. test_measurements_reproducibility
# -----------------------------------------------------------------------

def test_measurements_reproducibility():
    """Same seed must produce the same wave amplitude and measurements."""
    cfg = RingRoadConfig(
        n_vehicles=22, ring_length=230.0, t_max=120.0, seed=123,
    )
    df1 = simulate(cfg)
    # Reset the PI controller integral state if any (here all IDM, no state)
    cfg2 = RingRoadConfig(
        n_vehicles=22, ring_length=230.0, t_max=120.0, seed=123,
    )
    df2 = simulate(cfg2)

    w1 = compute_wave_characteristics(df1, ring_length=230.0)
    w2 = compute_wave_characteristics(df2, ring_length=230.0)

    assert w1["wave_amplitude_mean"] == pytest.approx(
        w2["wave_amplitude_mean"], abs=1e-10
    ), "Deterministic seed should give identical wave amplitude"

    mv1 = compute_mean_velocity_variance(df1)
    mv2 = compute_mean_velocity_variance(df2)
    assert mv1 == pytest.approx(mv2, abs=1e-10), \
        "Deterministic seed should give identical velocity variance"

    t1 = compute_throughput(df1, lane_length=230.0)
    t2 = compute_throughput(df2, lane_length=230.0)
    assert t1 == pytest.approx(t2, abs=1e-10), \
        "Deterministic seed should give identical throughput"

    f1 = compute_fuel_proxy(df1)
    f2 = compute_fuel_proxy(df2)
    assert f1 == pytest.approx(f2, abs=1e-10), \
        "Deterministic seed should give identical fuel proxy"
