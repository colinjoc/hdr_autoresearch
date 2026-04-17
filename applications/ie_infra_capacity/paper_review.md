# Blind Review: U-3 Infrastructure Capacity Blocks

## Overall Assessment

The paper asks a well-defined policy question and answers it with real data from the Uisce Eireann capacity register. The methodology is transparent and the findings are specific enough to be actionable. However, several issues require attention before the paper can be considered complete.

## Issue 1: Ecological Inference in the Headline Estimate (MAJOR)

The "1,524 ha blocked" figure multiplies county-level WWTP constraint rates by county-level zoned-land estimates. This is ecological inference: it assumes zoned land is distributed across settlements proportionally to the number of WWTPs. In reality, zoned land concentrates in larger settlements (towns, not hamlets). Kerry has 18 RED plants, but most are tiny rural plants (Ballyferriter, Portmagee, Cloghane) serving settlements with minimal or no zoned land, while Tralee and Killarney (where the zoning is) are GREEN. The 83-hectare blocked estimate for Kerry is therefore likely a substantial overestimate.

**Mandated experiment**: Compute a sensitivity analysis that weights blocked hectares by plant size (D-prefix vs A-prefix) rather than treating all plants equally. Report the range.

## Issue 2: Dublin / Ringsend Too Optimistic (MODERATE)

Ringsend WWTP is GREEN in the register, and the paper reports Dublin as "comparatively unconstrained" at 12.5%. The paper does mention the Greater Dublin Drainage delay (Section 5.4), but the framing downplays that: (a) Ringsend is GREEN only after a EUR 550M upgrade that took over a decade; (b) the register explicitly states it covers treatment capacity only, not network capacity; (c) network capacity is the binding constraint in many Dublin areas. Section 5.4 should be rewritten to state that GREEN treatment capacity does not imply unconstrained development, because network bottlenecks are excluded from the register.

**Mandated experiment**: Add an explicit caveat paragraph to Section 5.4 distinguishing treatment capacity (what the register measures) from network capacity (what it does not).

## Issue 3: CSS Color Extraction Spot-Check (VERIFIED OK)

I spot-checked 5 plants against the raw HTML: Ringsend (GREEN, confirmed `color:rgb(0, 128, 0)`), Turvey Cottages (RED, confirmed `color:#C8102E`), Newtown Cottages (RED, confirmed), Palatine/Carlow (AMBER, confirmed `color:#FF8C00`), Abbeydorney/Kerry (RED, confirmed). All 5 match the CSV. The scraper correctly maps the inline CSS colors. No action required.

## Issue 4: Network Capacity Caveat Not Prominent Enough (MODERATE)

The register itself states: "This register provides wastewater treatment capacity information only and does not provide an indication of network capacity." This is mentioned in Section 6.4 as limitation #1 in indirect terms ("county-level aggregation"), but the treatment-vs-network distinction deserves its own limitation item. A development can be blocked by insufficient sewer pipes even when the WWTP is GREEN.

**Mandated experiment**: Add a dedicated limitation item for network exclusion, quoting the register's own disclaimer.

## Issue 5: One-Off Houses / Septic Tanks (MODERATE)

E17 finds that a substantial share of residential planning applications are one-off houses using septic tanks. The paper mentions this in Section 6.4 limitation #6, but it does not quantify the impact. In the counties with the highest constraint rates (Kerry, Donegal), one-off houses dominate residential applications. The blocked-hectare estimate implicitly assumes all zoned land serves WWTP-connected development, but some zoned land (especially in rural areas) may be developed via septic tanks regardless of WWTP status.

**Mandated experiment**: Run E17 to get the actual percentage, and add the figure to the limitation discussion.

## Issue 6: Fingal 33-Hectare-Per-Plant Estimate (MINOR)

The investment priority ranking assigns each constrained Fingal plant 32.5 blocked hectares (97.5 ha / 3 RED plants). But Turvey Cottages, Newtown Cottages, and Oldtown are hamlets with A-prefix registration numbers (design PE likely under 2,000). Claiming each blocks 33 ha of zoned land is implausible -- these are tiny settlements. The equal-distribution-within-county assumption distorts the plant-level priority ranking.

**Mandated experiment**: Add a caveat to the investment priority discussion that plant-level estimates are illustrative, not precise, because the equal-distribution assumption does not hold at plant level.

## Summary of Mandated Experiments

| # | Action | Type |
|---|--------|------|
| R1 | Size-weighted sensitivity analysis for blocked hectares (D-prefix vs A-prefix) | New computation |
| R2 | Rewrite Section 5.4 Dublin caveat re: network vs treatment capacity | Text revision |
| R3 | Add dedicated limitation for network capacity exclusion with register quote | Text revision |
| R4 | Quantify E17 one-off house percentage and add to limitations | Run experiment + text |
| R5 | Add caveat to investment priority discussion re: equal-distribution assumption | Text revision |
