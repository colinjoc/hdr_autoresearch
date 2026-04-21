# Phase 2.75 Methodology Review — qec_resource_est

Reviewer: fresh blind methodology auditor (Phase 2.75 gate). Inputs: files on disk only. No prior conversation. Date of audit: 2026-04-20.

## 1. Central-claim audit

Restated: *at circuit-level SI1000 noise p=10⁻³ over 12 rounds on one RTX 3060, the `[[144,12,12]]` BB gross code decoded by GPU BP+OSD (CUDA-Q QEC `nv-qldpc-decoder`, max_iter=100, sparse mode, per-shot loop) costs 16.4× more wall-time and ~127× more energy per shot than "12 patches of rotated surface-code d=12" decoded by CPU PyMatching v2, per logical-qubit-round — reversing Bravyi 2024's 12× qubit-count advantage once classical decoder compute is folded in.*

Traceability of every numerical assertion:

| Claim | Number | Source row in `results.tsv` | Source line in script |
|---|---|---|---|
| BB GPU BP+OSD wall-time | 3,705.13 μs/shot | `E02_BB_circuit_SI1000_p0.001` col `gpu_bposd_us` | `e02_bb_circuit.py` line 105 |
| BB CPU BP+OSD wall-time | 541,984.66 μs/shot | same row col `cpu_bposd_us` | `e02_bb_circuit.py` line 123 |
| 12× surface CPU MWPM wall-time | 226.66 μs/shot = 12 × 22.66... (actual `E03` one-patch = 23.52) | `E03_surface_d12_matched12` col 11 = 282.21 (script writes `cpu_us_12 = 12*cpu_us_one`) | `e03_surface_matched.py` line 71 |
| **Time ratio 16.4×** | 3710.05 / 226.66 (from `E04`) | `E04_BB_energy` wall-time (3710) vs `E04_surface_matched12_energy` (226.66) | `e04_energy.py` line 196 |
| BB GPU energy/shot "gross" | 233 mJ | **NOT in `results.tsv`** — the `E04_BB_energy` row stores `J_per_shot` column = 0.0000, which is `active_J/shots` after idle subtraction; the 233 mJ gross is only in `phase_1_findings.md` and `observations.md` | `e04_energy.py` line 131 `gross_J` is logged on stdout but the 233 mJ value never appears in `results.tsv` |
| Surface 12× MWPM energy/shot | 1.84 mJ | `E04_surface_matched12_energy` row col 13 | `e04_energy.py` line 188 — computed as `(65W / 8 cores) × wall_s/shot`, **not measured** |
| **Energy ratio 127×** | 233 / 1.84 | neither side traceable to a single TSV row — BB uses **gross** (in findings doc), surface uses **estimated TDP/8** | comparison is asymmetric by construction |
| Time discrepancy | E02 says GPU BP+OSD on BB = 3,705.13 μs; E04 re-ran same config and got 3,710.05 μs (≈0.1% variance — fine) | `E02_BB_circuit_SI1000_p0.001` vs `E04_BB_energy` | reproducibility is OK here |

**Major flags:**

- **The 233 mJ "gross J" figure is not in `results.tsv`** — only in narrative docs. Audit trail is broken for the headline energy number. `e04_energy.py` writes `J_per_shot` (active, after idle subtraction) to column 13, and the resulting TSV value for `E04_BB_energy` is `0.0000` (rounded). The 233 mJ/shot number exists only in the `findings.md` text. That must be fixed: either write `gross_J/shots` and `active_J/shots` as separate columns, or the claim is non-reproducible from the TSV alone.
- **The energy ratio "127×" uses apples-to-oranges energy definitions**: BB energy is **gross GPU power × wall-time** (includes the 11 W idle baseline running for 3 ms — which is ~33 mJ of pure idle just to keep the GPU alive during a 3 ms decode). Surface energy is **(65 W / 8 cores) × wall-time** = active single-core only, no idle baseline, no platform overhead. Findings docs even note that "active above idle" for BB is 76 mJ/shot (33% of gross); if the comparison used active-vs-active, the ratio collapses from 127× → 76/1.84 ≈ **41×** — still bad for BB, but less dramatic.
- **The "per logical-qubit-round" normalisation in `phase_1_findings.md` is wrong by 12×.** BB: 309 μs/LQR, surface: 18.9 μs/LQR. But 3710 μs / 12 = 309 and 226.66 / 12 = 18.9, which is μs-per-round (not μs-per-logical-qubit-round) — the division is by rounds only, not by (rounds × logicals). True per-logical-qubit-round is 3710 / (12 × 12) = 25.8 μs (BB) vs 226.66 / (12 × 12) = 1.57 μs (surface). The 16× ratio survives but the absolute numbers in the findings doc are off by a factor of 12. Fix before drafting.

