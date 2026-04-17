# Blind Review: Irish Residential Development Viability Frontier

## Verdict: MAJOR REVISION REQUIRED — Critical Calibration Error

---

## 1. Fatal Flaw: Wrong Construction Cost Table Used

The single largest error in this paper is that the model uses the **SCSI House Rebuilding Guide** figures (lines 118-248 of buildcost_2025h1.txt) rather than the **Construction Cost Guide** figures (lines 812-822 of the same document).

- **SCSI Rebuilding Guide** (used by the model): €2,690/sqm for a 4-bed semi — this is an **insurance rebuild cost** designed to help homeowners insure their property. It includes demolition, site clearance, reinstatement, and other factors irrelevant to new-build development.
- **Construction Cost Guide** (correct for viability): €1,900-2,050/sqm for semi-detached houses — this is the **new-build base construction cost** explicitly labelled as excluding siteworks, VAT, professional fees, and other developer costs.

The model then separately adds finance (10% × 2.5 years = 25% on hard costs), development contributions, and developer profit — items that overlap with what the inflated rebuild figure already implicitly captures. This produces systematic double-counting of approximately 30-40%.

**Evidence of miscalibration**: The paper's own reference (SCSI 2023) reports national average delivery cost for a 3-bed semi as ~€397,000 all-in. The model computes €473,000 at national averages — a €76,000 (19%) overstatement that explains why "everything is unviable."

## 2. The Disconnect with Reality

The paper concludes that development is unviable in all 18 counties, yet 30,330 homes were completed in 2024. The paper's Section 6.2 attempts to explain this away with five reconciliation factors (below-median costs, state subsidies, cross-subsidy, compressed margins, above-median prices). While these are all real factors, they should explain why development is *difficult and marginal* — not why a -56.6% margin model sees any activity at all. A model that is wrong by 50+ percentage points for the median case cannot be rescued by noting that some projects have above-median prices.

**Cross-check**: If we use the Construction Cost Guide mid-range (€1,975/sqm for semi-detached), add 12% for professional fees and preliminaries (€237/sqm), 5% for site development (€99/sqm), giving ~€2,311/sqm all-in build cost, then for Dublin:
- Construction: €2,400/sqm × 110 = €264,000 (versus €332,200 in the model)
- Total cost: ~€453,000 (versus €583,873)
- Margin: ~-5.7% (versus -21.6%)

This makes Dublin *marginal* — consistent with the observed reality that Dublin has significant but below-target construction activity.

## 3. Part V Modelling

Part V obligations (20% of units at cost or at a discount to market) are modelled as a 5% effective revenue reduction (20% × 25% discount). This is reasonable but should be noted as approximate — the actual mechanism varies by negotiation and can range from 0% (exempted schemes) to 10% effective cost.

## 4. Finance Cost Assumptions

- **10% finance rate**: This is high for current Irish development finance. Senior debt rates are typically 5-7% (Central Bank of Ireland 2023; Banking & Payments Federation Ireland). Mezzanine layers add cost but are not universal. The model should use a blended rate closer to 6-8%.
- **2.5 year build duration**: Reasonable for estate housing, but finance typically applies to drawn amounts, not full cost from day one. Average drawdown is ~60% of the build period, effectively halving the finance cost. The model uses simple interest on full hard costs for the full period.

## 5. Specific Mandated Fixes

1. **Replace SCSI Rebuild Guide costs with Construction Cost Guide costs**: Use the residential new-build figures (€1,750-2,050/sqm base) from page 3-4 of the same Buildcost document, plus explicit add-ons for professional fees (10-12%), site development works (€200-250/sqm from the same guide), and preliminaries (8-10%).
2. **Reduce finance rate to 7%** and apply average drawdown factor of 60%.
3. **Re-run all 22 experiments and the tournament** with corrected parameters.
4. **Revise the paper** to present the corrected viability map — which should show a gradient from marginal (Dublin, commuter belt) to unviable (rural/remote), consistent with observed development patterns.
5. **Validate against SCSI 2023**: The corrected model's national average delivery cost should be within 10% of the SCSI's €397,000 figure.

## 6. What Should Be Preserved

- The RICS residual method framework is correct and well-documented.
- The CSO RZLPA02 land price data is a genuine contribution.
- The experiment design (22 experiments + interactions) is thorough.
- The correlation with planning application rates (E10) is a strong finding if it survives recalibration.
- The sensitivity hierarchy (construction > finance > size > profit > density > contributions > land) will likely persist in relative ordering even with corrected absolute values.

## 7. Summary of Required Changes

| Issue | Severity | Fix |
|-------|----------|-----|
| Wrong cost table (rebuild vs new-build) | CRITICAL | Use Construction Cost Guide + explicit add-ons |
| Finance rate too high | MODERATE | 7% blended, 60% drawdown factor |
| All-18-unviable conclusion contradicted by 30k completions | CRITICAL | Recalibrate; expect gradient from marginal to unviable |
| SCSI 2023 cross-check fails | CRITICAL | Corrected model should match within 10% |
| Part V modelling | MINOR | Acceptable as approximation |

---

Reviewer recommendation: **Major revision**. The core methodology is sound but the input calibration produces results that contradict observable reality. Fix the construction cost input, re-run, and the paper's contribution (first county-level viability map using CSO data) will be genuine and policy-relevant.
