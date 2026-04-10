# Headline Recommendations

## Top 5 Actionable Findings

1. **Minimum Adaptive Cruise Control (ACC) penetration for wave suppression (<1 m/s amplitude): 4/22 vehicles (18.2%)**. At this penetration, wave amplitude drops from 8.17 m/s to 0.55 m/s -- a 93.3% reduction. The transition is sharp: 3/22 (13.6%) still has 1.77 m/s amplitude.

2. **Minimum FollowerStopper (FS) penetration for wave suppression (<1 m/s): 5/22 vehicles (22.7%)**. Default-tuned FS achieves 0.74 m/s at 5/22. However, FS severely degrades throughput (from 1039 to 401 veh/hr at 5/22), making ACC strictly preferable.

3. **ACC dominates all other controllers**. At every penetration level from 4/22 upward, ACC achieves both lower wave amplitude AND higher throughput than FS. The ACC maintains 930 veh/hr throughput at 4/22 vs FS's 529 veh/hr -- nearly double.

4. **PIWithSaturation is catastrophically unstable** on the ring road. At 18.2% penetration it produces wave amplitudes of 30+ m/s (worse than baseline). Even with extensive gain tuning (H027-H033), the best PI result was 3.01 m/s with T_des=2.5. Integral windup from persistent gap error causes runaway oscillation.

5. **The ring road is a simplified model**. These results represent an upper bound on real-highway effectiveness. The ring has no lane changes, no on-ramps, no speed limit heterogeneity, and no multi-lane dynamics. Real-world critical penetration rates are likely higher.

## Secondary Findings

- Ring-tuned FS (v_des=6, s_st=2, s_go=12, k_v=0.8) performed worse than default FS at the same penetration, requiring 19/22 (86.4%) for wave_amp < 1 m/s. The ring-tuned parameters actually cause the FS to operate in a suboptimal regime.
- Noise level has minimal effect on steady-state wave amplitude (H055-H059: 5.92-8.23 m/s across noise_std 0-1.0).
- The perturbation type and timing have negligible effect on steady-state wave characteristics (H062-H065).
- ACC with shorter time headway (T_des < 1.4 s) is worse because it becomes string-unstable on the ring (H034-H035).
- Vehicle placement matters moderately: clustered FS (H066, 7.18 m/s) is worse than equally-spaced (T04, 4.44 m/s).
