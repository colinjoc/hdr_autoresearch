# Scope Check — thermodynamic_cross_substrate

Reviewer: fresh sub-agent, Phase −0.5. No project context beyond `proposal.md` and the scope-check sections of `program.md`.

## 1. Novelty

The proposed bound τ_min ≥ I · k_B T ln 2 / (φ·P) is *algebraically* a Landauer energy bound divided by a power, with a housekeeping-fraction prefactor. Three papers the proposal would be elbowing:

- **Wolpert, J. Phys. A 2019 ("Stochastic thermodynamics of computation")** — already derives minimum-time/minimum-dissipation bounds for computing systems with general state spaces, including housekeeping decomposition. Our bound is a corollary at best.
- **Kempes et al., J. R. Soc. Interface 2017** — already computes dissipation per bit / per operation across cells, ribosomes, and computers. This IS the cross-substrate comparison the proposal is pitching as new, minus the explicit "saturation ratio" framing.
- **Ito & Sagawa 2015 / Barato–Seifert 2015 TUR line** — the thermodynamic uncertainty relation already bounds precision·time·dissipation. "Minimum time to accumulate information" is within ε of a TUR restatement.

The proposal does not differentiate from any of these. The novelty claim is **weak-to-absent**.

## 2. Falsifiability

Mixed. The "bound violated by any single system" kill-outcome is genuinely falsifiable. But the headline — "saturation ratio S is universal" — is softened by "approximately preserved" and the four-orders-of-magnitude tolerance. Four decades on a ratio that is itself a ratio of a bound to observed time, across systems whose I_func and φ are known to ≲ one order of magnitude at best, is a band so wide that *not* sitting inside it would be surprising. This is the "consistent with observation" anti-pattern in disguise. Also: φ and I_func are not measured quantities for GPT-4; they are estimated with large freedom. The author chooses the φ convention and then tests whether the result is universal — a textbook tautology risk.

## 3. Venue fit

PRX does publish cross-disciplinary thermodynamics. But PRX wants a **sharp theorem or a sharp empirical claim**. A saturation-ratio survey with 4-decade tolerance and hand-chosen φ is magazine-physics, not PRX. Nature Communications Physics is more plausible but will still bounce it on novelty vs. Kempes 2017. **Target is too ambitious for the stated contribution.**

## 4. Most likely killer objections

1. "This is Landauer + housekeeping + a comparison table. What is the theorem?"
2. "I_func (Wong et al. 2023) is contested and not operationally defined for GPT-4 training. Your headline depends on it."
3. "φ is whatever you need it to be. Show the result is robust to the φ convention across all four systems."
4. "Kempes 2017 already did cross-substrate dissipation-per-bit. What is new here?"

## Specific revisions required for REFRAME

- Replace the "universal saturation ratio" headline with a **sharp testable theorem** (e.g. a tighter bound under a specific non-equilibrium condition) OR a **genuinely new empirical regularity** that survives φ-convention ablation.
- Provide operational definitions of I_func and φ for each of the four substrates before claiming they can be compared. The proposal must commit to one convention per quantity and justify it.
- Narrow to two substrates at most until the measurement conventions are defensible (biology vs. ML, not four).
- Drop PRX unless a theorem is on offer. Target PRE ("framework + data in stochastic thermodynamics") or J. Stat. Mech. until novelty is demonstrated.
- Cite and explicitly differentiate from Wolpert 2019, Kempes 2017, and the TUR literature (Barato–Seifert 2015, Horowitz–Gingrich 2020 review).

VERDICT: REFRAME
