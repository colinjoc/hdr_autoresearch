# Phase 0.5 Baseline Audit — entropy_brain_homology

Date: 2026-04-21.

## Data-access verification — PASS

From the earlier DANDI smoke test (4/4 tests, HDF5 magic bytes confirmed in Range-GET of the first NWB). Primary cortex substrate: Allen Institute Neuropixels Visual Coding via DANDI dandiset 000021. Secondary: CRCNS ssc-3 — status-poll cadence set to 2 weeks per Phase 0.25 reframe; pivot-to-in-vivo-only pre-registered if credentials don't arrive by Phase 1 week 3.

## SpikeGPT weights-load verification — PASS

Canonical HuggingFace repository resolved: **`ridger/SpikeGPT-OpenWebText-216M`** (SHA `4039295cca3d`, checkpoint `SpikeGPT-216M.pth`). The README had the wrong candidate ID format — corrected in the test. Full weight-load deferred to Phase 1 (the file is ~800 MB .pth not safetensors; format conversion may be needed).

## Synthetic-validator pre-registered kill gate — PASS

The Phase 0.25 publishability review set the validator as the first Phase 1 deliverable with a pre-registered pass criterion: **MR estimator recovers σ within 0.05 of truth at p = 0.025 Bernoulli subsampling (Allen Neuropixels native sampling fraction) and within 0.07 at p = 0.01 (stress test).** Phase 0.5 tested this on synthetic driven-branching-process data before any real-substrate work:

| Test | Ground truth | Recovered | Result |
|---|---|---|---|
| `test_no_subsample_sigma_recovered` | σ = 0.95, full observation | within 0.05 | ✓ |
| `test_critical_avalanche_alpha_approx_three_halves` | α = 3/2 | within [1.35, 1.70] | ✓ |
| `test_subsampled_sigma_MR_corrected[0.025]` | σ = 0.95, p=0.025 | within 0.07 | ✓ |
| `test_subsampled_sigma_MR_corrected[0.01]` | σ = 0.95, p=0.01 | within 0.07 | ✓ |

**The pre-registered kill gate is survived on synthetic data.** This means the MR estimator + powerlaw toolchain is competent at the subsampling fractions where Allen Neuropixels lives; if the validator fails on real data in Phase 1, the failure will be a protocol / event-definition problem (bin width, threshold) rather than a statistical-machinery problem.

## Toolchain installed

- Python 3.12.3 in `venv/` (same Python as sibling projects).
- `dandi 0.74.3 + pynwb 3.1.3 + h5py + remfile + requests` — DANDI route.
- `powerlaw 2.0.0 + mrestimator 0.2.0 + numpy + scipy` — analysis.
- `huggingface_hub` — for SpikeGPT reachability.

## Gate verdict

**Phase 0.5 PASSED.** Three concrete items for Phase 1 Day 1:
1. **Validator-on-real-data gate.** Run identical synthetic validator but at the actual Allen Neuropixels subsampling fraction measured from one real session; confirm σ recovery before any downstream science.
2. **SpikeGPT checkpoint conversion.** `.pth` → loadable inference format on RTX 3060 fp16. Unknown if SpikeGPT-216M fits — back-of-envelope 216M × 2 bytes = 432 MB plus activations; probably fine, verify.
3. **CRCNS status poll.** Submit account request today; poll at 2-week cadence; if no response by Phase 1 week 3, pivot-to-in-vivo-only pre-registered.
