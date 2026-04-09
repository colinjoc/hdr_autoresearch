# Research Queue: Robot Locomotion Policy Optimization

Hypotheses seeded from literature review, prioritized for HDR experimentation.

---

### Q1 -- Reward Weight Sensitivity Analysis [OPEN]
Impact: HIGH
Hypothesis: The velocity tracking reward weight and energy penalty weight interact non-linearly, and there exists a Pareto frontier between forward speed and energy efficiency that can be mapped by systematic HDR exploration.
Mechanism: High velocity tracking weight encourages aggressive acceleration at the expense of energy. Energy penalty dampens high-torque behaviors. The optimal ratio depends on the target task (speed vs endurance).
Reference: Adaptive Energy Regularization for Autonomous Gait Transition (ICRA 2025); shows 7-21% energy savings through proper gait-speed coupling.

### Q2 -- Action Rate Penalty as Transfer Proxy [OPEN]
Impact: HIGH
Hypothesis: Action rate penalty weight is the single most impactful reward term for sim-to-real transfer quality, and its optimal value can be predicted from the robot's actuator bandwidth.
Mechanism: High-frequency action oscillations that are rewarding in simulation cause motor damage and instability on real hardware. The action rate penalty must be large enough to suppress jitter but small enough to allow dynamic responses.
Reference: Chen et al. (2024) Lipschitz-Constrained Policies; shows jitter is the primary cause of sim-to-real degradation.

### Q3 -- PPO vs FastSAC for Consumer GPU Training [OPEN]
Impact: HIGH
Hypothesis: For a single RTX 4090/3090, FastSAC will outperform PPO in wall-clock time for humanoid locomotion (20+ DoF) but underperform for simpler quadruped tasks (12 DoF).
Mechanism: Off-policy methods become more efficient as state-action space grows because they reuse expensive experience. For simple tasks, PPO's massive parallelism advantage dominates.
Reference: Seo et al. (2024) Learning Sim-to-Real Humanoid Locomotion in 15 Minutes; PPO-TD3-SAC comparison (2023).

### Q4 -- Optimal Number of Parallel Environments [OPEN]
Impact: HIGH
Hypothesis: There is a non-monotonic relationship between number of parallel environments and final policy quality: performance improves from 1024 to 4096, plateaus from 4096 to 8192, and may degrade beyond 16384 due to PPO gradient estimation issues.
Mechanism: Too few environments underutilize GPU; too many reduce gradient signal-to-noise ratio per environment. PPO's on-policy updates become stale when batch statistics are dominated by parallel variation.
Reference: Preventing Learning Stagnation in PPO by Scaling to 1M Environments (2026); PPO batch size tradeoff analysis (ICLR 2026).

### Q5 -- Curriculum Domain Randomization vs Fixed Ranges [OPEN]
Impact: HIGH
Hypothesis: Curriculum domain randomization (starting narrow, expanding) will achieve 20-40% better sim-to-real transfer than fixed wide ranges, with the optimal expansion schedule being exponential rather than linear.
Mechanism: Fixed wide ranges cause the policy to hedge across all parameter values, producing conservative behavior. Curriculum allows the policy to first learn the core skill, then robustify.
Reference: TransCurriculum (2026); Evaluating DR in DRL Locomotion (2023).

### Q6 -- Foot Clearance vs Energy Tradeoff [OPEN]
Impact: MEDIUM
Hypothesis: Foot clearance reward of 5-8cm is optimal across quadruped platforms; below 3cm causes stumbling on rough terrain, above 10cm wastes energy with no robustness benefit.
Mechanism: Foot clearance creates a safety margin for terrain irregularities. Beyond a certain height, additional clearance adds energy cost without reducing stumble risk.
Reference: Barrier-based style rewards (2024); MuJoCo Playground foot clearance reward implementation.

### Q7 -- GAE Lambda Interaction with Contact Dynamics [OPEN]
Impact: MEDIUM
Hypothesis: Lower GAE lambda (0.92-0.95) will produce better policies for contact-rich locomotion than the standard 0.95-0.99, because contact dynamics introduce high-variance reward signals that need more bias correction.
Mechanism: Contact events (foot strikes, slips) create sudden reward changes. High lambda propagates these noisy signals through long horizons, destabilizing value function estimation.
Reference: Schulman et al. (2015) GAE; practical recommendation of 0.96-0.99 may not apply to contact-rich domains.

### Q8 -- Network Architecture Sweet Spot for Locomotion [OPEN]
Impact: MEDIUM
Hypothesis: [256, 256] MLP with ELU activation is near-optimal for quadruped locomotion, but humanoid locomotion benefits from [512, 256, 128] due to higher observation and action dimensionality.
Mechanism: Quadruped locomotion has ~48-dimensional observation and 12-dimensional action, well within [256, 256] capacity. Humanoid with 60+ observation and 20+ action dimensions requires more capacity.
Reference: Architecture Is All You Need (2025); standard locomotion architectures in literature.

