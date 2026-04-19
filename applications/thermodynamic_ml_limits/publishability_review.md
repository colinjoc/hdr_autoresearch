# Publishability Review (retroactive Phase 0.25)

**Date**: 2026-04-19
**Reviewer**: Fresh Phase 0.25 sub-agent (no prior conversation context)
**Inputs read**: `paper.md`, `literature_review.md`, `knowledge_base.md`, `research_queue.md`, `paper_review_signoff.md` (read last, did not anchor the checklist).
**Note**: No `proposal.md` or `scope_check.md` exists on disk; this is a retroactive review on a completed paper, not a pre-Phase 0.5 gate.

---

## Part 1 — Five-point checklist

### 1. Novelty taxonomy

**Category: synthesis + application, with one small genuinely new technical manoeuvre.**

The paper itself admits as much in §1: "The contribution of this paper is not to discover this gap but to systematically quantify it…". Breaking the claimed contributions apart:

- **A taxonomy of six multiplicative correction factors** — this is *synthesis* of well-established engineering corrections (MFU, data-movement fraction, mixed precision, sparsity, leakage, finite-time). Each individual factor is from prior work (Horowitz 2014; Chowdhery et al. 2023; Theis & Wong 2017; Proesmans et al. 2020). Closest prior works: Patterson et al. 2021 (Green AI energy breakdown); Ivanov et al. 2021 (data-movement decomposition); Yang, Chen & Sze 2017 (energy-aware pruning); Samsi et al. 2023 (per-token energy measurement). The multiplicative stacking is not itself a derivation — it is an accounting exercise.
- **Reformulated TUR bound using GNS** — this is the *one piece of arguably new technical content*. The substitution of McCandlish's gradient-noise-scale for a circular variance estimate is a minor but legitimate manoeuvre, and the best shot the paper has at a "first" claim. It is a one-line algebraic replacement, not a new theorem.
- **Sensitivity analysis / uncertainty quantification** — *application* of standard sensitivity analysis to an existing framework.
- **Cross-substrate biology comparison** — *application*, explicitly leveraging the "sibling project". §4.8 and §5.2 carry this, but §6.2 immediately retracts any directional claim ("no directional efficiency claim is supported"). This means the headline comparison was walked back to a metric-dependent observation.

**Nearest neighbours the paper is competing with (comparators, all exist):**
1. **Goldt & Seifert 2017** (PRL) — stochastic thermodynamics bound on perceptron learning. The paper's F2 (Crooks-for-SGD) is an extension of this framing, made explicit on p. 6.
2. **Boyd, Crutchfield & Gu 2022** (NJP / PRL) — thermodynamic ML, max-work = max-likelihood. Covers the conceptual ground the paper's Discussion uses.
3. **Peng, Sun, Duraisamy 2024** (Entropy) — "Stochastic Thermodynamics of Learning Parametric Probabilistic Models". This is the closest direct competitor; it already formulates ML training as a thermodynamic process with memorised vs. learned information and entropy-production accounting. The paper cites it once without a differentiation paragraph.
4. **Kolchinsky & Wolpert 2020** (PRR) and **Wolpert et al. 2024** — thermodynamic cost of Turing machines, generalised Landauer. The paper's Landauer-counting framework does not advance beyond these.
5. **Meier, Peper & Isokawa 2025** — Landauer bounds on DNNs (inference). Already derives per-neuron bounds using exactly the logic of §3.2 and §5.3.

**Verdict on novelty claim:** The abstract's phrasing ("establish a hierarchy of upper bounds") reads like category-four work. The actual contribution is category-two/three. The GNS-TUR substitution is defensible as a *minor* technical novelty but cannot carry a top-tier physics paper on its own. A reviewer at PRE/NJP who has read Peng et al. 2024 will ask, in the first paragraph of their report, "what is here that is not in Peng et al.?"

### 2. Falsifiability

The paper's headline claims and their falsifiability status:

| Headline claim | Falsifiable? | Kill-outcome |
|---|---|---|
| "ML training operates 10^7–10^28 above the Landauer limit" | **NO**, as stated. The range spans 21 OoM, so any number is "consistent". This is the classic unfalsifiable-in-disguise pattern ("is consistent with observation"). | Would need a single operating point with a defined metric, and then the kill-outcome would be a measured gap outside the reported uncertainty band. |
| "F3 TUR (GNS) is 1,409× tighter than bare Landauer" | **YES, trivially** — it is a deterministic calculation from published formulas. Can be "killed" only by arithmetic error. Not really a scientific claim; it is an arithmetic result. | Compute the same quantity and get a different answer. Not interesting. |
| "Sparsity has the widest parameter range (50×)" | **YES, trivially** — arithmetic sensitivity. | Re-run at different bounds. Uninteresting. |
| "Crooks (1 + T_sgd/T) heuristic holds for small η and fails for large" | **YES** — Jarzynski equality test on SGD trajectories. The paper actually did this (RV02). This is the *one* claim with a real empirical test. | More careful Langevin-SGD simulation at the same η showing Jarzynski holds. |
| "Biology and ML both operate far below Landauer; proofreading is the most efficient known" | **NO** (§6.2 already retracts directional comparison). | The paper itself says no directional claim is supported. |

**Structural problem:** four of the five headline results are deterministic calculations, not testable predictions. This is the paper the kind of thing that lives comfortably on arXiv / in a review journal but struggles in PRE or JSTAT, both of which expect a derivation, a prediction, or an experimental test.

**What could kill the paper overall:** a reviewer noting that none of the four "frameworks" produces a bound within 10^7 of the actual information-gain rate — meaning none of them is the *binding* constraint. The paper's own Conclusion says so: "The thermodynamic limits themselves are not the binding constraint on ML training; economics and engineering are." A grouchy reviewer will reply: if the thermodynamic limits are not binding, why is this paper a thermodynamics paper?

### 3. Load-bearing parameters

| Parameter | Headline value | Literature uncertainty | Headline scaling | Flag? |
|---|---|---|---|---|
| GPT-4 functional information I_func | 1.3e7 bits | **4.3e5 to 1.8e9 — 3.6 OoM** (§3.4, §6.3) | Efficiency ∝ I_func linearly. Gap ratios move 1:1 with this. | **FATAL FLAG**. The whole "10^7–10^28 gap" range is almost entirely driven by this parameter, not by the physics. The paper knows this and caveats it, but the caveat does not rescue the headline. |
| Housekeeping fraction φ | 0.39–0.69 for transformers | No published direct measurement at kernel level (own lit review, Theme 5). The paper's 0.39–0.69 is derived from Horowitz data + operational-intensity reasoning, not measured. | Linear in (1−φ). | **MAJOR FLAG**. An unmeasured load-bearing parameter. H-B01 is still "Queued" in research_queue.md — the project never measured it. |
| MFU | 0.3–0.6 | Chowdhery 2023; reasonable uncertainty ~2× | Linear in MFU. | OK. |
| B_geom = π² | Used as reference then overtly retracted | Known to overestimate CMOS by ~664× (own RV06) | — | Already retracted. |
| GPU junction temperature T | 350 K | ~15 K spread (RV05) | 1/T | OK, validated. |
| Gradient Noise Scale B_noise | 10^6 at GPT-4 scale | Extrapolated from McCandlish on much smaller models; no direct GPT-4 measurement | Linear in 1/B_noise | **MAJOR FLAG**. The TUR headline (1,409× tighter) depends directly on this, and the value is an extrapolation. Real B_noise for a GPT-4-scale language model is not publicly reported. |
| Total GPT-4 energy E_train | 1.36e14 J | Factor-of-2 uncertainty in published cluster estimates | Linear in E | OK (small flag). |
| p_bits, sparsity | headline FP8, 90% | Headline-dependent choice | 4× and 10× | Choice-driven, not physics-driven. Flag as a *design choice* presented as a *limit*. |

**Summary:** two of the headline's multiplicative factors (I_func and B_noise) are extrapolations with >1 OoM uncertainty. The paper quantifies I_func uncertainty honestly but does not propagate it into headline numbers in the abstract ("1,409× tighter", "10^13 tightening"). The abstract gives the impression of three-significant-figure precision; the underlying uncertainty is 3+ OoM.

