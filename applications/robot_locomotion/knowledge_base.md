# Knowledge Base: Robot Locomotion Policy Optimization

Established results, known-good configurations, and calibrated expectations for GPU-accelerated locomotion training.

---

## 1. Algorithm Selection

### PPO Dominates On-Policy Locomotion Training

**What works**: PPO with GAE is the default algorithm for locomotion. It is used in virtually all published locomotion results from ETH RSL, MIT CSAIL, UC Berkeley, Google DeepMind, and NVIDIA.

**Why PPO wins**: When combined with 4096+ parallel environments on GPU, PPO's on-policy nature becomes an advantage rather than a liability. The massive parallelism provides enough diverse experience per batch to make each update informative. PPO runs ~16x faster than off-policy methods (DDPG/TD3/SAC) when comparing wall-clock time with optimized parallelism.

**Known limitations**: PPO can stagnate at extreme parallelism (>100K environments) -- the gradient signal-to-noise ratio degrades. Recent work (2026) identifies specific PPO stagnation modes and mitigation strategies.

**Off-policy alternatives**: FastSAC and FastTD3 (Seo et al., 2024) demonstrate that properly parallelized off-policy methods can train humanoid locomotion in 15 minutes on a single RTX 4090, potentially outpacing PPO for high-dimensional tasks. SAC achieves the best gait quality in direct comparisons; TD3 provides the smoothest training curves.

### Standard PPO Configuration for Locomotion

| Hyperparameter | Recommended Value | Source |
|---------------|------------------|--------|
| Clip ratio | 0.2 | Schulman et al. (2017) |
| Entropy coefficient | 0.005 - 0.01 | Eimer et al. (2023) |
| Learning rate | 3e-4 | Standard; with linear decay |
| GAE lambda | 0.95 | Schulman et al. (2015) |
| Discount gamma | 0.99 | Standard |
| Minibatch epochs | 5 | legged_gym default |
| Num environments | 4096 | Rudin et al. (2022) |
| Rollout length | 24 steps | legged_gym default |
| Batch size | 4096 * 24 = 98304 | Derived |

---

## 2. Reward Design: What Works

### Essential Reward Components

Based on analysis of all major locomotion frameworks (legged_gym, MuJoCo Playground, Isaac Lab, Walk These Ways), these reward terms are universal:

**Always include**:
1. Velocity tracking (Gaussian kernel): Primary task reward
2. Angular velocity tracking: For directional control
3. Action rate penalty: Critical for smoothness and transfer
4. Torque penalty: Reduces motor stress
5. Termination penalty: Discourages falling
6. Body orientation penalty: Keeps robot upright

**Usually include**:
7. Feet airtime reward: Prevents shuffling
8. Foot clearance reward: Terrain robustness
9. Energy penalty: Reduces CoT
10. Joint acceleration penalty: Smoothness

**Sometimes include**:
11. Default pose penalty: Regularizes toward nominal configuration
12. Standing still penalty: Prevents unnecessary motion at zero command
13. Collision penalty: Prevents body-ground contacts
14. Base height penalty: Maintains desired height

### Known Reward Formulations

**Exponential kernel (recommended)**: `r = exp(-c * ||error||^2)` provides bounded [0,1] rewards that are stable to optimize. This is the recommended approach for tracking rewards (Ha et al., 2025 survey).

**Quadratic penalty (common)**: `r = -w * ||error||^2` is unbounded and can dominate other reward terms if not carefully scaled.

**Barrier-based (emerging)**: Logarithmic barrier functions provide principled penalty growth near constraint boundaries.

### Known Failure Modes

- **Reward hacking**: Policies exploit reward function loopholes (driving in circles, vibrating, exploiting physics engine bugs)
- **Reward dominance**: One reward term with poor scaling overwhelms all others
- **Phase transitions**: Sudden policy collapse when a reward hack becomes more profitable than intended behavior
- **Shuffling gait**: Emerges when foot clearance/airtime aren't rewarded

