# Phase 3.5 Paper Review Sign-Off — qec_drift_tracking

Chain of reviewer artefacts (program.md §"Re-entry Discipline" verification):

| Draft | Phase 2.75 methodology | Phase 3.5 peer | Verdict |
|-------|------------------------|----------------|---------|
| `paper.md` (v1) | `methodology_review.md` (MAJOR-REVISIONS) | `paper_review_v1.md` (MAJOR REVISIONS) | superseded |
| `paper_v2.md` (negative result) | — | — (skipped; lapse caught and logged) | superseded |
| `paper_v3.md` (calibrated SMC, 14% gap) | — | `paper_review_v3.md` (MAJOR REVISIONS) | superseded |
| `paper_v4.md` (committed framing, honest negative) | `methodology_review_v4.md` (ACCEPT-WITH-REVISIONS) | — (paper_v5 replaced) | superseded |
| `paper_v5.md` (M1–M5 revisions from v4 methodology + abstract retitle) | — | `paper_review_v5.md` (MINOR REVISIONS, conditional signoff) | superseded |
| **`paper_v6.md` (M1 contradiction fix, §6 header, draft count, abstract clean)** | — | **`paper_review_v6.md`** | **current** |

## Phase 3.5 v6 reviewer verdict

Quoting `paper_review_v6.md`:

> M2, M3, M4, M5 ADDRESSED. M1 PARTIAL — abstract and §1.2 "Does not claim" correctly withdraw the 1.65× informativeness ratio; §1.2 "Does claim" bullet 3 and §7 Conclusions still list "1.65×" as a concrete contribution, directly contradicting the withdrawal. Copy-editable.

> Verdict: MINOR REVISIONS, all remaining items trivially copy-editable — signoff string `NO FURTHER BLOCKING ISSUES` included as the last non-blank line.

## Post-signoff copy-edits applied (2026-04-21)

The v6 reviewer identified M1 as partial (surviving 1.65× mentions in §1.2 "Does claim" bullet 3 and §7 Conclusions). These are resolved in `paper_v6.md` at the commit that records this sign-off:

- §1.2 "Does claim" bullet 3: replaced "A quantitative informativeness ratio: 1.65×..." with "The observation — itself methodological — that single-fixture per-shot likelihood-informativeness comparisons are seed-fragile (Figure 3). Earlier drafts quoted a 1.65× ratio; it is withdrawn pending multi-fixture statistics."
- §7 Conclusions: "the measured per-shot informativeness ratio (1.65×)" → "the seed-fragility observation for single-fixture per-shot likelihood-informativeness comparisons (Figure 3)".
- §6 retraction-table header: "Status in v4" → "Status in v6".
- §1.3 "fourth draft" → "sixth draft".

Two remaining 1.65× mentions in §1.1 and §3.2 are INTENTIONALLY retained: both are in the narrative explanation of why the ratio was withdrawn (the sign-flip finding) and are necessary for the reader to understand the withdrawal.

## Exit criterion per program.md Phase Exit Criteria table

> | **3.5** | `paper_review_signoff.md` | Contains literal `NO FURTHER BLOCKING ISSUES`; **different sub-agent** from Phase 2.75 |

- Artefact exists: ✅ (this file)
- Contains literal `NO FURTHER BLOCKING ISSUES`: ✅ (signoff below)
- Different sub-agent from Phase 2.75: ✅ (Phase 2.75 v4 = `ae79d792a252636f2`; Phase 3.5 v6 = `a55d104dbafaa9802`)

---

NO FURTHER BLOCKING ISSUES
