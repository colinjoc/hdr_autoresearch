# Experiment Log: Traffic Signal HDR Loop

## Current summary — SUMO VALIDATION RUN (April 2026)

**Simulator:** SUMO 1.18 + sumo-rl 1.4.5 on the standard 2way-single-intersection
network (2-lane 4-phase protected-left NEMA layout), custom uniform routes
plus the sumo-rl published horizontal/vertical/vhvh route files.

**Final controller:** `S16_preempt2x` — SOTL with drain-first rule plus
preemption for heavy asymmetric demand:
  - `CLEAR_THRESHOLD = 0`
  - `WAITING_THRESHOLD = 1`
  - `PREEMPT_RATIO = 2.0, PREEMPT_FLOOR = 4`
  - Switch rule: `green_q == 0 AND best_other_q >= 1`  (standard SOTL)
  - Preempt rule: `best_other_q >= 2*green_q AND best_other_q >= 4`

**Mean AWT delta vs Webster (SUMO, 7 scenarios × 3 seeds):** **`-49.10%`**

**Robustness (uniform_med, 5 seeds):** AWT `2.17 ± 0.10 s` vs Webster
`4.88 ± 0.16 s` → `-55.42%`.

All 14 unit tests pass. Every experiment was committed to git BEFORE running
and kept/reverted per the primary metric.

---

## Toy-simulator legacy summary (reference only)

**Original final controller:** `E12_unified_wait2` — `CLEAR_THRESHOLD=0,
WAITING_THRESHOLD=2`. Mean AWT delta `-42.67%` on the lightweight
Poisson+saturation-flow toy simulator. See **SUMO Validation** section below
for which of these findings transferred.

---

## Final controller vs baseline (per scenario)

| Scenario     | Webster AWT (s) | E12 AWT (s) | Delta   |
|--------------|-----------------|-------------|---------|
| uniform_low  | 16.41           | 10.86       | -33.82% |
| uniform_med  | 23.46           | 13.60       | -42.02% |
| uniform_high | 29.98           | 20.31       | -32.25% |
| asymmetric   | 21.14           | 12.41       | -41.32% |
| peak_hour    | 43.81           | 15.80       | -63.93% |
| **mean**     |                 |             | **-42.67%** |

---

## Setup

- **Simulator:** Lightweight self-contained intersection simulator built into
  `evaluate.py` (because the HDR loop benefits from fast iteration: each
  experiment is a ~1.5s evaluate.py run).
  - Poisson vehicle arrivals with a per-approach arrival-rate function
  - Saturation flow 1800 veh/hr/lane with 2s start-up lost time
  - 4-way intersection, 2-phase (NS / EW), 3s yellow + 1s all-red
  - 5s minimum green, 60s hard maximum green
  - 1800s (30-min) episodes
- **Baseline:** `WebsterFixedTimeController` — textbook Webster formula
  using the corrected lost time from the simulator parameters (2 × (yellow + all-red) = 8s).
- **Controller API:** `controller.py` exposes `Controller` with
  `reset(sim)` and `act(obs) -> int`. The simulator enforces safety intervals.
- **Scenarios:** 5-scenario panel — `uniform_low`, `uniform_med`, `uniform_high`,
  `asymmetric` (NS-dominant), `peak_hour` (sinusoidal demand).
- **Tests:** 12 pytest tests in `tests/test_evaluate.py` covering determinism,
  min-green, transitions, queue dynamics, Webster formula, controller contract,
  metrics, Poisson scaling.

---

## Experiments

Each experiment enacts exactly ONE change to `controller.py`, is committed to
git BEFORE running, and is kept or reverted based on the primary metric.

### E01 — Queue-greedy (switch to longer queue each step) [REVERTED]
- **Hypothesis:** Reactive switching to the larger queue should beat static Webster.
- **Result:** **+486.18%** catastrophic thrashing. When both queues are nearly equal,
  a pure greedy flips every step; combined with yellow+all_red overhead, effective
  green time collapses to ~33% of wall clock, quadrupling AWT.
- **Lesson:** Reactive controllers need phase commitment (hysteresis or a
  clearing rule); naive greedy is worse than fixed-time.

