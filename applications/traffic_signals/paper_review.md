# Adversarial Review: Traffic Signals Paper

**Reviewer:** Automated adversarial review (HDR protocol)
**Date:** 2026-04-10
**Paper:** "A Two-Parameter Self-Organising Rule for Adaptive Traffic Signal Control"

---

## Category 1: Numerical Accuracy and Internal Consistency

### CRITICAL-1: Paper text vs CSV data disagree on headline numbers
The paper claims a mean controller AWT of 3.75 seconds and a 49.10% reduction (Abstract, Section 5.1, Section 7). The headline_finding.png plot shows 4.02 seconds and -48.9%. The source of truth (benchmark_sumo.csv, 3 seeds) gives a mean controller AWT of 4.02 seconds and a -48.9% reduction. The paper Table 1 per-scenario values (e.g. sumo_rl_vhvh = 5.78 s) come from results.tsv which used 2 seeds, not the 3-seed benchmark run. The Figure 1 caption explicitly says "3 seeds each" but the text numbers match the 2-seed data. This is a data provenance failure: the paper cites two different runs and does not acknowledge the discrepancy.

Specific mismatches between benchmark_sumo.csv (3-seed, authoritative) and paper Table 1 (2-seed, results.tsv):
- uniform_low controller: CSV=1.97, paper=1.86 (6% discrepancy)
- sumo_rl_horizontal controller: CSV=5.48, paper=4.87 (12% discrepancy)
- sumo_rl_vhvh controller: CSV=7.04, paper=5.78 (22% discrepancy)

The overall reduction computed from the CSV is -48.9%, not -49.1%. The 49.1% claim is from 2-seed results.tsv. The paper must pick ONE authoritative data source and use it consistently throughout.

### CRITICAL-2: demand_sensitivity.png percentage labels do not match CSV
The plot shows "-13%" for uniform_low, "-57%" for uniform_medium, "-60%" for high, "-54%" for asymmetric, "-51%" for horizontal, "-52%" for vertical, "-36%" for vhvh. The CSV-derived reductions are -12.9%, -56.9%, -59.7%, -53.9%, -50.7%, -52.1%, -36.1%. These are close because the plot reads from the CSV. But the paper text (Table 1) reports -18.1% for uniform_low and -56.2% for horizontal and -47.6% for vhvh -- which differ from the plot by 5-12 percentage points. The plot and the table are telling different stories.

### MAJOR-1: Robustness claim lacks SUMO-side evidence file
Section 5.2 claims "2.17 +/- 0.10 seconds" for the controller on uniform_med at 5 seeds, and "4.88 +/- 0.16 seconds" for Webster. There is no robustness_sumo.csv file. The only robustness CSV (discoveries/robustness.csv) is from the lightweight toy simulator and shows identical baseline/ctrl values (a clear bug). The SUMO robustness numbers are unsupported by any on-disk artefact.

---

## Category 2: Claims vs Evidence

### MAJOR-2: "Matching deep reinforcement learning" is unsupported
The paper claims the SOTL rule "matches or exceeds published deep reinforcement learning methods." The evidence is that both fall in the 30-50% improvement range. But:
1. No RL method was actually run on these scenarios. The comparison is against a literature-reported range, not a head-to-head experiment.
2. The "30-50% range" conflates different benchmarks, networks, baselines, and metrics across many papers. A range drawn from heterogeneous studies is not a valid comparison point.
3. The headline plot (Figure 1) shows the RL bar at 40% reduction (midpoint) with error bars for 30-50%, which visually implies a direct measured comparison. The caption should state explicitly that the RL bar is a literature estimate, not a measurement.

### MAJOR-3: Paper claims "two parameters" but the controller has four
The title says "two-parameter", the abstract says "two-parameter Self-Organising Traffic Light (SOTL) rule with one preemption clause." The controller code has four parameters: CLEAR_THRESHOLD=0, WAITING_THRESHOLD=1, PREEMPT_RATIO=2, PREEMPT_FLOOR=4. The paper tries to frame the preemption as a separate "clause" rather than parameters, but they are tuned (S15 tried ratio=3, S16 tried ratio=2, S17 tried ratio=1.5, S18 tried floor=2). They are parameters. The paper should say "four parameters" or explain clearly why two of them do not count.

