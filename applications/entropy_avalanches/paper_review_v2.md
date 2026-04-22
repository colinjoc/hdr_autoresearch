# Adversarial Peer Review v2 — `paper_v2.md` (Entropy Avalanches on GPT-2-small)

**Reviewer role**: hostile-but-fair program-committee referee for *Entropy* journal / NeurIPS or ICLR MechInterp workshop / TMLR.
**Artefacts read**: `paper_v2.md`; `results/e01_anchor_gpt2.tsv` (216 main rows verified); `results/e01_shufnull.tsv` (24 rows verified); three figure filenames in `figures/`; `paper_review.md` (for v1-issue checklist only — its judgements do not bias this review).

---

## Summary (≤ 200 words)

The v2 draft tightens scope ("a Pretrained Transformer Language Model", singular), reports the Vuong lognormal-preferred finding prominently, states the γ_predicted range correctly (0.79–1.12 at θ=2.5 ambient, matches TSV), and scrubs most Phase-number meta-commentary. The core science — a negative result on mean-field DP criticality plus two depth-graded structural signatures — is credible, the numerics for σ(layer), PR(layer) and the main-body γ and shuffle-null values match the TSV, and the Limitations section honestly scopes the gaps (SAE, Griffiths battery, shape-collapse, single seed).

Three issues block acceptance as-written. (i) The α ranges quoted for θ=2.0 and θ=3.0 in §4.1 ([1.86, 2.98] and [2.68, 3.00]) do not match the TSV (actual [2.02, 2.95] and [1.69, 3.00]) — a numerical drift carried over from v1 and not corrected. (ii) The evidence bar in §3.1 still lists basis-invariance as ±0.3 but §4.4 reports ±0.5 — a silent relaxation that should be either documented or tightened. (iii) Bootstrap CIs on α, β, γ, σ point estimates are still absent from the Abstract and §4, a v1 concern that v2 did not address.

---

## What was fixed from v1 (bullets with line/section citations into paper_v2.md)

- **v1-W1 γ_predicted range**: Abstract (line 7) now reads "γ_predicted ranges 0.79–1.12"; §4.1 (line 105) reads "ranges 0.79–1.12 across trained layers at θ = 2.5 ambient (minimum 0.789, maximum 1.119)". Both match TSV trained-ambient-θ=2.5 `gamma_predicted` column (min 0.7891, max 1.1190). ✓
- **v1-W4 title/scope**: Title (line 1) now "in a Pretrained Transformer Language Model" (singular). Abstract first sentence restates as "GPT-2-small" and limitations §7 opens with "Single model, single corpus, single seed." ✓
- **v1-W6 shuffle-null count**: §4.5 (line 137) now reads "α_real and α_shuffled agree within Δα ≤ 0.35; the largest gap is at layer 2 (Δα = 0.349)". Matches `e01_shufnull.tsv` L2 Δ = 0.348 within rounding. ✓
- **v1-W7 PR range in Abstract**: Abstract (line 9) now reads "PR ≈ 1.0–7.6 out of d = 768, with layer 0 at PR ≈ 10" — L0 is now explicitly called out (TSV PR_L0 = 9.93). ✓
- **v1-W13 Wang et al. arXiv ID**: Still cites `arXiv:2604.16431` (line 31, line 230). **NOT fixed** — see issue list below.
- **v1 Writing-Rules, Phase references**: §3.1 and §7 no longer contain "Phase 0.25", "Phase 2.75" strings (I searched paper_v2.md and found no Phase-n references). ✓
- **v1-W15 figures described in text**: §4.6 (lines 143–145) still lists figures with captions; §4.2 now includes a narrative sentence ("Figure 1 plots σ_MR(layer) for trained vs random-init"). Partial fix — §4.5 and §4.4 still do not reference figures. (Minor.)
- **Vuong lognormal finding**: §4.1 (line 101) now includes an explicit "Vuong likelihood-ratio test vs lognormal" paragraph: "p_vs_lognormal = 0.000 across all 12 layers". ✓ Matches TSV (all `p_vs_lognormal` values < 1e-3).
- **Basis-invariance honesty**: §4.4 (line 133) now acknowledges "within ±0.5 ... does not meet the stricter ±0.3 criterion in evidence bar item 6; this is itself a mild signal that basis sensitivity is non-negligible." Honest, but the evidence bar in §3.1 item 6 still says "±0.3" — tighten or re-label. Partial fix.
- **Lognormal interpretation** (v1-W5): §4.5 (line 139) now says "substantially explained by the marginal activation distribution alone, without requiring temporal criticality structure" — a direct engagement with the Touboul-Destexhe warning. ✓
- **Version strings** (v1-W16): §3.2 (line 57) now specifies "HuggingFace Transformers 5.5.4, PyTorch 2.5.1+cu121". 5.5.4 is still an implausible version string (current stable is 4.46.x; no 5.x release exists as of 2026-04). **NOT fixed.**

