# Phase −0.5 Scope Check — Yaida/GNS/TUR/Jarzynski proposal

Fresh grouchy-reviewer pass. Read only `proposal.md` and the Phase −0.5 section of `program.md`. No access to prior reviews.

## 1. Is the contribution new?

Narrowly yes, broadly questionable. The literal combination "measure Jarzynski equality directly on SGD work distributions, extract T_SGD, cross-check against the McCandlish Gradient Noise Scale formula" does not appear verbatim in the named comparators. But each ingredient is well-trodden:

- **Goldt & Seifert (2017)** already does closed-form stochastic thermodynamics on the perceptron including entropy production — you are claiming to *validate* their machinery, not extend it. That reduces the novelty to an applied engineering check.
- **Yaida (2018)** gives stationary-FDR tests on SGD. Jarzynski is a non-stationary generalisation of the same idea. The gap is real but narrower than advertised.
- **Kunin, Sagastuy-Breña, Gillespie et al. (2021) "Rethinking SGD as a Langevin process"** and follow-ups (Chaudhari/Soatto 2018 "Stochastic gradient descent performs variational inference") have already probed the validity regime of the Langevin approximation at finite η. If any of these computed a work-like quantity — and at least Chaudhari/Soatto come close — the novelty shrinks to "first to do it with GNS-derived T".
- A **PRE 2022–2024** search would likely surface at least one stochastic-thermodynamics-of-learning paper with a similar flavour (Peng–Sun–Duraisamy already named). You have not cited any 2023+ work. That is a red flag; the proposal cannot differentiate against papers it has not searched for.

Three close comparators: Yaida 2018, Goldt & Seifert 2017, Chaudhari & Soatto 2018.

## 2. Are the three kill-outcomes falsifiable?

Mixed.

- **Jarzynski on perceptron:** genuinely falsifiable — ⟨exp(−βW)⟩ vs exp(−βΔF) is a measurable ratio with Monte-Carlo error bars. Good.
- **T_SGD consistency within 30 %:** falsifiable but the 30 % threshold is arbitrary and conveniently loose. Why 30 and not 10? A reviewer will ask whether you picked the tolerance after seeing the data. Pre-register the threshold or derive it from theory.
- **MNIST transfer "within factor of 3":** weakest. "Validity regime" is not defined as a measured quantity. What is the quantitative definition — η at which |⟨e^{−βW}⟩ − e^{−βΔF}| / σ crosses 1? State it before the run. As written this is borderline tautological because you control the knob that defines the regime.

Two-and-a-half out of three. Tighten outcomes 2 and 3.

## 3. Is PRE the right target?

PRE is plausible for a *controlled* stochastic-thermodynamics validation, yes. But PRE is not in love with "we validated the heuristic in a prior ML paper" — it wants a physics claim. The current framing reads as debugging your own predecessor paper's assumption, which is an *internal* use case. Reframe the headline as "Jarzynski equality holds/fails for Langevin-approximated SGD with quantitative η-bound" and it fits. Fallback to JSTAT is fine. PRL is wisely not attempted.

## 4. Likely killer objections

- **"Langevin-SGD is not SGD."** The Langevin approximation breaks down exactly where the interesting ML regime lives (large η, non-Gaussian gradient noise). A reviewer will demand evidence that Σ_grad is Gaussian *at the tested η*. If it is not, the whole Jarzynski framing is inapplicable regardless of the measurement.
- **"Synthetic perceptron + 10-param MNIST is not a demonstration."** Reviewers will ask why you did not test at n=10^4 parameters where GNS actually matters. Hard rule on this: *the result must generalise to the regime the original bound was claimed in*, or the paper validates a heuristic in a toy regime where nobody doubted it.
- **"What is ΔF for SGD?"** Free energy for a non-equilibrium optimiser is not a given. Defining ΔF so that Jarzynski "holds" can be circular. Reviewer will want an a-priori, loss-function-derived ΔF.
- **Real-data rule (user global CLAUDE.md):** synthetic quadratic landscape is acceptable here only because stochastic thermodynamics *requires* a known analytical reference. Document this explicitly or the Phase 0.25 reviewer flags it as synthetic-by-default.

## Verdict

The question is real, narrowly novel, and PRE-appropriate *if* (a) the Langevin-validity check is made a first-class measurement, not an assumption; (b) the "validity regime" and 30 % threshold are pre-registered with quantitative definitions; (c) the lit review (Phase 0) actively searches 2022–2026 stochastic-thermodynamics-of-SGD papers to defend the novelty claim; (d) a larger network is added to the test battery, or the paper's scope is honestly restricted to "perceptron-scale validation".

VERDICT: REFRAME
