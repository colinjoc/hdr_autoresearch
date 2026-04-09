# Design Variables for Robot Locomotion HDR Loop

This document defines the design variables that the HDR loop iterates on for robot locomotion policy optimization. Each variable includes its range, motivation from literature, and expected effect.

---

## 1. Reward Components and Weights

The reward function is a weighted sum of individual terms. Each weight is a continuous design variable.

### 1.1 Velocity Tracking Weight
- **Variable**: `w_vel_tracking` (float, 0.5 - 5.0)
- **Formula**: `r = w * exp(-c * ||v_cmd - v_actual||^2)`
- **Tracking coefficient c**: float, 1.0 - 10.0
- **Reference**: Rudin et al. (2022) use Gaussian kernel velocity tracking as primary reward
- **Effect**: Higher weight prioritizes velocity matching over other objectives. Too high causes aggressive, jerky locomotion; too low causes sluggish response.

### 1.2 Angular Velocity Tracking Weight
- **Variable**: `w_ang_vel_tracking` (float, 0.1 - 2.0)
- **Formula**: `r = w * exp(-c * (yaw_cmd - yaw_actual)^2)`
- **Reference**: MuJoCo Playground locomotion environments
- **Effect**: Controls yaw tracking precision. Essential for directional control.

### 1.3 Energy Penalty Weight
- **Variable**: `w_energy` (float, 0.0 - 0.1)
- **Formula**: `r = -w * sum(|tau_i * dq_i|)` (mechanical power)
- **Reference**: Energy-efficient locomotion overview (2018); Adaptive Energy Regularization (ICRA 2025)
- **Effect**: Reduces energy consumption and Cost of Transport. Too high prevents dynamic behaviors; too low leads to inefficient gaits. Can save 7-21% energy when properly tuned.

### 1.4 Torque Penalty Weight
- **Variable**: `w_torque` (float, 0.0 - 0.01)
- **Formula**: `r = -w * sum(tau_i^2)`
- **Reference**: Ha et al. (2025) survey; standard in legged_gym
- **Effect**: Reduces joint stress and motor wear. Encourages efficient force usage.

### 1.5 Action Rate Penalty Weight
- **Variable**: `w_action_rate` (float, 0.0 - 0.5)
- **Formula**: `r = -w * sum((a_t - a_{t-1})^2)`
- **Reference**: Chen et al. (2024) Lipschitz-constrained policies
- **Effect**: Smooths action trajectories, reducing jitter. Critical for sim-to-real transfer. Too high causes sluggish response.

### 1.6 Joint Acceleration Penalty Weight
- **Variable**: `w_joint_accel` (float, 0.0 - 0.001)
- **Formula**: `r = -w * sum(ddq_i^2)`
- **Reference**: Ha et al. (2025); legged_gym default configuration
- **Effect**: Prevents abrupt joint movements. Reduces mechanical stress.

### 1.7 Feet Airtime Reward Weight
- **Variable**: `w_feet_airtime` (float, 0.0 - 2.0)
- **Minimum airtime threshold**: float, 0.1 - 0.4 seconds
- **Reference**: MuJoCo Playground; Rudin et al. (2022)
- **Effect**: Encourages proper foot lifting, prevents shuffling gaits. Threshold sets minimum swing duration.

### 1.8 Foot Clearance Reward Weight
- **Variable**: `w_foot_clearance` (float, 0.0 - 1.0)
- **Target clearance height**: float, 0.03 - 0.10 meters
- **Reference**: Barrier-based style rewards (2024)
- **Effect**: Ensures feet clear the ground during swing, preventing stumbling on terrain.

### 1.9 Body Orientation Penalty Weight
- **Variable**: `w_orientation` (float, 0.0 - 1.0)
- **Formula**: `r = -w * (roll^2 + pitch^2)`
- **Reference**: Standard in most locomotion frameworks
- **Effect**: Keeps body upright. Essential for stability but shouldn't be so strong it prevents natural body motion.