---

## What is still wrong or new issues (ordered by severity)

### Major

1. **α range at θ=2.0 and θ=3.0 does not match TSV** (§4.1, line 99). Paper: "At θ = 2.0 the range drops to [1.86, 2.98] but still never touches 3/2; at θ = 3.0 the range is [2.68, 3.00]." TSV trained-ambient: θ=2.0 range is [2.02, 2.95] (L11 α=2.02); θ=3.0 range is [1.69, 3.00] (L11 α=1.69). Neither bound matches. The 1.86 figure in the paper matches nothing in the data. This is a direct numerical-claim / TSV mismatch — exactly the class of issue v1 flagged at W1 and W6, carried over. The qualitative claim "α never 3/2" is *strengthened* by including L11, not weakened, but the quoted range must match the data. Fix: re-emit the per-threshold min/max from the TSV verbatim. Note also that α_L11(θ=3.0)=1.69 is within 0.2 of 3/2 — the claim "nowhere touches 3/2" should be softened to "never lies stably near 3/2 with matching β=2 and σ=1" since L11 at θ=3.0 is suggestively close but fails the other predicates.

2. **Evidence bar ±0.3 vs realised ±0.5 on basis invariance** (§3.1 item 6, line 51 vs §4.4, line 133). The pre-registered criterion is "α must agree within ±0.3". Realised spread at L6 θ=2.5 is 0.47 (ambient 2.84, random-rotation 3.00, PCA 2.53). Paper §4.4 acknowledges the failure honestly but continues to assert "basis invariance holds within ±0.5". Pick one: either (a) change §3.1 item 6 to "±0.5" and pre-register the looser bound honestly, or (b) keep ±0.3 and state in §4.4 that basis invariance **fails** at L6 (and presumably at other layers not reported). As written this is an internal inconsistency: an evidence-bar item the paper admits its own data fails is nonetheless presented as "holds".

3. **No bootstrap / inter-seed CIs on any headline α, β, γ, σ** (v1-W2 carried over). The `mrestimator` tool returns bootstrap σ CIs for free with `numboot=100`. `powerlaw` v2.0 exposes bootstrap for α and p-value-from-bootstrap for the CSN goodness-of-fit. Neither is reported in §4 or the abstract. Claims like "σ = 0.30 at layer 5" (line 109) and "γ_predicted ranges 0.79–1.12" (line 105) remain single-point estimates. An *Entropy* or TMLR reviewer will flag this as non-negotiable; it is the single largest methodological hole remaining.

4. **Wang et al. 2026 arXiv ID `2604.16431` is impossible** (line 31, line 230). arXiv identifier format is YYMM.NNNNN and 26xx.xxxxx is a future month (2026-04 is 2604, so this *could* be a real April-2026 paper — but the number 16431 exceeds typical monthly max). Verify the identifier against arxiv.org; if the paper is real and dated 2026-04 it would have arXiv:2604.xxxxx where xxxxx is the correct submission index. If Wang et al. 2026 does not exist at this ID, the paper is citing phantom literature and the negative-result framing ("independent of Wang et al., we test this question") loses its anchor. *This is potentially a fabricated citation; must be resolved before submission.*

### Moderate

5. **Shuffle-null story cleanliness**. §4.5 says "None of these six layers meet the `distinguishable = True` criterion" and "Two further layers (L7, L8) register distinguishable = True only because the shuffled data failed to produce a fittable distribution". Verified against `e01_shufnull.tsv` (L1–L6 all `distinguishable = False`; L7, L8 `distinguishable = True` with empty `shuffled_alpha`). Accurate. But the summary sentence ("shuffled α lies within Δα < 0.35 of real α where both can be fit") in the Abstract (line 7) glosses the "where both can be fit" caveat, and six of twelve layers where the fit is not possible is itself a finding that a hostile reviewer will want quantified in the Abstract.