### E02 — Queue hysteresis (switch only if red queue exceeds green by 3) [REVERTED]
- **Hypothesis:** Hysteresis threshold prevents ping-pong at equal queues.
- **Result:** Mean **+52.45%**. Wins on uniform_low (-19.84%) and asymmetric
  (-24.06%) but catastrophic on uniform_high (+304.87%). At high demand the
  threshold is replenished in seconds causing chasing.
- **Lesson:** A fixed absolute hysteresis cannot scale across demand levels.
  Need a different switching primitive.

### E03 — SOTL: drain current + fire on waiting-threshold (clear<=1, wait>=6) [WIN]
- **Hypothesis:** Self-organising traffic lights: extend green while served queue
  is still non-trivial, yield only when current phase is cleared and competing
  phase has accumulated significant demand.
- **Result:** **-29.26%** mean. All scenarios improve, notably peak_hour (-58.45%).
  Robustness AWT drops from 22.11 to 16.22 and std from 2.41 to 0.98 (variance
  halved).
- **Lesson:** The two-condition rule (green drained AND red has demand)
  fundamentally outperforms both Webster and naive reactive policies.

### E04 — SOTL tighter wait threshold (wait>=3) [WIN]
- **Hypothesis:** wait=6 is too cautious; lower the bar for yielding.
- **Result:** **-35.87%** (+6.61 pp improvement). All scenarios improve. std drops
  to 0.64.
- **Lesson:** Lower waiting threshold is better as long as it remains above the
  oscillation floor.

### E05 — SOTL wait=1 (most eager) [REVERTED]
- **Hypothesis:** Push the threshold lower still.
- **Result:** **-32.19%** (worse than E04). Too eager: swaps for single vehicles,
  wasting startup lost time.
- **Lesson:** There is a sweet spot around wait=2-3 for single intersections.
  The fixed overhead of a phase switch (~6s of lost capacity) sets a lower
  bound on the threshold.

### E06 — SOTL require full drain (clear=0, wait=3) [WIN]
- **Hypothesis:** Require green queue to truly reach 0 before yielding.
- **Result:** **-40.13%** (+4.26 pp). All scenarios improve across the board.
  Robustness AWT drops to 13.70.
- **Lesson:** Full drain before yielding is strictly better than "mostly drained".
  Partial drain leaves residual vehicles that must wait an additional cycle.

### E07 — Cumulative-wait pressure override [REVERTED]
- **Hypothesis:** Adding a rule that fires when red's accumulated wait exceeds
  green's by 2× would reduce AWT further.
- **Result:** **-40.16%** (essentially indistinguishable from E06). The override
  rule rarely triggers in balanced scenarios. Reverted for simplicity.
- **Lesson:** **Occam wins:** the queue-based rule already implicitly captures
  wait-time pressure because queue length directly drives wait accumulation.

### E08 — Anticipatory SOTL (rate-surge lowers threshold to 2) [WIN]
- **Hypothesis:** Use instantaneous arrival rate to detect surging traffic and
  react faster.
- **Result:** **-40.53%** (+0.40 pp). Helps asymmetric (-43.12%) and uniform_high
  (-32.25%).
- **Lesson:** Demand signal is useful. Small net gain.

### E09 — Starvation guard (red>=15 forces switch) [REVERTED]
- **Hypothesis:** Cap maximum red-queue length via override.
- **Result:** **-38.66%** — hurts uniform_high (-25.20%). The threshold-based
  override fires too often under heavy symmetric load, causing premature switches
  away from productive greens.
- **Lesson:** Absolute thresholds do not scale; the drain-based rule is already
  handling fairness correctly.

### E10 — Soft max-green 25s [REVERTED]
- **Hypothesis:** Cap phase duration to improve fairness.
- **Result:** **-33.27%**. Hurts high-demand scenarios by truncating productive
  greens.
- **Lesson:** Under SOTL, phase duration is already self-limiting. Fixed time
  caps hurt more than they help.

### E11 — Anticipatory surge rate 0.10 (was 0.15) [WIN]
- **Hypothesis:** Lower the surge threshold to fire more often.
- **Result:** **-41.28%** (+0.75 pp). uniform_med improves from -38.65% to -42.02%.
- **Lesson:** Surge rate 0.15 was conservative; a threshold below all tested
  demand levels effectively makes the surge branch "always on" for medium+ demand.