### 4. Venue fit

Candidate venues, with fit reasons and typical objections:

1. **Physical Review E (PRE)** — *Fit*: publishes framework and application papers in stochastic thermodynamics, including Crooks/Jarzynski applied to new systems. *Typical objection*: demands rigorous derivation of any claimed new inequality. PRE will call out the Crooks-for-SGD bound as heuristic (the paper already admits this), will ask for a rigorous derivation or reframing, and will find the paper light on new physics relative to Goldt & Seifert 2017 and Peng et al. 2024. **Fit: weak-to-moderate.**

2. **Journal of Statistical Mechanics (JSTAT)** — *Fit*: publishes synthesis/perspective pieces on the statistical mechanics of learning; slightly more tolerant of phenomenological work than PRE. *Typical objection*: will want a concrete statistical-mechanics model, not a bound-comparison exercise. Will also note the lack of an analytical result beyond the GNS substitution. **Fit: moderate.**

3. **New Journal of Physics (NJP)** — *Fit*: publishes broader interdisciplinary work linking physics and computation; happy with synthesis if it is comprehensive. *Typical objection*: still wants novelty; will ask "what is the single new result"; likely bounced to major revisions because of the Peng 2024 overlap. **Fit: moderate, probably best bet.**

4. **(Alternative, not top-tier but good match)** — *Entropy* (MDPI) or *Transactions on Machine Learning Research*. Both publish exactly this kind of systematic survey-with-calculation. Would likely accept with minor revisions. If the target is to publish rather than to publish at a top venue, one of these is the realistic path.

**Venue mismatch risk:** None of the three top-tier candidates is a strong fit. The paper's honest framing as "systematic quantification, not discovery" cuts against PRE/PRL-style venues that want a new bound, a new derivation, or a sharp falsifiable prediction. **Strong REFRAME signal: either sharpen the contribution to one new technical result (the GNS-TUR manoeuvre, written up as a short methods paper with the taxonomy as supporting material), or target an "Entropy"-class venue where surveys-with-numbers belong.**

### 5. Top three killer objections

**Objection 1 — FATAL: "The paper is a synthesis pitched as a derivation."**
Specific form: "The abstract claims to 'establish a hierarchy of upper bounds', but every bound in §2 is quoted from prior work (Landauer, Proesmans, Barato-Seifert, Margolus-Levitin). The only mathematical step that is not in the cited prior work is the one-line substitution of B_noise into the TUR. Peng et al. 2024 have already formulated ML training as a thermodynamic process with entropy-production accounting; the paper does not differentiate itself from this work." Current project plan: §1 acknowledges this but the abstract and conclusion do not. **Mitigation**: Rewrite the abstract and §1 to foreground the GNS-TUR reformulation as *the* contribution, demote the six-factor taxonomy to a methodology/accounting tool, and add an explicit "Relation to prior work" subsection comparing directly to Goldt & Seifert 2017, Peng et al. 2024, and Meier et al. 2025. Alternatively, REFRAME as a short methods note on the GNS-TUR substitution plus a reproducible accounting notebook — that is a cleaner, more publishable object.

**Objection 2 — MAJOR: "Load-bearing parameters have uncertainty that swamps the headline precision."**
Specific form: "The paper quotes the TUR bound as 3.71e24 bits/s and the tightening as 1,409×. Both depend linearly on B_noise, which is extrapolated to GPT-4 scale with no measurement, and on functional information I_func which is known to span 3.6 OoM in the same paper. Presenting three significant figures for a quantity with >1 OoM uncertainty is not acceptable." Current project plan: §3.4 and §6.3 acknowledge I_func uncertainty, but the abstract and §4 tables still report point estimates. **Mitigation**: Propagate the I_func and B_noise uncertainty bands into every headline number. Report tightening as "10²–10⁴×" not "1,409×". Replace abstract's "10^13" tightening claim with a range. Add a single figure showing headline bound with uncertainty band, not a point. This is concrete and probably a day's work.

