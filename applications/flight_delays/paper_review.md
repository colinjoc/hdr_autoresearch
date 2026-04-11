# Adversarial Peer Review: "When Your Flight Is Late: How Delays Ripple Through the US Aviation Network"

**Reviewer recommendation: Major revision**

---

## 1. Claims vs Evidence

**Severity: MAJOR**

1. **The abstract claims AUC 0.92; the results table says 0.923 (CV) and 0.920 (holdout).** These are close but the rounding in the abstract to a single significant figure (0.92) flatters the holdout slightly and obscures the CV number. The feature importance table in the text (Section 4.2) reports 27.4% for the top feature, but the corresponding plot (`feature_importance.png`) labels it at 29.3%. Similarly, "log previous delay" is 16.0% in the table but 17.1% in the plot. These are not rounding discrepancies -- they are different numbers. Either the table or the plot was generated from a different model run, and neither is marked as the authoritative version. This is a reproducibility red flag.

2. **The claim that "aircraft rotation is the single dominant propagation mechanism, accounting for 41% of all delay minutes" conflates two different analyses.** The 41% comes from BTS self-reported cause codes (Section 4.3), while the 55%+ comes from XGBoost feature importance (Section 4.2). These measure fundamentally different things. BTS cause codes are airline-reported categorical attributions; XGBoost gain importance is a measure of split usefulness in a tree ensemble. The paper acknowledges this ("model-based importance decomposition may be a more reliable estimate") but then uses the 41% BTS number in the abstract and conclusion while using the 55%+ model number in the discussion. This inconsistency undermines the central quantitative claim.

3. **The "super-spreader" analysis (Section 4.6) uses undefined metrics.** The term "propagation risk score" and "propagation score" are used to rank routes and airports, but neither is defined anywhere in the paper. What formula produces a propagation score of 43.7 for DFW? Without this definition, the rankings are unverifiable assertions.

4. **The carrier analysis (Section 4.7) claims Southwest "manages delay through its point-to-point network structure."** This is an interpretive assertion with no supporting analysis. The paper does not control for network topology, fleet age, route mix, or any other carrier-level confound. Delta's longer turnarounds could reflect its route mix (more long-haul with naturally longer gates) rather than deliberate buffer strategy.

**Severity: MINOR**

5. The text says "holdout AUC 0.92 on unseen months" (abstract), but the holdout is a single month (April 2024, trained on January-March). A single holdout month is not "unseen months" (plural).

---

## 2. Scope vs Framing

**Severity: MAJOR**

1. **The paper is framed as studying "delay propagation" but is fundamentally a predictive modeling paper with descriptive statistics appended.** The prediction task (Section 4.1), the feature engineering (Section 3.1), and the model tournament dominate the paper. The "propagation" analysis (Sections 4.4-4.7) is purely descriptive -- it counts cascade depths, computes hourly averages, and ranks routes. There is no causal model of propagation dynamics, no simulation, no counterfactual analysis. The framing implies a contribution to understanding propagation mechanisms, but the actual contribution is a well-engineered binary classifier.

2. **The research question ("how far through the network does that delay ripple -- and what makes one delay contagious versus contained?") is not fully answered.** The "what makes a delay contagious" part is addressed only through feature importance of a black-box model. The paper never directly answers which specific flight/route/time characteristics cause a delay to cascade versus be absorbed, beyond the truism that "tight schedules propagate more." A partial-dependence or SHAP analysis would be needed to answer the stated question.

3. **The "network analysis" promised in the introduction (item 3) is minimal.** There is no graph-theoretic analysis, no network centrality measures, no community detection, no modeling of multi-hop propagation through the airport network. The "network" contribution is a ranked list of routes and airports by an undefined score. This undersells the title's promise of studying "how delays ripple through the US aviation network."

---

## 3. Reproducibility

**Severity: MAJOR**

1. **No code or data availability statement.** The paper uses publicly available BTS data, which is good, but provides no repository link, no scripts, no configuration files. The feature engineering (29 features across 5 categories) involves many implementation choices (how is "hub" defined? what counts as "the same hour" for congestion? how is the carrier buffer factor normalized?) that are not specified at a level sufficient for independent reproduction.

2. **The XGBoost hyperparameters are not fully specified.** Model selection mentions "GPU acceleration (histogram method)" but no learning rate, max depth, number of rounds, regularization parameters, or early stopping criteria. The "enhanced features" model has 29 features but no feature list is complete -- only the top 10 by importance are shown.

3. **Temporal cross-validation details are insufficient.** "3-fold temporal cross-validation" with "training data always temporally before test data" describes many possible splitting strategies. Are the folds months 1-2/3-4/5-6? Are they expanding windows? What is the gap between train and test? Is there any embargo period?

**Severity: MINOR**

4. The propagation depth analysis (Section 4.4) is restricted to January 2024 only, not the full six months. No justification is given for this restriction.

---

## 4. Missing Experiments

1. **No SHAP or partial-dependence analysis.** The paper relies entirely on XGBoost gain importance, which is known to be biased toward high-cardinality features. SHAP values would provide more reliable feature attribution and would directly answer the stated research question about what makes a delay contagious.

2. **No calibration analysis.** For a binary classifier intended to predict delays, calibration (reliability diagrams) is essential. AUC tells you about ranking quality but not about the predicted probabilities being trustworthy. At 20% base rate, F1 at default 0.5 threshold is a poor metric choice -- precision-recall curves would be more informative.

