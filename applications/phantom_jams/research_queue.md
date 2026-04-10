# Research Queue: Pre-Registered Hypotheses

All hypotheses are single-change experiments relative to the canonical baseline:
22 vehicles, 230 m ring, 600 s, dt=0.1 s, seed=42, IDM human drivers (v0=30, T=1.0, a=1.3, b=2.0, delta=4, s0=2, noise_std=0.3).

**Primary metric** is wave amplitude unless otherwise noted. The noise floor from the 5-seed baseline sweep is:
- wave_amp: 0.20 m/s (1-sigma)
- vel_var: 0.05 m/s
- throughput: 7.6 veh/hr
- fuel: 0.99 mL/km

KEEP threshold: improvement must exceed 2-sigma (e.g., wave_amp reduction > 0.40 m/s).

---

## Theme 1: Penetration Rate Sweep (FollowerStopper)

### H001: FollowerStopper at 4.5% penetration (1/22)
- **Prior**: 0.25 (Stern 2018 showed 1/22 works on their ring; our ring parameters differ)
- **Mechanism**: A single AV absorbs the wave's trailing edge by refusing to accelerate into the queue, breaking the feedback loop [4, 5].
- **Single change**: Insert 1 FollowerStopper at index 0 (baseline has 0 smart vehicles)
- **Expected effect**: -1 to -3 m/s wave amplitude
- **Primary metric**: wave amplitude

### H002: FollowerStopper at 9.1% penetration (2/22)
- **Prior**: 0.45
- **Mechanism**: Two equally spaced AVs each damp half the ring. The wave must pass through two dampers per circuit, doubling the dissipation rate [4, 12].
- **Single change**: Insert 2 FollowerStopper vehicles, equally spaced
- **Expected effect**: -3 to -5 m/s wave amplitude
- **Primary metric**: wave amplitude

### H003: FollowerStopper at 13.6% penetration (3/22)
- **Prior**: 0.55
- **Mechanism**: Three AVs reduce the maximum undamped platoon length to ~6 humans. Below the critical platoon length for wave growth [12, 38].
- **Single change**: Insert 3 FollowerStopper vehicles, equally spaced
- **Expected effect**: -4 to -6 m/s wave amplitude
- **Primary metric**: wave amplitude

### H004: FollowerStopper at 18.2% penetration (4/22)
- **Prior**: 0.65 (confirmed in T04: wave_amp dropped to 4.44 m/s)
- **Mechanism**: Four AVs keep every human platoon to at most 4-5 vehicles, well below the string-instability growth threshold for these IDM parameters [12].
- **Single change**: Insert 4 FollowerStopper vehicles, equally spaced
- **Expected effect**: -4 to -6 m/s wave amplitude
- **Primary metric**: wave amplitude

### H005: FollowerStopper at 27.3% penetration (6/22)
- **Prior**: 0.75
- **Mechanism**: Six AVs limit every platoon to ~2-3 humans. Disturbances cannot grow across such short chains [37, 38].
- **Single change**: Insert 6 FollowerStopper vehicles, equally spaced
- **Expected effect**: -6 to -8 m/s wave amplitude; near-complete suppression
- **Primary metric**: wave amplitude

### H006: FollowerStopper at 36.4% penetration (8/22)
- **Prior**: 0.85
- **Mechanism**: With 8 AVs every human platoon is at most 1-2 vehicles. No amplification is possible in a 1-2 vehicle chain [37].
- **Single change**: Insert 8 FollowerStopper vehicles, equally spaced
- **Expected effect**: wave amplitude < 1 m/s
- **Primary metric**: wave amplitude

### H007: FollowerStopper at 50% penetration (11/22)
- **Prior**: 0.90
- **Mechanism**: Every human driver is immediately followed by an AV. Disturbance dies within one vehicle [12, 38].
- **Single change**: Insert 11 FollowerStopper vehicles, equally spaced
- **Expected effect**: wave amplitude < 0.5 m/s
- **Primary metric**: wave amplitude

### H008: FollowerStopper at 100% penetration (22/22)
- **Prior**: 0.95
- **Mechanism**: No human drivers. The FollowerStopper-only ring should converge to uniform flow at v_des or the equilibrium gap speed, whichever is lower [5]. Already confirmed in T11: wave_amp = 0.0.
- **Single change**: All 22 vehicles use FollowerStopper
- **Expected effect**: wave amplitude = 0
- **Primary metric**: wave amplitude

---

## Theme 2: Controller Family Comparison at Fixed Penetration

### H009: IDM "smart" at 4.5% (control condition)
- **Prior**: 0.15 (IDM smart vehicles have no wave suppression mechanism; just seed variation)
- **Mechanism**: Null control: replacing one IDM with another IDM should not change the wave. Any observed difference is seed/placement noise.
- **Single change**: 1 vehicle marked "smart" but using IDM with same params
- **Expected effect**: no change (within noise floor)
- **Primary metric**: wave amplitude

### H010: IDM "smart" at 18.2% (control condition)
- **Prior**: 0.15
- **Mechanism**: Same as H009 but at higher penetration. Controls for the effect of vehicle placement.
- **Single change**: 4 vehicles marked "smart" but using IDM
- **Expected effect**: no change (within noise floor)
- **Primary metric**: wave amplitude

### H011: PIWithSaturation at 4.5%
- **Prior**: 0.25
- **Mechanism**: PI tracks the mean leader velocity with integral feedback, smoothing oscillations [5]. Performance should be comparable to FollowerStopper at low penetration.
- **Single change**: 1 PIWithSaturation vehicle
- **Expected effect**: -0.5 to -2 m/s wave amplitude
- **Primary metric**: wave amplitude

