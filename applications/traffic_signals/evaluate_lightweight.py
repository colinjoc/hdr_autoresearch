"""
Traffic signal timing evaluation harness.

Phase A: Benchmark a controller on a panel of demand scenarios
         (uniform low/med/high, peak-hour, asymmetric N-S, stochastic).
Phase B: Multi-seed robustness sweep to compute mean/variance of metrics.

DO NOT MODIFY THIS FILE.
The autoresearch agent only modifies controller.py.

The harness uses a self-contained, lightweight intersection simulator based on:
  - Poisson vehicle arrivals (time-varying rate)
  - Deterministic saturation flow departures with start-up lost time
  - Queue dynamics with per-approach accumulation
  - Standard 4-way, 2-phase (NS / EW) signalised intersection
  - Multi-intersection corridor support (2-intersection arterial) for Phase B

The controller.py file exposes a `Controller` class with:
    reset(intersection) -> None
    act(obs) -> int  (phase index to serve next, gated by min-green)
    name: str        (optional tag for logging)

Usage:
    python evaluate.py              # all phases
    python evaluate.py --benchmark  # Phase A only
    python evaluate.py --robust     # Phase B only
"""

import argparse
import math
import random
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

RESULTS_DIR = Path(__file__).parent / "discoveries"
DT = 1.0                       # simulation step (s)
SIM_HORIZON = 1800             # 30 minutes per episode
SATURATION_FLOW = 1800 / 3600  # veh per second per lane (1800 veh/hr)
START_UP_LOST_TIME = 2.0       # s per phase activation
YELLOW_TIME = 3.0              # s
ALL_RED_TIME = 1.0             # s
MIN_GREEN_TIME = 5.0           # s
MAX_GREEN_TIME = 60.0          # s (safety cap)
LANES_PER_APPROACH = 1         # kept simple
N_APPROACHES = 4               # N, E, S, W
PHASES = {
    0: ("N", "S"),  # phase 0 serves North and South approaches
    1: ("E", "W"),  # phase 1 serves East and West approaches
}
APPROACH_INDEX = {"N": 0, "E": 1, "S": 2, "W": 3}
INDEX_APPROACH = {v: k for k, v in APPROACH_INDEX.items()}


# ─────────────────────────────────────────────────────────────
# Demand generation
# ─────────────────────────────────────────────────────────────

def demand_uniform(rate_veh_hr: float):
    """Constant arrival rate for all four approaches (veh/hr/approach)."""
    rate_per_s = rate_veh_hr / 3600.0

    def fn(t: float, approach: str) -> float:
        return rate_per_s
    return fn


def demand_asymmetric(ns_rate: float, ew_rate: float):
    """Asymmetric N-S vs E-W demand."""
    ns_s = ns_rate / 3600.0
    ew_s = ew_rate / 3600.0

    def fn(t: float, approach: str) -> float:
        return ns_s if approach in ("N", "S") else ew_s
    return fn


def demand_peak_hour(base: float, peak: float, period: float = SIM_HORIZON):
    """Sinusoidal peak-hour pattern: low -> high -> low across the episode."""
    base_s = base / 3600.0
    peak_s = peak / 3600.0

    def fn(t: float, approach: str) -> float:
        frac = 0.5 - 0.5 * math.cos(2 * math.pi * t / period)
        return base_s + (peak_s - base_s) * frac
    return fn


DEMAND_SCENARIOS = {
    "uniform_low": ("Uniform low (300 veh/hr/approach)",
                    demand_uniform(300)),
    "uniform_med": ("Uniform medium (450 veh/hr/approach)",
                    demand_uniform(450)),
    "uniform_high": ("Uniform high (600 veh/hr/approach)",
                     demand_uniform(600)),
    "asymmetric": ("Asymmetric (N-S 700, E-W 200 veh/hr)",
                   demand_asymmetric(700, 200)),
    "peak_hour": ("Peak-hour sinusoid (250 -> 650 veh/hr)",
                  demand_peak_hour(250, 650)),
}


# ─────────────────────────────────────────────────────────────
# Intersection simulator
# ─────────────────────────────────────────────────────────────

@dataclass
class IntersectionState:
    queues: np.ndarray = field(default_factory=lambda: np.zeros(N_APPROACHES))
    cumulative_wait: np.ndarray = field(default_factory=lambda: np.zeros(N_APPROACHES))
    total_vehicles: int = 0
    completed_vehicles: int = 0
    current_phase: int = 0            # 0 = NS green, 1 = EW green
    transition_state: str = "green"   # "green", "yellow", "all_red"
    time_in_phase: float = 0.0
    time_in_transition: float = 0.0
    pending_phase: Optional[int] = None
    start_up_remaining: float = 0.0
    total_phase_switches: int = 0


