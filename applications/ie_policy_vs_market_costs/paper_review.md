# Phase 2.75 Blind Review: Policy-Set vs Market-Driven Costs in Irish Residential Development

## Overall Assessment

The paper makes a useful contribution by quantifying the policy vs market cost split across all 26 Irish counties. The central finding -- policy costs at 13-17% cannot close a median viability gap of EUR 144k -- is well-supported. However, five methodological issues weaken specific claims.

## Issue A: VAT Calculation (MAJOR)

**Problem.** The paper states VAT at 13.5% on a EUR 400k home is EUR 47k, and the model applies VAT to `hard_cost + professional_fees`. However, Irish VAT on new residential construction is charged on the SALE PRICE to the buyer at 13.5%, not on the value added by the developer. The model actually computes `VAT = 0.135 * (hard_cost + professional_fees)`, which equals approximately EUR 45k for Dublin. This is the correct approach for a cost model: VAT is levied on the construction output (contractor's price + professional fees), not on the gross sale price. The "value added" in VAT terminology refers to output tax minus input tax; builders can reclaim VAT on inputs, so the effective VAT is on the net output value. The model is defensible but should explicitly state that VAT is computed on the construction output (hard cost + fees) because builders reclaim input VAT. The paper's Section 2.2 formula is correct.

**Verdict**: Minor clarification needed. The calculation is economically sound.

## Issue B: Part V at 20% -- Cost Mechanism (MAJOR)

**Problem.** Part V requires 20% of units to be transferred to the local authority at "cost price" (not market price). The cost to the developer is the forgone profit margin on those 20% of units, NOT 20% of units given away for free. The model uses fixed Part V costs per unit (EUR 5k-20k by region), which appears to approximate the cross-subsidy loss. E19 correctly models this: the loss is `0.20 * max(0, sale_price - cost_price)`, spread over 80% of market units. However, the fixed Part V cost in the cost stack (EUR 20k for Dublin) does not match the E19 cross-subsidy calculation (EUR 13,820 per market unit). The paper should reconcile these two figures or explain why the fixed estimate is used for the cost stack.

**Verdict**: The cost stack overestimates Part V cost in Dublin (EUR 20k vs EUR 13.8k computed). Needs reconciliation.

## Issue C: EUR 144k Median Viability Gap -- Provenance (MAJOR)

**Problem.** The median viability gap of EUR 144,289 comes from E18 in `results.tsv`. It is computed by `viability_gap_fund()` in `cost_model.py`, which calls `build_county_cost_stack()` for each county. This function uses the same cost model parameters throughout (0.85 scheme factor, 12% professional fees, 8% finance, 15% margin). The question is whether this uses the same calibration as U-2's corrected viability model (CCG not rebuild costs). The 0.85 scheme factor IS the CCG correction (converting rebuild costs to scheme costs). The gap is computed from the SAME model that produces all other results, so it is internally consistent. However, the paper does not explicitly state that the viability gap uses scheme-level costs (0.85 factor) rather than one-off rebuild costs. This should be stated.

**Verdict**: Internally consistent. Add one sentence confirming scheme-cost basis.

## Issue D: Static Price Assumption Under Policy Removal (MAJOR)

**Problem.** The claim "eliminating all policy costs makes only 4 counties viable" assumes sale prices remain constant. In reality, removing VAT (or other policy costs) would partially flow through to buyers as lower prices (reducing the revenue side), not purely as margin improvement for developers. The literature review itself cites Crossley et al. (2012) and Glaeser & Gyourko (2018) on tax capitalisation into land prices. This is acknowledged in the Limitations (Section 4.4 point 1: "Static model") but not quantified. The paper should run a sensitivity: if 50% of VAT savings are passed through to buyers (lower sale prices), how many counties become viable?

**Mandate**: Run experiment E31 with 50% pass-through of all policy savings to buyers. If removing VAT saves EUR 45k per unit but sale prices also drop by EUR 22.5k, re-test viability. Report in Section 4.4.

## Issue E: Developer Margin Classification (MODERATE)

**Problem.** Developer margin at 15% is classified as MARKET, but this is debatable. Social/affordable housing schemes (including AHBs and LDA developments) routinely accept 6-8% margins. Part V units are delivered at cost (0% margin). The state can and does set margin expectations through its procurement policies. A more nuanced classification would note that 15% is the COMMERCIAL benchmark but that state-led delivery can compress this. E13 already tests margin compression to 10%, finding that Wicklow comes very close to viability (-0.2%). The paper should note this classification ambiguity.

**Mandate**: Add a paragraph in Discussion acknowledging that developer margin sits on the POLICY-MARKET boundary, cross-referencing E13 margin-compression results. Note that if margin were reclassified as partially-POLICY, the policy share would rise to approximately 25-28%.

## Summary of Mandated Experiments

| ID | Description | Priority |
|:---|:---|:---|
| E31 | 50% pass-through sensitivity: if policy savings reduce sale price by 50% of the saving, recount viable counties for VAT-zeroed and all-policy-zeroed scenarios | HIGH |
| Text | Reconcile Part V fixed cost (EUR 20k) with E19 cross-subsidy (EUR 13.8k) | HIGH |
| Text | Add sentence confirming viability gap uses scheme costs (0.85 factor) | MEDIUM |
| Text | Add paragraph on developer margin classification ambiguity with E13 cross-ref | MEDIUM |
| Text | Clarify VAT calculation basis (output tax minus reclaimable input tax) | LOW |
