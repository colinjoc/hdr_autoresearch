# Data Sources — Phase 0 Smoke Test (qec_drift_tracking)

Date of smoke test: 2026-04-20.
Executed per `proposal_v3.md` §4.1 (primary data-access gate) and `feedback_verify_data_access_before_phase_0.md`.

## Decision

**OUTCOME: PRIMARY PATH PASSES.** Raw per-shot per-round syndrome streams are publicly downloadable from at least two independent vendor sources. Project proceeds on the primary-data path. §4.1.a synthetic-fallback dominance gate is NOT triggered; no KILL.

**Selected primary dataset:** Google Willow / Acharya et al. 2024, Zenodo DOI 10.5281/zenodo.13273331. Distance-3/5/7 surface-code memory experiments on 105-qubit Willow + repetition-code d=29 on 72-qubit Sycamore, ~50 000 shots per experiment, up to 250 QEC rounds per run, 420 experiments total, 112.5 GB. CC-BY 4.0.

**Secondary / cross-vendor dataset:** Rigetti Ankaa-2 / "Demonstrating real-time and low-latency quantum error correction with superconducting qubits," Zenodo DOI 10.5281/zenodo.13961130. Per-shot, per-round HDF5 with both hard and soft measurement results per qubit per repetition, ships with Stim circuits + qubit mappings. This gives us a second superconducting vendor for platform generality and drift-signature comparison.

**Scoop scan outcome:** No 2026 preprint publishes the three-way SMC-vs-sliding-window-vs-static drift-inference comparison on real Willow / Rigetti / H2 data at matched compute budget. Closest 2026 work is surveyed below and scoped distinctly from proposal_v3.

## Primary-path sources checked

| # | Source | URL checked | Result | Raw per-shot per-round? | Assessment |
|---|--------|--------|--------|---|---|
| 1 | Google Quantum AI datasets page | quantumai.google/qsim/datasets | 404 (page moved) | — | Not directly useful; dataset linked from Zenodo instead. |
| 1b | Google Research tools/datasets index | research.google/tools/datasets/ | page exists; generic index | — | Willow dataset is not hosted on research.google; it lives on Zenodo. |
| 2 | Zenodo — Willow 2024 | zenodo.org/records/13273331 "Data for Quantum error correction below the surface code threshold" | 200, CC-BY 4.0 | **YES** — 420 experiments, d=3/5/7, 50k shots × up to 250 rounds, 112.5 GB, README per archive | **PRIMARY CHOICE.** Matches the raw per-shot per-round requirement. Willow 2024 is exactly the Nature-paper dataset the proposal_v3 §4.2.a 1/hr cadence anchor cites. |
| 2b | Zenodo — Willow 2022 precursor | zenodo.org/records/6804040 "Suppressing quantum errors by scaling a surface code logical qubit" | 200 | **YES** — Sycamore d=3,5 memory experiment, raw stream | Available as a second Google dataset for cross-generation drift comparison (Sycamore → Willow). |
| 2c | Zenodo — "Demonstrating dynamic surface codes" | zenodo.org/records/14238907 | 200 | likely YES; same Google group | Extra Willow-era raw stream for dynamic-code experiments. Useful robustness slice. |
| 2d | Zenodo — Rigetti Ankaa-2 real-time QEC | zenodo.org/records/13961130 | 200 | **YES** — HDF5 per-shot per-round hard + soft, Stim circuits included, FPGA decoder outputs, T1 / readout calibrations | **SECONDARY CHOICE (cross-vendor).** Platform-general drift comparison, distinct superconducting vendor from Google. |
| 3 | arXiv ancillary — Acharya et al. 2408.13687 | arxiv.org/abs/2408.13687 | Data link points to Zenodo 13273331, confirmed | Handled via (2) | Consistent with Zenodo record. |
| 4 | GitHub — google-quantum-ai org | github.com/google-quantum-ai | org exists, redirects to quantumlib | — | No Willow-branded repo; QEC tooling lives in quantumlib/stim, quantumlib/tesseract-decoder, quantumlib/chromobius. Raw data is on Zenodo. Checked as of 2026-04-20. |
| 4b | GitHub — quantumlib org | github.com/quantumlib | 200; key repos: Stim, tesseract-decoder, chromobius, Cirq, qsim, OpenFermion, ReCirq, Qualtran, unitary | — | No raw-syndrome repos; infrastructure only. Stim-format assumed for Zenodo data given (2d) ships Stim circuits. |
| 5 | IBM Heron public QEC data | github.com/Qiskit + IBM Quantum Network pages + IBM qldpc Nature 2025 | No per-shot per-round stream identified | **NO** | IBM published the 288-qubit BB-code Nature 2025 result but raw syndrome stream is not on a public Zenodo / Qiskit repo as of 2026-04-20. Heron syndrome is accessible only via paid IBM Quantum Network runs. **Not usable as Phase 0 primary source.** |
| 6 | Quantinuum H2 public data | docs.quantinuum.com / QEC Decoder Toolkit + "most benchmarked quantum computer" blog claiming "publishes all the data" | Toolkit + Wasm + some per-shot data downloadable via vendor docs; not a single canonical Zenodo-style release | **PARTIAL** — single-shot QEC experiment data referenced in 2024 blog post; per-shot per-round QEC stream availability is fragmented | **Usable as a tertiary stress slice but not primary.** Trapped-ion timescale (drift behaviour very different from superconducting) makes it a natural cross-modality sanity check, not a headline slice. |
| 7 | Riverlane LCD benchmark release | github.com/riverlane + Nature Commun. 2025 paper + Deltakit textbook | Open repos (13 total) include Deltakit teaching material, LCD protocol reference, but no FPGA-LCD production raw syndrome release | **NO** (protocol open, production data not) | Confirms the PER-1 reimplementation-quality-gap risk directly: we must reimplement the LCD from the published protocol. No shortcut via raw Riverlane data. |

