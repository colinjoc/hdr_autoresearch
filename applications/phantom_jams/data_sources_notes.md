# Data Sources Notes — Phantom Jams Phase 0

Narrative covering usability, simulator status, canonical configurations,
standard metrics, and the experiment plan for Phases 0.5 through 2.

--------------------------------------------------------------------------------

## Which Data Sources Are Actually Usable Right Now

| Source | Usable? | Notes |
|--------|---------|-------|
| I-24 MOTION INCEPTION | Yes, after registration | Free account, ~1 day approval |
| NGSIM (US 101, I-80) | Yes, immediate | Public domain, data.transportation.gov |
| highD | Conditional | Requires academic application |
| Sugiyama 2008 raw data | No | Not publicly released |
| SUMO | Yes (installed v1.18.0) | TraCI works via PYTHONPATH; libsumo broken |
| Flow | No | Stale since 2020; do not depend on |
| CIRCLES algos-stack | Partially | MIT-licensed controller code; no runnable RL artifacts |
| CIRCLES energy models | Yes | MATLAB fuel models, useful for calibration |

**Bottom line**: For Phase 0, we do not need any external trajectory data.
The ring-road simulator (sim_ring_road.py) generates synthetic trajectories
with known ground truth.  External data (NGSIM, I-24 MOTION) becomes relevant
in Phase 3+ for calibration and validation.

--------------------------------------------------------------------------------

## I-24 MOTION Detail

The I-24 MOTION system is the 4-mile instrumented section of Interstate 24
in Nashville, Tennessee, operated by Vanderbilt University in partnership with
TDOT.  The initial public dataset is codenamed "INCEPTION" v1.0.0.

**Key question: does INCEPTION include the MVT runs?**  Based on the website
language ("the initial dataset described in this article"), INCEPTION appears
to be the first system-characterisation release, not specifically the MVT data.
The MVT (MegaVanderTest, November 2022) involved deploying ~100 CIRCLES AVs;
that data may be released under a separate codename.  The "Data Calendar"
page at https://i24motion.org/data should be checked periodically for new
named releases.

The trajectory format (per I24M_documentation repo) uses:
- 25 Hz base sampling rate
- State Plane Tennessee coordinates
- Vehicle-level tracks with ID, position, speed, lane, class

--------------------------------------------------------------------------------

## SUMO Installation Status

SUMO 1.18.0 is installed system-wide at `/usr/share/sumo/`.

- `sumo` binary: works (`sumo --version` confirms 1.18.0)
- **TraCI** (pure-python): works when PYTHONPATH includes `/usr/share/sumo/tools`
- **libsumo** (C++ bindings): broken (circular import in `_libsumo`)
- **sumo-rl** (Gymnasium wrapper): not installed (not needed for ring road)

For the ring-road phantom jam experiments, we use the **pure-Python IDM
integrator** (sim_ring_road.py) instead of SUMO.  Reasons:
1. The ring road is a 1-D ODE system; SUMO's network/routing overhead is unnecessary
2. Forward Euler at dt=0.1 s is stable and sufficient for IDM dynamics
3. No external process / socket communication needed
4. Deterministic by construction (seeded RNG for noise)
5. ~100x faster than SUMO+TraCI for the same experiment

SUMO remains available for Phase 3+ if we need multi-lane highways, on/off
ramps, or heterogeneous traffic.

--------------------------------------------------------------------------------

## Flow Framework Status

**Flow is effectively dead.**  Last release: v0.4.1 (September 2019).  Last
commit on master: December 2020.  173+ open issues with no maintainer response.
Dependencies include deprecated rllab and TensorFlow 1.x.

Flow's ring-road environment was the canonical RL benchmark for phantom jam
suppression (Vinitsky et al. 2018, Wu et al. 2022).  We preserve its
configuration parameters but implement the simulator independently.

For RL in Phase 2, we will wrap sim_ring_road.py as a Gymnasium environment
directly, avoiding the Flow dependency entirely.

--------------------------------------------------------------------------------

## Canonical Ring-Road Configurations

The literature uses several standard ring-road setups:

### 1. Sugiyama (22 vehicles / 230 m)

- **Source**: Sugiyama et al. (2008), NJP 10 033001
- **Vehicles**: 22
- **Circumference**: 230 m
- **Vehicle length**: ~4.5-5.0 m
- **Equilibrium spacing**: ~10.45 m (gap ~5.45 m)
- **Observed wave speed**: ~20 km/h (~5.6 m/s) backward
- **Use**: Original experiment; the gold standard for phantom jam demonstration

### 2. Flow ring (22 vehicles / 230 m, RL variant)

- **Source**: Wu et al. (2017), Vinitsky et al. (2018)
- **Same physical setup** as Sugiyama, but with IDM parameters tuned for
  SUMO compatibility and RL training
- **Penetration rates tested**: 1/22 (~4.5%), 2/22 (~9%), up to 10/22 (~45%)
- **Use**: RL benchmark; shows that 1 AV out of 22 can dampen waves

### 3. Extended ring (40 vehicles / 400-600 m)

- **Source**: Stern et al. (2018), various follow-ups
- **Use**: Larger ring to study multiple simultaneous waves and higher
  penetration rates

### 4. Large-scale ring (100-200 vehicles / 1-2 km)

- **Source**: Various computational studies
- **Use**: Scaling laws; how does the minimum penetration rate change
  with ring size?

**Our default**: 22 vehicles / 230 m (Sugiyama).  This is the most-studied
configuration and allows direct comparison with the literature.

--------------------------------------------------------------------------------

## Standard Metrics the Field Reports

