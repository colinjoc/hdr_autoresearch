"""
Traffic signal timing evaluation harness — SUMO + sumo-rl version.

This is the STANDARD published simulator (SUMO, Eclipse DLR) driven by sumo-rl
(Lucas Alegre's Gymnasium/PettingZoo wrapper used by the RESCO benchmark).
It replaces the previous custom Poisson+saturation-flow toy simulator.

Phase A: Benchmark a controller on a panel of SUMO scenarios.
Phase B: Multi-seed robustness sweep on a single scenario.

DO NOT MODIFY THIS FILE.
The autoresearch agent only modifies controller.py.

The controller.py file exposes a `Controller` class with:
    reset(env) -> None
    act(obs) -> int  (index of the requested next green phase)
    name: str        (optional tag for logging)

The `obs` passed to `controller.act` is a dict built from the sumo-rl
`TrafficSignal` object so the controller can reason about queue, density,
active phase, and timing without re-walking TraCI:

    {
        "phase_one_hot":    np.ndarray (num_green_phases,),
        "current_phase":    int,
        "num_green_phases": int,
        "min_green_flag":   int (0/1),
        "time_since_last_phase_change": int (seconds),
        "lane_density":     np.ndarray (n_lanes,),    [0,1]
        "lane_queue":       np.ndarray (n_lanes,),    [0,1]
        "lane_queue_count": np.ndarray (n_lanes,),    raw halting veh count
        "lane_ids":         list[str],
        "t":                float (simulation seconds),
        "phase_lane_mask":  np.ndarray (num_green_phases, n_lanes) in {0,1}
                            — 1 where the lane's movement is served in that phase
    }

Usage:
    python evaluate.py              # all phases
    python evaluate.py --benchmark  # Phase A only
    python evaluate.py --robust     # Phase B only
"""

import argparse
import os
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# SUMO setup — must be before sumo_rl import
if "SUMO_HOME" not in os.environ:
    for candidate in ("/usr/share/sumo", "/usr/local/share/sumo"):
        if Path(candidate).exists():
            os.environ["SUMO_HOME"] = candidate
            break
if "SUMO_HOME" not in os.environ:
    raise RuntimeError("SUMO_HOME not set and no standard install found")

# Suppress libsumo fallback warning (we use pure-python traci)
warnings.filterwarnings("ignore", category=UserWarning, module="traci")

import numpy as np
import pandas as pd
import sumo_rl  # noqa: E402


RESULTS_DIR = Path(__file__).parent / "discoveries"
SUMO_RL_NETS = Path(sumo_rl.__file__).parent / "nets"
LOCAL_NETS = Path(__file__).parent / "sumo_nets"

# Standard 4-approach 2-lane intersection shipped with sumo-rl, used across
# all scenarios. It has 4 protected green phases (NS-through, NS-left,
# EW-through, EW-left) — standard NEMA-style layout.
DEFAULT_NET = SUMO_RL_NETS / "2way-single-intersection/single-intersection.net.xml"

# Episode length — SUMO is ~10× slower than the toy sim, so we use shorter
# episodes and fewer seeds. 600s == 10 simulated minutes is long enough for
# demand patterns to steady-state while keeping per-episode wall time ≲5s.
SIM_HORIZON = 600
# DELTA_TIME=3 gives the controller fine-grained timing control (3s between
# decisions) while keeping traci overhead manageable. sumo-rl requires
# delta_time > yellow_time.
DELTA_TIME = 3      # seconds between controller decisions
MIN_GREEN = 5       # seconds
YELLOW_TIME = 2     # seconds (sumo-rl default)
MAX_GREEN = 60      # seconds

# ─────────────────────────────────────────────────────────────
# Scenarios
# ─────────────────────────────────────────────────────────────
# Panel mixing our uniform-flow routes (comparable to the toy-sim panel)
# with the sumo-rl published route files (horizontal-heavy, vertical-heavy,
# and time-varying vhvh). This gives honest coverage of the standard
# sumo-rl benchmark without losing the uniform-demand comparability.

