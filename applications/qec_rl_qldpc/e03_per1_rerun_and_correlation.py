"""
E03 — Phase 2.75 methodology review revisions 1+2.

(1) PER-1 re-run: warm GAP, gross-family polynomials at n ∈ {40, 48, 50, 72},
    300 s per-call timeout, including `get_transversal_ops` (the rank-computing
    function) not just `get_transversal_automorphism_group`.

(2) Proxy ↔ rank correlation at n ≤ 30 where GAP is tractable: for each of a
    handful of small codes, compute both (a) nauty Tanner-graph autgroup order
    and (b) `get_transversal_ops` length (number of non-trivial transversal
    logical Clifford operations). Report Pearson/Spearman correlation.
"""

from __future__ import annotations
import datetime
import subprocess
import sys
import time

import numpy as np
import sympy
import pynauty

from qldpc.codes import BBCode


def tanner_autgroup_order(code) -> float:
    Hx = np.asarray(code.matrix_x, dtype=np.uint8)
    Hz = np.asarray(code.matrix_z, dtype=np.uint8)
    n = code.num_qubits
    mx, mz = Hx.shape[0], Hz.shape[0]
    V = n + mx + mz
    adj = {i: [] for i in range(V)}
    for r in range(mx):
        for c in range(n):
            if Hx[r, c]:
                adj[n + r].append(c); adj[c].append(n + r)
    for r in range(mz):
        for c in range(n):
            if Hz[r, c]:
                adj[n + mx + r].append(c); adj[c].append(n + mx + r)
    coloring = [set(range(n)), set(range(n, n + mx)), set(range(n + mx, V))]
    g = pynauty.Graph(V, directed=False, adjacency_dict=adj, vertex_coloring=coloring)
    base, exp = pynauty.autgrp(g)[1:3]
    return float(base) * (10 ** int(exp))


# ---------- Revision 1 — PER-1 re-run (gross family, warm GAP, 300s) ----------

PROBE_WARM = '''
import sys, time, sympy
from qldpc.codes import BBCode
import qldpc.circuits as qc

x, y = sympy.symbols("x y")
codes = []
for pd, qd in [(2,3), (4,5), (6,4), (5,5), (6,6), (3,8)]:
    # Gross-family polynomials
    try:
        bb = BBCode({x: pd, y: qd}, x**3 + y + y**2, y**3 + x + x**2)
        codes.append((f"BB_gross_{pd}x{qd}", bb))
        print(f"built BB_gross_{pd}x{qd}: n={bb.num_qubits} k={bb.dimension}", flush=True)
    except Exception as e:
        print(f"build failed {pd}x{qd}: {e}", flush=True)

# Import GAP first to warm the cache, then call repeatedly
for label, bb in codes:
    t0 = time.perf_counter()
    try:
        grp = qc.get_transversal_automorphism_group(bb)
        dt = time.perf_counter() - t0
        print(f"{label} auto_group_s={dt:.3f}", flush=True)
        t0 = time.perf_counter()
        ops = qc.get_transversal_ops(bb, local_gates={"S", "H", "SQRT_X", "SWAP"})
        dt_ops = time.perf_counter() - t0
        n_ops = len(ops) if hasattr(ops, "__len__") else -1
        print(f"{label} transversal_ops_s={dt_ops:.3f} n_ops={n_ops}", flush=True)
    except Exception as e:
        print(f"{label} FAILED: {type(e).__name__}: {str(e)[:150]}", flush=True)
'''


def per1_rerun():
    print("[E03.1] PER-1 rerun — gross-family, warm GAP, 300s total timeout", flush=True)
    t0 = time.perf_counter()
    try:
        r = subprocess.run(
            [sys.executable, "-u", "-c", PROBE_WARM],
            capture_output=True, text=True, timeout=300
        )
        wall = time.perf_counter() - t0
        print(f"[E03.1] subprocess finished in {wall:.2f}s, exit={r.returncode}", flush=True)
        for line in r.stdout.splitlines():
            print(f"  {line}", flush=True)
        if r.stderr.strip():
            print(f"[E03.1] stderr tail:\n  {r.stderr[-400:]}", flush=True)
        return r.stdout
    except subprocess.TimeoutExpired:
        wall = time.perf_counter() - t0
        print(f"[E03.1] TIMEOUT at {wall:.1f}s", flush=True)
        return "TIMEOUT"


# ---------- Revision 2 — proxy ↔ rank correlation at n ≤ 30 ----------

