# Phase 3.5 Paper Review (v6) — qec_drift_tracking

## 1. Point-by-point response to v5 reviewer's five minor items

**M1 (strip/CI-ify the bare "1.65×" informativeness ratio).** PARTIAL. The abstract now explicitly says "no headline quantitative ratio is claimed" and §1.2 "Does not claim" lists "Any quantitative per-shot likelihood-informativeness ratio," and §3.2 documents the sign-flip with Figure 3. However, the §1.2 "Does claim" bullet still reads "A quantitative informativeness ratio: pair-correlation likelihood is 1.65× more informative per shot…", and §7 Conclusions still lists "the measured per-shot informativeness ratio (1.65×)" as a concrete contribution. These two sentences directly contradict the abstract's retraction and §1.2's own "Does not claim" bullet. This is a residual inconsistency that needs a copy-edit (strike the 1.65× line from §1.2 "Does claim" and from §7).

**M2 (3-seed bootstrap framing).** ADDRESSED. The abstract now reads "N = 3 replicates, reported with a 1000-resample bootstrap which is the in-seed sampling distribution and not the between-seed one"; §3.3 adds a "CI interpretation" paragraph making the same point and references Figure 2's min–max envelope; and §4.2 lists ≥10-seed work as an open item.

**M3 (cell indistinguishability scope lifted into §1.2).** ADDRESSED. §1.2 "Does not claim" now explicitly includes a bold bullet "That any drift-regime-specific claim can be made from this data," naming the 4-cell collapse and the prior-dominance explanation.

**M4 (justify the 5% null-test threshold).** ADDRESSED. §2.1 now gives a two-part justification: (a) a measured no-filter noise floor of ~3% gap-equivalent movement per 5000 shots obtained from a prior-at-truth control run, yielding 5% ≈ 1.7× the noise floor; (b) a qualitative argument that below 5% Laplace-prior-shrinkage could masquerade as filtering. 14% sits well above both bounds.

**M5 (figures).** ADDRESSED. Three figures are now referenced: Figure 1 (prior-migration trajectory, §3.3), Figure 2 (MSE vs T with min–max spread, §3.3), Figure 3 (log-L gap vs batch, §3.2). All three map directly onto v5 §8's requested list.

## 2. Housekeeping items from v5 review

- **Test-count reconciliation (abstract vs §2.5).** ADDRESSED. Abstract now says "25-test pytest regression suite (24 passing, 1 documented-scope skip)"; §2.5 says "24 passing tests + 1 documented-scope skip (25 collected)." Consistent.
- **Version-label drift (v4/v5 confusion).** PARTIAL. The header editorial note now reads "Phase 3 draft v5 … with v5 minor-revision fixes applied"; §6 is titled "Retraction table (v1–v3)"; however the retraction table's header column still reads "Status in v4," and §1.3 still calls this "the fourth draft," §6 has a row "Calibrated SMC beats baselines on MSE (v3 implied) — RETRACTED — SW-MLE wins on synthetic with 3-seed bootstrap." Internal version arithmetic is inconsistent but not scientifically load-bearing; trivial copy-edit.
- **§5 "Related work" inlined vs "Per v3 §5. Unchanged."** ADDRESSED. §5 is now a full four-paragraph inlined related-work section (online drift inference for QEC, SMC methodology, production adaptive decoders, QEC simulation tooling, Willow data).
- **Repository URL/DOI/commit-hash availability.** PARTIAL. The Data-and-code-availability paragraph now explicitly states "A Zenodo DOI and Git commit hash will be minted at submission; in the submission cover letter we commit to pre-filing these before peer review begins." This is an acceptable commit rather than a concrete binding — editors at SciPost will require the actual identifiers before publication, but the policy is now stated. No Python version / OS / seed list / hardware note is added (v5 §9 flagged all four); that metadata remains absent.
- **Orphan Willow citation status.** ADDRESSED. §5 now has a dedicated "Willow data" paragraph explicitly disclaiming any Willow-based empirical result in this draft and stating the loader is retained for the follow-up paper. The citation is no longer orphaned.
- **"Retracted" wording for internal drafts (v5 §6 caveat).** ADDRESSED. The Data-and-code-availability paragraph now clarifies: "'retracted' here means 'explicitly withdrawn from the submission record' rather than 'retracted from a published journal.'"

## 3. Any new blocking concerns introduced by the revisions?

No new blocking concerns. Three new non-blocking observations:

1. The 1.65× residue in §1.2 "Does claim" and §7 directly contradicts the abstract and §1.2 "Does not claim." This is a self-inconsistency that the v5 reviewer flagged in effect as M1, and v6 did not finish the cleanup. Copy-edit-only fix.
2. §2.1's 3%-no-filter-noise-floor number is asserted as measured but the measurement (prior-at-truth control run) is not shown as a figure or table. Acceptable for a methodology paper but could be stronger.
3. §4.3 "Venue" paragraph is still present ("SciPost Physics Codebases is the cleanest fit…"); v5 asked to remove editorial meta-commentary from the published version. Not removed. Minor copy-edit.

None of these block acceptance.

## 4. Figures

Based on the in-text descriptions only:

- **Figure 1** (prior-migration trajectory, three seeds, posterior mean from 1e-5 prior toward 1e-3 truth, monotone up to T ≈ 3000 then levelling off). Appropriate and adequate — this is the v5 §8 item-1 request, and the description covers the three-seed spread and the 14%-gap-closed endpoint. Missing explicit overlay of the naive-SMC and prior-at-truth control traces requested in v5 §8.1, but the core content is present.
- **Figure 2** (MSE vs T for SMC, SW-MLE, CP-lstsq; min–max shaded across 3 seeds; ordering preserved at every T and seed). Appropriate and adequate — directly matches v5 §8 item 2, and the min–max envelope is the correct honest visualisation for N = 3.
- **Figure 3** (log-L gap vs batch, pair-correlation vs independent-Bernoulli, 10×30 fixture, seed 42, T=2000 trajectory, pair-correlation crashes negative from batch ≥ 200). Appropriate and adequate — demonstrates the sign-flip caveat that replaces the withdrawn 1.65× ratio, and justifies the 1000-shot batch choice by showing per-shot measurements are unreliable below ~200 batch size. This figure does more work than v5 §8 item 3 asked for: it is now the evidentiary backbone of the M1 withdrawal.

All three captions are self-sufficient, the x/y axes are named, the seed and fixture are stated, and each figure is cross-referenced from the section that uses its conclusion. Adequate for SciPost Codebases.

## 5. Verdict

**MINOR REVISIONS** — with all outstanding items trivially copy-editable (no new experiments, no structural rewrites, no re-analysis).

Specifically:
- Strike "1.65×" from §1.2 "Does claim" bullet 3 and from §7 Conclusions.
- Change §6 table header "Status in v4" and §1.3 "the fourth draft" to be consistent with v5/v6 labelling.
- Remove the §4.3 "Venue" paragraph from the submission copy.
- Before SciPost submission, mint and insert the Zenodo DOI and Git commit hash (paper already commits to doing this).
- Optionally add Python version, OS, seed list ([0, 1, 2]), hardware note to Data-and-code availability.

None of these require new runs or figure regeneration. The scientific content, the null-hypothesis-test contribution, the Laplace-smoothing recipe, the honest negative result, the three figures, and the retraction table are all in place and correctly scoped. The v5 reviewer's five blocking items M1–M5 are substantively addressed (M1 is addressed in spirit but with a copy-edit residue), and all major housekeeping is done.

## 6. Signoff

NO FURTHER BLOCKING ISSUES