### 1.10 Body Height Penalty Weight
- **Variable**: `w_height` (float, 0.0 - 0.5)
- **Target height**: float (robot-dependent)
- **Reference**: MuJoCo Playground; legged_gym configurations
- **Effect**: Maintains desired standing height. Prevents crouching or over-extension.

### 1.11 Standing Still Penalty Weight
- **Variable**: `w_stand_still` (float, 0.0 - 0.5)
- **Reference**: MuJoCo Playground
- **Effect**: Penalizes unnecessary joint motion when zero velocity commanded.

### 1.12 Termination Penalty
- **Variable**: `w_termination` (float, -5.0 to -50.0)
- **Reference**: Universal in locomotion RL; large negative reward on falling
- **Effect**: Discourages falling. Magnitude affects risk-taking behavior: too large causes overly conservative policies.

### 1.13 Collision Penalty Weight
- **Variable**: `w_collision` (float, 0.0 - 1.0)
- **Reference**: legged_gym; penalizes undesired body-ground contacts
- **Effect**: Prevents knee, body, or head contacts with ground.

### 1.14 Default Pose Penalty Weight
- **Variable**: `w_default_pose` (float, 0.0 - 0.5)
- **Reference**: Standard regularization in locomotion
- **Effect**: Biases policy toward nominal standing configuration. Prevents extreme joint configurations.

---

## 2. Observation Space Configuration

### 2.1 Observation Components
- **Variable**: subset selection from {joint_pos, joint_vel, base_ang_vel, gravity_vector, prev_action, commands, phase_variables, contact_states, base_lin_vel}
- **Reference**: Ha et al. (2025); MuJoCo Playground unified observation structure
- **Effect**: Minimal proprioception (joint_pos, joint_vel, gravity, ang_vel, prev_action) is the baseline. Adding contact states, phase variables, or base linear velocity can improve performance at the cost of observation complexity.

### 2.2 History Length
- **Variable**: `n_history_frames` (int, 1 - 20)
- **Reference**: Ha et al. (2025) recommend 5-10 timesteps; frame stacking vs RNN
- **Effect**: Longer history helps with partial observability (latency, terrain estimation) but increases input dimensionality.

### 2.3 History Encoding Method
- **Variable**: categorical {frame_stack, gru, lstm, tcn, transformer}
- **Reference**: Miki et al. (2022) use attention; Radosavovic et al. (2024) use causal transformer; Li et al. (2024) use dual-history RNN
- **Effect**: Frame stacking is simplest but high-dimensional. RNN/GRU is compact but harder to train. Transformer captures long-range dependencies.

### 2.4 Noise Levels on Observations
- **Variable**: `obs_noise_scale` (float, 0.0 - 0.5)
- **Components**: per-sensor noise (joint position noise, velocity noise, IMU noise)
- **Reference**: Domain randomization practice; legged_gym noise injection
- **Effect**: Higher noise during training improves real-world robustness but slows convergence.

### 2.5 Privileged Observations (Teacher)
- **Variable**: subset of {terrain_heightmap, friction_coefficients, body_mass, contact_forces, external_forces}
- **Reference**: Lee et al. (2020) teacher-student framework; standard practice
- **Effect**: Privileged information makes teacher learning easier; student must reconstruct from history.

---

## 3. Action Space Configuration

### 3.1 Action Type
- **Variable**: categorical {joint_position_absolute, joint_position_residual, joint_torque, task_space_foot_position}
- **Reference**: Ha et al. (2025) survey: PD position control dominates; torque control requires higher frequency
- **Effect**: Position control is most robust for sim-to-real. Torque control gives finer force control. Residual actions constrain policy near default pose.

### 3.2 Action Scale
- **Variable**: `action_scale` (float, 0.1 - 1.0)
- **Formula**: `q_desired = q_default + action_scale * a_t` (for residual)
- **Reference**: MuJoCo Playground uses configurable k_a scaling factor
- **Effect**: Smaller scale constrains actions near default pose (safer, easier to learn). Larger scale enables more dynamic movements.

