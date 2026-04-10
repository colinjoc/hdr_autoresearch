# Design Variables Catalogue

All simulator levers for the phantom traffic jam ring-road experiments. Each variable lists its name, type, units, allowed range, current default, mechanism, and whether it is flagged for Phase B (multi-dimensional search).

---

## 1. Ring Geometry

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `ring_length` | continuous | m | 50 - 4000 | 230.0 | Sets density ρ = N / L; the Sugiyama instability requires ρ to sit inside the string-unstable band. Larger rings support more wavelengths and reduce finite-size effects [1, 2, 29]. | Yes |
| `n_vehicles` | integer | - | 5 - 200 | 22 | Together with ring_length determines the equilibrium gap s* = L/N - l_veh. The Sugiyama threshold is 22 vehicles on 230 m [1]. | Yes |
| `veh_length` | continuous | m | 3.0 - 7.0 | 5.0 | Physical vehicle length; affects gap computation. Standard passenger car ~5 m [29]. | No |

## 2. Integration Parameters

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `dt` | continuous | s | 0.01 - 0.5 | 0.1 | Forward-Euler timestep. Must be small relative to IDM characteristic time T to maintain stability. Smaller dt improves accuracy but increases runtime linearly. | No |
| `t_max` | continuous | s | 60 - 3600 | 600.0 | Total simulation time. Must be long enough for the wave to develop (typically >100 s) and for steady-state statistics to converge. | No |
| `seed` | integer | - | 0 - 2^31 | 42 | Random seed for noise and initial velocity perturbations. Controls reproducibility. | No |

## 3. Human Driver Model (IDM)

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `idm_v0` | continuous | m/s | 5.0 - 40.0 | 30.0 | Desired free-flow speed. On the ring, equilibrium speed is much lower than v0 due to density. Higher v0 increases the IDM's acceleration drive. Standard: 30 m/s for ring, 33 m/s for highway [17, 29]. | No |
| `idm_T` | continuous | s | 0.5 - 3.0 | 1.0 | Safe time headway. The primary stability lever: lower T makes the system more string-unstable. Default 1.0 s is tuned for Sugiyama instability; the textbook value is 1.5 s [29]. | Yes |
| `idm_a` | continuous | m/s^2 | 0.3 - 3.0 | 1.3 | Maximum acceleration. Higher a means faster response, which can either stabilise (quicker recovery) or destabilise (sharper reaction). Default 1.3 is a Flow benchmark value [6, 29]. | Yes |
| `idm_b` | continuous | m/s^2 | 0.5 - 4.0 | 2.0 | Comfortable deceleration. Higher b means the driver tolerates harder braking before gap becomes uncomfortable. Affects the desired gap s* [17]. | No |
| `idm_delta` | continuous | - | 1.0 - 8.0 | 4.0 | Acceleration exponent. Controls how quickly acceleration drops as v approaches v0. Standard value is 4 [17]. | No |
| `idm_s0` | continuous | m | 0.5 - 5.0 | 2.0 | Minimum standstill gap. Sets the jam density floor. Standard 2 m [17, 29]. | No |
| `noise_std` | continuous | m/s^2 | 0.0 - 1.5 | 0.3 | Gaussian acceleration noise applied to human drivers each timestep. Triggers the instability from the linearly-marginally-stable regime. Higher noise = earlier and stronger wave formation [4, 210]. | Yes |

## 4. Initial Perturbation

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `perturb_vehicle` | integer | - | 0 - N-1 | 0 | Index of the vehicle receiving the initial brake perturbation. | No |
| `perturb_time` | continuous | s | 0 - 60 | 5.0 | Time at which the perturbation is applied. Must be after initial transients settle. | No |
| `perturb_decel` | continuous | m/s^2 | -9.0 - 0.0 | -5.0 | Strength of the initial brake pulse. More negative = stronger perturbation. A single-step impulse at -5 m/s^2 reliably seeds the wave. | No |

## 5. Smart Vehicle Deployment

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `n_smart` | integer | - | 0 - N | 0 | Number of smart (controlled) vehicles. Penetration rate = n_smart / n_vehicles. The central design variable for the project [4, 5, 9, 12]. | Yes |
| `placement_strategy` | categorical | - | {equally_spaced, clustered, random} | equally_spaced | Spatial distribution of smart vehicles around the ring. Equally spaced maximises the distance between consecutive AVs, which theory predicts is optimal for wave suppression [12, 38]. | Yes |
| `controller_type` | categorical | - | {IDM, FollowerStopper, PIWithSaturation, ACC, ConstantVelocity, PlaceholderRL} | (none) | Which control policy the smart vehicles use. Each has different wave-suppression mechanism and safety profile [5, 12, 40]. | Yes |