## 2. Apples-to-apples hardware fairness

No. The comparison is structurally unfair.

- BB branch: GPU (CUDA-Q QEC `nv-qldpc-decoder`), per-shot loop, sparse mode, max_iter=100.
- Surface branch: CPU (PyMatching v2), single-core, no GPU path, no hybrid predecoder.

The proposal_v3 §3.1 itself commits to running the surface baseline on **"CUDA-Q QEC v0.6 hybrid Ising-CNN-predecoder (GPU) + PyMatching v2 (CPU), same commit-hash lock."** Phase 1 has *not* done this. Instead E03 uses pure CPU PyMatching. This directly contradicts the pre-registered pipeline. The 16.4× ratio therefore compares "GPU-with-kernel-launch-overhead-at-large-DEM" vs "CPU-with-no-overhead-at-small-DEM" — the choice of decoder-hardware is confounded with the code family.

The symmetric experiments needed:
1. **Surface on the same GPU path** (CUDA-Q QEC hybrid Ising-CNN + PyMatching, or CUDA-Q QEC `nv-qldpc-decoder` directly on the surface DEM). If surface GPU is slower than surface CPU at d=12 (likely — E00 shows this up to d=13 code-capacity), then the headline becomes "GPU doesn't help surface OR BB at this scale" — a very different paper.
2. **BB on CPU** as a non-confounded ablation. The current data has this: 541,985 μs/shot for BB CPU BP+OSD — 2,392× slower than 12× surface CPU MWPM. That is a much bigger story than the GPU-vs-CPU cross-pairing. The findings doc briefly mentions "surface wins even harder" in a caveat but this is the actually-apples-to-apples number and should be the primary headline (or at least co-headline).

Until the surface GPU number lands, the 16.4× should be reported as **"BB-on-GPU vs surface-on-CPU"** — an operational regime, not a decoder comparison.

## 3. Decoder-algorithm fairness

The project reports **time-per-shot**. It does **not** report logical error rate (LER) at matched operating points. This is a load-bearing omission.

- BP+OSD with max_iter=100 on d=12 BB at p=10⁻³ should land near the ~10⁻⁹ LER reported in Bravyi 2024 (per `knowledge_base.md`).
- MWPM on rotated-surface d=12 at p=10⁻³: `knowledge_base.md` line 41 itself says **matched surface-code distance is d ≈ 17–19** for the 10⁻⁹ target. Surface d=12 at p=10⁻³ gives LER ≈ 3 × 10⁻⁷ (naive (p/p_c)^((d+1)/2) estimate) — ~300× worse than BB.
- Therefore the "12 × surface d=12" baseline is *not LER-matched to the BB block*. The matched baseline would be 12 × surface d=17 (or d=19). At d=17, DEM size is ~2× larger than d=12, PyMatching wall-time grows by ~4× (d²), and per-patch cost goes from ~23 μs → ~90 μs → 12 × 90 = ~1100 μs for the 12-block. The 16× time advantage then becomes 3710 / 1100 ≈ **3.4×**, not 16×.

This is the biggest single threat to the headline claim. The project's **own** knowledge base says the matched-LER surface distance is 17–19, not 12. Using d=12 is the weakest possible surface baseline. `proposal_v3.md` §3.4 lists the pre-registered matched distance as d ∈ {15, 17, 19}. Phase 1 used d=12 and did not run 15/17/19. This is a pre-registration violation.

## 4. Code construction correctness

