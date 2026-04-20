**Target**: publication — primary venue: Physical Review X, fallback venue: Nature Communications (physics section)

# A thermodynamic minimum training time for any information-processing substrate

## 1. Question

Is there a single, hardware-agnostic thermodynamic lower bound on the time any physical system needs to accumulate a given amount of functional information — and, if so, how close to saturation do real systems (biological evolution, ribosomal proofreading, ML training) sit on that bound?

## 2. Proposed contribution

We propose to derive a minimum-training-time bound of the form

    τ_min ≥ I_func · k_B T ln 2 / (φ · P)

where I_func is the functional information to be gained, T the operating temperature, P the available dissipative power, and φ the fraction of that power allocated to information processing (as opposed to housekeeping). The bound combines the Landauer floor with the housekeeping decomposition from stochastic thermodynamics (Esposito–Van den Broeck 2010; Dechant–Sasa 2018). We will then evaluate the saturation ratio S = τ_observed / τ_min across a matched set of biological and artificial information-processing systems — ribosomal translation, CRISPR spacer acquisition, E. coli evolution, and GPT-4-class training — using published data for I_func, T, P, and φ. The paper will claim either (a) S is approximately preserved across substrates, revealing a universal "thermodynamic headroom" constant; or (b) S is systematically different between substrates, and we will identify which single parameter (φ, I_func measurement convention, or T) is responsible. A null result — no clean pattern — will also be reported honestly.

## 3. Why now

Two recent papers (Wong et al., *PNAS* 2023 on a proposed law of increasing functional information; McCandlish et al. 2018 on the Gradient Noise Scale) have, for the first time, put the input quantities on both sides of such a comparison on a common footing. The growing body of published φ-like measurements for cellular metabolism (Kempes et al. 2017) and GPU kernel accounting (Horowitz 2014; Patterson et al. 2021) make the calculation numerically tractable. No directional cross-substrate saturation comparison has been published, and the field is actively debating whether any substrate-independent thermodynamic law of learning exists (Peng, Sun, Duraisamy 2024; Boyd, Crutchfield, Gu 2022).

## 4. Falsifiability

A direct kill-outcome: if the saturation ratios S_bio and S_ML differ by more than four orders of magnitude across any two systems compared on matched φ and I_func conventions, the claim of a universal saturation floor is falsified and the paper reports this as its central result. A secondary kill-outcome: if the bound τ_min is violated by a single measured system (any system achieving τ_observed < τ_min under honest parameter values), the derivation itself is falsified. Both outcomes are concrete, measurable, and inside the data available at proposal time.

## 5. Target venue

**Physical Review X** — publishes cross-disciplinary physics results with sharp, falsifiable directional claims spanning biology and computation, and is the natural venue for a successful cross-substrate saturation comparison. Fallback **Nature Communications (Physics)** for a stronger-biology framing.
