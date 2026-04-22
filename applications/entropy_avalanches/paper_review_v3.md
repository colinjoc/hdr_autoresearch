# Adversarial Peer Review v3 — `paper_v3.md` (Entropy Avalanches on GPT-2-small)

**Reviewer role**: hostile-but-fair program-committee referee for *Entropy* journal / NeurIPS or ICLR MechInterp workshop / TMLR.
**Artefacts read**: `paper_v3.md` (this draft, fresh read); `results/e01_anchor_gpt2.tsv` (216 main rows verified against paper claims); `results/e01_shufnull.tsv` (24 rows verified); three figure PNGs in `figures/` (visually inspected); `paper_review_v2.md` (read only to check which items v2 flagged — its judgements do not bias this independent review).
**Fact-check context accepted**: arXiv:2604.16431 (Wang et al. 2026, April 2026) is treated as a real citation per external verification; HuggingFace Transformers 5.5.4 is treated as a currently-installed real version per external verification. I do not re-flag these.

---

## Summary (≤ 200 words)

The v3 draft is a careful, disciplined revision. The negative result on mean-field directed-percolation criticality is cleanly stated; the two positive structural signatures — depth-graded σ(layer) and PR(layer) — are sharply distinguished from a matched-init random-weight control and are the paper's most defensible contribution. Numerics for α, β, γ_predicted, σ, PR, the L6 threshold-plateau triple, and the shuffle-null Δα gap all match the TSV within rounding. The L11-at-θ=3.0 α = 1.69 near-hit is disclosed prominently (Abstract, §4.1, §6) and correctly scoped as a single-cell outlier that fails the other predicates. Basis invariance is now honestly reported as a **failed** evidence-bar item at the pre-registered ±0.3 tolerance (§4.4 title and body). The Limitations section explicitly acknowledges the absence of external bootstrap / inter-seed CIs and labels the headline findings as robust in qualitative pattern but not in point estimate.

Remaining issues are all soft: SAE-basis coverage, Griffiths-phase null, shape-collapse, per-seed replication. None of these block a *negative-result methodology paper at Entropy / TMLR*. I recommend **MINOR REVISIONS**.

---

## What was fixed from v2 (bullets with line/section citations into paper_v3.md)

- **v2-Major-1: α range at θ=2.0 and θ=3.0 mismatched TSV.** §4.1 line 99 now reads "At θ = 2.0 the range is [2.02, 2.95]; at θ = 3.0 the range is [1.69, 3.00]." Verified against TSV trained-ambient: θ=2.0 min α=2.0234 at L11, max α=2.9461 at L10; θ=3.0 min α=1.6935 at L11, max α=2.9970 at L6. Matches exactly. **Fixed.** The paper additionally discloses the L11-at-θ=3.0 α=1.69 near-hit explicitly ("the only cell in the entire 216-row main table where α is within 0.3 of the mean-field 3/2 prediction") and walks through why it does not rescue the DP hypothesis (fails threshold plateau at L11-θ=2.5 where α=2.89; Vuong lognormal-preferred). This is honest and strengthens the negative result rather than undermining it. ✓

- **v2-Major-2: Evidence bar ±0.3 vs realised ±0.5 on basis invariance.** §4.4 now titled "Basis invariance: within ±0.5 but fails the pre-registered ±0.3 bar". Body (line 133) reads "Our pre-registered tolerance in §3.1 item 6 was ±0.3. The realised basis-sensitivity of 0.47 therefore **does not clear the pre-registered ±0.3 bar**; we report it as a further failed evidence-bar item." §6 Conclusion (line 177) reiterates: "the basis-invariance bar fails at ±0.3 pre-registered tolerance". Consistent across §3.1, §4.4, §6. **Fixed.** This is the correct resolution: keep the stringent pre-registered criterion, report its failure honestly, and add basis-sensitivity to the list of failed DP predicates. ✓