### 3.3 Policy Frequency
- **Variable**: `policy_freq_hz` (int, 20 - 200)
- **Reference**: 50Hz is standard for position control; 100-200Hz for torque control
- **Effect**: Higher frequency enables finer control but increases computational cost and can amplify noise.

### 3.4 Action Smoothing
- **Variable**: categorical {none, exponential_moving_average, low_pass_filter, lipschitz_constraint}
- **EMA coefficient**: float, 0.0 - 0.5
- **Reference**: Chen et al. (2024) Lipschitz constraints; standard EMA smoothing
- **Effect**: Reduces jitter at the cost of response speed. Lipschitz constraint is differentiable and doesn't require manual tuning.

### 3.5 PD Controller Gains
- **Variable**: `kp` (float, 20 - 100), `kd` (float, 0.5 - 5.0)
- **Reference**: Robot-specific but critical for transfer; legged_gym default configuration
- **Effect**: Higher kp gives stiffer position tracking (more responsive, more oscillation). Higher kd adds damping (smoother, slower). Variable stiffness (kp as policy output) is emerging.

---

## 4. Network Architecture

### 4.1 Hidden Layer Sizes
- **Variable**: list of ints, e.g., [256, 256], [512, 256, 128], [256, 128]
- **Reference**: Standard locomotion uses [256, 256] or [512, 256, 128]; Architecture Is All You Need (2025)
- **Effect**: Wider/deeper networks have more capacity but risk overfitting and longer training. Diminishing returns beyond ~512 width.

### 4.2 Number of Hidden Layers
- **Variable**: int, 2 - 4
- **Reference**: Most locomotion policies use 2-3 layers; RLBenchNet (2025)
- **Effect**: Deeper networks can learn more complex behaviors but are harder to train.

### 4.3 Activation Function
- **Variable**: categorical {elu, relu, tanh, silu}
- **Reference**: ELU is standard in legged_gym/RSL; Architecture sweet spots (2025)
- **Effect**: ELU provides smooth gradients including for negative inputs. ReLU is simpler but has dead neuron problem. Tanh naturally bounds outputs.

### 4.4 Separate vs Shared Actor-Critic
- **Variable**: boolean
- **Reference**: Most locomotion uses separate networks; shared trunk reduces parameters
- **Effect**: Separate networks allow different representational needs. Shared trunk is more parameter-efficient.

### 4.5 Value Network Architecture
- **Variable**: independent architecture specification (may differ from policy)
- **Reference**: Value networks often benefit from being larger than policy networks
- **Effect**: Value function accuracy affects GAE quality; larger value network may improve training stability.

---

## 5. Training Configuration (PPO Hyperparameters)

### 5.1 Clip Ratio
- **Variable**: `clip_ratio` (float, 0.1 - 0.4)
- **Reference**: Schulman et al. (2017) default 0.2; 37 Implementation Details (2022)
- **Effect**: Controls maximum policy update magnitude. Smaller = more conservative updates, more stable but slower. PPO implementation details paper shows clip ratio can determine task success/failure.

### 5.2 Entropy Coefficient
- **Variable**: `entropy_coef` (float, 0.0 - 0.05)
- **Reference**: Eimer et al. (2023) hyperparameter study; standard PPO
- **Effect**: Encourages exploration by penalizing deterministic policies. Critical early in training; may need annealing.

### 5.3 Learning Rate
- **Variable**: `lr` (float, 1e-5 - 1e-3)
- **Schedule**: categorical {constant, linear_decay, cosine_decay}
- **Reference**: PPO for locomotion typically uses 3e-4; Eimer et al. (2023)
- **Effect**: Foundational hyperparameter. Too high causes instability; too low causes slow convergence. Schedule can improve final performance.

### 5.4 GAE Lambda
- **Variable**: `gae_lambda` (float, 0.9 - 0.99)
- **Reference**: Schulman et al. (2015); 0.95 is default for locomotion
- **Effect**: Controls bias-variance tradeoff in advantage estimation. Higher = lower bias, higher variance.

