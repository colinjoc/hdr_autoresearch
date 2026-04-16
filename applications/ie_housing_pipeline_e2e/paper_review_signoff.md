# Phase 3.5 Signoff: IE Housing Pipeline E2E

**Date**: 2026-04-16
**Reviewer**: Automated blind reviewer agent

## Blocking Issue Resolution

| ID | Issue | Resolution | Status |
|----|-------|------------|--------|
| R1 | Build-yield vs CCC-yield not distinguished | Build-yield (59.6%) added alongside CCC-yield (35.1%) in abstract, Section 5.1, Section 8. Title revised to "Certified Homes." | RESOLVED |
| R2 | 144,000 permissions headline misleading | Both figures now presented: ~85,000 (build-yield) and ~144,000 (CCC-yield). Section 5.6 explains which denominator is policy-relevant. | RESOLVED |
| R3 | Stage 2-3 decomposition incomplete | Decomposition table added to Section 5.2: 53.5% opt-out regulatory, 46.5% genuine/pending. | RESOLVED |
| R4 | PL-4 cluster-bootstrap CI not propagated | Yield CI revised to [32.8%, 37.1%] using PL-4 [4.4%, 15.6%]. Replaces [28.0%, 35.4%]. | RESOLVED |
| R5 | Cox champion unjustified (C=0.5) | Downgraded to framework recommendation. Binomial designated as primary yield model. | RESOLVED |

## Non-blocking Issue Resolution

| ID | Issue | Resolution |
|----|-------|------------|
| R6 | E07 apartment flag bug (0% CCC) | Confirmed: flag matches 0 rows. E07 withdrawn from paper. | 
| R7 | DES independence validation circular | Noted in Section 4.3 and Caveat 7. |
| R8 | LDA double-counting provenance | Explicitly noted PL-3 inheritance in Sections 5.8 and 8. |
| R9 | 95% CCC-to-occupied ungrounded | Cross-check added: CSO/BCMS ratio 1.28-1.42 shows proxy is conservative. Discussed in Section 3.1 and 6.3. |

## Verdict

**NO FURTHER BLOCKING ISSUES.**

All five blocking issues from the Phase 2.75 review have been resolved with code changes (analysis.py), updated results (results.tsv, 50 rows), and a revised paper (paper.md with Section 9 change log). The four non-blocking issues have also been addressed. The paper now correctly distinguishes CCC-yield from build-yield throughout, and the headline policy figures reflect both denominators.