### H012: PIWithSaturation at 18.2%
- **Prior**: 0.30 (T06 showed 30.13 m/s -- catastrophic. Likely a tuning issue.)
- **Mechanism**: PI integral windup may destabilise at higher penetration if the desired gap T_des=1.5 is too large for the ring's equilibrium gap of ~5.5 m [5].
- **Single change**: 4 PIWithSaturation vehicles
- **Expected effect**: uncertain; may need gain tuning to help
- **Primary metric**: wave amplitude

### H013: ACC at 4.5%
- **Prior**: 0.30
- **Mechanism**: ACC maintains constant time headway with gap-error and speed-difference feedback. One ACC adds damping to its local platoon [40, 99].
- **Single change**: 1 ACC vehicle
- **Expected effect**: -0.5 to -1 m/s wave amplitude
- **Primary metric**: wave amplitude

### H014: ACC at 18.2%
- **Prior**: 0.60 (confirmed in T08: wave_amp dropped to 0.55 m/s)
- **Mechanism**: Four ACCs create strong damping zones throughout the ring. The k2 relative-velocity feedback directly opposes wave propagation [40].
- **Single change**: 4 ACC vehicles
- **Expected effect**: wave amplitude < 1 m/s
- **Primary metric**: wave amplitude

### H015: ConstantVelocity at 4.5%
- **Prior**: 0.50 (T09 showed 0.46 m/s -- surprisingly effective but safety concern)
- **Mechanism**: A vehicle maintaining constant speed acts as a perfect wave damper: it does not amplify any perturbation. However, it ignores safety (no gap reaction), which is not realistic [12].
- **Single change**: 1 ConstantVelocity vehicle
- **Expected effect**: large wave reduction but unsafe
- **Primary metric**: wave amplitude (note min_spacing)

### H016: ConstantVelocity at 18.2%
- **Prior**: 0.55
- **Mechanism**: Same as H015 scaled up. Four constant-velocity vehicles act as anchors that refuse to oscillate.
- **Single change**: 4 ConstantVelocity vehicles
- **Expected effect**: near-complete wave suppression but unsafe
- **Primary metric**: wave amplitude (note min_spacing)

---

## Theme 3: FollowerStopper Gain Tuning

### H017: FS v_des = 8.0 m/s (near ring equilibrium)
- **Prior**: 0.45
- **Mechanism**: Setting v_des near the ring equilibrium speed (~4-5 m/s) means the FS spends more time in cruise mode rather than the quadratic ramp region, potentially smoothing the velocity profile more effectively [5, 217].
- **Single change**: FollowerStopper v_des=8.0 (default 15.0), 4 vehicles at 18.2%
- **Expected effect**: -1 to -3 m/s wave amplitude vs T04
- **Primary metric**: wave amplitude

### H018: FS v_des = 5.0 m/s (at ring equilibrium)
- **Prior**: 0.50
- **Mechanism**: Even closer to equilibrium. The AV cruises at the flow speed and acts purely as a damper. Risk: too slow may reduce throughput [5].
- **Single change**: FollowerStopper v_des=5.0, 4 vehicles
- **Expected effect**: -1 to -3 m/s wave amplitude vs T04
- **Primary metric**: wave amplitude

### H019: FS v_des = 25.0 m/s (well above equilibrium)
- **Prior**: 0.20
- **Mechanism**: High v_des means the FS always wants to accelerate, spending most time in the cruise-toward-leader regime. May reduce damping effectiveness.
- **Single change**: FollowerStopper v_des=25.0, 4 vehicles
- **Expected effect**: worse than T04 (higher wave amplitude)
- **Primary metric**: wave amplitude

### H020: FS s_st = 2.0 m (tighter stop threshold)
- **Prior**: 0.35
- **Mechanism**: Smaller stop gap means the AV tolerates closer spacing before commanding zero speed. May allow it to stay in the quadratic ramp longer, absorbing more wave energy [5].
- **Single change**: FollowerStopper s_st=2.0 (default 5.0), 4 vehicles
- **Expected effect**: -0.5 to -2 m/s wave amplitude vs T04
- **Primary metric**: wave amplitude

### H021: FS s_st = 8.0 m (wider stop threshold)
- **Prior**: 0.30
- **Mechanism**: Larger stop gap = more conservative. The AV begins stopping earlier, which may create a larger gap and reduce throughput but provide more wave absorption time.
- **Single change**: FollowerStopper s_st=8.0, 4 vehicles
- **Expected effect**: lower throughput, possibly lower wave amplitude
- **Primary metric**: wave amplitude

### H022: FS s_go = 20.0 m (shorter free-flow transition)
- **Prior**: 0.40
- **Mechanism**: Narrower transition region means the AV switches from stop to cruise more abruptly. The quadratic ramp covers a smaller gap range [5].
- **Single change**: FollowerStopper s_go=20.0 (default 35.0), 4 vehicles
- **Expected effect**: uncertain; may help or hurt depending on equilibrium gap
- **Primary metric**: wave amplitude

### H023: FS s_go = 50.0 m (longer free-flow transition)
- **Prior**: 0.35
- **Mechanism**: Wider transition means the AV is in the quadratic ramp for most gap values encountered on the ring (~5-15 m). More gradual response.
- **Single change**: FollowerStopper s_go=50.0, 4 vehicles
- **Expected effect**: smoother response, potentially better damping
- **Primary metric**: wave amplitude

### H024: FS k_v = 0.2 (lower gain)
- **Prior**: 0.35
- **Mechanism**: Slower velocity-tracking response. The AV adjusts speed more gradually, which could reduce its own oscillation but also reduce its damping bandwidth [5].
- **Single change**: FollowerStopper k_v=0.2 (default 0.5), 4 vehicles
- **Expected effect**: uncertain; may smooth but also slow response
- **Primary metric**: wave amplitude