### MINOR-1: "Without any training" overstates the case
The controller was developed through 38 experiments with manual iteration, hypothesis testing, and parameter tuning across two simulators. This is a form of training (human-in-the-loop search over a parameter space). The controller has no online learning, but the development process is itself an optimisation loop. The paper should say "without online learning" or "without gradient-based training" rather than "without any training."

---

## Category 3: Methodology

### MAJOR-4: 2 seeds per scenario during HDR iteration is very low
The experiment log states "2 seeds per scenario during HDR iteration, 3 for final confirmation." With only 2 seeds, the stochastic noise in SUMO vehicle routing could easily produce false positives (keeping a change that only won by luck) or false negatives (reverting a genuine improvement). The S02 experiment (wait=3) shows a +219% regression on uniform_low -- this extreme sensitivity to seeds suggests that 2-seed averages are unreliable for close-call decisions like S03 (+0.67pp), S04 (+0.06pp), S11 (+0.06pp).

### MAJOR-5: No SUMO robustness sweep on disk
The paper claims a robustness sweep (Section 5.2) with 5 seeds on uniform_med. The robustness.csv file contains only lightweight-simulator data (and has a bug: ctrl == baseline). The SUMO robustness results are not reproducible from any on-disk artefact. This sweep should be re-run and the CSV saved.

### MINOR-2: Cross-simulator validation table counts do not match
Section 5.4 says "nine candidate improvements tested in both simulators" and "eight of the nine ideas failed in both." The table lists exactly nine rows. But the toy simulator ran 20 experiments and SUMO ran 18. The mapping between toy experiments and SUMO experiments is not explicit. Which toy experiment corresponds to which SUMO experiment? Without this mapping, the "8 of 9 failed" claim cannot be verified.

---

## Category 4: Presentation and Clarity

### MINOR-3: Table 1 percentage labels do not match computed values
Table 1 shows uniform_low reduction as "-18.1%" but computes to -18.1% from (1.86-2.27)/2.27 = -18.1%. This is internally consistent with the 2-seed data. However, per CRITICAL-1, these are the wrong numbers (should use 3-seed data). Once the data source is fixed, the table must be regenerated.

### MINOR-4: "Seven scenarios" includes four custom routes
The paper tests on seven scenarios but four of them are custom uniform-demand routes not used by any other study. Only three (sumo_rl_horizontal, sumo_rl_vertical, sumo_rl_vhvh) are published benchmarks. The claim "across seven scenarios" should acknowledge that only three are externally reproducible.

### MINOR-5: Section 3.1 code uses undefined helper functions
The code listing in Section 3.1 calls `current_phase_lanes()`, `other_phases()`, `best_other_phase()`, and `phase_lanes()`. These are described in prose but not defined. The actual controller.py uses a matrix multiply (`mask @ queue`), which is simpler and more precise. The paper should show the actual code or note the simplification.

---

## Category 5: Missing Experiments

### MAJOR-6: No head-to-head comparison against an actual RL baseline
The central claim is that the simple rule matches RL. Running even one RL method (e.g. DQN from sumo-rl's built-in examples) on the same 7 scenarios would convert the "literature range" comparison into a direct measurement. Without this, the headline claim is soft.

### MINOR-6: No sensitivity analysis on MIN_GREEN
The MIN_GREEN parameter is fixed at 5 seconds and described as "enforced by SUMO." But it is a tunable parameter passed to sumo-rl. The paper does not test whether the SOTL rule's advantage changes at MIN_GREEN=3 or MIN_GREEN=10. This is relevant because the drain-first rule's effectiveness depends on the lost time per switch.

---

## Category 6: Scope and Framing

### MINOR-7: "Network of one intersection" limitation underplayed
Section 6.4 mentions single-intersection focus but treats it as a minor caveat. In practice, the single-intersection result has limited policy relevance because most signal timing improvements in practice come from coordination (green waves, offset optimisation). The paper should more prominently note that the result does not extend to the multi-intersection case, which is where RL's advantage is most likely to appear.

---

## Summary

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 2 | CRITICAL-1, CRITICAL-2 |
| MAJOR    | 6 | MAJOR-1 through MAJOR-6 |
| MINOR    | 7 | MINOR-1 through MINOR-7 |

The paper has a genuine and interesting finding (simple rule matches RL on standard benchmarks) but is undermined by inconsistent data sourcing (2-seed vs 3-seed numbers mixed throughout), a missing robustness artefact, and the absence of any head-to-head RL comparison. The "two-parameter" framing is misleading when the controller has four tuned parameters. These issues must be resolved before sign-off.
