# Autoresearch: [YOUR SCIENTIFIC QUESTION] — HDR

**Local**: `/path/to/your/project/`
**Venv**: `source /path/to/venv/bin/activate`

---

## ⚠️ GLOBAL RULE — READ THIS BEFORE ANY PHASE ⚠️

**EVERY phase defined in this document MUST be completed on EVERY project. NO EXCEPTIONS. NO "DESCRIPTIVE SHORTCUTS". NO "SKIP BECAUSE SIMPLE". NO "COMBINED WITH PREVIOUS PHASE".**

Every project is classified as either **website-target** (default — output is the HDR website summary) or **publication-target** (output is a manuscript to be submitted to a named journal). Publication-target projects have two additional mandatory phases (−0.5 and 0.25) that catch novelty and venue problems *before* the expensive Phase 0 / Phase 2 compute runs. Website-target projects skip both and go straight to Phase 0.

For every project, the agent MUST produce ALL of the following artifacts on disk, in order, before the project can be declared complete:

1. `proposal.md` + `scope_check.md` (Phase −0.5) — **publication-target projects only**
2. `papers.csv` (Phase 0)
3. `literature_review.md` (Phase 0)
4. `research_queue.md` (Phase 0)
5. `knowledge_base.md` (Phase 0)
6. `feature_candidates.md` + `design_variables.md` (Phase 0) — for Option D: `design_variables.md` lists ansatz families and their free parameters
7. `publishability_review.md` (Phase 0.25) — **publication-target projects only**
8. `data_sources.md` + `E00` row in `results.tsv` (Phase 0.5) — for Option D: `data_sources.md` lists CAS libraries/versions and reference results; `E00` is the baseline framework
9. ≥4 model families in `tournament_results.csv` + `results.tsv` (Phase 1) — for Option D: ≥3 mathematical frameworks including the textbook baseline
10. ≥20 KEEP/REVERT experiments in `results.tsv` (Phase 2)
11. Pairwise-interaction rows in `results.tsv` (Phase 2.5)
12. `paper_review.md` with reviewer-mandated experiments executed (Phase 2.75)
13. `paper.md` (Phase 3)
14. `paper_review_signoff.md` with literal `NO FURTHER BLOCKING ISSUES` (Phase 3.5)
15. `phase_b_discovery.py` output (Phase B)
16. Website `index.md` at `~/website/site/content/hdr/results/<slug>/` (Publish, only after artifact 14 exists)

**If any artifact is missing, the project is NOT complete. Publishing the website summary before artifact 12 exists is a retraction-grade failure.**

**Compact ≠ skipped.** For simple descriptive projects, the lit review can use 4 themes instead of 7 and the tournament can be minimal (logistic regression + one baseline), but the STRUCTURE of every phase must exist on disk. Running a trivial phase is mandatory; skipping it is forbidden.

**What counts as skipping (all forbidden):**
- "This project is descriptive-only so skipping Phase 1 tournament" — FORBIDDEN
- "Quick methodology clone of a previous project so no lit review needed" — FORBIDDEN
- "Reviewer would have nothing to add on this simple analysis" — FORBIDDEN
- "Tight on context budget so skipping reviewer" — FORBIDDEN
- "Went straight from analysis to website" — FORBIDDEN
- "Inlined reviewer concerns in the paper's limitations section" — FORBIDDEN

**If an artifact cannot be created because of a genuine external blocker (credentials, missing data, broken tool), the project is PAUSED — not published. Pause with a written reason and move to the next project.**

---

## Phase exit criteria (machine-checkable, BLOCKING)

A phase is **complete** only when the named artifact exists on disk AND the
named content marker is inside it. Summarising intent in another document
does NOT satisfy an exit criterion. A task-tracker entry cannot be marked
complete unless these are true.

| Phase | Required artifact(s) in `applications/<project>/` | Content marker / rule |
|---|---|---|
| **−0.5** (publication-target only) | `proposal.md` + `scope_check.md` | `scope_check.md` ends with literal `VERDICT: PROCEED`; written by a **different sub-agent invocation** from the HDR author |
| 0 | `papers.csv` + `literature_review.md` + `knowledge_base.md` + `research_queue.md` + `design_variables.md` | ≥200 citations in `papers.csv`; ≥100 hypotheses in `research_queue.md` |
| **0.25** (publication-target only) | `publishability_review.md` | All five checklist sections answered; ends with literal `VERDICT: PROCEED`; written by a **different sub-agent invocation** from Phase −0.5 |
| 0.5 | `E00` row in `results.tsv` + `data_sources.md` | Real data only (no synthetic); seed-stable. Option D: CAS versions + textbook reproduction |
| 1 | ≥4 model families in `results.tsv` + `tournament_results.csv` | Include a linear-model sanity check. Option D: ≥3 mathematical frameworks including textbook baseline |
| 2 | ≥20 rows in `results.tsv` with `status` ∈ {KEEP, REVERT} | Every KEEP ties to a commit and re-runs from cache |
| 2.5 | Pairwise-interaction rows in `results.tsv` | Top-N near-miss features actually tested |
| **2.75** | `paper_review.md` AND all reviewer-mandated experiments present in `results.tsv` with `status` in {RUN_RV, CONTROL, TEMPORAL, DIAG} | `paper_review.md` must be written by a **different sub-agent invocation** from the HDR author; "documented in §Limitations" is NOT a valid completion |
| 3 | `paper.md` | References each KEEP experiment by ID |
| **3.5** | `paper_review_signoff.md` | Must contain the literal string `NO FURTHER BLOCKING ISSUES`; written by a **different sub-agent invocation** from Phase 2.75 |
| B | `phase_b_discovery.py` output in `results.tsv` or `discoveries/` | Actual inverse-design outputs, not more training runs |
| Publish | `~/website/site/content/hdr/results/<slug>/index.md` | **Requires `paper_review_signoff.md` to exist in the project first.** Hugo build passes. |

**Anti-pattern watchlist** (explicit — these were cut corners in prior runs):
- Marking Phase 2.75 "complete" by inlining limitations into `paper.md §8`.
  The whole point of Phase 2.75 is a **blind independent reviewer**; the author
  cannot play both roles.
- Publishing to the website before `paper_review_signoff.md` exists.
- Claiming a "champion" on a random-split holdout without a temporal-split
  confirmation (`status=TEMPORAL` in `results.tsv`).
- Claiming framework novelty when hardware resolution is ≥10× below the
  published frontier — call it replication, not a contribution.

---

## Core Principle

**The goal is DISCOVERY, not model-fitting.** A model is infrastructure. The novel result is what the model finds: new materials, new designs, new physical insights. If the HDR loop never gets past improving a regression score, it has failed.

Every project has two phases:
- **Phase A (Infrastructure, <30% of effort)**: Build predictor/simulator, validate on known cases
- **Phase B (Discovery, >70% of effort)**: Use the tool to explore the unknown

---

## Objective

### Option A: Dataset-Based
Maximise **[METRIC]** on [BENCHMARK] via HDR. Then USE the model for discovery (screen novel candidates, identify non-obvious patterns, propose untested materials/designs).

### Option B: Simulation-Based
Optimise **[OBJECTIVE]** by modifying **[DESIGN VARIABLES]** evaluated via **[SIMULATOR]**. The simulation must be realistic (all dominant physics, hardware constraints, validated against known results).

### Option C: Decomposition-Based
Reverse-engineer an existing AI-discovered or black-box solution. Identify which components and parameters carry the win, which are optimisation artifacts, and what physical mechanism explains the performance. Use **systematic ablation** of the existing solution rather than forward search over a design space. Appropriate when a published result needs interpretation, not improvement. The Phase 2 loop runs in a different rhythm — see "Phase 2 Variant: Decomposition Loop" below.

### Option D: Symbolic/Analytical
Derive, verify, or classify **mathematical expressions** using a Computer Algebra System (CAS) as the evaluation oracle. Appropriate when the primary question is about the structural properties of equations — whether they satisfy constraints, what parameter regimes yield desired behaviour, what the minimal mathematical structure is that produces a result. The evaluation oracle is a CAS (SymPy, SageMath, Cadabra, EinsteinPy, Mathematica), not a dataset or a physics simulator.

**Objective:** Establish whether **[MATHEMATICAL STRUCTURE]** satisfies **[CONSTRAINT SET]** under **[PARAMETER REGIME]**, and identify the minimal structure and parameter bounds that achieve it.

**When to use Option D (not B):**
- The primary output is a symbolic expression, classification, or proof — not a numerical optimum
- The "evaluation" is constraint satisfaction (does this expression have property X?), not optimisation (what value of X minimises Y?)
- The search space is qualitatively different mathematical frameworks, not continuous parameters of a single framework
- The result includes analytical bounds, sign conditions, or symmetry classifications, not just a best-performing design

**When to use Option B instead:**
- The mathematical expression is fixed and you are sweeping continuous parameters to optimise a scalar objective
- The evaluation is purely numerical (a physics simulator that happens to solve equations)
- The result is a ranked design or Pareto front, not a structural insight about the mathematics

The Phase 1 tournament, Phase 2 loop, and Phase B discovery all run in different rhythms for Option D — see the corresponding variant sections below.

---

## Phase −0.5: Scope Check (publication-target projects only)

### When this phase applies

This phase applies only to projects whose intended primary output is a **journal submission**, not the HDR website. Classify the project at ideation:

- **Website-target projects** (default): primary output is `~/website/site/content/hdr/results/<slug>/`. Phase −0.5 and Phase 0.25 do NOT run. Most HDR projects are in this category.
- **Publication-target projects**: primary output is a manuscript to be submitted to a named journal. The website summary is still produced, but it is secondary. Phase −0.5 and Phase 0.25 are MANDATORY.

If the project is publication-target, state this in `proposal.md` on the first line:

```
**Target**: publication — primary venue: [journal name], fallback venue: [journal name]
```

If no journal is named, the project is not publication-target. Run it as website-target. A publication can always be spun out of a finished website-target project later, at which point Phase −0.5 and Phase 0.25 are run retroactively against the finished work before a submission is drafted.

### Why this phase exists

The Phase 2.75 and 3.5 reviewers catch *internal consistency* problems: does the abstract match §2.3, is the validation described in enough detail, are all references cited in the text. They do NOT catch *novelty weakness* or *venue mismatch*, because by that point the researcher has committed to a framing and a body of experiments. Phase −0.5 catches a different class of problem — "this idea cannot survive real peer review" — while the cost of a redirect is still a rewrite of one page.

A retroactive audit found that the most expensive projects on this methodology were not the ones that produced null results. They were the ones that produced interesting results in formats no journal would accept — synthesis papers pitched as novel derivations, unfalsifiable headline claims dressed as measurements, and bounds whose headline depended on parameters with unknown values.

### ⚠️ MANDATORY ARTIFACTS FOR PHASE −0.5

**Phase −0.5 is NOT complete and the project CANNOT proceed to Phase 0 unless ALL of these exist:**

- [ ] `proposal.md` (one page, structure below) in `applications/<project>/`
- [ ] `scope_check.md` written by a **different sub-agent invocation** from the HDR author — must be a fresh Agent call with no access to prior conversation
- [ ] `scope_check.md` ends with one of three literal strings: `VERDICT: PROCEED`, `VERDICT: REFRAME`, or `VERDICT: KILL`
- [ ] If the verdict is REFRAME, a `proposal_v2.md` (or v3) addressing the reviewer's specific points exists and has been re-reviewed
- [ ] If the verdict is KILL, the project is either downgraded to website-target or paused — it does not proceed as publication-target

### The one-page proposal

`proposal.md` is a single page — not a lit review, not an abstract. It captures the idea at the moment of commitment, before the literature has been read deeply enough to bias the framing. Five sections, each no more than a paragraph:

1. **Question.** One sentence describing the scientific question. No methodology, no deliverable — just the question.
2. **Proposed contribution.** One paragraph describing what the paper will claim. Concrete enough that someone reading it knows whether the claim is *new*, an *extension*, a *synthesis*, or an *application*. "We will derive X under condition Y" is specific; "we will explore Z" is not.
3. **Why now.** One paragraph on what makes this worth doing right now. What is the motivating development — a recent paper, an unexplained observation, a gap the literature keeps dancing around?
4. **Falsifiability.** One sentence describing the specific outcome that would kill the result. If nothing could kill it, the paper has no testable claim and the scope check will fail.
5. **Target venue.** One line naming the primary venue and one reason it is a fit (e.g. "PRE — publishes framework papers in stochastic thermodynamics").

### Running the scope-check reviewer

The scope-check reviewer is invoked as a **fresh sub-agent** with no access to the researcher's conversation. It reads only `proposal.md` and the relevant scope-check sections of `program.md`, and produces `scope_check.md`. Prompt template:

```
You are a grouchy physics reviewer at a top-tier journal. You reject
two papers out of three, and your job is to catch weak ideas before
their authors waste six months on them.

You have been given a one-page proposal for a research project. The
project has not been done yet — no lit review, no experiments, no data.
You are assessing whether the idea, as described, has any plausible
path to publication in the target venue.

Read the proposal. Do NOT be kind. Answer in ≤ 400 words:

1. Is the proposed contribution genuinely new? Name up to three existing
   papers the proposal would be competing with. If you find three close
   matches and the proposal does not differentiate clearly, the novelty
   claim is weak.
2. Is the falsifiability claim real, or is it unfalsifiable in disguise?
   A claim like "X tends to increase" or "the bound is consistent with
   observation" is not falsifiable — name it if you see it.
3. Would the target venue accept this kind of paper on its face? If the
   target is PRL and the claim is a synthesis paper, the venue is wrong.
4. What are the single most likely killer objections a real reviewer
   at that venue would raise? Name them explicitly.
5. End with exactly one of the literal strings:
   - VERDICT: PROCEED
   - VERDICT: REFRAME
   - VERDICT: KILL

A REFRAME verdict must list the specific proposal points to revise. A
KILL verdict is reserved for proposals that cannot be rescued — the
question itself has no plausible venue or no testable claim.
```

### Verdicts

- **PROCEED**: The project continues to Phase 0. The verdict and the reviewer's predicted killer objections are recorded at the top of `research_queue.md` so the lit review surfaces work that addresses them.
- **REFRAME**: The proposal is rewritten addressing the reviewer's specific points. The scope check is re-run on `proposal_v2.md`. Maximum two reframe cycles; a third non-PROCEED verdict automatically becomes KILL.
- **KILL**: The project does not proceed as publication-target. Two options — downgrade to website-target (drop the publication framing, continue under the standard website phases) or abandon the idea entirely. The decision and reason are recorded in `scope_check.md`.

### Why this gate is cheap

One sub-agent invocation. The reviewer reads about 400 lines of context (the proposal plus the scope-check sections of program.md) and produces 400 words. Compared to 200+ citations of lit review plus a full HDR loop, the scope check costs roughly an hour of compute against roughly a week. The asymmetry is the point.

---

## Phase 0: Literature Review

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 0

**Phase 0 is NOT complete and the project CANNOT proceed to Phase 0.5 unless ALL of these files exist on disk in `applications/<project>/`:**

- [ ] `papers.csv` with ≥200 verified citations (no fabrications)
- [ ] `literature_review.md` with 7 themes (or compact 4-theme version for descriptive-only projects), each theme section >1500 words
- [ ] `research_queue.md` with ≥100 hypotheses (compact: ≥30) each with prior, mechanism, design variable, metric, baseline
- [ ] `knowledge_base.md` with stylised facts + known pitfalls
- [ ] `feature_candidates.md` and `design_variables.md`

**Skipping Phase 0 or combining it with a previous project's Phase 0 is FORBIDDEN. If the project is a methodology clone, it still needs its own lit review — the substantive domain may differ even when the method is shared.**

**Do not skip. 200+ citations is the minimum; aim for 300–500 if the field is large; 1000+ for truly cross-disciplinary projects.** A shallow Phase 0 is the most expensive shortcut to take in HDR — almost every project that has needed major mid-loop pivots traces the failure to incomplete lit review.

### Deliverables
1. `literature_review.md` — 7 themes, 3000+ words each (was 2000)
2. `papers.csv` — 200+ entries minimum (was 100). Composition: 5–10 textbooks, 10–20 reviews, 60–100 recent results, 30–60 methods, 20–40 cross-disciplinary references
3. `feature_candidates.md` / `design_variables.md` — domain quantities → computable proxies
4. `research_queue.md` — **100+ hypotheses minimum** (was 20). Each one specifies its design variable, expected outcome, evaluation metric, baseline, and a Bayesian prior. The lit review's job is to surface the long tail of possible experiments, not just the obvious ones.
5. `knowledge_base.md` — established results, what works, what doesn't

