# Phase 0.5 Plan — qec_resource_est

Per program.md Phase 0.5 requires: `data_sources.md` (already complete from Phase 0), downloaded real data in `data/`, `E00` row in `results.tsv` (seed-stable baseline), reproduction of published SOTA where applicable.

Steps below are ordered by criticality. **Step 1 is time-critical (deadline 2026-04-27).**

---

## Step 1 — NVIDIA Academic Grant Program application ⚠️ TIME-CRITICAL

**Deadline: 2026-04-27 (6 days from today).** Miss this and the RTX 3060 + $300 Lambda/RunPod rental becomes the only path to the A100 headline.

- Application portal: https://www.nvidia.com/en-us/industries/higher-education-research/academic-grant-program/
- Write a 1-page research abstract describing the decoder-compute-aware resource estimation project; cite CUDA-Q QEC as the toolchain; request A100-class compute credits.
- Approval cycle: historically 4–8 weeks.
- **Fallback already budgeted:** $300 Lambda/RunPod rental if grant not awarded by 2026-06.

Outcome recorded in `data_sources.md` §2.

---

## Step 2 — Tooling install + RTX 3060 smoke runs

Create project venv (Python 3.11+, CUDA 12.x compatible with RTX 3060 compute-capability 8.6):

```bash
cd /home/col/generalized_hdr_autoresearch/applications/qec_resource_est
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install stim==1.15.0 pymatching==2.3.1 ldpc numpy scipy
pip install cuda-quantum[qec]  # CUDA-Q QEC v0.6 (verify CUDA 12 wheel)
pip install azure-quantum  # Azure Resource Estimator Python client
```

Verify each import in a smoke Python session; log versions to `data_sources.md` §1.

---

## Step 3 — Reproduce CUDA-Q QEC v0.4 published BP+OSD GPU benchmark (E00 candidate)

Goal: get a seed-stable number matching NVIDIA's published 29–42× BP+OSD GPU speedup at d=12 BB on SOME GPU (RTX 3060 counts; report the number consistent with consumer hardware).

1. Download `[[144,12,12]]` BB code definition from Bravyi 2024 supplement (or cudaq-qec examples).
2. Build Stim memory circuit at d=12 BB with SI1000 circuit noise at p=10⁻³.
3. Run BP+OSD iterations ∈ {10, 30, 100} on CPU `ldpc` v2 (baseline) and CUDA-Q QEC GPU (target).
4. Record: per-shot wall-time, LER, OSD invocation rate. Seed-stable (use `numpy.random.default_rng(42)`).
5. Write as E00 row in `results.tsv`:
   ```
   E00 | [[144,12,12]] BB + BP+OSD(iter=100) | CPU ldpc vs GPU CUDA-Q | p=1e-3 SI1000 | seed=42 | <wall-time-ratio> | KEEP | baseline
   ```

**Pass criterion:** CUDA-Q QEC GPU wall-time is 5–40× faster than CPU `ldpc` on the same host. If CUDA-Q QEC install fails on RTX 3060 (compute-capability 8.6 edge case), document in `data_sources.md` and proceed with CPU-only benchmarking until A100 access.

---

## Step 4 — Reproduce Azure Resource Estimator baseline for RSA-2048

Goal: run Gidney 2025's RSA-2048 compiled circuit (Zenodo DOI 10.5281/zenodo.15347487) through the Azure Estimator with default decoder assumptions to get the published logical-qubit-seconds number.

1. Download `code.zip` from Zenodo 15347487.
2. Run Azure Estimator Python client on the compiled Stim circuit, surface-code branch.
3. Confirm output matches Gidney 2025 published logical-qubit-seconds within 5%.
4. Record as E00_azure baseline in `results.tsv`.

**Pass criterion:** reproduction within 5%. This is the reference point the decoder-compute-aware extension will measure against.

---

## Step 5 — Update proposal to proposal_v3 reflecting Phase 0 findings

The research_queue amendments (R-PER-1a hybrid MWPM-GPU; R-PER-1b RTX 3060 + grant fallback) need to appear in the proposal text itself, not just the research queue. Write `proposal_v3.md`:

- §3 Method: replace "MWPM-GPU" with "CUDA-Q QEC v0.6 hybrid Ising-CNN-predecoder (GPU) + PyMatching (CPU) pipeline, pinned at commit hash <TBD Phase 0.5>"
- §6 Load-bearing parameters: replace "Single A100 24 GB" with "RTX 3060 (baseline, reported) + A100 (headline; acquired via NVIDIA Academic Grant by 2026-06 or Lambda/RunPod rental)"
- §Methods disclosure paragraph: hybrid-pipeline disclosure explicit
- Everything else preserved from proposal_v2

No fresh Phase 0.25 re-review needed (these are factual corrections aligned with the already-PROCEED'd proposal_v2 framing).

---

## Step 6 — Enter Phase 1 (experiment design)

Once Steps 1–5 are done, the project is Phase 0.5 complete and ready for Phase 1. Phase 1 builds the decoder-compute instrumentation and the extended Azure estimator plugin.

---

## Quality gates

- [ ] NVIDIA Academic Grant application submitted by 2026-04-27
- [ ] venv created with all deps installed; versions logged
- [ ] BP+OSD baseline run, E00 in results.tsv, seed-stable
- [ ] Azure Estimator baseline for RSA-2048 reproduced within 5%
- [ ] proposal_v3.md written reflecting R-PER-1a + R-PER-1b amendments