### H025: FS k_v = 1.0 (higher gain)
- **Prior**: 0.30
- **Mechanism**: Faster velocity tracking. The AV responds more quickly to gap changes, which could improve wave suppression but risk oscillation if gain is too high.
- **Single change**: FollowerStopper k_v=1.0, 4 vehicles
- **Expected effect**: uncertain; faster response vs oscillation risk
- **Primary metric**: wave amplitude

### H026: FS k_v = 2.0 (aggressive gain)
- **Prior**: 0.20
- **Mechanism**: Very aggressive gain. Likely to cause the AV itself to oscillate, worsening the wave rather than suppressing it.
- **Single change**: FollowerStopper k_v=2.0, 4 vehicles
- **Expected effect**: worse than T04 due to AV oscillation
- **Primary metric**: wave amplitude

---

## Theme 4: PIWithSaturation Gain Tuning

### H027: PI k_p = 0.1 (low proportional gain)
- **Prior**: 0.40
- **Mechanism**: Lower k_p reduces the proportional response to gap error. May prevent the instability seen in T06 (30.13 m/s wave) by reducing overshoot [5].
- **Single change**: PIWithSaturation k_p=0.1 (default 0.4), 4 vehicles at 18.2%
- **Expected effect**: large improvement over T06; wave_amp < 10 m/s
- **Primary metric**: wave amplitude

### H028: PI k_p = 0.8 (high proportional gain)
- **Prior**: 0.20
- **Mechanism**: Higher k_p increases responsiveness but likely worsens the oscillation problem seen in T06.
- **Single change**: PIWithSaturation k_p=0.8, 4 vehicles
- **Expected effect**: worse than T06
- **Primary metric**: wave amplitude

### H029: PI k_i = 0.005 (lower integral gain)
- **Prior**: 0.45
- **Mechanism**: Reducing integral gain slows the integral windup that likely caused T06's catastrophic instability [5].
- **Single change**: PIWithSaturation k_i=0.005 (default 0.02), 4 vehicles
- **Expected effect**: significant improvement over T06
- **Primary metric**: wave amplitude

### H030: PI k_i = 0.0 (pure P controller)
- **Prior**: 0.50
- **Mechanism**: Eliminating the integral term completely removes windup risk. Pure proportional control on gap error.
- **Single change**: PIWithSaturation k_i=0.0, 4 vehicles
- **Expected effect**: stable behaviour; wave_amp comparable to FS
- **Primary metric**: wave amplitude

### H031: PI k_i = 0.05 (higher integral gain)
- **Prior**: 0.15
- **Mechanism**: More integral action. Likely worsens windup instability.
- **Single change**: PIWithSaturation k_i=0.05, 4 vehicles
- **Expected effect**: worse than T06
- **Primary metric**: wave amplitude

### H032: PI T_des = 0.8 s (shorter desired headway)
- **Prior**: 0.45
- **Mechanism**: Shorter desired headway means the PI targets a smaller gap (s0 + v * 0.8 vs s0 + v * 1.5). On the ring with equilibrium gap ~5.5 m and speed ~4 m/s, desired gap drops from 11 m to 8.2 m, closer to the actual gap. Less gap error = less integral windup.
- **Single change**: PIWithSaturation T_des=0.8, 4 vehicles
- **Expected effect**: much better than T06; may fix the instability
- **Primary metric**: wave amplitude

### H033: PI T_des = 2.5 s (longer desired headway)
- **Prior**: 0.15
- **Mechanism**: Longer desired headway = larger target gap = persistent large gap error = more integral windup.
- **Single change**: PIWithSaturation T_des=2.5, 4 vehicles
- **Expected effect**: worse than T06
- **Primary metric**: wave amplitude

---

## Theme 5: ACC Time Headway Sweep

### H034: ACC T_des = 0.8 s
- **Prior**: 0.55
- **Mechanism**: Shorter time headway means tighter following. Below the string-stability threshold (h > 2*tau_delay) but the ACC here has no explicit delay. May increase throughput and reduce wave amplitude [88].
- **Single change**: ACC T_des=0.8 (default 1.8), 4 vehicles at 18.2%
- **Expected effect**: lower wave amplitude than T08 but potentially unsafe
- **Primary metric**: wave amplitude

### H035: ACC T_des = 1.0 s
- **Prior**: 0.55
- **Mechanism**: Moderate time headway. Near the string-stability boundary for delay-free ACC [88].
- **Single change**: ACC T_des=1.0, 4 vehicles
- **Expected effect**: similar to or slightly better than T08
- **Primary metric**: wave amplitude

### H036: ACC T_des = 1.4 s
- **Prior**: 0.50
- **Mechanism**: Slightly shorter than default. Less conservative spacing.
- **Single change**: ACC T_des=1.4, 4 vehicles
- **Expected effect**: similar to T08
- **Primary metric**: wave amplitude

### H037: ACC T_des = 2.5 s
- **Prior**: 0.40
- **Mechanism**: Very conservative spacing. The ACC maintains large gaps, which provides more absorption room but reduces throughput. May invite cut-ins in multilane settings [48].
- **Single change**: ACC T_des=2.5, 4 vehicles
- **Expected effect**: slightly higher wave amplitude than T08 due to large gap
- **Primary metric**: wave amplitude

### H038: ACC T_des = 3.0 s
- **Prior**: 0.35
- **Mechanism**: Extremely conservative. The ACC drives very slowly relative to flow, potentially acting as a moving bottleneck.
- **Single change**: ACC T_des=3.0, 4 vehicles
- **Expected effect**: reduced throughput; wave amplitude uncertain
- **Primary metric**: wave amplitude

---

## Theme 6: Ring Size Sensitivity