## Scoop scan — 2026 preprints in the SMC-on-QEC-drift-inference neighbourhood

Four candidates surfaced. None overlap the proposal_v3 contribution (three-way SMC vs sliding-window MLE vs static Bayesian, at matched compute, on real raw syndromes, LCD head-to-head, phase diagram over timescale × amplitude).

| Candidate | Nearest angle | Why it is NOT a scoop |
|---|---|---|
| arXiv:2603.00837 "ReloQate" (Feb 2026) | Transient drift detection via detector-fire-rate → LER prediction + logical-qubit remapping onto fresh tiles | Does NOT do SMC / particle-filter / sliding-window / static-Bayesian inference comparison. Method is DFR→LER regression + spatial remapping, which is orthogonal to drift-*inference* and complementary: one could imagine feeding our filter's drift estimate INTO a ReloQate-style remapper. Leaves the inference-method regime question fully open. |
| arXiv:2603.14687 "Adaptive Control of Stochastic Error Accumulation" (Mar 2026) | Chronological Deep Q-Network with internal belief state for noise evolution | Pure RL, simulation-only, no real data, no SMC comparison, no three-way methodological benchmark. Baselines are "static and recurrent" — not arXiv:2511.09491 / arXiv:2406.08981. |
| arXiv:2602.19722 "Differentiable Maximum Likelihood Noise Estimation" (Feb 2026) | Fully differentiable static MLE of circuit-level noise on Google processor data | Static, not drift-tracking. Baselines are correlation analysis + RL, not SMC / sliding-window. Naturally becomes a **fourth** static baseline for our Phase 2 diagram, not a scoop. |
| arXiv:2511.08493 "RL Control of QEC" (Nov 2025) | RL agent uses QEC detection events as learning signal for stabilization | RL angle, not Bayesian-inference angle. Compares against static baselines only. Orthogonal contribution. |
| arXiv:2512.10814 "Estimating Detector Error Models on Google's Willow" (Dec 2025) | Time-series of estimated DEMs on Willow data | **Most methodologically adjacent** — uses the same Zenodo dataset we propose to use. Needs careful read at Phase 0.5: if it already benchmarks SMC vs sliding-window vs static on Willow with a regime diagram, scope re-narrows. Abstract indicates DEM estimation time-series (per-window DEMs), which matches the sliding-window-MLE family, NOT SMC. Likely not a scoop on the SMC angle but a direct baseline to reproduce. **Flagged for Phase 0.5 deep read.** |

**Scoop decision: NO KILL.** No 2026 preprint delivers the three-way SMC/window/static + LCD-head-to-head + phase-diagram + real-data package that proposal_v3 commits to. The closest adjacent work (2512.10814) runs on our target data but is single-method (DEM time-series) and reinforces the benchmarking value rather than displacing it.

## Stim availability for synthetic fallback (defensive check)

Even though primary path passed, verified that Stim (Gidney 2021) is available as open-source Python/C++ (github.com/quantumlib/stim) so the §4.1.a synthetic fallback would have been executable if needed. Not triggered.

## Residual data-access risks to track

1. **Zenodo 13273331 is 112.5 GB** — plan local mirroring + GPU-local staging. TDD: time per-experiment load on a single file before scaling to all 420.
2. **Willow per-shot stream's round-to-round timestamp resolution** — the Nature paper reports operations across days; whether the per-shot timestamps distinguish "hours-scale drift" from "run boundary" needs to be verified once the README is read. If timestamp granularity is coarser than "per-run", the 1/hr drift slice of the phase diagram uses run-boundary bucketing rather than continuous timestamps. This does not kill Phase 0 but reshapes Phase 1 preprocessing.
3. **Licensing** — CC-BY 4.0 is compatible with open-source release of our derivatives. Confirm Rigetti dataset licence during Phase 0.5 ingestion.

## Summary line for proposal

> Phase 0 smoke test cleared on 2026-04-20. Primary data source: Google Willow Zenodo 13273331 (raw per-shot per-round, d=3/5/7, 112.5 GB, CC-BY 4.0); cross-vendor: Rigetti Ankaa-2 Zenodo 13961130. Scoop scan returned no 2026 preprint overlapping the three-way SMC / sliding-window MLE / static Bayesian + LCD-head-to-head + timescale×amplitude phase diagram on real raw syndromes. §4.1.a synthetic-fallback gate not triggered.