### Q9 -- Phase Variables Improve Gait Regularity [OPEN]
Impact: MEDIUM
Hypothesis: Adding sin/cos phase variables for each leg to the observation space will reduce training time by 30% and improve gait regularity, even without explicit gait conditioning.
Mechanism: Phase variables provide a time-varying signal that helps the policy discover periodic locomotion patterns without having to learn temporal structure purely from observation history.
Reference: Gait-driven RL framework (2025); MuJoCo Playground humanoid environments include phase variables.

### Q10 -- Velocity Curriculum Eliminates Early Collapse [OPEN]
Impact: HIGH
Hypothesis: Starting with low-velocity commands (0-0.5 m/s) and progressively expanding to full range (0-3+ m/s) will prevent the early training collapse that occurs when policies are immediately asked to achieve high speeds.
Mechanism: High-speed commands at the start of training cause frequent falls, generating overwhelming termination penalties that dominate gradients and prevent learning basic balance.
Reference: Margolis et al. (2024) Rapid Locomotion; adaptive velocity curriculum was a key component.

### Q11 -- Teacher-Student vs End-to-End for Terrain Locomotion [OPEN]
Impact: MEDIUM
Hypothesis: For flat-to-moderate terrain, end-to-end training with frame-stacked proprioception matches teacher-student performance. Teacher-student only provides benefit when heightmap or vision observations are needed for challenging terrain.
Mechanism: Teacher-student adds complexity (two training phases, distillation loss tuning). For simple proprioceptive policies, the extra complexity doesn't pay off. The benefit emerges when the student must infer privileged terrain information from limited sensors.
Reference: ULT unified framework (2025); Berkeley Humanoid uses simple end-to-end without teacher-student.

### Q12 -- Entropy Coefficient Schedule [OPEN]
Impact: MEDIUM
Hypothesis: An entropy coefficient that decays from 0.01 to 0.001 over training will outperform a fixed value, because early exploration is critical but late-stage exploitation benefits from deterministic actions.
Mechanism: High entropy early encourages diverse gait exploration. As training converges, entropy prevents the policy from sharpening to a precise gait pattern.
Reference: Eimer et al. (2023) hyperparameter study; PPO implementation details (2022).

### Q13 -- Termination Penalty Magnitude [OPEN]
Impact: MEDIUM
Hypothesis: There exists an optimal termination penalty magnitude (around -10 to -20) that balances risk-taking and caution; below -5 the robot takes unnecessary risks, above -30 it becomes overly conservative and refuses to walk quickly.
Mechanism: Termination penalty creates a "fear of falling" that trades off with velocity rewards. Too much fear prevents the robot from approaching its dynamic limits.
Reference: Reward hacking analysis (Weng, 2024); stage-wise reward shaping (2024).

### Q14 -- Domain Randomization Friction Range [OPEN]
Impact: HIGH
Hypothesis: The optimal friction randomization range for zero-shot transfer is [0.4, 1.5] for indoor deployment and [0.2, 2.0] for outdoor deployment, with wider ranges reducing average performance but improving worst-case performance.
Mechanism: Real-world friction varies dramatically (polished floors ~0.2, rubber on concrete ~1.5+). The policy must handle this entire range, but wider training ranges dilute the gradient signal for common friction values.
Reference: Evaluating DR in DRL Locomotion (2023); Isaac Lab sim-to-real for Spot (2024).

### Q15 -- PD Gain Optimization [OPEN]
Impact: MEDIUM
Hypothesis: Jointly optimizing PD gains (kp, kd) alongside the policy via HDR will improve both simulation performance and transfer, because factory-default gains are tuned for trajectory tracking, not RL-generated commands.
Mechanism: RL policies generate action patterns that differ from designed trajectories. PD gains optimized for RL-style commands will provide better torque tracking fidelity.
Reference: Variable Stiffness for Robust Locomotion (2025); PD gains as critical transfer parameter.

### Q16 -- Automatic Curriculum via Learning Progress [OPEN]
Impact: HIGH
Hypothesis: Learning Progress-based Automatic Curriculum (LP-ACRL) will discover better terrain progressions than hand-designed linear difficulty schedules, achieving faster convergence and better final performance on rough terrain.
Mechanism: LP-ACRL measures how quickly the agent is improving on each terrain type and preferentially samples terrains where learning is fastest, automatically focusing training effort where it matters most.
Reference: LP-ACRL (2025); achieved 2.5 m/s on diverse terrains with ANYmal D.

