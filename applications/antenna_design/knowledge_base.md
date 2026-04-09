# Antenna Design Knowledge Base

Cumulative reference of standard formulas, antenna-type cheat sheet, open-source tooling, and benchmarks. Consult before proposing any hypothesis.

---

## 1. Fundamental Formulas

### 1.1 Free-space wavelength and wavenumber

- lambda_0 = c / f0, with c = 2.998 x 10^8 m/s
- k0 = 2*pi / lambda_0
- At 1 GHz: lambda_0 = 299.8 mm. At 28 GHz: lambda_0 = 10.71 mm. At 60 GHz: lambda_0 = 4.997 mm.

### 1.2 Effective permittivity and guided wavelength (microstrip)

For a microstrip patch of width W on a substrate of permittivity epsilon_r and height h (W/h > 1):

    epsilon_reff = (epsilon_r + 1)/2 + (epsilon_r - 1)/2 * (1 + 12 h/W)^(-1/2)

    lambda_d = lambda_0 / sqrt(epsilon_reff)

### 1.3 Patch length and length extension (Hammerstad)

The open-end fringing field extends the electrical length of the patch. The length extension is

    Delta_L / h = 0.412 * (epsilon_reff + 0.3)(W/h + 0.264) / ((epsilon_reff - 0.258)(W/h + 0.8))

and the physical patch length for resonant frequency f0 is

    L = (c / (2 f0 sqrt(epsilon_reff))) - 2 * Delta_L

[Balanis ch. 14; Pozar 1992]

### 1.4 Patch width (Balanis design rule)

    W = (c / (2 f0)) * sqrt(2 / (epsilon_r + 1))

This choice maximises radiation efficiency for the fundamental TM10 mode.

### 1.5 Input impedance at patch edge

    R_in(edge) ~ 1 / (2 (G1 + G12))

where G1 is the self-conductance of a single radiating slot and G12 is the mutual conductance between the two slots. Typical edge impedance: 200--400 ohm. Inset-fed impedance:

    R_in(y0) = R_in(edge) * cos^2(pi * y0 / L)

This allows matching to 50 ohm by choosing y0 such that cos^2(pi y0 / L) = 50 / R_in(edge).

### 1.6 Resonant length of a half-wave dipole

    L_dipole ~ 0.47 * lambda_0  (corrected for wire radius)

Radiation resistance R_rad ~ 73 ohm; reactance ~ 42 ohm at exact half-wavelength; resonance achieved by slight shortening.

### 1.7 Radiation resistance (small dipole, length l << lambda_0)

    R_rad = 20 pi^2 (l / lambda_0)^2  [ohm]

### 1.8 Directivity of a uniform linear array (N isotropic elements, d = lambda_0/2, broadside)

    D ~ N  (linear scale)
    D_dB ~ 10 log10(N)

### 1.9 Gain, directivity, efficiency

    G = eta_rad * D
    eta_rad = P_rad / P_in
    G_dBi = 10 log10(G)

Typical patch efficiency: 80--95% below 6 GHz; drops to 50--70% at mmWave due to conductor and dielectric losses.

### 1.10 Friis transmission formula (free space)

    P_r / P_t = G_t * G_r * (lambda_0 / (4 pi R))^2

Or in dB:

    P_r_dBm = P_t_dBm + G_t_dBi + G_r_dBi - 20 log10(4 pi R / lambda_0)

Path loss at 1 GHz and 1 km: ~92.4 dB; at 28 GHz and 1 km: ~121.3 dB.

### 1.11 Fractional bandwidth of a rectangular patch (Balanis)

    BW ~ 3.77 * (epsilon_r - 1) / epsilon_r^2 * (W/L) * (h / lambda_0)   for VSWR < 2

Bandwidth scales linearly with h/lambda_0 and inversely with epsilon_r, making thicker low-permittivity substrates the standard BW-enhancement route.

### 1.12 Q-factor decomposition

    1/Q_total = 1/Q_rad + 1/Q_cond + 1/Q_diel + 1/Q_surf

Bandwidth is approximately 1/Q_total. Losses (Q_cond, Q_diel) reduce BW but also reduce efficiency.

### 1.13 VSWR / return loss / reflection coefficient

    Gamma = (Z_L - Z_0) / (Z_L + Z_0)
    VSWR = (1 + |Gamma|) / (1 - |Gamma|)
    Return_loss_dB = -20 log10(|Gamma|) = -S11_dB

S11 = -10 dB corresponds to VSWR = 1.925, |Gamma|^2 = 0.1 (10% reflected power).

### 1.14 Horn antenna gain (aperture efficiency eta_ap)

    G_horn ~ 4 pi A / lambda_0^2 * eta_ap

with A = physical aperture area. Pyramidal horns achieve eta_ap ~ 0.5; optimum-gain designs ~0.51; corrugated horns up to 0.8.

### 1.15 Array grating lobe condition

For a uniform linear array with spacing d and scan angle theta_0, grating lobes appear when

    d / lambda_0 > 1 / (1 + |sin(theta_0)|)

