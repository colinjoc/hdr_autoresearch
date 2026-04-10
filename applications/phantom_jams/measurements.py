"""Wave-characterisation and traffic performance measurements.

All functions operate on the trajectory DataFrame returned by
sim_ring_road.simulate(), which has columns:
    time, vehicle_id, position, velocity, acceleration, gap, is_smart

References
----------
- Sugiyama et al. (2008), NJP 10 033001 — wave amplitude definition
- Stern et al. (2018), TRC 89 — velocity variance, throughput
- Edie (1963), Operations Research 11(4) — generalised throughput definition
- Rakha et al. (2004), "Virginia Tech Microscopic energy and emission model
  (VT-Micro)", Transportation Research Record 1880 — fuel proxy
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import linregress


# ---------------------------------------------------------------------------
# Wave characteristics
# ---------------------------------------------------------------------------

def compute_wave_characteristics(traj_df: pd.DataFrame,
                                 steady_start: float | None = None,
                                 ring_length: float = 230.0) -> dict:
    """Return wave amplitude, propagation speed, period, velocity-variance
    time series.

    Parameters
    ----------
    traj_df : DataFrame from sim_ring_road.simulate()
    steady_start : float or None
        Start of the analysis window (seconds).  Defaults to the last 2/3
        of the simulation to skip transients.
    ring_length : float
        Ring circumference in metres (needed for wave speed estimation).

    Returns
    -------
    dict with keys:
        wave_amplitude_mean : float (m/s) — mean of per-step max-min velocity
        wave_amplitude_max  : float (m/s) — peak of per-step max-min velocity
        wave_speed          : float (m/s) — estimated upstream propagation speed
        wave_period         : float (s)   — estimated period from FFT
        velocity_variance_ts : pd.Series  — velocity variance indexed by time
    """
    t_max = traj_df["time"].max()
    if steady_start is None:
        steady_start = t_max / 3.0
    late = traj_df[traj_df["time"] >= steady_start].copy()

    # --- Amplitude ---
    per_step = late.groupby("time")["velocity"]
    v_range = per_step.max() - per_step.min()
    amp_mean = float(v_range.mean())
    amp_max = float(v_range.max())

    # --- Velocity variance time series ---
    v_var = per_step.var()

    # --- Wave propagation speed ---
    # Track the position of the velocity-minimum vehicle over time
    pivot_v = late.pivot_table(index="time", columns="vehicle_id",
                               values="velocity", aggfunc="first")
    pivot_p = late.pivot_table(index="time", columns="vehicle_id",
                               values="position", aggfunc="first")
    times = pivot_v.index.values
    min_veh_ids = pivot_v.idxmin(axis=1)
    jam_pos = np.array([
        pivot_p.loc[t, min_veh_ids.loc[t]]
        for t in times
    ])
    # Unwrap ring positions to remove modular jumps
    jam_unwrapped = np.unwrap(
        jam_pos * 2 * np.pi / ring_length
    ) * ring_length / (2 * np.pi)
    wave_speed = 0.0
    if len(times) > 10:
        slope, _, _, _, _ = linregress(times, jam_unwrapped)
        wave_speed = float(slope)

    # --- Wave period via FFT ---
    # Use mean velocity of all vehicles as a proxy signal
    mean_v_ts = per_step.mean()
    if len(mean_v_ts) > 20:
        signal = mean_v_ts.values - mean_v_ts.values.mean()
        dt = float(np.median(np.diff(mean_v_ts.index.values)))
        fft_mag = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=dt)
        # Skip DC component
        if len(fft_mag) > 1:
            peak_idx = np.argmax(fft_mag[1:]) + 1
            peak_freq = freqs[peak_idx]
            wave_period = 1.0 / peak_freq if peak_freq > 0 else float("inf")
        else:
            wave_period = float("inf")
    else:
        wave_period = float("inf")

    return {
        "wave_amplitude_mean": amp_mean,
        "wave_amplitude_max": amp_max,
        "wave_speed": wave_speed,
        "wave_period": wave_period,
        "velocity_variance_ts": v_var,
    }


# ---------------------------------------------------------------------------
# Throughput (Edie's generalised definition)
# ---------------------------------------------------------------------------

def compute_throughput(traj_df: pd.DataFrame, lane_length: float) -> float:
    """Vehicles per hour past a virtual cross-section.

    Uses Edie's definition: q = N_total_distance / (L * T), converted to
    veh/hr.  For a ring road the denominator is (ring_length * sim_duration).

    Parameters
    ----------
    traj_df : DataFrame from simulate()
    lane_length : float — ring circumference (m)

    Returns
    -------
    float — throughput in vehicles/hour
    """
    dt = traj_df.groupby("vehicle_id")["time"].apply(
        lambda s: s.diff().median()
    ).median()
    total_distance = (traj_df["velocity"] * dt).sum()
    t_range = traj_df["time"].max() - traj_df["time"].min()
    if t_range <= 0 or lane_length <= 0:
        return 0.0
    # Edie: q = total_distance / (L * T) in veh/s, convert to veh/hr
    q = total_distance / (lane_length * t_range) * 3600.0
    return float(q)


# ---------------------------------------------------------------------------
# Mean velocity variance
# ---------------------------------------------------------------------------

def compute_mean_velocity_variance(traj_df: pd.DataFrame,
                                   steady_start: float | None = None) -> float:
    """Standard deviation of velocity across all vehicles in the steady-state
    window.

    Parameters
    ----------
    traj_df : DataFrame from simulate()
    steady_start : float or None
        Defaults to last 2/3 of simulation.

    Returns
    -------
    float — sigma_v (m/s)
    """
    t_max = traj_df["time"].max()
    if steady_start is None:
        steady_start = t_max / 3.0
    late = traj_df[traj_df["time"] >= steady_start]
    return float(late["velocity"].std())


# ---------------------------------------------------------------------------
# Fuel-consumption proxy (VT-Micro inspired)
# ---------------------------------------------------------------------------

def compute_fuel_proxy(traj_df: pd.DataFrame,
                       steady_start: float | None = None) -> float:
    """A VT-Micro style fuel consumption proxy from (v, a).

    Uses the simplified VT-Micro model:
        fuel_rate ~ alpha * v + beta * v * max(a, 0) + gamma * v^3

    where:
        alpha = 0.1 (rolling resistance proxy, mL/m)
        beta  = 0.07 (positive-acceleration penalty, mL*s/(m^2))
        gamma = 3e-6 (aerodynamic drag proxy, mL*s^2/m^3)

    Returns the total fuel consumed per vehicle-km (normalised), in mL/km.

    Reference: Rakha et al. (2004), simplified to speed + acceleration terms.
    """
    t_max = traj_df["time"].max()
    if steady_start is None:
        steady_start = t_max / 3.0
    late = traj_df[traj_df["time"] >= steady_start].copy()

    dt = float(np.median(np.diff(sorted(late["time"].unique()))))
    v = late["velocity"].values
    a = late["acceleration"].values

    alpha = 0.1
    beta = 0.07
    gamma = 3e-6

    # Instantaneous fuel rate (mL/s per vehicle)
    fuel_rate = alpha * v + beta * v * np.maximum(a, 0) + gamma * v ** 3

    total_fuel = float(np.sum(fuel_rate * dt))  # mL total
    total_dist = float(np.sum(v * dt))  # m total distance (all vehicles)
    if total_dist <= 0:
        return 0.0
    # Convert to mL/km (per vehicle-km)
    return total_fuel / total_dist * 1000.0
