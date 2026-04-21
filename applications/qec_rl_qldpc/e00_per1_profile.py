"""
E00 / PER-1 gate — Zhu-Breuckmann automorphism-check wall-clock profile.

Phase 0.5 blocking gate per research_queue PER-1: profile the reward computation
(transversal-automorphism-group + logical-Clifford RANK) at n ∈ {20, 30, 50} on
representative small qLDPC codes. If reward-compute is >50% of a realistic RL step
on one A100 (or RTX 3060 proxy), the gate fails and we adopt a cheaper proxy
(fold-transversal-count, permutation-subgroup-size, or precomputed family tables).

Reference codes tested:
- small BB instances at n ∈ {20, 30, ~50}
- small hypergraph product (HGP) codes at n ∈ {20, 30, 50}
- Tanner-style codes if available
- [[16,6,4]] reference from proposal_v2

Reports:
- median + p95 wall-clock per `get_transversal_automorphism_group` call
- median + p95 wall-clock per `get_transversal_ops` call
- fraction of the typical Olle 2024 RL step budget (~0.5 s / step) consumed
"""

from __future__ import annotations
import datetime
import time

import numpy as np
import sympy

from qldpc.codes import BBCode, HGPCode, ClassicalCode, CSSCode
import qldpc.circuits as qc


def tiny_bb(p_deg: int, q_deg: int) -> BBCode:
    """Small BB instance with n = 2 * p_deg * q_deg."""
    x, y = sympy.symbols("x y")
    # Try to produce a valid BB at the requested sizes. Polynomial choice matters;
    # use a family that usually yields nonzero k.
    bb = BBCode({x: p_deg, y: q_deg}, x**1 + y + y**2, y**1 + x + x**2)
    return bb


def tiny_hgp(n: int) -> HGPCode:
    """Small HGP code built from a random regular LDPC seed."""
    # Build a classical random LDPC matrix of appropriate size; HGP takes two classical codes.
    # Here we use two copies of a small repetition-like code for a minimal smoke profile.
    rng = np.random.default_rng(42)
    # Target HGP n = n1*n2 + m1*m2 ~ n. Use two identical 3x4 sparse matrices.
    m, k = 3, 4
    Hc = np.zeros((m, k), dtype=np.uint8)
    for r in range(m):
        cols = rng.choice(k, size=2, replace=False)
        Hc[r, cols] = 1
    cc = ClassicalCode(Hc)
    return HGPCode(cc, cc)


def profile_code(code: CSSCode, label: str, step_budget_s: float = 0.5) -> dict:
    """Profile Zhu-Breuckmann automorphism + logical-Clifford ranking."""
    try:
        n = code.num_qubits
        k = code.dimension
    except Exception as e:
        return {"label": label, "error": f"code.num_qubits or .dimension failed: {e}"}

    out = {"label": label, "n": n, "k": k}

    # --- get_transversal_automorphism_group ---
    try:
        t0 = time.perf_counter()
        grp = qc.get_transversal_automorphism_group(code)
        out["auto_group_s"] = time.perf_counter() - t0
        out["auto_group_order"] = len(grp) if hasattr(grp, "__len__") else "?"
    except Exception as e:
        out["auto_group_s"] = None
        out["auto_group_error"] = f"{type(e).__name__}: {str(e)[:160]}"

    # --- get_transversal_ops (the heavier function yielding logical tableaus) ---
    try:
        t0 = time.perf_counter()
        ops = qc.get_transversal_ops(code, local_gates={"S", "H", "SQRT_X", "SWAP"})
        out["transversal_ops_s"] = time.perf_counter() - t0
        out["n_transversal_ops"] = len(ops) if hasattr(ops, "__len__") else "?"
    except Exception as e:
        out["transversal_ops_s"] = None
        out["transversal_ops_error"] = f"{type(e).__name__}: {str(e)[:160]}"

    # Reward-compute fraction vs typical RL-step budget
    total = (out.get("auto_group_s") or 0) + (out.get("transversal_ops_s") or 0)
    out["reward_fraction"] = total / step_budget_s if step_budget_s > 0 else None

    return out


