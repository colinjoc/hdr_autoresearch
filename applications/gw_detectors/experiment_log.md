# Experiment Log: Decomposing AI-Discovered GW Detectors

**RECONSTRUCTED.** The original `experiment_log.md` was lost on 2026-04-09 along with the rest of this project. This file is a reassembly of the experimental narrative from `paper.md`, the website summary, and an Explore-agent report from earlier in the same session. Numbers and per-experiment lessons match the paper. Per-commit timestamps are not recoverable.

## Goal

Reverse-engineer the type8/sol00 design from the Urania-discovered GW Detector Zoo to identify which components are essential, which are optimisation artifacts, and what physical mechanism drives the 3.12× improvement over LIGO Voyager in the post-merger band.

This is an Option C (decomposition) project — the Phase 2 loop runs in the ablation rhythm, not the forward-optimisation rhythm. See `program.md` Phase 2 Variant: Decomposition Loop.

## Setup

- **Simulator**: Differometor (JAX-based differentiable interferometer simulator)
- **Dataset**: GWDetectorZoo (50 AI-discovered detector designs from Krenn et al., Phys. Rev. X 2025)
- **Baseline**: LIGO Voyager (200 kg silicon test mass at 123 K, 2 µm laser, 10 dB FDS)
- **Target band**: 800–3000 Hz (post-merger)
- **Headline metric**: log-space-averaged improvement factor over Voyager strain

---

## Experiment summary

| ID | Experiment | Outcome | Status |
|---|---|---|---|
| exp01 | Voyager baseline | min strain 3.76e-25 /√Hz at 168 Hz, within 0.1% of published | BASELINE |
| exp02 | type8/sol00 post-merger improvement | 3.12× over Voyager | KEEP |
| exp03 | Cross-validate against Zoo CSV | Corrected exp02's initial mis-attribution: dominant mechanism is noise suppression, NOT signal amplification | VALIDATION |
| exp04 | Broadband characterisation | post-merger 3.12×; broadband ~1.2×; design is band-localised | CHARACTERISATION |
| exp05 | Topology inventory | 48 mirrors, 13 BSs, 3 lasers, 4 squeezers, 3 filter cavities, >120 free parameters | TOPOLOGY |
| exp06 | Component-level ablation | ~10 essential components; 4 squeezers all <0.5 dB; 11/13 cavities redundant; second laser is harmful | ABLATION |
| exp07 | Light-path analysis | Most "components" carry <0.001% of carrier power | ANALYSIS |
| exp08 | Cavity-level ablation | Only 2 of 13 four-km cavities are essential (the main Michelson arms) | ABLATION |
| exp09 | Cavity parameter extraction | Arm cavity finesse ≈ 6100 (vs Voyager 3100), at impedance-matching condition | ANALYSIS |
| exp10 | End-mirror mass sweep | Optimum at 7.3 kg; creates optomechanical spring resonance in post-merger band | SWEEP |
| exp11 | Homodyne angle sweep | 1.4% sensitivity variation across full 360° → essentially irrelevant | SWEEP |
| exp12 | Arm finesse ±5% sweep | Sharp peak: ±5% deviation drops design below Voyager. NARROW OPTIMUM (real physics) | NARROW_PEAK |
| exp13 | Beamsplitter R sweep [0.5–0.8] | All values within 5% of best. BROAD PLATEAU (parameterisation artifact) | BROAD_PLATEAU |
| exp14 | Minimal design + BS reoptimisation | **Headline result**: 10-component minimal design at BS=0.70 → **3.62× over Voyager (+16%)** | HEADLINE_RESULT |
| exp15 | Type8 family classification (25 solutions) | Two distinct mechanism families: noise suppression (dominant, includes sol00) and signal amplification (secondary, up to 13.7× signal gain) | FAMILY_SURVEY |

---

## Lessons (promoted to program.md Phase 2 Variant: Decomposition Loop)

1. **Component ablation before parameter sweeps.** First identify which components are essential (binary on/off ablation). Only sweep parameters of components that survive. Sweeping parameters of redundant components wastes effort and gives misleading sensitivity curves.
2. **Distinguish narrow optima from broad robustness.** Sharp peaks (±5% kills the design) indicate real physics — lock down tight specifications. Broad plateaus indicate the optimiser arbitrarily picked a workable point and can be improved by re-optimisation.
3. **Cross-validate decomposition against an independent source.** Differentiable simulators and step-based simulators can disagree on internal scales. The dominant mechanism for type8/sol00 was initially mis-identified as signal amplification before cross-validation against the GW Detector Zoo loss decomposition corrected it to noise suppression.
4. **Survey the family, don't extrapolate from one solution.** Distinct mechanism families can coexist within a single AI-discovered solution set. type8 has both noise-suppression and signal-amplification families.
5. **Verify the simplified design beats the original.** A successful decomposition produces a minimal design that, after re-optimising the broad-plateau parameters, exceeds the original AI-discovered performance. type8/sol00 minimal at BS=0.70 reached 3.62× vs the original 3.12× (+16%).