PROBE_CORR = '''
import sys, time, sympy, numpy as np, pynauty
from qldpc.codes import BBCode
import qldpc.circuits as qc

def tanner_order(code):
    Hx = np.asarray(code.matrix_x, dtype=np.uint8)
    Hz = np.asarray(code.matrix_z, dtype=np.uint8)
    n = code.num_qubits; mx, mz = Hx.shape[0], Hz.shape[0]; V = n+mx+mz
    adj = {i: [] for i in range(V)}
    for r in range(mx):
        for c in range(n):
            if Hx[r,c]: adj[n+r].append(c); adj[c].append(n+r)
    for r in range(mz):
        for c in range(n):
            if Hz[r,c]: adj[n+mx+r].append(c); adj[c].append(n+mx+r)
    coloring = [set(range(n)), set(range(n, n+mx)), set(range(n+mx, V))]
    g = pynauty.Graph(V, directed=False, adjacency_dict=adj, vertex_coloring=coloring)
    base, exp = pynauty.autgrp(g)[1:3]
    return float(base) * (10 ** int(exp))

x, y = sympy.symbols("x y")
# Small BB instances with k > 0
specs = [
    ("g_3x3", 3, 3),
    ("g_6x3", 6, 3),
    ("g_2x3", 2, 3),
]
# Polynomial variants for each (p,q): test multiple to get a range of (proxy, rank)
variants = [
    ("v1", lambda: (x**3 + y + y**2, y**3 + x + x**2)),
    ("v2", lambda: (x + y, y + x)),
    ("v3", lambda: (x**2 + y, y**2 + x)),
    ("v4", lambda: (x + y**2, y + x**2)),
    ("v5", lambda: (x**2 + y**2 + 1, y**2 + x**2 + 1)),
]

print("code\\tn\\tk\\tproxy\\trank_ops\\tauto_s\\tops_s", flush=True)
for label, pd, qd in specs:
    for vname, pfn in variants:
        try:
            A, B = pfn()
            bb = BBCode({x: pd, y: qd}, A, B)
            if bb.dimension == 0:
                continue
            proxy = tanner_order(bb)
            t0 = time.perf_counter(); _ = qc.get_transversal_automorphism_group(bb); auto_s = time.perf_counter()-t0
            t0 = time.perf_counter(); ops = qc.get_transversal_ops(bb, local_gates={"S","H","SQRT_X","SWAP"}); ops_s = time.perf_counter()-t0
            n_ops = len(ops) if hasattr(ops, "__len__") else -1
            print(f"{label}_{vname}\\t{bb.num_qubits}\\t{bb.dimension}\\t{proxy}\\t{n_ops}\\t{auto_s:.3f}\\t{ops_s:.3f}", flush=True)
        except Exception as e:
            print(f"{label}_{vname}\\tERR: {type(e).__name__}: {str(e)[:80]}", flush=True)
'''


def correlation_study():
    print("\n[E03.2] Proxy ↔ rank correlation at n ≤ 30", flush=True)
    t0 = time.perf_counter()
    try:
        r = subprocess.run(
            [sys.executable, "-u", "-c", PROBE_CORR],
            capture_output=True, text=True, timeout=600
        )
        wall = time.perf_counter() - t0
        print(f"[E03.2] subprocess finished in {wall:.2f}s, exit={r.returncode}", flush=True)
        pairs = []
        for line in r.stdout.splitlines():
            parts = line.strip().split("\t")
            if len(parts) == 7 and parts[0] != "code":
                try:
                    proxy = float(parts[3])
                    rank = int(parts[4])
                    if rank > 0:
                        pairs.append((proxy, rank))
                except ValueError:
                    pass
            print(f"  {line}", flush=True)

        if len(pairs) >= 3:
            proxies = np.array([p[0] for p in pairs])
            ranks = np.array([p[1] for p in pairs])
            # Log-proxy vs log-rank Pearson (proxies can span orders of magnitude)
            lp = np.log(proxies + 1)
            lr = np.log(ranks + 1)
            if len(lp) > 1 and np.std(lp) > 0 and np.std(lr) > 0:
                pearson = float(np.corrcoef(lp, lr)[0, 1])
                from scipy.stats import spearmanr
                rho, _ = spearmanr(proxies, ranks)
                print(f"\n[E03.2] n_pairs={len(pairs)} | Pearson(log-proxy, log-rank)={pearson:.3f} | Spearman={rho:.3f}", flush=True)
        else:
            print("[E03.2] insufficient pairs for correlation", flush=True)

        if r.stderr.strip():
            print(f"[E03.2] stderr tail:\n  {r.stderr[-400:]}", flush=True)
        return r.stdout
    except subprocess.TimeoutExpired:
        print(f"[E03.2] TIMEOUT at {time.perf_counter()-t0:.1f}s", flush=True)
        return "TIMEOUT"


def main():
    per1_out = per1_rerun()
    corr_out = correlation_study()

    # Save both outputs to results.tsv
    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc/results.tsv"
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    with open(tsv, "a") as f:
        f.write(f"E03.1_PER1_rerun\t{ts}\tPER1_warm_gross\tNA\tNA\tGAP_rerun\tNA\tDONE\tPhase2.75_revision_see_stdout\n")
        f.write(f"E03.2_correlation\t{ts}\tproxy_vs_rank_n<=30\tNA\tNA\tcorrelation\tNA\tDONE\tPhase2.75_revision_see_stdout\n")


if __name__ == "__main__":
    main()
