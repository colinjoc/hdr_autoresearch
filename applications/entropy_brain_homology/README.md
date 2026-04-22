**Target type**: publication-target

# entropy_brain_homology — LLM-vs-Cortex Universality Class via Quantitative Exponent Comparison

## Target paper

**Post-Phase-0.25 reframe:** the paper tests whether activation avalanches from pretrained LLMs (GPT-2, Pythia, Gemma), Mamba SSMs, and a spiking-transformer (SpikeGPT-216M) satisfy **quantitative exponent equality** with awake-mouse-cortex Neuropixels data (Allen Institute Visual Coding), under a **field-canonical event-definition protocol whose end-to-end correctness is established by a synthetic branching-process validator** that is the first Phase 1 deliverable. The contribution is **the calibrated multi-substrate comparison and its validator**, not a novel cortex or LLM measurement — Morales-di Santo-Muñoz 2023 PNAS already placed Allen in edge-of-synchronisation and Doimo 2024 already measured per-token Lyapunov on LLMs. What is new is the joint block-bootstrap on a *validated* matched-protocol pipeline across five substrates (cortex + 3 dense LLMs + Mamba + SpikeGPT).

**Cortex treated as validation anchor, not discovery substrate.** Primary: Allen Institute Neuropixels Visual Coding via DANDI dandiset 000021 (data-access verified Phase 0.5, 4/4 tests pass, HDF5 magic bytes confirmed). Secondary: CRCNS ssc-3 status-polled every 2 weeks during Phase 1; if credentials have not arrived by end of Phase 1 week 3, pre-registered pivot to in-vivo-only + acknowledge slice-modality as limitation. Do not block the project on CRCNS.

## Bundled candidates (from ideation workspace)

From `applications/entropy_ideation/candidate_ideas.md` and `promoted.md`:
- **C18 (§2–§4) — Cross-substrate exponent-equality test.** Pretrained LLMs (GPT-2 / Pythia / Gemma) vs Allen Neuropixels. Joint block-bootstrap on (α, β, γ) under matched event-definition protocol. Cortex is the validation reference; LLM exponent estimate is the new observable.
- **C20 (§5) — Dense-vs-SSM architectural-class arm.** Mamba vs dense transformer. Halloran 2406.00209 predicts σ_SSM bounded below 1 on token axis by theorem; we test whether the measured Mamba exponents are consistent. MoE dropped per scope-check.
- **C22 (§6) — SpikeGPT literal-spike comparison arm.** Inference-only on public SpikeGPT-216M weights (github.com/ridgerchu/SpikeGPT); apply identical cortical-avalanche pipeline to spike raster. **Must include at-init SpikeGPT control (random weights) to distinguish trained-spiking-transformer criticality from architectural prior.** ~0.5 GPU-day.
- **NEW §1.5 / Phase 1 deliverable 1 — Synthetic branching-process validator.** Seed Galton-Watson process at known σ ∈ {0.90, 0.95, 0.98, 1.00, 1.02}; render into both "cortex-style" discrete spike rasters and "LLM-style" continuous layer-wise activations at subsampling fraction matching real data (p = 0.01–0.025). Both pipelines must recover seeded σ within 95 % CI or the joint-bootstrap headline fails and we retreat to "qualitative consistency" framing (venue steps down to *Entropy*).
- **Griffiths-phase / neutral-null rejection: explicitly scoped as out-of-reach** in this paper. Name the gap, don't operationalise it. Paper 1 (entropy_avalanches §7) carries that arm. Saying "we don't reject Griffiths-phase here, see Paper 1" is better than pretending to.

## Scope and constraints

- **Single RTX 3060 12 GB.** Inference-only across all arms.
- **Cortex data — primary: Allen Institute Neuropixels Visual Coding** via `allensdk` (no registration, public). 58 awake-mouse in-vivo recordings spanning V1 / LM / AL / PM / AM / RL / higher visual areas / thalamus / hippocampus; Kilosort2-sorted spikes in NWB format. Same substrate-modality as Fontenele 2024, so Paper 11 (entropy_effective_dimension) shares the cache. **Secondary: CRCNS ssc-3** (Ito et al., Beggs-lab deposit, DOI 10.6080/K07D2S2F). Registration-gated but submitted in parallel as fire-and-forget for free optionality; if credentials arrive during Phase 1, becomes the slice-modality comparison arm (slice DP vs in-vivo edge-of-synchronisation). Shriki 2013 MEG and Ma 2019 are not publicly archived — cannot be used. Must verify data access before Phase 1 per `~/.claude/projects/-home-col/memory/feedback_verify_data_access_before_phase_0.md`.
- **Matched protocol synthetic ground-truth test is mandatory** before claiming quantitative universality-class equivalence. Branching-process simulator at known α recovered to within CI on both pipelines (cortex-side and transformer-side) is the pass criterion.
- **Downgrade "universality class"** to "exponent equality under field-canonical protocols" per scope-check; exponent coincidence does not identify a class.