**Objection 3 — MAJOR: "If the bound exceeds the actual rate by 10^7–10^28, it is not a constraint."**
Specific form: "A bound that is at minimum 10^7 above the observed rate, and whose authors admit ‘the thermodynamic limits themselves are not the binding constraint on ML training; economics and engineering are’, is a weak paper for a physics journal. Why is this a thermodynamics paper rather than a computing-efficiency accounting paper?" Current project plan: the Conclusion actually concedes the point. **Mitigation**: Either (a) reframe the paper as a methodology/roadmap for when thermodynamic limits *will* bite (near-Landauer hardware, reversible computing, photonic accelerators — these are the regimes where the bounds would matter), making the headline "here is the framework that will be needed at the ~10^5–10^6 improvement horizon", or (b) redirect to a non-physics venue (TMLR, Entropy) where this framing is acceptable. Option (a) is the honest physics reframe; option (b) accepts the venue downgrade.

---

## Part 2 — Recommended paper.md edits

### ESSENTIAL

**E1. Rewrite the abstract to present a range, not point estimates, and to foreground the single technical novelty.**
- Current (§Abstract, lines 3–5): "a hierarchy of upper bounds… tighten this bound by a combined factor of approximately 10^13… yielding a bound of 3.71 x 10^24 bits/s — 1,409x tighter than bare Landauer."
- Proposed: "…successive corrections… tighten this bound by roughly 10^10–10^14, with the range driven by uncertainty in the housekeeping fraction and gradient noise scale. Our single new technical contribution is a reformulation of the thermodynamic uncertainty relation using the independently measurable Gradient Noise Scale (McCandlish et al. 2018), yielding a bound in the range 10^23–10^25 bits/s and removing the circular dependency in prior TUR formulations."

**E2. Add a "Relation to prior work" subsection (new §1.1 or §2.5) with explicit differentiation from Peng et al. 2024, Goldt & Seifert 2017, Meier et al. 2025, and Kolchinsky & Wolpert 2020.**
Currently Peng et al. 2024 is cited once in the reference list and mentioned once in §2.2 region. A reviewer will ask: "what is in this paper that is not in Peng 2024?" That question must be answered in the manuscript, not in the response letter.
- Proposed placement: new §1.1 "Relation to prior work", ~300 words, naming each comparator and what the paper does differently.

**E3. Demote the "~10^13 tightening" headline and retract "1,409× tighter" to a range in §1 (intro) and §4.1 Table 1.**
- Current §1 bullet 1 (line 17): "A taxonomy of six multiplicative correction factors that tighten the naive Landauer bound by a combined ~10^13x"
- Proposed: "A taxonomy of six multiplicative correction factors; stacked, these tighten the bare Landauer bound by 10^10–10^14, with the range set by uncertainties in housekeeping and precision choices."
- Current §4.1 Table 1: reports "3.71 x 10^24" for F3 TUR.
- Proposed: report "~10^23–10^25" and footnote that the central value uses B_noise extrapolated from McCandlish et al. 2018 to GPT-4 scale.

**E4. In §4.4 (Reformulated TUR Bound), explicitly state that B_noise at GPT-4 scale is an extrapolation, not a measurement, and give the 1 OoM uncertainty it carries.**
- Current (line 183): "At GPT-4 parameters (P=17.5 MW, T=350 K, B=2048, B_noise=10^6)…"
- Proposed: add after "B_noise=10^6": "(extrapolated from McCandlish et al. 2018, who report B_noise ranging 10^4–10^6 across scales; the GPT-4 value is not directly measured and carries approximately 1 order of magnitude of uncertainty)".

**E5. Reframe the Conclusion to answer "why is this a physics paper?"**
- Current (§7, lines 294–298): ends with "The thermodynamic limits themselves are not the binding constraint on ML training; economics and engineering are."
- Proposed: add a following paragraph: "The framework becomes binding at the ~10^5–10^6 improvement horizon projected by Koomey's law (c. 2048–2100) or at the onset of reversible / photonic / neuromorphic computing, both of which are already in advanced research. The contribution of this paper is therefore not a constraint on today's training, but a calibrated tool for bound-vs-reality comparison at the regime where thermodynamic limits are expected to bind."

### STRONGLY RECOMMENDED