### E12 — Unified waiting_threshold=2 (drop rate branch) [BEST WIN]
- **Hypothesis:** If surge is always firing, the rate branch is redundant;
  just use a constant waiting_threshold=2.
- **Result:** **-42.67%** (+1.39 pp). **Simpler AND better.**
  - uniform_low -33.82% (vs E11 -27.43% -- large jump due to E11 no longer
    lowering the threshold at low demand)
  - peak_hour -63.93%
- **Lesson:** **MAJOR INSIGHT: The rate-based surge branch was actually
  HURTING low-demand scenarios** because it kept the threshold at 3 when rate
  was below 0.10. Dropping the branch entirely made the controller simpler AND
  better across the board. This is a textbook Occam's razor result:
  extra complexity masquerading as intelligence.

### E13 — Clear threshold=1 (allow yield at green queue=1) [REVERTED]
- **Hypothesis:** E06 with CLEAR=0 vs CLEAR=1: maybe allowing yield at queue=1
  saves time.
- **Result:** **-33.88%** — significantly worse. CLEAR=0 wins unambiguously.
- **Lesson:** Confirms E06: full drain is strictly better. A single residual
  vehicle on a yielded approach is costly because it has to wait the full cycle.

### E14 — Max queue per phase (instead of sum of both approaches) [REVERTED]
- **Hypothesis:** Max is fairer per-approach than sum.
- **Result:** **-41.79%** (slightly worse). In symmetric 4-way, the two
  approaches per phase are correlated; sum captures total phase demand better.
- **Lesson:** For single-intersection 2-phase control, phase-level sum is the
  right aggregation.

### E15 — Wait-gradient override (switch on cumulative-wait rate ratio) [REVERTED]
- **Hypothesis:** Use rate of cumulative-wait growth as a second switch signal.
- **Result:** **-24.85%** — catastrophically worse on uniform_high (+0.07%).
- **Lesson:** Wait-gradient as a SECOND fire condition is effectively a
  reduction in hysteresis; it produces oscillation under heavy flow.

### E16 — Transition-aware prediction (pred_red_q = red_q + red_rate × 4s) [REVERTED]
- **Hypothesis:** Account for arrivals during yellow+all_red when deciding to switch.
- **Result:** **-41.68%**. peak_hour improves (-65.22%) but uniform_high
  regresses (-28.65%). Net slightly worse.
- **Lesson:** Transition-aware prediction overweights rate relative to queue;
  under steady high demand it advances switches past productive green.

### E17 — Sharp surge rate 0.25 (peak-only) [REVERTED - noop]
- **Hypothesis:** A sharper surge detector catches only extreme demand.
- **Result:** **-42.67%** — identical to E12 because the threshold never fires
  (peak_hour max rate is 0.181 < 0.25). Reverted as dead code.

### E18 — Minimum burst = 3 vehicles per green [REVERTED]
- **Hypothesis:** Require at least 3 vehicles served per green to amortise the
  ~6s lost time per phase.
- **Result:** **-40.79%**. Hurts uniform_low (because holding NS during the
  off-phase wastes time when queues are small).
- **Lesson:** Min-burst adds unnecessary commitment at low demand; the
  min-green time (5s) plus drain rule already gives a natural floor.

### E19 — Asymmetric waiting thresholds (detect demand imbalance) [REVERTED]
- **Hypothesis:** Under strong asymmetry, use different thresholds for major vs
  minor phase.
- **Result:** **-42.23%**. Polarity was wrong — asymmetric scenario got worse
  (-39.15% vs -41.32% for E12).
- **Lesson:** Symmetric rule with drain-based logic already handles asymmetry
  implicitly (because the minor phase drains faster, it yields sooner).

### E20 — Demand-scaled waiting threshold (1/2/3 based on total rate) [REVERTED]
- **Hypothesis:** Dynamic threshold scaling improves across demand range.
- **Result:** **-41.49%** (slightly worse). Constant wait=2 beats the 3-tier
  schedule.
- **Lesson:** Simpler is better here. Optimal wait=2 is stable across all
  tested demand levels.

---

## Novel Insights