class Simulator:
    """Single 4-way intersection with 2 phases."""

    def __init__(self, demand_fn: Callable[[float, str], float], seed: int = 0,
                 horizon: float = SIM_HORIZON, min_green: float = MIN_GREEN_TIME):
        self.demand_fn = demand_fn
        self.rng = random.Random(seed)
        self.np_rng = np.random.RandomState(seed)
        self.horizon = horizon
        self.min_green = min_green
        self.state = IntersectionState()
        self.t = 0.0
        self.history: List[Dict] = []

    def reset(self) -> Dict:
        self.state = IntersectionState()
        self.t = 0.0
        self.history.clear()
        return self.observe()

    def observe(self) -> Dict:
        """Observation dict passed to the controller."""
        s = self.state
        active = PHASES[s.current_phase] if s.transition_state == "green" else ()
        return {
            "queues": s.queues.copy(),                     # length-4 array: N, E, S, W
            "current_phase": s.current_phase,
            "phase_is_ns": s.current_phase == 0,
            "time_in_phase": s.time_in_phase,
            "time_in_transition": s.time_in_transition,
            "transition_state": s.transition_state,
            "min_green_satisfied": s.time_in_phase >= self.min_green,
            "active_approaches": active,
            "t": self.t,
            "cumulative_wait": s.cumulative_wait.copy(),
            "total_vehicles": s.total_vehicles,
            "completed_vehicles": s.completed_vehicles,
            "total_phase_switches": s.total_phase_switches,
            "arrival_rates": np.array([self.demand_fn(self.t, a) for a in ["N", "E", "S", "W"]]),
        }

    def _arrivals(self) -> np.ndarray:
        """Poisson arrivals in the current DT step, per approach."""
        arr = np.zeros(N_APPROACHES, dtype=int)
        for a, idx in APPROACH_INDEX.items():
            rate = self.demand_fn(self.t, a)
            arr[idx] = self.np_rng.poisson(rate * DT)
        return arr

    def _departures(self) -> np.ndarray:
        """Service departures during this DT step for the active phase."""
        s = self.state
        dep = np.zeros(N_APPROACHES, dtype=int)
        if s.transition_state != "green":
            return dep
        active = PHASES[s.current_phase]
        # Startup lost time reduces effective service in the first seconds of a green.
        effective = DT
        if s.start_up_remaining > 0:
            lost = min(s.start_up_remaining, DT)
            effective = DT - lost
            s.start_up_remaining -= lost
        if effective <= 0:
            return dep
        for a in active:
            idx = APPROACH_INDEX[a]
            capacity = SATURATION_FLOW * LANES_PER_APPROACH * effective
            served = min(int(round(capacity + self.np_rng.random_sample() - 0.5)),
                         int(s.queues[idx]))
            dep[idx] = max(0, served)
        return dep

    def step(self, requested_phase: Optional[int]) -> Tuple[Dict, float, bool]:
        """Advance one DT step. `requested_phase` is the phase the controller wants next.

        The simulator enforces min-green, yellow, and all-red intervals. When a switch
        is requested while the current phase is green and min-green is satisfied, the
        simulator enters yellow then all-red then the new green.
        """
        s = self.state

        # 1. Handle transitions
        if s.transition_state == "yellow":
            s.time_in_transition += DT
            if s.time_in_transition >= YELLOW_TIME:
                s.transition_state = "all_red"
                s.time_in_transition = 0.0
        elif s.transition_state == "all_red":
            s.time_in_transition += DT
            if s.time_in_transition >= ALL_RED_TIME:
                s.transition_state = "green"
                s.time_in_transition = 0.0
                s.current_phase = s.pending_phase if s.pending_phase is not None else s.current_phase
                s.pending_phase = None
                s.time_in_phase = 0.0
                s.start_up_remaining = START_UP_LOST_TIME
                s.total_phase_switches += 1
        else:  # green
            s.time_in_phase += DT
            # Check if controller requested a phase change
            if (requested_phase is not None and
                    requested_phase != s.current_phase and
                    s.time_in_phase >= self.min_green):
                s.transition_state = "yellow"
                s.time_in_transition = 0.0
                s.pending_phase = int(requested_phase)
            # Enforce max green as a safety cap (force switch)
            elif s.time_in_phase >= MAX_GREEN_TIME:
                s.transition_state = "yellow"
                s.time_in_transition = 0.0
                s.pending_phase = 1 - s.current_phase

        # 2. Arrivals and departures
        arr = self._arrivals()
        dep = self._departures()
        s.queues += arr
        s.queues -= dep
        s.queues = np.clip(s.queues, 0, None)
        s.total_vehicles += int(arr.sum())
        s.completed_vehicles += int(dep.sum())

        # 3. Accumulate waiting time for all queued vehicles
        s.cumulative_wait += s.queues * DT

        # 4. Snapshot
        self.t += DT
        self.history.append({
            "t": self.t,
            "queues": s.queues.copy(),
            "phase": s.current_phase,
            "transition": s.transition_state,
            "arrivals": arr.copy(),
            "departures": dep.copy(),
        })

        done = self.t >= self.horizon
        reward = -float(s.queues.sum())  # informational; controller handles its own reward
        return self.observe(), reward, done

    def metrics(self) -> Dict:
        """Return scenario-level metrics."""
        s = self.state
        total_wait = float(s.cumulative_wait.sum())
        n_served = s.completed_vehicles
        total_arrived = s.total_vehicles
        awt = total_wait / max(1, total_arrived)
        # Average queue length over time = sum(cumulative_wait) / horizon (units: veh)
        aql = total_wait / max(1.0, self.horizon)
        throughput = n_served / (self.horizon / 3600.0)  # veh/hr
        return {
            "awt": awt,
            "aql": aql,
            "throughput": throughput,
            "total_arrived": total_arrived,
            "total_served": n_served,
            "unserved": total_arrived - n_served,
            "phase_switches": s.total_phase_switches,
        }


