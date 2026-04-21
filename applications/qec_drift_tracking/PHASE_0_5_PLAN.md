# Phase 0.5 Plan — qec_drift_tracking

Per program.md Phase 0.5: `data_sources.md` (complete from Phase 0), downloaded real data, E00 baseline reproducing published SOTA, reproduction of the direct baseline arXiv:2512.10814 (DEM-on-Willow) identified in Phase 0.

---

## Step 1 — Download Willow Zenodo dataset ⚠️ LARGE

Zenodo 13273331: ~112.5 GB of raw per-shot per-round syndromes from 420 Willow experiments.

```bash
cd /home/col/generalized_hdr_autoresearch/applications/qec_drift_tracking
mkdir -p data/raw
cd data/raw
# Verify disk space first
df -h .
# Download (use zenodo_get or wget/curl with resume)
pip install zenodo_get
zenodo_get 13273331
```

If disk space is a blocker, download a subset first (e.g., d=5 experiments only, ~30 GB) and document the partial scope in `data_sources.md`. Full 112.5 GB needed only for the cross-distance drift-timescale analysis.

Verify checksums + document file format.

---

## Step 2 — Verify detector-event format + timestamp resolution

Phase 0 flagged: Zenodo timestamps appear to be per-run, not per-shot (H63). This means sub-hour real-data drift cells need "real statistics + synthetic drift injection" hybrid processing.

1. Read Zenodo README carefully.
2. Inspect HDF5 / whatever format: check (a) detector-event shape (shots × rounds × detectors), (b) timestamp field granularity, (c) run metadata (date, temperature, ramsey-curve data if present).
3. Document in `data_sources.md` §3: exact timestamp granularity, shot-to-shot temporal info (if any), workaround for sub-hour cells.

---

## Step 3 — Install filter + baseline toolchain

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install stim pymatching numpy scipy jax[cpu] particles pyro-ppl matplotlib h5py
# For MCMC static baseline (arXiv:2406.08981)
pip install pymc arviz
```

Verify imports. Record versions in `data_sources.md`.

---

## Step 4 — Reproduce arXiv:2512.10814 DEM-on-Willow baseline (E00)

This is the direct head-to-head baseline identified in Phase 0. Reproducing it is the E00 baseline.

1. Fetch paper + supplementary code (GitHub? arxiv ancillary?).
2. Apply their single-method window-based DEM estimator to the same Zenodo shard.
3. Compute LER under reweighted PyMatching decoding.
4. Record:
   ```
   E00 | arXiv:2512.10814 DEM-on-Willow reproduction | d=5 Zenodo shard | seed=42 | <LER match fraction> | KEEP | baseline
   ```

**Pass criterion:** LER reproduced within 10% of published numbers. This is the benchmark our three-way (SMC + sliding-window-MLE + static-Bayesian) comparison must beat.

---

## Step 5 — Reproduce sliding-window MLE baseline (arXiv:2511.09491)

Second baseline from proposal_v3 §2. Reimplement or adopt author code if public.

Record as E01 row in `results.tsv`.

---

## Step 6 — Reproduce static Bayesian MCMC baseline (arXiv:2406.08981)

Third baseline. Use pymc or the author's code.

Record as E02 row.

---

## Step 7 — Begin LCD reimplementation (pre-empt-reviewer PER-1)

The LCD-class adaptive-decoder baseline (proposal_v3 §2.3) needs a reimplementation matching the published Riverlane protocol as closely as possible. Phase 0.5 only needs to demonstrate the reimplementation starts; quality-gap benchmarking against Riverlane's Nat. Commun. 2025 numbers is a Phase 1 task.

1. Read Barnes et al. 2025 Nat. Commun. LCD paper carefully + any open protocol releases.
2. Scaffold the reimplementation: core Python package + unit tests against published micro-benchmarks.
3. Document protocol conformance gap in `data_sources.md` §4 — what's matched, what's extrapolated.

---

## Step 8 — Enter Phase 1 (filter implementation + phase-diagram experiments)

Once Steps 1–7 pass, the project is Phase 0.5 complete. Phase 1 builds the JAX Rao-Blackwellised particle filter + phase-diagram sweep.

---

## Quality gates

- [ ] Willow Zenodo 13273331 downloaded (full or documented subset) with checksums
- [ ] Timestamp granularity + workaround for sub-hour cells documented
- [ ] venv with all dependencies installed and versioned
- [ ] arXiv:2512.10814 baseline reproduced within 10% LER (E00)
- [ ] Sliding-window MLE baseline reproduced (E01)
- [ ] Static Bayesian MCMC baseline reproduced (E02)
- [ ] LCD reimplementation scaffold with documented conformance gap
