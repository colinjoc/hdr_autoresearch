# Review Sign-off: Traffic Signals Paper

**Date:** 2026-04-10
**Reviewer:** Automated adversarial review (HDR protocol)
**Verdict:** PASS with noted limitations

---

## Resolution status

| ID | Severity | Status | Notes |
|----|----------|--------|-------|
| CRITICAL-1 | CRITICAL | RESOLVED | All numbers from fresh 3-seed benchmark_sumo.csv |
| CRITICAL-2 | CRITICAL | RESOLVED | Table 1 and plots now use same data source |
| MAJOR-1 | MAJOR | RESOLVED | robustness_sumo.csv created, variance claim corrected |
| MAJOR-2 | MAJOR | RESOLVED | All RL claims softened with explicit caveats |
| MAJOR-3 | MAJOR | RESOLVED | Title and text say "four-parameter" |
| MAJOR-4 | MAJOR | ACKNOWLEDGED | 2-seed iteration is a limitation; 3-seed confirmation validates |
| MAJOR-5 | MAJOR | RESOLVED | robustness_sumo.csv on disk |
| MAJOR-6 | MAJOR | ACKNOWLEDGED | RL head-to-head is #1 future work |
| MINOR-1 | MINOR | RESOLVED | "without online learning" |
| MINOR-2 | MINOR | ACKNOWLEDGED | Cross-sim mapping is approximate |
| MINOR-3 | MINOR | RESOLVED | Table uses 3-seed data |
| MINOR-4 | MINOR | RESOLVED | Custom scenario caveat in Section 6.4 |
| MINOR-5 | MINOR | RESOLVED | Pseudocode note added |
| MINOR-6 | MINOR | ACKNOWLEDGED | MIN_GREEN sensitivity in future work |
| MINOR-7 | MINOR | RESOLVED | Single-intersection limitation expanded |

## Remaining caveats for the reader

1. **No head-to-head RL comparison.** The claim is that the SOTL rule's improvement range overlaps with literature-reported RL ranges. This is not the same as saying SOTL matches RL on the same benchmark. Future work should close this gap.
2. **2-seed HDR iteration.** Close-call keep/revert decisions (S03, S04, S11) may have been affected by seed noise. The 3-seed final confirmation provides the authoritative numbers.
3. **Single-intersection scope.** The result does not extend to network-level control where RL's advantage is most likely to appear.
4. **Custom scenarios.** Four of seven scenarios are not externally published. The three sumo-rl scenarios are the strongest evidence.

## Verification

- Fresh 3-seed benchmark confirms -49.10% mean per-scenario reduction
- Robustness sweep confirms 4.88 +/- 0.16 s (Webster) vs 2.17 +/- 0.10 s (SOTL)
- All 25 tests pass
- Plots regenerated from authoritative data
- Paper text, table, and plots are internally consistent

**Signed off.**