### H039: 40 vehicles / 400 m ring (same density as Sugiyama)
- **Prior**: 0.50
- **Mechanism**: Doubling the ring size at constant density allows more jamiton wavelengths. The wave characteristics should scale predictably but controllers face a longer propagation path [1, 2].
- **Single change**: n_vehicles=40, ring_length=400, 4 FS vehicles (10% penetration)
- **Expected effect**: wave amplitude similar to Sugiyama; controller effect may be diluted by longer ring
- **Primary metric**: wave amplitude

### H040: 40 vehicles / 400 m ring, 8 FS vehicles (20%)
- **Prior**: 0.60
- **Mechanism**: Same density, larger ring, same penetration as T04. Tests if FS effectiveness scales with ring size.
- **Single change**: n_vehicles=40, ring_length=400, 8 FS vehicles
- **Expected effect**: similar wave reduction to T04
- **Primary metric**: wave amplitude

### H041: 100 vehicles / 2000 m ring (highway scale)
- **Prior**: 0.45
- **Mechanism**: Moving toward realistic highway segment length. At 100 veh / 2000 m, density = 50 veh/km, equilibrium gap = 15 m. This is a different stability regime [29, 37].
- **Single change**: n_vehicles=100, ring_length=2000, 0 smart vehicles (baseline)
- **Expected effect**: wave may or may not form depending on density vs stability boundary
- **Primary metric**: wave amplitude

### H042: 100 vehicles / 1000 m ring (high density)
- **Prior**: 0.55
- **Mechanism**: Density = 100 veh/km. Very dense, deep in the unstable regime. Equilibrium gap = 5 m, similar to Sugiyama.
- **Single change**: n_vehicles=100, ring_length=1000, 0 smart vehicles
- **Expected effect**: strong wave formation; larger amplitude than Sugiyama due to more vehicles
- **Primary metric**: wave amplitude

### H043: 100 vehicles / 1000 m ring, 5 FS vehicles (5%)
- **Prior**: 0.40
- **Mechanism**: 5% penetration on a large dense ring. Tests the Stern result at scale.
- **Single change**: 100 vehicles, 1000 m, 5 FS vehicles
- **Expected effect**: partial wave suppression
- **Primary metric**: wave amplitude

### H044: 200 vehicles / 4000 m ring (same density)
- **Prior**: 0.40
- **Mechanism**: Very large ring at Sugiyama density. Multiple jamitons may coexist. Tests if wave suppression scales to multi-jamiton regimes [26, 27].
- **Single change**: n_vehicles=200, ring_length=4000, 10 FS vehicles (5%)
- **Expected effect**: partial wave suppression at 5%
- **Primary metric**: wave amplitude

---

## Theme 7: Human Driver Model Perturbation

### H045: IDM T = 0.7 s (more unstable)
- **Prior**: 0.70
- **Mechanism**: Lower time headway makes the IDM more string-unstable. The wave should grow faster and with higher amplitude [29, 37].
- **Single change**: idm_T=0.7 (default 1.0), all-IDM baseline
- **Expected effect**: +1 to +3 m/s wave amplitude
- **Primary metric**: wave amplitude

### H046: IDM T = 1.2 s (more stable)
- **Prior**: 0.55
- **Mechanism**: Higher time headway moves the system toward the stability boundary. The wave should be weaker or absent [29].
- **Single change**: idm_T=1.2, all-IDM baseline
- **Expected effect**: -2 to -5 m/s wave amplitude
- **Primary metric**: wave amplitude

### H047: IDM T = 1.5 s (textbook value)
- **Prior**: 0.60
- **Mechanism**: The original Treiber value. At 22/230, the system should be linearly stable with T=1.5 but noise can still trigger transient waves [29].
- **Single change**: idm_T=1.5, all-IDM baseline
- **Expected effect**: wave amplitude < 3 m/s or absent
- **Primary metric**: wave amplitude

### H048: IDM T = 2.0 s (very stable)
- **Prior**: 0.70
- **Mechanism**: Well into the stable regime. No wave should form even with noise [29, 37].
- **Single change**: idm_T=2.0, all-IDM baseline
- **Expected effect**: wave amplitude < 1 m/s
- **Primary metric**: wave amplitude

### H049: IDM a = 0.73 m/s^2 (textbook highway value)
- **Prior**: 0.50
- **Mechanism**: Lower max acceleration means slower response. May change the stability boundary and wave shape [17, 29].
- **Single change**: idm_a=0.73 (default 1.3), all-IDM baseline
- **Expected effect**: different wave characteristics; uncertain direction
- **Primary metric**: wave amplitude

### H050: IDM a = 2.0 m/s^2 (aggressive drivers)
- **Prior**: 0.45
- **Mechanism**: Higher acceleration means sharper response, potentially more oscillatory [17].
- **Single change**: idm_a=2.0, all-IDM baseline
- **Expected effect**: may increase or decrease amplitude depending on stability diagram
- **Primary metric**: wave amplitude

### H051: IDM b = 1.0 m/s^2 (gentle braking)
- **Prior**: 0.40
- **Mechanism**: Lower comfortable deceleration changes the desired gap s* calculation, making the interaction term (s*/s)^2 larger. May shift stability boundary [17].
- **Single change**: idm_b=1.0 (default 2.0), all-IDM baseline
- **Expected effect**: uncertain; different wave characteristics
- **Primary metric**: wave amplitude

### H052: IDM b = 3.0 m/s^2 (aggressive braking)
- **Prior**: 0.40
- **Mechanism**: Higher b means the driver tolerates closer gaps before increasing desired spacing. May change the wave speed [17].
- **Single change**: idm_b=3.0, all-IDM baseline
- **Expected effect**: different wave speed; uncertain amplitude
- **Primary metric**: wave amplitude

