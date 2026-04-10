"""Ring-road phantom traffic jam simulator — pure-Python IDM integration.

Implements:
- N-vehicle ring of circumference L (e.g. 22 vehicles on 230 m for Sugiyama,
  or up to 200 vehicles on 2 km for larger experiments)
- IDM (Intelligent Driver Model) as the default human driver model
- Ability to insert M <= N controlled "smart" vehicles with a pluggable
  control policy from controllers.py
- Measurement hooks: per-vehicle (time, position, velocity, acceleration,
  spacing), aggregated (density, mean velocity, velocity variance,
  stop-and-go wave amplitude, wave propagation speed)
- Deterministic seed for reproducibility
- Configurable run length (typically 600 s)
- Returns a pandas DataFrame with one row per (vehicle x 0.1-s step)

Simulator choice: pure-Python with forward-Euler integration at dt=0.1 s.
This is chosen over SUMO because the ring-road is a 1-D continuous-time ODE
system where forward Euler at 0.1 s is well within stability limits for IDM
(the IDM's maximum jerk is ~a/T ~ 0.87 m/s^3, giving characteristic
timescale >> 0.1 s).  The trade-off: forward Euler is O(dt) accurate and
will accumulate phase error over very long runs, but for 600 s simulations
this is negligible.

References
----------
- Sugiyama et al. (2008), "Traffic jams without bottlenecks — experimental
  evidence for the physical mechanism of the formation of a jam",
  New Journal of Physics 10, 033001.
- Treiber, Hennecke, Helbing (2000), "Congested traffic states in empirical
  observations and microscopic simulations", Physical Review E 62(2).

IDM parameters for ring-road instability:
    v0    = 30.0   m/s     desired speed
    T     = 1.0    s       time headway (reduced from 1.5 to push the system
                           into the string-unstable regime at Sugiyama density;
                           see Treiber & Kesting 2013, Ch. 15)
    a     = 1.3    m/s^2   max acceleration
    b     = 2.0    m/s^2   comfortable deceleration
    delta = 4.0            acceleration exponent
    s0    = 2.0    m       minimum spacing
    veh_length = 5.0 m
    noise_std = 0.3 m/s^2  acceleration noise (Gaussian, per-vehicle per-step)

Note on parameter tuning: the original Treiber (2000) T=1.5 s yields an
equilibrium speed of only ~2.3 m/s on the 22/230 ring, which is linearly
stable.  Reducing T to 1.0 s raises v_eq to ~3.5 m/s and puts the system
exactly at the stability boundary.  Adding stochastic noise (sigma=0.3)
then reliably triggers stop-and-go waves, matching the Sugiyama experiment
qualitatively.  This approach follows Stern et al. (2018) and the Flow
ring-road benchmark configurations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np
import pandas as pd

from controllers import Controller, IDMController


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class RingRoadConfig:
    """Parameters for a ring-road experiment."""

    n_vehicles: int = 22
    ring_length: float = 230.0          # metres
    veh_length: float = 5.0             # metres
    dt: float = 0.1                     # integration timestep (s)
    t_max: float = 600.0                # total simulation time (s)
    seed: int = 42

    # IDM parameters for human drivers (tuned for ring-road instability)
    idm_v0: float = 30.0               # desired speed (m/s)
    idm_T: float = 1.0                 # time headway (s) — reduced for instability
    idm_a: float = 1.3                 # max accel (m/s^2)
    idm_b: float = 2.0                 # comfortable decel (m/s^2)
    idm_delta: float = 4.0             # accel exponent
    idm_s0: float = 2.0                # minimum spacing (m)

    # Stochastic noise on human-driver acceleration (Gaussian, per step)
    noise_std: float = 0.3             # m/s^2

    # Perturbation to trigger the jam
    perturb_vehicle: int = 0            # which vehicle index to brake
    perturb_time: float = 5.0           # when to apply the perturbation (s)
    perturb_decel: float = -5.0         # m/s^2, applied for one timestep


# ---------------------------------------------------------------------------
# Simulation state
# ---------------------------------------------------------------------------

@dataclass
class _VehicleState:
    position: float       # distance along ring from origin (m)
    velocity: float       # m/s
    controller: Any       # Controller instance
    is_smart: bool = False
    vehicle_id: int = 0


# ---------------------------------------------------------------------------
# Core simulator
# ---------------------------------------------------------------------------

def _gap(pos_self: float, pos_leader: float, ring_length: float,
         veh_length: float) -> float:
    """Bumper-to-bumper gap on a ring (leader is next car ahead)."""
    raw = (pos_leader - pos_self) % ring_length - veh_length
    return max(raw, 0.01)   # prevent non-physical negative gaps


def simulate(
    cfg: RingRoadConfig | None = None,
    smart_indices: Sequence[int] = (),
    smart_controller_factory: Any = None,
) -> pd.DataFrame:
    """Run the ring-road simulation and return a trajectory DataFrame.

    Parameters
    ----------
    cfg : RingRoadConfig
        Simulation configuration.  Defaults to the 22-vehicle / 230-m
        Sugiyama configuration.
    smart_indices : sequence of int
        Indices of vehicles to replace with smart controllers.
    smart_controller_factory : callable or None
        A zero-argument callable that returns a Controller instance.
        Called once per smart vehicle.  If None, smart_indices is ignored.

    Returns
    -------
    pd.DataFrame
        Columns: time, vehicle_id, position, velocity, acceleration, gap,
                 is_smart.  One row per (vehicle x timestep).
    """
    if cfg is None:
        cfg = RingRoadConfig()

    rng = np.random.RandomState(cfg.seed)

    # Initialize vehicles — evenly spaced, with small random velocity
    # perturbation to break symmetry
    spacing = cfg.ring_length / cfg.n_vehicles
    base_v = min(spacing - cfg.veh_length, 10.0)  # conservative initial speed
    # For Sugiyama (230 m / 22 veh), spacing ~10.45 m, base_v ~5.45 m/s

    # Build the default human-driver IDM with the config's parameters
    def _make_human_idm() -> IDMController:
        return IDMController(
            v0=cfg.idm_v0, T=cfg.idm_T, a=cfg.idm_a,
            b=cfg.idm_b, delta=cfg.idm_delta, s0=cfg.idm_s0,
        )

    smart_set = set(smart_indices)
    vehicles: list[_VehicleState] = []
    for i in range(cfg.n_vehicles):
        pos = i * spacing
        vel = max(0.0, base_v + rng.uniform(-0.5, 0.5))
        if i in smart_set and smart_controller_factory is not None:
            ctrl = smart_controller_factory()
            is_smart = True
        else:
            ctrl = _make_human_idm()
            is_smart = False
        vehicles.append(_VehicleState(
            position=pos, velocity=vel, controller=ctrl,
            is_smart=is_smart, vehicle_id=i,
        ))

    # Pre-allocate output arrays
    n_steps = int(cfg.t_max / cfg.dt) + 1
    n_veh = cfg.n_vehicles
    total_rows = n_steps * n_veh

    times = np.empty(total_rows, dtype=np.float64)
    veh_ids = np.empty(total_rows, dtype=np.int32)
    positions = np.empty(total_rows, dtype=np.float64)
    velocities = np.empty(total_rows, dtype=np.float64)
    accelerations = np.empty(total_rows, dtype=np.float64)
    gaps = np.empty(total_rows, dtype=np.float64)
    is_smart_arr = np.empty(total_rows, dtype=np.bool_)

    # Vehicles are ordered by position.  Vehicle i's leader is vehicle
    # (i+1) % n_veh (the ring wraps around).
    row = 0
    for step in range(n_steps):
        t = step * cfg.dt

        # Compute gaps and accelerations
        accels = np.empty(n_veh, dtype=np.float64)
        gap_arr = np.empty(n_veh, dtype=np.float64)
        for i in range(n_veh):
            leader_idx = (i + 1) % n_veh
            g = _gap(vehicles[i].position, vehicles[leader_idx].position,
                     cfg.ring_length, cfg.veh_length)
            gap_arr[i] = g
            acc = vehicles[i].controller(
                own_v=vehicles[i].velocity,
                lead_v=vehicles[leader_idx].velocity,
                gap=g,
                dt=cfg.dt,
            )
            accels[i] = acc

        # Add stochastic acceleration noise to human drivers
        if cfg.noise_std > 0:
            for i in range(n_veh):
                if not vehicles[i].is_smart:
                    noise = rng.normal(0.0, cfg.noise_std)
                    accels[i] = float(np.clip(
                        accels[i] + noise, -9.0, 3.0
                    ))

        # Apply perturbation (single-timestep brake) to trigger the jam
        if abs(t - cfg.perturb_time) < cfg.dt / 2:
            accels[cfg.perturb_vehicle] = cfg.perturb_decel

        # Record state
        for i in range(n_veh):
            times[row] = t
            veh_ids[row] = vehicles[i].vehicle_id
            positions[row] = vehicles[i].position
            velocities[row] = vehicles[i].velocity
            accelerations[row] = accels[i]
            gaps[row] = gap_arr[i]
            is_smart_arr[row] = vehicles[i].is_smart
            row += 1

        # Forward-Euler integration
        for i in range(n_veh):
            vehicles[i].velocity = max(0.0,
                                       vehicles[i].velocity + accels[i] * cfg.dt)
            vehicles[i].position = (
                (vehicles[i].position + vehicles[i].velocity * cfg.dt)
                % cfg.ring_length
            )

    df = pd.DataFrame({
        "time": times[:row],
        "vehicle_id": veh_ids[:row],
        "position": positions[:row],
        "velocity": velocities[:row],
        "acceleration": accelerations[:row],
        "gap": gaps[:row],
        "is_smart": is_smart_arr[:row],
    })
    return df


# ---------------------------------------------------------------------------
# Convenience: default Sugiyama run
# ---------------------------------------------------------------------------

def run_sugiyama_baseline(seed: int = 42, t_max: float = 600.0) -> pd.DataFrame:
    """Run the canonical 22-vehicle / 230-m ring-road with all IDM drivers."""
    cfg = RingRoadConfig(
        n_vehicles=22,
        ring_length=230.0,
        t_max=t_max,
        seed=seed,
    )
    return simulate(cfg)


# ---------------------------------------------------------------------------
# Smoke test: verify the ring produces a stop-and-go wave
# ---------------------------------------------------------------------------

def _smoke_test() -> None:
    """Quick verification that the baseline produces a wave."""
    print("Running 22-vehicle / 230-m ring-road for 300 s ...")
    cfg = RingRoadConfig(t_max=300.0)
    df = simulate(cfg)

    # Measure wave amplitude in the last 100 s (after wave has developed)
    late = df[df["time"] >= 200.0]
    per_step = late.groupby("time")["velocity"]
    v_range_per_step = per_step.max() - per_step.min()
    mean_amplitude = v_range_per_step.mean()
    max_amplitude = v_range_per_step.max()

    mean_v = late["velocity"].mean()
    std_v = late["velocity"].std()

    print(f"  Mean velocity:     {mean_v:.2f} m/s")
    print(f"  Velocity std:      {std_v:.2f} m/s")
    print(f"  Mean v-range:      {mean_amplitude:.2f} m/s")
    print(f"  Max v-range:       {max_amplitude:.2f} m/s")

    if mean_amplitude > 2.0:
        print("  PASS: stop-and-go wave detected (amplitude > 2 m/s)")
    else:
        print("  WARNING: wave amplitude is low — may need parameter tuning")

    # Estimate wave propagation speed using velocity minimum tracking
    # The velocity minimum (the "jam") propagates backwards around the ring
    late_pivot = late.pivot(index="time", columns="vehicle_id",
                           values="velocity")
    times = late_pivot.index.values
    min_veh = late_pivot.idxmin(axis=1).values  # vehicle with lowest v each step

    # Get position of the minimum-velocity vehicle
    pos_pivot = late.pivot(index="time", columns="vehicle_id",
                           values="position")
    jam_positions = np.array([
        pos_pivot.loc[t, min_veh[i]] for i, t in enumerate(times)
    ])

    # Unwrap the ring positions and estimate propagation speed
    jam_pos_unwrapped = np.unwrap(jam_positions * 2 * np.pi / cfg.ring_length
                                  ) * cfg.ring_length / (2 * np.pi)
    if len(times) > 10:
        from scipy.stats import linregress
        slope, _, _, _, _ = linregress(times, jam_pos_unwrapped)
        print(f"  Wave propagation speed: {slope:.2f} m/s "
              f"(negative = upstream)")
    print()


if __name__ == "__main__":
    _smoke_test()
