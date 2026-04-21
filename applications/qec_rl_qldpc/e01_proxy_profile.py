"""
E01 — permutation-symmetry proxy via pynauty (nauty graph automorphism).

PER-1 fallback: transversal-Clifford rank via GAP+GUAVA times out at n ≥ 40.
The proxy is nauty's canonical graph-automorphism group order of the Tanner graph
coloured with three vertex kinds (qubit, X-check, Z-check). Nauty is O(n^{log n})
in practice and gives the group order as a single number (no enumeration).
"""

from __future__ import annotations
import datetime
import time

import numpy as np
import sympy
import pynauty

from qldpc.codes import BBCode, CSSCode


def tanner_autgroup_order(code: CSSCode) -> tuple[int, float]:
    """Compute the order of the Tanner-graph automorphism group via nauty.

    Vertex colouring: qubits, X-checks, Z-checks are distinct colours so nauty only
    counts automorphisms that preserve role.
    """
    Hx = np.asarray(code.matrix_x, dtype=np.uint8)
    Hz = np.asarray(code.matrix_z, dtype=np.uint8)
    n = code.num_qubits
    mx, mz = Hx.shape[0], Hz.shape[0]
    V = n + mx + mz  # total vertices

    # pynauty expects vertices 0..V-1 and an adjacency-dict.
    # Qubits: 0..n-1. X-checks: n..n+mx-1. Z-checks: n+mx..V-1.
    adj: dict[int, list[int]] = {i: [] for i in range(V)}
    for r in range(mx):
        for c in range(n):
            if Hx[r, c]:
                adj[n + r].append(c)
                adj[c].append(n + r)
    for r in range(mz):
        for c in range(n):
            if Hz[r, c]:
                adj[n + mx + r].append(c)
                adj[c].append(n + mx + r)

    # Colour classes: each class is a list of vertex indices.
    vertex_coloring = [
        set(range(n)),                  # qubits
        set(range(n, n + mx)),          # X-checks
        set(range(n + mx, V)),          # Z-checks
    ]
    g = pynauty.Graph(V, directed=False, adjacency_dict=adj, vertex_coloring=vertex_coloring)

    t0 = time.perf_counter()
    # autgrp returns (generators, grpsize, orbits, numorbits)
    result = pynauty.autgrp(g)
    dt = time.perf_counter() - t0

    # grpsize is (base, exponent_of_10). Order ≈ base × 10**exp.
    base, exp = result[1], result[2]
    order_approx = float(base) * (10 ** int(exp))
    return order_approx, dt


def run_cell(label: str, code: CSSCode) -> dict:
    out = {"label": label, "n": code.num_qubits, "k": code.dimension}
    try:
        order, dt = tanner_autgroup_order(code)
        out["proxy_s"] = dt
        out["autgroup_order"] = order
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {str(e)[:160]}"
    return out


def main():
    x, y = sympy.symbols("x y")

    print("[E01] Permutation-symmetry proxy via nauty — Tanner-graph autgroup order", flush=True)
    print(f"{'label':<22} {'n':>5} {'k':>4} {'proxy_s':>10} {'autgroup_order':>18} status", flush=True)

    codes_spec = [
        ("BB_small_3x3",   3, 3),
        ("BB_small_6x3",   6, 3),
        ("BB_small_6x6",   6, 6),
        ("BB_small_8x4",   8, 4),
        ("BB_small_10x5", 10, 5),
        ("BB_gross_12x6", 12, 6),   # [[144,12,12]]
        ("BB_gross_12x12",12, 12),  # larger symmetric
    ]
    results = []
    for label, pd, qd in codes_spec:
        try:
            bb = BBCode({x: pd, y: qd}, x**3 + y + y**2, y**3 + x + x**2)
            r = run_cell(label, bb)
            results.append(r)
            status = "OK" if "error" not in r else f"ERR: {r['error'][:30]}"
            ps = r.get("proxy_s")
            proxy_str = f"{ps:>10.4f}" if isinstance(ps, float) else f"{str(ps):>10}"
            order = r.get("autgroup_order", "?")
            order_str = f"{order:>18.3e}" if isinstance(order, float) else f"{str(order):>18}"
            print(f"{label:<22} {r.get('n','?'):>5} {r.get('k','?'):>4} {proxy_str} {order_str} {status}", flush=True)
        except Exception as e:
            print(f"{label:<22} build failed: {e}", flush=True)

    # Summary
    ok = [r for r in results if "error" not in r]
    if ok:
        max_s = max(r["proxy_s"] for r in ok)
        print(f"\n[E01] max nauty wall-clock: {max_s:.4f}s at n={max((r['n'], r['proxy_s']) for r in ok)[0]}", flush=True)
        rl_step = 0.5
        print(f"[E01] as fraction of 0.5s RL step: {100*max_s/rl_step:.2f}%", flush=True)
        if max_s < 0.1:
            print(f"[E01] PROXY PASS — nauty gives order in milliseconds; scales to n ≥ 144", flush=True)
        elif max_s < 0.25:
            print(f"[E01] PROXY ACCEPTABLE — <50% of step budget", flush=True)
        else:
            print(f"[E01] PROXY SLOW — consider further speedup or caching", flush=True)

    # Append to results.tsv
    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc/results.tsv"
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    with open(tsv, "a") as f:
        for r in results:
            ps = r.get("proxy_s")
            order = r.get("autgroup_order", "?")
            f.write(
                f"E01_nauty_{r['label']}\t{ts}\t{r['label']}\t"
                f"{r.get('n','?')}\t{r.get('k','?')}\tnauty_proxy\t"
                f"{ps if ps is not None else 'ERR'}\t"
                f"{'OK' if 'error' not in r else 'ERR'}\t"
                f"Phase0.5_E01_nauty_proxy_order={order}\n"
            )
    print(f"[E01] wrote {len(results)} rows to {tsv}", flush=True)


if __name__ == "__main__":
    main()
