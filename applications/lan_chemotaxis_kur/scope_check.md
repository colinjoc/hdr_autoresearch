# Phase −0.5 Scope Check: Lan 2012 × KUR + housekeeping

Reviewer: fresh sub-agent, no access to prior conversation. Grouchy.

## 1. Novelty — is anyone already here?

The combination "KUR + housekeeping on Lan 2012" is narrow enough that I believe the literal intersection has not been published. But that does not make it new. The proposal is skating on the edge of three well-trodden results:

- **Hartich, Barato, Seifert (2014), *J. Stat. Mech.***, "Stochastic thermodynamics of bipartite systems" / related NESS-signalling papers — already applies TUR-style bounds to sensing and chemotactic information processing. The proposal merely *names* this paper and asserts "without KUR or housekeeping". That is not differentiation; that is a label swap. A reviewer will demand a concrete statement of what the KUR buys over the TUR on this dataset — does KUR give a numerically tighter bound here? Under what assumption (dynamical activity, time-symmetric current)? If the Lan 2012 observables are steady-state currents, the original TUR is the natural bound and KUR offers no tightening — the paper collapses.
- **Barato & Seifert (2015), *PRL* (TUR)** and follow-ups applying TUR to sensory adaptation (Hasegawa, Van Vu, Dechant–Sasa). A saturation test against an Lan-like dataset has been attempted before; the proposal must cite and beat them, not sidestep.
- **Lan & Tu's own 2016 review (*Rep. Prog. Phys.*)** reinterprets the 2012 data thermodynamically. If the review already compares against a bound, the re-analysis is incremental.

Housekeeping decomposition applied to sensing networks is in Sartori, Granger, Lee, Horowitz, Tu, Wingreen (2014, *PLoS Comp Biol*) — not cited. **This is the closest predecessor and its omission is damning.**

Verdict on novelty: weak as written. Probably *synthesis dressed as new bound*.

## 2. Falsifiability — are the three kill-outcomes real?

Mixed.

- "Everywhere below the bound vs above somewhere" — fine, binary, genuinely falsifiable.
- "Ratio < 3 at tightest point" — arbitrary. Why 3? Why not 2 or 5? Saturation in stochastic thermodynamics is usually reported as ratio → 1 within experimental uncertainty. A factor-of-3 gap is *loose*, not *saturated*. This threshold is chosen to guarantee the "saturation" headline survives. Reviewer will call it out.
- "r² > 0.5 across perturbations" — weak. r² = 0.5 across ~5–8 digitised points from a 14-year-old figure is not a correlation; it is noise. And r² comparisons between two different bounds (KUR vs Landauer-Bennett) require a proper model-selection statistic (ΔAIC, likelihood ratio), not a hand-waved r² threshold.

## 3. Venue

PRE is plausible for a *new bound or sharpened saturation test*. For a *re-analysis of one 2012 figure against an existing bound*, PRE will desk-reject as incremental. **Biophysical Journal is the correct primary venue** — they publish careful re-analyses of canonical biophysics datasets. Flip them.

## 4. Killer objections

1. Digitising Fig. 3 of Lan 2012 throws away the error bars. Any saturation claim depends on uncertainty you no longer have.
2. Kempes 2017 φ has >1 order-of-magnitude uncertainty; headline ratio is not stable.
3. TUR vs KUR on steady-state chemotactic currents may be identical — paper has no physics content.
4. Sartori et al. 2014 already did housekeeping decomposition on sensing.

VERDICT: REFRAME

## Required revisions for proposal_v2

- Cite and differentiate from Sartori et al. 2014 and Barato-Seifert TUR-on-sensing work explicitly.
- Prove KUR is strictly tighter than TUR for the Lan observables, or drop the KUR framing.
- Replace arbitrary "ratio < 3" / "r² > 0.5" thresholds with proper uncertainty-propagated tests.
- Flip primary venue to Biophysical Journal; PRE as fallback.
- Quantify load-bearing φ uncertainty and show the headline survives it.

VERDICT: REFRAME
