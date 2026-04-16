# Phase 3.5 Signoff Review -- Irish Housing Bottleneck Meta-Analysis

**Date**: 2026-04-16

**Paper**: `paper.md` (final, incorporating R1-R4 mandated experiments)

---

## Mandate Compliance

| Mandate | Requirement | Status | Finding |
|---------|------------|--------|---------|
| R1 | Opt-out sensitivity sweep (50%/70%/90%/100%) | PASS | Ranking never swaps. Perm volume outranks CCC at all tested rates. |
| R2 | Monte Carlo ranking robustness (5,000 draws) | PASS | Perm volume is #1 in 100.0% of draws. CCC never outranks it. |
| R3 | ABP/JR double-count audit | PASS | 100% overlap confirmed. Combined efficiency revised from ~6,100 to ~5,028. Paper updated. |
| R4 | Bootstrap 95% CIs on marginal-units/yr | PASS | CIs reported for all 5 top bottlenecks. Effective-completions CIs are non-overlapping for #1 vs #3. |

---

## Key Findings from Mandated Experiments

### R1: Opt-out sensitivity
The ranking is invariant to the opt-out build rate. At 50% (pessimistic), permission volume delivers +4,946 effective completions per +10k vs CCC at +3,267 per +10pp. The structural reason: permission volume scales with opt-out (more permissions create more opt-out commencements) while CCC improvements only affect non-opt-out projects.

### R2: Ranking robustness
Permission volume is #1 in every single Monte Carlo draw (5,000 draws). The 90% CI lower bound for permission volume (4,916 effective) exceeds the 90% CI upper bound for CCC (3,712). This is not a close call.

### R3: Double-count correction
The ABP and JR interventions share the same S-2 counterfactual channel. The paper now correctly reports approximately 5,028 combined efficiency completions (31% of gap) rather than approximately 6,100 (37%). This is a material correction that was properly incorporated.

### R4: Bootstrap CIs
Certified-completions CIs for permission volume [3,225, 3,769] and CCC [2,708, 3,788] overlap, but the policy-relevant effective-completions CIs are cleanly separated: [4,916, 6,350] vs [2,796, 3,712].

---

## Waterfall Arithmetic Self-Consistency

38,000 - 3,610 - 20,324 - 703 = 13,363 (paper says 13,362). Rounding error of 1 unit. PASS.

---

## Inherited Caveats Checklist

| Predecessor | Caveat | Flagged in paper? |
|-------------|--------|-------------------|
| PL-4 | Join-failure inflates lapse rate; 9.5% is upper bound | Yes (Caveat 11a) |
| S-2 | Indirect JR channel bounded [0, 9,305] with no point estimate | Yes (Caveat 11b) |
| PL-1 | Dark-permission rate channel-dependent [0.67%, 39%] | Yes (Caveat 11c) |
| S-1 | Apartment-flag data issue | Yes (Caveat 11d) |
| S-2 | ABP/JR overlap | Yes (Caveat 12, R3) |

---

## Limitations Acknowledged

1. Construction capacity as observed ceiling, not measured physical constraint -- properly caveated.
2. Steady-state assumption (962-day pipeline lag) -- properly caveated.
3. Monte Carlo parameter independence -- properly caveated.
4. No cost/tenure decomposition -- properly caveated.
5. Permission volume as gross flow, not net new-site -- properly caveated.

---

## Verdict

**ACCEPT.** The paper satisfies all four mandated experiments. The ranking (permission volume #1, construction capacity #2, CCC filing #3) is robustly established by R1 and R2. The ABP/JR double-count has been corrected (R3). Bootstrap CIs are provided for all top bottlenecks (R4). All material inherited caveats are flagged. The headline claims are appropriately hedged and supported by the evidence.

The paper makes a clear, well-supported contribution: it provides the first quantitative ranking of Irish housing bottlenecks using a TOC framework, with uncertainty quantification and sensitivity analysis demonstrating that the ranking is not an artefact of any single assumption.
