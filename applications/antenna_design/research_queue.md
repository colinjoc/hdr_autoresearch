# Research Queue: Antenna Design HDR

Prioritised hypotheses for HDR cycles.

Format:
```
### H[N] — [Title] [STATUS]
Impact: HIGH / MEDIUM / LOW
Hypothesis: ...
Mechanism: ...
```

Status: OPEN | RESOLVED | RETIRED

Phases:
- **Phase A (forward prediction)**: Predict antenna performance (gain, S11, BW) directly from geometry parameters.
- **Phase B (inverse / generative design)**: Discover novel topologies via inverse design, beat published benchmarks, explore miniaturisation and multi-band behaviour.

---

## Phase A — Forward Prediction

### H1 — MLP baseline for S11 prediction on rectangular patch [OPEN]
Impact: HIGH
Hypothesis: A 4-layer MLP (256-256-128-64) trained on ~5,000 GPU-FDTD simulations of rectangular microstrip patches will predict peak S11 within 1 dB MAE across 1--6 GHz.
Mechanism: Rectangular patches have 5--6 dominant parameters (L, W, h, epsilon_r, y0, W_f) and a smooth response surface dominated by the transmission-line/cavity model [18, 94, 95]. MLPs trained on 3k-10k samples have achieved <1 dB S11 MAE in prior work [37, 38]. This is the minimum viable surrogate before attempting anything harder.

### H2 — Log transform of h and epsilon_r improves surrogate accuracy [OPEN]
Impact: MEDIUM
Hypothesis: Replacing raw h and epsilon_r with log(h) and log(epsilon_r) will reduce surrogate S11 MAE by at least 10%.
Mechanism: Resonant frequency scales as 1/sqrt(epsilon_reff) and effective permittivity depends nonlinearly on h/W. A linear regression in log-space matches the physical scaling, saving network capacity for interaction effects [1, 3].

### H3 — CNN on pixelated geometry beats MLP on parameters [OPEN]
Impact: HIGH
Hypothesis: A CNN operating on a 32x32 binary image of the patch + slot geometry will out-predict a parametric MLP on a held-out set of U-slot and E-slot designs (broader topology family).
Mechanism: Parametric MLPs cannot generalise across topology changes. CNNs operating on pixelated representations have demonstrated S-parameter prediction across varying geometries when trained on 150k datasets [34, 71]. Our hypothesis is that even with 10k samples, a CNN will transfer better across slot variants.

### H4 — Multi-output head for (gain, S11, BW) jointly improves over per-target networks [OPEN]
Impact: MEDIUM
Hypothesis: A single branched-output network predicting gain, S11 sweep, and -10 dB bandwidth jointly will have lower test error than three separately trained networks with the same total parameter count.
Mechanism: The three targets share physical structure (all depend on cavity-mode excitation). Multi-task learning regularises representations and improves sample efficiency [38, 149]. Prior work at IEEE AWPL 2024 reported a ~15% improvement for branched-output architectures.

### H5 — Bayesian NN surrogate matches GP accuracy at 10x parameter count [OPEN]
Impact: MEDIUM
Hypothesis: A BNN (MC-dropout or variational) will match Gaussian Process mean prediction RMSE on a 5-parameter patch benchmark with <=5% degradation, while scaling to 15+ parameters where the GP fails.
Mechanism: The SB-SADEA result [36] shows BNNs can replace GPs for surrogate-assisted antenna optimisation. The cubic scaling of GPs is the bottleneck; BNNs scale linearly. We want to verify that the uncertainty estimates remain calibrated enough for acquisition functions.

### H6 — Fourier Neural Operator predicts E-field distribution across substrate [OPEN]
Impact: HIGH
Hypothesis: An FNO trained on FDTD-generated (epsilon_r(x, y), E_z(x, y)) pairs will predict the near-field distribution of novel patch geometries with <5% L2 error.
Mechanism: FNOs learn mappings between function spaces and have been applied to Maxwell-equation metasurface problems [46, 47, 112]. Unlike parametric networks, FNOs generalise across geometry without re-training.

### H7 — Transfer learning from patch to slot halves required training samples [OPEN]
Impact: MEDIUM
Hypothesis: A model pre-trained on 10k patch simulations and fine-tuned on 500 slot simulations will match the accuracy of a from-scratch model trained on 1,000 slot simulations.
Mechanism: The underlying physics (TM modes, cavity resonance) is shared across patches and slots via Babinet duality. Feature extractors learned on one topology should transfer [49, 50].

