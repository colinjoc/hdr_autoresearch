# Adversarial Peer Review — `paper.md` (Entropy Avalanches on GPT-2-small)

**Reviewer role**: hostile-but-fair program-committee referee for *Entropy* journal / NeurIPS or ICLR MechInterp workshop / TMLR.
**Artefacts read**: `paper.md`; `results/e01_anchor_gpt2.tsv` (216 rows verified); `results/e01_shufnull.tsv` (24 rows verified); `pipeline/*.py` (five modules, ~640 LOC); `figures/*.png` (file names and captions only — images not rendered in review environment); `entropy_ideation/knowledge_base.md` (evidence bar context).

---

## Summary (≤ 200 words)

The paper reports a *negative* result on the mean-field directed-percolation (DP) criticality hypothesis for activation avalanches in pretrained GPT-2-small on C4 text, using a six-element statistical-physics battery (Clauset–Shalizi–Newman power-law fit, MR-estimator branching ratio, Sethna γ cross-check, threshold-plateau, basis-invariance, temporal-shuffle null) against a matched-init random-weight control. None of the four DP predicates (α ≈ 3/2, β ≈ 2, γ ≈ 2, σ ≈ 1) is satisfied; the threshold plateau fails by a large margin; the shuffle null is not cleanly rejected. As a positive secondary contribution, the paper reports two depth-graded structural signatures — σ(layer) and participation-ratio(layer) — that differ sharply from the random-init control and align with the layer-specialisation literature.

Numerical claims are mostly faithful to the TSV, the methodology is sound, and the framing is honestly negative. However, scope is narrow (single model, single corpus, 62 K tokens, single seed), several numerical ranges in the abstract and §4 disagree with each other and with the TSV, bootstrap CIs are missing from every quoted point estimate, and the paper is short on reproducibility detail.

---

## Strengths

- **Honestly negative framing.** The paper does not cherry-pick θ or basis to manufacture a criticality claim. The title contains "Negative Result", the abstract states the failure of all four DP predicates up front, and §6 refuses to soft-pedal.
- **Multi-predicate battery is well-motivated.** Directly aligned with the 8-item evidence bar in `knowledge_base.md` §5. Threshold-plateau, basis-invariance, and shuffle-null are implemented and reported — all three are flagged as "mandatory" by the knowledge base and most are missing from the adjacent literature.
- **Matched-init random-weight control is thoughtful.** The choice to instantiate via `AutoModelForCausalLM.from_config(config)` to preserve the library's own `_init_weights` (avoiding the degenerate "xavier_normal + zero biases" collapse) is a genuine methodological improvement over the naive random-init baseline.
- **MLP-out hook rather than block-out.** Explicit, correct justification in §3.2 that hooking the residual-stream block output would trivially satisfy σ ≈ 1. This shows the authors understand the tautology and sidestep it.
- **Positive structural signatures are informative.** σ(layer) and PR(layer) gradients (verified in TSV rows) are clear, reproducible, and distinguish training from matched-init.
- **Code is pytest-tested** and lazy-imports heavy packages. The pipeline is compact (~640 LOC across five modules) and is plausibly reproducible.

---

## Weaknesses (ordered by severity)

### Major

1. **Internal inconsistency on γ_predicted range.** The abstract states γ_predicted ≈ 0.85–1.14; §4.1 states γ_predicted ranges 0.36–1.14. Verified against TSV (trained ambient θ = 2.5, column `gamma_predicted`): actual range is **[0.789, 1.119]**. **Neither the abstract nor §4.1 matches the data**. The 0.36 figure in §4.1 appears to be stale (it may include non-ambient or non-θ=2.5 layers); the 0.85 in the abstract is wrong (L11 is 0.789). Fix both to the actual measured range and cross-check every quoted interval in the paper the same way.