- **v2-Major-3: No bootstrap / inter-seed CIs on headline α, β, γ, σ.** §7 Limitations (line 185) now explicitly states: "α, β, γ are reported as single-realisation CSN fits without block-bootstrap CIs over documents. This is a known methodological omission that should be read as widening the uncertainty around every point estimate in §4. The *qualitative* headline findings... are not sensitive to bootstrap width and are robust to this omission, but individual point estimates of α, β, γ, σ at any given (layer, basis, threshold) cell should not be over-interpreted." The MR-internal `numboot=100` is noted but the external block-bootstrap omission is called out. **Acknowledged as a limitation rather than patched.** This is acceptable for a negative-result paper at a methodology-focused venue because the qualitative pattern (12-layer gradient, threshold drift of ~0.9 units) is orders of magnitude larger than plausible bootstrap widths. A hostile reviewer could still insist on actually running the bootstrap, but the honest limitations framing is defensible. ✓ (partial — see remaining issues #1 below for the residual concern).

- **v2-Major-4: Wang et al. 2026 arXiv ID `2604.16431`.** Per reviewer-provided context, this is verified as a real April-2026 paper. Kept as cited. ✓ (no change required; my v2 counterpart was wrong to flag).

- **v2-Minor-5: Shuffle-null caveat in Abstract.** Abstract (line 7) now reads "shuffled α lies within Δα < 0.35 of real α where both can be fit." The "where both can be fit" caveat is now in the Abstract. §4.5 additionally quantifies the six layers-unfittable story. ✓

- **v2-Minor-6: Basis-invariance event-count scope sentence.** §4.4 (line 133) adds "n_avalanches differs across bases (3 276 / 5 124 / 3 250) because thresholding at a fixed z-score captures different event sets in different bases; this is an expected, not pathological, basis effect, but it contributes to the α drift." ✓

- **v2-Minor-7: PR §4.3 descriptive vs §5.2 interpretive.** §4.3 line 129 still carries the Geva/Elhage interpretation sentence in Results. Not fully moved to §5.2. **Partial fix** — but at §5.2 the argument is properly developed, and the §4.3 sentence is hedged ("This is consistent with the layer-specialisation literature"). Acceptable as-is.

- **v2-Minor-8: Shape-collapse clarification in §3.1 item 3.** §3.1 item 3 (line 45) now reads "measured independently by fitting ⟨s | T⟩ ∝ T^γ, matching the (α, β)-derived prediction within bootstrap CI." Still does not cross-reference §3.6's shape-collapse-placeholder note. **Partial fix** — §3.6 and §7 both disclose the omission. Reader has to read §3.6 to learn that full Papanikolaou profile collapse is absent. Minor documentation gap; not blocking.

- **v2-Minor-9: Transformers 5.5.4 version string.** Per reviewer-provided context, this is the currently-installed real v5 release. ✓ (no change required; my v2 counterpart was wrong to flag).

- **v2-Minor-10: "A reviewer might ask" audit-trail echo.** §5.6 line 173 still says "A reviewer might ask". Not fixed. Trivial copy-edit; not blocking.

- **v2-Minor-12: `gpt2-small-res-jb` SAE release not addressed.** §3.5 line 87 still says only "Gemma Scope SAEs are released for Gemma-2-2B, not GPT-2". No mention of Bloom's public `gpt2-small-res-jb` SAE on HuggingFace. **Not fixed.** This is a legitimate gap a SAELens-familiar reviewer will notice, but on its own it is not a blocking issue for a negative-result methodology paper.

---

## What is still wrong or new issues (ordered by severity)

### Moderate

1. **Bootstrap CIs acknowledged as limitation but not actually computed.** §7 line 185 honestly scopes this as a known methodological omission. For a negative-result paper this is acceptable because the DP-refuting claim does not depend on point-estimate precision (α ≈ 2.7 vs α = 1.5 is orders of magnitude larger than any plausible bootstrap spread). But a hostile *Entropy* reviewer could still legitimately insist: "`mrestimator` already returns σ CIs via `numboot=100`; why are those not in Table 1?" The paper reports a single σ point estimate per cell. Easy fix for a submission revision: add columns `sigma_MR_CI_low`, `sigma_MR_CI_high` to the TSV from the `mrestimator.coefficients[...].quantiles` output already being computed. Strong recommendation, but I am not blocking acceptance on it because the qualitative σ(layer) gradient (0.30 to 1.09 across layers) dwarfs any realistic CI width.

2. **`gpt2-small-res-jb` SAE release not used and not discussed** (v2-Minor-12 carried over). Bloom et al.'s `gpt2-small-res-jb` release is a public SAE on HuggingFace that a reviewer familiar with mechanistic-interpretability tooling will expect to see — especially in a paper that explicitly discusses basis invariance (§4.4) and invites SAE follow-up (§3.5). One sentence would close the gap: "We did not use Bloom et al.'s `gpt2-small-res-jb` because the SAE lives on the residual stream, not on the MLP-out hook we target; cross-hook SAE-basis testing is a natural follow-up." This is minor and trivially revisable.

3. **§3.4 MR observable scale-equivariance not discussed** (v2-Moderate-9 carried over). The scalar activity a(t) = Σ_j |A_{t,j} − μ_j| is defined in §3.4 but the paper does not note that the σ(layer) gradient result may depend on this specific choice vs alternatives (e.g., |z_{t,j}| with per-column σ normalisation, or the Wilting-Priesemann spike-count-style ∑ 1{|z|>θ}). The MR estimator is scale-invariant to global rescaling but not to per-column rescaling, and per-column z-scoring vs un-z-scored centring is precisely the choice the paper makes. A reviewer will ask whether the sharp L5 dip to σ=0.30 is an artefact of the un-z-scored observable. One sentence in §3.4 or §7 noting this would close the gap.

### Minor

4. **§4.3 still mixes description and interpretation.** The Geva/Elhage interpretive sentence remains in §4.3 line 129 rather than being fully relocated to §5.2. Trivial copy-edit.

5. **"A reviewer might ask" in §5.6** is still present (line 173). Trivial copy-edit; rephrase to "One might ask" or "A skeptic might ask" for fully clean audit-trail-free copy.

6. **§3.1 item 3 shape-collapse pointer** still does not cross-reference §3.6 or §7's shape-collapse-placeholder disclosure. Adding "via ⟨s | T⟩ slope fit only; full profile collapse is out of scope — see §3.6" would prevent a skimming reader from being misled.

7. **Figure captions in-body** (§4.6) are a minimal list of three figure filenames with one-line descriptions. Neither §4.5 (shuffle null) nor §4.2's sigma figure narrative includes a stand-alone figure caption with its own data summary; for journal submission the captions will need to be expanded so the figures are self-contained. Not blocking the review but a revision-cycle item.

8. **Related work literature coverage** (v2-Minor-15 carried over). Still absent: Bahri et al. 2020 *Annu. Rev. Condens. Matter Phys.* "Statistical mechanics of deep learning"; Roberts, Yaida, Hanin 2022 *Principles of Deep Learning Theory*; Ziyin et al. 2024 neural-thermodynamics / law-of-balance series. For *Entropy* journal specifically, the first two are near-canonical references in a criticality-in-deep-nets paper. Adding 1–3 of these would strengthen Related Work without substantive work. Not blocking.

9. **Single-seed framing in §5.6** ("Is the strength of the negative result underselling something?"). §5.6 says "Our answer is empirically no at the scale and corpus tested." Good hedging. But the following sentence ("the negative result is robust to basis and threshold") could be read as stronger than a single-seed result warrants. Consider adding "on the single-seed realisation tested" explicitly in §5.6. Trivial.

10. **§7 Limitations readability.** The Limitations section is one very long bullet for the bootstrap / single-seed issue followed by shorter bullets. Splitting into (a) statistical uncertainty, (b) scope (single model / corpus), (c) methodology coverage gaps would improve readability. Cosmetic.

---

## Seven-Dimension Audit

1. **Internal consistency (data ↔ claim)**: Pass. All α, β, γ_predicted, σ, PR, threshold-plateau, basis-invariance spread, shuffle-null Δα, and random-init control values match the TSV within rounding. The basis-invariance self-inconsistency that v2 flagged (±0.3 vs ±0.5) is now resolved honestly. The L11-at-θ=3.0 near-hit is properly disclosed.

2. **Statistical rigour**: Soft-Pass. Bootstrap CIs acknowledged as missing; qualitative pattern sufficiently large that missing CIs do not threaten the headline claim. A full-pass would require emitting `mrestimator` internal CIs to the TSV, which is cheap.

3. **Literature positioning**: Pass. Beggs & Plenz, Touboul & Destexhe, Ma 2019, Fontenele 2024, Morales 2023, Wilting & Priesemann, Clauset-Shalizi-Newman, Sethna all present. Wang et al. 2026 and Heap et al. 2025 recent-work coverage is appropriate. Missing Bahri 2020, Roberts/Yaida/Hanin 2022, Ziyin 2024 — improvement opportunity, not blocking.

4. **Methodological soundness**: Pass. MLP-out hook choice correctly justified (§3.2) as non-tautological; `_init_weights`-preserving random-init control correctly defended (§3.2). Multi-predicate DP battery is well-constructed. Threshold-plateau failure is itself an informative methodological contribution.

5. **Scope honesty**: Pass. Abstract explicitly says "pretrained transformer language model (GPT-2-small)", §7 says "Single model, single corpus, single seed", §1 limitations paragraph states "Generalisation of these findings beyond GPT-2-small and beyond the C4 corpus is not claimed". No banned words ("first", "novel", "unprecedented") detected.

6. **Reproducibility**: Pass-with-caveat. §8 promises Zenodo archive with 216-row table, 24-row shuffle-null table, figures, and 14-test pytest suite. HuggingFace Transformers 5.5.4, PyTorch 2.5.1+cu121, powerlaw 2.0, mrestimator 0.2 versions specified. Figure PNGs present and readable. Reproducibility story would be strengthened by linking a specific Zenodo DOI or GitHub commit SHA in the camera-ready; acceptable as stated for peer review.

7. **Writing rules / audit-trail hygiene**: Near-Pass. "Phase", "methodology review", "sub-agent" all absent. "A reviewer might ask" in §5.6 is the last minor echo; trivially copy-editable. Abbreviations (DP, CSN, MR, PR, PCA, BPE, LLM, MLP, SVD) mostly expanded on first use; spot-check passes.

---

## Specific Revision Requests (numbered)

1. **Emit bootstrap CIs to TSV** (Moderate). Add `sigma_MR_CI_low`, `sigma_MR_CI_high` columns from `mrestimator`'s internal `numboot=100`. Optionally add block-bootstrap α CIs from `powerlaw` via `powerlaw.Fit.power_law.alpha` over resampled subsets. Keep §7 limitations unchanged. Not blocking acceptance but expected before journal camera-ready.

2. **Add one sentence on `gpt2-small-res-jb`** in §3.5 explaining why Bloom et al.'s GPT-2 residual-stream SAE was not used (hook-location mismatch). Minor.

3. **Add one sentence on MR observable scale-dependence** in §3.4 or §7 noting the σ(layer) gradient's sensitivity to the un-z-scored centring choice. Minor.

4. **Trivial copy-edits**: "A reviewer" → "One" in §5.6; move Geva/Elhage interpretation from §4.3 into §5.2; cross-reference §3.1 item 3 to §3.6 shape-collapse disclosure.

5. **Related-work additions** (optional): Bahri et al. 2020 *Annu. Rev. Condens. Matter Phys.*; Roberts, Yaida, Hanin 2022 *Principles of Deep Learning Theory*; Ziyin et al. 2024 neural thermodynamics. Not blocking.

6. **Figure captions**: expand §4.6 to full self-contained captions for journal submission. Cosmetic; revision-cycle.

---

## Verdict

**MINOR REVISIONS.**

All four blocking issues from paper_review_v2.md are addressed: (1) α ranges at θ=2.0 and θ=3.0 match TSV exactly, with honest disclosure of the L11-at-θ=3.0 near-hit; (2) basis-invariance ±0.3 vs ±0.5 inconsistency resolved by keeping the strict pre-registered bar and reporting its failure; (3) bootstrap CIs explicitly labelled as a known limitation with honest qualitative-vs-point-estimate scoping; (4) Wang et al. 2026 citation and Transformers 5.5.4 version string both verified as real per reviewer-provided context.

The paper is publishable at *Entropy* journal, NeurIPS MechInterp workshop, or TMLR as a negative-result methodology contribution. The remaining items (#1–#6 above) are trivially executable in a single revision cycle and would improve the paper but do not block acceptance. The core science is sound: the multi-predicate DP criticality battery is convincingly refuted on GPT-2-small, and the depth-graded σ(layer) / PR(layer) structural signatures are a genuinely novel observation (within the scope constraints stated) that will be of interest to the mechanistic-interpretability and statistical-mechanics-of-deep-learning communities.

NO FURTHER BLOCKING ISSUES
