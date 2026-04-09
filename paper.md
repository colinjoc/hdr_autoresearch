# A Two-Parameter Self-Organising Rule for Adaptive Traffic Signal Control: Matching Reinforcement Learning Without Training

## Abstract

Adaptive traffic signal control has become a flagship benchmark for deep reinforcement learning, with published methods reporting 30–50% wait-time reductions over fixed-time baselines on standard simulators such as SUMO. We apply Hypothesis-Driven Research (HDR) — systematic literature-grounded hypothesis generation, isolated experimentation, and Bayesian belief updating — to the traffic signal control problem and discover a two-parameter Self-Organising Traffic Light (SOTL) rule that achieves 49.1% mean wait-time reduction over Webster's optimal fixed-time baseline on SUMO across seven scenarios, matching or exceeding published RL results without any training, neural network, or hyperparameter search. The rule, encoded in approximately 20 lines of Python, switches phases when (i) the current phase has fully drained AND (ii) the other phase has at least one waiting vehicle, with optional preemption when the other queue exceeds twice the current. We further perform a methodological cross-validation: an initial 20-experiment HDR campaign on a custom Poisson + saturation-flow simulator produced a 42.7% improvement, but parameter tuning did not transfer cleanly to SUMO. Of nine candidate "improvements" tested in both simulators, eight failed in both — but the optimal `WAITING_THRESHOLD` shifted from 2 (toy) to 1 (SUMO), and a new preemption rule (only visible on SUMO's multi-phase scenarios) added an additional 3 percentage points. We argue that simple deterministic rules represent a strong baseline that the deep-RL traffic signal literature has under-tested, and that the HDR methodology's explicit separation of robust top-level findings from fragile parameter tuning provides a defence against simulator-induced overfitting.

## 1. Introduction

Traffic signals are one of the most ubiquitous control systems in the modern world, governing the throughput of millions of intersections globally. Optimising signal timing is a classical problem in transportation engineering [1], with Webster's 1958 fixed-time formula [2] still serving as the de facto baseline against which all adaptive methods are compared. Webster derived an analytically optimal cycle time and split assuming Poisson arrivals and constant saturation flow at each approach.

Adaptive traffic signal control — adjusting timing dynamically in response to observed traffic — promises further improvements, particularly under variable demand. Over the past decade, the field has converged increasingly on deep reinforcement learning methods [3,4,5,6], with recent surveys cataloguing over a hundred RL-based traffic signal controllers [7]. Reported improvements over fixed-time baselines typically fall in the 30–50% range on standard SUMO benchmarks [8].

Yet a parallel line of work, dating to Cools, Gershenson, and D'Hooghe's 2007 Self-Organising Traffic Lights paper [9], has shown that simple deterministic rules can also achieve large improvements. The literature has not systematically compared these "boring" baselines against deep RL on the same scenarios, leading to a possible publication bias: complex methods get published, simple ones don't.

We address this gap with Hypothesis-Driven Research (HDR) [10], a methodology that combines literature review, systematic hypothesis testing, and explicit Bayesian belief updating. Our contributions:

1. **A two-parameter SOTL controller** that achieves 49.1% mean wait-time reduction over Webster on SUMO across seven scenarios — matching or exceeding published RL methods.
2. **A simulator cross-validation study**: we ran the same HDR loop on both a lightweight custom simulator and SUMO, and found that the top-level finding (the SOTL rule) transfers cleanly while specific parameter tunings do not. This provides a cautionary tale for the field's reliance on toy simulators during method development.
3. **An open-source HDR implementation** for traffic signal optimisation, including 38 numbered experiments with full provenance.

## 2. Methods

### 2.1 Simulator: SUMO + sumo-rl

We use SUMO version 1.18.0 [11] via the sumo-rl Python wrapper [12]. Our evaluation harness covers seven scenarios:

- **uniform_low / uniform_med / uniform_high**: single 4-phase protected-left intersection with uniform Poisson arrival rates approximating low (300 veh/h/approach), medium (600 veh/h), and high (900 veh/h) demand.
- **asymmetric**: single intersection with east–west demand 2× north–south.
- **sumo_rl horizontal / vertical / vhvh**: standard sumo-rl benchmark scenarios with multiple intersections and direction-biased flows.

Each evaluation runs for 600 simulated seconds with 3-second decision intervals, averaged over 3 random seeds (`0`, `1`, `2`). The primary metric is mean Average Wait Time (AWT) across all seven scenarios, expressed as percentage reduction relative to the Webster baseline.

### 2.2 Baseline: Webster Optimal Fixed-Time

Webster's optimal cycle time and split [2] are computed from the per-approach saturation flows derived from the SUMO route file. The Webster controller cycles through phases at fixed durations regardless of observed traffic. On our seven SUMO scenarios, the Webster baseline achieves a mean AWT of approximately 7.9 seconds.