Broadside arrays (theta_0 = 0) can use d up to 1 lambda_0; fully steerable arrays require d <= 0.5 lambda_0.

### 1.16 FDTD Courant stability (3D)

    delta_t <= delta_x / (c sqrt(3))    (for uniform delta_x)

Yee grid requires 10--20 cells per wavelength for <1% dispersion error.

---

## 2. Common Antenna Types — Quick Reference

(See `design_variables.md` section 5 for design parameters.)

| Type | Typical Gain | BW (fractional) | Efficiency | Size | Common Applications |
|------|--------------|------------------|------------|------|---------------------|
| Half-wave dipole | 2.15 dBi | ~10% | >95% | L ~ 0.47 lambda_0 | Reference; broadcast FM |
| Folded dipole | 2.15 dBi | ~15% | >95% | L ~ 0.47 lambda_0 | TV receivers |
| Quarter-wave monopole | 5.15 dBi | ~10% | ~95% | L ~ 0.25 lambda_0 | Mobile, car whip |
| Yagi-Uda | 6--12 dBi | ~10% | >90% | several lambda_0 | VHF/UHF directive |
| Log-periodic | 6--10 dBi | 10:1 | >90% | several lambda_0 | Broadband measurements |
| Rectangular patch | 2--8 dBi | 1--5% | 80--95% | ~0.5 lambda_0 | WiFi, GPS, satellite |
| Wideband patch (U-slot) | 5--9 dBi | 10--25% | 80--90% | ~0.5 lambda_0 | UWB, radar |
| Stacked patch | 5--10 dBi | 10--30% | 75--90% | ~0.5 lambda_0 | Satellite, dual-band |
| PIFA (inverted-F) | 2--5 dBi | 5--20% | 80--95% | ~0.25 lambda_0 | Mobile phones |
| Rectangular slot | 3--6 dBi | 5--20% | 80--95% | ~0.5 lambda_0 | Vehicular, radomes |
| Annular slot | 3--5 dBi | 10--30% | 85--95% | ~0.3--0.5 lambda_0 | Circular polarisation |
| Fractal (Koch / Sierpinski) | 2--6 dBi | multiband | >85% | 0.3--0.5 lambda_0 | IoT, miniaturisation |
| Meandered monopole | 2--4 dBi | 5--15% | 70--90% | 0.1--0.2 lambda_0 | RFID, wearable |
| Dielectric resonator | 5--10 dBi | 10--20% | >95% | ~0.3 lambda_0 | mmWave, 5G |
| Horn (pyramidal) | 10--25 dBi | 20:1 | 40--80% (ap.) | several lambda_0 | Gain-standard, radar |
| Parabolic reflector | 25--60 dBi | 10--50% | 50--70% (ap.) | 10+ lambda_0 | Satellite, deep-space |
| Helix (axial mode) | 10--15 dBi | ~70% | ~90% | several lambda_0 | Circular polarisation, satellite |
| Phased array (N elements) | 10 log10(N) + G_elem | depends on element | > 80% | N * 0.5 lambda_0 | Radar, 5G beamforming |

---

## 3. Simulation Methods — Comparative Summary

(From literature review table, section 2.4.)

| Criterion | FDTD | FEM | MoM |
|-----------|------|-----|-----|
| Broadband capability | Excellent (single run) | Poor (per-frequency) | Poor (per-frequency) |
| GPU acceleration | Excellent | Moderate | Difficult |
| Complex geometry | Staircasing | Excellent | Surface only |
| Open-source maturity | Good | Limited | Good (wires) |
| Dataset generation speed | Fast | Slow | Moderate |
| Memory scaling | O(N) | O(N) | O(N^2) unless MLFMA |

**HDR default**: GPU-FDTD for dataset generation; FEM for targeted validation of geometrically complex designs.

---

## 4. Open-Source EM Simulator Catalogue

| Tool | Method | Lang/API | GPU | License | Notes |
|------|--------|----------|-----|---------|-------|
| gprMax | FDTD | Python + OpenCL | Yes (single + multi-GPU OpenCL) | GPL v3 | Antenna-focused; GPR origins; well-documented Python API |
| Meep | FDTD | Python / Scheme / C++ | Limited (CPU MPI primary) | GPL v2 | MIT, photonics-heavy; adjoint gradient support via `meep.adjoint` |
| openEMS | FDTD (EC-FIT) | Matlab/Octave + Python | Partial | GPL v3 | Unstructured mesh adapters; strong microstrip support |
| MEEP/MPB | FDTD + mode solver | Python | No | GPL v2 | Useful for photonic-crystal/metasurface design |
| NEC-2 / nec2c | MoM (wire) | Fortran, C port | No | Public domain | Wire antennas; 4nec2 GUI popular for HAM designs |
| FEKO student edition | MoM + MLFMA | GUI + scripting | No (student) | Free (restricted) | Node-limited, adequate for small benchmarks |
| OpenParEM | FEM | C++ / Python | Partial | LGPL | Scalable parallel FEM |
| Ansys HFSS student | FEM | GUI + PyAEDT | No (student) | Free (restricted) | Industry reference; limited student licence |
| CST Studio student | FIT/FDTD | GUI | No (student) | Free (restricted) | Heavy GUI, good for cross-check |