## 6. FollowerStopper Parameters

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `fs_v_des` | continuous | m/s | 3.0 - 30.0 | 15.0 | Desired cruising speed. At this speed the controller is in free-flow mode. For a ring with equilibrium speed ~3-5 m/s, this is well above equilibrium — the gap dynamics dominate [5]. | Yes |
| `fs_s_st` | continuous | m | 1.0 - 15.0 | 5.0 | Stop gap threshold. Below this gap, v_cmd = 0 (full stop target). Sets the safety margin [5, 217]. | Yes |
| `fs_s_go` | continuous | m | 10.0 - 60.0 | 35.0 | Free-flow gap threshold. Above this gap, the controller cruises at v_des. Controls how early the AV begins to slow when approaching a queue [5]. | Yes |
| `fs_k_v` | continuous | 1/s | 0.1 - 2.0 | 0.5 | Proportional gain on velocity error (v_cmd - own_v). Higher gain = faster response but more oscillation risk [5]. | Yes |

## 7. PIWithSaturation Parameters

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `pi_T_des` | continuous | s | 0.5 - 3.0 | 1.5 | Desired time headway. Sets the target gap = s0 + v * T_des. Larger T_des = more conservative spacing [5]. | Yes |
| `pi_s0` | continuous | m | 1.0 - 10.0 | 5.0 | Minimum standstill gap for the PI target. | No |
| `pi_k_p` | continuous | - | 0.05 - 2.0 | 0.4 | Proportional gain. Controls how aggressively the controller responds to gap error [5]. | Yes |
| `pi_k_i` | continuous | - | 0.001 - 0.2 | 0.02 | Integral gain. Eliminates steady-state gap error but too high causes oscillation [5]. | Yes |
| `pi_a_max` | continuous | m/s^2 | 0.5 - 3.0 | 1.3 | Saturation upper limit for acceleration. | No |
| `pi_a_min` | continuous | m/s^2 | -4.0 - -0.5 | -2.0 | Saturation lower limit (deceleration). | No |

## 8. ACCController Parameters

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `acc_v_des` | continuous | m/s | 5.0 - 35.0 | 20.0 | Desired cruise speed. Above the equilibrium ring speed — acts as an upper bound on AV speed [40, 99]. | No |
| `acc_T_des` | continuous | s | 0.5 - 4.0 | 1.8 | Desired time headway. The central lever for ACC string stability: must be > 2 * delay for string stability [88]. | Yes |
| `acc_s0` | continuous | m | 1.0 - 8.0 | 4.0 | Minimum standstill gap. | No |
| `acc_k1` | continuous | - | 0.05 - 1.0 | 0.3 | Gap-error gain. Higher k1 = faster gap tracking but more oscillatory [40]. | Yes |
| `acc_k2` | continuous | - | 0.1 - 2.0 | 0.5 | Speed-difference gain. Relative-velocity feedback for damping [40]. | Yes |

## 9. ConstantVelocityController Parameters

| Variable | Type | Units | Range | Default | Mechanism | Phase B |
|---|---|---|---|---|---|---|
| `cv_v_target` | continuous | m/s | 1.0 - 15.0 | 8.0 | Target constant speed. Should be near the ring equilibrium speed for meaningful results. If too high or too low, the AV creates an artificial bottleneck or unsafe condition [12]. | Yes |
| `cv_k_p` | continuous | 1/s | 0.1 - 5.0 | 1.0 | P-controller gain towards v_target. | No |

## 10. Derived / Computed Variables

| Variable | Expression | Units | Notes |
|---|---|---|---|
| `penetration_rate` | n_smart / n_vehicles | - | The primary independent variable. Range: 0 to 1 [4, 9, 12]. |
| `density` | n_vehicles / ring_length | veh/m | Equilibrium density. Sugiyama: 22/230 = 0.0957 veh/m = 95.7 veh/km [1]. |
| `equilibrium_gap` | ring_length / n_vehicles - veh_length | m | Gap if all vehicles were equally spaced. Sugiyama: 5.45 m. |
| `equilibrium_speed` | (from IDM steady-state solver) | m/s | The speed at which IDM acceleration = 0 at equilibrium gap. |

---

## Summary Statistics

- **Total design variables**: 37
- **Phase B (multi-dimensional search) variables**: 16
- **Categorical variables**: 2 (placement_strategy, controller_type)
- **Continuous variables**: 31
- **Integer variables**: 4

---

*End of design variables catalogue.*
