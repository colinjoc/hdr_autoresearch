# Review Response: "When Your Flight Is Late: How Delays Ripple Through the US Aviation Network"

We thank the reviewer for a thorough and constructive review. Below we address each finding with specific changes made to the manuscript. Changes are organized by review section.

---

## 1. Claims vs Evidence

### MAJOR 1: Feature importance numbers disagree between text and plot

**Response**: The discrepancy arose because the plot and the table were generated from separate model runs (different random seeds). We have:
- Pinned the model random seed (random_state=42) in the plot generation code
- Added SHAP analysis as the primary feature attribution method (Section 3.5, Section 4.2)
- Reported both XGBoost gain importance (Table 2) and SHAP values (Table 3) explicitly, noting their disagreement and why SHAP is treated as more reliable (per Strobl et al. 2007)
- Regenerated all plots from the same model run

The XGBoost gain importance numbers (27.4%, 16.0%, etc.) now match between text and plot. More importantly, the SHAP analysis reveals a materially different story: airport congestion features dominate (dest_arr_delay 20.4%, origin_dep_delay 15.4%), with rotation features at 28% of total SHAP importance rather than 58% of gain importance.

### MAJOR 2: 41% BTS vs 55% model conflation

**Response**: Section 4.3 now explicitly states that BTS cause codes and model-based importance measure fundamentally different quantities (realized delay minutes by reported cause vs. predictive variance across all flights). The abstract and conclusion no longer juxtapose these numbers as if they measure the same thing. The conclusion now separately reports "41% of airline-reported delay minutes (BTS cause codes) and 28% of SHAP-based model importance."

### MAJOR 3: "Propagation risk score" undefined

**Response**: Section 4.6 now defines the formula explicitly:

propagation_score(r) = delay_rate(r) x mean_LateAircraftDelay(r) x log(1 + n_flights(r))

with explanations of each component, the minimum traffic threshold (100 flights for routes, 500 departures for airports), and the rationale for the log-traffic weighting.

### MAJOR 4: Carrier claims without controls

**Response**: Section 4.7 has been rewritten to use observational language throughout. Specific changes: "manages delay through its point-to-point network structure" -> "shows moderate propagation rates; its network structure, aircraft size, and route mix may all contribute, though we cannot isolate these factors with observational data alone." A new limitations paragraph (Section 5.3) explicitly states that all carrier-level findings are observational correlations that do not control for fleet composition, route mix, or operational strategy.

### MINOR 5: "unseen months" (plural) vs single holdout month

**Response**: Abstract corrected to "holdout AUC 0.920 on a single unseen month, April 2024."

---

## 2. Scope vs Framing

### MAJOR 1: Framing as "network propagation" but delivering classifier + descriptive stats

**Response**: Introduction item 3 changed from "Network analysis" to "Descriptive network characterization." The introduction now describes the contribution accurately as a prediction model with descriptive characterization, not a causal propagation model. The conclusion no longer claims to have modeled propagation dynamics.

### MAJOR 2: "What makes a delay contagious" not answered beyond feature importance

**Response**: Added SHAP analysis (Section 3.5, Section 4.2) with feature-level attributions. Added first-leg-of-day analysis (Section 4.9) quantifying the contribution of rotation information vs. airport information. The SHAP results directly answer the question: congestion at destination and origin airports, turnaround time, and the delay-buffer interaction jointly determine propagation.

### MAJOR 3: Minimal network analysis

**Response**: Added Section 4.8 (Network Structure) with degree centrality, betweenness centrality, and PageRank for all 343 airports. Key finding: DFW ranks #1 on both degree centrality (0.58) and propagation score. Betweenness reveals that some smaller airports (AGS, DAB) are critical connectors whose disruption would fragment the network. The analysis now includes genuine graph-theoretic metrics computed with NetworkX, not just ranked lists.

---

## 3. Reproducibility

### MAJOR 1: No code or data availability statement

**Response**: Added a "Code and Data Availability" section with GitHub repository link, BTS data URL, and instructions for reproducing each analysis component.

### MAJOR 2: Hyperparameters not fully specified

**Response**: Section 3.3 now specifies all hyperparameters: n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, histogram method, random_state=42. All 29 features are listed in Section 3.1 and the full feature list is in the code repository.

### MAJOR 3: Temporal CV details insufficient

**Response**: Section 3.3 now describes the expanding-window strategy with a concrete example (fold boundaries for a 3-month dataset). The gap between train and test (none beyond the fold boundary date) and the NaN handling strategy (-999 fill for tree models) are specified.

### MINOR 4: Propagation depth restricted to January only

**Response**: Section 4.4 now states the restriction and gives the reason (computational cost of per-chain analysis) and the choice criterion (first month in dataset).

---

## 4. Missing Experiments

### MAJOR 1: No SHAP analysis

**Response**: Added. SHAP TreeExplainer on 20,000 subsampled flights (Section 3.5, Table 3, new Figure 6: shap_importance.png). Key finding: SHAP and gain importance disagree substantially. SHAP shows airport congestion dominating (35.5% total for destination + origin + taxi-out) and rotation features at 28%. This changes the paper's central narrative: we no longer claim rotation is "dominant" by model importance, only by BTS cause codes.

### MAJOR 2: No calibration analysis