2. **No confidence intervals on ANY point estimate.** §3.4 says `powerlaw` v2.0 is used with `distribution_compare` and the MR estimator is used with `numboot=100`. Neither α, β, γ_predicted, nor σ is ever quoted with a bootstrap CI anywhere in the Results or Abstract. Claims like "σ = 0.30 at layer 5" are unfalsifiable without a CI. The CSN protocol (Clauset-Shalizi-Newman 2009) — explicitly cited in §3.1 — requires the bootstrap p-value for goodness-of-fit; the TSV contains `ks` statistics and `p_vs_lognormal` / `p_vs_exponential` columns but neither the p-value for the power-law hypothesis itself nor bootstrap CIs on α. The evidence bar in `knowledge_base.md` §5 item 1 explicitly demands "bootstrap p-value ≥ 0.05 for power-law" — this is not reported. A reviewer at *Entropy* or NeurIPS will flag this immediately.

3. **Single seed, single corpus sample, no run-to-run variability.** The paper streams "1 000 documents from `allenai/c4`" with no mentioned seed for dataset streaming, no mention of seed for the random-init control, no mention of seed for the `QR`-factorised random-rotation basis. All claims are single-realisation point estimates. The depth-graded σ pattern [1.09, 1.08, 1.08, 0.97, 0.96, 0.30, 0.69, 0.66, 0.76, 0.80, 0.92, 0.95] could be partly a sampling fluctuation — we cannot tell without at least 3 random-init seeds, 3 corpus resamples, and inter-seed σ variability on trained. The random-init column's reported σ std of 0.006 across 12 layers is NOT the same as run-to-run std.

4. **Title/scope generalisation.** Title: "Activation Avalanches in Trained Transformer Language Models". Corpus: GPT-2-small only (124 M), C4 'en' only, 64-token truncation, 62 K valid tokens. The plural "Language Models" is not licensed. A reviewer will require one of (i) downscoping the title to "…in GPT-2-small" or (ii) adding Pythia-160M / Pythia-410M / one other architecture. §5.6 acknowledges the limitation but the title does not. The Limitations section is not a substitute for honest title scoping.

5. **62 K-token sample is thin for tail statistics.** At θ = 2.5 ambient most layers have 3 000–6 000 avalanches after the size-≥ 2 cut. The CSN alternative-distribution tests (p_vs_lognormal, p_vs_exponential columns) show many p ≪ 0.05 values — meaning power-law is NOT preferred over lognormal/exponential — but the paper never interprets these columns. For instance, trained L0 ambient θ=2.5 has p_vs_lognormal = 5.9e-14 — power-law is *rejected* in favour of lognormal. If the data do not prefer power-law over lognormal, fitting α and discussing "α ≠ 3/2" is itself on unstable footing; the proper framing is "the distribution is not power-law, and whatever α we quote is a maximum-likelihood fit to a model the data rejects". This is a subtle but real methodological hole — it strengthens the negative result but the paper should acknowledge it.

6. **Shuffle-null reporting is minor but wrong.** §4.5 says "The other 6 fittable layers show α_shuffled within ±0.3 of α_real." Verifying against `e01_shufnull.tsv`: L1 Δ = 0.203 ✓; L2 Δ = 0.348 ✗ (*not* within 0.3); L3 Δ = 0.077 ✓; L4 Δ = 0.071 ✓; L5 Δ = 0.075 ✓; L6 Δ = 0.090 ✓. So 5 of 6, not 6 of 6. The qualitative story stands but the sentence is numerically inaccurate.

7. **"PR ≈ 1–8 out of d = 768" in abstract does not match TSV.** Abstract: "trained layers 1–5 collapse to a very low-dimensional subspace (PR ≈ 1–8 out of d = 768)". TSV `participation_ratio` column for trained layers: L0=9.93, L1=1.07, L2=1.00, L3=1.86, L4=2.49, L5=7.64. Layer 0 is 9.93, outside the stated "1–8" range and outside the stated "layers 1–5" layer-range. §4.3 is internally consistent; the abstract is loose. Fix the abstract to either "layers 1–5 PR ≈ 1–8" (drop L0) or widen the range.

