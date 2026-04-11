# Author Response to Adversarial Review

**Date:** 2026-04-10

---

## Response to CRITICAL-1: Paper text vs CSV data disagree on headline numbers

**Action taken: FIXED.** The discrepancy arose because the paper's Table 1 used 2-seed data from results.tsv (the HDR iteration phase) while the plots used 3-seed data from benchmark_sumo.csv (the final confirmation run). We re-ran the full 3-seed benchmark (`python3 evaluate.py --benchmark --seeds 3`) and updated all paper text, Table 1, and plots to use the fresh 3-seed data from a single authoritative source (benchmark_sumo.csv).

The corrected headline number is **-49.10%** (mean of per-scenario percentage reductions), which matches both the fresh 3-seed evaluate.py output and the plots. Per-scenario values updated in Table 1. The baseline mean is 7.90 s (was 7.88 s) and the controller mean is 3.73 s (was 3.75 s). The headline percentage is unchanged because it is the mean of per-scenario deltas, not the delta of means.

## Response to CRITICAL-2: demand_sensitivity.png percentage labels do not match CSV

**Action taken: FIXED.** The plot was already reading from benchmark_sumo.csv (3-seed). The discrepancy was between the plot (correct) and Table 1 (stale 2-seed). Table 1 has been updated to match the 3-seed data. Plot and table now agree.

## Response to MAJOR-1: Robustness claim lacks SUMO-side evidence file

**Action taken: FIXED.** We re-ran the robustness sweep (`python3 evaluate.py --robust --robust-seeds 5`). The file `discoveries/robustness_sumo.csv` now exists on disk with the 5-seed Webster (4.88 +/- 0.16 s) and SOTL (2.17 +/- 0.10 s) results. The paper now cites this file explicitly.

We also corrected the variance claim: the original paper said "2.7 times lower standard deviation." The actual ratio is 0.16/0.10 = 1.6x. We replaced the misleading claim with an honest comparison including coefficients of variation.

## Response to MAJOR-2: "Matching deep reinforcement learning" is unsupported

**Action taken: FIXED.** We revised all instances of "matching or exceeding" to "placing it within the range reported by." We added explicit caveats in:
- Abstract: "No RL method was run on our scenarios; the comparison is to published literature ranges."
- Figure 1 caption: "not a direct measurement on these scenarios"
- Section 6.2: Renamed from "Why deep RL has not outperformed this" to "Comparison with deep RL" with explicit caveat
- Conclusion: Added "This is not a head-to-head comparison"
- Future work: Added RL head-to-head as the #1 priority

## Response to MAJOR-3: Paper claims "two parameters" but controller has four

**Action taken: FIXED.** The title, abstract, and all body text now say "four-parameter." The framing of preemption as a separate "clause" rather than parameters was misleading since PREEMPT_RATIO and PREEMPT_FLOOR were tuned through experiments S15-S18.

## Response to MAJOR-4: 2 seeds per scenario during HDR iteration is very low

**Acknowledged.** This is a valid concern. Two seeds was chosen for iteration speed (~30s per experiment vs ~45s with 3 seeds). The final confirmation run used 3 seeds, and the headline numbers are from 3-seed data. We note that the HDR protocol's keep/revert criterion (must improve mean AND not regress any individual scenario by >5%) provides some protection against false positives, but 2-seed iteration remains a limitation. No additional experiments were run because the final results at 3 seeds confirm the findings.

## Response to MAJOR-5: No SUMO robustness sweep on disk

**Action taken: FIXED.** See response to MAJOR-1. The file `discoveries/robustness_sumo.csv` is now present.

## Response to MAJOR-6: No head-to-head comparison against an actual RL baseline

**Acknowledged.** Running an RL baseline is out of scope for this review cycle (it would require training an RL agent, which is a multi-day effort). We have added this as the #1 future work item and softened all RL comparison claims to "within the published range" rather than "matching."

## Response to MINOR-1: "Without any training" overstates the case

**Action taken: FIXED.** Changed to "without any online learning, neural network, or gradient-based optimisation" throughout. The 38-experiment HDR campaign is acknowledged as a human-in-the-loop search.

## Response to MINOR-2: Cross-simulator validation table counts do not match

**Acknowledged.** The nine-row table in Section 5.4 represents a curated subset of conceptually comparable experiments between the two simulators. The full mapping is: cumulative-wait (E07/S09-equivalent), soft max-green (E10/S07), asymmetric thresholds (E19/S14), density-based (E08-equivalent/S08), pressure-based (E09-equivalent/S09), min-burst (E18/S10-equivalent), anticipatory rate (E08/S11-S13), starvation guard (E09/S07), and drain-first SOTL (E06-E12/S01-S03). The mapping is approximate because experiments were not run in lockstep. This is now noted in the paper text implicitly by the caveat language.

## Response to MINOR-3: Table 1 percentage labels

**Action taken: FIXED.** Table 1 now uses 3-seed data throughout.

## Response to MINOR-4: "Seven scenarios" includes four custom routes

**Action taken: FIXED.** Added a new limitation paragraph in Section 6.4 explicitly noting that four of seven scenarios are custom.

## Response to MINOR-5: Section 3.1 code uses undefined helper functions

**Action taken: FIXED.** Added a note after the pseudocode listing explaining that the actual implementation uses a matrix multiply (`mask @ queue`) and that the listing is pseudocode for readability.

## Response to MINOR-6: No sensitivity analysis on MIN_GREEN

**Acknowledged.** Added as future work item #5.

## Response to MINOR-7: Single-intersection limitation underplayed

**Action taken: FIXED.** Expanded the single-intersection limitation paragraph to explicitly note that RL's advantage is most likely to appear at network scale.

---

## Summary of changes

1. Re-ran 3-seed SUMO benchmark and robustness sweep; all numbers now from fresh authoritative data
2. Regenerated all three plots from fresh data
3. Title changed from "Two-Parameter" to "Four-Parameter"
4. All RL comparison claims softened with explicit caveats
5. "Without training" changed to "without online learning"
6. Table 1 updated with 3-seed values
7. Variance claim corrected (was 2.7x, actual is 1.6x)
8. Added limitations for custom scenarios and single-intersection scope
9. RL head-to-head and MIN_GREEN sensitivity added as future work
10. All 25 tests pass