### H8 — GPU-FDTD dataset at multiple mesh resolutions enables multi-fidelity surrogate [OPEN]
Impact: HIGH
Hypothesis: A co-kriging multi-fidelity model trained on 1,000 low-resolution (lambda/10) and 100 high-resolution (lambda/30) simulations will match a single-fidelity model trained on 500 high-resolution samples.
Mechanism: Co-kriging has demonstrated ~90 high-fidelity evaluations suffice for convergence vs 200+ single-fidelity [73]. This directly enables the 70% speedup and 85% cost savings reported in [72, 74].

### H9 — Global sensitivity analysis identifies top-5 parameters for rectangular patch [OPEN]
Impact: MEDIUM
Hypothesis: Sobol indices computed from surrogate evaluations will rank L, epsilon_r, h, y0, W as the top-5 influential parameters, and fixing all others will not increase held-out error by >5%.
Mechanism: Sensitivity analysis studies [40, 76] have repeatedly identified length and substrate parameters as dominant. Confirming this enables 2x--3x dimensionality reduction for subsequent optimisation rounds.

### H10 — PCA of S11 sweeps reduces output dimensionality without accuracy loss [OPEN]
Impact: MEDIUM
Hypothesis: Projecting a 201-point S11 sweep onto the top-10 PCA components will preserve 99% of variance, enabling a surrogate that predicts 10 numbers instead of 201 with no loss in reconstructed-sweep MAE.
Mechanism: Antenna S11 sweeps are highly correlated across frequency and dominated by a small number of resonant features. PCA-reduced Kriging surrogates have been demonstrated in [39].

---

## Phase B — Inverse Design and Novel Topologies

### H11 — BPSO + CNN surrogate discovers 10x10 patch outperforming rectangular benchmark [OPEN]
Impact: HIGH
Hypothesis: Binary PSO over a 10x10 pixel grid, using a CNN surrogate, will discover a pixelated patch with >=10% wider bandwidth than the rectangular reference at the same footprint and f0.
Mechanism: This replicates the framework of [71] which demonstrated automated structure generation. The rectangular patch is a known sub-optimum of the pixel design space; the literature gap we address is verifying transfer to mmWave frequencies.

### H12 — Inverse design via adjoint FDTD beats BPSO+CNN at 32x32 resolution [OPEN]
Impact: HIGH
Hypothesis: Differentiable FDTD (FDTDX in JAX) will find higher-gain designs in a 32x32 pixel domain than BPSO+CNN, using fewer wall-clock hours.
Mechanism: Adjoint methods compute gradients for all N pixels with 2 simulations regardless of N, while BPSO requires O(N) evaluations per iteration. Adjoint-based topology optimisation has a 40x design-time advantage in NETO [67] and memory savings in [65]. The scalability gap widens with resolution.

### H13 — Fractal iteration order as a learnable variable yields multi-band designs [OPEN]
Impact: MEDIUM
Hypothesis: Parameterising Koch/Sierpinski fractal iteration depth as a continuous-relaxed variable and optimising with a surrogate will discover 3+ usable bands for a given footprint, beating hand-designed fractal antennas [16, 97, 98, 99].
Mechanism: Fractal antennas show 3--4 resonances per iteration level. The literature uses fixed iteration orders; we hypothesise that jointly optimising iteration order and local perturbations yields better multi-band performance than either alone.

### H14 — Metasurface inverse design via neural operator finds novel unit cells [OPEN]
Impact: MEDIUM
Hypothesis: Starting from a random metasurface unit cell and optimising via FNO+adjoint, we can discover unit cells achieving >5% relative bandwidth improvement over split-ring-resonator references at 28 GHz.
Mechanism: [46, 52] showed GAN/FNO-based metasurface design can produce designs "completely distinct from training data". We replicate at 28 GHz (5G NR) and measure the benchmark gap against SRR.

### H15 — Miniaturisation via meandering achieves 50% size reduction at <=2 dB gain loss [OPEN]
Impact: HIGH
Hypothesis: Automated meandering optimisation will reduce monopole antenna footprint by 50% while losing less than 2 dB gain, matching the best hand-tuned IoT designs [125].
Mechanism: Meandering introduces inductive loading, trading physical length for electrical length. The trade-off curve is well characterised; the hypothesis is that ML-guided search finds a better Pareto point.

### H16 — NSGA-II over (gain, footprint, BW) finds dense Pareto front [OPEN]
Impact: MEDIUM
Hypothesis: NSGA-II with a CNN surrogate will generate >=50 non-dominated designs spanning gain 2--10 dBi, footprint 0.1--1 lambda^2, BW 2--20%, within a computational budget of 500 high-fidelity evaluations.
Mechanism: NSGA-II is the dominant algorithm for antenna multi-objective design [55, 61]. Surrogate integration cuts the evaluation budget by 10x [74].

