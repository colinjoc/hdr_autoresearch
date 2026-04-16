# Blind Reviewer Report — Irish Emigration 2020-2025

**Verdict**: Revise. Descriptive claims are sound but framing is mis-scoped.

## Major issues

1. **Title/scope mismatch**: Folder is `ie_graduate_emigration` and prior framing says "graduate", but PEA18 is all-ages. Title correctly drops "graduate" but directory, repo slug, and any internal references must be reconciled. State in §1 that graduate-specific analysis requires HEA GOS and is out of scope.

2. **"Australia overtook UK" not tested**: CSO PEA18 figures are survey/modelled estimates with non-trivial standard errors (historically ±2-3k for small cells). Gap is 13.5 vs 12.6 = 0.9k. Without CSO-published CIs or a bootstrap on component estimators, "structural shift" is overclaim. Downgrade to "Australia is now statistically tied with the UK at the top; 2023-25 shows Australia consistently at or above UK" and cite CSO precision notes.

3. **2024→2025 drop unexplained**: 69.9k→65.6k (-6%) is ignored. Either note it as provisional/revision-prone or discuss whether the wave has peaked.

4. **No net-migration context**: Paper mentions +76k net only in "what we cannot say". Lead should acknowledge Ireland is net-receiving; otherwise headline misleads.

5. **2012 peak (83.0k) ratio stated but not sourced in table/plot**: add row to table or annotation on chart.

## Minor
- Aggregated "Other-23" (11.1k) rivals top destinations; flag as limitation.
- April-stock frame differs from ACS flow — note once.
- `analysis.py` has no tests.
