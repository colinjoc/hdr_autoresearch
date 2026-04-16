# Phase 3.5 Signoff Review — LRD vs SHD JR intensity

**Reviewer**: independent Phase 3.5 signoff (did not participate in
Phases 0-2.5 or Phase 2.75). Re-read `paper.md`, `paper_review.md`,
`results.tsv`, `phase_2_75_revisions.py`, `discoveries/opr_bulletin_cases.csv`,
and spot-checked `analysis.py` fresh for this review.
**Date**: 2026-04-16

## Verdict: **NO FURTHER BLOCKING ISSUES**

The Phase 2.75 blind reviewer's R1-R12 mandates have been discharged with
appropriate status labels and the paper's quantitative claims have been
stripped back to what the data can support. Below are the verification
steps that justify this verdict, followed by a list of non-blocking nits
the authors may choose to address at any future revision pass (they are
not gating the signoff).

## Verification

### R1-R12 mandate coverage in results.tsv

| R   | Rows         | Statuses                        | Notes |
|-----|--------------|---------------------------------|-------|
| R1  | R1a, R1b     | KEEP, UNANSWERABLE              | Aligned SHD 16/392 and withdrawn LRD per-permission. |
| R2  | R2a, R2b, R2c| KEEP, KEEP, KEEP                | Lodged-basis both sides + Fisher p. |
| R3  | R3a-R3d      | KEEP × 4                        | ITS single/three-knot + Commercial/SHD placebos. |
| R4  | R4a, R4b     | wide_CI, KEEP                   | `wide_CI` is a documented 4th status (§4.7) for CIs >30pp; acceptable. |
| R5  | R5a, R5b     | UNANSWERABLE, KEEP              | Per-unit withdrawn; SHD units-permitted context only. |
| R6  | R6a-R6c      | KEEP, KEEP, REVERT              | Projection NON-INFORMATIVE; reframe executed. |
| R7  | R7a, R7b     | KEEP × 2                        | Firth OR CI 0.04-28.53; Bayesian CrI straddles zero. |
| R8  | R8a, R8b     | UNANSWERABLE, KEEP              | Bulletins 10/11 hold zero LRD-era cases; honest numerator is 2. |
| R9  | R9a-R9c      | KEEP × 3                        | Commercial/Infrastructure/LRD growth comparison. |
| R10 | R10a-R10c    | KEEP, KEEP, REVERT              | 2/2 LRD 100% loss withdrawn explicitly. |
| R11 | R11a         | KEEP                            | 8-case CSV; zero LRD permissions. |
| R12 | R12          | KEEP                            | Rewrite pointer; paper.md supersedes draft. |

All twelve R-mandates appear, each has at least one row with a defensible
status, and the UNANSWERABLE/REVERT labels are used where the data does
not support a quantitative answer (as Phase 2.75 required).

### Abstract / one-sentence finding

- Line 5: "The per-permission LRD judicial-review (JR) rate cannot yet be
  cleanly estimated from public data; the substantive-LRD-outcome sample
  to end-2024 is n=2 cases..." — matches the Phase 2.75 demanded honest
  framing.
- Line 11 (Abstract body): "The answer is that the comparison **cannot
  yet be defensibly made**" — unambiguous.
- Line 15 (Abstract close): "the reform's LRD-specific JR effect is below
  the detection floor of currently-available data." — frames null result
  as underpowered, not established.

The abstract never says "LRD is not lower than SHD" as a positive claim;
never smuggles back the 6.4%-vs-8.6% comparison; never labels a regime
effect as detectable.

### C1 "SHD 6.4% vs LRD 8.6%, p=0.51" withdrawal

The literal strings "6.4% vs 8.6%", "p=0.51", and "16/250 = 6.4%" appear
in `paper.md` only within explicit withdrawal sentences (lines 59, 61,
67, 127, 171). No sentence presents the comparison affirmatively. §4.1
explicitly: "**What survived from the draft headline**: nothing as a
comparative claim."

### C8 "LRD 100% state loss" withdrawal

"100% LRD state-loss" appears only inside withdrawal sentences (lines 72,
134, 169). Line 72 explicitly demonstrates the figure collapses under
every defensible concession treatment (exclude → 0/0 undefined; re-weight
to 33.3% baseline → undefined). Not used as a headline.

### Phase B reframe (C5 / R6c)

- §4.6 titled "Phase B projection — recast as monitoring framework (R6)"
- §5 titled "Phase B — LRD monitoring framework (not projection)"
- "2028" appears only in a negative context: "does not support
  point-estimate claims like '2028 hit year'" (line 90) and "its 'year
  2028' column is flagged NON-INFORMATIVE by R6c and must not be quoted
  as a forecast" (line 107).
- Three triggers (A: 2025 ABP report; B: DHLGH release; C: 2027 ABP
  report) replace the old year-of-target forecasting.