### Q17 -- LLM-Bootstrapped Reward Functions [OPEN]
Impact: MEDIUM
Hypothesis: Using Eureka/DrEureka to generate initial reward functions, then refining weights via HDR, will outperform both pure LLM design and pure HDR search from scratch.
Mechanism: LLMs provide excellent initial structure (which terms to include) but poor weight calibration. HDR excels at continuous weight optimization from a good starting point.
Reference: Eureka (2024) 83% human-expert-beating rate; DrEureka (2024) 34% improvement over human designs.

### Q18 -- MJX vs Isaac Gym Training Efficiency [OPEN]
Impact: MEDIUM
Hypothesis: MuJoCo Playground (MJX) will achieve comparable or better training efficiency to Isaac Gym/Lab for standard locomotion tasks on a single RTX 4090, due to JAX compilation advantages and simpler setup.
Mechanism: MJX's JAX-native implementation enables whole-program optimization through XLA, potentially outperforming PyTorch-based Isaac Gym's tensor API for the specific computation pattern of RL training.
Reference: MuJoCo Playground (2025) training times; Isaac Lab benchmarks.

### Q19 -- Multiplicity of Behavior for HDR [OPEN]
Impact: MEDIUM
Hypothesis: Training a single MoB policy that encodes diverse locomotion strategies will enable faster HDR iteration, because strategy selection parameters can be optimized without retraining the base policy.
Mechanism: Walk These Ways shows that a family of behaviors can be encoded in one policy. HDR can then search over behavior parameters rather than reward weights, dramatically reducing evaluation cost per iteration.
Reference: Walk These Ways (Margolis & Agrawal, 2023); diverse gaits from single policy.

### Q20 -- Morphology Co-Optimization Feasibility [OPEN]
Impact: MEDIUM
Hypothesis: HDR can effectively co-optimize body parameters (link lengths +/- 20%) alongside policy parameters if morphology changes are made infrequently (every 5-10 HDR iterations) with controller fine-tuning between changes.
Mechanism: Morphological changes invalidate the current controller (Cheney et al., 2018 innovation protection). By changing body parameters slowly and allowing controller re-adaptation, HDR can explore the joint body-controller space.
Reference: Morphological pretraining (2025); Stackelberg PPO for co-design (2026).

### Q21 -- Dual-History Architecture for Adaptation [OPEN]
Impact: MEDIUM
Hypothesis: A dual-history architecture (short 5-step window for reflexes + long 50-step window for adaptation) will outperform single-history approaches for rough terrain locomotion by simultaneously capturing fast contact dynamics and slow terrain features.
Mechanism: Contact events happen in <100ms (short history), while terrain type assessment requires 0.5-2s of experience (long history). Separate processing paths can specialize for each timescale.
Reference: Li et al. (2024) dual-history for Cassie; KiVi multi-rate sensing (2025).

### Q22 -- Action Delay Randomization Impact [OPEN]
Impact: HIGH
Hypothesis: Randomizing action delay in the range [0, 30ms] during training will be the single most impactful DR parameter for sim-to-real transfer on consumer-grade robots (Unitree Go2), which typically have 10-20ms communication latency.
Mechanism: Action delay creates a feedback control lag that fundamentally changes the system dynamics. Policies trained without delay randomization are brittle to real-world latencies.
Reference: legged_gym noise configuration; PACE systematic sim-to-real (2024).

### Q23 -- Multi-Objective Reward Optimization [OPEN]
Impact: LOW
Hypothesis: Treating the locomotion reward as a multi-objective optimization problem (speed vs energy vs smoothness vs stability) and finding the Pareto frontier will yield more useful policies than single-objective optimization.
Mechanism: Different deployment scenarios require different tradeoffs. A Pareto frontier provides a menu of policies to choose from, or enables runtime interpolation between objectives.
Reference: Multi-objective MARL survey (2024); stage-wise reward shaping (2024).

### Q24 -- Contact State as Observation [OPEN]
Impact: LOW
Hypothesis: Including binary contact states (foot on/off ground) as observations improves gait regularity by 15% compared to relying solely on joint position/velocity for contact inference.
Mechanism: Contact states are difficult to infer from joint measurements alone, especially during the make/break transition. Direct sensing removes this inference burden.
Reference: legged_gym contact force observations; MuJoCo Playground observation structure.

### Q25 -- Lipschitz Constraint vs Action Rate Penalty [OPEN]
Impact: MEDIUM
Hypothesis: Lipschitz-constrained policies will produce smoother locomotion than action rate penalties with equal task performance, because the constraint operates on the network directly rather than as a reward signal.
Mechanism: Action rate penalties create a soft preference for smoothness but the policy can still produce jitter if the task reward is sufficiently high. Lipschitz constraints provide a hard architectural bound on output sensitivity.
Reference: Chen et al. (2024) Lipschitz-Constrained Policies; Spectral Normalization for Lipschitz constraints (2025).