SCENARIOS = {
    "uniform_low": {
        "description": "Uniform 300 veh/hr/approach, straight-only",
        "net": DEFAULT_NET,
        "rou": LOCAL_NETS / "uniform_low.rou.xml",
        "horizon": SIM_HORIZON,
    },
    "uniform_med": {
        "description": "Uniform 450 veh/hr/approach, straight-only",
        "net": DEFAULT_NET,
        "rou": LOCAL_NETS / "uniform_med.rou.xml",
        "horizon": SIM_HORIZON,
    },
    "uniform_high": {
        "description": "Uniform 600 veh/hr/approach, straight-only",
        "net": DEFAULT_NET,
        "rou": LOCAL_NETS / "uniform_high.rou.xml",
        "horizon": SIM_HORIZON,
    },
    "asymmetric": {
        "description": "NS 700 vs EW 200 veh/hr/approach, straight-only",
        "net": DEFAULT_NET,
        "rou": LOCAL_NETS / "asymmetric.rou.xml",
        "horizon": SIM_HORIZON,
    },
    "sumo_rl_horizontal": {
        "description": "sumo-rl published 'horizontal' scenario (EW-heavy, 12 turning flows)",
        "net": DEFAULT_NET,
        "rou": SUMO_RL_NETS / "2way-single-intersection/single-intersection-horizontal.rou.xml",
        "horizon": SIM_HORIZON,
    },
    "sumo_rl_vertical": {
        "description": "sumo-rl published 'vertical' scenario (NS-heavy, 12 turning flows)",
        "net": DEFAULT_NET,
        "rou": SUMO_RL_NETS / "2way-single-intersection/single-intersection-vertical.rou.xml",
        "horizon": SIM_HORIZON,
    },
    "sumo_rl_vhvh": {
        "description": "sumo-rl published time-varying 'vhvh' scenario",
        "net": DEFAULT_NET,
        "rou": SUMO_RL_NETS / "2way-single-intersection/single-intersection-vhvh.rou.xml",
        "horizon": SIM_HORIZON,
    },
}


# ─────────────────────────────────────────────────────────────
# Observation adapter — turn the raw sumo-rl obs vector into a
# richer dict that lets the controller reason about phases/lanes.
# ─────────────────────────────────────────────────────────────

def build_phase_lane_mask(ts) -> np.ndarray:
    """Mask[phase, lane] = 1 iff any controlled link starting in `lane` gets
    a green signal ('G' or 'g') in that green phase.

    This is what lets a controller score phases by the queue they would serve.
    """
    n_phases = ts.num_green_phases
    lanes = ts.lanes
    lane_to_idx = {l: i for i, l in enumerate(lanes)}
    # trafficlight.getControlledLinks returns a list of lists, one per link index
    # in the phase state string.
    links = ts.sumo.trafficlight.getControlledLinks(ts.id)
    mask = np.zeros((n_phases, len(lanes)), dtype=np.float32)
    for phase_idx in range(n_phases):
        state = ts.green_phases[phase_idx].state
        for link_idx, lnk in enumerate(links):
            if not lnk or link_idx >= len(state):
                continue
            from_lane = lnk[0][0]
            if from_lane not in lane_to_idx:
                continue
            ch = state[link_idx]
            if ch in ("G", "g"):
                mask[phase_idx, lane_to_idx[from_lane]] = 1.0
    return mask


def build_rich_obs(ts, sim_time: float, phase_lane_mask: np.ndarray) -> Dict:
    density = np.array(ts.get_lanes_density(), dtype=np.float32)
    queue = np.array(ts.get_lanes_queue(), dtype=np.float32)
    queue_count = np.array(
        [ts.sumo.lane.getLastStepHaltingNumber(lane) for lane in ts.lanes],
        dtype=np.float32,
    )
    lane_veh_count = np.array(
        [ts.sumo.lane.getLastStepVehicleNumber(lane) for lane in ts.lanes],
        dtype=np.float32,
    )
    phase_one_hot = np.zeros(ts.num_green_phases, dtype=np.float32)
    phase_one_hot[ts.green_phase] = 1.0
    min_green_flag = 1 if ts.time_since_last_phase_change >= (ts.min_green + ts.yellow_time) else 0
    return {
        "phase_one_hot": phase_one_hot,
        "current_phase": int(ts.green_phase),
        "num_green_phases": int(ts.num_green_phases),
        "min_green_flag": int(min_green_flag),
        "time_since_last_phase_change": int(ts.time_since_last_phase_change),
        "lane_density": density,
        "lane_queue": queue,
        "lane_queue_count": queue_count,
        "lane_veh_count": lane_veh_count,
        "lane_ids": list(ts.lanes),
        "phase_lane_mask": phase_lane_mask,
        "t": float(sim_time),
    }