### Themes
1. Domain fundamentals (textbooks, governing equations)
2. Phenomena of interest (mechanisms, precursors, known relationships)
3. Candidate features / design variables (the bridge from theory to computation)
4. ML/optimisation for this problem (what's been tried, what gaps remain)
5. Objective function design / feature engineering techniques
6. Transfer / generalisation across conditions
7. Related problems (cross-domain insights)

### Quality Gate
- [ ] 200+ papers.csv entries with 5+ textbooks, 10+ reviews
- [ ] 15+ candidate features/variables with physics justification
- [ ] **100+ hypotheses** in research_queue.md
- [ ] Can explain the domain physics without notes
- [ ] **The "enough citations" heuristic below has been satisfied**

### How many citations is "enough"? — the saturation heuristic

The 200-citation floor is a minimum, not a target. The right question is "have we covered the field well enough that the next paper we read is unlikely to change our priors?" Use these three independent saturation checks; the lit review is "enough" when all three are satisfied:

1. **Marginal information gain.** Track every new citation against the running `knowledge_base.md`. A new paper "contributes" if reading it adds at least one new fact, hypothesis, mechanism, or correction to the knowledge base. Maintain a rolling count of "contributing fetches per 10 fetches". When the rolling count drops to ≤ 1 in 10 (90 percent of new fetches add nothing), the citation graph is saturating. **Stop when 20 consecutive new fetches add zero new facts to `knowledge_base.md`.**

2. **Citation-graph closure.** As you add papers to `papers.csv`, also track which references each cited paper itself cites. The lit review is approaching closure when 90 percent of any new paper's references are already in `papers.csv` — the citation graph has been mostly traversed. Compute this ratio for the 10 most-recently-added papers and stop when the rolling average exceeds 0.9.

3. **Standard textbook coverage.** Identify the canonical textbook of the field (the book a graduate student in this discipline reads in their first year). For every chapter heading in that textbook, `papers.csv` should contain at least 3 references to current research that builds on that chapter. If any chapter has fewer than 3 representative papers, the lit review is missing a sub-area.

When all three are satisfied, the lit review is "enough". Most projects will hit this between 200 and 500 citations. A few cross-disciplinary projects (e.g. AI-for-physics, where the literature spans computer science AND a physics subfield AND multi-objective optimisation AND a specific dataset) may need 800+ citations before all three saturate.

**One more rule: do not stop early just because the count crossed a threshold.** A 250-citation lit review where 80 percent of fetches still add new facts is INCOMPLETE. A 180-citation lit review where 19 of the last 20 fetches added nothing is COMPLETE. The signal is the saturation, not the count.

---

## Phase 0.25: Publishability Review (publication-target projects only)

This phase runs between the literature review (Phase 0) and the baseline (Phase 0.5) for publication-target projects. It does NOT run for website-target projects — those go straight from Phase 0 to Phase 0.5.

### Why this phase exists

After the literature review, the researcher knows enough to state the contribution specifically: what is the claim, what has been done before, what is new. This is the cheapest moment at which a reviewer can catch novelty weakness, because the lit review output is fresh and no experiments have been committed to. Once Phase 0.5 runs, the project has picked a dataset or simulator and redirecting the framing costs much more.

Phase −0.5 caught the obvious dead ends before anyone read a paper. Phase 0.25 catches the subtler failures — ideas that looked plausible on a one-pager but, in the light of the lit review, turn out to be re-derivations of known work, or to rest on parameters nobody has measured, or to aim at a venue that does not publish this kind of paper.

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 0.25

**Phase 0.25 is NOT complete and the project CANNOT proceed to Phase 0.5 unless ALL of these exist:**

- [ ] `publishability_review.md` written by a **different sub-agent invocation** from Phase −0.5 (a fresh Agent call with no access to any prior conversation)
- [ ] All five checklist sections below are answered in `publishability_review.md` — none empty, none "N/A"
- [ ] `publishability_review.md` ends with one of three literal strings: `VERDICT: PROCEED`, `VERDICT: REFRAME`, or `VERDICT: KILL`
- [ ] If the verdict is REFRAME, a rewritten proposal (`proposal_v2.md`, v3, …) exists and a fresh publishability review has been run on it
- [ ] If the verdict is PROCEED, the reviewer's top three predicted killer objections are added to `research_queue.md` with the flag `pre-empt-reviewer`, so Phase 2 experiments address them pro-actively

**Forbidden shortcuts, each of which has been observed in practice and each of which invalidates the gate:**
- Running Phase 0.25 on the same sub-agent that did Phase −0.5 — FORBIDDEN; must be a fresh Agent call
- Self-reviewing ("I'll play the reviewer role") — FORBIDDEN
- Skipping Phase 0.25 because "the lit review already showed novelty" — FORBIDDEN; the lit review is input to this gate, not its verdict
- Skipping Phase 0.25 because "the scope check said PROCEED" — FORBIDDEN; the scope check ran on a one-pager before any literature was read
- "Short on context budget, will skip and run later" — FORBIDDEN; pause the project

### Reviewer inputs (read-only)

The publishability reviewer reads:
- `proposal.md` (or the latest `proposal_vN.md`)
- `literature_review.md`
- `knowledge_base.md`
- `research_queue.md`
- `scope_check.md` from Phase −0.5 (for context on what was already flagged)
- The Phase 0.25 section of `program.md`

Do NOT give the reviewer: `papers.csv` (raw citation list — too long, and the reviewer is supposed to form judgements from the synthesised lit review), any code, any experiment results (there are none yet).

### The five-point checklist

The reviewer produces `publishability_review.md` answering five sections, in order. Every section is mandatory — missing or empty sections mean the phase is not complete.

**1. Novelty taxonomy.** Categorise the proposed contribution into one of:
- *Extension* of a known result (e.g. adding a finite-time correction to a quasistatic bound)
- *Synthesis* of multiple known results into a unified framework
- *Application* of a known framework to a new domain
- *Genuinely new bound, proof, or prediction* not reducible to prior work

For *anything other than category four*, the reviewer names the specific prior work the contribution extends/synthesises/applies. For category four, the reviewer lists up to five papers that are the closest existing thing, forcing a specific comparison. If the reviewer cannot find any close comparisons, that is flagged as either genuine novelty or a deficient lit review — the researcher addresses which.

The reviewer is encouraged to be cynical about novelty claims. If the contribution is *synthesis* dressed as *genuinely new*, the gate catches it here, not after the paper is written.

**2. Falsifiability.** Name the specific measurable outcome that would kill the claim. If the claim is "X exists", the kill-outcome is "X is not detected on measurement set Y with sensitivity Z". If the claim is a bound, the kill-outcome is "dataset Y violates the bound". If no measurable outcome could kill the claim, the paper has no testable contribution and the verdict must be REFRAME or KILL.

Unfalsifiable-in-disguise patterns to watch for: "tends to increase", "is consistent with observation", "accounts for", "bridges frameworks". None of those, on their own, is a falsifiable claim.

**3. Load-bearing parameters.** List every numerical parameter the headline depends on. For each, give:
- The value used in the headline
- The literature-consensus uncertainty (range or confidence interval)
- How the headline scales in that parameter

Flag any parameter whose uncertainty is wide enough that the headline is not stable. A headline that reads "X is 1.5" when the underlying parameter is unknown over three orders of magnitude and X scales quadratically in it is actually "X is 0.015 to 146". Real reviewers catch this within the first page. The gate catches it before the paper is written.

**4. Venue fit.** Name two or three candidate journals. For each, give:
- One reason it is a fit (what class of paper does it publish?)
- One class of objection that venue typically raises

Example: "*PRE* — publishes framework papers in stochastic thermodynamics. Typical objection: demands rigorous derivation of any claimed new bound; heuristic interpolations are sent back for major revision."

If none of the named venues is a strong fit, the verdict is REFRAME (pick a better target, which may mean rewriting the contribution) or KILL.

**5. Killer objections.** The top three objections a human reviewer at the primary venue would raise, each scored *fatal / major / minor*. For each:
- State the objection specifically (not "novelty is unclear" but "the *B*(*r*) formula is claimed as derived but the paper shows only an interpolation between two limits")
- Name whether the current project plan has a way to address it
- If not, name the experiment, derivation, or reframing that would address it

**Any fatal objection without a clear mitigation plan makes the verdict REFRAME.**

### Verdicts

- **PROCEED**: All five checklist items are clear. No fatal objection is unaddressed. At least one named venue is a plausible fit. The reviewer's top three killer objections are added to `research_queue.md` as `pre-empt-reviewer` hypotheses — the Phase 2 experiment plan must include at least one experiment addressing each.
- **REFRAME**: One or more fatal problems — an unfalsifiable claim, poor venue fit, a load-bearing unknown parameter, or weak novelty. The researcher writes `proposal_v2.md` addressing the specific points raised and Phase 0.25 is re-run on it with a fresh sub-agent. Maximum two reframe cycles; a third non-PROCEED verdict is automatically KILL.
- **KILL**: The project cannot be reframed into a publishable paper. Two options — downgrade to website-target (the project still runs, the website summary is still produced, but the publication framing is dropped and Phase −0.5 and Phase 0.25 artifacts are archived) or abandon the project entirely. The decision is recorded in `publishability_review.md`.

### Why this gate is blocking

A fatal objection discovered at Phase 2.75 — after a month of experiments and a written draft — costs a rewrite of the paper. The same objection discovered at Phase 0.25 — before Phase 0.5 has even picked a dataset — costs a rewrite of one page of proposal. If a project cannot survive this gate, it has no business sinking the compute of Phase 0.5 through Phase 3.

The blocking design is not symmetrical with Phase 2.75. The 2.75 reviewer has concrete experiments to audit and can insist on re-runs. The 0.25 reviewer works on a proposal and a lit review, so its verdict is binary: either the idea can be pursued as publication-target (PROCEED), it needs to be reframed first (REFRAME), or it cannot be pursued as publication-target (KILL / downgrade). A "minor revisions" verdict is not available; minor problems are folded into the `pre-empt-reviewer` queue as part of a PROCEED verdict.

### Deliverables

```
applications/<project>/
├── proposal.md (or proposal_v2.md, proposal_v3.md)
├── scope_check.md                  # Phase −0.5 verdict
├── publishability_review.md        # Phase 0.25 verdict with 5-point checklist
└── research_queue.md               # Top three killer objections appended with flag pre-empt-reviewer
```

---

## Phase 0.5: Baseline Audit

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 0.5

**Phase 0.5 is NOT complete and the project CANNOT proceed to Phase 1 unless ALL of these exist:**

- [ ] `data_sources.md` listing every data source with direct URL, coverage, schema, smoke-test pass/fail
- [ ] Downloaded real data in `data/raw/` or `data/` (NO synthetic data unless explicitly justified per the REAL DATA ONLY rule below)
- [ ] `E00` row in `results.tsv` recording the baseline with seed, evaluation metric, numerical value
- [ ] Seed-stable — re-running the baseline must produce the identical number

**Skipping the `E00` baseline row is FORBIDDEN. Every project needs a numerical baseline against which improvement can be measured, even if the project is descriptive — in that case E00 is the "no-model climatology" line.**

1. **Read all code** — find bugs, suboptimal defaults, unused features/design freedom
2. **Decompose the score** — where does improvement effort have highest ROI?
3. **Validate the validation** — does it predict real-world performance?
4. **Audit data/simulation fidelity** — enough data? Realistic physics? Sufficient resolution?
5. **Missing data audit** — what would help but isn't available? What proxies exist?
6. Record baseline in `results.tsv`

### Simulation Realism (Option B only)
Before optimising, verify: all dominant physics included, hardware constraints enforced, sufficient resolution, validated against published results, dissipation/noise modeled, constraint violations reported.

### Symbolic Verification (Option D only)

Before starting the HDR loop, verify the CAS pipeline is trustworthy:

1. **Reproduce a textbook result.** Pick a known analytical result from the literature (a solved metric, a known energy condition, a published bound) and verify the pipeline reproduces it exactly. This is the Option D equivalent of "reproduce published SOTA" — if the CAS gives wrong answers on known cases, everything downstream is suspect.
2. **Grid convergence test.** When symbolic expressions are evaluated numerically on a grid (e.g., checking energy conditions at spatial points), run at 3 resolutions (e.g., 50/100/200 points) and verify the result changes by <1%. Record the convergence check in `results.tsv` as `E00_convergence`.
3. **Simplification sanity check.** Verify that `simplify()` or equivalent does not silently drop terms. Compare the full unsimplified expression evaluated at 5 test points against the simplified version. Disagreements > machine epsilon indicate a CAS bug or an invalid simplification assumption.
4. **Dimension/unit consistency.** For physics problems, verify that every term in every equation has consistent dimensions. A CAS will happily add meters to seconds. Catch this before the loop starts.

**Baseline for Option D:** The `E00` row in `results.tsv` records the baseline mathematical framework (typically the textbook/standard result) with its constraint satisfaction status. Example: `E00 | Alcubierre metric, standard GR | min(G00) = -0.583 | WEC_violated | KEEP | baseline`.

**Data sources for Option D:** `data_sources.md` lists the CAS libraries (with versions), any published symbolic results being reproduced, and references to the mathematical formulations being tested. There may be no "dataset" in the traditional sense — the "data" is the mathematical structure itself. This is acceptable; the synthetic-data prohibition does not apply to Option D because the expressions under study are the primary objects, not proxies for missing measurements.

### Use Published Simulators and Datasets — DO NOT BUILD YOUR OWN

**CRITICAL: Always use the standard published simulator or dataset for the field, even if it's slower or more complex than building your own.** Building a simplified custom simulator is almost always the wrong choice, even when it speeds up iteration.

**Why this matters:**
- Results from custom simulators are **not comparable** to published benchmarks. You cannot claim "we beat SOTA" unless you tested on the same simulator SOTA was measured on.
- Custom simulators tend to encode the same simplifications as the analytical baselines they replace. Beating an analytical baseline on a simulator that IS that baseline is meaningless.
- Custom simulators miss the physics that matters in reality. The optimisation will find solutions that exploit simulator artifacts rather than real phenomena.
- Reviewers and replicators will not trust results from a one-off simulator built by the same person making claims about it.

**The rule:**
1. **Identify the standard simulator/dataset** for your field during Phase 0 lit review.
2. **Use it.** Even if it is 100x slower than a custom alternative.
3. **If iteration speed is a problem**, fix it the right way: smaller test cases, lower resolution, fewer simulation steps, GPU acceleration of the standard tool, surrogate models trained on the standard tool's output. NOT a custom simulator.
4. **Validate the standard simulator reproduces published results** for a known case before starting HDR. If it doesn't, your installation is broken.
5. **Only build a custom simulator if there is genuinely no standard tool**, AND the lit review confirms this. Document why explicitly.

**Acceptable speed tradeoffs:**
- Use the standard simulator at lower fidelity (coarser mesh, fewer particles, shorter time)
- Use a published surrogate model trained on the standard simulator
- Use the standard simulator with GPU acceleration if available
- Cache expensive computations within the standard tool

**Unacceptable:**
- Reimplementing the simulator yourself "for speed"
- Replacing a complex physics simulator with a simple analytical model
- Building "the simplest possible simulator that captures the essence of the problem" — this almost always misses the essence

### REAL DATA ONLY — Never Generate Synthetic Data When Real Data Exists

**CRITICAL: Always use real measured data. Synthetic data generation is not a shortcut for "the download is annoying."**

This rule exists because a retroactive audit found that agents consistently defaulted to generating synthetic data calibrated to published statistics rather than downloading the actual datasets. Results from synthetic data reflect the calibration assumptions, not reality.

**The rule:**
1. **Always download the real dataset first.** If the API requires registration, register. If it requires pagination, paginate. If it requires manual CSV download, do it.
2. **Synthetic data is acceptable ONLY when ALL of these are true:**
   - The real data genuinely does not exist in any downloadable form
   - The project cannot proceed without it
   - The lit review confirms no open dataset exists for this problem
   - The synthetic generation method and calibration are documented with exact citations
3. **When synthetic data IS the only option:**
   - Label all results as "conditional on synthetic data" in the paper and website summary
   - The paper's limitations section must lead with this
   - Phase B discovery claims are strictly hypotheses, not findings
4. **Simulation-based projects (Option B) are exempt** — running a physics simulator (SUMO, ring-road IDM, PyPSA) is not "synthetic data", it's the project's evaluation method by design.

**Rubric impact for project selection:** If a candidate problem can only be answered with synthetic data (real data genuinely unavailable), apply a -3 penalty to the Data/Sim Availability dimension. Prefer problems where real open data exists. If the penalty drops the total below 24/30, do not select the project.

**If you find yourself writing `np.random` to generate training data for a project that has a real dataset listed in `data_sources.md`, STOP. You are making a mistake. Go download the real data.**

### Sanity Checks Before the HDR Loop Starts

Four cheap calibration runs before any HDR experiment. Each one is more valuable than a new experiment because they reveal whether downstream improvements can even be trusted.

1. **Reproduce published SOTA on the same system.** Run the published state-of-the-art method exactly as described — same simulator, same parameters, same optimiser — and verify your number is within 0.1–0.5% of theirs. A larger gap means your installation, simulator fidelity, or evaluation harness is broken. Fix the gap before starting the loop.
2. **Featurizer speed audit at 500 samples.** For Option A projects, time every off-the-shelf featurizer on a 500-sample subset before running on the full dataset. Featurizers that work on toy data can hang for hours on real scale. Cache featurization output to disk on the first run, not the tenth.
3. **Validation must not overlap training.** Run leave-one-condition-out CV alongside any holdout split. If they disagree, the holdout is overlapping training in disguise (same condition, same source) and reported gains are inflated. Trust the leave-one-out result. Do not pivot to ensembles or architecture changes until validation is honest.
4. **Linear baseline first.** Fit Ridge / Logistic on the raw features before trying any tree, NN, or ensemble. If tree methods are not >2× better than the linear baseline, the relationship is mostly linear and you should skip neural models entirely. They will not help and they will overfit.

---

## Phase 1: Tournament

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 1

**Phase 1 is NOT complete and the project CANNOT proceed to Phase 2 unless ALL of these exist:**

- [ ] `tournament_results.csv` with ≥4 model families compared on the same task
- [ ] At least one family is a **linear-model sanity check** (logistic regression, ridge, OLS)
- [ ] Corresponding rows in `results.tsv` for each tournament entry
- [ ] A clearly-stated winner (family + metric + value)

**For descriptive-only projects**: the tournament is still mandatory. Compare the climatology baseline, a simple linear regression, a ridge-regularised linear model, and a gradient-boosted tree predicting the descriptive summary as a function of the base covariates. Four families, running through the same evaluation harness. Skipping the tournament because "the project doesn't use ML" is FORBIDDEN — the tournament establishes what floor the descriptive analysis is answering against.

Compare 3-5 **fundamentally different** approaches (not hyperparameter variants) with ~5 experiments each on the same features/data. Record in `tournament_results.md`. Select 1-2 winners for the HDR loop.

Re-run the tournament if the HDR loop plateaus (5+ consecutive reverts).

### Tournament anti-patterns

- **Bagging beats boosting for small N.** When the tournament includes a task with N < 400 training examples, ExtraTrees / Random Forest typically beats XGBoost / LightGBM by 5–10%. The boosters overfit. Test bagging explicitly on small tasks.
- **Per-task model selection is mandatory.** Do not pick one model family for the whole project. Different tasks have different optimal model families, featurizers, and target transforms. Capture per-task winners in a decision table after the tournament — one-size-fits-all trades wins on ~50% of tasks.
- **Hard thresholds beat soft blends for bimodal targets.** When a target has a sharp physical boundary (metal ↔ nonmetal, stable ↔ unstable, present ↔ absent), use a two-stage classifier→regressor with a hard threshold, not a soft probability blend. Soft blends consistently lose.

### Phase 1 Variant: Framework Tournament (Option D)

For symbolic/analytical projects, the tournament compares **mathematical frameworks**, not ML model families. The question is not "which algorithm fits best?" but "which mathematical structure best satisfies the target constraints?"

**Procedure:**
1. **Identify ≥3 fundamentally different mathematical frameworks** from the Phase 0 literature review. These must be structurally distinct (different field equations, different symmetry groups, different dimensionality), not parameter variants of the same framework. Include the **textbook/standard framework as the baseline** (analogous to the linear-model sanity check).
2. **For each framework**, implement the symbolic expression in `ansatz.py` (or `src/metric_ansatze.py` or equivalent), compute all derived quantities (tensors, constraints, conservation laws), and evaluate the target constraint set.
3. **Record in `tournament_results.csv`**: framework name, constraint satisfaction (yes/no/partial), margin (how far from satisfaction), computational cost (CAS wall time), expression complexity (term count or leaf count of the simplified expression).
4. **Select 1-2 winner frameworks** for the Phase 2 HDR loop. The winner is the framework with the best constraint satisfaction margin, or (if multiple frameworks satisfy constraints) the simplest one.

**Example (warp drive):**
| Framework | min(G₀₀) | WEC satisfied? | Expression complexity |
|-----------|-----------|---------------|----------------------|
| F1: Standard GR (baseline) | -0.583 | No | 12 terms |
| F2: Kaluza-Klein 5D | -0.526 | No | 38 terms |
| F3: f(R) = R + αR² | -2.138 | No (worse) | 24 terms |
| F4: Einstein-Cartan | +0.006 | Yes (at s₀=5) | 18 terms |

**The linear-model sanity check equivalent:** The textbook/standard framework (e.g., standard GR for gravity problems, flat-space QFT for particle problems) must always be included. If a modified framework cannot beat the standard one on the target constraint, the modification is not useful.

**Option D code structure:**
```
applications/<project>/
├── src/
│   ├── ansatze.py            # Parameterised mathematical structures (metrics, Hamiltonians, ansätze)
│   │                         # Each function returns: expression, coordinates, parameters, framework ID
│   ├── field_equations.py    # Derived quantities: tensors, curvatures, conservation laws, etc.
│   ├── constraints.py        # Constraint checkers: energy conditions, positivity, unitarity, symmetry
│   └── __init__.py
├── run_experiments.py        # Orchestrates: pick ansatz → compute derived quantities → check constraints → record
├── tests/                    # TDD: one test per framework reproducing a textbook result
├── results.tsv
├── knowledge_base.md         # Accumulated symbolic facts (sign conditions, limiting cases, mechanism classifications)
├── research_queue.md
├── literature_review.md
├── papers.csv
├── design_variables.md       # Ansatz families and their free parameters
├── data_sources.md           # CAS library versions, reference results, mathematical formulations
├── tournament_results.csv
├── paper.md
├── generate_plots.py
├── plots/
└── discoveries/              # Minimal structures, analytical bounds, solution family classifications
```

`ansatze.py` is the Option D equivalent of `strategy.py` — it is the **only file modified during the Phase 2 HDR loop** (plus `constraints.py` if new constraint types are added). `field_equations.py` and `run_experiments.py` are infrastructure, fixed after Phase 1.

---

## Phase A → Phase B Bridge

### ⚠️ MANDATORY CHECK BEFORE PHASE B

**Phase A (Infrastructure) is NOT complete and the project CANNOT proceed to Phase B (Discovery) unless:**

- [ ] Feature availability check run on 5-10 synthetic candidates spanning the design space (no feature defaults to placeholder)
- [ ] Predictor returns scores in the same range on synthetic candidates as on training data
- [ ] Stability/feasibility post-filter specified and implemented
- [ ] Combinatorial template inventory for Phase B (≥3 template families documented)

A common Phase A → Phase B failure: the predictor improves in training but cannot rank novel candidates because features it relies on are not available outside the training set. Catch this before scaling discovery.

### Feature availability check

For every feature in the predictor, verify it can be computed for an arbitrary candidate (not just training-set members). If a feature requires data that is only present for training samples (e.g. crystal structure for compositional candidates), it will default to a placeholder on candidates and the predictor will systematically under-rank them.

Add this test:
1. Generate 5–10 synthetic candidates that span the design space.
2. Run the featurizer on them. Verify no feature defaults to a placeholder value.
3. Verify the predictor returns scores in the same range as on training data.

### Combinatorial template diversity beats predictor improvement

In Phase B the highest-impact lever is usually the **diversity of candidate templates**, not the predictor's MAE. Going from 1 template family to 5 typically yields 2–10× more discoveries. A modest predictor improvement typically yields none. Allocate Phase B effort to templates first, predictor refinement second.

### Stability / feasibility post-filter

For materials, designs, and any domain with a "physically realisable?" constraint, run a lightweight feasibility filter on the top-K predictions from the predictor. Universal ML potentials and constraint solvers are typically fast (1–10 seconds per candidate). Throw away anything infeasible. This removes predictions that exploit model weaknesses and restores honest discovery counts.

---

## Phase 2: The HDR Loop

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 2

**Phase 2 is NOT complete and the project CANNOT proceed to Phase 2.5 unless ALL of these exist:**

- [ ] ≥20 rows in `results.tsv` with `status` ∈ {KEEP, REVERT} (compact bar; preferred target 100+)
- [ ] Every KEEP experiment ties to a git commit
- [ ] Every KEEP experiment re-runs deterministically from cache
- [ ] `knowledge_base.md` updated after each KEEP with what was learned
- [ ] `research_queue.md` updated with status changes on each experiment

**For descriptive projects**: the 20+ experiments are variations of the descriptive analysis — bootstrap CIs on the headline, subset analyses (pre/post-COVID, large/small entities, sector-by-sector), placebo/shuffle tests, different outcome thresholds, different time windows. Each appears as a row in `results.tsv`. Skipping Phase 2 because "there is no model to iterate" is FORBIDDEN — every project has robustness dimensions that constitute Phase 2.

**Run hundreds of experiments. The 20-experiment-loop pattern from the early HDR projects was too short.** A real HDR project should run **100 experiments minimum** in Phase 2 before declaring convergence, and projects with rich research queues should run **300–1000+** experiments. Each experiment is cheap if the evaluation harness is fast; the cost is in the per-experiment thinking (prior, mechanism, single change), not in the compute.

```
1. Pick Question        ← highest-impact OPEN from research_queue.md
2. State Prior          ← probability (0-100%) BEFORE testing
3. Articulate Mechanism ← WHY would this work? Causal story.
4. Implement ONE Change ← git commit BEFORE running
5. Evaluate             ← run on ALL tasks
6. Record Results       ← append to results.tsv (no cherry-picking)
7. Update Beliefs       ← keep or revert
8. Update Knowledge     ← knowledge_base.md, research_queue.md, observations.md
```

### Experiment Priority
1. Fix bugs (highest ROI)
2. Domain-informed features / design parameterisations
3. Data utilisation / simulation fidelity
4. Training improvements
5. Architecture changes
6. Speed optimisation

### Hypothesis Selection: Impact Scoring

"Highest-impact first" must be explicit, not vibes. Each hypothesis in `research_queue.md` gets a 3-axis score:

| Axis | 1 (low) | 2 (medium) | 3 (high) |
|------|---------|------------|----------|
| **Expected Δ** | < noise floor | 1–3× noise | > 3× noise |
| **Novelty** | Standard technique, well-explored | Published but untested in this domain | No prior work; genuinely new combination |
| **Mechanistic clarity** | "Might help" | Plausible causal story | Clear physics/domain mechanism with literature support |

**Impact = Expected Δ + Novelty + Mechanistic clarity** (range 3–9). Pick the highest-scoring OPEN hypothesis. Break ties by preferring the one with the prior closest to 0.5 (maximum expected information gain — see Prior Discipline below).

**Long-shot quota:** At least 20% of hypotheses in `research_queue.md` must have a stated prior ≤ 0.3. This prevents the queue from being dominated by "safe" confirmatory hypotheses. If the queue falls below the 20% long-shot ratio after pruning, add new speculative hypotheses from the literature before continuing. Long-shots are where the surprising discoveries come from — the methodology must not systematically avoid them.

### How many experiments is "enough"? — the saturation heuristic for Phase 2

Mirroring the Phase 0 saturation rule: stop the HDR loop when both signals fire.

1. **Sustained revert streak.** When 20 consecutive experiments are reverted (no improvement above the noise floor), the local search is exhausted. Re-run Phase 1 (tournament) to look for a fundamentally different approach, or stop and write the paper.
2. **Research-queue exhaustion.** When fewer than 5 hypotheses remain OPEN in `research_queue.md` AND each has a Bayesian prior below 20 percent, the productive ideas are gone. Add 20+ new hypotheses from a fresh pass over the lit review, or stop.

Stopping at 100 experiments because you "hit the count" is wrong if either signal still says "keep going". Stopping at 50 experiments because the research queue is exhausted AND the last 20 experiments were all reverts is correct.

### Principles
- **Domain-first**: every hypothesis grounded in domain science
- **Isolation**: one change per experiment (but see Interaction Sweep below)
- **Bayesian**: state beliefs before data, update after (see Prior Discipline below)
- **Cumulative**: every experiment produces knowledge, even failures
- **Plateau detection — distinguish optimisation plateau from physical floor.**
  - **Optimisation plateau** (5+ consecutive reverts at moderate margins): re-tournament. The HDR loop has exhausted the current approach.
  - **Physical floor** (improvements smaller than the simulator's noise floor across many experiments): pivot to a new problem dimension instead of pushing harder. If a fundamental physical limit is binding, no amount of optimisation will help. Move to a different objective, hardware regime, or problem formulation.
- **Tighten the revert threshold late-loop.** Early experiments (1–20) accept any positive Δ above noise. Mid-loop (20–50), require Δ > 2× the experimental noise floor. Late-loop (50+), require Δ > 3× noise OR a parallel benefit (inference speed, robustness, simplicity). Otherwise the loop drowns in tied experiments.

### Mandatory experiments for reporting-channel outcomes

**When the outcome is observed via a reporting mechanism — any filing, claim, permit, registration, scrape, or self-report that is optional, thresholded, or channel-dependent — Phase 2 MUST include a lookalike placebo.** This is distinct from the standard fake-treatment placebo (which tests identification) and from the alternative-treatment placebo (which tests treatment specificity). It tests whether the *outcome definition itself* is biased by the channel through which outcomes are observed.

**Why this matters.** Many "outcomes we care about" differ from "outcomes we can observe": funding vs SEC filings, closure vs website resolution, hospitalisation vs insurance-claim records, permits vs open-data entries, employment vs W-2 issuance, etc. If the treated group and the matched-control group use the reporting channel differently — even when they behave identically on the underlying outcome — the observed difference is a channel artefact, not a treatment effect. A standard placebo will cleanly return null while your primary ATT remains silently wrong.

**The lookalike-placebo procedure.**
1. Fit the primary propensity model P(treated | X) on the full treated-vs-control universe.
2. Take the top-N untreated units by propensity score — these are the untreated units that most structurally resemble treated units on observables.
3. Compare their observed outcome rate against the remaining untreated pool.
4. Interpret: a large, clean gap (|RD| > 10 pp with CI excluding zero, where the treatment ATT itself is much smaller or null) is evidence that your matched controls are channel-selected rather than behaviour-selected, and your primary ATT is biased in the direction of the gap.

**When the lookalike placebo fires.** Report the gap prominently (headline findings, not appendix). Acknowledge in the paper that the primary ATT is a lower/upper bound rather than a point estimate. Consider whether a channel-corrected outcome is feasible (e.g. combining filings with web-scrape survival, claims with registry, permits with satellite imagery) before pushing the ATT as the headline result.

**When the lookalike placebo returns null** (the top-propensity untreated have outcomes similar to the rest), the channel is well-calibrated across the treated-control comparison and the primary ATT can be interpreted conventionally.

Document the result of the lookalike placebo in every paper whose outcome is channel-observed. Skipping it for such outcomes is a cherry-pick — you are implicitly choosing not to look at a failure mode that the design makes highly likely.

### Interaction Sweep (Phase 2.5)

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 2.5

**Phase 2.5 is NOT complete and the project CANNOT proceed to Phase 2.75 unless:**

- [ ] ≥1 pairwise-interaction experiment row in `results.tsv` tagged `interaction=True`
- [ ] If ≥2 near-miss rejects exist: all N×(N-1)/2 pair combinations tested
- [ ] Any synergistic pair documented in `knowledge_base.md`

**If the Phase 2 experiments produced no near-miss rejects (within 1× noise of KEEP threshold), Phase 2.5 runs the minimum valid sweep: at least one interaction test between the top-2 KEEP experiments, to confirm they are additive or identify any conflict. Writing "no near-misses" and skipping is FORBIDDEN.**

The isolation principle is analogous to coordinate descent: it finds improvements along single axes but misses combinatorial effects. A change that fails in isolation may succeed in combination with another. After the main Phase 2 loop converges, run an interaction sweep to catch these.

**When to run:** After Phase 2 converges (sustained revert streak OR research-queue exhaustion), before writing the paper.

**Procedure:**
1. **Collect near-miss rejects.** From `results.tsv`, identify all reverted experiments where the result was within 1× the noise floor of the KEEP threshold (the "almost worked" changes). Take the top N candidates (N ≤ 8, typically 5).
2. **Run a fractional factorial.** Test all pairs of near-miss rejects applied simultaneously (N×(N-1)/2 experiments). For N=5 this is 10 experiments; for N=8 this is 28. Each experiment applies exactly two reverted changes together.
3. **Escalate winners.** Any pair that passes the KEEP threshold is kept as a unit. If multiple pairs win, test the union of all winning pairs as a single experiment.
4. **Record interaction findings.** In `results.tsv`, tag interaction experiments with `interaction=True` and note which individual experiments they combine. In `knowledge_base.md`, document which interactions were synergistic and hypothesise why — this is often a genuine discovery about the problem structure.

**What this is NOT:** It is not a full combinatorial search (2^N is intractable for large N). It is a targeted sweep over the most promising rejected changes. The methodology is closer to coordinate descent with a post-hoc pairwise interaction check than a full design-of-experiments approach. This is an explicit trade-off: tractability over completeness.

**Scope limit:** If no reverted experiments are within 1× noise of the KEEP threshold, skip the interaction sweep — the rejected changes were clearly bad individually and unlikely to rescue each other.

### Prior Discipline

Bayesian priors are only useful if they are (a) calibrated, (b) used to order work, and (c) updated after each experiment. Without all three, stating a prior is performative rather than functional.

#### 1. Calibration Tracking

After every 20 experiments, compute a calibration check: bin all stated priors into buckets (0–0.3, 0.3–0.5, 0.5–0.7, 0.7–1.0) and compare the stated probability against the actual KEEP rate in each bucket. Record this in `results.tsv` as a calibration row.

- If priors in the 0.7–1.0 bucket have a KEEP rate below 0.4, the agent is systematically overconfident. Apply a blanket 0.7× deflation to all future priors until the next calibration check.
- If priors in the 0–0.3 bucket have a KEEP rate above 0.5, the agent is systematically underconfident about long-shots. Raise the long-shot quota (see Hypothesis Selection above) to 30%.
- If calibration is reasonable (within ±15pp per bucket), no adjustment needed.

Over time this produces a calibration curve that is itself a finding about how well the methodology predicts its own outcomes.

#### 2. Prior-Informed Queue Ordering

Hypotheses where the prior is far from 0.5 (strong belief either way) are less informative — you mostly already know what will happen. Hypotheses near 0.5 with high impact scores should go first because they maximise expected information gain.

**Ordering formula:** When two hypotheses have the same impact score, break ties by preferring the one whose prior is closest to 0.5. When impact scores differ, impact wins — a high-impact hypothesis at 0.8 prior still beats a low-impact one at 0.5 prior. But among equals, chase uncertainty.

#### 3. Posterior Updating

After each experiment, compute and record the updated belief:
- **KEEP result**: posterior = prior × 1.5 (capped at 0.95) for related hypotheses in the same cluster (e.g. if a VIX feature worked, raise priors for other volatility features)
- **REVERT result**: posterior = prior × 0.5 for related hypotheses

Record the posterior in `research_queue.md` alongside the prior. If a cluster of related hypotheses all converge toward posterior < 0.1 after multiple experiments, retire the cluster — the mechanism is not active in this problem. Conversely, if a cluster converges toward posterior > 0.8, the mechanism is confirmed; shift effort elsewhere.

This prevents two failure modes: (a) endlessly testing variants of a dead idea, and (b) abandoning a productive direction after a single failure.

#### 4. Known Bias Corrections

Stated priors are systematically wrong in characteristic directions. Adjust accordingly:

- **Training-trick priors are overconfident.** Hyperparameter tweaks (LR schedules, weight decay, optimiser changes, init strategies, loss-function variants) feel plausible but rarely transfer. Default prior should be ≤ 30% for any standard ML training trick on a problem where the data is small or physics-rich. If your gut says 60%, write down 30%.
- **Domain-feature priors are well-calibrated.** A new feature derived from domain physics with a clear mechanistic story typically lands in the 40–60% range and the realised hit rate matches.
- **Architecture-pivot priors are catastrophically overconfident.** Switching model families feels like a 50% bet but realised success is closer to 10%. Demand strong motivation; do not pivot architectures because the loop is plateauing.
- **Inference / speed-optimisation priors are well-calibrated and stack reliably.** Treat inference-level optimisation (binary I/O, manual scaling, operator fusion, caching) as a separate axis from accuracy. It is reliable, it compounds, and it never hurts the score. Run these in parallel to accuracy work.

### Anti-Patterns to Watch For

- **"Slightly tied" experiments are a sign Occam has won.** If a more complex variant is statistically tied with a simpler baseline (Δ < 0.5pp or < experimental noise), revert. Keeping the complex variant adds noise to the next experiment's signal.
- **Per-scenario regressions hide under positive means.** Always report per-scenario / per-task / per-condition results, not just aggregate. A +5% mean improvement that includes a +200% catastrophe on one condition is a regression, not a win. The aggregate mean can be a lie.
- **Absolute conditions scale; relative thresholds don't.** Rules of the form `queue == 0` (drain fully) or `confidence > 0.9` scale across regimes. Rules of the form `current − other > K` or `improvement > 5%` work in one regime and break in others. Prefer absolute conditions.
- **Random initialisation is malpractice for parameterised search.** Never start gradient-based pulse / waveform / neural ODE / Fourier basis search from random parameters. Always warm-start from a known-good baseline (analytical solution, published seed, transfer-learned weights). Random init converges to local minima with 10–100× worse fidelity.
- **Cache custom featurization on first run.** A featurizer that takes 35 seconds on first run takes 35 milliseconds on the second if cached to disk. Add the cache the moment you write the featurizer, not after the loop is slow.

### Phase 2 Variant: Decomposition Loop (for Option C projects)

When the goal is to reverse-engineer an existing AI-discovered or black-box solution rather than to forward-optimise a new one, the HDR loop runs in a different rhythm. Replace steps 1–8 above with:

```
1. Pick component / parameter to ablate     ← from a structured list of all components
2. State expected effect                    ← Bayesian prior: essential / important / redundant
3. Ablate one thing                         ← set to 0, infinity, or remove; commit before measuring
4. Measure performance change               ← <1.2× degradation = redundant, 1.2–2× = important, >2× = essential
5. Cross-validate the finding               ← run on a second independent simulator OR against published results
6. Rebuild the minimal essential design     ← only the essentials that survived ablation
7. Re-optimise the simplified design        ← one or two parameters the original may not have tuned
8. Survey solution family                   ← repeat the decomposition on 3–5 solutions; classify by mechanism
```

#### Decomposition-mode rules

- **Component ablation before parameter sweeps.** First identify which components are essential (binary on/off ablation). Only sweep parameters of components that survive. Sweeping parameters of redundant components wastes effort and gives misleading sensitivity curves.
- **Distinguish narrow optima from broad robustness.** A parameter sweep gives you a sensitivity curve. Sharp peaks (±5% kills the design) indicate real physics — lock down tight specifications. Broad plateaus indicate the optimiser over-parameterised a robust choice — simplify or reoptimise.
- **Cross-validate decomposition against an independent source.** Differentiable simulators and step-based simulators can disagree on internal scales. Verify the dominant mechanism on both before publishing the interpretation.
- **Survey the family, don't extrapolate from one solution.** After decomposing the best solution, decompose 3–5 others from the same family. They may use distinct mechanisms (e.g. signal amplification vs noise suppression). The "explanation" of the AI's discovery may be plural.
- **Verify the simplified design reaches or beats the original.** A successful decomposition produces a minimal design that, after re-optimising 1–2 free parameters, matches or exceeds the original AI-discovered performance. If it doesn't, you removed something essential.

### Phase 2 Variant: Symbolic Analysis Loop (for Option D projects)

When the evaluation oracle is a CAS rather than a dataset or simulator, the HDR loop runs with a different vocabulary but the same discipline. Replace steps 1–8 above with:

```
1. Pick structure to test          ← ansatz modification, coupling term, boundary condition, symmetry constraint
2. State prior                     ← probability that this structure satisfies the target constraint
3. Articulate mechanism            ← mathematical reasoning: WHY would this term/structure produce the desired property?
                                     (sign argument, symmetry argument, dimensional argument, limiting-case argument)
4. Implement ONE symbolic change   ← modify ansatz.py or equivalent; git commit BEFORE evaluating
5. Evaluate symbolically           ← compute derived quantities via CAS → check constraint set → grid-evaluate if needed
6. Record results                  ← append to results.tsv (see schema below)
7. Update beliefs                  ← KEEP (constraint improved or satisfied) or REVERT (no improvement or regression)
8. Update knowledge                ← knowledge_base.md gains a symbolic fact; research_queue.md updated
```

#### Option D results schema

Option D experiments produce hybrid results — symbolic expressions AND numerical evaluations. The `results.tsv` schema is extended:

```
experiment_id | description | constraint | margin | status | symbolic_result | notes
E00           | Alcubierre, std GR | WEC | -0.583 | KEEP | G00 = -(dv/dx)²f² < 0 always | baseline
E01           | +torsion, s0=1 | WEC | -0.412 | REVERT | correction has right sign but too small | need s0 >> 1
E02           | +torsion, s0=5 | WEC | +0.006 | KEEP | H00 dominates G00 at s0>4.3 | critical threshold found
```

**Key columns:**
- `constraint`: the target mathematical property being checked (WEC, NEC, unitarity, positivity, convergence, symmetry class, etc.)
- `margin`: numerical distance from constraint satisfaction. Positive = satisfied, negative = violated. For binary constraints (symmetry yes/no), use 1/0.
- `symbolic_result`: the key symbolic expression or classification from this experiment. Keep it to one line; put the full derivation in `knowledge_base.md`.

#### Symbolic-mode rules

- **Sign arguments before parameter sweeps.** Before scanning parameter ranges, check whether the modification has the *right sign* to improve the target constraint. A correction term with the wrong sign will never help, regardless of parameter values. The warp drive f(R) framework failed this test — the correction amplified WEC violation regardless of the coupling constant. Catching wrong-sign terms symbolically saves dozens of numerical experiments.

- **Limiting cases as free theorems.** Every new ansatz should be evaluated in at least two limiting cases (e.g., weak-field, flat-space, zero-coupling, infinite-coupling). If the expression doesn't reduce to the expected result in a known limit, the implementation has a bug. These are free sanity checks — the CAS does them instantly.

- **Simplification is an experiment, not just cleanup.** After a KEEP result, explicitly simplify the winning expression and record the simplified form as a separate experiment. Often the simplified form reveals the *essential mathematical mechanism* — which terms actually matter and which are along for the ride. Example: "the torsion correction reduces to H₀₀ ∝ s₀² |∇f|² in the thin-wall limit" is a discovery that the full expression obscures.

- **Expression complexity as a secondary metric.** Track the term count (or SymPy `count_ops()`) of each expression. Between two frameworks that both satisfy the constraint, prefer the simpler one. Complexity is measured after simplification. This is the symbolic equivalent of Occam's razor.

- **Cross-validate symbolic results numerically.** Every symbolic KEEP must be spot-checked by numerical evaluation at ≥5 test points (not just the grid used during evaluation). CAS simplification can silently drop terms, introduce branch cuts, or assume variable signs. Numerical cross-validation catches these.

- **Parameter-regime mapping after structural search.** Once a framework is confirmed to satisfy the target constraint for at least one parameter value, map the full parameter regime: scan the key parameters and record the boundary where constraint satisfaction flips. This boundary (a curve or surface in parameter space) is a primary result of Option D projects.

#### Phase B for Option D: Analytical Discovery

Phase B for symbolic projects produces one or more of these artifacts:

1. **Minimal sufficient structure.** Strip the winning framework down to the fewest terms that still satisfy the target constraint. This is the symbolic equivalent of "inverse design" — what is the simplest mathematics that works?
2. **Analytical bounds.** Derive closed-form expressions for the parameter regime where the constraint is satisfied. Example: "WEC requires s₀ > 4.3 √(v/c) for bubble velocity v."
3. **Classification of solution families.** If multiple frameworks satisfy the constraint, classify them by the mathematical mechanism (sign flip via torsion vs. sign flip via bulk geometry vs. sign flip via higher-order curvature). This survey of the solution space is the highest-value Phase B output.
4. **Conjectures and proof sketches.** If the numerical parameter scans suggest a general pattern (e.g., "all frameworks satisfying WEC require a topological correction"), state it as a conjecture with supporting evidence and record it in `knowledge_base.md`.

---

## Phase 2.75: Adversarial Results Review

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 2.75 — ZERO SHORTCUTS ALLOWED

**Phase 2.75 is NOT complete and the project CANNOT proceed to Phase 3 (paper) unless ALL of these exist:**

- [ ] `paper_review.md` written by a DIFFERENT sub-agent invocation (not the HDR author) — the reviewer file must be created by a fresh Agent call with no access to prior conversation
- [ ] Every reviewer-mandated experiment appears in `results.tsv` with `status` ∈ {RUN_RV, CONTROL, TEMPORAL, DIAG}
- [ ] `review_response.md` (or equivalent) explicitly addressing each reviewer finding with FIX / REBUT / ACKNOWLEDGE

**Forbidden shortcuts, each of which has been observed in practice and each of which will require paper retraction:**
- Skipping the reviewer entirely and writing a paper with "limitations" baked into §8 — FORBIDDEN
- Self-reviewing ("I'll play the reviewer role") — FORBIDDEN; the reviewer must be a different sub-agent invocation
- Running the reviewer but ignoring the mandated experiments — FORBIDDEN
- Marking Phase 2.75 "complete" because the reviewer file exists but experiments are unrun — FORBIDDEN
- "This is a descriptive analysis so a reviewer would have nothing to add" — FORBIDDEN; descriptive projects have real flaws (endpoint sensitivity, uncertainty, confounds) that a reviewer catches
- "Short on context budget, will skip reviewer and run it later" — FORBIDDEN; pause the project instead

**Mandatory. Do not skip. Do not combine with the HDR agent's own context.**

After Phase 2.5 (interaction sweep) converges and before writing the paper, a **separate reviewer agent** audits the project. The reviewer must run in a fresh context with no access to the HDR agent's conversation history — it sees only the project artifacts on disk. Its job is to find flaws, not confirm quality.

### Reviewer inputs (read-only)

The reviewer reads these files from `applications/<project>/`:
- `results.tsv` — every experiment result
- `knowledge_base.md` — accumulated claims
- `research_queue.md` — what was tested and what wasn't
- `literature_review.md` — what the literature says
- `model.py`, `evaluate.py` — the code
- `data/` — the actual data (or `data_sources.md` to fetch it)

### Review protocol

The reviewer produces `review.md` with structured findings:

**1. Reproducibility check.** Re-run 5 randomly selected experiments from `results.tsv` using the committed code. Verify the numbers match within the stated noise floor. Flag any that don't.

**2. Cherry-picking audit.** Compare the number of git commits tagged as experiments to the number of rows in `results.tsv`. They should match. Check that REVERT experiments are recorded, not just KEEPs. Flag any gaps.

**3. Overclaiming check.** For every claim in `knowledge_base.md`, trace it to a specific experiment in `results.tsv`. Flag any claim not directly supported by experimental evidence. Check that effect sizes are described accurately (not rounded up, not stripped of uncertainty).

**4. Statistical validity.** Check whether reported improvements exceed the experimental noise floor. Check for per-task regressions hidden under positive aggregate means. Check whether the evaluation metric is appropriate for the claim being made.

**5. Missing experiments.** This is the highest-value step. The reviewer proposes 5–10 experiments that the HDR agent did not run but should have, given the literature review, the results so far, and obvious robustness/generalisability gaps. These are not optional suggestions.

**6. Scope and framing audit.** Check whether the headline finding, title, and abstract carry appropriate qualifiers. Flag any result presented without the conditions under which it holds (e.g. "works on a single-lane ring road" omitted from a claim about traffic).

### Each finding has a severity

| Severity | Definition | HDR agent obligation |
|----------|-----------|---------------------|
| **CRITICAL** | Result is wrong or unreproducible | Must fix before proceeding |
| **MAJOR** | Overclaim, missing qualifier, or significant gap | Must fix or rebut with specific experimental evidence |
| **MINOR** | Style, clarity, or a nice-to-have experiment | Should fix; may acknowledge as limitation |

### HDR agent response protocol

The HDR agent writes `review_response.md` addressing every finding. Each response must be one of:

- **FIX** — change the code, re-run the experiment, or revise the claim. Show the diff or new result.
- **REBUT** — cite a specific experiment (by ID in `results.tsv`) that contradicts the finding. "I disagree" without evidence is not a valid rebuttal.
- **ACKNOWLEDGE** — add to `knowledge_base.md` limitations and flag for the paper's Discussion section.

### Suggested experiments are mandatory

**When the reviewer proposes missing experiments, the HDR agent MUST run them.** This is not optional. The reviewer's missing-experiment suggestions are treated as new entries in `research_queue.md` with priority above all remaining queued hypotheses. The HDR agent:

1. Adds each suggested experiment to `research_queue.md` with a prior and mechanism (the reviewer may suggest these, or the HDR agent states them).
2. Runs each experiment through the standard Phase 2 loop (implement, evaluate, record, update).
3. Reports results in `review_response.md` with the experiment ID from `results.tsv`.

If a suggested experiment reveals a problem (e.g. the headline finding doesn't hold under different conditions), this is a genuine discovery and must be reported honestly — not suppressed. The paper must reflect whatever the experiments show, even if it weakens the headline.

### Second pass

After the HDR agent submits `review_response.md`, the reviewer gets one more pass. If all CRITICAL and MAJOR findings are resolved, the reviewer signs off. If not, the cycle repeats. Maximum 3 review rounds — if findings are still unresolved after 3 rounds, they go into the paper as open limitations.

### Deliverables

```
applications/<project>/
├── review.md              # Reviewer's structured findings
├── review_response.md     # HDR agent's responses + new experiment results
└── review_signoff.md      # Final reviewer pass — approved or open items noted
```

---

## Phase 3: paper.md (the only writeup the project owns)

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 3

**Phase 3 is NOT complete and the project CANNOT proceed to Phase 3.5 unless:**

- [ ] `paper.md` exists in `applications/<project>/`
- [ ] Every KEEP experiment in `results.tsv` is referenced by its ID in `paper.md`
- [ ] Abstract, Introduction, Detailed Baseline, Detailed Solution, Methods, Results, Discussion, Conclusion, References sections all present
- [ ] ≥30 citations from `papers.csv` used inline
- [ ] `generate_plots.py` exists and runs; `plots/` directory populated; paper references plots by filename
- [ ] Three mandatory plots produced: predicted-vs-actual scatter, feature importance, headline-finding
- [ ] No references to internal review process (words "reviewer", "sub-agent", etc. absent)
- [ ] No work-effort metrics ("we ran 34 experiments", "200 citations reviewed") in the paper body

**Writing paper.md from the website summary is FORBIDDEN — the paper is the canonical source and must have full technical depth. Copying the website index.md and calling it paper.md is a shortcut that violates the Detailed Baseline / Detailed Solution depth requirement.**

After the review cycle is complete (reviewer sign-off obtained), produce a single deliverable: `paper.md`, a formal academic paper. This is the canonical source of truth for the project. The public-facing website summary is generated automatically by the website summary pipeline (`~/website/pipeline/`) directly from `paper.md` — projects no longer maintain their own `summary.md`.

### `paper.md` — Formal academic paper

A publication-quality academic paper. Structure:

1. **Abstract** — 200-300 words. Problem, method, key result, novelty.
2. **Introduction** — context, prior work, the gap this paper fills. Cite the foundational papers in the field.
3. **Methods** — simulator/dataset (with version), baseline, HDR protocol, evaluation metric. Reproducible from the description alone.
4. **Results** — every kept experiment, with tables and figures. Quantitative findings. Number every claim.
5. **Discussion** — physical interpretation, why it worked, what surprised us, limitations, threats to validity, what wasn't tested.
6. **Conclusion** — punchline + implications + future work.
7. **References** — 30+ citations from `papers.csv`, properly formatted (numbered or author-year, consistent throughout).

**Quality bar**:
- Every claim cited
- Every number traceable to a specific experiment in `results.tsv`
- Honest about limitations and what wasn't tested
- A reviewer should be able to replicate the work from the paper alone
- Match the conventions of the target venue (Phys. Rev. Letters, Nature Communications, or domain-specific journal)
- Standard academic tone — not breathless, not understated
- Write the paper LAST so it reflects the full HDR journey, not the original hypotheses

**Writing rules** (apply to both `paper.md` and any derived public summary):

- **Always expand abbreviations on first use.** Every acronym, shorthand, Greek letter or symbol must be spelled out the first time it appears, with the abbreviated form in parentheses, before it is used standalone. This applies even to "well-known" abbreviations — the audience may not know them. Subsequent mentions in the same document can use the short form.

- **Every paper.md and every derived public summary must contain a Detailed Baseline section and a Detailed Solution section as standalone sections.** These are in addition to the methodology section, not replacements for it.

  The **Detailed Baseline section** describes what the baseline algorithm / dataset / design actually is, in enough depth that an unfamiliar reader can understand it without external references. It must include: the name of the baseline, its mathematical formulation (formulas, equations) if applicable, its historical and theoretical origin, what it actually computes or produces step by step, its assumptions and known failure modes, the specific parameter values used in this study, and a justification for why it is the right comparison target. Examples of what counts as "the baseline" depend on the project type — it might be an analytical formula, a published algorithm, a published reference design, or a standard dataset preprocessing pipeline.

  The **Detailed Solution section** describes the final discovered solution in equivalent depth. It must include: the name of the solution, the mathematical formulation, the actual final code block for code-based solutions, a step-by-step explanation of how it works, the causal mechanism for why it works, the concrete differences from the baseline, the assumptions and limits, and how to reproduce it starting from the baseline. The reader should be able to read the code (or equations) and understand what changed.

  The reader should be able to reach the end of these two sections and understand both (a) the prior state of the art well enough to reproduce it, and (b) the new contribution well enough to reproduce it, without needing any external context.

- **The methodology section answers two questions only**: (a) what was the baseline and how was it calculated, with enough detail for reproduction, and (b) how did the project iterate on the baseline to reach the final result, including what classes of hypothesis were tested and what the keep-vs-revert criterion was. The methodology section MUST NOT include literature citation counts, hypothesis counts, or any other Phase 0 / Phase 0.5 work-effort metric. Those numbers are administrative trivia and live in `experiment_log.md`, not in the published methodology.

- **Section ordering for paper.md**: Abstract → Introduction → **Detailed Baseline** → **Detailed Solution** → Methods (the iteration process) → Results → Discussion → Conclusion → References. The two new sections sit between the introduction and the methods because they establish what is being compared *before* the reader sees how the comparison was done.

- **Never reference the internal review process.** The paper is written as a unified scientific analysis, not as a narrative of how the research was produced. The following must not appear anywhere in `paper.md`:
  - the words "reviewer", "sub-agent", "agent", "Phase 2.75", "Phase 3.5", "blind review", "mandatory follow-up", "RV01..RVnn"
  - any meta-narrative of the form "the reviewer caught a bug", "during review we added...", "mandatory experiments were required"
  - filenames that expose the review machinery (`paper_review.md`, `paper_review_signoff.md`, `run_reviewer_experiments.py`, `reviewer_experiments_spec.md`) — these are on-disk artefacts, not publishable references

  Every finding that emerged from the review cycle — including bug-fix corrections and mandatory robustness experiments — must be reported as if it were part of the original analysis plan. A bug caught in review becomes "the corrected specification is..." without narrating the bug; an experiment demanded by the reviewer becomes part of §3 Robustness without attribution. The reader sees one coherent study, not the production process that produced it.

- **Never report work-effort metrics as findings.** Sentences of the form "we ran 34 experiments and kept 3", "100 hypotheses were tested", "five families were evaluated", "200 citations were reviewed", or any count of iterations, experiments, hypotheses, citations, or phases belong in `experiment_log.md`, not in `paper.md` and not in its Abstract, Introduction, Methods, or Results. The publishable fact is *what* was tested and *what the result was*, never *how many things were tried*. The only exception is sample size `n` in the primary analysis — that is a statistical input, not a work-effort metric.

### Plots and figures in paper.md (mandatory)

Every paper.md must include plots generated by a `generate_plots.py` script in the project directory. Plots are saved as PNG (300 DPI) to a `plots/` subdirectory and referenced in the markdown as `![caption](plots/filename.png)`. Commit the PNGs to git alongside the paper.

**Rule of thumb: add a plot when the finding would take more than 2 sentences to describe in text.** If you're writing a paragraph of numbers comparing 5 things, that's a chart, not prose.

**Mandatory plots (every project):**

1. **Predicted vs actual scatter** — shows model quality at a glance. Tight diagonal = good, scatter = bad. Include the 1:1 reference line.
2. **Feature importance (top 10-15)** — horizontal bar chart of permutation importance or SHAP values. This IS the mechanism finding — what the model actually relies on.
3. **The headline finding visualised** — whatever the "surprise" is (the refutation, the threshold, the decomposition, the Pareto front) as a single compelling figure. This is the figure a journalist would use.

**Conditional plots (add when the trigger applies):**

| Trigger | Plot type |
|---|---|
| Phase 2 had multiple keeps | Waterfall chart of cumulative improvement, experiment by experiment |
| Phase B produced a Pareto front | Pareto scatter with labelled knee points and the baseline marked |
| Data has a geographic dimension | Choropleth map or station-level heatmap |
| Data has a time dimension | Time series with the key event or anomaly highlighted |
| Two competing hypotheses tested | Side-by-side grouped bar chart or paired dot plot |
| Distribution shape matters to the story | Histogram with annotated thresholds (e.g. the 200 Bq/m³ radon line) |
| Before/after comparison | Paired scatter or back-to-back histogram showing the shift |
| Cross-city or cross-country comparison | Faceted small-multiples or a single ranked bar chart |

**Style rules for plots:**
- Use `matplotlib` with a clean style (`plt.style.use('seaborn-v0_8-whitegrid')` or similar)
- Label axes with units. Title optional (the caption in the markdown serves as the title).
- Use colourblind-safe palettes (e.g. `tab10`, `Set2`, or the Wong palette)
- `dpi=300, bbox_inches='tight'` for every `savefig`
- Keep each PNG under 500 KB (resize if needed)
- No more than 8-10 plots per paper — each one must earn its place

**File structure:**
```
applications/<project>/
├── generate_plots.py    # reads results.tsv + cached data, produces all PNGs
├── plots/
│   ├── pred_vs_actual.png
│   ├── feature_importance.png
│   ├── headline_finding.png
│   └── ...
├── paper.md             # references plots as ![](plots/filename.png)
└── ...
```

`generate_plots.py` must be runnable standalone (`python generate_plots.py`) and produce all plots from cached data without re-running the model. It reads `results.tsv`, any cached predictions, and the cleaned dataset.

### Public summary (auto-generated, do not maintain by hand)

The website summary pipeline at `~/website/pipeline/` runs daily, scans every `applications/<project>/paper.md`, and regenerates `~/website/site/content/hdr/results/<project>/index.md` whenever the paper changes (hash-diff detection). The pipeline takes care of:
- Hugo frontmatter
- Tech-leaning-layman tone
- Resolving hyperlinks for benchmarks, datasets, simulators, and code repos
- Footer links to source code and HDR methodology
- Auto-commit and push to the website repo

**Do not write `summary.md` in the project directory.** It is deprecated; the pipeline owns the public version.

**Rules the summarizer MUST follow (also enforced by the prompt at `~/website/pipeline/hdr_summary_pipeline.md`):**

1. **No references to agents, reviewers, or the review process.** The words "agent", "sub-agent", "reviewer", "blind review", "Phase 2.75", "Phase 3.5", "mandatory follow-up", and "HDR pipeline" must not appear in the public summary. If a finding emerged from a review cycle, it is presented as part of the research, not as a meta-narrative of how the research was produced.

2. **No experiment, iteration, or citation counts.** The summary must not state "we ran 34 experiments", "100 hypotheses tested", "200 citations reviewed", "after 5 iterations", or any equivalent work-effort metric. These numbers are administrative trivia and are not interesting to the reader. The only count that may appear is sample size `n` in the primary analysis.

3. **No phase narration.** The summary must not describe the project as a sequence of phases ("in Phase 0 we did X, in Phase 1 we did Y"). It presents the research as a unified question → method → finding arc: what we asked, what we did, what we found, why it matters.

4. **Result first, method second, process never.** The structure is: the question → the headline result → one or two sentences of method for credibility → implications. The reader should never need to know how the work was produced to understand what it found.

5. **Say "we found" or "the analysis showed", never "the reviewer noticed" or "the agent caught".** First-person research voice, not production-process voice.

These rules are hard constraints. A summary that violates them must be regenerated.

### Craft rules — what makes a summary actually grab and hold a reader

The hard constraints above stop a summary from being *bad*. The craft rules below are what move a summary from "follows the schema" to "a curious adult reads to the end and forwards the link". Apply them whenever the project's nature allows; not every section will fit every project.

1. **Title as a question or a contested claim, not a description.** A title that asks "Did X actually do Y?" pulls a reader in; a title that names the technique does not. If the headline finding is a null result or a debunking, put the contest right in the title.

2. **Open with public stakes, not method.** The first paragraph names the real-world actors who care: ministers, regulators, named agencies, public hearings, specific dated moments. The reader should know within three sentences what was at stake to whom. Method comes later.

3. **The "naive finding first, then falsified" structure for null results and debunkings.** When the headline finding is "no, the obvious-looking effect isn't real", structure the body as: (a) what the naive look suggested — show the striking number that *would have been* the headline had the analysis stopped early; (b) what the proper test showed — walk the reader through the control or peer comparison that killed it; (c) a one-paragraph sanity check, typically a placebo, that reinforces. This gives the reader the satisfaction of seeing the alternative considered and rejected, rather than just being told the answer.

4. **Plot captions are part of the narrative, not labels.** Each caption tells the reader what to *look at* and what it *means*: "Real X (black) versus synthetic X built from peer Y (red dashed). The two track each other closely all the way through the shock and beyond." Avoid captions that only restate axis labels. Three plots maximum, each load-bearing for the argument.

5. **Name the alternative explanation when the headline collapses.** A null finding without a "what was actually going on?" paragraph leaves the reader unsatisfied. Identify the real mechanism (often: a broader cohort-wide effect, a confounder, a measurement artefact) and attribute it specifically.

6. **Close with the transferable lesson.** The final short section is the methodological takeaway — abstracted from the project so a reader in an adjacent field gets value: "If you only compare X to its own past, ordinary cohort-wide events look like local Y." This is what gets the link forwarded.

7. **Use named real-world actors throughout.** Concrete institutions (the antitrust regulator, the named legislative committee, the specific minister) give the writing texture and credibility. Avoid passive "it has been alleged that" — name who alleged it and when.

8. **Conversational subheaders.** "What the first look suggested" beats "Initial Results"; "What was actually going on?" beats "Discussion"; "A second sanity check" beats "Robustness". Subheaders are signposts for a reader who is scanning.

9. **For policy- or implication-relevant findings: a numerical implications section.** When a project has actionable policy or practical implications, add a section with specific numbers — magnitudes, costs, legal limits, comparison to known reference points — and rank options by directness. End with a one-sentence "bottom line" or scannable ranked list. Vague "this could inform policy" is filler; "the maximum legal cut is 31 cents per litre, costing approximately €X per year" is what readers need.

10. **Specific-but-plain numbers throughout.** "About 17 cents per litre" is plain English. "z = +4.4σ above the pre-shock conditional residual" is not. Translate every statistical claim into a concrete unit a reader can picture, even if it loses some precision. Precision lives in `paper.md`; readability lives here.

A summary that follows the hard constraints AND most of the craft rules above is the publication target. The pipeline summarizer prompt at `~/website/pipeline/hdr_summary_pipeline.md` enforces both layers.

---

## Phase 3.5: Adversarial Paper Review

### ⚠️ MANDATORY ARTIFACTS FOR PHASE 3.5 — PUBLICATION BLOCKER

**Phase 3.5 is NOT complete and the project CANNOT proceed to Phase B or Publish unless ALL of these exist:**

- [ ] `paper_review.md` for the paper (separate from the Phase 2.75 results review) written by a DIFFERENT sub-agent invocation
- [ ] `paper_review_response.md` documenting the HDR agent's response to every finding
- [ ] Any reviewer-mandated paper experiments present in `results.tsv` with `status` ∈ {RUN_RV, CONTROL, TEMPORAL, DIAG}
- [ ] `paper_review_signoff.md` exists AND contains the literal string `NO FURTHER BLOCKING ISSUES` AND is written by a DIFFERENT sub-agent invocation from Phase 2.75

**Publishing the website summary before `paper_review_signoff.md` contains `NO FURTHER BLOCKING ISSUES` is a retraction-grade failure.** A project that was published without reviewer sign-off must have the website summary retracted and the reviewer cycle run retroactively.

**Mandatory. Do not skip. The paper must survive independent review before publication.**

After the Phase 3 paper draft is complete, a **separate reviewer agent** reads `paper.md` in isolation — simulating a blind peer reviewer. This agent has no access to the HDR agent's conversation, `results.tsv`, or code. It sees only what a journal reviewer would see: the paper itself.

### Reviewer inputs

- `paper.md` only (plus any figures in `plots/`)
- The reviewer does NOT see `results.tsv`, `review.md`, `knowledge_base.md`, or code

### Review protocol

The reviewer produces `paper_review.md` with findings in these categories:

**1. Claims vs evidence.** For every quantitative claim in the paper, does the Methods section describe an experiment that would produce that number? Are confidence intervals or noise floors reported? Flag any number that appears without methodological support.

**2. Scope vs framing.** Does the title accurately reflect the scope of the work? Does the abstract carry the same qualifiers as the Discussion? Flag any case where the headline framing omits conditions that limit the result. Example: a finding demonstrated on a single-lane ring road simulation should not be titled as if it applies to real highways.

**3. Reproducibility.** Could a reader replicate the work from the paper alone? Are all parameters specified? Is the dataset identified with version/URL? Are evaluation metrics defined precisely? Flag anything a replicator would have to guess.

**4. Missing experiments.** Based on the claims made, what obvious follow-up experiments would a reviewer demand? These are experiments the *paper itself implies should exist* but doesn't report. Examples: robustness to parameter variation, sensitivity to dataset size, generalisation to a second dataset or domain, ablation of key components.

**5. Overclaiming and language.** Check for hedging failures: "we prove" when "we find evidence for" is appropriate; "always" when "in all tested conditions" is accurate; causal language when only correlation was demonstrated.

**6. Literature positioning.** Does the paper fairly represent prior work? Are there obvious missing citations that a domain expert would notice? Does the paper claim novelty for something already published?

### Severity and response

Same severity scale as Phase 2.75 (CRITICAL / MAJOR / MINOR). Same response obligations (FIX / REBUT / ACKNOWLEDGE).

### Suggested experiments are mandatory

**This is the most important rule in the review process.** When the paper reviewer identifies missing experiments — robustness checks, sensitivity analyses, generalisation tests, ablations — the HDR agent MUST run them. These experiments are not optional follow-up work. They are required before publication.

The HDR agent:
1. Runs each suggested experiment through the standard evaluation harness
2. Adds results to `results.tsv`
3. Adds a new section or extends the Results section of `paper.md` with the findings
4. **Reports the results honestly, even if they weaken the headline.** If a robustness check fails, the paper must say so. Suppressing a negative result from a reviewer-suggested experiment is the single most damaging thing the methodology can do to its credibility.

If reviewer-suggested experiments significantly change the findings, the paper may need substantial revision — new abstract, revised conclusions, updated title. This is expected, not a failure. A paper that survives adversarial review is worth more than one that was never challenged.

### Revision cycle

1. HDR agent revises `paper.md` and writes `paper_review_response.md`
2. Reviewer gets a second pass on the revised paper
3. If all CRITICAL and MAJOR items are resolved, the reviewer signs off in `paper_review_signoff.md`
4. Maximum 3 rounds. Unresolved items after 3 rounds become mandatory entries in the Discussion/Limitations section.

### Deliverables

```
applications/<project>/
├── paper_review.md              # Reviewer's structured findings on the paper
├── paper_review_response.md     # HDR agent's responses + paper revisions
└── paper_review_signoff.md      # Final reviewer approval or noted open items
```

### Only after sign-off

The website summary pipeline should not publish a project until `paper_review_signoff.md` exists. A paper without reviewer sign-off is a draft, not a result.

---

## Phase B: Discovery

### ⚠️ MANDATORY ARTIFACTS FOR PHASE B

**Phase B is NOT complete and the project CANNOT proceed to Publish unless ALL of these exist:**

- [ ] `phase_b_discovery.py` in `applications/<project>/` — a standalone runnable script
- [ ] `discoveries/` directory with Phase B outputs (novel candidates, Pareto fronts, inverse-design outputs, anomaly detections, or domain-specific equivalents)
- [ ] `results.tsv` contains at least one row with `status=DISCOVERY` summarising the Phase B output
- [ ] If Phase B involves a live monitor or detector: the JSON state file exists in `discoveries/`

**Phase B is not "run more training experiments". It is "use the tool to explore the unknown". The output is a ranked list, a discovered candidate, a flagged anomaly, a Pareto front, or a specification for an extension — not just another row in the tournament.**

**For descriptive-only projects**: Phase B is a rank-list / ranking output (e.g. "top 10 hospitals at risk next month", "which operators are worst-recovered") written to `discoveries/<project>_rankings.csv`. Skipping Phase B because "the project is descriptive" is FORBIDDEN — every project produces a forward-looking artifact.

**For Option D (symbolic/analytical) projects**: Phase B produces one or more of: (1) minimal sufficient mathematical structure, (2) closed-form analytical bounds on constraint-satisfying parameter regimes, (3) classification of solution families by mathematical mechanism, (4) conjectures with proof sketches. See "Phase B for Option D: Analytical Discovery" in the Phase 2 Variant section. The output lives in `discoveries/` as markdown files with embedded LaTeX equations, plus any generated plots of parameter-regime boundaries.

---

## Phase Publish: Website Summary

### ⚠️ MANDATORY ARTIFACTS AND GATING FOR PHASE PUBLISH

**Publishing the website summary is NOT permitted unless ALL of these are true:**

- [ ] `paper_review_signoff.md` exists in the project directory AND contains the literal string `NO FURTHER BLOCKING ISSUES`
- [ ] `paper.md` exists and has been revised to incorporate all Phase 2.75 and Phase 3.5 mandated changes
- [ ] Phase B output exists per the Phase B mandatory artifacts above
- [ ] Hugo build passes locally with no errors
- [ ] Website `index.md` at `~/website/site/content/hdr/results/<slug>/` conforms to the auto-generated summary style rules
- [ ] Git commit to `~/website/site/` submodule and push to `colinjoc.github.io`

**Publishing before `paper_review_signoff.md` contains `NO FURTHER BLOCKING ISSUES` is a retraction-grade failure. If this happens, the website summary must be retracted immediately and the reviewer cycle completed retroactively before republication.**

**Forbidden shortcuts:**
- Writing the website index.md before `paper.md` exists — FORBIDDEN
- Writing the website index.md using the paper_draft.md (pre-reviewer) numbers — FORBIDDEN
- Publishing when paper_review_signoff.md exists but `NO FURTHER BLOCKING ISSUES` is missing — FORBIDDEN
- Using "I'll run the reviewer after publish" as a plan — FORBIDDEN (memory rule `feedback_no_phase_shortcuts.md`)

---

## Novelty Checklist

Before declaring done:
- [ ] Results exceed published SOTA (or match with simpler/faster/more robust method)
- [ ] At least one surprising finding
- [ ] Knowledge base contains insights valuable to other researchers
- [ ] Paper.md drafted with abstract, methods, results, discussion, references

---

## Repository Hygiene: No Data, No PDFs

**The git repo must contain ONLY code and markdown — never data files, never paper PDFs.**

### Why
- Data files bloat the repo (gigabytes of parquet/csv/h5)
- Paper PDFs may have copyright restrictions
- Other researchers should fetch data from the canonical source, not a copy
- Reproducibility requires linking to versioned upstream sources

### What gets committed
- `program.md`, `literature_review.md`, `papers.csv`, `research_queue.md`, `knowledge_base.md`, `results.tsv`, `observations.md`, `paper.md` — all markdown
- `model.py`, `evaluate.py`, `tests/` — all Python source
- `.gitignore` — exclude `data/`, `literature/`, `venv/`, `__pycache__/`, `discoveries/*.csv` if large

### What gets a URL link instead
- **Datasets** → URL in `data_sources.md`
- **Paper PDFs** → DOI/arXiv/journal URL in `papers.csv`
- **Trained model weights** → HuggingFace/Zenodo URL in `model_artifacts.md`
- **External code** → GitHub URL with commit hash in `dependencies.md`

### Required: `data_sources.md`

Single markdown file at the project root listing every external data source with:
- **Name** — what it is
- **URL** — where to download it
- **Size** — approximate
- **Checksum** — SHA256 of the canonical version (for reproducibility)
- **License** — what you can do with it
- **Local path** — where the code expects to find it after download
- **Download command** — wget/curl/gh-clone command to fetch it

### .gitignore template
```
# Data — fetched from URLs in data_sources.md
data/
discoveries/*.csv

# Literature — fetched from URLs in papers.csv
literature/papers/
literature/books/

# Python
venv/
__pycache__/
*.pyc

# Models — too large for git
*.pkl
*.ubj
*.h5
*.safetensors
```

---

## File Structure

```
program.md              # Methodology (this file)
literature_review.md    # Phase 0 narrative review
papers.csv              # 100+ citations with URLs (no PDFs)
data_sources.md         # External data URLs (no data files)
feature_candidates.md   # Domain → computable features
research_queue.md       # Prioritised hypotheses
knowledge_base.md       # Cumulative findings
results.tsv             # Every experiment result
observations.md         # Data gaps, signal ideas
paper.md                # Phase 3 academic paper writeup
model.py / strategy.py  # ONLY file modified during HDR
evaluate.py             # Evaluation harness (fixed)
tests/                  # TDD — test every component before integration
discoveries/            # Novel candidates found (Phase B output)
```

---

## Constraints

- ONE change per experiment
- ALWAYS test on small data before full runs
- ALWAYS commit before evaluation
- ALWAYS record in results.tsv
- ALWAYS use GPU if available
- Ground every hypothesis in domain science
- NEVER stop — keep iterating until the human stops you