---

## 3. Network Architecture: Known Good Configurations

### Standard Locomotion Policy Architecture

| Component | Configuration | Source |
|-----------|--------------|--------|
| Policy network | MLP [256, 256] or [512, 256, 128] | legged_gym; MuJoCo Playground |
| Value network | MLP [256, 256] or [512, 256, 128] | Same architecture or larger |
| Activation | ELU | RSL convention; smooth gradients |
| Output | Tanh (scaled by action_scale) | Bounds actions naturally |
| Initialization | Orthogonal | PPO implementation details |

### When to Use Larger Networks

- **Humanoid locomotion** (20+ DoF): [512, 256, 128] preferred
- **Multi-skill policies**: Larger networks encode more behaviors
- **Vision-based**: Separate CNN encoder + MLP policy head

### When to Use Smaller Networks

- **Simple quadruped flat terrain**: [128, 128] sufficient
- **Deployment on embedded hardware**: Smaller networks run faster
- **Efficiently learning small policies** (Dao et al., 2022): 64-128 units can suffice for basic locomotion

---

## 4. Observation Space: Standard Configuration

### Minimum Viable Observation (Proprioceptive)

For flat-terrain quadruped locomotion, the minimum observation that works:

| Component | Dimension | Notes |
|-----------|-----------|-------|
| Joint positions | 12 | Relative to default |
| Joint velocities | 12 | rad/s |
| Base angular velocity | 3 | From IMU |
| Gravity vector (body frame) | 3 | From IMU orientation |
| Velocity commands | 3 | vx, vy, wz |
| Previous action | 12 | For smooth transitions |
| **Total** | **45** | |

### Extended Observation (Terrain-Aware)

Add for rough terrain:

| Component | Dimension | Notes |
|-----------|-----------|-------|
| History (5 frames) | 5 * 45 = 225 | Frame stacking |
| OR GRU hidden state | 64-128 | Compact alternative |
| Heightmap (if teacher) | 121 (11x11) | Privileged information |

### Humanoid Observation (Additional)

| Component | Dimension | Notes |
|-----------|-----------|-------|
| Phase variables (sin/cos per foot) | 4 | For gait timing |
| Base linear velocity | 3 | If available |
| Contact states | 2-4 | Binary foot contacts |

---

## 5. Action Space: Standard Configuration

### Dominant Approach: Joint Position Residuals

```
q_desired = q_default + action_scale * policy_output
torque = kp * (q_desired - q_actual) - kd * dq
```

**Standard parameters**:
- `action_scale`: 0.25 - 0.5 (constrains actions near default pose)
- `kp`: Robot-specific (Go1: ~20, ANYmal: ~80, humanoid: 40-100)
- `kd`: ~0.5-2.0 (critical damping regime)
- Policy frequency: 50 Hz (20ms)
- Physics substeps: 4 (5ms physics timestep)

### Why Position Control Dominates

1. Natural action bounds from joint limits
2. PD controller absorbs high-frequency dynamics
3. Lower policy frequency reduces computation
4. Better sim-to-real transfer (PD controller is implemented on the real robot too)
5. Less susceptible to jitter than torque control

---

## 6. Domain Randomization: Calibrated Ranges

### Proven Ranges for Sim-to-Real Transfer

These ranges have been validated in published sim-to-real demonstrations:

| Parameter | Range | Robot(s) | Source |
|-----------|-------|----------|--------|
| Ground friction | [0.4, 1.5] | ANYmal, Go1 | Rudin et al. (2022) |
| Base mass | +/- 25% | Multiple | Standard practice |
| Motor strength | [0.8, 1.2] | Multiple | Peng et al. (2018) |
| PD gains (kp) | +/- 20% | ANYmal | legged_gym |
| Joint offset | +/- 0.03 rad | Multiple | MuJoCo Playground |
| Action delay | [0, 20ms] | Go1 | Walk These Ways |
| External push | [0, 30N] | ANYmal | legged_gym |
| Joint pos noise | 0.01 rad | Multiple | Standard |
| Joint vel noise | 1.0 rad/s | Multiple | Standard |
| IMU noise | 0.05 rad/s | Multiple | Standard |