# ─────────────────────────────────────────────────────────────
# Episode runner
# ─────────────────────────────────────────────────────────────

def run_episode(controller, demand_fn, seed: int,
                horizon: float = SIM_HORIZON,
                min_green: float = MIN_GREEN_TIME) -> Dict:
    sim = Simulator(demand_fn, seed=seed, horizon=horizon, min_green=min_green)
    obs = sim.reset()
    controller.reset(sim)
    done = False
    while not done:
        action = controller.act(obs)
        obs, _, done = sim.step(action)
    return sim.metrics()


# ─────────────────────────────────────────────────────────────
# Webster fixed-time baseline (built into harness, not in controller.py)
# ─────────────────────────────────────────────────────────────

def webster_cycle(y_ns: float, y_ew: float,
                  lost_time: float = 2 * (YELLOW_TIME + ALL_RED_TIME)) -> float:
    """Webster's optimal cycle length formula.

    Default lost time matches the simulator's yellow + all-red intervals per phase,
    so the baseline controller matches the textbook Webster cycle for this simulator.
    """
    Y = y_ns + y_ew
    if Y >= 0.95:
        Y = 0.95
    return (1.5 * lost_time + 5) / (1 - Y)


class WebsterFixedTimeController:
    """Fixed-time baseline using Webster's optimal cycle and effective green split."""
    name = "Webster-FixedTime"

    def __init__(self):
        self.green_ns: float = 30.0
        self.green_ew: float = 30.0

    def reset(self, sim: Simulator):
        # Estimate saturation ratios from demand function at t=0
        y_ns = max(sim.demand_fn(0, "N"), sim.demand_fn(0, "S")) / SATURATION_FLOW
        y_ew = max(sim.demand_fn(0, "E"), sim.demand_fn(0, "W")) / SATURATION_FLOW
        y_ns = min(y_ns, 0.9)
        y_ew = min(y_ew, 0.9)
        C = webster_cycle(y_ns, y_ew)
        C = max(30.0, min(C, 120.0))
        total_lost = 2 * (YELLOW_TIME + ALL_RED_TIME)
        effective_green = C - total_lost
        if (y_ns + y_ew) > 0:
            self.green_ns = effective_green * y_ns / (y_ns + y_ew)
            self.green_ew = effective_green - self.green_ns
        else:
            self.green_ns = effective_green / 2
            self.green_ew = effective_green / 2
        self.green_ns = max(MIN_GREEN_TIME, self.green_ns)
        self.green_ew = max(MIN_GREEN_TIME, self.green_ew)

    def act(self, obs) -> int:
        if obs["current_phase"] == 0 and obs["time_in_phase"] >= self.green_ns:
            return 1
        if obs["current_phase"] == 1 and obs["time_in_phase"] >= self.green_ew:
            return 0
        return obs["current_phase"]


# ─────────────────────────────────────────────────────────────
# Phase A: Benchmark controller on panel of scenarios
# ─────────────────────────────────────────────────────────────