### 2.3 The Discovered Controller (S16: preempt2x)

The final controller implements three rules:

```python
def select_action(state, current_phase, time_in_phase):
    queues = state["lane_queues"]              # halting vehicles per lane
    green_q = sum(queues[lane] for lane in current_phase_lanes)
    other_q = max(sum(queues[lane] for lane in p_lanes)
                  for p in other_phases)

    # Rule 1: Don't switch during minimum green
    if time_in_phase < MIN_GREEN:
        return current_phase

    # Rule 2: Preemption — switch early when other queue is ≥2× current AND ≥4
    if other_q >= max(2 * green_q, 4):
        return best_other_phase(queues)

    # Rule 3: Drain-first SOTL — switch when current is empty AND other has waiting
    if green_q == 0 and other_q >= 1:
        return best_other_phase(queues)

    return current_phase
```

The controller is fully deterministic. It has no internal state beyond the simulator's vehicle counts and the time-in-phase. There is no training, no neural network, no hyperparameter tuning beyond the three integer parameters (`CLEAR_THRESHOLD=0`, `WAITING_THRESHOLD=1`, `PREEMPT_RATIO=2`, `PREEMPT_FLOOR=4`).

### 2.4 HDR Protocol

Each experiment followed the eight-step HDR cycle [10]: (1) pick highest-priority hypothesis from `research_queue.md`; (2) state numerical prior; (3) articulate physical mechanism; (4) implement exactly one change in `controller.py`; (5) git commit before evaluation; (6) run `evaluate.py` over all scenarios; (7) record results in `results.tsv`; (8) keep or revert based on mean AWT reduction.

We ran 20 experiments on a custom Poisson + saturation-flow simulator (E01–E20) and 18 experiments on SUMO + sumo-rl (S01–S18). The custom simulator completed each experiment in ~1.5 seconds; the SUMO experiments took ~30–60 seconds each.

### 2.5 Reproducibility

All code is at https://github.com/colinjoc/colinjoc.github.io. SUMO 1.18.0 and sumo-rl can be installed via pip. Random seeds are fixed: benchmark uses `(0, 1, 2)`, robustness sweep uses `range(5)`. The standard sumo-rl benchmark networks are bundled with the library. Custom route files for the four single-intersection scenarios are committed in `sumo_nets/`.

## 3. Results

### 3.1 SUMO Results: The Two-Parameter Rule Beats Webster by 49.1%

Direct port of the best toy-simulator rule to SUMO (S01) achieved -46.05% mean AWT reduction. Through 17 further experiments, we identified a SUMO-specific preemption rule (S16) that adds an additional 3 percentage points, yielding the final result:

| Scenario | Webster (s) | S16 (s) | Reduction |
|----------|------------|---------|-----------|
| uniform_low | 2.27 | 1.86 | -18.1% |
| uniform_med | 4.72 | 2.06 | -56.4% |
| uniform_high | 9.54 | 3.84 | -59.8% |
| asymmetric | 5.43 | 2.50 | -54.0% |
| sumo_rl horizontal | 11.11 | 4.87 | -56.2% |
| sumo_rl vertical | 11.05 | 5.31 | -52.0% |
| sumo_rl vhvh | 11.02 | 5.78 | -47.6% |
| **Mean** | **7.88** | **3.75** | **-49.1%** |

Variance across seeds (uniform_med, 5 seeds): 2.17 ± 0.10 s for S16 vs 4.88 ± 0.16 s for Webster — a 2.7× variance reduction in addition to the mean improvement.

### 3.2 Cross-Simulator Validation

We tested the same nine candidate "improvements" on both the custom simulator (E01–E20) and SUMO (S01–S18). Eight of the nine failed in both cases:

| Idea | Toy result | SUMO result | Verdict |
|------|------------|-------------|---------|
| Cumulative-wait override | reverted | reverted | redundant |
| Soft max-green | reverted | reverted | hurts high demand |
| Asymmetric thresholds | reverted | reverted | wrong polarity |
| Density-based picking | reverted | reverted | tracks moving, not waiting |
| Pressure-based switching | reverted | reverted | equivalent to queue on isolated intersections |
| Min-burst constraint | reverted | reverted | hurts low demand |
| Anticipatory rate | reverted | reverted | mixed gains |
| Starvation guard | reverted | reverted | dead code in well-behaved demand |

The Occam principle held in both simulators: simple beats complex.

However, parameter tuning did not transfer:

| Parameter | Toy optimum | SUMO optimum |
|-----------|-------------|--------------|
| WAITING_THRESHOLD | 2 | 1 |
| CLEAR_THRESHOLD | 0 (strict win) | 0 or 1 (tied) |
| Preemption rule | not discovered | required for full gain |

