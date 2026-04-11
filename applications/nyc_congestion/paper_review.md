# Adversarial Review: NYC Congestion Charge Effect Decomposition

**Reviewer Instructions**: This is a blind review of paper.md. The reviewer is tasked with identifying overclaiming, methodological weaknesses, missing experiments, and cherry-picking.

---

## Overall Assessment

The paper presents a multi-source descriptive analysis of the NYC congestion charge's effects. The negative finding on displacement is well-supported by multiple independent data sources. However, several methodological concerns limit the strength of the causal claims.

**Recommendation**: Major revision required. The analysis is descriptive, not causal, and the paper should be more explicit about this distinction.

---

## Major Issues

### M1. The decomposition is accounting, not causal inference

The decomposition into mode shift, route displacement, time shift, and trip elimination is presented as if these are identified causal components. They are not. The "mode shift" estimate comes from observing that transit ridership increased, but this conflates the congestion charge effect with ongoing post-pandemic transit recovery. Without a counterfactual for transit ridership (what would ridership have been without the charge?), the mode shift component is confounded.

**Required experiment**: Compare Q1 ridership growth (Q1 2024 to Q1 2025) against Q1 2023 to Q1 2024 growth to assess the pre-existing trend. If subway ridership was already growing at 9% per year, the congestion charge contribution is zero.

### M2. November vs February TLC comparison has severe seasonal confound

Comparing November 2024 TLC trips to February 2025 TLC trips conflates the congestion charge with winter weather effects. February typically has fewer trips than November due to cold weather and shorter month.

**Required experiment**: Download October 2023 and February 2024 TLC data (pre-charge) and compute the same CBD pickup share. If the November-to-February seasonal drop in CBD pickups is similar in non-charge years, the 4.4% decline is not attributable to the charge.

### M3. DID model is underpowered and misspecified

The DID model uses Manhattan vs all outer boroughs as treatment vs control. But the outer boroughs are heterogeneous -- some are more plausible controls than others. Brooklyn and Queens share borders with the CRZ; the Bronx is connected via bridges; Staten Island is geographically isolated. Using all outer boroughs equally weights them, diluting the treatment effect.

**Suggested improvement**: Report DID separately for each outer-borough control, or weight by proximity to the CRZ.

### M4. ATR data limitations are acknowledged but the paper still uses ATR-based decomposition as headline finding

The paper correctly notes that ATR R-squared is 0.06, yet the decomposition chart and the abstract feature ATR-based volume percentage changes as if they are meaningful. If the ATR data is too noisy, it should not appear in the decomposition waterfall chart.

**Required change**: Either remove the ATR-based decomposition percentages from the abstract and headline, or present them with explicit uncertainty bounds.

## Minor Issues

### m1. Missing pre-pandemic baseline for transit

The MTA data includes percent-of-comparable-pre-pandemic-day columns. These should be reported alongside raw ridership to contextualise the 9% YoY increase.

### m2. CRZ entry data is available but not used

The MTA dataset includes CRZ Entries (daily counts of vehicles entering the Congestion Relief Zone) from January 5, 2025 onward. This is the most direct measure of traffic entering the zone and should be the centerpiece of the analysis, not the noisy ATR data.

**Required**: Report CRZ entry trends over the 15-month post-charge period.

### m3. No consideration of toll exemptions

The congestion charge has significant exemptions (emergency vehicles, buses, residents of the zone receiving a credit, low-income drivers). The paper should note these exemptions and their potential effect on the observed volume changes.

### m4. "Trip elimination" is a residual, not a measured component

The trip elimination component is defined as the residual after subtracting mode shift, route displacement, and time shift from the total change. This means all measurement error accumulates in this component. The paper should flag this explicitly.

### m5. R-squared 0.06 for the main predictive model

A model that explains 6% of variance should not be used for counterfactual prediction. The counterfactual analysis in Section 3.4 should be de-emphasised or removed.

## Required Additional Experiments

1. **E-R01**: Pre-existing transit ridership trend (Q1 2023 to Q1 2024 vs Q1 2024 to Q1 2025)
2. **E-R02**: Seasonal TLC comparison (Nov 2023 vs Feb 2024 CBD share)
3. **E-R03**: CRZ entry count trend analysis
4. **E-R04**: Per-outer-borough DID estimates
5. **E-R05**: Report pre-pandemic percent for transit metrics

---

**Signed**: Independent Adversarial Reviewer