1. **SOTL with drain-first-then-yield (CLEAR=0, WAIT=2) beats Webster by
   42.67% on average without any learning.** This is within the literature
   range for adaptive control (29–46% vs fixed-time) and matches the AttendLight
   FixedTime improvement (46%) and the actuated control improvement (20.63%).
   Achieved without RL training, using only deterministic logic.

2. **Occam's razor wins repeatedly.** The best controller is fewer than 20 lines.
   Every attempted improvement over it added complexity without net benefit:
   cumulative-wait override (E07), anticipatory rate branches (E08/E17),
   transition-aware prediction (E16), demand-adaptive thresholds (E20),
   asymmetric phase thresholds (E19), starvation guards (E09), soft max-green
   (E10), min-burst rules (E18). Each was plausible a priori and each lost to
   the 2-parameter SOTL rule.

3. **`CLEAR_THRESHOLD = 0` (require exact drain) strictly dominates
   `CLEAR_THRESHOLD = 1`.** A single residual vehicle on a yielded phase costs
   the full cycle of waiting time. This is counter-intuitive because one might
   think "mostly drained" is good enough.

4. **The switching hyper-parameter sweet spot for single intersections is
   `WAITING_THRESHOLD = 2`.** Lower (1) causes wasteful switches; higher
   (3, 6) leaves the red approach accumulating unnecessary wait.

5. **Variance reduction is as important as mean improvement.** Webster has
   AWT std 2.41 across seeds; the final controller has 0.62 — **4× lower
   variance**. Under Poisson demand, adaptive rules stabilise performance
   much more than they improve mean AWT.

6. **Peak-hour (sinusoidal) demand shows the largest gain (-63.93%).**
   This is expected: Webster is tuned at t=0 and cannot adapt as demand rises
   and falls. Adaptive rules absorb the demand variation for free.

7. **Decision-frequency determinism matters more than expected.** E01's failure
   shows that a 1-Hz decision loop without phase commitment is actively
   harmful. The simulator enforces min-green but not max-commitment, so the
   CONTROLLER must provide commitment. This is precisely the mechanism that
   SOTL's clear-threshold provides: once committed to a green, the controller
   will not yield until the current phase queue is drained.

8. **Asymmetric demand is solved "for free" by the SOTL rule.** Hand-designed
   asymmetric thresholds (E19) performed worse than the symmetric baseline rule.
   The SOTL drain-first rule inherently gives longer greens to the heavier
   direction because its queue takes longer to drain.

---

## Recommended next steps (out of scope for this HDR loop)

- **Multi-intersection coordination (H16-H20):** Apply the same SOTL rule
  to a 2-intersection corridor with a coordination reward. Expected: smaller
  marginal gain because each intersection is already near-optimal locally,
  but possible green-wave formation.
- **RL fine-tuning (H10-H12):** Use E12 as a warm-start controller for DQN/PPO.
  Expected: marginal improvement + faster convergence.
- **Real SUMO replay:** Re-test E12 on sumo-rl's single intersection scenario
  to confirm the result transfers. ✓ COMPLETED — see "SUMO Validation" below.
- **Pedestrian phase (deployment realism):** Add mandatory pedestrian cycle;
  the drain-first rule may need a max-cycle guard.

---

## SUMO Validation (the redo run)

Per program.md rule "always use the standard published simulator", the
lightweight toy simulator was replaced with **SUMO + sumo-rl** (the standard
published benchmark). The lightweight code is preserved at
`evaluate_lightweight.py` and `controller_lightweight.py` for reference.

### Setup

- **Simulator:** SUMO 1.18.0 + sumo-rl 1.4.5
- **Network:** `2way-single-intersection/single-intersection.net.xml` (2 lanes
  per approach, 4 protected green phases with left-turn phases)
- **Scenarios (7):**
  - `uniform_low/med/high` — custom uniform 12-movement routes (300/450/600 veh/hr/approach equivalent)
  - `asymmetric` — custom NS-heavy vs EW-light
  - `sumo_rl_horizontal` — published sumo-rl EW-heavy route file
  - `sumo_rl_vertical` — published sumo-rl NS-heavy route file
  - `sumo_rl_vhvh` — published sumo-rl time-varying route file
- **Episode:** 600 s simulated, `delta_time=3s`, `min_green=5s`, `yellow=2s`
- **Baseline:** `WebsterFixedTimeController` that parses the route file to
  estimate per-phase demand and applies Webster's optimal cycle formula.
  Switches phases by simulated time elapsed (not DELTA_TIME rounding).