### What Breaks If Ranges Are Too Wide

- Friction < 0.2: Policy cannot learn to walk (all feet slip)
- Mass > +50%: Policy collapses under weight
- Motor strength < 0.6: Robot cannot support its own weight
- Action delay > 60ms: Control loop becomes unstable

### What Breaks If Ranges Are Too Narrow

- Fixed friction = 1.0: Policy fails on any surface different from training
- No mass variation: Fails with any payload
- No noise: Overreliance on precise sensing that doesn't exist on real hardware

---

## 7. Training Times and Compute Requirements

### Expected Training Times on Single Consumer GPU (RTX 4090)

| Task | Environments | Training Time | Final Performance |
|------|-------------|---------------|-------------------|
| Quadruped flat terrain walking | 4096 | 2-5 minutes | Reliable walking |
| Quadruped rough terrain | 4096 | 15-30 minutes | Multi-terrain traversal |
| Quadruped high-speed running | 4096 | 20-40 minutes | 3+ m/s |
| Humanoid basic walking | 4096 | 30-60 minutes | Stable walking |
| Humanoid velocity tracking | 8192 | 45-90 minutes | Precise tracking |
| Humanoid rough terrain | 4096 | 60-120 minutes | Multi-terrain |

### Compute Scaling

- **2x RTX 4090**: ~1.5x speedup (communication overhead limits scaling)
- **8x H100**: ~3x speedup over 1x RTX 4090 (Playground benchmark)
- **A100 vs RTX 4090**: A100 ~1.3x faster for RL (more memory allows larger batches)

### Steps Per Second (MuJoCo Playground, A100)

- Acrobot: ~752,000 steps/s
- Cheetah: ~435,000 steps/s
- Humanoid: ~92,000 steps/s

---

## 8. Benchmark Performance: What Scores to Expect

### MuJoCo Gym Environments (Solved)

| Environment | Good Score | Excellent Score | SOTA |
|-------------|-----------|----------------|------|
| HalfCheetah-v3 | 4000 | 8000 | ~12000 |
| Ant-v3 | 3000 | 5000 | ~7000 |
| Humanoid-v3 | 2000 | 4000 | ~6000 |
| Walker2d-v3 | 2000 | 4000 | ~5500 |
| Hopper-v3 | 2000 | 3000 | ~3800 |

### Real-World Locomotion Benchmarks

| Task | Metric | Good | SOTA |
|------|--------|------|------|
| Quadruped flat walking | Forward velocity | 1.0 m/s | 3.9 m/s (Mini Cheetah) |
| Quadruped rough terrain | Success rate | 70% | 85-95% |
| Humanoid flat walking | Forward velocity | 0.5 m/s | 2.0+ m/s |
| Quadruped energy efficiency | CoT | 1.0 | 0.5 (animals ~0.3) |
| Humanoid energy efficiency | CoT | 1.5 | 0.7 (humans ~0.2) |
| Sim-to-real transfer | Zero-shot success | 50% | 95%+ |

---

## 9. What's Known NOT to Work

### Common Mistakes

1. **Training without action rate penalty**: Produces jittery policies that destroy motors on real hardware
2. **Using pure torque control at 50Hz**: Too slow for stable torque control; need 200Hz+ or use PD position control
3. **Fixed terrain difficulty**: Robots learn to exploit easy terrain patterns; need curriculum or randomization
4. **Symmetric reward for forward/backward**: Robots learn to walk backward (easier balance); asymmetric velocity reward needed
5. **No termination penalty**: Robots learn to fall intentionally to reset to favorable positions
6. **Reward scaling without normalization**: One large reward term dominates learning signal
7. **Training with single friction value**: Zero-shot transfer fails on any different surface
8. **Using RGB images directly as observations**: Too high-dimensional; need pretrained encoders or depth sensing
9. **Not clipping observations**: Large observation values (from velocity spikes during contact) destabilize training
10. **Ignoring action delay in simulation**: Major source of sim-to-real gap for consumer robots