### H053: IDM s0 = 1.0 m (tighter jam gap)
- **Prior**: 0.40
- **Mechanism**: Smaller minimum gap means higher jam density. Changes the shape of the fundamental diagram at high density [17].
- **Single change**: idm_s0=1.0 (default 2.0), all-IDM baseline
- **Expected effect**: different wave characteristics; potentially higher amplitude
- **Primary metric**: wave amplitude

### H054: IDM s0 = 4.0 m (wider jam gap)
- **Prior**: 0.40
- **Mechanism**: Larger minimum gap reduces jam density and may shift the stability boundary [17].
- **Single change**: idm_s0=4.0, all-IDM baseline
- **Expected effect**: different equilibrium speed; uncertain amplitude
- **Primary metric**: wave amplitude

---

## Theme 8: Noise Level Sweep

### H055: noise_std = 0.0 m/s^2 (no noise)
- **Prior**: 0.50
- **Mechanism**: Without noise, the system is deterministic. With T=1.0 the system is at the stability boundary. The single perturbation at t=5 should seed a wave but without noise to sustain it, the wave may decay [29, 210].
- **Single change**: noise_std=0.0 (default 0.3), all-IDM baseline
- **Expected effect**: wave amplitude may be lower (perturbation-seeded only)
- **Primary metric**: wave amplitude

### H056: noise_std = 0.1 m/s^2
- **Prior**: 0.50
- **Mechanism**: Low noise. The wave should still form (system is at stability boundary + perturbation) but may be weaker.
- **Single change**: noise_std=0.1
- **Expected effect**: slightly lower wave amplitude than baseline
- **Primary metric**: wave amplitude

### H057: noise_std = 0.5 m/s^2
- **Prior**: 0.60
- **Mechanism**: Higher noise drives the system deeper into the unstable regime. Stronger wave formation expected [210].
- **Single change**: noise_std=0.5
- **Expected effect**: +0.5 to +2 m/s wave amplitude
- **Primary metric**: wave amplitude

### H058: noise_std = 0.8 m/s^2
- **Prior**: 0.65
- **Mechanism**: High noise. Multiple waves may coexist. The wave structure may become more complex.
- **Single change**: noise_std=0.8
- **Expected effect**: +1 to +3 m/s wave amplitude; possibly multiple waves
- **Primary metric**: wave amplitude

### H059: noise_std = 1.0 m/s^2
- **Prior**: 0.55
- **Mechanism**: Very high noise. At this level, noise may dominate the IDM dynamics and the wave structure may be washed out into pure randomness rather than a coherent wave.
- **Single change**: noise_std=1.0
- **Expected effect**: uncertain; may increase or saturate wave amplitude
- **Primary metric**: wave amplitude

### H060: noise_std = 0.3, FS at 18.2%, noise robustness check
- **Prior**: 0.55
- **Mechanism**: Same as T04 but now we also test with noise_std=0.5 to see if FollowerStopper effectiveness degrades with higher noise.
- **Single change**: noise_std=0.5, 4 FS vehicles (compare to T04 which used noise_std=0.3)
- **Expected effect**: wave_amp higher than T04 (4.44); controller partially overwhelmed
- **Primary metric**: wave amplitude

### H061: noise_std = 0.8, FS at 18.2%, noise robustness check
- **Prior**: 0.40
- **Mechanism**: High noise stress-test of FollowerStopper at 18.2%.
- **Single change**: noise_std=0.8, 4 FS vehicles
- **Expected effect**: wave_amp higher than H060
- **Primary metric**: wave amplitude

---

## Theme 9: Initial Perturbation

### H062: No explicit perturbation (perturb_decel = 0)
- **Prior**: 0.55
- **Mechanism**: With noise_std=0.3, the wave should still emerge spontaneously from accumulated noise even without the initial brake pulse. Tests how much the perturbation accelerates wave formation [1].
- **Single change**: perturb_decel=0.0 (default -5.0)
- **Expected effect**: wave still forms but may take longer; same steady-state amplitude
- **Primary metric**: wave amplitude

### H063: Strong perturbation (perturb_decel = -9.0)
- **Prior**: 0.40
- **Mechanism**: Maximum braking pulse. Should seed a stronger initial wave, but steady-state amplitude may be the same (the attractor is the jamiton, independent of initial condition) [26].
- **Single change**: perturb_decel=-9.0
- **Expected effect**: same steady-state wave amplitude (jamiton attractor)
- **Primary metric**: wave amplitude

### H064: Weak perturbation (perturb_decel = -1.0)
- **Prior**: 0.50
- **Mechanism**: Mild braking. The wave should still form if the system is truly unstable, just may take longer.
- **Single change**: perturb_decel=-1.0
- **Expected effect**: same steady-state wave amplitude
- **Primary metric**: wave amplitude

### H065: Late perturbation (perturb_time = 50 s)
- **Prior**: 0.45
- **Mechanism**: Delaying the perturbation gives the system more time in uniform flow before the wave is seeded. With noise, the wave may have already started forming.
- **Single change**: perturb_time=50.0 (default 5.0)
- **Expected effect**: same steady-state amplitude
- **Primary metric**: wave amplitude

---

## Theme 10: Smart Vehicle Placement

### H066: Clustered placement (4 FS, all adjacent)
- **Prior**: 0.30
- **Mechanism**: Clustering all AVs in one platoon leaves 18 consecutive humans uncontrolled. The 18-vehicle human chain is deep in the unstable regime. Chou [12] predicts this is suboptimal.
- **Single change**: 4 FS at indices [0,1,2,3] instead of equally spaced
- **Expected effect**: wave_amp higher than T04 (4.44); clustering hurts
- **Primary metric**: wave amplitude