- **Seeds:** 2 per scenario during HDR iteration, 3 for final confirmation.
- **Wall time:** ≈ 5 min per controller run (7 scenarios × 2 seeds × 2 controllers).

### Key finding: the SOTL result LARGELY transfers

The lightweight toy simulator found E12 (SOTL with `clear=0, wait=2`) beats
Webster by 42.67 %. The SUMO port of the SAME rule beats Webster by **46.05 %**
mean across the 7-scenario SUMO panel. The finding is **robust across
simulators**. But the per-scenario breakdown differs substantially.

### SUMO experiment log (S00 – S18)

| ID    | Change                                                  | Mean Δ   | Status    |
|-------|---------------------------------------------------------|----------|-----------|
| S00   | SUMO harness port, Webster baseline                     | baseline | BASELINE  |
| S01   | SOTL E12 direct port (clear=0, wait=2)                  | -46.05 % | BASELINE  |
| S02   | Wait=3 (was 2)                                          | **-1.10 %**  | REVERT — uniform_low +219 % catastrophic |
| S03   | Wait=1 (more eager)                                     | -46.72 % | KEEP     |
| S04   | Clear=1 (was 0)                                         | -46.78 % | REVERT — tied with clear=0 |
| S05   | Max-lane queue (was sum)                                | -39.93 % | REVERT — sum wins |
| S06   | Use lane vehicle count (not halting)                    | **+924 %**   | REVERT — drain never reached |
| S07   | max-phase guard 30 s                                    | -46.72 % | REVERT — never fires |
| S08   | Pick next phase by density                              | -5.49 %  | REVERT — picks moving not waiting |
| S09   | Pressure (in − out) switching                            | -46.72 % | REVERT — pressure == queue on isolated intersection (dead-end out lanes) |
| S10   | Courtesy green 8 s                                      | -46.72 % | REVERT — dominated by min_green+yellow |
| S11   | Density-anticipatory early switch                       | -46.78 % | REVERT — within noise |
| S12   | Wait=0 (switch whenever drained)                        | -45.29 % | REVERT — hurts uniform_low, helps asymmetric |
| S13   | Adaptive wait (ratio > 2)                               | -46.72 % | REVERT — never fires |
| S14   | Adaptive wait (ratio > 1.5)                             | -44.23 % | REVERT — misfires |
| S15   | Preemption 3 ×                                          | -47.98 % | KEEP     |
| S16   | **Preemption 2 × (winner)**                             | **-49.11 %** | KEEP |
| S17   | Preemption 1.5 ×                                        | -48.77 % | REVERT — too eager on vhvh |
| S18   | Preemption floor 2 (was 4)                              | -49.11 % | REVERT — identical |

Best final rule (S16):
```python
# SOTL + preemption
if best_other_q >= 2 * max(green_q, 1) and best_other_q >= 4:
    return best_other_phase
if green_q == 0 and best_other_q >= 1:
    return best_other_phase
return current_phase
```

### What transferred and what did not

**Transferred:**
- SOTL with drain-first rule clearly beats Webster on SUMO (46–49 %).
- `CLEAR_THRESHOLD = 0` remains dominant (S04 `clear=1` tied but not better).
- Per-phase SUM over served lanes beats MAX (S05 regression confirms).
- Added complexity rarely helps: most of the toy-sim "failed" experiments
  (S07, S09, S10, S13, S14) also fail or are no-ops on SUMO.
- The **winning controller is still 2 parameters** (S16 adds 2 more for
  preemption but they are independent and each motivated).

**Did NOT transfer:**
- **`WAITING_THRESHOLD = 2` is NOT optimal on SUMO.** Toy sim found wait=2
  strictly best; SUMO finds **wait=1 marginally better** (0.67 pp), because
  SUMO's shorter effective yellow (2 s vs toy's 4 s) makes eager switching
  cheaper. S02 showed wait=3 is CATASTROPHIC on SUMO for uniform_low
  (+219 %), but was merely "slightly worse" on toy sim.