### Methods That Don't Scale

- **Model-based RL through contacts**: Gradient explosion/vanishing over long contact sequences
- **Pure evolutionary strategies**: Orders of magnitude slower than gradient-based methods for neural network policies
- **Analytical inverse kinematics for all motions**: Cannot handle the diversity of behaviors needed for robust locomotion
- **Single-environment training**: Not feasible for deep RL locomotion (would take days/weeks)

---

## 10. Simulation Framework Recommendations

### For HDR on Single Consumer GPU

**Primary recommendation**: MuJoCo Playground (MJX backend)
- JAX-native, fast compilation, integrated RL training
- Extensive pre-built locomotion environments
- Train most tasks in minutes
- Active development by Google DeepMind
- pip install mujoco-playground

**Alternative**: MuJoCo Playground (MuJoCo Warp backend)
- 252x faster than MJX for locomotion tasks
- Requires NVIDIA GPU (Warp is NVIDIA-specific)
- Still maturing but dramatically faster

**For NVIDIA-specific workflows**: Isaac Lab
- More mature ecosystem for NVIDIA hardware
- Integration with NVIDIA Omniverse
- Slightly more complex setup

**Not recommended for single-GPU HDR**:
- Genesis: Impressive speed claims but rigid body differentiability still in progress
- Custom Brax: Now largely superseded by MuJoCo Playground which uses Brax's RL libraries
- Isaac Gym: Deprecated in favor of Isaac Lab

### Robot Models for HDR Experiments

**Start with (simplest)**:
- Unitree Go1/Go2 (12 DoF quadruped, well-validated)
- HalfCheetah (2D, fastest iteration)

**Intermediate**:
- ANYmal (12 DoF, extensive published baselines)
- Robotis OP3 (compact humanoid)

**Advanced**:
- Unitree H1/G1 (full humanoid, 20-29 DoF)
- Berkeley Humanoid (affordable, documented sim-to-real)
- Booster T1 (humanoid with dedicated framework)

---

## 11. Key Equations and Formulations

### PPO Clipped Surrogate Objective

```
L_CLIP = E[min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)]
where r_t = pi_theta(a|s) / pi_theta_old(a|s)
```

### GAE Advantage Estimation

```
A_t^GAE = sum_{l=0}^{inf} (gamma * lambda)^l * delta_{t+l}
delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
```

### PD Position Control

```
tau = kp * (q_desired - q_actual) - kd * dq_actual
q_desired = q_default + action_scale * pi(observation)
```

### Gaussian Kernel Reward (Velocity Tracking)

```
r_vel = exp(-c * ||v_commanded - v_actual||^2)
where c ~ 4.0 (tracking sharpness)
```

### Cost of Transport

```
CoT = P / (m * g * v)
where P = power, m = mass, g = gravity, v = velocity
```

---

## 12. Reproducibility Notes

### Seeds and Variance

- Locomotion RL results have high variance across random seeds (20-40% performance spread is normal)
- Always run 3-5 seeds minimum for any HDR comparison
- Report mean +/- standard deviation

### Evaluation Protocol

- Evaluate on held-out terrain configurations not seen during training
- Test with randomized initial conditions (not just standing still)
- Measure over 100+ episodes for stable statistics
- Track multiple metrics: velocity tracking error, energy consumption, survival rate, smoothness

### Timestep Sensitivity

- Results are sensitive to physics timestep (smaller = more accurate but slower)
- Standard: 5ms physics, 20ms policy (4 substeps)
- Always report timestep configuration for reproducibility