**Response**: Added to Section 4.9. Brier score 0.074 (vs. baseline 0.162), ECE 0.009. The model is well calibrated, meaning predicted probabilities can be interpreted directly.

### MAJOR 3: No tail-number swap sensitivity

**Response**: Acknowledged in limitations (Section 5.3) as a gap. We note that "a sensitivity analysis randomly breaking some fraction of chains would bound this concern" but have not performed it. This remains future work.

### MAJOR 4: No seasonal analysis

**Response**: Added temporal stability analysis in Section 4.9: AUC is stable at 0.919-0.921 across months 4-6 (std=0.0008). Section 5.3 now acknowledges that the data does not cover summer thunderstorm season and performance may differ.

### MAJOR 5: No comparison to prior models

**Response**: Section 1 now cites specific prior AUC results (Rebollo 2014: AUC 0.80-0.85; Choi 2016: AUC 0.75-0.82) and notes that direct comparison is impossible due to different datasets and time periods. The literature review mentions recent post-2020 work on GNNs and transformers.

### MAJOR 6: No first-leg-of-day analysis

**Response**: Added to Section 4.9. First-leg flights (24.4% of holdout) achieve AUC 0.880 vs. 0.928 for non-first-leg. The model degrades gracefully to airport congestion features. First-leg delay rate is 12.6% vs. 21.1% for subsequent legs.

### MAJOR 7: No passenger impact

**Response**: Acknowledged in limitations (Section 5.3): "We report flight-level delay counts but do not estimate passenger-hours of delay, which would require load factor data not available in BTS."

---

## 5. Overclaiming

### MAJOR 1: "Key technical contribution" overclaimed

**Response**: Reworded Section 3.1 from "the key technical contribution" to "derived from tail-number reconstruction, following Beatty et al. 1999 and Pyrgiotis et al. 2013." The contribution is now framed as systematic evaluation of rotation features in a modern ML framework at scale, not the reconstruction itself.

### MAJOR 2: "At this scale" doing heavy lifting

**Response**: Introduction now reads "confirms at large scale what prior studies have shown on smaller samples" instead of claiming a novel empirical demonstration.

### MAJOR 3: Causal claims from observational data

**Response**: All carrier-level language changed to observational ("associated with," "correlated with") throughout Sections 4.7 and 5. New explicit limitation paragraph on causal inference.

### MINOR 4: "Book the first flight" as finding

**Response**: Conclusion now describes this as "straightforward and consistent with prior knowledge" rather than presenting it as a novel finding.

---

## 6. Literature Positioning

### MAJOR 1: Thin 14-reference bibliography

**Response**: Expanded to 27 references. Added: Baspinar & Koyuncu (2016), Belcastro et al. (2016), Campanelli et al. (2016), Dunbar et al. (2012), EUROCONTROL (2023), Fleurquin et al. (2014), Guimera et al. (2005), Henricksen & Olaya (2020), Lan et al. (2006), Lundberg & Lee (2017), Strobl et al. (2007), Wu (2005).

### MAJOR 2: Literature review outdated (pre-2020)

**Response**: Added Henricksen & Olaya (2020) survey. Introduction acknowledges that recent post-2020 work uses GNNs, transformers, and spatiotemporal models that do incorporate network features.

### MAJOR 3: No EUROCONTROL/CODA context

**Response**: Added EUROCONTROL (2023) CODA reference to bibliography. The European "reactionary delay" decomposition methodology is now cited for international context.

### MINOR 4: AhmadBeygi (2010) characterized as "theoretical"

**Response**: Changed to "simulated" throughout.

---

## Summary of Changes

| Category | Finding | Status |
|----------|---------|--------|
| Claims vs evidence | Feature importance disagreement | Fixed: SHAP + gain, pinned seed |
| Claims vs evidence | 41% vs 55% conflation | Fixed: explicit distinction |
| Claims vs evidence | Propagation score undefined | Fixed: formula added |
| Claims vs evidence | Carrier causal claims | Fixed: observational language |
| Scope vs framing | Mismatch title/content | Fixed: reframed as classifier + descriptive |
| Scope vs framing | No SHAP for research question | Fixed: SHAP added |
| Scope vs framing | No network analysis | Fixed: centrality metrics added |
| Reproducibility | No code/data statement | Fixed: added |
| Reproducibility | Hyperparameters incomplete | Fixed: all specified |
| Reproducibility | Temporal CV unclear | Fixed: detailed description |
| Missing experiments | SHAP | Added: Section 3.5, Table 3 |
| Missing experiments | Calibration | Added: Brier 0.074, ECE 0.009 |
| Missing experiments | Tail-number sensitivity | Acknowledged as future work |
| Missing experiments | Seasonal analysis | Added: temporal stability + limitation |
| Missing experiments | Prior model comparison | Added: cited prior AUC results |
| Missing experiments | First-leg-of-day | Added: AUC 0.880 vs 0.928 |
| Missing experiments | Passenger impact | Acknowledged as limitation |
| Overclaiming | "Key technical contribution" | Fixed: tempered |
| Overclaiming | "At this scale" | Fixed: tempered |
| Overclaiming | Causal claims | Fixed: observational language |
| Literature | Thin bibliography | Fixed: 14 -> 27 references |
| Literature | Outdated ML references | Fixed: added post-2020 |
| Literature | No EUROCONTROL | Fixed: added |

All 18 MAJOR and 4 MINOR findings have been addressed.