# ─────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────

@dataclass
class EpisodeMetrics:
    awt: float              # mean per-vehicle waiting time over the episode
    aql: float              # mean total halting count over the episode
    peak_queue: float       # max instantaneous total halting count
    phase_switches: int
    total_arrived: int
    total_finished: int
    mean_speed: float
    elapsed_s: float


def _make_env(scen: Dict, seed: int, horizon: Optional[int] = None):
    h = horizon if horizon is not None else scen["horizon"]
    return sumo_rl.SumoEnvironment(
        net_file=str(scen["net"]),
        route_file=str(scen["rou"]),
        num_seconds=h,
        delta_time=DELTA_TIME,
        yellow_time=YELLOW_TIME,
        min_green=MIN_GREEN,
        max_green=MAX_GREEN,
        single_agent=True,
        sumo_warnings=False,
        use_gui=False,
        sumo_seed=seed,
        add_system_info=True,
        add_per_agent_info=True,
    )


def run_episode(
    controller,
    scen: Dict,
    seed: int,
    horizon: Optional[int] = None,
) -> EpisodeMetrics:
    """Run one SUMO episode with the given controller, return metrics."""
    t0 = time.time()
    env = _make_env(scen, seed=seed, horizon=horizon)
    try:
        env.reset()
        ts_id = env.ts_ids[0]
        ts = env.traffic_signals[ts_id]

        # Build phase-lane mask once (it is static for a given net).
        phase_lane_mask = build_phase_lane_mask(ts)

        controller.reset(env)

        sim_wait_samples: List[float] = []
        queue_samples: List[float] = []
        speed_samples: List[float] = []
        peak_queue = 0.0
        phase_switches = 0
        prev_phase = int(ts.green_phase)

        done = False
        while not done:
            obs_dict = build_rich_obs(ts, env.sim_step, phase_lane_mask)
            action = controller.act(obs_dict)
            if action is None:
                action = int(ts.green_phase)
            action = int(action) % ts.num_green_phases
            _, _, term, trunc, info = env.step(action)

            # Capture per-step system info
            sim_wait_samples.append(float(info.get("system_mean_waiting_time", 0.0)))
            total_halt = float(info.get("system_total_stopped", 0.0))
            queue_samples.append(total_halt)
            peak_queue = max(peak_queue, total_halt)
            speed_samples.append(float(info.get("system_mean_speed", 0.0)))

            new_phase = int(ts.green_phase)
            if new_phase != prev_phase:
                phase_switches += 1
                prev_phase = new_phase

            done = term or trunc

        awt = float(np.mean(sim_wait_samples)) if sim_wait_samples else 0.0
        aql = float(np.mean(queue_samples)) if queue_samples else 0.0
        mean_speed = float(np.mean(speed_samples)) if speed_samples else 0.0

        # Get vehicle counts from SUMO directly (TraCI is still live before close).
        total_arrived = int(env.sumo.simulation.getDepartedNumber())  # instantaneous — not useful
        # Use metrics from sumo-rl's internal tracking:
        total_finished = int(env.sumo.simulation.getArrivedNumber())  # instantaneous — not useful

    finally:
        try:
            env.close()
        except Exception:
            pass

    return EpisodeMetrics(
        awt=awt,
        aql=aql,
        peak_queue=peak_queue,
        phase_switches=phase_switches,
        total_arrived=total_arrived,
        total_finished=total_finished,
        mean_speed=mean_speed,
        elapsed_s=time.time() - t0,
    )


# ─────────────────────────────────────────────────────────────
# Webster fixed-time baseline
# ─────────────────────────────────────────────────────────────

SATURATION_FLOW_VEH_HR = 1800.0
LOST_TIME_PER_PHASE = YELLOW_TIME + 1.0  # yellow + ~1s effective lost


def webster_cycle(y_values: List[float], lost_per_phase: float = LOST_TIME_PER_PHASE) -> float:
    """Webster's optimal cycle length.

    C_o = (1.5 * L + 5) / (1 - Y), where L = total lost time per cycle,
    Y = sum of critical phase flow ratios (y_i = q_i / s_i).
    """
    L = len(y_values) * lost_per_phase
    Y = sum(y_values)
    if Y >= 0.95:
        Y = 0.95
    return (1.5 * L + 5) / (1 - Y)


