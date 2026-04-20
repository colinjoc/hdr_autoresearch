**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics

# Empirical test of the Gradient-Noise-Scale TUR bound on SGD via Jarzynski work-distribution measurement

## 1. Question

Does the Gradient-Noise-Scale–substituted thermodynamic-uncertainty-relation bound proposed in the predecessor paper `thermodynamic_ml_limits/paper.md` actually hold when the Crooks / Jarzynski fluctuation relation is measured directly on a controlled Langevin-SGD training run — or is the (1 + T_SGD/T) heuristic factor that underpins the bound systematically violated at realistic learning rates?

## 2. Proposed contribution

**(a) Controlled Langevin-SGD testbed.** Train an overparameterised perceptron on a synthetic quadratic loss landscape with known-analytical entropy production (Goldt & Seifert 2017 closed-form). Measure forward and time-reversed trajectory work distributions directly; compute ⟨exp(−βW)⟩ and test the Jarzynski equality across a grid of learning rates η.

**(b) Extraction of the effective T_SGD via gradient-noise-scale.** Compute B_noise = Tr(Σ_grad)/‖g‖² from the same run using the McCandlish et al. 2018 infrastructure. Extract an empirical effective temperature T_SGD_empirical via the measured Jarzynski work histogram, and compare to the heuristic T_SGD_heuristic = η σ_g² / (2B) from Mandt et al. 2017.

**(c) Validity regime.** Report the range of η over which the Jarzynski equality holds within experimental uncertainty. This defines the regime of validity of the GNS-TUR bound used in `thermodynamic_ml_limits/paper.md`.

**(d) Small-scale transfer.** Apply the same measurement to a 10-parameter tanh network on MNIST and compare the extracted validity regime.

## 3. Why now

Yaida 2018 derived fluctuation-dissipation relations for SGD but only for the stationary-distribution case; the Jarzynski-equality test at arbitrary learning rate has not been published for SGD. Goldt & Seifert 2017 provides the closed-form reference point for the perceptron. The Phase 0.25 publishability review of `thermodynamic_ml_limits` (April 2026) flagged the GNS-TUR substitution's empirical validity as the single load-bearing unknown; closing this gap is the highest-priority follow-on.

## 4. Falsifiability

Three binary kill-outcomes:

- **Jarzynski test on the perceptron.** The ratio ⟨exp(−βW)⟩ / exp(−βΔF) is either unity within Monte-Carlo error for at least one η value, or it is not. If the Jarzynski equality fails for the entire tested η range, SGD is not microscopically reversible in any practically usable regime — a significant negative result.
- **T_SGD consistency.** The empirical T_SGD from the Jarzynski histogram either agrees with the Mandt et al. 2017 heuristic T_SGD = η σ_g² / (2B) to within 30 %, or it does not.
- **MNIST transfer.** The validity regime on the 10-parameter MNIST network is either within a factor of 3 of the perceptron regime, or it is not (testing substrate-independence of the regime).

## 5. Named comparators and differentiation

- Yaida (2018), "Fluctuation-dissipation relations for stochastic gradient descent", ICLR workshop.
- Goldt & Seifert (2017), PRL on stochastic thermodynamics of perceptron learning.
- Mandt, Hoffman & Blei (2017) — SGD-as-approximate-Bayesian-inference, introducing T_SGD.
- McCandlish, Kaplan, Amodei (2018) — Gradient Noise Scale.
- Peng, Sun, Duraisamy (2024), *Entropy* — stochastic thermodynamics of learning parametric probabilistic models.

No prior work combines (i) direct Jarzynski measurement on SGD, (ii) GNS-based extraction of T_SGD, and (iii) the η-range at which the two agree.

## 6. Target venue

**PRE** — publishes empirical stochastic-thermodynamics validations with controlled testbeds. **Fallback: J. Stat. Mech.** if the Jarzynski test fails globally and the paper becomes a null result.