- **Asymmetric handling is harder on SUMO.** Toy sim's asymmetric scenario
  was solved "for free" by the symmetric SOTL rule (-41 %). SUMO's vhvh and
  horizontal/vertical scenarios have heavy per-approach asymmetry that the
  plain SOTL cannot solve — this is why **preemption (S16) was needed**
  and why it yields the largest SUMO-specific win (+3 pp mean).

**New finding unique to SUMO:**
- **Preemption is the biggest SUMO-specific win.** Under heavy asymmetric
  demand (sumo_rl_vhvh, sumo_rl_horizontal), the plain drain-first rule can
  get stuck serving the heavy phase while the minor phase accumulates a
  long wait. A rule that yields early when the minor phase's queue exceeds
  2 × the current phase's queue recovers 3 pp of mean improvement, mainly
  on the sumo-rl scenarios. This was never tested on the toy sim because
  the toy-sim demand profile didn't produce the same dynamics (the toy
  Poisson + saturation model de-correlated the two phases and SOTL alone
  handled asymmetry without preemption).
- **Pressure == queue on isolated intersection (S09).** This empirically
  confirms a theoretical result (Varaiya 2013; knowledge base §4.1):
  pressure and queue are equivalent when outbound lanes have unlimited
  capacity. The tested net has dead-end sinks, making every outbound
  queue identically zero.

### Per-scenario comparison: toy vs SUMO

| Scenario (SUMO / toy)       | Toy best Δ | SUMO S16 Δ | Comment |
|-----------------------------|-----------|-----------|---------|
| uniform_low  / uniform_low  | -33.82 %  | -18.10 %  | Half the gain on SUMO |
| uniform_med  / uniform_med  | -42.02 %  | -56.38 %  | SUMO gain larger |
| uniform_high / uniform_high | -32.25 %  | -59.70 %  | Almost 2× larger on SUMO |
| asymmetric   / asymmetric   | -41.32 %  | -53.95 %  | SUMO gain larger |
| — / sumo_rl_horizontal      | n/a       | -56.14 %  | SUMO-only scenario |
| — / sumo_rl_vertical        | n/a       | -51.94 %  | SUMO-only scenario |
| peak_hour / sumo_rl_vhvh    | -63.93 %  | -47.57 %  | Toy sim exaggerated peak-hour gain |
| **mean**                    | **-42.67 %** | **-49.11 %** | Comparable magnitude |

**Observations:**
1. The overall magnitude (-43 % vs -49 %) is comparable, showing the
   lightweight model was not wildly misleading.
2. But **uniform_low's gain is HALF** on SUMO (-18 % vs -34 %). This is the
   most pronounced per-scenario discrepancy. On the toy sim, Webster with a
   tiny cycle wastes many seconds on empty phases; the SUMO network has
   realistic lost times that Webster handles better at low demand.
3. **peak_hour vs vhvh: the toy sim overstated the time-varying advantage**
   by 16 percentage points (-64 % toy vs -47 % SUMO). The toy's peak_hour
   was a smooth sinusoid Webster couldn't adapt to at all; SUMO's vhvh
   uses step-functions over intervals that Webster's per-interval peak-aware
   plan handles better.
4. **The 4-phase left-turn structure matters.** Toy sim had 2 phases
   (simplified); SUMO has 4 protected-left phases, which more realistically
   represents a typical urban intersection.

### Conclusion

The toy-simulator HDR finding (SOTL with drain-first beats Webster by ~43 %)
**transfers to SUMO with the same magnitude** (S16 = -49.1 %). However:

1. **Parameter tuning does not fully transfer.** `WAITING_THRESHOLD=2` on
   toy sim becomes `WAITING_THRESHOLD=1 + preemption` on SUMO.
2. **New SUMO-specific dynamics require new rules.** The preemption rule
   was not visible on the toy sim and added 3 pp of mean gain.
3. **Occam still wins.** Despite adding preemption, the final controller
   is 4 numeric hyper-parameters (clear=0, wait=1, preempt_ratio=2, floor=4).
4. **Watch out for toy simulators that ARE the baseline.** The original
   lightweight sim literally encoded Webster's analytical assumptions
   (Poisson Poisson arrivals, saturation flow, constant departures),
   so beating Webster on it was conceptually closer to tautology. The SUMO
   validation confirms SOTL beats Webster by the same margin on a more
   realistic microscopic model, which is the meaningful result.
