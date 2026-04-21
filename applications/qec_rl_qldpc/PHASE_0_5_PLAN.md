# Phase 0.5 Plan — qec_rl_qldpc

Per program.md Phase 0.5: `data_sources.md` (already complete), tooling install, E00 baseline reproducing Olle 2024, pre-Phase-1 reference-set update.

---

## Step 1 — PER-1 day-0 profile: Zhu-Breuckmann automorphism check wall-clock ⚠️ BLOCKING

The Phase 0 review flagged this as the single most critical pre-Phase-1 gate. If the automorphism-enumeration cost at n=50 is infeasible on one A100, the "RANK of induced logical Clifford" reward must be replaced by a proxy (fold-transversal-count, permutation-subgroup-size, or precomputed family tables).

1. Install `qLDPCOrg/qLDPC` (the adopted reward back-end; follows Sayginel 2024 arXiv:2409.18175):
   ```bash
   cd /home/col/generalized_hdr_autoresearch/applications/qec_rl_qldpc
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install qldpc stim pymatching numpy scipy
   # Olle's qdx is dormant since Dec 2024 — fork and pin
   git clone https://github.com/<TBD>/qdx qdx-fork  # fork URL to confirm
   pip install -e ./qdx-fork
   ```
2. Build representative stabilizer matrices at n ∈ {20, 30, 50}. Use 5 small-BB, 5 Tanner, 5 hypergraph-product instances per n.
3. Profile `qldpc.automorphism_to_logical_Clifford()` (or equivalent) wall-clock. Report median + p95 per call at each n.
4. Compute reward-computation wall-clock as fraction of total RL step time (estimate via Olle 2024 step-time baseline).
5. **Pass criterion:** reward-computation fraction <50% of total RL step at n=50 on one A100 (or proxy). **Fail path:** document in `data_sources.md` + adopt fold-transversal-count proxy (H-TG-2 or equivalent).

Record as E00_profile in `results.tsv`.

---

## Step 2 — Reproduce Olle 2024 RL baseline at n=20, d=5 (E00)

1. Fork + boot `qdx` (MIT licensed, dormant; must pin commit).
2. Run PPO baseline on Olle's published reward curve config.
3. Verify convergence at n=20, d=5 within 12 GPU-hours on one A100 (or equivalent 3060 time-scaled).
4. Record E00 row in `results.tsv`:
   ```
   E00 | Olle 2024 reproduction, PPO, n=20 d=5 | [[16,6,4]] reference | seed=42 | <reward curve match fraction> | KEEP | baseline
   ```

**Pass criterion:** match Olle's reported reward curve within 15% at each checkpoint. This is H-RL-1.

---

## Step 3 — Expand pre-registered reference set (pre-Phase-1)

Phase 0 finding: RASCqL (arXiv:2602.14273), SHYPS (arXiv:2502.07150), and asymmetric-HGP (arXiv:2506.15905) are 2025–2026 hand-crafted automorphism-gate qLDPC constructions that MUST be in the reference Pareto set or the novelty claim collapses.

Update `proposal_v2.md` or Phase 0.5 protocol doc:
- Add RASCqL, SHYPS, asymmetric-HGP, fold-transversal BB, covering BB to the reference code list.
- Re-compute Pareto-reference (n,k) grid to ensure each cell has ≥1 reference code.
- Lock the equivalence relation per PER-2 (default: Pauli-equivalence under qubit permutation + local Clifford).
- Pre-register the (n,k) grid per PER-3.

This is a one-paragraph proposal amendment, not a full v3.

---

## Step 4 — Scaling feasibility curve (gate for proposal_v3)

Per proposal_v2 Phase 0 gate: n=20→50 scaling curve must reach n≥35 on one A100 within 1 week of training. Run:

- n ∈ {20, 25, 30, 35, 40, 50}
- Per n: PPO with default Olle config, 24 GPU-hours, track wall-clock to first valid code.
- Record each as E01–E06 rows in `results.tsv`.

**Pass criterion:** n=35 reachable within 168 GPU-hours total (1 A100-week). If n_max <35, downgrade to website-target per proposal_v2 Kill #1.

---

## Step 5 — Enter Phase 1 (Pareto-front experiment design)

Once Steps 1–4 pass, the project is Phase 0.5 complete. Phase 1 builds the multi-reward Pareto-front evaluator + structural-novelty pipeline.

---

## Quality gates

- [ ] PER-1 automorphism-check profile at n ∈ {20,30,50}; <50% of step time at n=50 OR proxy adopted
- [ ] Olle 2024 reward-curve reproduction within 15% at n=20
- [ ] Reference set expanded with RASCqL, SHYPS, asymmetric-HGP; (n,k) grid re-pre-registered
- [ ] n=20→50 scaling curve; n=35 reached within 168 A100-hours
- [ ] results.tsv populated with E00_profile, E00, E01–E06
