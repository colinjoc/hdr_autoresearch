# Paper Review: Housing Policy Lever Interactions (Phase 2.75 / 3.5 Combined)

**Reviewer role:** Blind adversarial reviewer. Inputs: `paper.md`, `results.tsv`, `feedback_model.py`, `plots/`.

---

## 1. Claims vs Evidence

### F1 — CRITICAL: 50% workforce expansion treated as feasible without evidence

The paper claims "52,500 achievable with +50% workforce + 4.9% cost reduction." Ireland's construction workforce is approximately 160,000 (CIF, 2022; SOLAS, 2022). A 50% expansion requires ~80,000 additional workers within 3–5 years. Ireland has never achieved immigration at this scale in any sector. The paper's own SOLAS citation projects workforce growth of ~5,000/year, which would require 16 years to reach the +50% target. The paper labels this as a model input without discussing the probability that it can actually be delivered, creating a critical gap between the model's assumptions and policy reality.

**Mandated experiment RV01:** Add a workforce ramp-rate sensitivity analysis. Model 3 scenarios: (a) +5,000 workers/year (SOLAS projection), (b) +10,000/year (optimistic), (c) +20,000/year (unprecedented). Report completions trajectory over 10 years for each scenario with the "everything" package. Report in paper §5 or §6.

### F2 — MAJOR: Diminishing returns to workforce expansion not modeled

The hard ceiling treats workforce as a linear multiplier on capacity (35,000 × 1.5 = 52,500). In reality, marginal workers have lower productivity due to: training time (1–3 years for skilled trades), supervision bottlenecks, site congestion, and supply-chain constraints (materials, equipment, land with planning permission). The 80,001st worker is not as productive as the 1st.

**Mandated experiment RV02:** Implement a diminishing-returns workforce model analogous to the soft cost ceiling. For example: effective_capacity = 35000 + additional_workers × productivity_decay(additional_workers). Test the "everything" package under this model. Report in paper.

### F3 — MAJOR: r = 0.91 viability-application elasticity used linearly beyond observed range

The r = 0.91 correlation is observed at current margins (-3.1% to -11%). The model extrapolates this to viability margins of +67% (the "everything" package), far beyond any observed data. At positive margins, application rates would saturate: there is a finite number of developable sites, a finite number of developers, and a finite planning-authority throughput. The linear extrapolation produces 258,144 gross completions — 7.4× current output — from a correlation observed at negative margins.

The paper's §6.3 acknowledges this limitation (#1 and #6) but does not quantify the impact. The Monte Carlo varies r by ±0.05, which tests precision, not the structural question of whether the relationship is linear at all.

**Mandated experiment RV03:** Run the full model with a saturating elasticity: app_multiplier = 1 + r × tanh(viability_delta / scale_factor × k) for k ∈ {0.5, 1.0, 2.0}. Report soft-ceiling completions for the "everything" and "feasible" packages under each k. This tests whether the headline numbers survive a nonlinear demand response.

### F4 — MAJOR: General-equilibrium price compression mentioned but not modeled

§5.7 notes that a 44% supply increase would reduce prices ~22% and compress margins ~11pp. This feedback is not incorporated into any reported number. The soft-ceiling "everything" estimate of 167,810 is presented as the central result, with a caveat that GE effects would "compress this substantially." This is a major gap because the GE effect directly contradicts the model's fixed-price assumption at the supply levels being claimed.

**Mandated experiment RV04:** Implement a single-step GE correction: for each supply level, compute the implied price reduction (using the stated -0.5 demand elasticity), subtract the margin compression from the cost reduction, and re-run the feedback loop. Report corrected soft-ceiling completions for each policy package. This is a first-order correction, not a full GE model, but it bounds the effect.

### F5 — MAJOR: Modular × Land CPO redundancy (-14,588) may be a ceiling artifact