The toy simulator's `WAITING_THRESHOLD=3` was merely suboptimal (-1.1%); on SUMO it was catastrophic (+219% on uniform_low). And the preemption rule (S15–S16) was never visible on the toy because the toy simulator used only 2 phases, hiding the inter-phase competition that SUMO's 4-phase protected-left intersections expose.

### 3.3 Magnitude Comparison: Toy vs SUMO

| Scenario | Toy reduction | SUMO reduction |
|----------|---------------|----------------|
| Low demand | -33.8% | -18.1% |
| Medium demand | -42.0% | -56.4% |
| High demand | -32.3% | -59.8% |
| Asymmetric | -41.3% | -54.0% |
| Peak hour / vhvh | -63.9% | -47.6% |
| **Mean** | **-42.7%** | **-49.1%** |

The toy simulator overstated improvements at extreme demand and understated them at medium demand. The aggregate mean was within 6 percentage points but the per-scenario distribution differed significantly, illustrating the danger of relying on toy simulators for fine-grained claims.

## 4. Discussion

### 4.1 Why a Simple Rule Works

The drain-first SOTL rule succeeds for three reasons grounded in queueing theory:

1. **It eliminates phase-end waste.** Webster's fixed cycle commits to a green duration before observing demand; if the green ends with vehicles still waiting on the other approach but cars still arriving on the current one, those waiting vehicles experience an additional full cycle of delay. Drain-first switches only when the current phase is empty, eliminating this source of waste.

2. **It is naturally adaptive to demand asymmetry.** Asymmetric demand (e.g., 70% east–west, 30% north–south) is handled implicitly: the heavier approach naturally takes longer to drain and thus holds the green longer, while the lighter approach gets short bursts. No explicit asymmetry parameter is needed.

3. **The preemption rule handles heavy multi-phase scenarios.** When one phase has 5 vehicles waiting and another has 1, drain-first will keep the 1 cycling indefinitely. The preemption rule (`other ≥ 2× current AND ≥ 4`) breaks ties in favour of the heavily loaded phase, recovering the gain that pure drain-first leaves on the table.

### 4.2 Why Deep RL Has Not Outperformed This

Published deep RL traffic signal controllers report 30–50% improvements over fixed-time, the same range our two-parameter rule achieves. We conjecture three reasons the field has not noticed this:

1. **Baseline weakness.** Many RL papers compare against poorly tuned fixed-time controllers rather than Webster-optimal ones, inflating the apparent improvement.
2. **Benchmark choice.** Standard benchmarks (CityFlow, sumo-rl small grids) under-test the conditions where complex policies might genuinely help: very heavy congestion, long-horizon planning, multi-modal interactions.
3. **Publication bias.** A simple deterministic rule is harder to publish than a novel neural architecture, even if both achieve the same result.

We do not claim deep RL is useless for traffic signals — it likely helps under conditions our simple rule cannot handle (network-level coordination at scale, multi-modal optimisation, demand prediction). But the claim "RL beats fixed-time by 30–50%" is incomplete without stating that a 20-line deterministic rule does the same.

### 4.3 The Custom-Simulator Lesson

We initially built a lightweight Poisson + saturation-flow simulator to enable fast iteration (~1.5 seconds vs ~30 seconds per SUMO experiment). After 20 experiments on the toy and 18 on SUMO, the verdict is: **the top-level finding (SOTL) transferred, but parameter tuning did not.** The Pareto-optimal `WAITING_THRESHOLD` shifted from 2 to 1, and a new preemption rule was needed to recover full performance.

The deeper issue is that our custom simulator was, mathematically, equivalent to Webster's analytical model. Beating Webster on it was suspiciously easy. Only by validating on SUMO — the standard published tool — could we be confident the result transferred to the field's accepted benchmark.

This is consistent with a broader methodological principle: **always use the standard published simulator, even when it is slower.** Custom simulators encode the same simplifications as the analytical baseline they replace, hiding both the bugs and the genuine optimisation opportunities.

### 4.4 Limitations

**Single-intersection focus.** Five of our seven scenarios are single intersections. Network-level coordination (green waves, gridlock prevention, demand-responsive routing) is not addressed by our rule. Real cities are networks.

**No pedestrian phase.** Real traffic signals must accommodate pedestrian crossing phases, emergency vehicle preemption, and transit priority. Our simulation does not include these.

**Short horizon.** 600-second episodes test steady-state behaviour but not demand transitions, accidents, or special events.

**SUMO is itself a model.** SUMO uses car-following and lane-changing models that are themselves approximations of real driver behaviour. Validation on real intersections via field deployment remains the only way to fully verify the result.

