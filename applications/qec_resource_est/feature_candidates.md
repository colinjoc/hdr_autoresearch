# feature_candidates.md — qec_resource_est

Feature candidates for the Phase 2 measurement pipeline and Phase 3 Azure-estimator plugin. Features partition into **measured** (collected at Phase 2), **derived** (computed from measured), and **modelled** (taken from literature models).

See `design_variables.md` for the pre-registered axes; this file enumerates the specific features that will populate the plugin's `DecoderModel` and the headline tables.

---

## A. Measured features (Phase 2 collection)

### A-1. `bp_osd_wallclock_per_shot` (BB branch)
- Measured: μs per single-shot BP+OSD decode.
- Swept over: code distance d ∈ {6,8,10,12,14}, iter ∈ {10,30,100}, batch ∈ {1,100,1000}, GPU ∈ {3060, A100}.
- Instrumentation: `time.perf_counter_ns` wrap around `decoder.decode()` calls; averaged over ≥10⁵ shots after 10⁴-shot warm-up.

### A-2. `bp_osd_gpu_joules_per_shot` (BB branch)
- Measured: μJ per single-shot BP+OSD decode.
- Derivation: (average GPU power during window − idle power) × window duration / shots per window.
- Instrumentation: NVML `power.draw` at 1 Hz × 10-s windows with 10⁴ shots per window.

### A-3. `mwpm_hybrid_wallclock_per_round` (Surface branch)
- Measured: μs per QEC round for Ising-predecoder + PyMatching hybrid pipeline.
- Swept over: d ∈ {9,13,15,17,19}, batch ∈ {1,100,1000}, GPU.

### A-4. `mwpm_hybrid_combined_joules_per_round` (Surface branch)
- Measured: μJ per round for full GPU+CPU pipeline (wall-plug; GPU-rail-only variant also logged).
- Methodology: per A-2.

### A-5. `bp_osd_osd_invocation_rate` (BB branch)
- Measured: fraction of shots where OSD post-processing is invoked (BP fails to converge).
- Swept over: iter count.

### A-6. `bp_osd_logical_error_rate` (BB branch)
- Measured: LER at each (d, iter) cell.
- Target match: within 0.5–2× of expected Bravyi 2024 LER at p = 10⁻³.

### A-7. `mwpm_hybrid_logical_error_rate` (Surface branch)
- Measured: LER at each d cell under SI1000 noise.
- Target: ~p_L = 10⁻⁹ at d = 17 matching Gidney 2025's LER target.

### A-8. `gpu_thermal_steady_state_temp`
- Measured: junction temperature at end of 5-min warm-up.
- Purpose: ensure no thermal throttling during measurements.

### A-9. `cpu_utilization_during_hybrid_pipeline`
- Measured: CPU % used by PyMatching worker threads on host.
- Purpose: verify CPU is not the bottleneck in hybrid pipeline.

### A-10. `decoder_memory_footprint`
- Measured: peak GPU VRAM and host-RAM usage per decoder instance.
- Purpose: verify fit on 12 GB RTX 3060 + 32 GB host.

---

## B. Derived features (Phase 2/3)

### B-1. `total_decoder_joules_per_logical_qubit_second`
- Derived: `decoder_joules_per_shot` × `decode_rate_per_second_per_logical_qubit`.
- `decode_rate` = 1 / logical-cycle time × (syndrome-extractions per logical operation).

### B-2. `logical_qubit_seconds_total`
- Derived: logical qubits × wall-clock from Azure estimator with our logical-cycle-time extension.
- Formula: `logical_qubits × (T_cyc_base + μ_react × T_react)` × total cycles.

### B-3. `headline_metric_J_qubit_s`
- Derived: B-1 × B-2 (our project's core number).

### B-4. `bb_vs_surface_ratio_on_headline`
- Derived: BB's B-3 / surface's B-3.

### B-5. `bb_advantage_compression_factor`
- Derived: (raw BB qubit-count advantage) / (headline BB advantage).
- Pre-registered kill threshold: ≥2× triggers "hidden dominant cost" verdict.

### B-6. `matched_surface_distance`
- Derived: arg min_d {surface LER at d ≤ target} targeting B-5 match with BB.

### B-7. `reaction_time_sensitivity_slope`
- Derived: d(headline)/d(μ_react) across the {1,3,10} sweep.

### B-8. `iteration_count_sensitivity_slope`
- Derived: d(headline)/d(iter_count) across {10,30,100}.

### B-9. `energy_per_decode_scaling_exponent`
- Derived: log-log slope of energy vs code distance. BP+OSD expected O(d⁴); MWPM expected O(d² log d).

### B-10. `connectivity_cost_multiplier_effect`
- Derived: B-3 with B6 ∈ {1.0, 1.2, 1.5}. Range of B-5 across the three.

---

## C. Modelled features (from literature)

### C-1. `gidney_2025_t_count_for_rsa2048` — 10⁹ (model).
### C-2. `gidney_2025_logical_qubit_count` — ~1500 (model).
### C-3. `bravyi_2024_ler_at_d12_p_e3` — 10⁻⁹ (model).
### C-4. `rotated_surface_qubits_per_logical_at_d17` — 162 (model formula).
### C-5. `cultivation_t_equivalent_cost` — 1 qubit-round per output (Gidney 2024).
### C-6. `cultivation_output_infidelity` — 2 × 10⁻⁹ (Gidney 2024).
### C-7. `surface_code_threshold` — 0.7–1.1% depending on decoder (literature).
### C-8. `bb_code_threshold` — 0.8% (Bravyi 2024).
### C-9. `mu_react_rsa` — ~1 for RSA at cultivation-level magic supply (Gidney 2025).
### C-10. `syndrome_extractions_per_logical_cycle` — d for surface (round-by-round); variable for BB (single-shot in some regimes).

---

## D. Plugin-specific features (Phase 3 Azure-estimator extension)

### D-1. `DecoderModel.compute_latency_formula` — lookup table keyed on (code, d, iter, batch, GPU).
### D-2. `DecoderModel.compute_energy_formula` — lookup table keyed as above.
### D-3. `DecoderModel.mu_react_formula` — function of (code, algorithm_class).
### D-4. `QecSchemeExtended.logical_cycle_time_formula` — `T_cyc_base + μ_react × compute_latency`.
### D-5. `QecSchemeExtended.decoder_energy_per_cycle` — new field piped into a `total_decoder_energy` estimator output.

---

## E. Reporting tables (Phase 4)

### E-1. Table 1: raw BB and surface metrics at Phase 2 headline (d=12 BB / d=17 surface, p=1e-3, iter=100, μ_react=1, batch=1000).
### E-2. Table 2: sensitivity ablation grid — min/max of headline ratio across all {iter × μ_react × batch} cells.
### E-3. Table 3: A100 vs RTX 3060 comparison for toy d=6/d=9 case.
### E-4. Table 4: connectivity-cost-multiplier sweep B-10.
### E-5. Figure 1: energy-per-decode vs d for both decoders.
### E-6. Figure 2: reaction-time-sensitivity slope curves.
### E-7. Figure 3: BB advantage compression on headline vs iteration count.