### H067: Two clusters of 2 (4 FS, paired)
- **Prior**: 0.40
- **Mechanism**: Two pairs of adjacent AVs, separated by 11 humans each. Intermediate between clustered and equally spaced.
- **Single change**: 4 FS at indices [0,1,11,12]
- **Expected effect**: wave_amp between T04 and H066
- **Primary metric**: wave amplitude

### H068: Random placement seed=0 (4 FS)
- **Prior**: 0.40
- **Mechanism**: Random placement. Tests sensitivity to AV distribution [12].
- **Single change**: 4 FS at random positions (drawn with seed=0)
- **Expected effect**: wave_amp near T04 +/- 1 m/s
- **Primary metric**: wave amplitude

### H069: Random placement seed=1 (4 FS)
- **Prior**: 0.40
- **Mechanism**: Different random placement. Provides a second sample.
- **Single change**: 4 FS at random positions (drawn with seed=1)
- **Expected effect**: wave_amp near T04 +/- 1 m/s
- **Primary metric**: wave amplitude

### H070: Random placement seed=2 (4 FS)
- **Prior**: 0.40
- **Mechanism**: Third random placement sample.
- **Single change**: 4 FS at random positions (drawn with seed=2)
- **Expected effect**: wave_amp near T04 +/- 1 m/s
- **Primary metric**: wave amplitude

---

## Theme 11: Desired Speed Spread (Heterogeneity)

### H071: Heterogeneous v0 (uniform 25-35 m/s)
- **Prior**: 0.45
- **Mechanism**: Drivers with different desired speeds create intrinsic speed differences that may seed additional disturbances or change the stability regime [38, 127].
- **Single change**: Each human's idm_v0 drawn from U(25, 35) instead of fixed 30
- **Expected effect**: potentially higher wave amplitude due to heterogeneity
- **Primary metric**: wave amplitude

### H072: Heterogeneous v0 (uniform 20-40 m/s, wider spread)
- **Prior**: 0.50
- **Mechanism**: Larger spread in desired speeds. More heterogeneity = more disturbance sources.
- **Single change**: Each human's idm_v0 drawn from U(20, 40)
- **Expected effect**: higher wave amplitude than H071
- **Primary metric**: wave amplitude

### H073: Heterogeneous v0 with FS at 18.2%
- **Prior**: 0.45
- **Mechanism**: Tests if FollowerStopper still works when human drivers are heterogeneous. The FS controller has a single v_des; it may not adapt well to varied leader speeds.
- **Single change**: Heterogeneous v0 U(25,35) + 4 FS vehicles
- **Expected effect**: wave_amp higher than T04 but still reduced from heterogeneous baseline
- **Primary metric**: wave amplitude

---

## Theme 12: Multi-Objective Trade-off

### H074: FS at 18.2%, optimise for fuel (compare fuel vs wave_amp)
- **Prior**: 0.55
- **Mechanism**: Same as T04 but evaluating the fuel metric as primary. The fuel proxy should decrease when the wave is suppressed because acceleration variance decreases [4, 103].
- **Single change**: T04 reanalysis with fuel as primary
- **Expected effect**: fuel reduction from 130.65 to ~120 mL/km
- **Primary metric**: fuel

### H075: ACC at 18.2%, optimise for throughput
- **Prior**: 0.55
- **Mechanism**: Same as T08 but evaluating throughput as primary. ACC's time-headway policy may affect throughput differently than FS.
- **Single change**: T08 reanalysis with throughput as primary
- **Expected effect**: throughput near baseline (~1000 veh/hr) with wave suppression
- **Primary metric**: throughput

### H076: FS at 18.2% with k_v=0.3 (fuel-optimised gain)
- **Prior**: 0.40
- **Mechanism**: Lower gain produces smoother acceleration profiles, which directly reduces the fuel proxy's positive-acceleration penalty term [103].
- **Single change**: FS k_v=0.3, 4 vehicles at 18.2%
- **Expected effect**: fuel improvement over T04; wave_amp may be slightly worse
- **Primary metric**: fuel

### H077: FS at 27.3%, fuel vs wave trade-off
- **Prior**: 0.55
- **Mechanism**: Higher penetration should further reduce both wave amplitude and fuel consumption.
- **Single change**: 6 FS vehicles at 27.3%
- **Expected effect**: fuel < 115 mL/km; wave_amp < 3 m/s
- **Primary metric**: fuel

---

## Theme 13: Run Length Sensitivity

### H078: t_max = 300 s (half duration)
- **Prior**: 0.55
- **Mechanism**: Shorter run. The wave should be fully developed by 200 s, so 300 s captures the steady state with a shorter measurement window. Tests if 600 s is necessary.
- **Single change**: t_max=300 (default 600), all-IDM baseline
- **Expected effect**: similar wave amplitude but higher variance (shorter window)
- **Primary metric**: wave amplitude

### H079: t_max = 1200 s (double duration)
- **Prior**: 0.55
- **Mechanism**: Longer run allows more wave cycles in the measurement window, reducing statistical noise. May reveal slow drift.
- **Single change**: t_max=1200
- **Expected effect**: similar wave amplitude, lower variance
- **Primary metric**: wave amplitude

### H080: t_max = 300 s with FS at 18.2%
- **Prior**: 0.50
- **Mechanism**: Tests if FS effectiveness is fully captured in 300 s. The controller may need more time to fully suppress the wave.
- **Single change**: t_max=300, 4 FS vehicles
- **Expected effect**: wave_amp potentially higher than T04 (incomplete suppression)
- **Primary metric**: wave amplitude

---

## Theme 14: dt Sensitivity

### H081: dt = 0.05 s (finer integration)
- **Prior**: 0.40
- **Mechanism**: Halving the timestep doubles computational cost but improves Euler accuracy. The baseline wave amplitude should be similar if 0.1 s is stable [29].
- **Single change**: dt=0.05 (default 0.1), all-IDM baseline
- **Expected effect**: wave_amp within noise floor of baseline (validates dt=0.1)
- **Primary metric**: wave amplitude