6. **Basis-invariance n_avalanches inconsistency across bases** (§4.4, line 133). Paper notes "n_avalanches differs across bases (3 276 / 5 124 / 3 250)" and calls this an "expected, not pathological, basis effect". This is defensible but a hostile reviewer will ask: if the event *count* differs by 57% across bases for a fixed z-score threshold, the avalanche-size distribution is not basis-equivariant at the event level, and calling α "basis-invariant" when α is being fit to genuinely different event streams is a subtle story. Consider adding one sentence: "the size-distribution *shape* is basis-robust within ±0.5 even though the event-count is not, because z-score thresholding is a per-column operation."

7. **§4.3 PR interpretation as "layer-specialisation"** (line 129) still leans on post-hoc citation of Geva 2021 / Elhage 2021 without a causal probe (this was v1-W10, not directly addressed in v2). §5.2 (line 155) softens to "consistent with" but the Results section (§4.3 line 129) still reads as explanation rather than correlation. Recommend moving the Geva/Elhage citation fully into §5.2 and keeping §4.3 purely descriptive.

8. **Shape-collapse omission is better scoped but not fully transparent**. §3.6 (line 91) now says "Shape-collapse analysis is implemented only as a γ-slope from ⟨s | T⟩ fits; full per-avalanche profile collapse (Papanikolaou 2011) is out of scope". §7 repeats. Good. But §3.1 item 3 (line 45) still reads as if the full Sethna γ predicate is tested — a reviewer skimming §3.1 will not know until §3.6 that the predicate is only partially instantiated. Add one clause to §3.1 item 3: "via ⟨s | T⟩ slope fit; per-avalanche profile collapse is out of scope, see §3.6".

9. **MR observable definition vagueness** (v1-W9 carried over). §3.4 (line 77) says "scalar activity signal a(t) = Σ_j |A_{t,j} − μ_j|, i.e. the sum of per-neuron absolute-centred activations at time t (where μ_j is the time-mean of neuron j)". This is now explicit about the un-z-scored centring — fixed from v1's ambiguous "|z_{t,j}|" wording. ✓ Partial fix, but the paper should still note that the MR branching-ratio estimate depends on this observable choice and that the qualitative σ(layer) gradient may not be scale-equivariant under alternative definitions (e.g., |z_{t,j}| with per-column σ normalisation).

### Minor

10. **Single corpus / single seed** (v1-W3 carried over). §7 (line 185) now states the limitation explicitly: "Single model, single corpus, single seed ... no external cross-seed CIs are reported." Honestly scoped. ✓ — but the claim "the negative result is robust" in §5.6 (line 173) is still a single-realisation claim; rephrase to "robust across 216 cells on the single seed / corpus realisation tested".

11. **Transformers 5.5.4 version string** (v1-W16 carried over). Transformers stable is 4.46.x as of 2026-04; no 5.x exists. Verify and correct to the actual installed version. If this is a bleeding-edge dev tag, note that.

12. **SAE basis omission** (v1-W17). §3.5 and §7 both now scope the SAE gap honestly ("Gemma Scope not released for GPT-2"). But Joseph Bloom's `gpt2-small-res-jb` SAE IS public on HuggingFace — a reviewer familiar with SAELens will flag this. Add one sentence addressing why the gpt2-small-res-jb release was not used.

13. **"first / novel / unprecedented"** language audit: I searched paper_v2.md — "first" does not appear, "novel" does not appear, "unprecedented" does not appear. ✓ §2 last paragraph's "No prior work we are aware of (i) runs the full CSN + Sethna + MR-σ + threshold-plateau + basis-invariance + shuffle-null battery (ii) on pretrained transformer LM activations on natural text (iii) against a matched-init random-weight control" is a legitimate scope claim without the banned words. Acceptable.

14. **Writing-Rules Phase-number audit**: I searched paper_v2.md for "Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "sub-agent", "reviewer", "methodology review" in the body. None found. ✓ The word "review" appears only in §5.6 as "A reviewer might ask" which is a rhetorical device, not audit-trail leakage — borderline acceptable. Recommend rephrasing to "One might ask" or "A skeptic might ask" for fully clean copy.