### Moderate

8. **Shape-collapse is a stub, not an implementation.** `exponents.shape_collapse` returns a `chi=2.0` placeholder — it does not actually do per-avalanche profile collapse. §3.4 does not mention shape collapse at all; §5.6 notes "only the γ slope is reported" but does not flag that the shape-collapse code is non-functional. This is not load-bearing on the headline claim (the claim is already negative) but a reviewer reading the code will see that the module exists only to be cited.

9. **MR-estimator `activity` signal definition is vague.** §3.4 says "Scalar activity signal a(t) = Σ_j |z_{t,j}|". Reading `pipeline/subspace.py` line 92, the ambient activity is `|X - X.mean|.sum(axis=1)` — i.e., summed absolute *deviation from column mean*, not |z| (no division by σ_j). The two differ by a per-column scaling; the MR exponential-autocorrelation fit is not invariant to per-column scaling in general. Either document that the MR observable is un-z-scored absolute deviation, or re-run with the z-scored version that the paper describes.

10. **Depth-graded σ interpretation is speculative.** §5.2 attributes the σ(layer) / PR(layer) gradient to "layer-specialisation" with appeals to Geva 2021, Elhage 2021, Olsson 2022. This is plausible post-hoc storytelling but there is no causal test, no ablation, no activation-patching evidence that the low-PR early layers are in fact "shared token-frequency/positional" features. A reviewer will want either (i) honest framing as "consistent with" rather than "consistent-with-and-also-explained-by", or (ii) a concrete causal probe (e.g., unembedding the layer-0 principal direction and showing it aligns with BPE token frequency).

11. **No comparison against Wang et al. 2026 on *their* observable.** §5.4 says "Our substrate (pretrained natural-text GPT-2) and observable (σ, α, β, γ on activations rather than D on gradients) differ on every axis." This is fine, but then why is Wang et al. 2026 cited as the key motivating transformer-criticality work? A reviewer will ask: did you try computing Wang's cascade-dimension D on GPT-2, or running their TDU-OFC probe? If not, a one-sentence explicit statement ("D(t) as defined in Wang et al. requires a gradient-based observable we did not implement; see §5.6") is needed.

12. **Griffiths-phase rejection is incomplete.** §3.1 item 7 requires "Null rejection" but only temporal-shuffle is implemented. §5.6 acknowledges this but a *negative* criticality claim still has to rule out Griffiths-phase-like "broad apparent-criticality" regimes (knowledge_base.md §4 "Cross-cutting"). The paper's negative-result conclusion is not weakened by this gap, but the claim "trained GPT-2 is not in the mean-field DP criticality class" does not rule out "trained GPT-2 is in a Griffiths-phase or edge-of-synchronisation class". The paper gestures at this in §5.5 re: Morales et al. but could be firmer about what classes are and are not excluded.

13. **Reference 2026 arXiv ID.** The Wang et al. 2026 citation — `arXiv:2604.16431` — is a future identifier. Either this is a future dated work or a typo for 2024/2025. A reviewer will flag and the copy-editor at *Entropy* will require verification. Sanity-check every arXiv ID against the actual papers.

### Minor

14. **"F_l^{MLP}(h_l) ... non-tautological" wording.** The hook is on the MLP sublayer output *before* the residual add, which is correct. But the output of `block.mlp` in GPT-2 depends on post-LN h_l — the paper should be explicit that this is the post-LayerNorm MLP output, not the pre-LN MLP output.

15. **Figures are referenced but not interrogated.** §4.6 lists the three figures but does not describe what they show beyond the caption. For a double-blind review, every figure needs a sentence in the text identifying the take-away the reader should extract from it ("Figure 1 shows that trained σ(layer) has a sharp dip at L5 absent in random-init"). A reviewer without figure access will not know what "reference lines at σ = 1 (critical) and σ = 0.98 (Ma 2019 reverberating)" looks like relative to the data.