### 4.1 Differentiable simulators (critical for inverse design)

| Tool | Method | Framework | GPU | Notes |
|------|--------|-----------|-----|-------|
| FDTDX | FDTD | JAX | Yes | GPU-accelerated differentiable FDTD; the natural HDR backbone for adjoint-based design |
| Meent | RCWA/FMM | PyTorch | Yes | Differentiable metasurface/grating simulator; photonic focus but usable for RF metasurfaces |
| meep.adjoint | FDTD | Python | No | Analytic adjoint gradients inside Meep (CPU only) |
| ceviche / ceviche-challenges | FDFD | autograd / JAX | Partial | 2D inverse-design reference implementations |
| TidyFDTD / JAX-FDTD | FDTD | JAX | Yes | Research projects; API unstable |

### 4.2 ML toolkits for antenna design

- **AntennaCAT** (Linkous et al., GitHub: LC-Linkous/AntennaCAT): surrogate training + optimisation pipelines.
- **PyAEDT**: Python wrapper for ANSYS AEDT; full HFSS automation.
- **Emopt**: adjoint-method EM optimisation (photonics, some RF).
- **scikit-optimize / BoTorch**: general Bayesian optimisation libraries used for surrogate-assisted antenna design.

---

## 5. Benchmark Datasets

| Dataset | Source | Size | Target | Notes |
|---------|--------|------|--------|-------|
| URSI 2024 Microstrip Dataset | LC-Linkous GitHub | 27,026 entries | 1.5 / 2.4 / 5.8 GHz | HFSS simulations; strong ML baseline target [80] |
| CST 2.4 GHz Patch with Slot | Data in Brief 2025 | ~1 month of sweeps | 2.4 GHz | Parametric ML benchmark [81] |
| Mendeley Antenna Parameters | Mendeley Data 2024 | varies | gain, S11, directivity, eta | Tabular format [79] |
| PathWave ADS Dataset | Keysight 2024 | 1,000 antennas | 0.5--10.5 GHz | Multi-substrate sweep [82] |

Use URSI as the primary Phase-A supervised benchmark and CST 2.4 GHz slot dataset for the first transfer-learning experiment.

---

## 6. Published ML Benchmarks for Antenna Prediction

| Model | Dataset / Target | Metric | Reference |
|-------|------------------|--------|-----------|
| MLP (3--5 layers) | S11 across parametric patch sweeps | <1 dB MAE (widely reported) | [37, 38] |
| CNN on 10x10 pixels | S11 across topology variants | 150k training samples for <1 dB MAE | [34, 71] |
| BNN-LSTM | Frequency-dependent S-parameters | Comparable to GP, better scaling | [35] |
| SB-SADEA (BNN surrogate) | Surrogate-assisted DE antenna optimisation | Competitive with GP SADEA | [36] |
| Kriging (PCA-reduced) | High-dimensional patch optimisation | 50--200 samples sufficient | [32, 39] |
| Co-kriging multi-fidelity | Gain / S11 prediction | ~90 HF evals converge | [73] |
| NETO (adjoint + NN) | Topology optimisation | 40x speedup over iterative FEM | [67] |
| FNO | Maxwell equations / metasurface | Mesh-independent generalisation | [46, 112] |

---

## 7. Current Best Scores (HDR local leaderboard)

(To be populated after baseline runs.)

| Experiment | Metric | Score | Notes |
|------------|--------|-------|-------|
| Phase A — patch S11 MLP baseline | MAE [dB] | TBD | H1 |
| Phase A — CNN on pixel geometry | MAE [dB] | TBD | H3 |
| Phase B — inverse design pixel patch | BW improvement vs rect | TBD | H11 |
| Phase B — 28 GHz benchmark | (gain, BW, eta) | TBD | H21 |

---

## 8. What Works (to be populated)

## 9. What Doesn't Work (to be populated)

## 10. Key Domain Facts

- Centre frequency of a rectangular patch is primarily set by L and epsilon_r; width mainly controls input impedance and BW.
- Bandwidth of a thin-substrate patch is ~1--5%; BW scales linearly with h/lambda_0.
- FR4 is unusable for high-efficiency designs above ~2 GHz due to tan(delta) = 0.02.
- Mutual coupling in arrays becomes critical for d < 0.5 lambda_0; target isolation for MIMO is >=25 dB.
- Circular polarisation requires two orthogonal modes 90 degrees out of phase; common realisations are corner-fed patches or truncated-corner patches.
- GPU-FDTD achieves 17x--80x speedups that make 1k--150k training datasets tractable.
- Adjoint methods scale to thousands of design variables in constant simulator cost; BPSO does not.
- S11 < -10 dB is the standard impedance-match target; equivalent to <10% reflected power or VSWR < 2:1.
- Most ML surrogates published to date are trained for a single antenna family; cross-family transfer is an open problem.
- Current pixelated inverse-design grids are limited to ~10x10; scaling to 100x100 is an open challenge.
