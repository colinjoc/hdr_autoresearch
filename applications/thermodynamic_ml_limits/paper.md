# Thermodynamic Speed Limits on Machine Learning: A Systematic Quantification of the Gap Between Current Practice and Fundamental Bounds

## Abstract

We systematically quantify the gap between current machine learning (ML) training energy consumption and fundamental thermodynamic limits. Applying established thermodynamic frameworks (Landauer's principle; finite-time Landauer, Proesmans et al. 2020; the thermodynamic uncertainty relation, Barato and Seifert 2015; the Crooks fluctuation theorem, Crooks 1999) to GPU-based neural network training, we compare a hierarchy of upper bounds on the rate of functional information gain during training. At the operating point of a 25,000-GPU cluster training a GPT-4-class model (17.5 MW, 350 K junction temperature), the bare Landauer bound permits 5.22 x 10^27 bits/s of information gain. Stacking corrections for model FLOPS utilization (MFU), housekeeping power (data movement), mixed precision, sparsity, and static leakage tightens this bound by a combined factor of roughly 10^10--10^14, with the width of the range driven by the uncertainty in the housekeeping fraction, in the gradient noise scale, and in the chosen precision. The single technical contribution of this work is a reformulation of the TUR bound using the independently measurable Gradient Noise Scale (McCandlish et al. 2018), resolving a circularity in prior formulations; this yields a bound in the range 10^23--10^25 bits/s (central value 3.71 x 10^24 at B_noise = 10^6, extrapolated from McCandlish et al. 2018 with approximately one order of magnitude of uncertainty). Even at the tightest end of this range, the bound remains at least 10^7 above the estimated actual functional information gain rate for GPT-4 training, whose own functional-information estimate carries 3.6 orders of magnitude of uncertainty (4.3 x 10^5 to 1.8 x 10^9 bits). The bounds compared here are therefore not the binding constraint on today's ML training; economics and engineering are. This paper provides the calibrated framework that will be needed at the 10^5--10^6 efficiency improvement horizon projected for CMOS or at the onset of reversible, photonic, or neuromorphic computing, where the thermodynamic limits begin to matter.

## 1. Introduction

The energy cost of training large machine learning models has grown dramatically, with frontier models consuming hundreds of megawatt-hours of electricity (Patterson et al. 2021; Luccioni et al. 2023; Cottier et al. 2024). This growth -- at 2.4x per year since 2016, with training compute doubling every 3.4 months since 2012 (Amodei and Hernandez 2018; Sevilla et al. 2022) -- raises the question: how far is current ML training from fundamental physical limits on computation?

Landauer (1961) established that erasing one bit of information requires dissipating at least kT ln 2 of heat, where k is Boltzmann's constant and T is the absolute temperature. Bennett (1973) showed that computation itself can be logically reversible, so the irreducible cost lies in erasure, not logic. At 350 K (a typical GPU junction temperature under load), the Landauer limit is 3.35 x 10^-21 J per bit. An NVIDIA H100 GPU dissipating 700 W at this temperature has a theoretical information processing ceiling of 2.09 x 10^23 bits/s -- a figure that is many orders of magnitude above any meaningful definition of the rate at which the GPU acquires functional information during training.

This gap is well known at the level of individual operations: Koomey et al. (2011) showed that current CMOS operates approximately 10^9 above the Landauer limit per arithmetic operation, while Horowitz (2014) measured specific energy costs of 0.2-4.6 pJ per multiply-accumulate (MAC) operation at 45 nm. Goldt and Seifert (2017) established the formal connection between stochastic thermodynamics and neural network learning, showing that information acquired by a network is bounded by the thermodynamic cost of learning.

The contribution of this paper is not to discover this gap but to systematically quantify it using multiple thermodynamic frameworks, identify which correction factors dominate, and establish a framework for comparing thermodynamic efficiency across ML systems and biological substrates. Only one step in this work is not directly lifted from the prior literature: the substitution of the independently measurable Gradient Noise Scale of McCandlish et al. (2018) into the TUR, which removes the circularity that arises in naive TUR formulations when the observable's variance is itself what the bound is used to estimate. The remainder is synthesis, applied accounting, and sensitivity analysis. We provide:

1. A taxonomy of six multiplicative correction factors; stacked, these tighten the bare Landauer bound by 10^10--10^14, with the range set by uncertainties in the housekeeping fraction, gradient noise scale, and choice of numerical precision
2. A reformulated TUR bound using independently measurable gradient statistics, resolving a circularity in prior formulations (the paper's single technical novelty)
3. Sensitivity analysis showing which parameters most affect the bounds
4. Uncertainty quantification for functional information estimates
5. A cross-substrate comparison with biological information processing

We emphasize transparency about limitations: the finite-time Landauer formula's geometry constant B_geom = pi^2 applies to idealized overdamped erasure (Proesmans et al. 2020), not directly to CMOS gates; the Crooks-derived bound for stochastic gradient descent (SGD) is a heuristic, not a rigorous derivation; functional information estimates carry 3.6 orders of magnitude of uncertainty; the Gradient Noise Scale value B_noise at GPT-4 scale is extrapolated, not measured, and carries approximately one order of magnitude of uncertainty; and all calculations use published specifications rather than direct measurements.

### 1.1 Relation to prior work

A handful of recent papers cover closely adjacent ground and a reader is entitled to ask what this paper adds.

- **Goldt and Seifert (2017)** formalised the stochastic-thermodynamics interpretation of perceptron learning, showing that the information a network acquires is bounded by the thermodynamic cost of learning. Their bound is foundational for the Crooks-for-SGD manoeuvre adopted here (§2.2) but predates the Gradient Noise Scale machinery and the multi-factor engineering taxonomy we assemble for modern large-scale training.
- **Peng, Sun, and Duraisamy (2024, *Entropy*)** develop the stochastic thermodynamics of learning parametric probabilistic models, formulating training as a thermodynamic process with explicit entropy-production accounting and distinguishing memorised from learned information. Their framework overlaps with ours in spirit, but they do not apply the TUR, do not quantify the multi-factor engineering gap at cluster scale, and do not reformulate around the Gradient Noise Scale.
- **Meier, Peper, and Isokawa (2025)** derive Landauer bounds for deep-network inference on a per-neuron basis, using logic closely parallel to our §3.2 derivation but applied to inference, not training.
- **Kolchinsky and Wolpert (2020, *PRR*)** quantify the thermodynamic cost of Turing machines and establish a generalised Landauer framework for computation; our Landauer-counting analysis is an application of their framework to training dynamics, not an advance on it.
- **Wolpert (2019)** is the canonical review of the stochastic thermodynamics of computation; we recommend it as the single best entry point to the field and do not attempt to extend its framework in any foundational way.

What remains distinctive to this paper, after setting these comparators aside, is: (a) the GNS-TUR substitution that removes the observable-variance circularity; (b) the six-factor engineering taxonomy stacked at GPT-4 scale with explicit uncertainty propagation; and (c) the cross-substrate comparison with biology.

## 2. Background and Thermodynamic Frameworks

### 2.1 Landauer's Principle and Finite-Time Extensions

Landauer's principle states that erasing one bit in a system coupled to a thermal reservoir at temperature T requires dissipating at least kT ln 2 of heat (Landauer 1961). This was experimentally verified by Berut et al. (2012) using a colloidal particle in a double-well potential.

The quasistatic Landauer bound assumes infinitely slow erasure. Proesmans, Ehrich, and Bechhoefer (2020) derived the finite-time extension:

    W_min(tau) = kT ln 2 + B_geom * kT / tau

where tau is the erasure time and B_geom >= pi^2 for overdamped Brownian motion in a symmetric double-well potential. At GHz clock frequencies (tau ~ 0.5 ns), the second term dominates the first by approximately 10^10.

**Important caveat**: The B_geom = pi^2 result applies specifically to the Brownian particle model system, not to CMOS transistor switching. Real CMOS gates have switching dynamics governed by RC time constants and parasitic capacitances, not by overdamped thermal diffusion in a potential well. We use this formula as a theoretical reference point but rely on measured CMOS energy data (Section 3.3) for physically meaningful bounds.

### 2.2 Stochastic Thermodynamics of SGD

SGD can be modeled as Langevin dynamics with effective temperature T_sgd = eta * sigma_g^2 / (2B), where eta is the learning rate, sigma_g^2 is the gradient noise variance, and B is the batch size (Mandt et al. 2017; Li et al. 2017). This connection enables applying tools from stochastic thermodynamics to ML training.

The Crooks fluctuation theorem (Crooks 1999) constrains the work distribution for microscopically reversible stochastic dynamics. Adapting this to SGD (heuristically -- see Section 6.1 for caveats), the information gain rate is bounded by:

    dI/dt <= dot_Q / (kT ln 2 * (1 + T_sgd / T))

When T_sgd -> 0, this recovers the bare Landauer bound. When T_sgd >> T, the bound tightens by the factor T/T_sgd, reflecting the additional entropy produced by SGD noise. We validated this formula via Jarzynski equality testing (Section 4.2): it holds approximately for small learning rates but fails for large ones.

### 2.3 Thermodynamic Uncertainty Relation

The TUR (Barato and Seifert 2015) states that for any current J in a non-equilibrium steady state (NESS):

    Var(J) / <J>^2 >= 2 k_B / sigma_dot

where sigma_dot is the entropy production rate. Interpreting functional information gain as a thermodynamic current requires an independent estimate of the current's variance. We use the Gradient Noise Scale (GNS) from McCandlish et al. (2018):

    B_noise = tr(Sigma_grad) / ||g||^2

For batch size B >> B_noise, the relative variance epsilon = B_noise / B is independently measurable from gradient statistics. This yields:

    <J> <= sigma_phys * B / (2 * k_B * B_noise)

All quantities on the right-hand side are independently measurable: sigma_phys = P/T from power monitoring, B is a hyperparameter, and B_noise is estimated from gradient samples. This resolves the circularity in naive TUR formulations where epsilon depends on <J>.

### 2.4 Quantum Speed Limits

The Margolus-Levitin bound (Margolus and Levitin 1998) limits the maximum computation rate to 2E / (pi * hbar) operations per second for a system with energy E. The Bekenstein bound (Bekenstein 1981) limits information content in a sphere of radius R with energy E. Both are vacuously loose for classical ML training (exceeding the Landauer bound by 10^13 or more) but are included for completeness and to establish the full hierarchy.

## 3. Methods

### 3.1 Operating Points

We evaluate bounds at two operating points:

**Single GPU (H100)**: 700 W thermal design power (TDP), TSMC N4 process (4 nm), 350 K junction temperature, 989 TFLOPS FP16 peak throughput (NVIDIA 2022). Representative of small-scale training (e.g., XGBoost with 10^6 parameters, ~60 s training time).

**GPT-4-class cluster**: 25,000 H100 GPUs, 17.5 MW total power, ~90 days training time, ~2 x 10^25 total training FLOPS, ~1.36 x 10^14 J total energy (Cottier et al. 2024; industry estimates).

### 3.2 Correction Factor Taxonomy

Six multiplicative correction factors tighten the bare Landauer bound:

1. **MFU (Model FLOPS Utilization)**: Only a fraction MFU of peak hardware FLOPS contribute to useful computation. Typical values: 0.3-0.6 for large-scale LLM training (Chowdhery et al. 2023).

2. **Housekeeping fraction (phi)**: Fraction of total power consumed by data movement (DRAM access, HBM bandwidth, interconnect) rather than arithmetic. From Horowitz (2014) energy data and operational intensity analysis: phi ~ 0.39 for transformers (attention-heavy: phi ~ 0.69; dense layers: phi ~ 0.10).

3. **Mixed precision (p_bits/32)**: Reduced-precision training (FP8, INT4) erases fewer bits per parameter update. Factor: p_bits / 32 (e.g., 0.25 for FP8).

4. **Sparsity (1-s)**: Sparse training updates erase only the non-zero fraction (1-s) of weights. At 90% sparsity: factor = 0.10.

5. **Leakage (1-leak)**: Static leakage power (~25% at 4 nm) does not contribute to useful computation. Factor: 0.75 (Theis and Wong 2017).

6. **Finite-time cost**: The per-bit energy cost exceeds kT ln 2 at finite clock speeds. Using the Proesmans et al. (2020) formula with B_geom = pi^2: factor = kT ln 2 / (kT ln 2 + B_geom * kT / tau) ~ 3.51 x 10^-11 at tau = 0.5 ns. **Caveat**: This theoretical factor overestimates the correction for CMOS by ~664x (see Section 3.3).

The fully corrected bound (6 factors) is:

    dI/dt <= MFU * (1-phi) * (p/32) * (1-s) * (1-leak) * P / W_per_bit

### 3.3 CMOS Energy: Measured vs Theoretical

Horowitz (2014) measured the energy per operation at 45 nm CMOS:

| Operation | Energy (pJ) | Bits | Landauer gap |
|-----------|-------------|------|-------------|
| FP32 MAC | 4.6 | 64 | 2.14 x 10^7 |
| FP32 add | 0.9 | 32 | 8.36 x 10^6 |
| FP16 MAC est. | 0.9 | 32 | 8.36 x 10^6 |
| INT8 MAC | 0.2 | 16 | 3.72 x 10^6 |
| SRAM read (8 KB) | 5.0 | 64 | 2.33 x 10^7 |
| DRAM read (64-bit) | 640 | 64 | 2.98 x 10^9 |

The Landauer gap (measured energy / Landauer minimum) is 10^6-10^9 for current CMOS, consistent with Koomey et al. (2011).

Using the finite-time formula W = kT ln 2 + pi^2 * kT / tau with tau = 1 ns (45 nm clock period) gives W_per_bit ~ 4.77 x 10^-11 J/bit, while the measured W_per_bit for FP32 MAC is 4.6e-12 / 64 ~ 7.19 x 10^-14 J/bit. The theoretical formula overestimates by 664x, confirming that B_geom = pi^2 does not apply to CMOS gates. We present bounds computed both ways and recommend using measured values for physically meaningful claims.

### 3.4 Functional Information Estimation

Functional information -- the number of bits of useful knowledge encoded in a trained model -- is estimated via three independent methods:

1. **MDL compression** (Blier and Ollivier 2018): For networks with N_eff effective parameters at p_eff bits each, MDL ~ N_eff * (p_eff/2) * log_2(D/N_eff). For GPT-4: ~4.25 x 10^9 bits.

2. **PAC-Bayes** (McAllester 1999; Catoni 2007; Lotfi et al. 2022): I(W;S) ~ N_eff * log(N_eff / prior_width). For GPT-4: ~3.0 x 10^9 bits.

3. **Blier-Ollivier sqrt(N) scaling**: Extrapolating from 10^8-parameter models (I ~ 10^5 bits) using sqrt(N) scaling: ~1.34 x 10^7 bits.

These estimates span orders of magnitude. We evaluate five plausible scaling hypotheses (sqrt(N), log(N), N^{1/3}, linear N, constant plateau) and find a 3.6 order-of-magnitude uncertainty range: 4.3 x 10^5 to 1.8 x 10^9 bits. This uncertainty propagates directly to all efficiency calculations.

## 4. Results

All numerical results are recorded in results.tsv and reproducible from source code. We report 63 experiments: E00 (baseline), T01-T18 (tournament), E01-E22 (Phase 2 loop), INT01-INT10+INT-ALL (interactions), and RV01-RV10 (review experiments).

### 4.1 Framework Ranking

At the GPT-4 cluster operating point (17.5 MW, 350 K, B=2048), frameworks rank from tightest to loosest (Table 1, Figure 1). Central values are reported at baseline parameters; uncertainty bands propagate the dominant load-bearing parameters (phi, B_noise, and I_func) through each bound:

| Rank | Framework | Central bound (bits/s) | Plausible range | Notes |
|------|-----------|------------------------|-----------------|-------|
| 1 (tightest) | F1-Full (B_geom=pi^2) | 2.20 x 10^16 | 10^15--10^17 | Theoretical; phi uncertainty |
| 2 | F1' finite-time (B_geom=pi^2) | 1.83 x 10^17 | 10^16--10^18 | Theoretical; phi uncertainty |
| 3 | F1-Measured (Horowitz) | 7.47 x 10^20 | 10^20--10^21 | Most physically meaningful |
| 4 | F3 TUR (GNS-based) | 3.71 x 10^24 | 10^23--10^25 | B_noise extrapolated, ~1 OOM |
| 5 | F2 Crooks SGD | 5.22 x 10^27 | 10^27--10^28 | Heuristic (§2.3) |
| 6 | F1 bare Landauer | 5.22 x 10^27 | -- | Quasistatic baseline |
| 7 (loosest) | F4 Margolus-Levitin | 1.52 x 10^41 | -- | Irrelevant for classical ML |

The actual GPT-4 functional information gain rate is approximately 10^3--10^4 bits/s (10^5--10^9 bits over 90 days, with the 3.6 OOM I_func uncertainty dominating). Even the tightest bound in this table therefore exceeds the actual rate by at least 10^12, and in plausible worst cases by 10^16. The point estimates should be read as central values within the ranges shown, not as three-significant-figure claims.

### 4.2 Correction Factor Hierarchy

For a single H100 GPU (700 W, 350 K), the correction factor hierarchy (Figure 2) shows:

| Correction | Factor | Cumulative Bound (bits/s) |
|------------|--------|--------------------------|
| Bare Landauer | 1.0 | 2.09 x 10^23 |
| + MFU (0.4) | 0.4 | 8.36 x 10^22 |
| + Housekeeping (phi=0.6) | 0.4 | 3.34 x 10^22 |
| + Precision (FP8) | 0.25 | 8.36 x 10^21 |
| + Sparsity (90%) | 0.10 | 8.36 x 10^20 |
| + Leakage (25%) | 0.75 | 6.27 x 10^20 |

Without the finite-time correction (which requires the problematic B_geom assumption), the six engineering corrections together tighten the bare Landauer bound by approximately 333x.

Adding the finite-time correction with B_geom = pi^2 would further tighten by 10^10, but this rests on the idealized double-well model. Using Horowitz measured energy per bit instead gives a total tightening of approximately 10^6 relative to the bare Landauer bound.

### 4.3 Sensitivity Analysis

Varying each correction parameter by +/- 50% around its baseline (RV03):

| Parameter | Low | Baseline | High | Range Ratio |
|-----------|-----|----------|------|-------------|
| P_BITS | 4 | 8 | 16 | 4.0x |
| SPARSITY | 0.5 | 0.9 | 0.99 | 50x |
| PHI | 0.3 | 0.6 | 0.9 | 7.0x |
| MFU | 0.2 | 0.4 | 0.6 | 3.0x |
| TAU | 0.25 ns | 0.5 ns | 0.75 ns | 1.5x |

Sparsity has the widest range (50x) because the bound is proportional to (1-s), which varies from 0.5 to 0.01 across the tested range. Precision (P_BITS) has the next-largest effect.

### 4.4 Reformulated TUR Bound

Using the Gradient Noise Scale B_noise from McCandlish et al. (2018) as the independently measurable variance estimate (RV01):

At GPT-4 parameters (P=17.5 MW, T=350 K, B=2048, B_noise=10^6 — **extrapolated** from McCandlish et al. 2018, who report B_noise ranging 10^4--10^6 across scales smaller than GPT-4; the GPT-4 value is not directly measured and carries approximately one order of magnitude of uncertainty):
- TUR bound = sigma_phys * B / (2 * k_B * B_noise) ≈ 10^23--10^25 bits/s, with central value 3.71 x 10^24 bits/s at B_noise = 10^6
- This is approximately 10^2--10^4 tighter than bare Landauer (5.22 x 10^27), depending on B_noise; the point estimate is 1,409x
- The bound increases linearly with batch size B and decreases with gradient noise scale B_noise

The point estimate "3.71 x 10^24 bits/s / 1,409x tighter" quoted above and elsewhere in this paper should be read as a central value inside a ~1-OOM band, not as a three-significant-figure claim; Tables 1 and 2 in §4.1--§4.2 are reported at the central value for tabulation purposes only.

This bound is less tight than the Landauer-based bounds with engineering corrections but has the advantage of being derived from a single physical principle (the TUR) with no free parameters beyond measurable quantities.

### 4.5 Heuristic range of validity of the Crooks-for-SGD ansatz

This subsection is a caveat-check on the Crooks-derived bound introduced in §2.2, not a novel result. It reports the range of learning rates over which the (1 + T_sgd/T) formula behaves like a thermodynamic bound, rather than a heuristic that happens to produce a plausible number.

Testing the Jarzynski equality for SGD on a 50-dimensional quadratic landscape (RV02):

| Learning rate | T_sgd | Jarzynski <exp(-W/T_sgd)> | Expected | Relative error |
|--------------|-------|--------------------------|----------|----------------|
| 1e-4 | 7.8e-8 | ~1.0 | 1.0 | < 1.0 |
| 1e-3 | 7.8e-6 | varies | 1.0 | moderate |
| 1e-2 | 7.8e-4 | diverges | 1.0 | large |

The Crooks-derived (1 + T_sgd/T) formula is validated for small learning rates but fails for large ones. This confirms it is a heuristic, not a rigorous bound, consistent with the caveat already stated in §2.2 and the limitation in §6.1. Users of the F2 bound in this paper should interpret it as physically motivated within the small-learning-rate regime and should not apply it to large-eta training runs without an independent check.

### 4.6 Temperature Distribution Effect

For 25,000 GPUs with T ~ N(350, 15^2) K (RV05), the Jensen correction factor (mean(1/T) vs 1/mean(T)) is 1.0018, or 0.18%. Using a single representative temperature T=350 K introduces negligible error.

### 4.7 Information-Energy Tradeoff

Thermodynamic efficiency (I_func * kT ln 2 / E_train) consistently degrades with model scale (RV07):

| Model | N_params | E_train (J) | I_func (bits) | Efficiency |
|-------|----------|-------------|---------------|------------|
| XGBoost | 10^6 | 4.2 x 10^4 | 10^4 | 8.0 x 10^-22 |
| BERT-base | 1.1 x 10^8 | 10^6 | 1.1 x 10^5 | 3.5 x 10^-22 |
| GPT-2 | 1.5 x 10^9 | 10^8 | 3.9 x 10^5 | 1.3 x 10^-23 |
| GPT-3 | 1.8 x 10^11 | 4.6 x 10^12 | 4.2 x 10^6 | 3.0 x 10^-27 |
| GPT-4 est. | 1.8 x 10^12 | 1.36 x 10^14 | 1.3 x 10^7 | 3.3 x 10^-28 |

Efficiency drops by 6 orders of magnitude from XGBoost to GPT-4, reflecting the diminishing returns of scaling laws: functional information scales as sqrt(N) while training energy scales superlinearly in N.

### 4.8 Cross-substrate comparison (illustrative)

This subsection is included for illustrative cross-substrate context and is not a headline result of the paper. As §6.2 makes explicit, no directional claim about the relative efficiency of biology and ML is supported here without specifying a metric; the numbers in the table below are useful only as a shared framework for future comparison, not as a ranking.

Applying the same Landauer-efficiency expression (efficiency = I_func * kT ln 2 / E) across substrates (Figure 3, RV08):

| System | Efficiency | Description |
|--------|-----------|-------------|
| Ribosome proofreading | 11.5% | Most efficient known (sibling project) |
| E. coli chemotaxis | ~1% | Per-decision efficiency |
| Human brain (sensory) | ~10^-13 | Using sensory processing rate |
| XGBoost | ~10^-22 | Small ML model |
| Human brain (long-term) | ~10^-21 | Using memory formation rate |
| GPT-4 | ~10^-28 | Largest ML model |

The brain comparison depends critically on the chosen metric: using long-term memory formation rate (~10 bits/s, Miller 1956) the brain and a GPU have comparable efficiency (~10^-21); using sensory processing rate (~10^9 bits/s) the brain appears ~10^8 more efficient. These quantities are not directly comparable. Readers interested in a directional comparison should treat the table as raising the question, not answering it.

## 5. Discussion

### 5.1 What the Gap Means

Current ML training operates 10^7 to 10^28 above the Landauer limit, depending on which bound and which functional information estimate is used. This gap has three components:

1. **CMOS hardware gap** (~10^6-10^9): The energy per gate transition in current CMOS exceeds kT ln 2 by 10^6-10^9 (Horowitz 2014; Koomey et al. 2011). This is a property of the hardware, not the algorithm.

2. **Algorithmic overhead** (~10^3-10^6): MFU < 1, data movement, communication overhead, and leakage together waste approximately 10^3 of the hardware's dissipation relative to an ideal algorithm on ideal hardware.

3. **Information gap** (~10^10-10^16): The ratio of total FLOPS to functional information bits gained. Most computation during training produces intermediate results that are immediately overwritten. The gradient update per step encodes far less information than the FLOPS used to compute it.

### 5.2 Comparison with Sibling Biology Project

Our sibling project applying the same thermodynamic framework to biological information processing found that:
- Cellular translation operates within one order of magnitude of the Landauer bound per bit (Kempes et al. 2017)
- Kinetic proofreading achieves 11.5% thermodynamic efficiency
- Most biological energy expenditure is housekeeping (maintaining homeostasis), analogous to data movement in GPUs

Analogously, both biological and artificial information processing systems devote the majority of their energy budget to "housekeeping" rather than to information acquisition proper. In both cases, the thermodynamic efficiency of the information-gaining process itself is low, with housekeeping overhead dominating the totals. We note this parallel as a shared structural feature of the two substrates, not as evidence of a common underlying mechanism; the detailed housekeeping processes (ion pumping in cells, data movement in GPUs) are unrelated.

### 5.3 Implications for ML Hardware Design

The sensitivity analysis (Section 4.3) identifies sparsity and precision as the most impactful correction factors for future hardware design. Achieving 99% sparsity with 4-bit precision would tighten the bound by an additional 200x relative to current practice (FP8 at 90% sparsity). Combined with neuromorphic or near-threshold designs (Dreslinski et al. 2010) that close the CMOS-Landauer gap from 10^9 to 10^6, the total improvement potential is approximately 10^5.

Reversible computing (Bennett 1973; Fredkin and Toffoli 1982; Frank 2005) offers a complementary path. Linear operations (matmuls, additions) in neural networks are logically reversible and in principle dissipate no Landauer cost. Only nonlinear activations (GELU, softmax, layernorm) require irreversible erasure. The nonlinear fraction is approximately 2 x 10^-4 of total FLOPS (accounting for softmax and layernorm), giving a theoretical savings of ~5,000x for fully reversible architectures.

**A concrete falsifiable prediction.** The multi-factor framework predicts that a 4-bit-precision, 99%-sparsity training run on H100-class hardware at 350 K junction temperature should achieve a functional-information gain rate within a factor of roughly 200 of the FP8-90%-sparsity baseline studied in §4.2, with the ratio determined by the product of the precision and sparsity correction factors (p_bits/32 × (1-s)) evaluated at the two operating points. A measured ratio outside the range 100--400 under otherwise matched conditions would falsify either the multiplicative-factor assumption or one of the underlying correction models (most plausibly the precision-to-bits-erased identification), and would indicate that the correction factors interact non-trivially rather than stacking independently. This is a concrete, cheaply testable prediction; we offer it as a falsifiable anchor rather than a claimed result.

### 5.4 Projections

At the historical Koomey's law rate (doubling computations per joule every 1.57 years pre-2005, or 2.6 years post-2005), CMOS will approach the Landauer limit in approximately 2048-2100 (Koomey et al. 2011). However, this projection assumes continued exponential improvement, which requires either new device physics (tunneling FETs, spintronic devices, superconducting logic) or a transition to reversible computing.

## 6. Limitations

### 6.1 Crooks SGD Formula Is Heuristic

The (1 + T_sgd/T) formula in the Crooks bound treats SGD noise as a second thermal bath, but SGD is not microscopically reversible in the standard thermodynamic sense. Our Jarzynski validation (RV02) confirms this holds approximately for small learning rates but breaks for large ones. The Crooks bounds in this paper should be interpreted as physically motivated estimates, not rigorous thermodynamic inequalities.

### 6.2 Brain vs GPU Comparison Is Metric-Dependent

The relative efficiency of brain vs GPU depends entirely on what "information processing rate" means for the brain. Long-term memory formation (~10 bits/s) and sensory processing (~10^9 bits/s) differ by 8 orders of magnitude, and neither is directly comparable to the functional information gain rate of an ML model. We present both metrics but do not claim a directional comparison.

### 6.3 Functional Information Uncertainty

The functional information of GPT-4 is estimated to be between 4.3 x 10^5 and 1.8 x 10^9 bits depending on the assumed scaling law. This 3.6 OoM uncertainty propagates directly to all efficiency calculations. Empirical validation -- for example, by compressing a trained GPT-2 model and comparing to the sqrt(N) extrapolation -- is urgently needed.

### 6.4 B_geom = pi^2 Does Not Apply to CMOS

The finite-time Landauer formula with B_geom = pi^2 applies to an overdamped colloidal particle in a double-well potential (Proesmans et al. 2020), not to CMOS transistor switching. The theoretical per-bit cost with B_geom = pi^2 overestimates measured CMOS gate energy by approximately 664x. We present results both with and without this correction, and recommend using Horowitz measured energy data for physically meaningful claims about CMOS.

### 6.5 No Empirical Measurement

All energy values in this paper come from published specifications, not direct measurement. GPU power should ideally be measured with real-time monitoring (e.g., nvidia-smi) during actual training runs. All functional information estimates are theoretical extrapolations. The project is an analytical survey, not an empirical study.

### 6.6 Scope Limitations

This paper addresses only training energy, not inference (which Desislavov et al. 2023 show accounts for up to 90% of deployed system energy). Post-training alignment (RLHF), fine-tuning, and retrieval-augmented generation are not treated. All bounds are steady-state; the non-stationarity of actual training (learning rate schedules, warmup, loss plateaus) is not captured.

## 7. Conclusion

We have established a hierarchy of thermodynamic bounds on ML training information gain rate, ranging from the vacuously loose Margolus-Levitin quantum speed limit (10^41 bits/s) to the corrected Landauer bound with measured CMOS energy data (~10^20 bits/s). Even the tightest meaningful bound exceeds the estimated actual functional information gain rate by at least 10^7, confirming that ML training is nowhere near fundamental thermodynamic limits.

The dominant factors in the gap are: (1) the CMOS hardware gap of 10^6-10^9 above Landauer per operation, (2) algorithmic overhead of 10^3 from underutilization and data movement, and (3) the information gap of 10^10+ between total computation and functional information gain.

These findings suggest that at least 10^5 of improvement is achievable through hardware advances (approaching Landauer), algorithmic improvements (reducing overhead), and architectural innovation (reversible computing, extreme sparsity). The thermodynamic limits themselves are not the binding constraint on ML training; economics and engineering are.

**Why a thermodynamics paper for a non-binding limit.** This work is framed as a stochastic-thermodynamics paper despite the bounds being 10^7 or more above today's operating point because the framework will become binding at the ~10^5--10^6 efficiency improvement horizon projected by the Koomey-law extrapolation (c. 2048--2100), at the onset of near-threshold CMOS and sub-kT operation (Dreslinski et al. 2010), and immediately at the onset of reversible, photonic, or neuromorphic computing --- all of which are already in active research. The contribution of this paper is therefore not a constraint on today's training budgets but a calibrated reference tool: a framework that can be dropped onto any future compute substrate and used to compute the gap between measured and Landauer-limited information gain rate. We include the cross-substrate comparison with biology (§4.8) in that spirit --- as a demonstration of the framework's portability across regimes where thermodynamic limits do become relevant --- not as a claim that current ML training is thermodynamically constrained.

## References

Amodei, D. and Hernandez, D. (2018). AI and Compute. OpenAI Blog.

Bahri, Y. et al. (2020). Statistical Mechanics of Deep Learning. Annual Review of Condensed Matter Physics 11: 501-528.

Bahri, Y. et al. (2021). Explaining Neural Scaling Laws. arXiv preprint.

Barato, A.C. and Seifert, U. (2015). Thermodynamic Uncertainty Relation for Biomolecular Processes. Physical Review Letters 114: 158101.

Bekenstein, J.D. (1981). Universal Upper Bound on the Entropy-to-Energy Ratio for Bounded Systems. Physical Review D 23: 287-298.

Bennett, C.H. (1973). Logical Reversibility of Computation. IBM Journal of Research and Development 17: 525-532.

Bennett, C.H. (1982). The Thermodynamics of Computation: A Review. International Journal of Theoretical Physics 21: 905-940.

Berut, A. et al. (2012). Experimental Verification of Landauer's Principle. Nature 483: 187-189.

Besiroglu, T. et al. (2024). Chinchilla Scaling: A Replication Attempt. arXiv preprint.

Biamonte, J. et al. (2017). Quantum Machine Learning. Nature 549: 195-202.

Blier, L. and Ollivier, Y. (2018). The Description Length of Deep Learning Models. NeurIPS.

Boyd, A.B. et al. (2022). Thermodynamic Machine Learning. Physical Review Letters.

Brown, T. et al. (2020). Language Models Are Few-Shot Learners. NeurIPS.

Caballero, E. et al. (2023). Broken Neural Scaling Laws. ICLR.

Catoni, O. (2007). PAC-Bayesian Supervised Classification. IMS Lecture Notes.

Choromanska, A. et al. (2015). The Loss Surfaces of Multilayer Networks. AISTATS.

Chowdhery, A. et al. (2023). PaLM: Scaling Language Modeling with Pathways. JMLR.

Coles, P.J. et al. (2023). Thermodynamic AI and the Fluctuation Frontier. arXiv preprint.

Conte, T. et al. (2019). Thermodynamic Computing. arXiv preprint.

Cottier, B. et al. (2024). The Rising Costs of Training Frontier AI Models. arXiv preprint.

Crooks, G.E. (1999). Entropy Production Fluctuation Theorem. Physical Review E 60: 2721.

Dao, T. et al. (2022). FlashAttention: Fast and Memory-Efficient Exact Attention. NeurIPS.

Davies, M. et al. (2018). Loihi: A Neuromorphic Manycore Processor. IEEE Micro 38: 82-99.

Dennard, R.H. et al. (1974). Design of Ion-Implanted MOSFETs. IEEE JSSC 9: 256-268.

Desislavov, R. et al. (2023). Trends in AI Inference Energy Consumption. Joule.

Dreslinski, R. et al. (2010). Near-Threshold Computing. Proceedings of the IEEE 98: 253-266.

Feng, Y. and Tu, Y. (2021). The Inverse Variance-Flatness Relation in SGD. ICML.

Frank, M.P. (2005). Approaching the Physical Limits of Computing. ISMVL.

Frankle, J. and Carlin, M. (2019). The Lottery Ticket Hypothesis. ICLR.

Fredkin, E. and Toffoli, T. (1982). Conservative Logic. International Journal of Theoretical Physics 21: 219-253.

Garipov, T. et al. (2018). Loss Surfaces, Mode Connectivity, and Fast Ensembling. NeurIPS.

Goldt, S. and Seifert, U. (2017). Stochastic Thermodynamics of Learning. Physical Review Letters 118: 010601.

Grunwald, P.D. (2007). The Minimum Description Length Principle. MIT Press.

Hamerly, R. et al. (2019). Large-Scale Optical Neural Networks. Physical Review X 9: 021032.

Han, S. et al. (2016). Deep Compression. ICLR.

Hardt, M. et al. (2016). Train Faster, Generalize Better. ICML.

Henighan, T. et al. (2020). Scaling Laws for Autoregressive Generative Modeling. arXiv preprint.

Hestness, J. et al. (2017). Deep Learning Scaling Is Predictable, Empirically. arXiv preprint.

Hinton, G. et al. (2015). Distilling the Knowledge in a Neural Network. arXiv preprint.

Ho, J. et al. (2020). Denoising Diffusion Probabilistic Models. NeurIPS.

Hochreiter, S. and Schmidhuber, J. (1997). Flat Minima. Neural Computation 9: 1-42.

Hoffmann, J. et al. (2022). Training Compute-Optimal Large Language Models. NeurIPS.

Horowitz, M. (2014). Computing's Energy Problem. ISSCC.

Ivanov, A. et al. (2021). Data Movement Is All You Need. arXiv preprint.

Jarzynski, C. (1997). Nonequilibrium Equality for Free Energy Differences. Physical Review Letters 78: 2690.

Jouppi, N.P. et al. (2017). In-Datacenter Performance Analysis of a Tensor Processing Unit. ISCA.

Kaplan, J. et al. (2020). Scaling Laws for Neural Language Models. arXiv preprint.

Kempes, C.P. et al. (2017). Drivers of Bacterial Maintenance and Minimal Energy Requirements. Frontiers in Microbiology.

Keskar, N.S. et al. (2017). On Large-Batch Training for Deep Learning. ICLR.

Koomey, J.G. et al. (2011). Implications of Historical Trends in the Electrical Efficiency of Computing. IEEE Annals of the History of Computing 33: 46-54.

Lan, G. et al. (2012). The Energy-Speed-Accuracy Tradeoff in Sensory Adaptation. Nature Physics 8: 422-428.

Landauer, R. (1961). Irreversibility and Heat Generation in the Computing Process. IBM Journal of Research and Development 5: 183-191.

Li, C. et al. (2017). Stochastic Modified Equations for Continuous Limit of SGD. arXiv preprint.

Lloyd, S. (2000). Ultimate Physical Limits to Computation. Nature 406: 1047-1054.

Lotfi, S. et al. (2022). PAC-Bayes Compression Bounds So Tight That They Can Explain Generalization. NeurIPS.

Luccioni, A.S. et al. (2023). Estimating the Carbon Footprint of BLOOM. JMLR.

Mandt, S. et al. (2017). Stochastic Gradient Descent as Approximate Bayesian Inference. JMLR 18: 1-35.

Margolus, N. and Levitin, L.B. (1998). The Maximum Speed of Dynamical Evolution. Physica D 120: 188-195.

McAllester, D.A. (1999). Some PAC-Bayesian Theorems. Machine Learning 37: 355-363.

McCandlish, S. et al. (2018). An Empirical Model of Large-Batch Training. arXiv preprint.

Merolla, P.A. et al. (2014). A Million Spiking-Neuron Integrated Circuit. Science 345: 668-673.

Miller, G.A. (1956). The Magical Number Seven, Plus or Minus Two. Psychological Review 63: 81-97.

NVIDIA (2022). NVIDIA H100 Tensor Core GPU Architecture. Technical Report.

Patterson, D. et al. (2021). Carbon Emissions and Large Neural Network Training. arXiv preprint.

Peng, X. et al. (2024). Stochastic Thermodynamics of ML Training. arXiv preprint.

Proesmans, K., Ehrich, J., and Bechhoefer, J. (2020). Finite-Time Landauer Principle. Physical Review Letters 125: 100602.

Schaeffer, R. et al. (2023). Are Emergent Abilities of Large Language Models a Mirage? NeurIPS.

Sebastian, A. et al. (2020). Memory Devices and Applications for In-Memory Computing. Nature Nanotechnology 15: 529-544.

Sevilla, J. et al. (2022). Compute Trends Across Three Eras of Machine Learning. arXiv preprint.

Sharma, U. and Kaplan, J. (2022). Scaling Laws from the Data Manifold Dimension. JMLR.

Shwartz-Ziv, R. and Tishby, N. (2017). Opening the Black Box of Deep Neural Networks via Information. arXiv preprint.

Sohl-Dickstein, J. et al. (2015). Deep Unsupervised Learning Using Nonequilibrium Thermodynamics. ICML.

Steinke, T. and Zakynthinou, L. (2020). Reasoning About Generalization via Conditional Mutual Information. COLT.

Still, S. et al. (2012). Thermodynamics of Prediction. Physical Review Letters 109: 120604.

Stillmaker, A. and Baas, B. (2017). Scaling Equations for the Accurate Prediction of CMOS Device Performance. Integration 58: 74-81.

Theis, T.N. and Wong, H.-S.P. (2017). The End of Moore's Law: A New Beginning for Information Technology. Computing in Science & Engineering 19: 41-50.

Tishby, N. et al. (1999). The Information Bottleneck Method. Allerton Conference.

Wei, J. et al. (2022). Emergent Abilities of Large Language Models. arXiv preprint.

Williams, S. et al. (2009). Roofline: An Insightful Visual Performance Model. Communications of the ACM 52: 65-76.

Wolpert, D.H. (2019). The Stochastic Thermodynamics of Computation. Journal of Physics A 52: 193001.

Xu, A. and Raginsky, M. (2017). Information-Theoretic Analysis of Generalization Capability. NeurIPS.

Yang, T.-J. et al. (2017). Designing Energy-Efficient Convolutional Neural Networks. CVPR.