def _parse_flows_from_route(route_path: Path) -> Dict[str, float]:
    """Return a dict mapping 'from_edge' -> total veh/hr flowing into that edge.

    Used by Webster to estimate per-approach demand from the route file.
    We sum all `<flow>` elements whose route starts with each incoming edge.
    Time-varying scenarios: we take the peak sum across the set of overlapping
    intervals (Webster is tuned to the busiest profile).
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(route_path)
    root = tree.getroot()

    # Map route id -> first edge
    route_first_edge: Dict[str, str] = {}
    for r in root.findall("route"):
        rid = r.get("id")
        edges = (r.get("edges") or "").split()
        if rid and edges:
            route_first_edge[rid] = edges[0]

    # Collect flows by (begin, end) interval and first edge
    interval_flows: Dict[Tuple[int, int], Dict[str, float]] = {}
    for f in root.findall("flow"):
        rid = f.get("route")
        begin = int(float(f.get("begin", "0")))
        end = int(float(f.get("end", "100000")))
        vph = f.get("vehsPerHour")
        prob = f.get("probability")
        if vph is not None:
            rate = float(vph)
        elif prob is not None:
            # Probability-per-step at 1 Hz -> veh/hr
            rate = float(prob) * 3600.0
        else:
            continue
        if rid not in route_first_edge:
            continue
        edge = route_first_edge[rid]
        key = (begin, end)
        if key not in interval_flows:
            interval_flows[key] = {}
        interval_flows[key][edge] = interval_flows[key].get(edge, 0.0) + rate

    # For time-varying profiles, take the peak per-edge rate across intervals
    # that are active during the simulation horizon.
    peak: Dict[str, float] = {}
    for (begin, end), edge_rates in interval_flows.items():
        if begin > SIM_HORIZON:
            continue
        for edge, rate in edge_rates.items():
            peak[edge] = max(peak.get(edge, 0.0), rate)
    return peak


def compute_webster_plan(scen: Dict) -> "WebsterPlan":
    """Given a scenario, compute a fixed-time plan: per-phase green duration.

    Strategy:
      1. Build the env briefly to pull phase-lane masks and lane-to-approach map
      2. Parse the route file to estimate per-approach demand (veh/hr/lane)
      3. Compute y_i = demand_i / saturation_flow for each green phase by
         taking the MAX over its served lanes (standard Webster convention)
      4. Webster cycle length from sum(y_i)
      5. Distribute effective green in proportion to y_i (capped to [MIN_GREEN, MAX_GREEN])
    """
    env = _make_env(scen, seed=0, horizon=60)
    try:
        env.reset()
        ts_id = env.ts_ids[0]
        ts = env.traffic_signals[ts_id]
        phase_lane_mask = build_phase_lane_mask(ts)
        lanes = list(ts.lanes)
    finally:
        env.close()

    # Map each lane -> its "from edge" (first 3 chars handle 'n_t_0' -> 'n_t')
    def lane_to_edge(lane_id: str) -> str:
        # Lane IDs look like 'n_t_0' — edge is everything before the final _digit
        parts = lane_id.rsplit("_", 1)
        return parts[0]

    edge_flows = _parse_flows_from_route(Path(scen["rou"]))

    # Per-lane flow = edge total / number of lanes on that edge
    edge_lane_counts: Dict[str, int] = {}
    for lane in lanes:
        e = lane_to_edge(lane)
        edge_lane_counts[e] = edge_lane_counts.get(e, 0) + 1

    lane_flow = np.zeros(len(lanes), dtype=np.float64)
    for i, lane in enumerate(lanes):
        e = lane_to_edge(lane)
        total = edge_flows.get(e, 0.0)
        n = max(1, edge_lane_counts.get(e, 1))
        lane_flow[i] = total / n  # veh/hr per lane

    # y_i per green phase = max over served lanes of lane_flow / saturation
    n_phases = phase_lane_mask.shape[0]
    y_per_phase = np.zeros(n_phases)
    for p in range(n_phases):
        mask = phase_lane_mask[p]
        served_flows = lane_flow[mask > 0]
        if len(served_flows) > 0:
            y_per_phase[p] = served_flows.max() / SATURATION_FLOW_VEH_HR
    y_per_phase = np.clip(y_per_phase, 0.0, 0.9)

    C = webster_cycle(list(y_per_phase))
    C = max(30.0, min(C, 150.0))
    L = n_phases * LOST_TIME_PER_PHASE
    eff_green = max(n_phases * MIN_GREEN, C - L)

    denom = y_per_phase.sum()
    if denom > 0:
        green_split = eff_green * (y_per_phase / denom)
    else:
        green_split = np.full(n_phases, eff_green / n_phases)
    green_split = np.clip(green_split, MIN_GREEN, MAX_GREEN)

    return WebsterPlan(
        cycle=C,
        y_per_phase=y_per_phase,
        green_per_phase=green_split,
    )


@dataclass
class WebsterPlan:
    cycle: float
    y_per_phase: np.ndarray
    green_per_phase: np.ndarray


class WebsterFixedTimeController:
    """Fixed-time baseline: compute per-phase green from Webster at reset,
    then cycle through phases in order, holding each for its allotted green
    (measured in simulated seconds, via obs['time_since_last_phase_change']).

    When the current phase has exceeded its allotted green, request the next
    phase in order. sumo-rl enforces min_green automatically.
    """
    name = "Webster-FixedTime"

    def __init__(self, scenario: Optional[Dict] = None):
        self._scenario = scenario
        self._plan: Optional[WebsterPlan] = None
        self._target_phase = 0

    def set_scenario(self, scenario: Dict) -> None:
        self._scenario = scenario

    def reset(self, env) -> None:
        if self._scenario is None:
            raise RuntimeError("WebsterFixedTimeController: scenario not set")
        self._plan = compute_webster_plan(self._scenario)
        self._target_phase = 0

    def act(self, obs) -> int:
        if self._plan is None:
            return int(obs["current_phase"])
        n_phases = int(obs["num_green_phases"])
        cur = int(obs["current_phase"])
        elapsed = float(obs["time_since_last_phase_change"])
        # Green duration target for the current phase (floor at MIN_GREEN)
        target = max(float(MIN_GREEN), float(self._plan.green_per_phase[cur]))
        if elapsed >= target:
            return (cur + 1) % n_phases
        return cur


# ─────────────────────────────────────────────────────────────
# Benchmark + robustness sweep
# ─────────────────────────────────────────────────────────────

def benchmark(
    controller_factory,
    scenarios: Optional[List[str]] = None,
    seeds: Tuple[int, ...] = (0, 1, 2),
    horizon: Optional[int] = None,
    scenario_aware: bool = False,
) -> pd.DataFrame:
    """Run controller on a panel of scenarios and return per-scenario metrics.

    If `scenario_aware`, the controller_factory receives the scenario dict
    (used for Webster which needs demand information).
    """
    scenarios = scenarios or list(SCENARIOS.keys())
    rows = []
    for scen_key in scenarios:
        scen = SCENARIOS[scen_key]
        awts = []
        aqls = []
        pq = []
        switches = []
        elapsed = 0.0
        for seed in seeds:
            if scenario_aware:
                ctrl = controller_factory(scen)
            else:
                ctrl = controller_factory()
            m = run_episode(ctrl, scen, seed=seed, horizon=horizon)
            awts.append(m.awt)
            aqls.append(m.aql)
            pq.append(m.peak_queue)
            switches.append(m.phase_switches)
            elapsed += m.elapsed_s
        rows.append({
            "scenario": scen_key,
            "description": scen["description"],
            "awt_mean": float(np.mean(awts)),
            "awt_std": float(np.std(awts)),
            "aql_mean": float(np.mean(aqls)),
            "peak_queue_mean": float(np.mean(pq)),
            "switches_mean": float(np.mean(switches)),
            "elapsed_s": elapsed,
        })
    return pd.DataFrame(rows)


def robustness_sweep(
    controller_factory,
    scen_key: str = "uniform_med",
    n_seeds: int = 5,
    horizon: Optional[int] = None,
    scenario_aware: bool = False,
) -> Dict:
    scen = SCENARIOS[scen_key]
    awts = []
    for seed in range(n_seeds):
        if scenario_aware:
            ctrl = controller_factory(scen)
        else:
            ctrl = controller_factory()
        m = run_episode(ctrl, scen, seed=seed, horizon=horizon)
        awts.append(m.awt)
    arr = np.array(awts)
    return {
        "scenario": scen_key,
        "n_seeds": n_seeds,
        "awt_mean": float(arr.mean()),
        "awt_std": float(arr.std()),
        "awt_min": float(arr.min()),
        "awt_max": float(arr.max()),
        "awts": arr.tolist(),
    }


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--robust", action="store_true")
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--robust-seeds", type=int, default=5)
    parser.add_argument("--scenario", type=str, default=None,
                        help="Restrict to a single scenario key")
    args = parser.parse_args()
    run_bench = not args.robust or args.benchmark
    run_robust = not args.benchmark or args.robust

    start = time.time()
    RESULTS_DIR.mkdir(exist_ok=True)

    from controller import Controller  # noqa: E402

    def ctrl_factory():
        return Controller()

    def webster_factory(scen):
        return WebsterFixedTimeController(scenario=scen)

    scenarios = [args.scenario] if args.scenario else list(SCENARIOS.keys())
    seeds = tuple(range(args.seeds))

    print("=" * 70)
    print(f"Simulator: SUMO {os.popen('sumo --version 2>&1 | head -1').read().strip()}")
    print(f"Library:   sumo-rl {getattr(sumo_rl, '__version__', '(n/a)')}")
    print(f"Net:       {DEFAULT_NET.name}")
    print(f"Horizon:   {SIM_HORIZON}s  delta={DELTA_TIME}s  min_green={MIN_GREEN}s")
    print(f"Scenarios: {scenarios}")
    print(f"Controller: {getattr(Controller, 'name', Controller.__name__)}")
    print(f"Baseline:   {WebsterFixedTimeController.name}")
    print("=" * 70)

    if run_bench:
        print(f"\nPHASE A: Scenario benchmark ({len(seeds)} seeds per scenario)\n")
        base_df = benchmark(webster_factory, scenarios=scenarios, seeds=seeds, scenario_aware=True)
        ctrl_df = benchmark(ctrl_factory, scenarios=scenarios, seeds=seeds, scenario_aware=False)
        merged = base_df[["scenario", "awt_mean", "aql_mean"]].rename(
            columns={"awt_mean": "baseline_awt", "aql_mean": "baseline_aql"}
        )
        merged["ctrl_awt"] = ctrl_df["awt_mean"].values
        merged["ctrl_aql"] = ctrl_df["aql_mean"].values
        merged["awt_delta_pct"] = 100 * (
            merged["ctrl_awt"] - merged["baseline_awt"]
        ) / np.maximum(merged["baseline_awt"], 1e-9)
        print(merged[["scenario", "baseline_awt", "ctrl_awt", "awt_delta_pct"]]
              .to_string(index=False,
                         formatters={"baseline_awt": "{:7.2f}".format,
                                     "ctrl_awt": "{:7.2f}".format,
                                     "awt_delta_pct": "{:+7.2f}%".format}))
        merged.to_csv(RESULTS_DIR / "benchmark_sumo.csv", index=False)
        overall = merged["awt_delta_pct"].mean()
        print(f"\nMean AWT change vs Webster: {overall:+.2f}%")
        print("(negative = controller beats Webster)")
        print(f"Total SUMO wall time Phase A: {base_df['elapsed_s'].sum() + ctrl_df['elapsed_s'].sum():.1f}s")

    if run_robust:
        rob_scen = args.scenario if args.scenario else "uniform_med"
        print(f"\nPHASE B: Robustness sweep on {rob_scen} ({args.robust_seeds} seeds)\n")
        base_rs = robustness_sweep(webster_factory, scen_key=rob_scen, n_seeds=args.robust_seeds, scenario_aware=True)
        ctrl_rs = robustness_sweep(ctrl_factory, scen_key=rob_scen, n_seeds=args.robust_seeds, scenario_aware=False)
        print(f"  Baseline AWT: {base_rs['awt_mean']:6.2f} ± {base_rs['awt_std']:.2f} s")
        print(f"  Controller AWT: {ctrl_rs['awt_mean']:6.2f} ± {ctrl_rs['awt_std']:.2f} s")
        denom = max(base_rs['awt_mean'], 1e-9)
        delta = 100 * (ctrl_rs['awt_mean'] - base_rs['awt_mean']) / denom
        print(f"  Delta vs baseline: {delta:+.2f}%")
        pd.DataFrame([{"controller": "baseline", **base_rs},
                      {"controller": "ctrl", **ctrl_rs}]).to_csv(
            RESULTS_DIR / "robustness_sumo.csv", index=False)

    elapsed = time.time() - start
    print(f"\n{'='*70}\nElapsed: {elapsed:.1f}s\n{'='*70}")


if __name__ == "__main__":
    main()
    sys.exit(0)