16. **§3.6 version claim.** "HuggingFace Transformers 5.5" — this version does not exist as of 2025/2026 (Transformers 4.46.x is current). Either this is a typo for 4.x, or a bleeding-edge dev branch. Document exact version + commit hash for reproducibility.

17. **No SAE basis.** §3.5 correctly notes that Gemma Scope SAEs aren't GPT-2-compatible, but there IS a public `SAELens` release for GPT-2-small that could be used. `openai-community/gpt2` + Joseph Bloom's `gpt2-small-res-jb` SAEs are on HuggingFace. A reviewer familiar with the SAE literature will know this and ask.

---

## Writing-Rules Compliance Check

Per the project's rules that the audit-trail draft (`paper.md`) must NOT contain reviewer/Phase meta-commentary in the body:

- **Reviewer / sub-agent / Phase-number references**: §3.1 contains "Following the Phase 0.25 publishability review for this project, we also require:" — a Phase-number reference. §3.2 contains "Rather than randomly re-initialising pretrained weights ... as we observed with a `xavier_normal(gain=0.02)` initialisation". This phrasing is borderline — not a Phase reference, but it reads like an audit-trail aside. §7 contains "the Phase 0.25 scope-check reframes and the Phase 2.75 methodology-review revisions applied to the experiment design" — explicit Phase numbers. `pipeline/activation_cache.py` docstrings reference "Phase 2.75 D1" and "Phase 2.75 bonus finding" — these are in the code, not the paper, so they do not violate the rule for paper.md but must be stripped when code is archived for submission.
- **Retraction tables of prior drafts**: none observed. ✓
- **Draft-version subtitles in the header**: none observed; title is clean "Activation Avalanches... : A Negative Result...". ✓
- **"first", "unprecedented", "novel" hyperbole**: §2 last paragraph: "No prior work we are aware of (i) runs the full CSN + Sethna + MR-σ + threshold-plateau + basis-invariance + shuffle-null battery (ii) on pretrained transformer LM activations on natural text (iii) against a matched-init random-weight control that preserves the architecture's own LayerNorm initialisation. Our contribution fills that specific niche." — this is strong-form novelty claim without the banned words. Acceptable. The word "novel" does not appear; "first" does not appear; "unprecedented" does not appear. ✓

**Verdict on Writing-Rules**: Phase-number references in §3.1 and §7 must be stripped before the submission-form artefact (`paper_submission.md`). They do not block Phase 3.5 sign-off because the user's rule cited in memory is that paper_submission.md is the clean artefact — but the paper.md audit trail should not leak Phase numbers into inline text either. Recommend removing or at minimum paraphrasing ("the pre-registered scope-check" rather than "Phase 0.25 publishability review").

---

## Specific Revision Requests (numbered)

1. **Fix γ_predicted range** in both the abstract and §4.1 to match the TSV. Actual trained ambient θ = 2.5 range is **[0.789, 1.119]**. Remove the "0.85" and "0.36" figures. Either quote the range or quote a mean ± std.

2. **Add bootstrap confidence intervals** to every α, β, γ, σ point estimate in the Abstract and §4. At minimum, add the CSN bootstrap p-value for power-law goodness-of-fit to Table rows and in-text quotes of α. At minimum, add MR-estimator bootstrap 95 % CI for every σ quoted in §4.2 (the TSV re-run should re-emit these columns — `mrestimator` `numboot=100` gives them for free).

3. **Rerun with ≥ 3 random seeds** for the random-init control, ≥ 3 corpus resamples for the trained, ≥ 3 QR random-rotation seeds. Report seed-to-seed std on σ(layer) and α(layer, θ, basis). Without this, the "depth-graded σ" story is a single-realisation claim.

