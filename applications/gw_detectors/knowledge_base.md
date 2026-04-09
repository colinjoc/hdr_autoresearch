# Knowledge Base — gw_detectors

**RECONSTRUCTED.** The original `knowledge_base.md` was lost on 2026-04-09. This file is a reassembly of the established facts and accumulated insights from `paper.md` and the Explore-agent report.

## Established baselines

| Quantity | Value | Source |
|---|---|---|
| LIGO Voyager strain minimum | 3.76 × 10⁻²⁵ /√Hz at 168 Hz | Adhikari et al. 2020, Class. Quantum Grav. 37 165003 |
| Voyager arm cavity finesse | ~3100 | Voyager design document |
| Voyager test mass | 200 kg silicon at 123 K | Voyager design document |
| Voyager laser wavelength | 2 µm | Voyager design document |
| Voyager FDS depth | 10 dB | Voyager design document |
| Standard quantum limit | h_SQL(f) = √(2ℏ/(M(2πf)²L²)) | Caves 1981, Phys. Rev. D 23, 1693 |

## Urania / GW Detector Zoo facts

| Quantity | Value | Source |
|---|---|---|
| Number of designs in Zoo | 50 | Krenn et al. 2025, Phys. Rev. X 15, 021012 |
| Best post-merger improvement (type8/sol00) | 3.12× over Voyager (800–3000 Hz) | Krenn et al. 2025 |
| Best broadband improvement | up to 5.3× → ~50× observable volume | Krenn et al. 2025 |
| UIFO parameter count for type8/sol00 | >120 free parameters, 48 mirrors, 13 BSs, 3 lasers, 4 squeezers | This work, exp05 |
| Optimisation method | BFGS with 1000 random restarts | Krenn et al. 2025 |

## Decomposition results (from this work)

### Component essentiality (type8/sol00)

| Component type | In original | Essential | Notes |
|---|---|---|---|
| Lasers | 3 | 1 | Removing the second laser improves sensitivity by 3% |
| Squeezers | 4 | 0 | All 4 carry <0.5 dB; effectively unused |
| Arm cavities (4 km) | 13 | 2 | Only the two main Michelson arms |
| Beamsplitters | 13 | 1 | A single 70:30 beamsplitter |
| Filter cavities | 3 | 0 | No frequency-dependent squeezing required |
| **Total** | **48 mirrors + 13 BSs + 3 lasers + 4 squeezers** | **~10 components** | |

### Mechanism contributions to improvement

| Mechanism | Contribution | Physical description |
|---|---|---|
| Critical cavity coupling | 65% | Arm cavity finesse ~6100, mirror reflectivities precisely impedance-matched |
| Light test mass (7.3 kg) | 35% | Optomechanical spring resonance in 800–3000 Hz band |
| Asymmetric beamsplitter | 10% | 70:30 split balances signal pickup vs radiation pressure |

(Sums to >100% because mechanisms partially overlap.)

### Re-optimisation result

| Design | BS reflectivity | Improvement |
|---|---|---|
| type8/sol00 (Urania original) | 0.81 | 3.12× |
| Minimal design, AI's BS | 0.81 | 3.18× (matches) |
| **Minimal + re-optimised BS** | **0.70** | **3.62× (+16%)** |

### Parameter sensitivity classification

| Parameter | Regime | Implication |
|---|---|---|
| Arm cavity finesse | Sharp peak — ±5% kills design | Real physics; lock down to tight tolerance |
| Beamsplitter reflectivity | Broad plateau in [0.5, 0.8] | Parameterisation artifact; re-optimise |
| Homodyne readout angle | Flat (1.4% over 360°) | Irrelevant; no precision alignment needed |
| End-mirror mass | Sharp peak at 7.3 kg | Real physics; spring resonance in target band |

### Family classification (25 type8 solutions)

| Family | Count | Dominant mechanism | Max signal gain |
|---|---|---|---|
| Noise suppression | dominant | Critical cavity coupling + light test mass | n/a |
| Signal amplification | secondary | Aggressive signal-recycling cavity tuning | 13.7× |

## Methodology lessons (synthesised, also in program.md)

1. **Component ablation before parameter sweeps.**
2. **Distinguish narrow optima (real physics) from broad robustness (parameterisation artifact).**
3. **Cross-validate decomposition against an independent source.**
4. **Survey the family, don't extrapolate from one solution.**
5. **Verify the simplified design beats the original.**

## Surprises that became headline insights

- **No squeezing needed.** All 4 squeezers carry <0.5 dB. Quantum noise suppression comes from ponderomotive squeezing built into the cavity topology, not external squeezed light.
- **Multi-laser pumping is redundant.** Removing the second laser improves sensitivity by 3% — the optimiser added it but never used it productively.
- **Homodyne angle is irrelevant.** Only 1.4% sensitivity variation across 360°. No precision phase alignment required.
- **Two distinct mechanism families coexist.** Among 25 type8 solutions, some use noise suppression and some use signal amplification (up to 13.7× signal gain). The "explanation" of the AI's discovery is plural.
- **The simplified design beats the original.** After re-optimising the broad-plateau BS parameter, the 10-component minimal design reaches 3.62× vs the AI's 3.12×. Decomposition is not just interpretation — it's an improvement step.