def benchmark(controller_cls, seeds: List[int] = (0, 1, 2)) -> pd.DataFrame:
    rows = []
    for scen_key, (scen_name, demand_fn) in DEMAND_SCENARIOS.items():
        awts, aqls, thrus, switches = [], [], [], []
        for seed in seeds:
            controller = controller_cls()
            m = run_episode(controller, demand_fn, seed=seed)
            awts.append(m["awt"])
            aqls.append(m["aql"])
            thrus.append(m["throughput"])
            switches.append(m["phase_switches"])
        rows.append({
            "scenario": scen_key,
            "name": scen_name,
            "awt_mean": np.mean(awts),
            "awt_std": np.std(awts),
            "aql_mean": np.mean(aqls),
            "throughput_mean": np.mean(thrus),
            "switches_mean": np.mean(switches),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────
# Phase B: Multi-seed robustness sweep (uniform_med scenario)
# ─────────────────────────────────────────────────────────────

def robustness_sweep(controller_cls, scen_key: str = "uniform_med",
                     n_seeds: int = 10) -> Dict:
    scen_name, demand_fn = DEMAND_SCENARIOS[scen_key]
    awts = []
    for seed in range(n_seeds):
        controller = controller_cls()
        m = run_episode(controller, demand_fn, seed=seed)
        awts.append(m["awt"])
    awts_arr = np.array(awts)
    return {
        "scenario": scen_key,
        "n_seeds": n_seeds,
        "awt_mean": float(awts_arr.mean()),
        "awt_std": float(awts_arr.std()),
        "awt_min": float(awts_arr.min()),
        "awt_max": float(awts_arr.max()),
        "awts": awts_arr.tolist(),
    }


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--robust", action="store_true")
    args = parser.parse_args()
    run_bench = not args.robust or args.benchmark
    run_robust = not args.benchmark or args.robust

    start = time.time()
    RESULTS_DIR.mkdir(exist_ok=True)

    from controller import Controller

    print("=" * 60)
    print(f"Controller: {getattr(Controller, 'name', Controller.__name__)}")
    print(f"Baseline:   {WebsterFixedTimeController.name}")
    print("=" * 60)

    if run_bench:
        print("\nPHASE A: Scenario benchmark (3 seeds per scenario)\n")
        base_df = benchmark(WebsterFixedTimeController)
        ctrl_df = benchmark(Controller)
        merged = base_df[["scenario", "name", "awt_mean", "aql_mean", "throughput_mean"]]\
            .rename(columns={"awt_mean": "baseline_awt",
                             "aql_mean": "baseline_aql",
                             "throughput_mean": "baseline_thru"})
        merged["ctrl_awt"] = ctrl_df["awt_mean"].values
        merged["ctrl_aql"] = ctrl_df["aql_mean"].values
        merged["ctrl_thru"] = ctrl_df["throughput_mean"].values
        merged["awt_delta_pct"] = 100 * (
            merged["ctrl_awt"] - merged["baseline_awt"]) / merged["baseline_awt"]
        print(merged[["scenario", "baseline_awt", "ctrl_awt", "awt_delta_pct"]]
              .to_string(index=False,
                         formatters={"baseline_awt": "{:7.2f}".format,
                                     "ctrl_awt": "{:7.2f}".format,
                                     "awt_delta_pct": "{:+7.2f}%".format}))
        merged.to_csv(RESULTS_DIR / "benchmark.csv", index=False)
        overall = merged["awt_delta_pct"].mean()
        print(f"\nMean AWT change vs Webster: {overall:+.2f}%")
        print("(negative = controller beats Webster)")

    if run_robust:
        print("\nPHASE B: Robustness sweep on uniform_med (10 seeds)\n")
        base_rs = robustness_sweep(WebsterFixedTimeController)
        ctrl_rs = robustness_sweep(Controller)
        print(f"  Baseline AWT: {base_rs['awt_mean']:6.2f} ± {base_rs['awt_std']:.2f} s")
        print(f"  Controller AWT: {ctrl_rs['awt_mean']:6.2f} ± {ctrl_rs['awt_std']:.2f} s")
        delta = 100 * (ctrl_rs['awt_mean'] - base_rs['awt_mean']) / base_rs['awt_mean']
        print(f"  Delta vs baseline: {delta:+.2f}%")
        pd.DataFrame([{"controller": "baseline", **base_rs},
                      {"controller": "ctrl", **ctrl_rs}]).to_csv(
            RESULTS_DIR / "robustness.csv", index=False)

    elapsed = time.time() - start
    print(f"\n{'='*60}\nElapsed: {elapsed:.1f}s\n{'='*60}")


if __name__ == "__main__":
    main()
    sys.exit(0)
