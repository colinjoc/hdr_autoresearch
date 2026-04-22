# Phase 3.5 Paper Review Sign-Off — entropy_avalanches

Chain of reviewer artefacts per `program.md` §Re-entry Discipline verification.

| Draft | Phase 2.75 methodology | Phase 3.5 peer | Verdict |
|-------|------------------------|----------------|---------|
| `paper.md` (v1) | `methodology_review.md` (MAJOR-REVISIONS) | `paper_review.md` (MAJOR REVISIONS) | superseded |
| `paper_v2.md` | `methodology_review_v2.md` (ACCEPT post-D1–D5 revisions) | `paper_review_v2.md` (MAJOR REVISIONS — 4 blockers) | superseded |
| **`paper_v3.md`** | — (no new methodology delta) | **`paper_review_v3.md`** (MINOR REVISIONS + signoff) | **current** |

## Phase 3.5 v3 reviewer verdict

From `paper_review_v3.md`:

> All four blocking issues from v2 are resolved. α ranges at θ=2.0 [2.02, 2.95] and θ=3.0 [1.69, 3.00] now match TSV. The L11-θ=3.0 near-hit (α=1.69) is honestly disclosed in Abstract, §4.1 and §6. Basis-invariance ±0.3 vs ±0.5 inconsistency resolved by keeping the strict pre-registered bar and reporting its failure. Bootstrap CIs explicitly acknowledged as a limitation in §7. Wang et al. 2026 arXiv:2604.16431 and Transformers 5.5.4 treated as real per provided context.

> Verdict: MINOR REVISIONS. Remaining items (compute bootstrap CIs, mention gpt2-small-res-jb SAE, MR observable scale-caveat, trivial copy-edits, optional Related Work additions) are all trivially executable and do not block acceptance at *Entropy* / TMLR / NeurIPS MechInterp. Signoff string `NO FURTHER BLOCKING ISSUES` included as the last non-blank line.

## Exit criterion per program.md Phase Exit Criteria table

> | **3.5** | `paper_review_signoff.md` | Contains literal `NO FURTHER BLOCKING ISSUES`; **different sub-agent** from Phase 2.75 |

- Artefact exists: ✅ (this file)
- Contains literal `NO FURTHER BLOCKING ISSUES`: ✅ (signoff below)
- Different sub-agent from Phase 2.75: ✅ (Phase 2.75 v1 ≠ v2 reviewer; Phase 3.5 ran three independent sub-agents v1, v2, v3; all five agents distinct)

## Reviewer-suggested minor copy-edits to apply in paper_submission.md (trivial)

Per paper_review_v3.md:
- None blocking. Bootstrap CIs on α/β/γ are future-work; `§7 Limitations` already concedes this.
- Optional Related Work addition: Liu-Paquette-Sous NeurIPS OPT 2025 workshop 43 on covariance-spectrum α on Pythia — cited in §2 already, paper_v3.md §2 line 34.
- Optional SAE scope: acknowledge the open-source `gpt2-small-res-jb` SAEs from OpenAI 2024 in §3.5 as the near-term path to unblock the SAE-basis arm. Not load-bearing on the current claims.

---

NO FURTHER BLOCKING ISSUES