### H17 — Multi-band patch via simultaneous slot + stacked layer [OPEN]
Impact: MEDIUM
Hypothesis: Jointly optimising slot geometry and a stacked parasitic layer will yield a dual-band patch with isolation >20 dB between bands at 2.4 and 5.8 GHz, beating the URSI 2024 dataset baseline [80].
Mechanism: Slots add a resonance below the fundamental; stacking adds a resonance above. Joint optimisation is more efficient than sequential tuning. The URSI dataset provides a head-to-head benchmark.

### H18 — Yield-aware optimisation reduces -10 dB BW sensitivity to fabrication by 30% [OPEN]
Impact: MEDIUM
Hypothesis: Including a Monte Carlo fabrication tolerance term (sigma = 50 um on L, W) in the optimisation objective will produce designs whose worst-case S11 across tolerance sampling is 30% better than nominal-only optimisation.
Mechanism: Response-variability essential directions [76] identify the parameters whose deviations most affect performance. Yield-driven design [75] routinely trades 5--10% nominal performance for large robustness gains. We replicate for a representative 5 GHz patch.

### H19 — Reinforcement learning agent transfers across patch shapes [OPEN]
Impact: LOW
Hypothesis: A PPO agent trained to modify rectangular-patch parameters and rewarded by S11 improvement will, without retraining, yield positive improvement when deployed on U-slot patches.
Mechanism: Deep RL for topology optimisation has demonstrated 40% weight reduction while maintaining compliance in structural problems [70]; we test whether learned "design strategies" transfer across antenna families.

### H20 — Physics-informed loss improves small-dataset surrogate accuracy [OPEN]
Impact: MEDIUM
Hypothesis: Adding a Maxwell residual loss term to an MLP surrogate trained on 1,000 samples will reduce S11 test MAE by >=15% relative to a data-only MLP.
Mechanism: PINN-type losses embed physical consistency constraints [42, 113] and provide inductive bias useful when data is scarce. Known open challenges with high-frequency multi-scale problems [168] make this a high-risk experiment but with clear upside if loss balancing is tuned.

### H21 — Differentiable simulation beats published 28 GHz benchmark in mmWave patch [OPEN]
Impact: HIGH
Hypothesis: An adjoint-optimised mmWave patch at 28 GHz will achieve simultaneous gain >=8 dBi, BW >=10%, and efficiency >=85%, beating the best CST-tuned baseline reported in [34].
Mechanism: The mmWave regime is where GPU-FDTD acceleration matters most [26, 27]. Pixel-level gradients via adjoint [65, 67] enable richer designs than parametric search. This is the most ambitious benchmark-beating claim.

### H22 — GAN-generated UWB slot designs reach 10:1 bandwidth [OPEN]
Impact: MEDIUM
Hypothesis: An ACWGAN or RGAN trained on the CST slot dataset [81] will generate designs achieving >=10:1 BW ratio after a short fine-tuning optimisation, matching the 13:1 record in [19].
Mechanism: GAN-generated designs have been shown to produce "completely distinct" topologies from training data [52]. The fractal slot benchmark provides a clear target.

### H23 — Active learning halves samples needed for target MAE [OPEN]
Impact: HIGH
Hypothesis: Uncertainty-guided active learning with a BNN surrogate will achieve the same S11 MAE as random sampling with 50% fewer simulations.
Mechanism: Active learning concentrates evaluations where the surrogate is uncertain [74]. The 85% cost savings reported in [74] suggest substantial room for improvement over uniform sampling; we target a conservative 50% reduction for the first HDR cycle.

### H24 — 3D DRA topology optimisation on GPU-FDTD outperforms 2D patch at mmWave [OPEN]
Impact: LOW
Hypothesis: A 3D topology-optimised dielectric resonator antenna will achieve higher radiation efficiency (>=95%) than an equivalent 2D patch (<90%) at 60 GHz.
Mechanism: DRAs eliminate conductor losses, which dominate at mmWave. Open challenge [400] in the literature (3D topology optimisation rarely addressed). This is speculative but high-leverage if it works.

### H25 — Meta-learning over antenna families enables few-shot new-topology surrogates [OPEN]
Impact: MEDIUM
Hypothesis: A MAML-trained meta-surrogate over (patch, slot, DRA, meandered) families will converge on a new topology with <=100 samples, matching the accuracy of a from-scratch model with 1,000 samples.
Mechanism: Few-shot learning addresses the expensive-simulation bottleneck [184]. Directly builds on the transfer-learning result in H7 but with a meta-objective across families.
