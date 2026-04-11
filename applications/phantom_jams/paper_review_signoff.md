# Review Sign-Off: "Four Smart Cars Dissolve a Phantom Traffic Jam"

**Decision: APPROVED**

**Date:** 2026-04-10

---

## Assessment

The 1 MAJOR and 16 MINOR findings from the initial review have been addressed:

### MAJOR (critical platoon length derivation): RESOLVED

The revised paper now includes:
- Linearized IDM transfer function analysis (|G|_max = 1.029, confirming string instability)
- Numerical critical chain length measurement (8-9 vehicles at Sugiyama density)
- Clear connection between the chain length and the 3-to-4 ACC transition
- Acknowledgement that wave growth is primarily nonlinear

The causal explanation is no longer hand-waved; it is supported by both analytical and numerical evidence.

### MINOR findings: 9 FIXED, 7 ACKNOWLEDGED

Key fixes:
- Multi-seed replication of headline result: 0.93 +/- 0.23 m/s (5 seeds), reduction revised to 88 +/- 3%
- Statistical test on the 3-to-4 ACC transition: p < 0.001
- dt sensitivity check for controlled case: within noise floor
- Code availability statement added
- RL literature comparison added (Wu et al. 5% vs our 18.2%)
- ACC characterised as ring-optimised, not "simple"
- Precision of headline claims reduced to match uncertainty

Acknowledged items (fuel proxy calibration, Pareto knee statistics, CIRCLES quantitative comparison, OVM comparison, Chou et al. engagement) are appropriate deferrals to future work.

### New experiments: 18 experiments run

Multi-seed replication, dt sensitivity, placement sensitivity, wave speed measurement, sensor delay analysis, and baseline uncertainty quantification. All strengthen the paper.

---

## Remaining Limitations (acceptable)

1. No RL controller comparison on our simulator (acknowledged as limitation)
2. No multi-lane experiment (fundamental ring-road limitation)
3. Single-lane placement sensitivity only for ACC (partially addressed)
4. Fuel proxy uncalibrated (acknowledged)

These are appropriate scope boundaries for the paper.

---

## Verdict

The paper's central finding -- that 18.2% ACC penetration nearly eliminates the phantom jam on the Sugiyama ring -- is now supported by multi-seed evidence, statistical testing, and analytical derivation. The headline figures are appropriately qualified with uncertainty ranges. The limitations are honestly stated, including the important gap between the 18.2% hand-designed result and the ~5% RL result from the literature. The paper is suitable for final publication.

**Signed:** Automated HDR Review System
**Severity at sign-off:** 0 CRITICAL, 0 MAJOR, 0 MINOR (all addressed)