No surviving point-estimate year forecast. ✓

### R4 CI coverage

Every primary rate that the paper quotes as a point estimate carries a
Wilson or Clopper-Pearson CI:

- Line 11: 4.08% [2.53-6.53%]; 8.62% [4.75-15.14%]
- Line 19: 14/16 [61.7-98.5%]
- Line 61: 4.08% [2.53-6.53%]
- Line 71: 87.5% [61.7%, 98.5%]
- Line 86: 8.93% [6.5-12.1%] vs 8.62% [4.8-15.1%]
- Line 90: 7/79 [4.36%, 17.18%]; target [2.18%, 8.59%]

Growth percentages (58%, 133%, 150%, 850%) are raw year-over-year
counts with fully-observed numerators and denominators at annual
resolution; they are not effect estimates and CI is not required for
this use.

R4a's wide_CI summary in `results.tsv` enumerates every percentage that
could not be quoted tightly (including 2/2 LRD loss, 7/79 LRD rate,
E21_LRD_2023 and 2024, Dublin/apartment descriptors). Those percentages
appear in the paper qualitatively, not as point estimates, consistent
with R4's acceptance criterion.

### §Caveats concurrent-trend and data-limit risks

§7 enumerates C1 through C11 line by line. The three concurrent
interventions (Heather Hill, Planning and Environment List, 2024
concession spike) are each named and their sign matched to the
hypothesised LRD effect (§6 line 119: "Each of these has the same sign
as the hypothesised LRD effect ... none of them can be separated from a
putative regime effect"). Data limits (DHLGH LA-level data absent,
OPR Bulletins narrative-only, PDA 2024 only signalled) are enumerated
in §7 "Further limitations".

### §Change log R1→R12 map

§9 presents a complete 12-row table mapping each mandate to its paper
impact. Matches the rows observed in `results.tsv`.

### Smuggled-claim scan

I searched `paper.md` for the following prohibited patterns:

- `regime effect is detectable` → not present (only "below the detection
  floor", "cannot be separated", "cannot be isolated")
- `LRD rate is not lower` → not present in any affirmative form
- Any positive `p-value` claim of regime equivalence → only the §4.5
  lodged-basis Fisher p=1.00, immediately followed by "This is **not**
  evidence that the two regimes are equal" — acceptable.

### Numeric reproducibility spot-check

- `SHD_DECISIONS` in `phase_2_75_revisions.py` sum 2018-2021 = 60+82+137+113
  = 392 ✓ (matches paper.md line 61).
- `LRD_CONCLUDED` sum 2022-2024 = 1+36+79 = 116 ✓ (matches paper.md line
  11).
- `discoveries/opr_bulletin_cases.csv` has 8 rows: 1 SHD, 0 LRD, 7 other
  — matches §2 "Zero of the 8 are LRD-era permissions" and R11a row.
- Firth-adjusted 15/18 = 0.833; 3/4 = 0.750 ✓ (paper.md line 76).

## Non-blocking nits (authors may address at any time)

1. §4.2 line 72 mentions "pre-2022 baseline concession share of 33.3%"
   without an inline CI. The underlying fraction is 49/147, Wilson
   [26.2%, 41.3%]. This is used as a sensitivity-reweight parameter, not
   a primary estimate, so it is not strictly in scope of R4 — but for
   uniformity the authors could append `[Wilson 26.2-41.3%]`.
2. §4.3 Firth/Bayesian rates 83.3% and 75.0% are quoted inline without a
   rate-level CI next to each; the adjacent odds-ratio and credible
   interval both straddle neutrality, so the conclusion is intact, but a
   per-rate CI (15/18 Wilson [60.8-94.2%]; 3/4 Wilson [30.1-95.4%])
   would complete the R4 uniformity.
3. R4a's status string `wide_CI` is a valid 4th category documented in
   §4.7, but is not strictly one of {KEEP, REVERT, UNANSWERABLE}. This is
   an acceptable extension and is clearly explained. Mentioned only for
   completeness.
4. The change-log entry for R4 collapses nine percentages under "wide-CI
   qualitative-only"; the paper could optionally list them. Not
   required.

None of these nits affect whether the paper can be posted. The signoff
stands.

## Signoff

**NO FURTHER BLOCKING ISSUES**

The paper is ready to be posted to the website summary with the
understanding that it is a "data-cannot-yet-answer" methodology and
monitoring report, not a comparative effect estimate. A follow-up
review is appropriate once:

- The 2027 ABP Annual Report is published (Trigger C), enabling
  substantively-decided LRD outcomes to exceed 20.
- DHLGH releases LA-level LRD permission counts for 2022-2024
  (Trigger B), enabling per-permission denominator alignment.

Until then, the honest headline from this paper is the one the paper
states: the LRD-vs-SHD per-permission JR-rate comparison is not yet
testable, and any point estimate that claims otherwise is an artefact
of denominator mismatch.
