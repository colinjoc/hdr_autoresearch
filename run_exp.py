"""Run the SUMO benchmark + robustness sweep and print a one-line TSV row.

Usage:
    python run_exp.py                # full panel, 2 seeds, 3 robustness seeds
    python run_exp.py --fast         # short horizon for iteration
"""
import argparse
import importlib
import sys
import time

import numpy as np

# Force reimport of controller to pick up edits
if "controller" in sys.modules:
    del sys.modules["controller"]
from evaluate import (  # noqa: E402
    SCENARIOS,
    WebsterFixedTimeController,
    benchmark,
    robustness_sweep,
)
from controller import Controller  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=2)
    parser.add_argument("--robust-seeds", type=int, default=3)
    parser.add_argument("--fast", action="store_true",
                        help="Use a shorter horizon (300s) for quick HDR iteration")
    args = parser.parse_args()
    horizon = 300 if args.fast else None

    t0 = time.time()

    def ctrl_factory():
        return Controller()

    def webster_factory(scen):
        return WebsterFixedTimeController(scenario=scen)

    seeds = tuple(range(args.seeds))
    base_df = benchmark(webster_factory, seeds=seeds, horizon=horizon, scenario_aware=True)
    ctrl_df = benchmark(ctrl_factory, seeds=seeds, horizon=horizon, scenario_aware=False)

    # Robust sweep on uniform_med
    rs_base = robustness_sweep(webster_factory, scen_key="uniform_med",
                               n_seeds=args.robust_seeds, horizon=horizon, scenario_aware=True)
    rs_ctrl = robustness_sweep(ctrl_factory, scen_key="uniform_med",
                               n_seeds=args.robust_seeds, horizon=horizon)

    print(f"# {getattr(Controller, 'name', 'controller')}  (horizon={'300' if args.fast else '600'}s)")
    rows = []
    for i in range(len(base_df)):
        scen = base_df.iloc[i]["scenario"]
        b = base_df.iloc[i]["awt_mean"]
        c = ctrl_df.iloc[i]["awt_mean"]
        delta = 100 * (c - b) / max(b, 1e-9)
        rows.append(delta)
        print(f"  {scen:22s}  webster={b:6.2f}  sotl={c:6.2f}  {delta:+7.2f}%")
    mean_delta = float(np.mean(rows))
    print(f"  MEAN_DELTA_PCT = {mean_delta:+.2f}%")
    print(f"  ROBUST(uniform_med): webster={rs_base['awt_mean']:.2f}±{rs_base['awt_std']:.2f}  "
          f"sotl={rs_ctrl['awt_mean']:.2f}±{rs_ctrl['awt_std']:.2f}  "
          f"delta={100*(rs_ctrl['awt_mean']-rs_base['awt_mean'])/max(rs_base['awt_mean'],1e-9):+.2f}%")
    # TSV row (matches results.tsv columns after the first few)
    awts = [f"{ctrl_df.iloc[i]['awt_mean']:.2f}" for i in range(len(ctrl_df))]
    print(f"TSV: {chr(9).join(awts)}\t{mean_delta:+.2f}\t{rs_ctrl['awt_mean']:.2f}\t{rs_ctrl['awt_std']:.2f}")
    print(f"wall time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