`e01_bb_codecap.py` and `e02_bb_circuit.py` both construct the code as:
```python
BBCode({x: 12, y: 6}, x**3 + y + y**2, y**3 + x + x**2)
```
Polynomials A = x³+y+y² and B = y³+x+x² on a 12×6 torus. This matches Bravyi 2024's `[[144,12,12]]` parameters symbolically.

**But**: `e01_bb_codecap.py` stores `bb.num_qubits` and `bb.dimension` (n and k) but **never verifies d=12**. Distance is a claimed parameter of the qLDPC package, not verified numerically. Given this is the headline code, there should be at minimum a check that `H_shape = (144, 144)` and ideally a minimum-distance certificate from qldpc, or cross-check of the LER curve against Bravyi 2024's Fig 3. Neither is present.

Additionally, the K=12 observable count is confirmed by E02's stdout (`12 observables`). So n=144, k=12 are implicit from the construction. d=12 is unverified — assume-and-hope.

Recommend: add `assert bb.num_qubits == 144 and bb.dimension == 12` and document that d=12 is the nominal value from Bravyi 2024, not independently verified in Phase 1.

## 5. Circuit-level noise model correctness

This is the second-biggest methodological concern.

- `e02_bb_circuit.py` uses `qldpc.circuits.SI1000NoiseModel(p)`. `e04_energy.py` uses the same. The canonical SI1000 model (Gidney 2021 arXiv:2107.02194) has **different per-channel rates**: 1-q Clifford ≈ p/10, 2-q Clifford = p, reset = 2p, measurement = 5p, idle = p/10, with specific SD6 vs SI1000 distinctions. Whether `qldpc.circuits.SI1000NoiseModel(p=1e-3)` actually implements this schedule or a simplified uniform-p variant is **not verified in any file on disk**. The `qldpc` package's own documentation would need to be consulted; the review cannot do so.
- `e03_surface_matched.py` uses `stim.Circuit.generated(code_task="surface_code:rotated_memory_z", ...)` with **all four noise parameters set to p=1e-3**:
  ```python
  after_clifford_depolarization=p,
  before_round_data_depolarization=p,
  before_measure_flip_probability=p,
  after_reset_flip_probability=p,
  ```
  This is a uniform depolarising schedule, **NOT SI1000**. SI1000 has measurement flip rate = 5p and idle = p/10, not all-p. So the surface branch experiences a noise model that is ~5× optimistic on measurements and ~10× pessimistic on idle compared to SI1000.

The BB and surface branches therefore run under **different circuit-level noise models**. Even if the 16× wall-time ratio is decoder-dominated and nearly noise-independent (plausible since BP+OSD and MWPM iteration counts do not depend strongly on error density at low p), the *LER comparison* §3 above is invalidated. The paper cannot claim "matched noise point" without fixing this.

Fix: either (a) build the surface circuit with a true SI1000 schedule (e.g. use `stim` noise replacement to set per-channel rates matching `qldpc.circuits.SI1000NoiseModel`), or (b) drop the BB side's SI1000 claim and run both under uniform depolarising-p.

## 6. Matched-overhead assumption

"12 × rotated-surface d=12 patches" is the weakest defensible baseline and arguably invalid:

- **LER mismatch (§3, §5)**: not matched at the 10⁻⁹ BB target. Correct distance is ~17–19 per the project's own knowledge base.
- **Patch-tiling is literal**: 12 independent patches with no shared ancilla or lattice-surgery overhead. Real FTQC architectures share bus-space routing; either the baseline is more expensive (routing) or cheaper (lattice surgery merge amortises some decoder effort over multiple logicals). The literal 12× scaling in `e03_surface_matched.py` line 71 (`cpu_us_12 = 12 * cpu_us_one`) is a back-of-envelope, not a compiled-circuit measurement.
- **Alternative baselines not evaluated**: (i) a single higher-distance patch carrying 12 logicals via domain walls / Steane-style block, (ii) a colour code block, (iii) a smaller [[k, d']] BB of appropriate d' matched to d=12 surface LER in the opposite direction. None are in the experiment matrix.
- **Decoder choice for matched surface**: PyMatching-only for the matched branch, but the surface-code LER at d=12 is high enough that soft-info or neural MWPM is the standard modern choice. Using vanilla PyMatching disadvantages the surface decoder-throughput number slightly (though PyMatching v2 is already very fast).

Strongest baseline for the paper: **12 × rotated-surface d=17** under true SI1000, PyMatching v2 CPU. That would drop the 16× to ~3–4× by my estimate. Still publishable as "decoder compute matters", but quantitatively different from the current headline.

## 7. Energy measurement methodology

(a) **GPU "gross J" includes idle baseline that is not decoder-specific.** `e04_energy.py` line 127 computes `active_joules = max(joules_total - idle_baseline_W × wall_s, 0)` — correct. But the headline "233 mJ/shot" cited in `observations.md` and `phase_1_findings.md` is **gross**, which includes ~11 W × 3.7 ms ≈ 41 mJ of idle baseline per shot. `active_J` is 76 mJ/shot by the findings doc. The 233 gross / 1.84 surface = 127× ratio therefore double-counts idle power that would exist whether or not the decoder ran. The correct decoder-attributed-energy comparison is 76 mJ / 1.84 mJ ≈ **41×**, still dramatic but 3× smaller. The findings doc acknowledges this in caveat 4 but the headline claim uses gross.

(b) **CPU energy via TDP/8** is very rough. `e04_energy.py` line 188: `sc_J_one = (TDP_W / 8) * (sc_wall / shots)` with TDP=65 W. This assumes (i) CPU is a 65 W TDP chip — author's actual CPU spec is not recorded anywhere in the repo that I can find, (ii) 8 cores share TDP equally, (iii) a single-core-bound workload draws exactly 1/8 of package TDP. In reality, a single active core can draw anywhere from 1/16 × TDP (light workload, other cores parked) to 1/2 × TDP (active core boosts to near-package-limit with others idle). Sensitivity: if single-core actually draws 65/4 = 16.25 W, surface energy doubles to 3.68 mJ, dropping the 127× to ~63× or (with gross→active adjustment) ~21×. If single-core draws 65/16 = 4 W, surface energy halves to 0.92 mJ, and 127× grows to ~254×. **The 127× is sensitive by ±2× to an unknown CPU TDP allocation model.**

Fix: replace TDP/8 with measured energy via `perf stat -e power/energy-pkg/` (Linux RAPL), or report the gross-vs-active BB comparison with matched-GPU-power surface (use the same NVML sampler during CPU decode — idle draw of ~11 W × 0.23 ms = 2.5 mJ of "GPU idle while CPU decodes" should be subtracted fairly).

## 8. Statistical power

E02 (BB circuit-level): 300 shots. E03: 300 shots. E04: 300 shots. `max_iter=100`. No repeats. No reported standard deviation. No confidence interval on the 16× or 127× ratio.

- 3,705 μs/shot × 300 shots = ~1.1 s total decode time. Variance from OS noise (GC, context switches, thermal throttling on consumer RTX 3060) over such a short window is not negligible. A standard practice is **≥3 independent replicate runs** and **≥10,000 shots per replicate** for headline decoder throughput numbers.
- 300 shots is fine for estimating a mean to ±5–10% if the underlying distribution is well-behaved. But the paper's headline is a **ratio of two means**, each estimated at 300 shots, on different hardware paths — so the compounded uncertainty is ±10–20% on the 16× (i.e. it could plausibly be 13× or 20×). Not enough to claim "inverts Bravyi's 12× advantage" with publication-grade confidence.
- Recommended minimum: 10,000 shots per cell, 3 replicates, report mean ± std across replicates. Wall-time cost ~30× current = ~30 s per cell, trivial. No reason not to do this.

## 9. Iteration-count sensitivity

`phase_1_findings.md` open items §"Next Phase 1 items" lists "iteration-count ablation at 10, 30, 100 on the circuit-level BB DEM" as not done. `proposal_v3.md` pre-registered iter ∈ {10, 30, 100}. This has not run at circuit-level.

E01 code-capacity shows **negligible iter effect** (iter=30 vs iter=100 within 1%: 198.58 vs 192.58 μs GPU, 40.54 vs 39.66 μs CPU at p=0.01). But this is code-capacity, not circuit-level. At circuit-level with H=936×10512, BP iteration cost is ~50× larger per iteration, and the OSD post-processor is typically invoked in only 5–15% of shots (per `knowledge_base.md`). So a 10× iter reduction could collapse BB GPU time from 3705 μs to ~500–1000 μs, shrinking the 16× to ~2–5×.

**This single axis could kill the headline.** It is pre-registered and not yet measured. Must run before paper draft.

## 10. Overclaiming check

Specific overclaim instances:

- `observations.md` §"Central finding": **"inverts"** the qubit-count advantage. Strictly true as stated (16× > 12×) but ignores that the 16× is on a non-LER-matched, hardware-asymmetric, non-SI1000 surface baseline. "Inverts" is stronger than data supports.
- `phase_1_findings.md` §"the paper's decisive result": **"decisive"** is too strong. Several pre-registered knobs remain unmeasured (iter count, matched distance, surface GPU path), each of which plausibly moves the ratio by ≥2×.
- `phase_1_findings.md` §"Interpretation": **"reverses"** — same issue.
- `proposal_v3.md` §2: **"hidden dominant cost"** — pre-registered phrase and fine *if* the other knobs do not collapse the ratio. Currently premature.
- `observations.md` "12× more energy-efficient per shot" uses the 127× figure from gross-vs-TDP/8; per §7 this is almost certainly between 40× and 60× on an apples-to-apples energy accounting. Overstated by ~2–3×.

Recommended language for the paper: "on RTX 3060 against a **d=12 surface-code floor** under **uniform depolarising p=10⁻³** with CPU PyMatching, the BB branch's decoder cost exceeds the surface branch by ~16× wall-time and ~40× decoder-attributed energy. The matched-LER comparison (d≈17 surface) reduces this to an estimated ~3–4× wall-time." Weaker but defensible.

## 11. Specific bugs / questionable choices in the scripts

- `e00_benchmark.py` line 125–149: the TSV writer **overwrites** the file with `open(tsv_path, "w")`, but `e00_azure.py`, `e01`, `e02`, `e03`, `e04` all **append**. Running E00 a second time clobbers all subsequent data. Fragile. Should append-only.
- `e02_bb_circuit.py` line 112: CPU BP+OSD `error_rate=float(rates.mean())` — uses the *mean* DEM error rate. But DEMs from circuit-level noise typically have a highly non-uniform `rates` vector (e.g. measurement errors at 5p, idles at p/10). Using the mean as a single scalar prior to BP is a **known BP degrader**. Should pass per-error rates via `channel_probs=rates` if the `ldpc.BpOsdDecoder` API supports it. If the BP CPU number is artificially slow because of this, the 2,392× BB-CPU-vs-surface-CPU number is pessimistic for the CPU BP+OSD side.
- `e02`, `e03`, `e04` all set shots=300 hard-coded. No CLI flag, no way to re-run with more shots without editing source. Low reproducibility.
- `e02_bb_circuit.py` line 34: `dem = circuit.detector_error_model(decompose_errors=False, allow_gauge_detectors=True)`. Note `decompose_errors=False` — for BP+OSD this is fine, but then there's no decomposition; this should be documented.
- `e03_surface_matched.py` line 50: `decompose_errors=True` for surface — needed for PyMatching. OK. But noise model is **not SI1000** per §5.
- `e04_energy.py` line 116: warm-up calls `decode_fn(i)` for `i in range(min(10, shots))` — only 10 warm-up shots. GPU JIT/kernel cache stabilises in 10–30 iters typically; for a 300-shot measurement the first ~5% of decodes may still be warm-up contaminated. Recommend 50 warm-up shots.
- `e04_energy.py` line 40–48: the NVML sampler uses `time.sleep(self.interval)` with `sample_hz=50` = 20 ms. The trapezoid integration is over ≤2 ms sample gaps; for a 1.1 s total decode window this gives ~55 samples. Fine for integration but **GPU power has sub-ms transients** that this will smooth out; gross J might be biased ±5%. Acceptable if documented.
- `e04_energy.py` line 177–188: the 12× projection for surface is `12 * cpu_us_one` — it runs **1 patch** and multiplies. So surface wall-time of 226.66 μs/shot is **not directly measured for 12 patches simultaneously**; it is a linear extrapolation assuming zero inter-patch cache effects. Real 12-patch decoding on 1 CPU serially will have cache-eviction penalties at this H size (~450K nonzeros × 12 = 5.4M). Best-case 12× assumption may be 1.2–1.5× optimistic.
- `e04_energy.py` line 149: CPU energy model uses **gpu idle_W** subtraction for GPU but **no baseline** subtraction for CPU. Asymmetric again.
- **No fixed random seed assertion for stim sampling** in E02, E03, E04. `sampler.sample(shots=300)` uses stim's default internal PRNG — not seeded. Re-running gives non-identical detector_events. The `seed=42` at top-level numpy is not plumbed through to stim. Results are therefore not bit-reproducible, only distributionally similar. Minor but relevant to reproducibility claims.

## 12. Top three recommended revisions before paper draft

1. **Run the matched-LER baseline (surface d=17) with true SI1000 noise, and the surface GPU path.** This is the single biggest threat to the headline. Required: rebuild `e03_surface_matched.py` with (a) per-channel SI1000 noise replacing uniform depolarising-p, (b) distance sweep d ∈ {15, 17, 19} per pre-registration, (c) hybrid Ising-CNN + PyMatching GPU path per pre-registration. Estimated cost: 1–2 days dev, <1 hour compute. Expected outcome: 16× likely collapses to 3–5×; 127× energy to 20–40×. Headline survives qualitatively, not quantitatively.

2. **Run the iteration-count ablation on the circuit-level BB DEM and add CIs.** Required: sweep iter ∈ {10, 30, 100} for E02 (GPU + CPU) and E04 (energy). Increase shots to 10,000 per cell with 3 replicates. Estimated cost: 1 hour dev, ~30 min compute. Expected outcome: either confirms the 16× is iter-count-robust (paper survives as-is) or shows the ratio is iter-sensitive (paper becomes a more nuanced "operating-regime" story). Either way, the ablation is pre-registered and cannot be skipped.

3. **Fix the energy accounting and per-logical-qubit-round arithmetic.** Required: (a) write gross_J and active_J as separate columns in `results.tsv` for *both* BB and surface; (b) replace TDP/8 with measured RAPL energy; (c) correct the per-LQR divide-by-12 bug (should be divide-by-144) in `phase_1_findings.md`; (d) report energy ratio using matched metrics (gross-vs-gross or active-vs-active, not gross-vs-TDP/8). Estimated cost: 2 hours dev, 30 min compute. Expected outcome: 127× becomes ~40–60× with proper accounting; per-LQR numbers shift but the ratio is stable. Primarily a credibility fix.

## VERDICT: MAJOR-REVISIONS

The headline numbers cannot be trusted without first addressing §3 (LER-matched distance), §5 (SI1000 vs uniform-p noise mismatch between branches), §2 (GPU-vs-CPU hardware asymmetry), and §9 (iteration-count ablation). Each of these is independently capable of moving the 16× ratio by ≥2×, and their combined effect plausibly collapses the headline to ~2–4× time, ~20–40× energy — still a story, but not "inverts the 12× Bravyi advantage." The project has the right tooling, the right pre-registration discipline (proposal_v3 is explicit about d ∈ {15,17,19}, hybrid GPU path, iter ∈ {10,30,100}), but Phase 1 ran a subset that happened to maximise the headline ratio. That is not a fraud pattern — it is the default consequence of running the easiest cells first — but it means the current observations.md central finding **overclaims relative to the pre-registered Phase 1 plan**.

Three top revisions (§12) are the minimum re-run list. They are cheap in compute (~1 hour total) and moderate in dev time (~1–2 days). Once they land, the paper is likely to pass Phase 2.75 re-review and proceed to drafting with a calibrated, defensible headline. The underlying claim that decoder compute matters is almost certainly correct; the precise multiplier needs to settle on apples-to-apples numbers.

Not REJECT — the methodology is fixable, the tooling is right, the pre-registration is genuine, and the central insight is plausibly true. Not ACCEPT-WITH-REVISIONS — too many load-bearing knobs are unmeasured to call this "ready to draft".

(Word count: ~2,430.)