3. **No analysis of tail-number reliability.** The paper acknowledges that "tail number swaps (aircraft substitutions) are not captured" but does not quantify how often this occurs or what effect it has. A simple sensitivity analysis -- randomly breaking some fraction of rotation chains and measuring prediction degradation -- would bound this concern.

4. **No seasonal analysis.** Six months (January-June) covers winter and spring but not summer (the highest-delay season historically) or fall. At minimum, the paper should acknowledge whether its findings are likely to hold in July-September, when thunderstorm-driven delays dominate.

5. **No comparison to prior flight delay prediction models.** The literature review cites Rebollo and Balakrishnan (2014), Gui et al. (2019), Kim et al. (2016), and others. None of these are benchmarked against the proposed model, even on different data. What AUC do prior models achieve? Is 0.92 good in context?

6. **No analysis of first-leg-of-day flights.** These flights have no rotation history and represent the "clean reset" starting point. What is the model's accuracy on these flights specifically? If rotation features are zero for ~20% of flights, does the model fall back to airport congestion features gracefully?

7. **No passenger impact analysis.** The paper counts "flights affected" but a more policy-relevant metric would be passenger-hours of delay, which depends on aircraft size and load factor. A 10-flight cascade on regional jets has very different passenger impact than a 3-flight cascade on widebodies.

---

## 5. Overclaiming

**Severity: MAJOR**

1. **"Our key technical contribution is the reconstruction of aircraft rotation chains from tail-number identifiers."** Sorting flights by (date, tail_number, scheduled_departure) is a straightforward data-engineering step, not a technical contribution. It has been done in multiple prior studies (Beatty et al. 1999 is cited; Pyrgiotis et al. 2013 also reconstruct rotations). The paper should claim the contribution is the systematic evaluation of rotation features in a modern ML framework, not the reconstruction itself.

2. **"This finding... has not previously been demonstrated empirically at this scale using tail-number rotation reconstruction."** The qualifier "at this scale" is doing heavy lifting. Prior studies use smaller BTS samples but the same methodology. The scale (3.4M flights) is valuable but is not a qualitative advance in understanding. The claim should be tempered to "we confirm at large scale what prior studies have shown on smaller samples."

3. **The carrier-level conclusions (Section 4.7) make causal claims from observational data.** "Airlines that build more turnaround time into their schedules absorb incoming delays" implies a causal mechanism, but the data are observational. Carriers with longer turnarounds may also have different fleet mixes, route networks, and passenger demographics. The paper should use causal language more carefully.

**Severity: MINOR**

4. The practical advice ("book the first flight of the day") is reasonable but trivial and well-known to frequent travelers. Framing it as a finding of the analysis oversells it.

---

## 6. Literature Positioning

**Severity: MAJOR**

1. **The reference list is thin for an aviation delay paper.** Fourteen references is inadequate. Major omissions include: Fleurquin et al. (2013, Scientific Reports) is cited but their follow-up work on network resilience is not; the EUROCONTROL/FAA delay attribution literature is absent; the robust airline scheduling literature (Lan et al. 2006, Dunbar et al. 2012) that directly addresses buffer optimization is missing; the machine-learning-for-delay-prediction survey literature (e.g., Henricksen and Olaya 2020) is not cited.

2. **The claim that "most machine learning models for flight delay prediction treat each flight independently" is not well-supported.** The cited papers (Rebollo 2014, Choi 2016, Gui 2019) are from 2014-2019. The field has progressed substantially. Recent work (post-2020) using GNNs, transformers, and spatiotemporal models does incorporate network-level features. The literature review is outdated.

3. **No comparison to the EUROCONTROL/FAA "reactionary delay" framework.** The European delay attribution methodology (CODA reports) explicitly decomposes delay into primary and reactionary components at a system level. The paper's BTS-based decomposition is the US equivalent but should be contextualized within the international framework.

**Severity: MINOR**

4. The AhmadBeygi et al. (2010) result ("adding 5 minutes to minimum turnaround times at the 10 busiest US airports would reduce propagated delay by 15-20%") is cited as theoretical prediction but it was a simulation study, not pure theory. The characterization should be corrected.

---

## Summary of Required Revisions

| Category | Critical | Major | Minor |
|----------|----------|-------|-------|
| Claims vs evidence | 0 | 2 | 1 |
| Scope vs framing | 0 | 3 | 0 |
| Reproducibility | 0 | 2 | 1 |
| Missing experiments | 0 | 7 | 0 |
| Overclaiming | 0 | 2 | 1 |
| Literature positioning | 0 | 2 | 1 |
| **Total** | **0** | **18** | **4** |

The paper presents competent descriptive and predictive analysis of a well-studied problem using a well-known public dataset. The writing is clear and the visualizations are effective. However, the mismatch between the ambitious framing (network propagation analysis) and the actual contribution (a good classifier plus descriptive statistics), combined with reproducibility gaps and thin literature positioning, requires major revision before publication. The most important fixes are: (a) reconcile the feature importance numbers between tables and plots, (b) define the "propagation score" metric, (c) add SHAP analysis to answer the stated research question, (d) provide full reproducibility details, and (e) substantially expand the literature review.