15. **Literature positioning (dimension 6)**: No new mis-citations introduced in v2. Relevant 2024–2026 work *likely to be flagged as missing* for a negative-result criticality paper on transformers:
    - Ziyin, Wang, Ueda 2024 "Neural thermodynamics" / "Law of balance" series on weight-norm fluctuation-dissipation — relevant to the statistical-mechanics-of-trained-networks framing.
    - Bahri, Kadmon, Pennington et al. "Statistical mechanics of deep learning" *Annu. Rev. Condens. Matter Phys.* 2020 — foundational review; absent.
    - Roberts, Yaida, Hanin 2022 "Principles of Deep Learning Theory" (Cambridge) — finite-width edge-of-chaos theory; absent.
    - Hoover, Chau, Lai et al. 2024 on transformer feature geometry — relevant to §4.3 PR interpretation.
    - Not strictly blocking, but adding 2–3 of these would strengthen the Related Work.

---

## Specific Revision Requests (numbered)

1. **Fix §4.1 α ranges for θ=2.0 and θ=3.0** to match the TSV exactly. Trained ambient θ=2.0: **[2.02, 2.95]** (L11 min, L10 max). Trained ambient θ=3.0: **[1.69, 3.00]** (L11 min, L6 max). Soften the "never touches 3/2" claim to accommodate L11-θ=3.0 at α=1.69 — note that 1.69 is within 0.2 of 3/2 but fails all the other DP predicates at that layer, so DP is still refuted. (This is a numerical error; mandatory.)

2. **Reconcile §3.1 item 6 ±0.3 with §4.4 ±0.5 on basis invariance.** Either tighten the realised spread by re-fitting on a broader layer set or relax the evidence bar. Currently the paper passes a self-imposed criterion it admits its own data fails. (Mandatory.)

3. **Add bootstrap CIs to every α, β, γ, σ point estimate in §4.** `mrestimator.numboot=100` provides σ CIs for free; `powerlaw` v2.0 bootstrap likewise. Emit a `sigma_CI_low / sigma_CI_high / alpha_CI_low / alpha_CI_high` column set in `e01_anchor_gpt2.tsv` and quote the best and worst in §4.2. (Mandatory.)

4. **Verify arXiv:2604.16431** (Wang et al. 2026). Confirm the paper exists at that ID; if not, replace with the correct citation or remove. (Mandatory — potential phantom citation.)

5. **Verify HuggingFace Transformers 5.5.4** in §3.2. If the installed version is 4.46.x or similar, correct. (Mandatory for reproducibility.)

6. **Shape-collapse clarification**: add to §3.1 item 3 "via ⟨s | T⟩ slope fit; per-avalanche profile collapse is out of scope, see §3.6". (Minor.)

7. **Move Geva/Elhage interpretation from §4.3 to §5.2**; keep §4.3 purely descriptive. (Minor.)

8. **Add one-sentence scope note in §4.4** on event-count variation across bases. (Minor.)

9. **Add one sentence on `gpt2-small-res-jb` SAE release** in §3.5 explaining why it was not used. (Minor.)

10. **Rephrase "A reviewer might ask" in §5.6** to "A skeptic might ask" or similar to remove the last audit-trail echo. (Trivial.)

---

## Verdict

**MAJOR REVISIONS.**

Revision items 1 (α range mismatch), 2 (±0.3 vs ±0.5 inconsistency), 3 (no bootstrap CIs) and 4 (phantom arXiv ID) are each independently blocking for *Entropy* / TMLR / NeurIPS. Items 1 and 2 are direct numerical-claim / TSV mismatches of the same class that v1 flagged and that v2 explicitly set out to fix — some were fixed, but §4.1's θ=2.0 and θ=3.0 ranges are still wrong and the evidence-bar internal inconsistency is new. Item 3 was a disqualifying v1 issue that v2 simply did not address. Item 4 is a potential fabricated-citation issue that must be resolved.

The good news: the core science is sound, v1's four disqualifying issues are 2.5-of-4 addressed (title scope ✓, γ range ✓, Vuong lognormal ✓, bootstrap CIs still missing). The required revisions are all executable in 2–4 days of re-runs and text edits; no new experiments beyond re-emitting bootstrap columns from `mrestimator` / `powerlaw` and re-reading the TSV for the α ranges at θ=2.0 and θ=3.0.

Return with revisions 1–5 addressed; 6–10 are nice-to-have.