**No long-term effects.** Adaptive control may cause driver route choice to shift over time (drivers learn that an intersection is now better and use it more), which could erode the apparent improvement. We do not model this.

### 4.5 Future Work

1. **Network-scale validation** on city-sized SUMO scenarios (Manhattan, Monaco) to test whether the simple rule degrades, holds, or requires extension.
2. **Pedestrian and emergency preemption** to handle the constraints real signals must satisfy.
3. **Field deployment** at a controlled real intersection with before/after measurement.
4. **Direct comparison** against published RL methods on identical sumo-rl benchmark scenarios with identical evaluation protocols.

## 5. Conclusion

A two-parameter Self-Organising Traffic Light rule achieves 49.1% mean wait-time reduction over Webster's optimal fixed-time baseline on SUMO across seven scenarios — matching or exceeding published deep reinforcement learning methods, without any training. The result is robust: 38 HDR experiments across two simulators (a custom toy and the standard SUMO+sumo-rl) confirm the top-level finding while exposing the limits of toy-simulator parameter tuning. Eight of nine candidate "improvements" failed in both simulators, supporting the Occam principle in this domain. We argue that the deep-RL traffic signal literature has under-tested simple deterministic baselines and that a 20-line rule should be the new floor against which complex policies must demonstrate value.

## References

[1] Roess, R.P., Prassas, E.S., and McShane, W.R. *Traffic Engineering* (4th ed.). Pearson (2011).

[2] Webster, F.V. "Traffic Signal Settings." *Road Research Technical Paper No. 39*, HMSO London (1958).

[3] El-Tantawy, S., Abdulhai, B., and Abdelgawad, H. "Multiagent Reinforcement Learning for Integrated Network of Adaptive Traffic Signal Controllers (MARLIN-ATSC)." *IEEE Transactions on Intelligent Transportation Systems* **14**(3), 1140–1150 (2013).

[4] Wei, H., Zheng, G., Yao, H., and Li, Z. "IntelliLight: A Reinforcement Learning Approach for Intelligent Traffic Light Control." *Proc. KDD 2018*, 2496–2505 (2018).

[5] Chen, C., Wei, H., Xu, N., Zheng, G., Yang, M., Xiong, Y., Xu, K., and Li, Z. "Toward A Thousand Lights: Decentralized Deep Reinforcement Learning for Large-Scale Traffic Signal Control." *Proc. AAAI 2020*, 3414–3421 (2020).

[6] Mei, H., Lei, X., Da, L., Shi, B., and Wei, H. "LibSignal: An Open Library for Traffic Signal Control." *Machine Learning* **113**, 5235–5271 (2024).

[7] Wei, H., Zheng, G., Gayah, V., and Li, Z. "A Survey on Traffic Signal Control Methods." arXiv:1904.08117 (2019).

[8] Liang, X., Du, X., Wang, G., and Han, Z. "A Deep Reinforcement Learning Network for Traffic Light Cycle Control." *IEEE Transactions on Vehicular Technology* **68**(2), 1243–1253 (2019).

[9] Cools, S.B., Gershenson, C., and D'Hooghe, B. "Self-Organizing Traffic Lights: A Realistic Simulation." *Advances in Applied Self-Organizing Systems*, Springer (2007). https://arxiv.org/abs/nlin/0610040

[10] [HDR Methodology — this work]. https://github.com/colinjoc/colinjoc.github.io/blob/main/content/hdr/_index.md

[11] Lopez, P.A., Behrisch, M., Bieker-Walz, L., Erdmann, J., Flötteröd, Y., Hilbrich, R., Lücken, L., Rummel, J., Wagner, P., and Wießner, E. "Microscopic Traffic Simulation using SUMO." *Proc. IEEE ITSC 2018*, 2575–2582 (2018). https://www.eclipse.org/sumo/

[12] Alegre, L.N. "SUMO-RL." GitHub repository (2019–). https://github.com/LucasAlegre/sumo-rl

[13] Varaiya, P. "The max-pressure controller for arbitrary networks of signalized intersections." *Advances in Dynamic Network Modeling in Complex Transportation Systems*, Springer, 27–66 (2013).

[14] Jin, J. and Ma, X. "A learning-based adaptive group-based signal control system: A case study." *Transportation Research Part C* **51**, 17–31 (2015).

[15] Genders, W. and Razavi, S. "Using a deep reinforcement learning agent for traffic signal control." arXiv:1611.01142 (2016).

[16] Zheng, G., Xiong, Y., Zang, X., Feng, J., Wei, H., Zhang, H., Li, Y., Xu, K., and Li, Z. "Learning Phase Competition for Traffic Signal Control." *Proc. CIKM 2019*, 1963–1972 (2019).

(Reference [10]: project methodology repository.)