The paper reports the largest redundant interaction as modular × land CPO at -14,588 completions. Both are large cost levers (15.9% and 16.2% respectively). Their redundancy arises because both push demand above the capacity ceiling, producing diminishing returns in the soft-ceiling region. This is a mechanical consequence of the ceiling specification, not an economic insight about the interaction between modular construction and land policy. The paper presents it as a substantive finding about lever redundancy.

**Mandated experiment RV05:** Decompose the modular × CPO interaction into: (a) the component attributable to ceiling truncation, and (b) any residual interaction in the gross (uncapped) completions. If the residual is zero (as expected from the linear cost model), state explicitly that the "redundancy" is entirely a ceiling artifact and revise the framing in §5.2 and §6.1.

### F6 — MAJOR: Parameter CIs not propagated through the 104,976 factorial

The 104,976-combination factorial is computed deterministically with point estimates. Monte Carlo is run only for selected packages (E16). The interaction terms, Pareto frontier, and optimal package rankings all use single-point estimates. No confidence intervals are reported for the interaction matrix or Pareto rankings.

**Mandated experiment RV06:** Run the Monte Carlo (1,000 draws minimum) for the top-5 and bottom-5 interaction pairs. Report 95% CIs on the interaction terms. If the CI for any "synergistic" pair includes zero, or the ranking of the Pareto frontier changes, flag this in the paper.

## 2. Scope vs Framing

### F7 — MINOR: Title implies empirical discovery; method is parameter propagation

The title "Do Housing Policy Levers Interact?" implies an empirical investigation. The method is a deterministic algebraic model with parameters from 19 prior studies. The "full factorial" is not an experimental design in the usual sense — it is a parameter sweep of a closed-form model. The paper should clarify this in the abstract: "We model 10 policy levers across 104,976 combinations in a **deterministic parameter-propagation model**."

### F8 — MINOR: "Pareto-efficient" framing assumes fiscal costs are accurate

The Pareto frontier relies on fiscal cost estimates (VAT zeroing = EUR 1.4B, land CPO = EUR 1.5B, etc.) that are stated without sources or confidence intervals. If these estimates are rough, the Pareto ranking may not be robust.

## 3. Reproducibility

### F9 — MINOR: Soft-ceiling congestion parameter (2%) is not sourced

The soft-ceiling formula uses a congestion parameter of 0.02, described as "calibrated to reasonable estimates but not empirically validated" (§6.3, limitation #3). No source is cited. This parameter controls the entire shape of the soft-ceiling curve, which is the basis for most reported numbers.

## 4. Overclaiming and Language

### F10 — MAJOR: "Optimal policy package" language without optimization

§3 calls the all-levers-maximised combination the "optimal policy package." No optimization was performed — this is the maximum of all levers, not an optimum in any constrained sense. With GE effects, this package may not be optimal because the marginal return to the 10th lever may be negative after price compression. Revise to "maximum policy package" or "all-levers-max."

---

## Summary of mandated experiments

| ID | Description | Severity |
|----|-------------|----------|
| RV01 | Workforce ramp-rate sensitivity (3 scenarios, 10-year trajectory) | CRITICAL |
| RV02 | Diminishing-returns workforce model | MAJOR |
| RV03 | Saturating elasticity (tanh) for r = 0.91 | MAJOR |
| RV04 | First-order GE price correction | MAJOR |
| RV05 | Decompose modular × CPO interaction (ceiling artifact vs real) | MAJOR |
| RV06 | Monte Carlo CIs on interaction terms and Pareto ranking | MAJOR |

## Findings requiring paper revision (no new experiments)

| ID | Description | Severity | Action |
|----|-------------|----------|--------|
| F7 | Title/abstract should clarify method is parameter propagation | MINOR | FIX |
| F8 | Pareto fiscal costs unsourced | MINOR | ACKNOWLEDGE |
| F9 | Soft-ceiling congestion parameter unsourced | MINOR | ACKNOWLEDGE |
| F10 | "Optimal" → "maximum" | MAJOR | FIX |