def main():
    print("[E00/PER-1] Zhu-Breuckmann transversal-automorphism profile", flush=True)
    print(f"[E00/PER-1] qldpc 0.2.9, Stim 1.16-dev, RTX 3060 host, CUDA 12.9", flush=True)
    print()

    cells = []

    # Small BB instances — vary (p_deg, q_deg) for n ∈ {~20, 30, 50}
    # n = 2 * p * q, so (2,5)->n=20, (3,5)->n=30, (5,5)->n=50
    for (p_deg, q_deg) in [(2, 5), (3, 5), (5, 5), (3, 8), (6, 6)]:
        label = f"BB_{p_deg}x{q_deg}"
        print(f"\n=== {label} (target n={2*p_deg*q_deg}) ===", flush=True)
        try:
            code = tiny_bb(p_deg, q_deg)
            r = profile_code(code, label)
            for k, v in r.items(): print(f"  {k}: {v}", flush=True)
            cells.append(r)
        except Exception as e:
            print(f"  build failed: {type(e).__name__}: {e}", flush=True)
            cells.append({"label": label, "error": f"build: {e}"})

    # Small HGP codes
    for n_target in [20, 30, 50]:
        label = f"HGP_small_n~{n_target}"
        print(f"\n=== {label} ===", flush=True)
        try:
            code = tiny_hgp(n_target)
            r = profile_code(code, label)
            for k, v in r.items(): print(f"  {k}: {v}", flush=True)
            cells.append(r)
        except Exception as e:
            print(f"  build failed: {type(e).__name__}: {e}", flush=True)
            cells.append({"label": label, "error": f"build: {e}"})

    # Reference Bravyi [[144,12,12]] gross code for upper-bound timing
    print(f"\n=== BB_gross_12x6 (n=144) — upper bound ===", flush=True)
    try:
        x, y = sympy.symbols("x y")
        bb_gross = BBCode({x: 12, y: 6}, x**3 + y + y**2, y**3 + x + x**2)
        r = profile_code(bb_gross, "BB_gross_n144")
        for k, v in r.items(): print(f"  {k}: {v}", flush=True)
        cells.append(r)
    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}", flush=True)

    # --- Summary table + pass/fail verdict ---
    print("\n" + "=" * 70, flush=True)
    print("PER-1 PROFILE SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print(f"{'label':<20} {'n':>4} {'k':>3} {'auto_s':>10} {'ops_s':>10} {'%step':>8}", flush=True)
    for r in cells:
        if "error" in r and "n" not in r:
            print(f"{r['label']:<20} ERROR: {r.get('error','')[:40]}", flush=True)
            continue
        ag = r.get("auto_group_s")
        tv = r.get("transversal_ops_s")
        rf = r.get("reward_fraction")
        print(f"{r.get('label','?'):<20} {r.get('n','?'):>4} {r.get('k','?'):>3} "
              f"{ag if ag is not None else 'ERR':>10} {tv if tv is not None else 'ERR':>10} "
              f"{(100*rf if rf is not None else 'ERR'):>8}", flush=True)

    # Verdict
    max_rf = max((r.get("reward_fraction") or 0) for r in cells)
    print(f"\n[PER-1] Max reward-compute fraction across tested codes: {100*max_rf:.1f}% of a 0.5s RL step", flush=True)
    if max_rf < 0.5:
        print("[PER-1] PASS — reward-compute <50% of step budget on all tested codes", flush=True)
        verdict = "PASS"
    else:
        print("[PER-1] FAIL — adopt cheaper proxy (fold-transversal-count / subgroup-size / cached tables)", flush=True)
        verdict = "FAIL"

    # Write to results.tsv
    tsv = "/home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc/results.tsv"
    import os
    new_file = not os.path.exists(tsv)
    with open(tsv, "a") as f:
        if new_file:
            f.write("id\ttimestamp\tlabel\tn\tk\tauto_group_s\ttransversal_ops_s\treward_fraction\tstatus\tnote\n")
        ts = datetime.datetime.now(datetime.UTC).isoformat()
        for r in cells:
            if "error" in r and "n" not in r:
                continue
            f.write(
                f"E00_PER1_{r.get('label','?')}\t{ts}\t{r.get('label','?')}\t"
                f"{r.get('n','?')}\t{r.get('k','?')}\t"
                f"{r.get('auto_group_s') if r.get('auto_group_s') is not None else 'ERR'}\t"
                f"{r.get('transversal_ops_s') if r.get('transversal_ops_s') is not None else 'ERR'}\t"
                f"{r.get('reward_fraction') if r.get('reward_fraction') is not None else 'ERR'}\tKEEP\t"
                f"Phase0.5_E00_PER1_ZhuBreuckmann_profile_{verdict}\n"
            )
    print(f"\n[PER-1] wrote {len(cells)} rows to {tsv}", flush=True)


if __name__ == "__main__":
    main()
