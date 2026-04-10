"""Plug-in control policy library for the ring-road phantom jam simulator.

Each controller takes (own_v, lead_v, gap, dt) and returns an acceleration
in m/s^2.  Controllers are callables with a common signature so the
simulator can mix-and-match human and smart vehicles.

References
----------
- Treiber, Hennecke, Helbing (2000), "Congested traffic states in empirical
  observations and microscopic simulations", Physical Review E 62(2).
  (IDM original paper)
- Stern et al. (2018), "Dissipation of stop-and-go waves via control of
  autonomous vehicles: Field experiments", Transportation Research Part C 89.
  (FollowerStopper and PIWithSaturation controllers)
- Milanes & Shladover (2014), "Modeling cooperative and autonomous adaptive
  cruise control dynamic responses using experimental data",
  Transportation Research Part C 48.
  (ACC constant time-headway model)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np


# ---------------------------------------------------------------------------
# Controller protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class Controller(Protocol):
    """Common interface every controller must satisfy."""

    name: str

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        """Return longitudinal acceleration (m/s^2)."""
        ...


# ---------------------------------------------------------------------------
# Physical clamps shared by all controllers
# ---------------------------------------------------------------------------

_MAX_ACCEL = 3.0   # m/s^2  (physical vehicle limit)
_MAX_DECEL = -9.0  # m/s^2  (hard braking limit)


def _clamp(a: float) -> float:
    return float(np.clip(a, _MAX_DECEL, _MAX_ACCEL))


# ---------------------------------------------------------------------------
# 1. IDMController — Intelligent Driver Model (Treiber et al. 2000)
# ---------------------------------------------------------------------------

@dataclass
class IDMController:
    """Intelligent Driver Model.

    Default parameters from Treiber et al. (2000), Table I, also used in
    Sugiyama (2008) ring-road reproduction studies.

    Parameters
    ----------
    v0 : float  — desired speed (m/s)
    T  : float  — safe time headway (s)
    a  : float  — maximum acceleration (m/s^2)
    b  : float  — comfortable deceleration (m/s^2)
    delta : float — acceleration exponent
    s0 : float  — minimum jam distance (m)
    """

    v0: float = 30.0
    T: float = 1.5
    a: float = 1.3
    b: float = 2.0
    delta: float = 4.0
    s0: float = 2.0
    name: str = "IDM"

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        dv = own_v - lead_v
        # Desired gap (Eq. 3 in Treiber 2000)
        s_star = self.s0 + max(0.0,
                                own_v * self.T
                                + own_v * dv / (2.0 * np.sqrt(self.a * self.b)))
        # Acceleration (Eq. 2)
        if gap < 0.01:
            gap = 0.01  # avoid division by zero
        accel = self.a * (1.0
                          - (own_v / self.v0) ** self.delta
                          - (s_star / gap) ** 2)
        return _clamp(accel)

    def steady_state_gap(self, v: float | None = None) -> float:
        """Return the gap at which acceleration = 0 for speed *v* (default v0).

        Useful for unit testing: when own_v = lead_v = v and gap = this value,
        the IDM should produce zero acceleration.
        """
        if v is None:
            v = self.v0
        s_star = self.s0 + v * self.T
        # a * (1 - (v/v0)^delta - (s_star/gap)^2) = 0
        # => (s_star/gap)^2 = 1 - (v/v0)^delta
        ratio = 1.0 - (v / self.v0) ** self.delta
        if ratio <= 0:
            return float("inf")
        return s_star / np.sqrt(ratio)


# ---------------------------------------------------------------------------
# 2. FollowerStopper — Stern et al. (2018), Section 3.A
# ---------------------------------------------------------------------------

@dataclass
class FollowerStopper:
    """FollowerStopper controller from the CIRCLES field experiments.

    Uses a desired-velocity curve U(s, dv) that smoothly reduces speed
    as the gap drops below safety thresholds.

    Reference: Stern et al. (2018), Eq. (2)-(4).

    The three regions are defined by gap thresholds:
        s_go  : above this, cruise at desired speed
        s_st  : below this, target velocity is zero (stop)
    Between s_st and s_go the target follows a quadratic ramp.
    """

    v_des: float = 15.0   # desired cruising speed (m/s)
    s_st: float = 5.0     # stop gap (m)
    s_go: float = 35.0    # free-flow gap (m)
    k_v: float = 0.5      # proportional gain on velocity error
    name: str = "FollowerStopper"

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        # Desired velocity from gap (Stern 2018, Eq. 2-4)
        if gap <= self.s_st:
            v_cmd = 0.0
        elif gap >= self.s_go:
            v_cmd = self.v_des
        else:
            # Quadratic interpolation
            frac = (gap - self.s_st) / (self.s_go - self.s_st)
            v_cmd = self.v_des * frac ** 2
        accel = self.k_v * (v_cmd - own_v)
        return _clamp(accel)


# ---------------------------------------------------------------------------
# 3. PIWithSaturation — Stern et al. (2018), Section 3.B
# ---------------------------------------------------------------------------

@dataclass
class PIWithSaturation:
    """PI controller with saturation (CIRCLES baseline).

    Tracks a desired time-headway by adjusting acceleration with
    proportional + integral terms, saturated to physical limits.

    Reference: Stern et al. (2018), "PI with saturation" variant.
    """

    T_des: float = 1.5      # desired time headway (s)
    s0: float = 5.0          # minimum jam distance (m)
    k_p: float = 0.4         # proportional gain
    k_i: float = 0.02        # integral gain
    a_max: float = 1.3       # saturation: max accel (m/s^2)
    a_min: float = -2.0      # saturation: max decel (m/s^2)
    name: str = "PIWithSaturation"
    _integral: float = field(default=0.0, init=False, repr=False)

    def reset(self) -> None:
        self._integral = 0.0

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        # Gap error: desired gap minus actual gap
        desired_gap = self.s0 + own_v * self.T_des
        error = desired_gap - gap
        self._integral += error * dt
        accel = -self.k_p * error - self.k_i * self._integral
        # Saturate to physical limits
        accel = float(np.clip(accel, self.a_min, self.a_max))
        return _clamp(accel)


# ---------------------------------------------------------------------------
# 4. ACCController — Adaptive Cruise Control (constant time-headway)
# ---------------------------------------------------------------------------

@dataclass
class ACCController:
    """Simple Adaptive Cruise Control.

    Constant time-headway policy: adjust speed to maintain a gap of
    s0 + v * T_des.  Uses lower gains than IDM, mimicking commercial ACC.

    Reference: Milanes & Shladover (2014), cooperative ACC model simplified.
    """

    v_des: float = 20.0    # desired cruise speed (m/s)
    T_des: float = 1.8     # desired time headway (s)
    s0: float = 4.0        # minimum standstill gap (m)
    k1: float = 0.3        # gap-error gain
    k2: float = 0.5        # speed-difference gain
    name: str = "ACC"

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        desired_gap = self.s0 + own_v * self.T_des
        accel = self.k1 * (gap - desired_gap) + self.k2 * (lead_v - own_v)
        # Also gently cruise towards v_des if no one is close
        if gap > 3.0 * desired_gap:
            accel += 0.2 * (self.v_des - own_v)
        return _clamp(accel)


# ---------------------------------------------------------------------------
# 5. ConstantVelocityController — simplest possible smart vehicle
# ---------------------------------------------------------------------------

@dataclass
class ConstantVelocityController:
    """Maintain a constant velocity regardless of the leader.

    The simplest possible "smart" vehicle.  Useful as a lower bound.
    Acceleration is a P-controller towards v_target.
    """

    v_target: float = 8.0   # target speed (m/s)
    k_p: float = 1.0        # P gain
    name: str = "ConstantVelocity"

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        accel = self.k_p * (self.v_target - own_v)
        return _clamp(accel)


# ---------------------------------------------------------------------------
# 6. PlaceholderRLController — stub for Phase 2 RL integration
# ---------------------------------------------------------------------------

@dataclass
class PlaceholderRLController:
    """Stub for a learned RL policy.

    Currently returns zero acceleration.  Phase 2 will replace the
    __call__ body with a neural network forward pass.

    The signature matches the Controller protocol so it can be dropped
    into the simulator without changes.
    """

    name: str = "PlaceholderRL"

    def __call__(self, own_v: float, lead_v: float, gap: float,
                 dt: float) -> float:
        # TODO(Phase 2): load ONNX / PyTorch policy, call forward pass
        return 0.0


# ---------------------------------------------------------------------------
# Registry: handy list of all controllers
# ---------------------------------------------------------------------------

ALL_CONTROLLERS = [
    IDMController,
    FollowerStopper,
    PIWithSaturation,
    ACCController,
    ConstantVelocityController,
    PlaceholderRLController,
]


def make_controller(name: str, **kwargs) -> Controller:
    """Factory: create a controller by short name."""
    registry = {cls.__name__: cls for cls in ALL_CONTROLLERS}
    # Also allow lookup by .name attribute defaults
    for cls in ALL_CONTROLLERS:
        instance = cls()
        registry[instance.name] = cls
    if name not in registry:
        raise ValueError(f"Unknown controller: {name!r}. "
                         f"Available: {sorted(registry.keys())}")
    return registry[name](**kwargs)
