# Phase −0.5 Scope Check: Non-Markovian TUR Empirical Search

## 1. Novelty

Marginal. The proposal frames itself as an empirical first, but the surrounding literature is crowded and the author has not demonstrated awareness of the closest neighbors. Three comparators a real reviewer will cite in the desk-reject letter:

- **Skinner & Dunkel, PNAS (2021)** — inferred entropy production from real single-molecule time-series (flagellar motor, beating flagellum) and explicitly benchmarked against TUR bounds. This is the paper the proposal is functionally competing with and it is not cited.
- **Manikandan, Gupta & Krishnamurthy, PRL (2020)** / **Van der Meer, Ertel, Seifert, PRX (2022)** — "TUR as thermodynamic inference" from trajectories; applied to molecular motor data.
- **Di Terlizzi & Baiesi (2019)**, **Otsubo et al. (2020)** — kinetic-uncertainty / entropy-production estimation from experimental dwell-time data.

The claim "nobody has systematically compared" is not credible as written. At minimum, the proposal must differentiate from Skinner–Dunkel.

## 2. Falsifiability of the four kill-outcomes

Mixed. Outcomes 3 and 4 (non-Markovian violation; monotonicity in k) are genuine binary tests. Outcome 2 is **tautological**: the standard TUR is a *theorem* for Markovian steady-state dynamics. A "Markovian system violating TUR" cannot happen — if it appears to, the correct inference is that σ was mis-estimated, the system is not actually Markovian, or the NESS assumption fails. Listing this as a "major result" kill-outcome reveals a conceptual gap; a PRL referee will hammer this.

Outcome 1 (data availability) is **not falsifiability** — it is a project-feasibility gate dressed as a scientific outcome. The listed sources (Wen 2008, Chen 2013/14, Zeger 2019, Greenleaf 2009, Blanchard FRET) are papers, not public datasets. Single-molecule dwell-time traces are rarely deposited; authors publish histograms. Extracting Var(N)/⟨N⟩² for *cycle counts* (not dwell times) requires raw trajectories, which for most of these works means emailing the PI. This is a serious blocker and should be smoke-tested before Phase 0.

## 3. Venue

Wrong. PRL/PRX is not realistic for a cross-dataset reanalysis that confirms a known theorem (Van Vu–Hasegawa 2020 already proved non-Markovian violations are allowed). The most likely outcome — "Erlang-k correlates with TUR ratio across five datasets" — is a confirmatory empirical study. That is **PRE** territory, or *J. Stat. Mech.* A genuine Markovian violation would be PRL, but that outcome is both unlikely and, per point 2, almost certainly an estimation artifact.

## 4. Most likely killer objections

- σ (entropy production per cycle) cannot be read off "ATP/GTP hydrolyzed per step" — futile cycles, branching pathways, and partial hydrolysis make this a >2× uncertainty. The TUR ratio is linear in σ; headline conclusions are not robust.
- Cycle-counting variance Var(N)/⟨N⟩² needs long trajectories at steady state; most published single-molecule work reports dwell-time histograms, not cycle-count statistics.
- Erlang-k fit is a parametric caricature of non-Markovianity; real reviewers will ask for model-free memory measures.
- Tautology in outcome 2 (above).

Reframe: drop PRL; target PRE; replace outcome 2; do a 1-week data-access smoke test on two datasets before committing.

VERDICT: REFRAME