### 5.5 Discount Factor (Gamma)
- **Variable**: `gamma` (float, 0.95 - 0.999)
- **Reference**: Standard RL; 0.99 is typical for locomotion
- **Effect**: Higher gamma values weight future rewards more. Important for long-horizon locomotion behaviors.

### 5.6 Number of Minibatch Epochs
- **Variable**: `n_epochs` (int, 2 - 8)
- **Reference**: PPO implementation details; typically 3-5 for locomotion
- **Effect**: More epochs per batch improve sample efficiency but risk overfitting to current batch.

### 5.7 Number of Parallel Environments
- **Variable**: `n_envs` (int, 1024 - 16384)
- **Reference**: Rudin et al. (2022) use 4096; scaling to 1M shows benefits (2026)
- **Effect**: More environments improve training stability and final performance. GPU memory limits maximum count. 4096 is standard for consumer GPUs.

### 5.8 Rollout Length
- **Variable**: `n_steps` (int, 8 - 64)
- **Reference**: Standard PPO; legged_gym uses 24 steps
- **Effect**: Longer rollouts reduce bias but increase memory usage. batch_size = n_envs * n_steps.

### 5.9 Minibatch Size
- **Variable**: `minibatch_size` (int, fraction of total batch)
- **Reference**: Standard PPO implementation
- **Effect**: Smaller minibatches provide noisier but cheaper gradient estimates.

---

## 6. Domain Randomization Parameters

### 6.1 Friction Range
- **Variable**: `friction_range` (tuple, e.g., [0.3, 2.0])
- **Reference**: Evaluating DR in DRL Locomotion (2023); legged_gym defaults
- **Effect**: Wide friction range enables transfer across surfaces. Too wide makes learning impossible.

### 6.2 Base Mass Perturbation
- **Variable**: `mass_range` (tuple, e.g., [-20%, +30%])
- **Reference**: Domain randomization practice; simulates payload variation
- **Effect**: Robustness to mass variation is essential for real-world deployment with varying payloads.

### 6.3 Motor Strength Scaling
- **Variable**: `motor_strength_range` (tuple, e.g., [0.8, 1.2])
- **Reference**: Peng et al. (2018) dynamics randomization
- **Effect**: Accounts for motor-to-motor variation and degradation over time.

### 6.4 PD Gain Perturbation
- **Variable**: `kp_range`, `kd_range` (tuples, +/- 10-30%)
- **Reference**: legged_gym configuration; SysID uncertainty
- **Effect**: Robustness to controller parameter uncertainty.

### 6.5 Joint Calibration Offset
- **Variable**: `joint_offset_range` (float, 0.0 - 0.05 rad)
- **Reference**: MuJoCo Playground DR settings
- **Effect**: Simulates encoder calibration errors that exist on real robots.

### 6.6 Link CoM Offset
- **Variable**: `com_offset_range` (float, 0.0 - 0.05 m)
- **Reference**: MuJoCo Playground DR settings
- **Effect**: Accounts for manufacturing tolerances in body construction.

### 6.7 Action Delay
- **Variable**: `action_delay_range` (int, 0 - 40 ms)
- **Reference**: Standard practice; communication latency simulation
- **Effect**: Robustness to variable communication delays in real deployment.

### 6.8 External Push Force
- **Variable**: `push_force_range` (float, 0 - 50 N), `push_interval` (float, 5-15 seconds)
- **Reference**: HiFAR (2025); standard robustness training
- **Effect**: Trains recovery from external disturbances. Essential for deployment robustness.

### 6.9 Sensor Noise
- **Variable**: `joint_pos_noise` (float, 0.0 - 0.03 rad), `joint_vel_noise` (float, 0.0 - 1.5 rad/s), `imu_noise` (float, 0.0 - 0.1 rad/s)
- **Reference**: legged_gym default noise configuration
- **Effect**: Simulates real sensor noise characteristics.