4. **Downscope the title** to "Activation Avalanches in GPT-2-small" OR add at least one additional model (Pythia-160M is a one-afternoon run on a 3060). If keeping the plural, at minimum rewrite the abstract first sentence to restrict scope and move the "Language Models" framing to the discussion.

5. **Interpret the `p_vs_lognormal` / `p_vs_exponential` columns.** Report in §4.1 the fraction of (layer, basis, θ) cells for which the power-law hypothesis is rejected in favour of lognormal (LLR p < 0.05). If the majority, explicitly reframe: "the distributions are not power-law — we report α only as a maximum-likelihood slope for comparison, and note that this strengthens the negative result".

6. **Fix the §4.5 shuffle-null count.** Replace "within ±0.3" with "within ±0.35" OR list the actual Δα per layer. Layer 2 has Δα = 0.348.

7. **Fix the abstract PR range** to either "layers 1–5, PR 1–8" (drop L0) or "layers 0–5, PR 1–10" — whichever the authors prefer. Currently internally inconsistent with §4.3.

8. **Strip Phase-number references** from §3.1 ("Phase 0.25 publishability review") and §7 ("Phase 0.25 scope-check reframes and the Phase 2.75 methodology-review"). Replace with scope-check / pre-registration language.

9. **Document exact versions**: Transformers 5.5 is suspicious — verify and correct. Add git commit hash, HuggingFace dataset config ("allenai/c4" has many subsets — `en`, `en.noblocklist`, `realnewslike`; paper says 'en' but does not specify revision / checksum). Report the random seeds used for model random-init, for QR rotation, for C4 streaming.

10. **Make the shape-collapse placeholder honest.** Either remove the citation to Papanikolaou 2011 shape-collapse from §3.1 item 3 as an implemented test (it is not), or implement a real per-profile collapse. §5.6's "placeholder" wording is not enough — §3.1 currently reads as if shape collapse is part of the battery.

11. **Clarify the MR activity observable.** Reconcile §3.4 ("a(t) = Σ_j |z_{t,j}|") with the code in `pipeline/subspace.py` line 92 (`|X - X.mean|.sum(axis=1)`, un-z-scored). If the reported σ is on the un-z-scored observable, say so.

12. **Describe each figure in the text**, not just the caption. One sentence per figure identifying the take-away.

13. **Verify the Wang et al. 2026 arXiv ID.** `arXiv:2604.16431` is a future identifier format. Resolve to the actual paper. Same for any other citations with implausible IDs.

14. **Consider adding a GPT-2 SAE basis** (Joseph Bloom `gpt2-small-res-jb` is public on HuggingFace). If omitted, add a sentence explaining the choice beyond "Gemma Scope isn't released for GPT-2".

15. **Add a brief §5.7 "Classes not excluded"**: note explicitly that the negative result rules out mean-field DP but does not rule out Griffiths phase, edge-of-instability (Morales 2023), or edge-of-synchronisation (di Santo 2018).

---

## Verdict

**MAJOR REVISIONS.**

The paper is methodologically serious, the negative result is credible, and the secondary positive structural finding is real. But four of the Major weaknesses are disqualifying in their current form for any of the target venues:

- (W2) No confidence intervals — *Entropy* and TMLR will reject on this alone.
- (W3) Single seed / single corpus realisation — NeurIPS/ICLR workshop reviewers will reject on this.
- (W1 + W7 + W6) Three independent numerical disagreements between Abstract / §4 text / TSV data — a hostile reviewer sees sloppiness; a copy-editor sees errors.
- (W4) Title over-generalises scope — any reviewer will flag.

None of the revisions is research-blocking — all can be addressed in a one-to-two-week revision cycle (re-runs with multi-seed, recomputation of bootstrap CIs from the existing `powerlaw` / `mrestimator` API, text edits). The core science holds. Return with revisions addressing at minimum items 1–7 in the Specific Revision Requests list.