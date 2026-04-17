# Phase 3.5 Signoff Review

## Status: PASS

---

## Review of Corrections

### Issue 1 (CRITICAL): Wrong construction cost table
**Status: FIXED.** The model now uses the Buildcost.ie Construction Cost Guide base rates (semi-detached EUR 1,975/sqm) plus explicit add-ons for site development (EUR 225/sqm) and professional fees/preliminaries (12%), producing all-in costs of EUR 2,224-2,766/sqm by region. The SCSI House Rebuilding Guide figures (EUR 2,428-3,020/sqm) are no longer used for viability calculation.

**Validation**: Model total cost at national average parameters = EUR 399,580 versus SCSI (2023) benchmark of EUR 397,000. Error: 0.6%. A dedicated test (`test_scsi_cross_check`) enforces this within 15%.

### Issue 2 (MODERATE): Finance rate and drawdown
**Status: FIXED.** Default finance rate reduced from 10% to 7% (blended senior/mezzanine, consistent with BPFI 2024 data). A 60% average drawdown factor is applied to reflect the S-curve of construction expenditure, reducing effective finance cost from 25% of hard costs to 10.5%.

### Issue 3 (CRITICAL): All-18-unviable contradicted reality
**Status: FIXED.** The corrected model shows:
- Dublin: **-3.1% (marginal)** -- consistent with active but constrained market
- GDA commuter belt: -9% to -12% -- consistent with significant but below-target activity
- Secondary cities: -20% to -30% -- consistent with limited development requiring state support
- Rural/remote: -60% to -95% -- consistent with negligible market-led development

### Issue 4 (MINOR): Part V modelling
**Status: UNCHANGED.** The 5% effective revenue reduction (20% x 25% discount) remains approximate but acceptable. Paper notes the approximation in Section 6.4 (Limitations).

## Experiment Results Post-Correction

| Experiment | Old Value | New Value | Direction | Plausibility |
|-----------|----------|----------|-----------|-------------|
| E00 national margin | -56.6% | -31.2% | Improved | Consistent with SCSI benchmark |
| E01 Dublin margin | -21.6% | -3.1% | Improved | Consistent with active market |
| E02 apartment margin | -12.2% | +5.1% | Now viable | Consistent with apartment delivery |
| E04 land sensitivity | 3.9pp | 3.4pp | Slightly less | Land still least sensitive |
| E05 constr sensitivity | 37.5pp | 30.4pp | Less extreme | Still dominant |
| E09 viable under cost reduction | 0 counties | 3 counties | Improved | Dublin, Meath, Kildare matches reality |
| E10 correlation | r=0.907 | r=0.908 | Preserved | Core finding robust |
| E14 cost-rental subsidy | 9.7% | 0.0% | Now viable | Validates government programme |
| T04 Monte Carlo % viable | 9.2% | 38.5% | Higher | More realistic uncertainty range |
| E18 break-even premium | 90.5% | 55.4% | Lower | Dublin now only 3.8% gap |
| E21 combined policy viable | 1 county | 4 counties | More responsive | Dublin, Meath, Kildare, Cork |

## Key Findings Preserved After Correction

1. Construction cost dominance (9:1 sensitivity ratio over land cost) -- robust
2. Viability-application rate correlation (r = 0.91) -- robust
3. Sensitivity hierarchy ordering unchanged -- robust
4. GDA-to-periphery viability gradient -- now more nuanced and realistic
5. RZLT paradox for unviable land -- still valid for 17/18 counties

## New Findings Enabled by Correction

1. Apartment-density development is viable at +5.1% -- actionable policy finding
2. Cost-rental programme is economically sound without subsidy -- validates government policy
3. Dublin's marginal status explains observed market behaviour -- intellectual coherence
4. Scale economies make 200-unit schemes viable even nationally -- favours large-site policy

## Checklist

- [x] Construction costs use Construction Cost Guide, not SCSI Rebuild Guide
- [x] Finance rate corrected to 7% with 60% drawdown
- [x] SCSI cross-check passes (0.6% error)
- [x] All 7 unit tests pass
- [x] All 22 experiments + 1 interaction re-run
- [x] Results.tsv updated
- [x] Plots regenerated
- [x] Paper.md rewritten with corrected findings
- [x] Viability gradient consistent with observed development patterns
- [x] Limitations section updated
- [x] Abbreviations expanded on first use throughout paper

## Verdict

**PASS.** The critical calibration error has been identified and fixed. The corrected model produces results that are (a) validated against an independent industry benchmark (SCSI 2023, 0.6% error), (b) consistent with observed development patterns across Irish counties, and (c) yield actionable policy findings (density pathway, construction cost reduction priority). The core research contributions -- first county-level viability map using CSO data, construction cost dominance finding, viability-application correlation -- survive correction and are strengthened by internal consistency with reality.