### H082: dt = 0.2 s (coarser integration)
- **Prior**: 0.35
- **Mechanism**: Doubling the timestep reduces cost but may introduce integration error. If wave_amp changes significantly, dt=0.1 is necessary.
- **Single change**: dt=0.2
- **Expected effect**: wave_amp similar to baseline if 0.2 s is still stable
- **Primary metric**: wave amplitude

### H083: dt = 0.05 s with FS at 18.2%
- **Prior**: 0.40
- **Mechanism**: Tests if FS results are sensitive to integration timestep.
- **Single change**: dt=0.05, 4 FS vehicles
- **Expected effect**: wave_amp similar to T04 (validates dt robustness)
- **Primary metric**: wave amplitude

---

## Theme 15: Cross-Controller at Different Penetrations

### H084: ACC at 9.1% (2/22)
- **Prior**: 0.45
- **Mechanism**: ACC showed dramatic improvement at 18.2% (T08: 0.55 m/s). Testing at 9.1% probes the transition region.
- **Single change**: 2 ACC vehicles, equally spaced
- **Expected effect**: wave_amp between baseline and T08 (0.55-8.17 m/s)
- **Primary metric**: wave amplitude

### H085: ACC at 27.3% (6/22)
- **Prior**: 0.70
- **Mechanism**: Higher ACC penetration. Given the dramatic effect at 18.2%, 27.3% should push wave amplitude even lower.
- **Single change**: 6 ACC vehicles, equally spaced
- **Expected effect**: wave_amp < 0.5 m/s
- **Primary metric**: wave amplitude

### H086: FS at 9.1% (2/22)
- **Prior**: 0.40
- **Mechanism**: FollowerStopper at intermediate penetration. Interpolates between T03 (8.28) and T04 (4.44).
- **Single change**: 2 FS vehicles, equally spaced
- **Expected effect**: wave_amp ~ 5-7 m/s
- **Primary metric**: wave amplitude

### H087: ACC at 50% (11/22)
- **Prior**: 0.85
- **Mechanism**: Half the vehicles are ACC. Should nearly suppress the wave given 18.2% already achieved 0.55 m/s.
- **Single change**: 11 ACC vehicles, equally spaced
- **Expected effect**: wave_amp < 0.3 m/s
- **Primary metric**: wave amplitude

---

## Theme 16: ACC Gain Tuning

### H088: ACC k1 = 0.1 (lower gap-error gain)
- **Prior**: 0.40
- **Mechanism**: Weaker gap tracking. The ACC responds more slowly to gap deviations, which may reduce oscillation but slow wave suppression [40].
- **Single change**: ACC k1=0.1 (default 0.3), 4 vehicles at 18.2%
- **Expected effect**: wave_amp possibly slightly higher than T08
- **Primary metric**: wave amplitude

### H089: ACC k1 = 0.6 (higher gap-error gain)
- **Prior**: 0.40
- **Mechanism**: Stronger gap tracking. May improve or worsen depending on oscillation risk.
- **Single change**: ACC k1=0.6, 4 vehicles
- **Expected effect**: uncertain; may cause ACC oscillation
- **Primary metric**: wave amplitude

### H090: ACC k2 = 0.2 (lower speed-difference gain)
- **Prior**: 0.35
- **Mechanism**: Weaker relative-velocity damping. This term is crucial for string stability; reducing it may make ACC string-unstable [40, 88].
- **Single change**: ACC k2=0.2 (default 0.5), 4 vehicles
- **Expected effect**: wave_amp higher than T08 due to reduced damping
- **Primary metric**: wave amplitude

### H091: ACC k2 = 1.0 (higher speed-difference gain)
- **Prior**: 0.50
- **Mechanism**: Stronger damping of relative velocity. Should improve string stability and wave suppression.
- **Single change**: ACC k2=1.0, 4 vehicles
- **Expected effect**: wave_amp similar to or lower than T08
- **Primary metric**: wave amplitude

---

## Theme 17: FollowerStopper Tuning at Low Penetration

### H092: FS v_des=8.0, 1 vehicle at 4.5%
- **Prior**: 0.35
- **Mechanism**: Lowering v_des to near-equilibrium at low penetration. Tests if the FS's poor T03 result (8.28 m/s, slightly worse than baseline) can be improved by tuning.
- **Single change**: FS v_des=8.0, 1 vehicle
- **Expected effect**: wave_amp lower than T03
- **Primary metric**: wave amplitude

### H093: FS s_st=2.0, s_go=15.0, 1 vehicle at 4.5%
- **Prior**: 0.35
- **Mechanism**: Tighter gap thresholds tailored to the ring's ~5-10 m gap range. Default s_go=35 is too large for the ring; most of the operating range falls below s_st.
- **Single change**: FS s_st=2.0, s_go=15.0, 1 vehicle
- **Expected effect**: wave_amp lower than T03 by 1-3 m/s
- **Primary metric**: wave amplitude

### H094: FS tuned for ring: v_des=6.0, s_st=2.0, s_go=12.0, k_v=0.8
- **Prior**: 0.45
- **Mechanism**: Comprehensive re-tuning of FS for the Sugiyama ring. Matching the gap range and equilibrium speed of the ring environment rather than using freeway defaults [5, 217].
- **Single change**: FS with ring-tuned params, 1 vehicle at 4.5%
- **Expected effect**: significant improvement over T03; wave_amp < 6 m/s
- **Primary metric**: wave amplitude

