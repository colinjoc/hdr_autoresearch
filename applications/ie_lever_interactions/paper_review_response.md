# Paper Review Response

Response to all findings in `paper_review.md`.

## F1 (CRITICAL): 50% workforce expansion treated as feasible without evidence

**FIX.** Ran RV01 (workforce ramp-rate sensitivity). At SOLAS rates (+5k/yr), it takes 16 years. At optimistic (+10k/yr), 8 years. Paper now includes SS5.5 with full trajectory table and explicitly states the timescale challenge. Title's "optimal" replaced with "maximum." Abstract revised to flag the 16-year timeline.

## F2 (MAJOR): Diminishing returns to workforce expansion not modeled

**FIX.** Ran RV02. Diminishing-returns model shows effective capacity of 49,289 at +80k workers vs. linear 52,500 -- below the HFA target. Added to SS4.8 and SS6.4. Paper now notes that the HFA target may require more than 80,000 additional workers under diminishing productivity.

## F3 (MAJOR): r=0.91 used linearly beyond observed range

**FIX.** Ran RV03 (tanh elasticity, k in {0.5, 1.0, 2.0}). Results devastating to headline numbers: maximum package drops from 167,810 to 91,702 (k=0.5) or 50,925 (k=2.0). Paper now presents linear numbers explicitly as upper bounds, with tanh results in SS5.4 and SS5.6. Abstract revised.

## F4 (MAJOR): GE price compression mentioned but not modeled

**FIX.** Ran RV04. First-order correction overshoots (eliminates all cost reduction for large packages), which is itself informative: it demonstrates partial-equilibrium assumption breaks down. Paper now includes SS5.9 explaining why soft-ceiling estimates above ~60,000 should not be used for policy planning without a dynamic GE model. Honest framing, not a missing experiment.

## F5 (MAJOR): Modular x Land CPO redundancy may be ceiling artifact

**FIX.** Ran RV05. Confirmed: gross interaction is exactly zero. The -14,526 redundancy is entirely a ceiling artifact. Paper SS5.2 and SS6.3 now state this explicitly with the decomposition result.

## F6 (MAJOR): Parameter CIs not propagated through factorial

**FIX.** Ran RV06 (1,000 MC draws on 5 interaction pairs). All CIs exclude zero; signs robust. Results in SS5.8. Paper acknowledges that CIs capture parameter precision only, not model-specification uncertainty.

## F7 (MINOR): Title implies empirical discovery

**FIX.** Title changed to "Deterministic Parameter-Propagation Analysis." Abstract clarifies method.

## F8 (MINOR): Pareto fiscal costs unsourced

**ACKNOWLEDGE.** Added caveat to SS4.5 and SS5.7 noting that fiscal estimates are approximate and the Pareto ranking may shift.

## F9 (MINOR): Soft-ceiling congestion parameter unsourced

**ACKNOWLEDGE.** Added explicit caveat to SS4.2.

## F10 (MAJOR): "Optimal" language without optimization

**FIX.** Changed all instances of "optimal policy package" to "maximum policy package" throughout paper.
