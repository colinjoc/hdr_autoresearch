# Design Variables — gw_detectors

**RECONSTRUCTED SKELETON.** The original `design_variables.md` (~10 KB) was lost on 2026-04-09. This is a smaller reconstruction derived from `paper.md` and the Urania paper.

## What the UIFO parameterises

A Urania UIFO is an n×n grid of optical elements (mirrors and beamsplitters) connected by ports. Each element exposes a small set of physical parameters that the optimiser can adjust.

## Per-element parameters

| Element | Parameters | Range | Notes |
|---|---|---|---|
| Mirror | reflectivity R | [0, 1] | R=0 transparent, R=1 perfect reflector |
| Mirror | mass | [0.1, 200] kg | Voyager: 200 kg silicon |
| Mirror | temperature | [4, 300] K | Voyager: 123 K |
| Beamsplitter | reflectivity R | [0, 1] | Standard 50:50 → R=0.5 |
| Laser | input power | [0, 1000] W | |
| Laser | wavelength | discrete (1064 nm, 1550 nm, 2 µm) | Voyager: 2 µm |
| Squeezer | level | [0, 15] dB | 0 dB = unused |
| Squeezer | angle | [0, 360] deg | |
| Cavity | length | [10 m, 4 km] | Arm cavities: 4 km |
| Photodetector | homodyne angle | [0, 360] deg | |

## Derived quantities (computed from elements)

| Quantity | Formula | Notes |
|---|---|---|
| Arm cavity finesse | F = π√R/(1-R) | for input mirror reflectivity R |
| Standard quantum limit | h_SQL(f) = √(2ℏ/(M(2πf)²L²)) | M = test mass, L = arm length |
| Spring resonance frequency | ω_s = √(K/M) | K = optical spring constant from radiation pressure |

## Components and counts in type8/sol00 (the headline design)

| Element type | Count | Essential? (this work) |
|---|---|---|
| Mirrors | 48 | ~6 essential |
| Beamsplitters | 13 | 1 essential |
| Lasers | 3 | 1 essential (2nd is harmful) |
| Squeezers | 4 | 0 essential (all <0.5 dB) |
| Filter cavities | 3 | 0 essential |
| **Total free parameters** | **>120** | |

## Scope reduction strategy used in this project

Per `program.md` Phase 2 Variant: Decomposition Loop, this project ablates components (binary on/off) BEFORE sweeping continuous parameters. The reasoning: a parameter sweep on a redundant component is wasted work. exp06 (component ablation) and exp08 (cavity ablation) reduce the parameter space to a tractable size before exp10–exp13 (parameter sweeps) and exp14 (rebuilding + reoptimisation).
