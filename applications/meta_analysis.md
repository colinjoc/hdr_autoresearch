# HDR Meta-Analysis: Empirical Conversion-Rate Prior

**Purpose.** Provide the reference-class prior on phase-conversion rates that every Phase −0.5 Drake decomposition (`proposal.md` §7) must use as input. **You do not estimate Pr(reach Phase 3) or Pr(non-null | reach Phase 3) from scratch — you read them from this file.**

**Updated.** Re-run after every project reaches Phase 3 OR is auto-killed. Owner: whoever closes the project.

---

## Why this file exists

Without an empirical conversion-rate prior, every new proposal's Drake decomposition is anchored on the author's optimism, not on the realised distribution of past outcomes. The literature on Cooke-calibrated expert elicitation (Cooke 1991 *Experts in Uncertainty*; Hanea et al. 2017 IDEA protocol) is unambiguous: **uncalibrated experts overestimate conversion probabilities by 2–5× across nearly every domain studied.** The fix is to track the empirical conversion rate from your own past work and use it as the reference-class prior for the next proposal.

The numbers below are the load-bearing input to every Phase −0.5 `assurance` calculation and every Drake `PriorImpact` decomposition.

---

## Phase-conversion rates (rolling, last 30 projects)

| Conversion stage | Estimated Pr | Sample size | 95% CI |
|---|---|---|---|
| Phase 0 → Phase 0.5 | 0.90 | 30 | [0.74, 0.98] |
| Phase 0.5 → Phase 2 KEEP exists | 0.70 | 27 | [0.50, 0.86] |
| Phase 2 → Phase 3 non-null | 0.45 | 20 | [0.23, 0.68] |
| Phase 3 → published-and-cited within 12 months | 0.50 | 9 | [0.19, 0.81] |
| **Compound: Phase −0.5 → cited publication** | **~0.14** | — | wide |

**Use these as the default `Pr(reach Phase 3)` and `Pr(non-null | reach Phase 3)` values in Drake decomposition unless your project has a strong reference-class argument for different rates.** If you override, document why in `proposal.md` §7.

**Update protocol.** When a project transitions phases, append a row to the `transitions.tsv` log (one row per project per stage) and re-compute the rates above. Numbers in this table go stale fast; consider any value > 60 days old as advisory only.

---

## Cluster-specific conversion modifiers

Some clusters reliably under- or over-perform the overall rate. These multipliers apply to `Pr(non-null | reach Phase 3)`:

| Cluster | Modifier | Reasoning |
|---|---|---|
| IE — Irish-specific | × 1.0 | Baseline; CSO/RTB data accessible, near-real-time deployments |
| EU — Europe-wide ex-Ireland | × 0.9 | Data fragmentation across countries |
| T — Transport | × 1.0 | GTFS-style standards make data accessible |
| W — Weather/climate | × 1.1 | Strong reanalysis priors usually deliver |
| O — Econ/urban/public | × 0.7 | Reporting-channel bias kills several (cf. OSS-1, ECON-1, ECON-2 nulls 2026-04) |
| P — Physical-sciences wildcards | × 0.6 | Often falls foul of HW-resolution-vs-SOTA check |
| criticality_* (LLM internals) | × 0.8 | σ_MR saturation kills several at Phase 0.5 |
| QEC / quantum codes | × 1.2 | Standard simulators + tournament-friendly design space |
| Stellarator / fusion | × 1.0 | DESC/simsopt mature; bottleneck is wall-clock not signal |
| Solar flare prediction | × 1.0 | SDO/HMI data + Bobra-Couvidat baseline well-established |
| HDR-applications (Irish housing micro-projects) | × 1.1 | Specific data sources usually deliver |

---

## Documented historical non-nulls and nulls (most recent 15)

Used to calibrate the cluster modifiers above. Update after each Phase 3 closure.

| Project | Cluster | Outcome | Phase reached | Notes |
|---|---|---|---|---|
| irish_fuel_profiteering (IE-fuel) | IE | NULL | 3 | EU27 synthetic-control shows no profiteering effect; live detector deployed |
| ssw_polar_vortex (P-13) | P | NULL | 3 | Public-index AUC 0.65±0.10; apparent 0.72 fragile under M-tests |
| swio_cyclone_ri (W-20) | W | non-null | 3 | AUC 0.886/0.909, survives M01-M06; ranker not calibrated |
| oss_abandonment (OSS-1) | O | NULL | 2.75 paused | E28 temporal-holdout AUC 0.54 |
| housing_crashes (ECON-2) | O | NULL | 3 | 4.7× PR-AUC lift dissolved under metro-cluster bootstrap |
| yc_vs_non_yc (ECON-1) | O | NULL | 3 | +6pp [-3, +15] null; placebo-diagnosis bias |
| criticality_sft_rlhf_distortion | criticality | NULL | 3 | Headline FALSIFIED at locked k=3-of-7 threshold |
| criticality_capability_axis | criticality | KILLED | 0.5 | σ_MR saturates at ≈1 on autoregressive generations |
| criticality_training_signal | criticality | non-null | 3 | Pre-registered double null; shipped |
| building_permits (O-4) | O | non-null | 3 | Austin 48d vs SF 605+d mechanism revealed |
| heat_mortality (W-5) | W | non-null | 3 | Wet-bulb night-time confirmed |
| iberian_blackout (EU-1) | EU | non-null | 3 | Cascade predictor + grid-state diagnosis |
| irish_radon (IE-2) | IE | non-null | 3 | Pre-measurement risk scoring deployed |
| dart_punctuality (IE-3) | IE | non-null | 3 | Cascade prediction (92.8 → 64.5%) |
| dublin_no2 (IE-7) | IE | non-null | 3 | Source attribution under WHO 2021 limits |

---

## Calibration check (run quarterly)

Bin the last 20 Phase −0.5 Drake P50(PriorImpact) estimates against the realised P50(PriorImpact) computed *after* the project closes (or auto-kills). If the average ratio `realised / proposed` is < 0.5, the author is over-optimistic and proposal-Drake estimates should be deflated by the running ratio.

Symmetric check on Bayesian assurance: bin last 20 Phase −0.5 assurance values against realised "did the falsifiable test produce a significant result" boolean. If assurance ≥ 0.5 cohort hits significance < 40% of the time, the prior on effect size is over-optimistic and should be widened (lower mean, fatter left tail) for future proposals.

These calibration checks are themselves an instance of Cooke's classical method (Cooke 1991, Aspinall 2010 *Nature*) applied to the user's own historical record.

---

## Transitions log

Append-only log used to recompute the rates table above. Format: `date,project_slug,from_phase,to_phase,verdict`.

`transitions.tsv` lives alongside this file. Schema:

```
date            project_slug     from_phase  to_phase  verdict
2026-05-13      non_cash_15min   2            3         non-null
2026-04-26      criticality_*    2            3         NULL_AS_PREREG
…
```

The compound conversion rates at the top of this file are computed by running `python -m hdr_meta_analysis transitions.tsv` after each append.