| Metric | Definition | Units | Source |
|--------|-----------|-------|--------|
| Wave amplitude | max(v) - min(v) across vehicles at each timestep, averaged | m/s | Sugiyama 2008 |
| Mean velocity | Time-and-vehicle-averaged speed | m/s | Standard |
| Velocity variance (sigma_v) | Std of velocity across all vehicles in steady state | m/s | Stern 2018 |
| Wave propagation speed | Speed of the velocity-minimum point around the ring | m/s | Sugiyama 2008 |
| Throughput | Vehicles/hour past a cross-section (Edie's definition) | veh/hr | Edie 1963 |
| Fuel consumption | VT-Micro proxy or CIRCLES energy model | mL/km or L/100km | Rakha 2004 |
| Time-to-collision (TTC) | Minimum gap / closing speed | s | Standard safety |
| Percentage of time in stop-and-go | Fraction of time where any vehicle has v < 1 m/s | % | Stern 2018 |

Our measurements.py implements: wave amplitude, wave speed, wave period,
velocity variance, throughput (Edie), and fuel proxy (VT-Micro style).

--------------------------------------------------------------------------------

## Phase 0.5 Baseline Recipe

**Goal**: Establish the uncontrolled baseline wave characteristics.

```
1. Run 22-vehicle / 230-m ring for 600 s, all IDM, seed=42
2. Discard first 200 s (transient)
3. Measure:
   - Wave amplitude (mean and max of per-step v_range)
   - Wave propagation speed (linear regression on jam position)
   - Wave period (FFT of mean velocity signal)
   - Velocity variance (std of v in steady state)
   - Throughput (Edie's definition)
   - Fuel proxy (VT-Micro)
4. Repeat for seeds 42-51 (10 seeds) to report mean +/- std
5. Compare with literature:
   - Sugiyama: wave speed ~20 km/h, amplitude ~several m/s
   - Flow benchmark: similar values
```

**Current baseline results** (seed=42, 600 s):
- Wave amplitude (mean): 8.17 m/s
- Wave amplitude (max): 8.88 m/s
- Wave speed: -5.36 m/s (backward)
- Wave period: 400.10 s
- Throughput: 1039 veh/hr
- Velocity std: 2.89 m/s
- Fuel proxy: 130.65 mL/km

The wave speed of -5.36 m/s is close to the Sugiyama experimental value of
~-5.6 m/s.  The wave amplitude is consistent with strong stop-and-go
oscillations (vehicles reach 0 m/s, i.e., complete stops).

--------------------------------------------------------------------------------

## Phase 1 Tournament Plan

**Goal**: Find the best controller and minimum penetration rate.

### Penetration Rates

| Smart vehicles | Penetration | Label |
|---------------|-------------|-------|
| 1 / 22 | 4.5% | Minimal |
| 2 / 22 | 9.1% | Low |
| 4 / 22 | 18.2% | Moderate |
| 6 / 22 | 27.3% | High |
| 11 / 22 | 50.0% | Half |

### Controllers

1. IDMController (control = no change; this IS the baseline)
2. FollowerStopper (Stern 2018)
3. PIWithSaturation (Stern 2018)
4. ACCController (Milanes & Shladover 2014)
5. ConstantVelocityController (simplest possible)
6. PlaceholderRLController (to be replaced by trained policy in Phase 2)

### Experiment Matrix

5 penetration rates x 5 active controllers x 10 seeds = 250 runs.
Each run: 600 s, dt=0.1 s, ~132K trajectory rows.
Estimated wall time: ~250 x 2 s = ~8 minutes (pure Python, single-threaded).

### Success Criteria

- **Primary**: Wave amplitude reduction > 50% vs. baseline
- **Secondary**: Velocity variance reduction, throughput increase, fuel savings
- **Minimum penetration**: Find the lowest fraction that achieves > 50%
  amplitude reduction for the best controller

--------------------------------------------------------------------------------

## Phase 2 Sweep Plan

### Controller Gain Sweeps

For each promising controller from Phase 1, sweep the key gains:

- **FollowerStopper**: s_st in [3, 5, 8, 12], s_go in [20, 35, 50], k_v in [0.3, 0.5, 0.8]
- **PIWithSaturation**: k_p in [0.2, 0.4, 0.8], k_i in [0.01, 0.02, 0.05], T_des in [1.0, 1.5, 2.0]
- **ACC**: T_des in [1.2, 1.5, 1.8, 2.5], k1 in [0.1, 0.3, 0.5], k2 in [0.3, 0.5, 0.8]

### Penetration-Rate Sweeps

Fine-grained sweep from 0% to 50% in 2% increments for the best controller
configuration from the gain sweep.

### Car-Following Model Perturbations

Test robustness of the best controller against:
- IDM parameter variations: T in [0.8, 1.0, 1.2], a in [1.0, 1.3, 1.6]
- Different noise levels: sigma in [0.0, 0.1, 0.3, 0.5, 1.0]
- Heterogeneous populations (mix of aggressive and timid IDM parameters)

### Noise-Level Sensitivity

The acceleration noise (sigma) controls how quickly the jam forms and how
strong it is.  Sweep sigma from 0.0 to 1.0 to characterise:
- At what noise level does the jam first appear? (bifurcation point)
- How does the minimum penetration rate change with noise?
- Is the best controller robust to high noise?

### Ring-Size Scaling

Repeat the best configuration at:
- 22 / 230 m (Sugiyama)
- 40 / 400 m
- 100 / 1000 m
- 200 / 2000 m

to determine if the minimum penetration rate scales with ring size.
