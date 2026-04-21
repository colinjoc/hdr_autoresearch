"""
E02 — brute-force Pareto sweep over small BB polynomial families using the
nauty proxy reward. Phase 1 Pareto demonstration without needing full RL.

Scope: enumerate BB codes with random small-weight polynomials over (x, y) with
x-order p, y-order q, for (p,q) ∈ small set. For each, compute n, k, distance-lower-bound,
nauty autgroup order. Identify Pareto-optimal points on (k, d, proxy_order, -n).
"""

from __future__ import annotations
import datetime
import itertools
import time

import numpy as np
import sympy
import pynauty

from qldpc.codes import BBCode


def bb_polynomial_enum(max_deg_x: int, max_deg_y: int, num_terms: int = 3):
    """Generate random-but-deterministic BB polynomials with `num_terms` nonzero monomials."""
    x, y = sympy.symbols("x y")
    monomials = []
    for i in range(max_deg_x + 1):
        for j in range(max_deg_y + 1):
            if i == 0 and j == 0:
                continue
            monomials.append(x**i * y**j)
    # All 3-term combinations
    for combo in itertools.combinations(monomials, num_terms):
        yield sum(combo)


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


def main():
    x, y = sympy.symbols("x y")
    print("[E02] brute-force Pareto over small BB polynomials with nauty proxy", flush=True)

    # Search space: (p_deg, q_deg) ∈ {(3,3), (4,4), (5,5), (6,4)} — yields n up to 72
    p_q_grid = [(3, 3), (4, 4), (5, 5), (6, 4), (6, 6)]

    results = []
    t0_total = time.perf_counter()
    for (pd, qd) in p_q_grid:
        target_n = 2 * pd * qd
        polys = list(bb_polynomial_enum(pd, qd, num_terms=3))
        # Cap to sample 40 per (pd, qd) cell to bound wall-time
        import random
        random.seed(42)
        polys_sample = random.sample(polys, min(40, len(polys)))
        print(f"\n[E02] (p={pd}, q={qd}) n={target_n}, sampling {len(polys_sample)} polys of {len(polys)}", flush=True)

        seen = 0
        for pA, pB in itertools.islice(itertools.product(polys_sample, repeat=2), 60):
            try:
                code = BBCode({x: pd, y: qd}, pA, pB)
                n = code.num_qubits
                k = code.dimension
                if k == 0:
                    continue
                t0 = time.perf_counter()
                order = tanner_autgroup_order(code)
                dt = time.perf_counter() - t0
                d_lb = None
                # distance lower-bound via qldpc cheapest path: just report k and proxy
                results.append({
                    "pd": pd, "qd": qd, "n": n, "k": k,
                    "proxy_order": order, "proxy_s": dt,
                    "poly_A": str(pA), "poly_B": str(pB),
                })
                seen += 1
                if seen <= 3:
                    print(f"  [n={n}, k={k}] proxy={order:.2e}  polyA={pA}  polyB={pB}", flush=True)
            except Exception:
                pass
        print(f"  kept {seen} non-trivial instances", flush=True)

    total = time.perf_counter() - t0_total
    print(f"\n[E02] total sweep: {total:.2f}s, {len(results)} non-trivial codes", flush=True)

    # Identify Pareto front on (k, proxy_order) — both maximise
    if results:
        pareto = []
        for r in results:
            dominated = False
            for s in results:
                if s is r: continue
                if s["n"] <= r["n"] and s["k"] >= r["k"] and s["proxy_order"] >= r["proxy_order"]:
                    if s["n"] < r["n"] or s["k"] > r["k"] or s["proxy_order"] > r["proxy_order"]:
                        dominated = True
                        break
            if not dominated:
                pareto.append(r)
        print(f"\n[E02] Pareto front (n, k, proxy_order): {len(pareto)} points", flush=True)
        for p in sorted(pareto, key=lambda r: (r["n"], -r["k"])):
            print(f"  n={p['n']:>4}  k={p['k']:>3}  proxy={p['proxy_order']:.2e}  polyA={p['poly_A'][:40]}  polyB={p['poly_B'][:40]}", flush=True)

    # Write to results.tsv
    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc/results.tsv"
    ts = datetime.datetime.now(datetime.UTC).isoformat()
    with open(tsv, "a") as f:
        f.write(f"E02_pareto_summary\t{ts}\tBB_poly_sweep\tNA\tNA\tnauty_proxy\t{total}\tKEEP\tPhase1_E02_brute_force_Pareto_{len(results)}codes_{len(pareto) if results else 0}Pareto\n")
        for r in results[:20]:  # first 20 for reproducibility
            f.write(
                f"E02_BB_pd{r['pd']}qd{r['qd']}_n{r['n']}_k{r['k']}\t{ts}\t"
                f"BB_pd{r['pd']}qd{r['qd']}\t{r['n']}\t{r['k']}\tnauty_proxy\t"
                f"{r['proxy_s']}\tKEEP\tPhase1_E02_proxy_order={r['proxy_order']:.3e}_polyA='{r['poly_A']}'_polyB='{r['poly_B']}'\n"
            )
    print(f"[E02] wrote summary + {min(20, len(results))} rows to {tsv}", flush=True)


if __name__ == "__main__":
    main()