### H095: FS tuned for ring, 4 vehicles at 18.2%
- **Prior**: 0.60
- **Mechanism**: Same ring-tuned FS at higher penetration. Should combine tuning benefit with penetration benefit.
- **Single change**: FS ring-tuned, 4 vehicles
- **Expected effect**: wave_amp < 2 m/s (better than T04's 4.44)
- **Primary metric**: wave amplitude

---

## Theme 18: Interaction Between Noise and Controller Penetration

### H096: noise_std=0.0, FS at 4.5%
- **Prior**: 0.45
- **Mechanism**: Without noise, the wave is seeded only by the perturbation. Tests if FS is effective against a purely perturbation-seeded wave.
- **Single change**: noise_std=0.0, 1 FS vehicle
- **Expected effect**: wave may be weaker; FS may fully suppress the perturbation-only wave
- **Primary metric**: wave amplitude

### H097: noise_std=0.0, no perturbation (perturb_decel=0)
- **Prior**: 0.60
- **Mechanism**: Zero noise plus zero perturbation. The system should remain in uniform flow indefinitely (if truly at equilibrium with initial conditions).
- **Single change**: noise_std=0.0, perturb_decel=0.0
- **Expected effect**: wave_amp < 0.5 m/s (near-zero; only initial velocity spread)
- **Primary metric**: wave amplitude

### H098: noise_std=0.5, ACC at 18.2%
- **Prior**: 0.45
- **Mechanism**: Higher noise stress-tests ACC. The ACC showed excellent performance at 18.2% with standard noise (T08: 0.55 m/s). Does it degrade with more noise?
- **Single change**: noise_std=0.5, 4 ACC vehicles
- **Expected effect**: wave_amp somewhat higher than T08
- **Primary metric**: wave amplitude

---

## Theme 19: Density Variation at Fixed Ring Length

### H099: 18 vehicles / 230 m (below Sugiyama threshold)
- **Prior**: 0.60
- **Mechanism**: Below the critical density of 22 vehicles [1]. The system should be stable with no wave formation.
- **Single change**: n_vehicles=18 (default 22)
- **Expected effect**: wave_amp < 2 m/s (stable or weakly unstable)
- **Primary metric**: wave amplitude

### H100: 20 vehicles / 230 m (near threshold)
- **Prior**: 0.50
- **Mechanism**: Just below the Sugiyama threshold. The system is marginally stable; noise may trigger transient waves.
- **Single change**: n_vehicles=20
- **Expected effect**: wave_amp 2-5 m/s (reduced from baseline)
- **Primary metric**: wave amplitude

### H101: 25 vehicles / 230 m (above threshold)
- **Prior**: 0.60
- **Mechanism**: Above the Sugiyama threshold. Higher density should produce a stronger wave with a different equilibrium speed [1, 2].
- **Single change**: n_vehicles=25
- **Expected effect**: wave_amp > 8 m/s; lower equilibrium speed
- **Primary metric**: wave amplitude

### H102: 30 vehicles / 230 m (very dense)
- **Prior**: 0.65
- **Mechanism**: Very high density. Equilibrium gap = 230/30 - 5 = 2.67 m. Deep in the stop-and-go regime.
- **Single change**: n_vehicles=30
- **Expected effect**: large wave amplitude; very low mean speed
- **Primary metric**: wave amplitude

### H103: 25 veh / 230 m, FS at 20% (5/25)
- **Prior**: 0.50
- **Mechanism**: Tests FS at above-threshold density. The wave is stronger; does the same penetration still help?
- **Single change**: n_vehicles=25, 5 FS vehicles
- **Expected effect**: partial wave suppression
- **Primary metric**: wave amplitude

---

## Theme 20: Mixed Controller Strategies

### H104: 2 FS + 2 ACC at 18.2% (mixed AV fleet)
- **Prior**: 0.50
- **Mechanism**: Combining two different controllers. FS excels at wave absorption; ACC at maintaining stable headway. Together they may complement each other.
- **Single change**: 2 FS + 2 ACC vehicles (indices [0,5] FS, [11,16] ACC)
- **Expected effect**: wave_amp between T04 and T08
- **Primary metric**: wave amplitude

### H105: 1 FS + 1 ACC at 9.1%
- **Prior**: 0.35
- **Mechanism**: Low-penetration mixed fleet. Tests if mixing controller types at low penetration is better than pure FS or pure ACC.
- **Single change**: 1 FS at index 0, 1 ACC at index 11
- **Expected effect**: wave_amp between T03/T07 and H086/H084
- **Primary metric**: wave amplitude

---

## Summary

| Theme | Hypotheses | IDs |
|---|---|---|
| 1. Penetration rate sweep (FS) | 8 | H001-H008 |
| 2. Controller family comparison | 8 | H009-H016 |
| 3. FollowerStopper gain tuning | 10 | H017-H026 |
| 4. PIWithSaturation gain tuning | 7 | H027-H033 |
| 5. ACC time headway sweep | 5 | H034-H038 |
| 6. Ring size sensitivity | 6 | H039-H044 |
| 7. Human driver model perturbation | 10 | H045-H054 |
| 8. Noise level sweep | 7 | H055-H061 |
| 9. Initial perturbation | 4 | H062-H065 |
| 10. Smart vehicle placement | 5 | H066-H070 |
| 11. Desired speed spread | 3 | H071-H073 |
| 12. Multi-objective trade-off | 4 | H074-H077 |
| 13. Run length sensitivity | 3 | H078-H080 |
| 14. dt sensitivity | 3 | H081-H083 |
| 15. Cross-controller penetrations | 4 | H084-H087 |
| 16. ACC gain tuning | 4 | H088-H091 |
| 17. FS tuning at low penetration | 4 | H092-H095 |
| 18. Noise x controller interaction | 3 | H096-H098 |
| 19. Density variation | 5 | H099-H103 |
| 20. Mixed controller strategies | 2 | H104-H105 |
| **Total** | **105** | H001-H105 |

---

*End of research queue.*