### 6.10 Curriculum on DR
- **Variable**: `dr_curriculum_enabled` (boolean), `dr_ramp_schedule` (linear/exponential)
- **Reference**: TransCurriculum (2026); curriculum domain randomization
- **Effect**: Starting with narrow ranges and expanding prevents early learning collapse.

---

## 7. Terrain and Curriculum

### 7.1 Terrain Types
- **Variable**: subset of {flat, rough, slopes, stairs_up, stairs_down, stepping_stones, gaps, mixed}
- **Reference**: Rudin et al. (2022); LP-ACRL (2025)
- **Effect**: Terrain diversity determines generalization. Progressive addition via curriculum improves training stability.

### 7.2 Terrain Difficulty Progression
- **Variable**: `terrain_curriculum_type` (categorical: {fixed, linear, adaptive/LP-ACRL})
- **Reference**: LP-ACRL (2025) for automatic; Rudin et al. (2022) for game-inspired
- **Effect**: Automatic curriculum removes need to manually design progression. Adaptive methods adjust based on agent capability.

### 7.3 Velocity Command Range
- **Variable**: `vx_range` (tuple, e.g., [-1.0, 2.0]), `vy_range` (tuple, e.g., [-0.5, 0.5]), `wz_range` (tuple, e.g., [-1.0, 1.0])
- **Reference**: Margolis et al. (2024) adaptive velocity curriculum
- **Effect**: Progressive expansion of command range prevents early collapse on extreme commands.

### 7.4 Command Curriculum
- **Variable**: `cmd_curriculum_enabled` (boolean), `cmd_ramp_schedule`
- **Reference**: Margolis et al. (2024) rapid locomotion
- **Effect**: Starting with easy commands and expanding enables learning of extreme velocities.

---

## 8. Morphology Parameters (if co-optimizing body)

### 8.1 Link Lengths
- **Variable**: per-link scaling factors (float, 0.7 - 1.3 of nominal)
- **Reference**: Cheney et al. (2018); morphological co-design literature
- **Effect**: Longer legs enable longer strides but reduce stability. Shorter legs improve stability but limit speed.

### 8.2 Link Masses
- **Variable**: per-link mass scaling (float, 0.7 - 1.3 of nominal)
- **Reference**: Morphological pretraining (2025)
- **Effect**: Mass distribution affects dynamics, stability, and energy efficiency.

### 8.3 Joint Range of Motion
- **Variable**: per-joint limits (float, 80-120% of nominal range)
- **Reference**: Standard morphology optimization
- **Effect**: Larger range enables more dynamic movements but may cause instability.

### 8.4 Foot Geometry
- **Variable**: foot radius (float, 0.01 - 0.05 m), foot shape
- **Reference**: Hardware-algorithm co-design literature
- **Effect**: Larger feet provide more stability but may impede terrain traversal.

### 8.5 Actuator Parameters
- **Variable**: max_torque (float), gear_ratio (float), motor_bandwidth (Hz)
- **Reference**: PACE SysID (2024); actuator modeling
- **Effect**: These define the physical capabilities envelope of the robot.

---

## Summary: HDR Variable Priority

| Priority | Category | Key Variables | # Continuous | # Categorical |
|----------|----------|---------------|-------------|---------------|
| 1 (Critical) | Reward weights | 14 weight terms | 14 | 0 |
| 2 (High) | Training config | PPO hyperparameters | 8 | 1 |
| 3 (High) | Domain randomization | 10 DR ranges | 20 | 2 |
| 4 (Medium) | Action space | scale, frequency, smoothing | 3 | 2 |
| 5 (Medium) | Network architecture | width, depth, activation | 3 | 2 |
| 6 (Medium) | Curriculum | terrain, velocity, DR schedules | 4 | 3 |
| 7 (Low) | Observation space | components, history length | 2 | 2 |
| 8 (Optional) | Morphology | link lengths, masses, joints | 10+ | 0 |

**Total design space**: ~60+ continuous variables, ~12 categorical choices. HDR should prioritize reward weights and training configuration in early iterations, then expand to domain randomization and curriculum as baseline performance stabilizes.