**S1. Convert Table 1 in §4.1 and Table in §4.2 to include uncertainty bands on every bound.**
At minimum, propagate the 3.6 OoM I_func uncertainty and the ~1 OoM B_noise uncertainty through the final column. A point estimate like "3.71 x 10^24" in a column next to "3.6 OoM uncertainty" is an internal inconsistency that a reviewer will flag.

**S2. Move §4.5 Crooks Validation forward to §2.3 as a caveat, not a result.**
The Crooks-for-SGD bound is already labelled heuristic in §2.2 and §6.1. Presenting the Jarzynski validation as a "Result" oversells what it is: a negative check that the heuristic survives only for small η. Re-label §4.5 as "Heuristic range of validity" and move into §2.

**S3. Delete §4.8 (biology comparison) or move it to Appendix.**
§6.2 already retracts any directional claim from this section. A section whose claim is retracted in the Limitations section should not live as a numbered Result section. The cross-substrate comparison works better as a supplementary discussion or an appendix, not as §4.8.

**S4. Strengthen §1 framing of the contribution as synthesis-with-one-new-substitution, not "establish a hierarchy".**
Current §1 (lines 15–22): lists five contributions in a way that reads like novelty stack. Proposed: lead with a single sentence stating the contribution type ("This is a systematic quantification and a one-line technical substitution that resolves a known circularity in TUR-based bounds on learning currents.").

**S5. Add one concrete falsifiable prediction to §5 Discussion.**
The paper currently has no testable prediction that could be checked by a future experiment. Propose adding in §5.3 a sentence like: "The framework predicts that a 4-bit precision, 99%-sparsity training run on H100-class hardware at 350 K will achieve a functional-information gain rate within a factor of 200 of today's best practice, with deviations beyond this flagging a failure of one of the multiplicative factors." This gives the paper a falsifiable hook, even a cheap one.

### NICE TO HAVE

**N1. §3.2, bullet 6 "Finite-time cost":** state up front that this factor is retracted for CMOS use rather than asking the reader to read to §6.4.

**N2. §4.2:** the cumulative-bound column mixes factors and is hard to read at the "3.34 x 10^22" row; consider a log-cumulative column.

**N3. §2.4 Quantum Speed Limits:** the Margolus-Levitin and Bekenstein bounds are acknowledged as "vacuously loose". Consider moving them to a single "§2.5 Why quantum bounds are not binding" paragraph rather than a theme-weight section.

**N4. References:** Peng, X. et al. (2024) is cited as "Stochastic Thermodynamics of ML Training" — the actual Entropy paper title is "Stochastic Thermodynamics of Learning Parametric Probabilistic Models" (Peng, Sun, Duraisamy). Fix.

**N5. §5.2:** the sibling-project comparison is interesting context but the second paragraph's "striking parallel" framing overstates what is established. Soften to "analogously".

**N6. §6.3:** "Empirical validation… is urgently needed" is a strong phrase; soften to "remains future work" to match the honest framing elsewhere.

---

## Verdict

VERDICT: REFRAME

The paper is an honest, competent synthesis with one small technical manoeuvre (the GNS-TUR substitution). Internally it is consistent — the Phase 2.75 signoff correctly notes that all critical issues were addressed. But internal consistency is not publishability. Against a grouchy PRE/JSTAT/NJP reviewer, three major problems surface: (1) the abstract reads as a novelty claim while the content is synthesis-plus-one-substitution; (2) two load-bearing parameters (I_func and B_noise) carry 1–3.6 OoM uncertainty that is not propagated into headline numbers; (3) the paper concedes thermodynamic limits are not binding, which undercuts the physics framing. The GNS-TUR reformulation is a real, defensible contribution — but it is a short methods note, not a top-tier physics paper. The recommended path is to either (a) reframe for a realistic venue (Entropy, TMLR) where this kind of systematic-quantification paper belongs and accept the venue downgrade, or (b) shrink to a short note on the GNS-TUR substitution targeted at PRE, keeping the taxonomy as supplementary material. Rewriting the abstract and §1 as listed under ESSENTIAL is the minimum needed before any submission.

VERDICT: REFRAME
