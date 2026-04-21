"""
PER-1 probe — time Zhu-Breuckmann automorphism-group calls across n ∈ {12..72}
with a 60s per-call timeout. Each call is run in a subprocess so GAP errors
don't crash the main process.
"""

from __future__ import annotations
import datetime
import os
import signal
import subprocess
import sys
import time


CODES = [
    # (label, n_target, BB poly degrees (p,q))
    ("BB_2x3",  12, 2, 3),
    ("BB_2x5",  20, 2, 5),
    ("BB_3x5",  30, 3, 5),
    ("BB_4x5",  40, 4, 5),
    ("BB_5x5",  50, 5, 5),
    ("BB_3x8",  48, 3, 8),
    ("BB_6x6",  72, 6, 6),
    ("BB_gross",144, 12, 6),  # the gross code
]


PROBE_CODE = '''
import sys, time, sympy
from qldpc.codes import BBCode
import qldpc.circuits as qc

p_deg, q_deg = int(sys.argv[1]), int(sys.argv[2])
x, y = sympy.symbols("x y")

if p_deg == 12 and q_deg == 6:
    # gross code polynomials
    bb = BBCode({x: p_deg, y: q_deg}, x**3 + y + y**2, y**3 + x + x**2)
else:
    # generic family
    bb = BBCode({x: p_deg, y: q_deg}, x + y + y**2, y + x + x**2)

print(f"n={bb.num_qubits} k={bb.dimension}", flush=True)

t0 = time.perf_counter()
grp = qc.get_transversal_automorphism_group(bb)
dt = time.perf_counter() - t0
print(f"AUTO_GROUP_S={dt:.4f}", flush=True)
'''


def run_one(p_deg: int, q_deg: int, timeout_s: int = 60) -> dict:
    t0 = time.perf_counter()
    try:
        r = subprocess.run(
            [sys.executable, "-u", "-c", PROBE_CODE, str(p_deg), str(q_deg)],
            capture_output=True, text=True, timeout=timeout_s
        )
        wall = time.perf_counter() - t0
        out = r.stdout
        return {
            "ok": r.returncode == 0,
            "wall": wall,
            "n": next((int(l.split("=")[1].split()[0]) for l in out.splitlines() if l.startswith("n=")), None),
            "k": next((int(l.split("k=")[1]) for l in out.splitlines() if l.startswith("n=")), None),
            "auto_s": next((float(l.split("=")[1]) for l in out.splitlines() if l.startswith("AUTO_GROUP_S=")), None),
            "stdout": out,
            "stderr": r.stderr[:300],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "wall": timeout_s, "timeout": True}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def main():
    import os
    os.chdir("/home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc")

    print(f"[PER-1] probe — per-call timeout 60s", flush=True)
    print(f"{'label':<12} {'n':>5} {'k':>4} {'auto_s':>10} {'wall':>10} status", flush=True)

    results = []
    for label, n_target, p_deg, q_deg in CODES:
        r = run_one(p_deg, q_deg, timeout_s=60)
        r["label"] = label
        r["n_target"] = n_target
        results.append(r)
        auto_s = r.get("auto_s", "ERR")
        n = r.get("n", "?")
        k = r.get("k", "?")
        wall = r.get("wall", "?")
        status = "TIMEOUT" if r.get("timeout") else ("OK" if r.get("ok") else "ERROR")
        wall_str = f"{wall:.2f}" if isinstance(wall, float) else str(wall)
        auto_str = f"{auto_s:.3f}" if isinstance(auto_s, float) else str(auto_s)
        print(f"{label:<12} {str(n):>5} {str(k):>4} {auto_str:>10} {wall_str:>10} {status}", flush=True)

    # Write TSV row per code
    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc/results.tsv"
    new_file = not os.path.exists(tsv) or os.path.getsize(tsv) < 50
    with open(tsv, "w") as f:
        f.write("id\ttimestamp\tlabel\tn\tk\tauto_group_s\twall_s\tstatus\tnote\n")
        ts = datetime.datetime.now(datetime.UTC).isoformat()
        for r in results:
            auto = r.get("auto_s")
            wall = r.get("wall")
            status = "TIMEOUT" if r.get("timeout") else ("OK" if r.get("ok") else "ERROR")
            f.write(
                f"E00_PER1_{r['label']}\t{ts}\t{r['label']}\t"
                f"{r.get('n','?')}\t{r.get('k','?')}\t"
                f"{auto if auto is not None else 'ERR'}\t"
                f"{wall if wall is not None else 'ERR'}\t"
                f"{status}\t"
                f"Phase0.5_PER1_GAP_automorphism_probe\n"
            )
    print(f"\n[PER-1] wrote {len(results)} rows to {tsv}", flush=True)

    # Verdict
    auto_times = [r["auto_s"] for r in results if r.get("auto_s") is not None]
    if auto_times:
        max_auto = max(auto_times)
        print(f"[PER-1] max auto-group call: {max_auto:.2f}s", flush=True)
        rl_step_budget = 0.5
        if max_auto < 0.5 * rl_step_budget:
            print(f"[PER-1] PASS — reward cost <25% of step budget ({max_auto:.2f}s < {0.5*rl_step_budget}s)", flush=True)
        else:
            print(f"[PER-1] FAIL — reward cost exceeds 25% of step budget; need proxy metric", flush=True)


if __name__ == "__main__":
    main()
