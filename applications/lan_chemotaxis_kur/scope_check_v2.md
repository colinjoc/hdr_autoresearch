# Scope Check v2 — Phase −0.5 Round 2 of 3

Reviewer: grouchy biophysics / stochastic-thermodynamics sub-agent, fresh invocation, no prior context beyond program.md Phase −0.5 and proposal_v2.md.

## 1. Is the Phase 0.5 KUR-tightness gate genuinely decisive?

Partially. The gate *is* crisp: either KUR's dynamical-activity factor gives a strictly tighter bound than TUR on Lan-2012-type steady-state adaptation observables, or it does not. Good. What is *not* crisp is the fallback. "TUR + housekeeping with proper φ uncertainty propagation" is dangerously close to Sartori et al. 2014 with better error bars. Sartori already did housekeeping decomposition on sensory adaptation in bipartite-system form. A re-analysis whose novel contribution is "we propagated φ through their framework and put CIs on the ratio" is a methods paper at best — Biophysical Journal *might* take it as a technical re-analysis, but it is NOT a "new physics" paper. The proposal acknowledges this ("a tighter replication"), which is honest, but the fallback paper needs a second independent contribution — e.g., a quantitative φ-budget tolerance map for future chemotaxis measurements — to justify publication on its own. As written, the O1-fail branch is a major risk, not a clean pivot.

## 2. Falsifiability

O1–O5 are genuinely binary and tied to statistics (bootstrap 95% CI, ΔAIC ≥ 2 log-likelihood units, factor-of-2 φ-stability). This is a real improvement over v1's "ratio < 3" / "r² > 0.5". Minor quibble: O5's "factor of 2" stability window is still a taste threshold — justify it from the φ measurement uncertainty, not handwave.

## 3. Dataset-reachability risk

Inadequately handled. §2(c) *commits* to extracting ±SEM from Lan 2012 Fig. 3 + SI, but there is no pre-commitment that a 15-minute reachability smoke test has been done. Per program.md memory ("verify data access before Phase 0"), this is precisely the failure mode that sinks a 200-citation lit review. O2 names the risk but does not operationalise: what if bars are present in the figure but not point-resolved? The proposal should require that Phase 0.5 begins with a pixel-level digitisation test on Fig. 3 *and* independent cross-check against the Lan-Tu 2016 review's reproduction of those points, with a GO/NO-GO recorded before Phase 0 burns 200 citations.

## 4. Venue fit

Biophysical Journal is correct for a careful uncertainty-propagated re-analysis of a canonical dataset. PRE fallback is defensible only on the KUR-tightening branch.

## 5. Top three killer objections

1. **O1-fail fallback is thin (MAJOR).** Mitigation: pre-commit a second novel contribution in the TUR-only branch (e.g., φ-tolerance envelope usable by future experiments) so the fallback paper does not reduce to "Sartori 2014 with error bars".
2. **Dataset extraction not smoke-tested (MAJOR).** Mitigation: run Fig. 3 digitisation + SI error-bar extraction as a 1-day task *before* Phase 0; record in data_sources.md.
3. **Lan-Tu 2016 review may already contain a bound comparison (MAJOR, could be fatal).** Mitigation: the proposal flags this in §5 — enforce it: Phase 0 must open with a full read of the 2016 review and an explicit gap-statement, or the project is KILLed at Phase 0.

None are fatal on v2 as written; two are major and have concrete mitigations.

VERDICT: PROCEED

---

Summary: v2 fixes v1's four lethal objections. Gate is decisive for the KUR-pass branch; the KUR-fail branch needs a second contribution to justify publication. Proceed with mitigations 1–3 added to research_queue.md as `pre-empt-reviewer` flags.
