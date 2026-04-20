**Target**: publication — primary venue: Physical Review E, fallback venue: Journal of Statistical Mechanics

# An operational definition of the housekeeping fraction for stochastic gradient descent

## 1. Question

Is there a measurement protocol — derivable from stochastic thermodynamics rather than chosen by convention — that gives the housekeeping fraction φ a single, substrate-independent meaning in both biomolecular copying systems (ribosome, RNA polymerase) and large-scale machine-learning training (stochastic gradient descent at GPT-4 scale)?

## 2. Proposed contribution

The scope-check reviewer correctly identified that the housekeeping fraction φ is the load-bearing free parameter in both prior thermodynamic-speed-limit papers (thermodynamic_info_limits and thermodynamic_ml_limits) and that a directional cross-substrate comparison is impossible so long as φ is chosen by convention rather than measured. We propose to close that gap by:

**(a) A theorem.** Extending Harada–Sasa (2005), which defines σ_excess as the fluctuation–dissipation-theorem violation in continuous-time overdamped Langevin systems, to discrete-time stochastic gradient descent. We will show that in the continuous-time limit η → 0 the extension reduces to standard Harada–Sasa, and that at finite η it yields a φ that depends only on the measured gradient-noise power spectrum and the response of loss to a small applied perturbation of the optimiser. No free parameter remains.

**(b) A calibration.** Applying the extended protocol to a controlled testbed (an overparameterised perceptron, where φ can also be computed analytically from the Goldt–Seifert 2017 stochastic-thermodynamics solution) and verifying that the two numbers agree within a specified tolerance.

**(c) Two substrate measurements.** Re-extracting φ from the Kempes et al. 2017 ribosome dissipation data under the new protocol (a calibration check — must recover their published number within stated uncertainty) and computing φ for a published McCandlish et al. 2018 training run using the new protocol. This gives, for the first time, two φ values measured under a shared operational definition. Whether the two numbers are numerically close is itself a falsifiable empirical claim, not a theoretical one.

A null result — the protocol does not recover Harada–Sasa in the limit, or the two substrate values are inconsistent under any reasonable interpretation — will be reported honestly.

## 3. Why now

Three specific developments in the last 24 months make this tractable. McCandlish et al. (2018) + Shallue et al. (2019) published enough gradient-variance data at multiple training scales to support a direct φ extraction. Peng, Sun, Duraisamy (2024) gave a rigorous ELBO-based thermodynamic formulation of learning that can be used to cross-check the Harada–Sasa extension analytically. Horowitz & Gingrich (2020, Nat. Phys. review) reorganised the TUR literature in a form that makes the Harada–Sasa / TUR / Landauer relationships explicit. Without these three pieces the theorem could not be stated operationally.

## 4. Falsifiability

Three concrete kill-outcomes:

- **Continuous-time limit fails.** If the extended protocol does not recover standard Harada–Sasa as η → 0 in the perceptron testbed, the theorem is wrong. This is a symbolic check, computable to any precision.
- **Analytical disagreement on the perceptron.** If the measured φ disagrees with the Goldt–Seifert analytical φ on the perceptron by more than the stated uncertainty, the extension is misderived.
- **Ribosome calibration fails.** If the re-extracted ribosome φ differs from the Kempes 2017 published value by more than 0.5 after accounting for stated measurement uncertainty, either our protocol or their analysis is wrong; either finding is publishable.

None of these is a ratio with a four-decade tolerance. All three are binary outcomes with clean error bars.

## 5. Target venue

**Physical Review E** — publishes rigorous extensions of stochastic-thermodynamics measurement protocols with empirical validation; exactly the class of paper this proposal describes. Expected objection: PRE will ask for the continuous-time-limit proof to be rigorous (not just heuristic interpolation), and will demand that the perceptron calibration include analytical and numerical results agreeing to specified precision. Both are tractable.

Fallback **Journal of Statistical Mechanics**, which has historically published Harada–Sasa extensions and is more tolerant of the synthesis framing this would share with the two predecessor papers.

## 6. Relation to the two predecessor papers

If this project succeeds, the merged thermodynamic paper is defensible: the info_limits and ml_limits results become two substrate-specific applications of a shared φ measurement protocol, and the cross-substrate comparison becomes sharp (not 4-decade hand-waving). If this project fails, the two predecessor papers remain separately submittable under their existing REFRAME framings and no forced merge is attempted. Either way, Phase 0.25 of THIS project will verify the protocol's novelty before any experiments are run.