## Prior-art engagement (mandatory citations)

- Ghavasieh 2026 (arXiv:2512.00168, papers.csv 2046) — DP universality tuning in DNNs; theoretical only, no cortex-LLM empirical comparison. The cleanest nearest work.
- Arola-Fernández 2025 (arXiv:2508.06477) — Maximum-Caliber on toy maze, not trained LLMs.
- Gauthaman-Ménard-Bonner 2024 (arXiv:2409.06843) — visual-cortex covariance power law.
- Halloran 2025 (arXiv:2406.00209) — Mamba SSMs are Lyapunov-stable by theorem; if trained-weight exponents are strictly negative, Mamba is sub-critical on token axis by theorem. Must engage.
- Gu-Dao 2024 (arXiv:2405.21060) — Mamba-2 / structured-semiseparable-duality; defines SSM token-axis.
- Hengen & Shew 2025 (Neuron review, papers.csv 4006) — mandatory framing.
- Sooter 2025 (papers.csv 4007) — temporal RG on cortical data; sibling technique.
- SpikeGPT (Zhu, Zhou, Eshraghian 2023, arXiv:2302.13939) — public spiking transformer weights.

## Phase sequence

- **Phase 0 — deep lit review** (in progress; target 200+ citations spanning cortical avalanche methodology, RNN / LLM activation statistics, architecture-class universality theory, spiking-transformer literature, CRCNS data access protocols).
- **Phase 0.25 — publishability review** including cross-disciplinary venue audit.
- **Phase 0.5** — (a) Allen Neuropixels data-access smoke test via `phase_0_5_data_access.py` (primary, no-registration, ~15 min target); (b) submit CRCNS ssc-3 account request in parallel (fire-and-forget); (c) verify SpikeGPT-216M weights load on RTX 3060.
- **Phase 1** — pipeline build: matched event-definition protocol, synthetic branching-process ground-truth validator, cortex-side + transformer-side + SSM-side + SpikeGPT-side exponent extractors.
- **Phase 2** — experiments; joint bootstrap exponent-equality test across the four substrates.
- **Phase 2.75 / 3 / 3.5 / 4** per program.md.

## Venue target

**Post-Phase-0.25 reframe: drop Nature Machine Intelligence and PNAS from primary target.** Morales-di Santo-Muñoz 2023 PNAS already took the cortex-side bridge space; a hostile PNAS reviewer would frame this paper as "LLM-plumbing on already-published cortex result". Realistic venue ranking conditional on clean validator execution:

- **Primary: *Neural Computation*** (~60 % conditional on clean validator + positive exponent-equality).
- **Parallel submission: *Entropy* MDPI + NeurIPS UniReps workshop.** If validator fails its pass criterion at p = 0.01–0.025 subsampling, retreat to "qualitative consistency" framing and *Entropy* becomes primary (~80%).
- **Pythia scale-axis finite-size-scaling commitment:** compute (α, β, γ) across 5 Pythia scales (70M, 160M, 410M, 1B, 1.4B — drop 2.8B if VRAM-marginal) to give reviewers an FSS convergence test, not a single-point comparison. Without FSS the claim is "Gemma matches Allen at one point", which is weak.

## Phase 0.25 reframes applied (2026-04-21)

Full review at `publishability_review.md`. Six load-bearing reframes:
1. **Synthetic branching-process validator as first Phase 1 deliverable**, with pre-registered basis (render-into-spikes + render-into-continuous), block-bootstrap block length, and pass criterion at p = 0.01–0.025 subsampling.
2. **At-init SpikeGPT control** added to C22 arm (random-weight SpikeGPT inference).
3. **CRCNS upgraded from fire-and-forget to 2-week status-poll + pre-registered pivot-to-in-vivo-only.**
4. **Abstract reframing: cortex = validation anchor, not discovery substrate.** Morales 2023 is cited as "confirming Allen in edge-of-synchronisation"; our contribution is the validated multi-substrate pipeline, not a novel cortical exponent.
5. **Venue realignment.** Drop NatMI / PNAS from primary (Morales took the space); primary = *Neural Computation*; parallel = *Entropy* + NeurIPS UniReps workshop.
6. **Griffiths-phase rejection explicitly out-of-scope.** Reference Paper 1 (entropy_avalanches §7) for that arm; do not operationalise silently.

## Parent ideation

See `../entropy_ideation/` for the full portfolio.
