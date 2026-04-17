# Blind Review — Phase 2.75

**Reviewer:** Automated blind review agent
**Date:** 2026-04-16

## Overall Assessment

The paper presents a competent decomposition of Irish construction material costs using real CSO data (WPM28, EHQ03, BEA04). The core analysis — CAGR ranking, PCA, weighted contribution, structural breaks — is sound. However, four substantive issues require correction before publication.

## Issue A: Employment-Output Gap Uses Wrong Comparator (CRITICAL)

**Finding:** The paper claims "employment doubled while output grew 9%" (E11). The 9% figure comes from BEA04C02 (Volume of Production Index for residential building), which is a *deflated production index* with base 2015 = 100. This index measures the real (inflation-adjusted) value of production, NOT physical units of output.

**Problem:** The volume index rose from 100.0 to 108.9 (2015-2024), a 9% increase. But CSO dwelling completions rose from approximately 12,666 (2015) to 30,330 (2024) — a 139% increase. The volume index is suppressed because it deflates by construction price indices, so cost inflation mechanically reduces the "volume" measure even when more physical dwellings are being built.

**Comparing employment (+103%) with a deflated volume index (+9%) conflates a measurement artifact with a real productivity decline.** The correct physical output measure (dwelling completions) shows +139% vs employment +103%, suggesting productivity is roughly flat or slightly positive — the opposite conclusion.

**Mandate:** Replace the BEA04 volume index comparison with CSO dwelling completions (HSM06 or NDQ06). If completions data is unavailable in the current dataset, state the limitation explicitly: "BEA04 is a deflated production index, not a physical output measure. The apparent 94pp gap likely reflects construction cost inflation embedded in the deflator rather than a real productivity decline."

## Issue B: NZEB Causal Claims Are Confounded (MAJOR)

**Finding:** The paper reports "excess inflation" of 2.3-5.1pp/yr for NZEB-affected materials (E20) and frames this as a regulatory cost burden. The Discussion section partially hedges ("should be treated as upper bounds") but the Abstract and Results present the numbers without adequate caveats.

**Problem:** NZEB implementation (November 2019) coincided almost exactly with COVID (March 2020) and preceded Ukraine (February 2022) by 27 months. The "pre-NZEB" period (2015-2019) was a low-inflation steady state, while the "post-NZEB" period (2019-2024) includes two of the largest supply chain shocks in modern history. ANY material would show excess post-2019 inflation regardless of NZEB.

**The E20 method uses simple percentage change (not CAGR) for the pre/post trend calculation,** dividing total change by number of years. This is mathematically incorrect for compound growth and biases the post-NZEB estimate upward because the post period includes the COVID/Ukraine spike-and-partial-reversion pattern.

**Mandate:**
1. Add a non-NZEB control group (e.g., cement, structural steel, plaster — materials unaffected by NZEB) and compute the same pre/post difference-in-differences. If the control group also shows excess post-2019 inflation, the NZEB attribution is confounded.
2. Use CAGR rather than simple percentage change for both periods.
3. In the Abstract, qualify: "associated with" not "caused by"; state the confounding explicitly.

## Issue C: WPM28 Measures Input Prices, Not Delivered Cost (MAJOR)

**Finding:** The paper interprets WPM28 as a proxy for construction cost. WPM28 is a wholesale price index — it measures the price of materials *at the wholesale level*, not installed cost.

**Problem:** WPM28 does not capture:
- **Productivity changes:** If labour productivity declines, more labour-hours per unit of material are needed, raising installed cost even if material price is flat.
- **Waste and over-ordering:** If specification changes (e.g., NZEB thicker walls) increase material quantity per sqm, WPM28 does not capture this because the index tracks price per unit, not quantity per dwelling.
- **Specification shift:** NZEB requires higher-spec materials (e.g., 150mm insulation instead of 100mm). If the unit price is flat but the quantity doubles, WPM28 shows no change while the actual insulation cost per dwelling has increased substantially.

**Mandate:** Add a paragraph in Limitations explicitly stating that WPM28 tracks input prices per unit, not installed cost per dwelling, and that specification-driven quantity changes (particularly for NZEB-mandated materials) are not captured. The insulation CAGR of 2.3% may understate the true insulation cost increase per dwelling if wall U-values require more material per sqm.

## Issue D: PCA Components Lack Interpretation (MINOR)

**Finding:** The paper reports "3 PCA components explain 90%" but does not interpret what they represent.

**Analysis of loadings:**
- **PC1 (82.4%):** Near-uniform positive loadings across all materials. This is a "rising tide" factor — general construction demand or common macroeconomic drivers (energy costs, exchange rates). Glass and hardwood timber have the lowest loadings, consistent with independent supply dynamics.
- **PC2 (5.1%):** Positive on glass/sand/stone, negative on timber/steel. This appears to be a **mineral vs. organic** contrast, or possibly a **domestic vs. imported** factor. It separates domestically-extracted materials (glass, aggregates) from internationally-traded ones (timber, steel).
- **PC3 (4.3%):** Positive on lighting/metal fittings, negative on bituminous/concrete. This may represent a **manufactured goods vs. bulk commodities** factor — finished manufactured products vs. raw/semi-processed materials.

**Mandate:** Add a paragraph interpreting each PC's loading pattern. PC1 is the common inflation factor. PC2 and PC3 are substantively interesting but not policy-critical. Note that none of the top-3 components isolates an "energy-related materials" cluster (insulation + HVAC + electrical), which means the NZEB-affected materials do not form a distinct latent factor — their price movements are driven by the same common factors as non-NZEB materials.

## Mandated Experiments

| ID | Experiment | Purpose |
|----|-----------|---------|
| E21 | Difference-in-differences: NZEB-affected vs control materials, pre/post Nov 2019 | Isolate NZEB effect from COVID/Ukraine confounding |
| E22 | Recompute E20 using CAGR instead of simple percentage change | Correct mathematical bias |
| E23 | BEA04 limitation statement + comparison with CSO completions (published figures, not from dataset) | Correct the productivity narrative |

## Minor Issues

- Abstract line "structural steel fabricated metal grew at 8.2%" — this is a sub-sub-category, not a distinct material. The abstract should use the parent "structural steel" category (7.78%) to avoid overstating.
- The T02 variance decomposition metric (12.4465 = 1244.6%) exceeds 100%, which means the "contribution shares" are not normalised and are misleading as stated. This is because the covariance-based decomposition does not sum to 1 when the sub-indices are not the actual portfolio weights. State this limitation.
- References [44] and [28] are duplicates (both SEAI NZEB). Similarly [45] and [29] (both TGD Part L).
