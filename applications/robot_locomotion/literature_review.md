# Literature Review: Robot Locomotion Policy Optimization via GPU-Accelerated Simulation

## 1. Domain Fundamentals

### Rigid Body Dynamics and Robot Simulation

The physics of robot locomotion rests on rigid body dynamics -- the study of how interconnected rigid links move under forces, torques, and constraints. Featherstone's *Rigid Body Dynamics Algorithms* (2008) remains the definitive reference, presenting spatial vector notation (6D) and recursive O(n) algorithms for both forward and inverse dynamics of articulated bodies. The two core algorithms -- the Recursive Newton-Euler Algorithm (RNEA) for inverse dynamics and the Articulated Body Algorithm (ABA) for forward dynamics -- underpin every modern physics engine used in robot simulation (Featherstone, 2008). RNEA computes the joint torques required to produce a given set of joint accelerations (inverse dynamics), essential for feedforward control, while ABA computes the joint accelerations resulting from applied torques (forward dynamics), which is what a simulator needs to propagate state forward in time. Both operate in O(n) time complexity, where n is the number of joints, by exploiting the tree structure of articulated bodies through recursive outward (velocity/acceleration) and inward (force) passes.

The equations of motion for a robot with generalized coordinates q take the form M(q) * ddq + C(q, dq) * dq + g(q) = tau + J^T * f_contact, where M is the mass matrix, C captures Coriolis and centrifugal effects, g is the gravity vector, tau is the vector of applied joint torques, and J^T * f_contact represents contact forces mapped to joint space. Computing M, C, and g efficiently is the job of the dynamics algorithms, and the contact forces f_contact must be determined by the contact model.

Lynch and Park's *Modern Robotics: Mechanics, Planning, and Control* (2017) provides a complementary perspective using screw theory, covering kinematics, dynamics, motion planning, and control in a unified geometric framework. Their use of the product of exponentials formula for forward kinematics and the geometric Jacobian provides intuitive tools for understanding how joint motions map to end-effector (or foot) velocities. For legged systems specifically, Tedrake's *Underactuated Robotics* (continuously updated, MIT 6.832) addresses the unique challenges of systems with fewer actuators than degrees of freedom -- exactly the situation in dynamic locomotion where the robot is intermittently in flight. Tedrake emphasizes that underactuated systems cannot be controlled with standard feedback linearization or computed torque methods, and instead require techniques from nonlinear dynamics, trajectory optimization, and reinforcement learning. His treatment of the simple models (compass gait, rimless wheel, spring-loaded inverted pendulum) provides essential intuition for understanding how locomotion emerges from passive dynamics and how control should complement rather than fight the natural dynamics.

### Physics Engines: How They Work

Modern robot simulators solve the equations of motion at discrete timesteps, handling the critical challenge of contact and collision. Contact is the defining difficulty of locomotion simulation: every footstep involves a transition from free flight to constrained motion, and the contact forces must simultaneously satisfy physical constraints (non-penetration, friction cone, complementarity). The dominant approaches to contact resolution are:

**Constraint-based (complementarity) methods** formulate contact as a Linear Complementarity Problem (LCP) or Nonlinear Complementarity Problem (NCP), enforcing that contact forces are non-negative, penetration is non-negative, and their product is zero (complementarity: either the foot is not in contact and the force is zero, or the foot is in contact and penetration is zero). This produces physically accurate hard contacts but can be computationally expensive, and the combinatorial nature of contact mode enumeration (each contact point can be in sliding, sticking, or separation mode) creates challenges for both solving and differentiating through the solution. The ODE (Open Dynamics Engine) and DART use LCP-based contact, while Dojo (Howell et al., 2022) uses an interior-point solver that smooths the complementarity conditions.

**Penalty-based (soft contact) methods**, used by MuJoCo, model contact forces as proportional to constraint violation depth, combined with damping. MuJoCo reformulates contacts as a convex optimization problem, yielding smooth, fast solutions at the cost of some penetration (Todorov et al., 2012). Specifically, MuJoCo solves a cone-constrained QP at each timestep to find contact forces that minimize a weighted combination of constraint violation and contact force magnitude. This soft contact model is numerically stable and highly efficient, making MuJoCo the dominant engine for learning-based locomotion research. The trade-off is that soft contacts allow small interpenetrations, which can lead to energy injection in edge cases, but for locomotion applications the benefits of speed and stability far outweigh this limitation.

**Impulse-based methods** resolve contacts through instantaneous velocity changes, computing impulses that prevent penetration and enforce friction. Bullet Physics uses this approach and was historically popular for games and robotics simulation, but has largely been superseded by MuJoCo for learning applications due to MuJoCo's superior performance in massively parallel settings and its cleaner API for reinforcement learning.

### Collision Detection

Before contact forces can be computed, the simulator must detect which bodies are in contact. This involves two phases: broad-phase collision detection (quickly determining which pairs of bodies might be in contact using bounding box tests) and narrow-phase collision detection (computing exact contact points, normals, and penetration depths for candidate pairs). MuJoCo uses a convex collision detection system that supports primitive shapes (spheres, capsules, boxes, cylinders, ellipsoids) and convex meshes. For locomotion, feet are typically modeled as spheres or capsules, and the ground as a half-space or heightfield. The maximum number of contact points per body pair (set by the nconmax parameter) affects both accuracy and computational cost -- MuJoCo Playground uses 8 maximum contact points for humanoid tasks.

### Time Stepping and Integration

Physics engines use semi-implicit Euler or symplectic integration with typical timesteps of 1-5ms. For locomotion, MuJoCo typically operates at 200Hz (5ms timestep) with the policy running at 50Hz (20ms), meaning 4 physics substeps per policy step. This separation is important: the PD controller operates at the physics rate, computing torques at each substep based on the desired position set by the policy, while the neural network policy operates at a lower rate, reducing computational cost while maintaining physical accuracy. The choice of timestep involves a fundamental tradeoff: smaller timesteps improve accuracy (especially for stiff contacts and fast dynamics) but increase computational cost proportionally. For MJX specifically, the DM Control Suite environments required solver parameter adjustments -- CartpoleBalance uses 1 solver iteration and 4 line-search iterations, while humanoid tasks use 0.005s timesteps with expanded contact parameters.

Numerical integration introduces errors that accumulate over time. Symplectic integrators preserve the geometric structure of Hamiltonian systems (energy conservation), making them preferred for long simulations. However, the presence of contact forces, damping, and actuation breaks the Hamiltonian structure, so in practice semi-implicit Euler is the standard choice, trading formal energy conservation for stability and simplicity.

### Actuator Models

Real motors have dynamics that simulators must approximate. The gap between simulated and real actuators is one of the primary sources of sim-to-real failure. Key considerations include:
- **Motor saturation**: torque limits that depend on velocity (the torque-speed curve). At high joint velocities, the available torque decreases, which affects dynamic movements like running and jumping.
- **Bandwidth**: motors cannot instantaneously track desired positions. The motor-gear-load system has a natural frequency and damping ratio that limit response speed. Typical motor bandwidth is 10-50Hz for position control.
- **Backlash and friction**: gear train imperfections create dead zones where motor motion doesn't translate to joint motion, and Coulomb friction adds hysteresis.
- **Thermal limits**: sustained high-torque operation causes motor winding temperature to rise, reducing available torque and potentially causing thermal shutdown.
- **Communication delays**: the time between policy output and torque application on the motor. Consumer robots like Unitree Go2 have 10-20ms communication latency.

Modern sim-to-real pipelines either model these explicitly (actuator networks, as in RSL's legged_gym, which learns a neural network mapping from desired to actual motor behavior) or randomize over them during domain randomization. The PACE framework (ETH RSL, 2024) provides a systematic approach to actuator identification, combining data-driven methods with evolutionary optimization to create accurate actuator models that significantly improve sim-to-real transfer.

---

## 2. Locomotion Theory

### Gaits and Their Classification

Legged locomotion is organized into gaits -- periodic patterns of leg coordination defined by the timing and duration of each leg's stance (ground contact) and swing (aerial) phases. The key parameters characterizing a gait are the duty factor (fraction of the cycle each leg spends in stance), the phase offset between legs, and the stride frequency. For quadrupeds, the fundamental gaits are:

- **Walk**: slow, always at least two feet on ground, sequential leg lifting (duty factor > 0.5). The sequence is typically left-hind, left-front, right-hind, right-front, with each leg lifting in turn. Walking maximizes stability by maintaining a large support polygon at all times.
- **Trot**: diagonal legs move together (left-front + right-hind, then right-front + left-hind), two legs always in contact, moderate speed. Trotting is the most common gait for quadruped robots because it provides good stability with reasonable speed.
- **Pace**: lateral legs move together (left-front + left-hind simultaneously), producing a side-to-side swaying motion. Less common in robots but used by some animals (camels, giraffes) and can emerge naturally from RL training.
- **Bound/Gallop**: front legs and back legs move together (bound) or in rapid sequence (gallop), high speed, includes aerial phases where no feet touch the ground. These gaits achieve the highest speeds but require precise timing and are dynamically unstable -- the robot must actively control its trajectory through the air.
- **Pronk**: all four legs lift and land simultaneously, used for jumping or dynamic standing. Energetically expensive but useful for clearing obstacles.

Animals naturally transition between gaits as speed increases, and this is energetically optimal: walking is efficient at low speeds, trotting at moderate speeds, and galloping at high speeds (Hoyt & Taylor, 1981). This was demonstrated experimentally by showing that horses voluntarily switch gaits at speeds where each gait's energy cost crosses over. Cost of Transport (CoT = Power / (mass * gravity * velocity)) is the standard dimensionless metric for locomotion efficiency. Biological reference values include: humans walking ~0.2, horses trotting ~0.2, and cockroaches running ~10. Current humanoid robots achieve CoT ~0.7 at best, while quadruped robots range from 0.5 to 2.0, indicating significant room for improvement. Recent work on adaptive energy regularization (ICRA 2025) demonstrates that RL policies can learn to automatically switch gaits based on speed, achieving 7-21% energy savings compared to single-gait policies.

For bipeds, the fundamental gaits are walking (always one foot on ground, duty factor > 0.5) and running (aerial phase exists, duty factor < 0.5). Humanoid robots face additional gait challenges due to the need to coordinate arm swing for angular momentum management, maintain an upright torso, and handle the inverted pendulum dynamics of a tall, heavy body on relatively small feet.

### Central Pattern Generators (CPGs)

Biological locomotion is driven by central pattern generators -- neural circuits in the spinal cord that produce rhythmic motor patterns without requiring rhythmic input from the brain. CPGs are self-organizing networks that spontaneously generate the coordinated muscle activation patterns for walking, swimming, and other rhythmic behaviors. They consist of coupled oscillators, one per limb, whose phase relationships determine the gait. The connections between CPGs for each limb manage interlimb coordination, and the balance between alternating-phase gaits (walk, trot) and synchronous gaits (bound, gallop) is determined by the coupling strengths. Critically, CPGs can produce spontaneous gait transitions by changing only speed-related parameters, without requiring explicit gait selection logic (Ijspeert, 2008).

In robotics, artificial CPGs have been implemented as systems of coupled nonlinear oscillators (typically Hopf or Van der Pol oscillators) whose parameters -- frequency, amplitude, phase offset, and coupling strength -- are tuned to produce desired gaits. CPG-based controllers have the advantage of inherent rhythmicity, smooth gait transitions, and robustness to perturbations (the oscillator naturally returns to its limit cycle after disturbances). However, they also have limitations: the space of achievable behaviors is constrained by the oscillator topology, and tuning the many coupling parameters is non-trivial.

Recent RL approaches have largely replaced explicit CPGs as the primary locomotion controller, but CPG-inspired concepts remain influential. Phase variables encoding the gait cycle are common observations in modern RL policies -- MuJoCo Playground provides sin/cos phase variables for each foot as part of the humanoid observation space. These phase variables give the policy a "clock" signal that helps it discover periodic locomotion patterns without having to learn temporal structure purely from observation history. The gait-conditioned RL framework (2025) explicitly encodes gait identity (standing, walking, running) as a conditioning input, enabling a single policy to produce multiple gaits with human-inspired biomechanical characteristics.

Hierarchical approaches combining CPGs with RL have also shown promise. A CPG generates the basic rhythmic pattern (frequency, phase coordination), while the RL policy modulates CPG parameters or adds residual corrections. This provides the benefits of structured periodic motion with the adaptability of learned control (hierarchical CPG-RL, 2025).

### Stability Criteria

Several frameworks quantify locomotion stability, each appropriate for different regimes:

- **Static stability**: the simplest criterion -- the center of mass projection must lie within the support polygon (convex hull of foot contact points). This is only relevant for very slow walking with high duty factors.
- **Zero Moment Point (ZMP)**: the point on the ground where the net ground reaction force produces zero horizontal moment. If ZMP remains within the support polygon, the robot will not tip over. Developed by Vukobratovic and Borovac (2004), ZMP has been the foundation of humanoid walking control for decades (Honda ASIMO, HRP series). ZMP-based walking generates flat-footed, quasi-static gaits that are energy-inefficient but highly stable. The limitation is that ZMP assumes flat-foot contact and doesn't handle toe-off or heel-strike dynamics.
- **Capture Point** (also called Instantaneous Capture Point or Divergent Component of Motion): the point on the ground where a robot must place its foot in order to come to a complete stop. For the Linear Inverted Pendulum (LIP) model, the capture point is determined by x_cp = x_com + (dx_com / omega_0), where omega_0 = sqrt(g/z_com). Developed by Pratt et al. (2006), it extends ZMP to dynamic walking where the robot is not quasi-static. If the capture point lies within the reachable foot placement area, the robot can recover from a disturbance. Recent work (2026) embeds capture point and center-of-mass momentum as privileged critic inputs and reward terms for humanoid recovery, achieving robust push recovery through balance-informed RL.
- **Raibert Heuristic**: a simple linear relationship between desired velocity and foot placement: x_foot = x_hip + v * T_stance/2 + k * (v - v_desired), where k is a gain parameter. This was developed by Marc Raibert in his pioneering work on dynamically stable one-legged hopping robots (1986). Despite its simplicity, this heuristic captures the essential physics of dynamic balance: place the foot ahead of the center of mass in proportion to forward velocity to decelerate, behind to accelerate. The Raibert heuristic and capture point are related -- both use linear functions of body velocity for foot placement control.
- **Orbital stability**: for periodic gaits, stability can be analyzed through Poincare maps. A gait is orbitally stable if small perturbations from the limit cycle decay over subsequent strides. This is the relevant notion for RL-trained gaits, though it is rarely computed explicitly.

### Ground Reaction Forces

Ground reaction forces (GRFs) are the forces exerted by the ground on the robot's feet during contact. They are the only external forces (besides gravity) that a legged robot can use to control its motion. GRFs have three components: a normal force perpendicular to the ground (supporting the robot's weight and enabling acceleration/deceleration in the vertical direction), and two tangential (friction) forces parallel to the ground surface. The friction forces are bounded by the friction cone: |f_tangential| <= mu * f_normal, where mu is the coefficient of friction. If the required tangential force exceeds this limit, the foot slips.

In simulation, GRFs are computed by the contact solver at each timestep. In MuJoCo's soft contact model, the normal force increases smoothly with penetration depth, while friction forces are computed to satisfy the friction cone constraint. The shape of the ground reaction force profile during a stride -- the time history of vertical and horizontal GRF -- is characteristic of the gait and is used in biomechanics to analyze walking and running. Healthy human walking shows a distinctive double-hump vertical GRF pattern (heel-strike and push-off peaks), while running shows a single peak. Reward functions can target specific GRF profiles to encourage natural gaits, though most current approaches use indirect measures (velocity tracking, foot clearance) rather than explicit GRF shaping.

### What Makes Locomotion Hard

Locomotion is a hybrid dynamical system with discrete contact mode switches (stance/swing), underactuation (can't directly control center of mass -- it can only be indirectly influenced through foot forces), high dimensionality (12+ joints for quadrupeds, 20+ for humanoids), and multi-contact constraint satisfaction. The contact-rich nature means small errors in contact timing or force can cascade into falls through a positive feedback loop: a misstep shifts the center of mass, which requires corrective forces that may not be achievable within the friction cone, leading to further instability.

The hybrid dynamics create a fundamental challenge for optimization-based approaches: the contact mode sequence (which feet are in contact at each timestep) is discrete, creating a combinatorial explosion. A quadruped with 4 feet has 2^4 = 16 possible contact modes at each timestep. Over a trajectory of N timesteps, the total number of contact mode sequences is 16^N -- an astronomically large space that cannot be enumerated. This is why RL, which does not require explicit contact scheduling, has proven so effective for locomotion.

Additional difficulties include the underactuated floating base (the robot's body has 6 degrees of freedom -- 3 position, 3 orientation -- but no direct actuation; all control must go through the legs), the need to satisfy unilateral contact constraints (feet can push but not pull on the ground), and the requirement for real-time computation (the controller must run at 50-1000Hz to maintain balance). For humanoids, the challenge is compounded by the small support polygon (two feet, each roughly 25cm x 10cm), high center of mass (approximately 1m above the ground), and the need to coordinate 20+ joints for whole-body balance.

---

## 3. Reinforcement Learning for Locomotion

### Policy Gradient Methods

The reinforcement learning approach to locomotion treats the problem as a Markov Decision Process (MDP): at each timestep, the agent observes the state s (joint angles, velocities, body orientation, commands), selects an action a (desired joint positions) according to a policy pi(a|s), receives a reward r(s,a), and transitions to a new state s'. The objective is to find the policy pi* that maximizes the expected cumulative discounted reward: J(pi) = E[sum_t gamma^t * r(s_t, a_t)], where gamma is the discount factor (typically 0.99 for locomotion). The policy and value function are parameterized by neural networks, and training proceeds by collecting rollouts in simulation and updating parameters via gradient ascent on J.

The foundational theory is covered in Sutton and Barto's *Reinforcement Learning: An Introduction* (2nd edition, 2018), which provides the mathematical framework for temporal difference learning, policy gradients, and actor-critic methods. The policy gradient theorem establishes that the gradient of J with respect to policy parameters theta is: nabla_theta J = E[sum_t nabla_theta log pi_theta(a_t|s_t) * A(s_t, a_t)], where A is the advantage function (how much better action a_t is compared to the average action in state s_t).

**Proximal Policy Optimization (PPO)** (Schulman et al., 2017) dominates locomotion training. PPO is an on-policy actor-critic method that constrains policy updates via a clipped surrogate objective: L_CLIP = E[min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)], where r_t = pi_new(a|s) / pi_old(a|s) is the probability ratio. The clipping prevents destructively large updates that could collapse the policy. PPO alternates between collecting data through environment interaction and performing multiple epochs of minibatch updates on the collected data, making efficient use of each batch. Its key hyperparameters for locomotion include: clip ratio (typically 0.2, but this can determine success/failure per Eimer et al. 2023), entropy coefficient (0.001-0.01, encouraging exploration early in training), learning rate (~3e-4, often with linear decay), GAE lambda (0.95-0.99), and number of minibatch epochs (3-5). PPO's simplicity, stability, and compatibility with massively parallel environments make it the default choice. The "37 Implementation Details of PPO" (2022) documents that seemingly minor implementation choices -- observation normalization, advantage normalization, learning rate annealing, gradient clipping, orthogonal initialization -- significantly impact performance and must be carefully implemented.

**Generalized Advantage Estimation (GAE)** (Schulman et al., 2015) provides the variance-reduced advantage estimates that PPO relies on. The GAE formula computes: A_t^GAE = sum_{l=0}^{inf} (gamma * lambda)^l * delta_{t+l}, where delta_t = r_t + gamma * V(s_{t+1}) - V(s_t) is the one-step TD error. The lambda parameter (typically 0.95) controls the bias-variance tradeoff: lambda=0 gives the one-step TD error (low variance, high bias), while lambda=1 gives the Monte Carlo advantage (high variance, low bias). Values of lambda in [0.96, 0.99] yield fast, stable learning for continuous control. For contact-rich locomotion, where reward signals can be noisy due to contact events, slightly lower lambda values (0.92-0.95) may provide better stability by reducing the propagation of high-variance contact signals.

**Trust Region Policy Optimization (TRPO)** (Schulman et al., 2015b) preceded PPO and provides stronger theoretical guarantees through explicit KL-divergence constraints on policy updates. However, TRPO's second-order optimization (conjugate gradient method for computing the natural gradient) is more computationally expensive and harder to implement than PPO's simple clipping. TRPO remains relevant conceptually as the theoretical motivation for PPO's conservative updates.

**Soft Actor-Critic (SAC)** (Haarnoja et al., 2018) is an off-policy maximum-entropy algorithm that learns a stochastic policy alongside two Q-functions. The maximum entropy objective augments the standard RL objective with an entropy bonus: J(pi) = E[sum_t r(s_t, a_t) + alpha * H(pi(.|s_t))], where H is the entropy and alpha is automatically tuned. This encourages exploration and prevents premature convergence to suboptimal deterministic policies. While more sample-efficient than PPO (reusing experience from a replay buffer), SAC is less commonly used for locomotion because: (1) the replay buffer doesn't benefit from massive parallelism as directly -- PPO can immediately use all parallel experience while SAC must store and sample from it, (2) off-policy methods can be less stable with the rapid distribution shift that occurs during early locomotion training when the robot frequently falls, and (3) PPO's wall-clock training time advantage with 4096+ parallel environments typically outweighs SAC's per-sample efficiency advantage.

However, this picture is changing rapidly. Recent work on FastSAC and FastTD3 (Seo et al., 2024) has shown that off-policy methods can match or exceed PPO when properly parallelized with thousands of environments feeding a shared replay buffer. Their approach trains humanoid locomotion in 15 minutes on a single RTX 4090, and with 4x L40s GPUs and 16384 parallel environments, FastSAC learns complex dancing motions faster than PPO in wall-clock time. The key insight is that off-policy methods benefit from parallelism differently: more environments fill the replay buffer faster, providing more diverse experience for each gradient step.

**TD3** (Fujimoto et al., 2018) extends DDPG with three innovations: clipped double-Q learning (using the minimum of two Q-functions to reduce overestimation), delayed policy updates (updating the policy less frequently than Q-functions), and target policy smoothing (adding noise to target actions). In comparative evaluations for quadruped locomotion (PPO-TD3-SAC comparison, 2023), TD3 achieves 78% success rate with the smoothest training curves and fewest training instabilities, making it attractive for sim-to-real applications where training reliability matters.

### Imitation Learning and Motion Priors

Pure RL requires engineering reward functions from scratch, which is laborious and error-prone. Imitation learning provides an alternative by leveraging reference motions:

**DeepMimic** (Peng et al., 2018) demonstrated that physics-based characters could learn to imitate motion capture data through a combination of motion tracking reward and task reward. The agent receives high reward for matching reference joint angles, velocities, and end-effector positions at each timestep, plus additional reward for task completion (e.g., reaching a target). DeepMimic produced remarkable results -- human characters performing backflips, martial arts, and varied locomotion styles -- and established the framework for motion-conditioned RL.

**AMP (Adversarial Motion Priors)** (Peng et al., 2021, SIGGRAPH) replaced explicit motion tracking with an adversarial discriminator that distinguishes between agent behavior and reference motion. The discriminator provides a style reward signal that encourages natural-looking motion without requiring explicit frame-by-frame tracking. This enables using unstructured motion datasets and automatically composing skills from multiple clips.

**Learning Agile Robotic Locomotion Skills by Imitating Animals** (Peng et al., 2020, RSS Best Paper) transferred animal motion capture data to a real quadruped robot, demonstrating diverse agile behaviors (trotting, pacing, galloping, spinning) learned from animal reference motions with domain adaptation for sim-to-real transfer.

### Key Breakthroughs in Learned Locomotion

The field has seen rapid progress over the past five years:

- **ANYmal** (ETH Zurich RSL): Rudin et al. (2022) demonstrated "Learning to Walk in Minutes" using massively parallel simulation in Isaac Gym with 4096 environments, training ANYmal locomotion policies in under 4 minutes on flat terrain and 20 minutes on rough terrain. This paper established the template for GPU-accelerated locomotion training, introducing a game-inspired curriculum where terrain difficulty increases based on robot performance, and analyzing how different training components (reward terms, domain randomization, curriculum) interact in the massively parallel regime.
- **ANYmal Parkour** (Hoeller et al., 2024, Science Robotics): The robot learned to jump, climb, and crouch for rapid navigation of obstacle courses at up to 2 m/s, splitting the problem into three interconnected modules: a perception module processing point clouds from cameras and LiDAR, a locomotion module containing a catalog of skills (walking, jumping, climbing, crouching), and a navigation module selecting which skill to activate. This modular decomposition proved essential for learning complex multi-skill behaviors.
- **Wild ANYmal** (Miki et al., 2022, Science Robotics): Perceptive locomotion combining exteroceptive (heightmap) and proprioceptive sensing through an attention-based recurrent encoder trained end-to-end. The system seamlessly integrates different perception modalities without heuristics and completed a 1-hour Alpine hike at human-recommended pace, handling muddy trails, snow, dense vegetation, and rocky terrain.
- **Cassie** (UC Berkeley): Li et al. (2024) developed versatile bipedal locomotion including walking, running (400m dash), and jumping through a unified RL framework with dual-history policy architecture. The dual-history approach uses separate short-term (for fast reflexive responses) and long-term (for environmental adaptation) memory, achieving zero-shot sim-to-real transfer on the 31kg, 1.1m tall Cassie robot.
- **MIT Mini Cheetah** (Margolis et al., 2023): Achieved record-breaking 3.9 m/s running speed using an adaptive velocity curriculum (starting with easy commands and progressively increasing difficulty) and online system identification for sim-to-real transfer. The controller demonstrated robust running on grass, ice, gravel, and other natural terrains.
- **Digit** (Agility Robotics): A full-size humanoid (175cm, 65-76kg) with an LSTM-based whole-body controller (under 1M parameters) trained via deep RL in Isaac Sim. Deployed commercially in GXO warehouse logistics, moving 100,000+ totes, validating that RL-trained locomotion is production-ready.
- **Atlas** (Boston Dynamics): Combines Model Predictive Control with reinforcement learning and a 450M parameter Diffusion Transformer-based policy using flow-matching objectives. Atlas's control system uses over 150 million simulation runs per maneuver, representing the extreme compute end of locomotion learning. The 2025 demonstrations showed Atlas performing parkour, dance, and dexterous manipulation.
- **A Walk in the Park** (Smith et al., 2023, RSS): Demonstrated that a Unitree A1 quadruped can learn to walk from scratch in 20 minutes directly on real hardware using SAC, without any simulation. This challenges the assumption that sim-to-real is always necessary and shows that careful algorithm implementation can make real-world RL practical.

---

## 4. GPU-Accelerated Simulation

### The Parallel Simulation Revolution

The key insight enabling modern locomotion training is massive parallelism: instead of training one robot, simulate thousands simultaneously on GPU. This transforms RL training from hours/days to minutes. The paradigm shift occurred in 2021 with the release of Isaac Gym (Makoviychuk et al., 2021), which demonstrated that by keeping all simulation data on the GPU and providing a tensor-based API that wraps physics buffers as PyTorch tensors, the CPU-GPU data transfer bottleneck could be eliminated entirely. This enabled running tens of thousands of simultaneous environments on a single GPU, with end-to-end training proceeding entirely in GPU memory.

The mathematical basis is straightforward: PPO requires a batch of experience (state, action, reward, next_state) tuples for each update. With N parallel environments running for T timesteps, the batch size is N * T. Larger batches provide better gradient estimates, enabling larger and more stable policy updates. With 4096 environments and 24 timestep rollouts, each PPO update uses ~100K transitions, providing a rich statistical picture of policy performance. The resulting training throughput, measured in environment steps per second, determines wall-clock training time.

### Framework Comparison

**MuJoCo XLA (MJX)**: A JAX reimplementation of MuJoCo's physics engine that runs on GPUs and TPUs via XLA compilation. Part of Google DeepMind's MuJoCo ecosystem. Throughput benchmarks on A100: ~752K steps/second (Acrobot), ~435K (Cheetah), ~92K (Humanoid). MJX is JAX-native, enabling automatic differentiation, JIT compilation, and seamless integration with JAX-based RL libraries like Brax.

**MuJoCo Warp (MJWarp)**: Announced at GTC 2025, co-developed by Google DeepMind and NVIDIA using NVIDIA Warp. Achieves 252x speedup over MJX for locomotion and 475x for manipulation on RTX PRO 6000. Optimized for NVIDIA hardware with features like auto-hibernation and contact island optimization. Part of the Newton 1.0 physics engine (2026) under the Linux Foundation.

**Brax**: Google's JAX-based differentiable physics engine offering multiple simulation pipelines (generalized, positional, spring, and MJX). Achieves millions of physics steps per second on TPU. Includes built-in RL algorithms (PPO, SAC, ES). A humanoid locomotion policy was trained in ~56 minutes on a PC with RTX 4090 using 8192 parallel environments.

**Isaac Gym / Isaac Lab / Isaac Sim**: NVIDIA's simulation stack. Isaac Gym (2021) pioneered GPU-accelerated RL with tens of thousands of simultaneous environments. Performance: ANYmal trained in under 2 minutes, Ant in 20 seconds, humanoid character animation (AMP) in 6 minutes on a single A100. Isaac Lab is the successor, achieving ~90,000 frames/second for Spot locomotion on RTX A6000. Based on PhysX/USD, deeply integrated with NVIDIA hardware.

**Genesis**: Released December 2024, claims 430,000x real-time (43 million FPS on RTX 4090), 10-80x faster than Isaac Gym. Pure Python, supports differentiable simulation for MPM and tool solvers (rigid body differentiability in progress). A universal engine handling rigid bodies, fluids, cloth, and deformable bodies.

**MuJoCo Playground**: Google DeepMind's open-source framework built on MJX, released February 2025. Provides complete locomotion environments for Unitree Go1, Boston Dynamics Spot, Google Barkour, Berkeley Humanoid, Unitree H1/G1, Booster T1, and Robotis OP3. Most environments train in under 10 minutes on a single GPU. Supports both MJX and MuJoCo Warp backends.

### Practical Considerations for Framework Selection

The choice of simulation framework depends on several factors: hardware (NVIDIA GPU required for Isaac Lab and MuJoCo Warp; MJX runs on any JAX-supported accelerator including AMD GPUs and TPUs), programming paradigm (JAX functional programming for MJX/Brax vs PyTorch imperative programming for Isaac Lab), ecosystem maturity (Isaac Lab has more pre-built environments and integrations, while MuJoCo Playground is simpler to set up), and differentiability requirements (Brax and JAXsim provide automatic differentiation, while Isaac Lab does not).

For HDR on a single consumer GPU (RTX 3090/4090 class), the recommended approach is MuJoCo Playground with MJX backend. It provides the fastest path from installation to trained policy, with pip install and Colab notebook support. The MuJoCo Warp backend can be used for significant speedups on NVIDIA hardware once the codebase matures further. For researchers already embedded in the NVIDIA ecosystem with Isaac Sim experience, Isaac Lab is a strong alternative with more mature tooling for complex scenarios.

A critical consideration is RL library compatibility. MuJoCo Playground supports both Brax's JAX-based RL (PPO, SAC) and RSL-RL's PyTorch-based training. Both achieve comparable performance -- in benchmarks on the Unitree Go1 platform, identical policies trained with either library produced similar reward curves and wall-clock training times. This flexibility allows researchers to use whichever RL library they are more familiar with.

### Training Times on Consumer Hardware (RTX 4090)

The following table summarizes demonstrated training times for various locomotion tasks:

| Task | Framework | Time | Environments |
|------|-----------|------|-------------|
| Go1 joystick | MuJoCo Playground | ~5 min (2x 4090) | 4096 |
| Berkeley Humanoid | MuJoCo Playground | <15 min (2x 4090) | 4096 |
| Unitree G1/Booster T1 | MuJoCo Playground | <30 min (2x 4090) | 4096 |
| Vision-based pick-cube | MuJoCo Playground | 10 min (1x 4090) | 4096 |
| ANYmal flat terrain | Isaac Gym | <4 min (1x GPU) | 4096 |
| ANYmal rough terrain | Isaac Gym | ~20 min (1x GPU) | 4096 |
| Humanoid (FastSAC) | Custom | 15 min (1x 4090) | 4096 |
| Humanoid velocity (Brax+MJX) | Brax | ~56 min (1x 4090) | 8192 |
| LeapCubeReorient | MuJoCo Playground | ~35 min (1x 4090) | 4096 |
| Ant (Isaac Gym) | Isaac Gym | 20 sec (1x A100) | 4096 |
| AMP humanoid | Isaac Gym | 6 min (1x A100) | 4096 |

These times are for training to convergence (stable reward plateau). HDR iterations may use shorter training runs (50-75% of full convergence) for faster evaluation when identifying promising design variable directions, then run full training only for the best candidates.

### Multi-GPU Scaling

Scaling beyond a single GPU provides diminishing returns for RL training due to communication overhead. MuJoCo Playground benchmarks show that 8x H100 achieves approximately 3x speedup over 1x RTX 4090 for the LeapCubeReorient task (~670s vs ~2080s). The bottleneck shifts from physics computation to gradient synchronization across devices. For HDR, running independent trials on separate GPUs (embarrassingly parallel) is more efficient than scaling a single training run across GPUs.

### Differentiable Physics

Differentiable simulation enables gradient computation through the physics engine, potentially replacing RL's zeroth-order optimization with first-order methods. Key challenges include non-smooth contact dynamics: the discontinuities at contact make/break events produce incorrect or infinite gradients. Solutions include:

- **Implicit differentiation** of the contact NCP (up to 100x faster than alternatives)
- **Time-of-impact (TOI) corrections** for accurate pre-collision gradients
- **Interior-point solvers** providing smooth gradient approximations

Frameworks supporting differentiable physics include Brax, JAXsim, Dojo, and (partially) Genesis. JAXsim (2024) provides a reduced-coordinate physics engine built entirely in JAX with full automatic differentiation support for both forward and reverse modes, including differentiation with respect to kinematic and dynamic parameters. This enables gradient-based morphology optimization -- computing how changes to link lengths, masses, and inertias affect locomotion performance.

While promising for trajectory optimization, system identification, and morphology co-design, pure gradient-based policy optimization through contacts remains challenging for long horizons. The fundamental issue is that contact events create discontinuities in the state trajectory: the gradient of a 100-step trajectory through multiple contact/release events can either explode or vanish. Recent work on "Hard Contacts with Soft Gradients" (2025) addresses this by providing smooth gradient approximations through interior-point methods that maintain hard contact physics accuracy while enabling useful gradient information. Despite these advances, the consensus in the field is that gradient-free RL (PPO) with massively parallel environments remains more practical for locomotion policy learning, while differentiable physics is most valuable for system identification, short-horizon trajectory optimization, and morphology parameter optimization.

---

## 5. Reward Engineering

### The Art of Reward Design for Locomotion

Reward engineering is arguably the most impactful design choice in learned locomotion, and it is the area where HDR methodology has the most to contribute. The reward function defines what behavior is desired, and the policy optimization algorithm finds the best behavior according to that definition. A poorly designed reward function will produce a policy that perfectly optimizes the wrong objective. The comprehensive survey by the reward engineering review (2024) identifies seven critical pitfalls: reward sparsity, deceptive rewards, reward hacking, unintended consequences, misalignment, function complexity, and evaluation difficulty. For locomotion specifically, the reward function must balance multiple competing objectives -- speed, efficiency, smoothness, stability, and naturalness -- through a weighted combination of 8-15 terms:

The standard approach in the field is to compose the total reward as r_total = sum_i w_i * r_i(s, a), where each r_i is a reward component and w_i is its weight. The weights are the primary design variables that HDR should optimize. The legged_gym framework (ETH RSL) implements this cleanly: each non-zero reward scale in the configuration adds a named function to the reward computation, and setting a scale to zero removes that component entirely. This modular structure is ideal for HDR exploration.

**Task rewards** (what to achieve):
- **Velocity tracking**: `r_vel = exp(-c * ||v_cmd - v_actual||^2)` -- Gaussian kernel tracking commanded velocity, typically the largest reward component
- **Angular velocity tracking**: similar Gaussian tracking for yaw rate commands

**Regularization rewards** (how to achieve it):
- **Energy penalty**: `-w * sum(|tau * dq|)` penalizing mechanical power consumption
- **Torque penalty**: `-w * sum(tau^2)` penalizing large joint torques
- **Action rate**: `-w * sum((a_t - a_{t-1})^2)` penalizing jerky motions
- **Joint acceleration**: `-w * sum(ddq^2)` penalizing rapid joint velocity changes
- **Smoothness**: `-w * sum((a_t - 2*a_{t-1} + a_{t-2})^2)` second-order smoothness

**Style rewards** (what it should look like):
- **Foot clearance**: reward for sufficient foot height during swing (typically 5-8cm)
- **Body height**: penalty for deviation from nominal standing height
- **Body orientation**: penalty for roll/pitch deviation from upright
- **Feet airtime**: reward for each foot spending sufficient time in air (prevents shuffling)
- **Base motion**: penalty for excessive vertical or lateral body motion
- **Default pose**: small penalty for deviation from nominal joint configuration

**Safety rewards**:
- **Termination**: large negative reward for falling (base height too low, body contact)
- **Collision**: penalty for self-collision or undesired body-ground contacts
- **Joint limits**: penalty for approaching joint position or velocity limits

### Reward Hacking and Failure Modes

Reward hacking occurs when the agent exploits reward function loopholes. Common locomotion examples include:
- **Shuffling**: moving forward without lifting feet (if foot clearance isn't penalized)
- **Vibrating**: high-frequency oscillation exploiting energy terms
- **Exploiting termination**: deliberately ending episodes to avoid negative rewards
- **Phase transitions**: sudden qualitative policy shifts as network capacity increases, where proxy reward increases but true performance collapses

Mitigation strategies include multi-layered rewards (upper-level goal + lower-level style, as in the two-layered reward framework for humanoid motion tracking), exponential kernel functions for bounded rewards (which prevent any single term from producing arbitrarily large gradients), iterative reward tuning (training, observing behavior, adjusting weights), and formal analysis of reward function properties. The stage-wise reward shaping approach (2024) decomposes complex behaviors into phases, applying different reward structures at each phase to guide learning through the correct sequence of subgoals.

A particularly important consideration is the interaction between reward terms. Velocity tracking and energy penalty are inherently conflicting -- going faster requires more energy. The Pareto frontier between these objectives defines the achievable tradeoff space, and the relative weights w_vel and w_energy determine where on this frontier the trained policy operates. Similarly, action rate penalty (smoothness) conflicts with high-speed responses, and foot clearance reward conflicts with energy efficiency. Understanding these interactions is essential for effective HDR optimization of reward weights.

The reward function's mathematical properties also matter. Bounded rewards (using exponential kernels like exp(-c*||error||^2)) are preferred over unbounded quadratic penalties because they produce well-behaved gradients regardless of the error magnitude. The tracking sharpness coefficient c in the Gaussian kernel controls the sensitivity: larger c makes the reward more sensitive to small tracking errors (sharper peak), while smaller c provides a smoother signal that is easier to optimize but less precise. Typical values of c range from 2.0 to 10.0 depending on the units of the tracked quantity.

### Automatic Reward Design

**Eureka** (Ma et al., 2023, ICLR 2024) uses GPT-4 to generate reward functions from environment source code and task descriptions, then iteratively improves them through evolutionary search and training feedback. Eureka outperforms human experts on 83% of tasks across 29 environments and 10 robot morphologies, achieving 52% average improvement.

**DrEureka** (2024, RSS) extends Eureka for sim-to-real transfer by addressing two additional challenges: generating reward functions that produce physically safe behaviors (not just high task reward), and automatically designing domain randomization configurations. DrEureka's three-stage pipeline -- safety-constrained reward generation, Reward-Aware Physics Prior (RAPP) construction (evaluating policy robustness across perturbed dynamics to determine effective DR ranges), and LLM-guided DR distribution sampling -- produces policies that outperform human-designed systems by 34% in forward velocity and 20% in distance traveled across real-world evaluation terrains. DrEureka also demonstrated solving novel tasks (quadruped balancing on a yoga ball) without iterative manual design, highlighting the potential for LLM-guided automated design to discover solutions that human engineers might not consider.

The implications for HDR are significant: LLM-based reward generation could provide excellent initial reward function structure (which terms to include and their approximate forms), while HDR's systematic search can then fine-tune the weights and coefficients that LLMs struggle to calibrate precisely. This hybrid approach -- LLM for structure, HDR for optimization -- may outperform either in isolation.

---

## 6. Observation and Action Spaces

### Observation Space Design

The observation space defines what information is available to the policy at each decision point. The design of the observation space has profound effects on learning speed, policy quality, and sim-to-real transferability. A fundamental principle is that the observation must provide sufficient information to reconstruct the Markov property -- the policy should be able to determine the optimal action from the current observation alone (or with history for partially observable cases). The comprehensive survey by Ha et al. (2025) identifies the key categories of observations and provides practical recommendations based on extensive experimental evidence.

Observations must provide sufficient information for the policy to infer the state of the robot and its environment:

**Proprioceptive observations** (always available):
- Joint positions (relative to default): 12 values (quadruped) to 20+ (humanoid)
- Joint velocities: same dimensionality
- Base angular velocity (from IMU): 3 values
- Gravity vector in body frame (from IMU orientation): 3 values
- Previous action: same dimensionality as action space

**Command inputs**:
- Desired linear velocity (x, y): 2 values
- Desired angular velocity (yaw): 1 value

**Phase variables** (for humanoids/structured gaits):
- sin/cos of foot phase for each leg: 2 * num_legs values

**Exteroceptive observations** (for terrain-aware locomotion):
- Local heightmap around the robot: typically 11x11 or 21x21 grid, 0.1m resolution
- Depth images from cameras: 64x64 or 128x128
- Point clouds from LiDAR

**History encoding**: Since locomotion is partially observable (latencies, unobserved terrain), history is critical:
- **Frame stacking**: concatenating 5-10 previous observation vectors (simple but high-dimensional)
- **RNN/GRU/LSTM**: recurrent networks maintaining hidden state across timesteps (compact but harder to train)
- **Transformer/attention**: for combining multimodal inputs (Miki et al., 2022)

### Privileged Information and Teacher-Student

The teacher-student framework is standard for complex locomotion:

1. **Teacher policy** trains with privileged information available only in simulation: exact terrain heightmap, friction coefficients, body mass, contact states. This simplifies learning.
2. **Student policy** trains to imitate the teacher using only deployable observations (proprioception, maybe depth cameras). Typically uses an RNN/TCN to infer latent state from observation history.

This approach was formalized by Lee et al. (2020) and has become the default for sim-to-real locomotion. The teacher typically has access to exact terrain heightmaps (eliminating the need for noisy depth sensing), ground truth friction coefficients (which vary dramatically in the real world), exact body mass and inertial properties (which may change with payloads), and precise contact force measurements. The student must reconstruct this information implicitly from its observation history, which is why recurrent architectures (GRU, LSTM, TCN) are essential -- they can integrate temporal information to infer latent environmental properties.

Recent work has explored alternatives to the two-phase teacher-student approach. The Unified Locomotion Transformer (ULT, 2025) introduces privilege information as another modality in a unified framework, performing single-phase optimization that simultaneously learns to use and reconstruct privileged information. CTS (Concurrent Teacher-Student, 2024) trains teacher and student concurrently rather than sequentially, improving both sample efficiency and final policy quality. The Berkeley Humanoid (2024) demonstrated that for simple enough tasks (flat-terrain walking with light domain randomization), a simple end-to-end approach without teacher-student works well, suggesting that the complexity of teacher-student should be matched to the difficulty of the sim-to-real gap.

### Action Space Design

**Joint position targets** (dominant): The policy outputs desired joint angles, which are tracked by a PD controller: `tau = kp * (q_desired - q_actual) - kd * dq`. This is the most common choice because:
- Natural action bounds (joint limits)
- Inherent smoothing from PD tracking
- Lower policy frequency sufficient (50Hz)
- Better sim-to-real transfer (PD controllers absorb some modeling error)

**Residual actions**: `q_desired = q_default + k_action * a_t`, where a_t is the policy output scaled by a gain factor (typically 0.25-0.5). This constrains the policy to operate near the default standing pose.

**Direct torque**: Policy outputs motor torques directly. Requires higher control frequency (200-1000Hz), more prone to jitter, but allows finer control. Less common for locomotion.

**Structured actions**: Task-space foot positions (the policy specifies where each foot should go, and inverse kinematics computes joint angles), CPG parameters (amplitude, frequency, phase -- the policy modulates the rhythm generator), or residuals on top of a reference trajectory (the policy corrects a baseline motion plan). These structured action spaces inject domain knowledge into the learning process, reducing the search space at the cost of limiting the behaviors the policy can express.

The choice of action space significantly affects sim-to-real transfer. Position control with PD tracking naturally absorbs high-frequency modeling errors because the PD controller acts as a low-pass filter. Torque control faithfully reproduces the policy's intent but also faithfully reproduces any simulation-reality mismatch. For this reason, the Ha et al. (2025) survey confirms that "most researchers use desired joint positions (residuals) as the action space and then calculate the torque through a PD controller to control the robot locomotion."

Action smoothing is critical for real-world deployment. Without smoothing, RL policies frequently develop jittery behaviors where consecutive actions differ significantly, producing high-frequency torque oscillations that stress actuators and waste energy. Common smoothing approaches include exponential moving average filtering (action_t = alpha * raw_action_t + (1-alpha) * action_{t-1}), action rate penalties in the reward function, and the recently proposed Lipschitz-constrained policies (Chen et al., 2024, IROS 2025). The Lipschitz constraint bounds the sensitivity of the policy network's output to changes in its input, enforced via a gradient penalty during training. This is differentiable and doesn't require manual tuning of filter coefficients, making it particularly attractive for HDR optimization.

---

## 7. Sim-to-Real Transfer

### The Sim-to-Real Gap

The sim-to-real gap refers to the performance difference between a policy's behavior in simulation and its behavior on a real robot. Even with high-fidelity physics engines, simulation inevitably abstracts away aspects of reality that affect control performance. Closing this gap is the central challenge of simulation-based robot learning, and the approaches to addressing it constitute one of the most active research areas in robotics. The two dominant paradigms are domain randomization (making the policy robust to a range of conditions) and system identification (making the simulation match reality as closely as possible). Most practical systems use both.

### Domain Randomization

Domain randomization (Tobin et al., 2017) was originally proposed for visual sim-to-real transfer, randomizing rendering parameters (textures, lighting, camera poses) to make object detectors transfer from simulation to reality. The approach was quickly extended to dynamics randomization for control (Peng et al., 2018), randomizing physical parameters like mass, friction, and motor dynamics. By training with randomized simulation parameters, the policy learns to be robust to the range of conditions it might encounter in the real world. The fundamental assumption is that if the policy performs well across a sufficiently wide range of simulated conditions, the real world will fall within that range.

**Parameters commonly randomized for locomotion**:

| Parameter | Typical Range | Effect |
|-----------|---------------|--------|
| Ground friction | 0.3 - 2.0 | Slip resistance |
| Base mass | +/- 20-30% | Payload variation |
| Link CoM offset | +/- 2-5cm | Manufacturing tolerance |
| Motor strength | 80-120% | Actuator variation |
| PD gains | +/- 20% | Controller uncertainty |
| Joint offset | +/- 0.05 rad | Calibration error |
| Sensor noise | Gaussian, sigma varies | Measurement uncertainty |
| Action delay | 0-40ms | Communication latency |
| External pushes | 0-50N, random timing | Disturbance robustness |
| Terrain friction | 0.5 - 1.5 | Surface variation |

A critical challenge in domain randomization is setting appropriate ranges. The Evaluating DR in DRL Locomotion study (2023) systematically demonstrates that policy training is highly sensitive to randomization ranges: too-wide ranges make the task impossible to learn (the policy must be good everywhere, including extreme conditions), while too-narrow ranges don't cover the conditions encountered in reality (the policy transfers poorly). This sensitivity makes DR range optimization a prime candidate for HDR.

**Curriculum domain randomization** starts with narrow ranges and progressively widens them as the policy improves, preventing early learning collapse while ultimately achieving broad robustness. The intuition is that the policy should first learn the basic skill under nominal conditions, then gradually learn to handle perturbations. TransCurriculum (2026) extends this idea to a multi-dimensional curriculum, simultaneously adapting along three axes: velocity command targets, terrain difficulty, and domain randomization parameters (friction and payload mass). A transformer model predicts appropriate difficulty levels based on the agent's current performance, enabling automatic, data-driven curriculum generation without manual scheduling.

DrEureka (2024) introduced the concept of Reward-Aware Physics Priors (RAPP) for domain randomization, where the trained policy is evaluated on various perturbed simulation dynamics to determine which parameters most affect performance. This creates a data-driven prior over the DR parameter space, which an LLM then uses to generate appropriate randomization distributions. This approach grounds the often arbitrary choice of DR ranges in empirical sensitivity analysis.

### System Identification

Instead of or in addition to domain randomization, system identification matches simulator parameters to the real robot:
- **Offline SysID**: Measure motor response curves, friction coefficients, inertial properties
- **Online adaptation**: Use observation history to implicitly identify system parameters during deployment (e.g., the RNN hidden state in teacher-student frameworks encodes environmental adaptation)
- **PACE** (ETH RSL): Combines data-driven system identification with evolutionary optimization for accurate actuator modeling

### What Causes the Sim-to-Real Gap

The primary sources of sim-to-real discrepancy are:
1. **Contact modeling**: Simulation uses simplified contact models (point contacts, uniform friction) vs. real deformable surfaces
2. **Actuator dynamics**: Motor bandwidth, thermal effects, gear backlash are hard to model perfectly
3. **Sensor noise and latency**: Real IMUs, encoders have noise characteristics different from Gaussian
4. **Unmodeled dynamics**: Cable forces, body flexibility, wind
5. **State estimation**: In simulation the state is perfect; on real robots it must be estimated

### Success Stories and Failure Analysis

Successful sim-to-real transfer has been demonstrated at increasing levels of complexity:

- **Zero-shot transfer for flat-terrain quadruped walking** is now routine across multiple platforms (Unitree Go1/Go2, ANYmal, MIT Mini Cheetah, Boston Dynamics Spot). These robots walk reliably on flat indoor surfaces and paved outdoor terrain using policies trained entirely in simulation with standard domain randomization. Training typically takes 5-20 minutes on a consumer GPU.
- **Perceptive locomotion on rough terrain** transfers with careful teacher-student distillation. Wild ANYmal (Miki et al., 2022) completed a 1-hour Alpine hike, and ANYmal Parkour (Hoeller et al., 2024) demonstrated climbing, jumping, and crawling through obstacle courses. These require significantly more sophisticated training (privileged teacher with terrain information, student with onboard sensing only).
- **Humanoid walking** transfers with light domain randomization. The Berkeley Humanoid (2024) demonstrated outdoor walking on diverse surfaces (grass, sidewalks, trails, asphalt) using simple PPO without teacher-student distillation. Digit (Agility Robotics) operates commercially in warehouses with RL-trained whole-body control.
- **Real-world learning without simulation** is also possible: Smith et al. (2023) demonstrated learning quadruped walking in 20 minutes directly on hardware using SAC with careful algorithm implementation, bypassing the sim-to-real gap entirely.
- **GROQLoco** (2025) achieved 85% success rate on rubble terrain with a single generalist locomotion policy capable of handling various quadrupedal robots, demonstrating that domain randomization can generalize across robot platforms, not just environmental conditions.

Common failure modes include: policies that exploit simulation artifacts (e.g., unrealistic ground friction allowing impossible maneuvers), policies that rely on precise timing that real communication latency disrupts, policies that demand motor performance exceeding real actuator capabilities, and policies that fail on terrain textures not represented in the training heightmap curriculum.

The emerging "sim-to-real-to-sim" paradigm (He, CMU, 2025) uses real-world deployment data to update the simulation environment, creating a continuous improvement cycle. Initial policies are trained in simulation and deployed on the real robot, where performance data is collected. This data is used to refine the simulation parameters (system identification) and DR ranges, and a new policy is trained in the updated simulation. This iterative process progressively closes the sim-to-real gap and is philosophically aligned with HDR's iterative optimization approach.

---

## 8. Morphology Optimization

### Co-Design of Body and Controller

Morphology optimization jointly optimizes the robot's physical design (link lengths, masses, joint placement) alongside its controller. This is a natural fit for HDR methodology since both body and policy are parameterizable, and the evaluation function (simulated locomotion performance) can assess any body-controller combination. The fundamental insight is that body design and control policy are deeply coupled: the optimal body depends on the control algorithm, and the optimal controller depends on the body. Optimizing either in isolation produces suboptimal results.

The scalable co-optimization framework (Cheney et al., 2018) formalized this problem, showing that in populations of embodied machines, morphological and behavioral evolution are co-dependent and must be addressed jointly. The key metric is task performance (e.g., forward velocity, energy efficiency, terrain traversal capability) as a function of both body parameters and controller parameters.

### Approaches

**Evolutionary methods** have the longest history, with the morphology encoded in a genome and controllers co-evolved or trained independently. A key challenge is the "morphology-control coupling" problem: changing the body invalidates the controller, causing fitness to drop before the controller can readapt. Solutions include morphological innovation protection (temporarily relaxing selection pressure after body changes).

**Differentiable simulation** enables gradient-based morphology optimization. JAXsim provides physically consistent gradients with respect to kinematic and dynamic parameters. Recent work on "Evolution and Learning in Differentiable Robots" (RSS 2024) shows that differentiable simulation can efficiently optimize neural controllers for large morphology populations.

**Hybrid approaches**: DiffuseBot (NeurIPS 2023) uses diffusion models to propose diverse morphologies while exploiting gradient-based optimization for controller tuning. Stackelberg Proximal Policy Optimization (2026) frames co-design as a Stackelberg game between morphology (leader) and controller (follower).

**Accelerated co-design**: Morphological pretraining (2025) learns a universal, morphology-agnostic controller that can be rapidly adapted to new body designs via gradient-based fine-tuning through differentiable simulation, dramatically reducing the per-design training cost.

### Design Parameters for HDR

In a locomotion HDR loop, morphology parameters could include:
- Link lengths (thigh, shin, foot) -- directly affects stride length, workspace, and moment of inertia
- Link masses and inertias -- affects dynamic response, energy consumption, and ground reaction forces
- Joint range of motion limits -- determines the envelope of achievable postures and gaits
- Joint stiffness/damping (PD gains) -- affects compliance, response speed, and energy dissipation
- Foot geometry (size, shape) -- affects contact area, stability, and terrain interaction
- Actuator placement and gear ratios -- determines the available torque-speed tradeoff

The challenge is that morphology changes invalidate the trained controller. Cheney et al. (2018) identified this as the "morphological innovation protection" problem: when a body parameter changes, the controller trained for the old body suddenly underperforms, and naive optimization would discard the new body before the controller has time to readapt. Solutions include temporarily reducing selection pressure after body changes, warm-starting controllers from related morphologies, and the morphological pretraining approach (2025) which learns a universal, morphology-agnostic controller that can be rapidly fine-tuned for any body via gradient descent through differentiable simulation.

For HDR specifically, the recommendation is to iterate on morphology parameters infrequently (every 5-10 HDR iterations) with full controller retraining between morphology changes, treating morphology as a slow outer loop and controller optimization as a fast inner loop. The Stackelberg PPO framework (2026) formalizes this as a bilevel optimization: the morphology is the "leader" that commits first, and the controller is the "follower" that best-responds to the chosen morphology.

---

## 9. State of the Art

### Maturity Levels of Locomotion Tasks

The field has reached different levels of maturity across locomotion tasks. Understanding this landscape is essential for identifying where HDR can contribute most effectively.

**Solved (reliable, reproducible, commercially deployable)**:
- **Flat terrain quadruped walking/trotting**: Routinely trained in minutes on consumer GPUs, transfers zero-shot to real robots (Unitree Go1/Go2, ANYmal). Performance metrics: 1-2 m/s forward velocity, precise velocity tracking (<0.1 m/s error), 100% survival rate on flat ground. This is now a commodity capability.
- **Basic quadruped rough terrain**: With curriculum learning and domain randomization, quadrupeds can navigate stairs, slopes, gravel, and uneven ground with >90% success rate. Training time: 15-30 minutes.
- **Basic humanoid walking**: Achievable on multiple platforms (Unitree H1/G1, Berkeley Humanoid, Digit, Booster T1). Flat-ground walking at 0.5-1.5 m/s with reasonable robustness to small perturbations. Training time: 30-90 minutes.
- **Velocity tracking**: Precise command following for forward (vx), lateral (vy), and turning (wz) commands is standard functionality.

**Active frontier (demonstrated but not yet robust/general)**:
These are the areas where HDR optimization can have the greatest impact by systematically improving performance through design variable tuning.

### Current Frontiers

**Quadruped Parkour** (Hoeller et al., 2024): ANYmal navigates obstacle courses including jumps, climbs, and crawls at 2 m/s, decomposed into perception + skills + navigation modules.

**Humanoid Running and Jumping** (Cassie, Berkeley): 400m dash, standing long jumps, high jumps -- all transferred from simulation to the real Cassie robot.

**Whole-Body Loco-Manipulation** (2025-2026): Simultaneously walking and manipulating objects. WholeBodyVLA (ICLR 2026) achieves unified humanoid loco-manipulation, outperforming baselines by 21.3%. HWC-Loco reformulates humanoid control as robust optimization for safety-critical recovery.

**Multi-Skill Generalist Policies**: MOVE (2024) integrates leaping, crawling, climbing, and walking into a single network using pseudo-siamese architecture. Walk These Ways (Margolis & Agrawal, 2023) encodes a structured family of locomotion strategies with real-time switchable gaits.

**Vision-Based Locomotion**: MuJoCo Playground integrates the Madrona batch GPU renderer for end-to-end vision policy training on a single GPU, eliminating teacher-student for manipulation tasks.

**LLM-Guided Design**: Eureka and DrEureka automate reward design and domain randomization using large language models, achieving human-competitive or better results. This represents a meta-level automation of the design process itself.

**Rapid Off-Policy Training**: FastSAC and FastTD3 (Seo et al., 2024) challenge PPO's dominance by demonstrating that properly parallelized off-policy methods can train humanoid locomotion in 15 minutes on a single RTX 4090. This could fundamentally change the economics of HDR by reducing per-iteration evaluation cost.

**Imitation Learning Integration**: The shift from pure reward engineering toward motion-conditioned learning (AMP, DeepMimic-style approaches) is accelerating. The 2025 imitation learning survey catalogs 35 pivotal works showing that imitation learning has "fundamentally transformed legged robot locomotion, removing dependence on hand-engineered reward functions."

**Multi-Embodiment Policies**: URMA (One Policy to Run Them All, 2024) and related work demonstrate that a single neural network can learn locomotion across multiple robot morphologies using multi-task RL. This has implications for HDR: a universal policy could enable morphology optimization without full retraining.

### Key Research Groups

- **ETH Zurich RSL** (Marco Hutter): ANYmal, legged_gym, Wild ANYmal, ANYmal Parkour
- **UC Berkeley** (Pieter Abbeel, Sergey Levine, Koushil Sreenath): Cassie, Berkeley Humanoid, AMP, DeepMimic
- **MIT CSAIL** (Pulkit Agrawal): Mini Cheetah rapid locomotion, Walk These Ways
- **Google DeepMind**: MuJoCo, MJX, MuJoCo Playground, Brax
- **NVIDIA**: Isaac Gym/Lab/Sim, MuJoCo Warp, Newton
- **CMU**: Humanoid control, sim-to-real transfer (Tairan He)
- **Stanford/Caltech**: Optimal control, humanoid push recovery

---

## 10. Open Challenges

### Sample Efficiency

Despite massive parallelism reducing wall-clock time, the total number of environment interactions required remains enormous (~100M-1B steps). A single locomotion training run with 4096 environments for 20 minutes at 50Hz policy frequency generates approximately 250 million transitions. Model-based methods offer 10x+ sample efficiency gains by learning a dynamics model and planning through it, but struggle with the discontinuous contact dynamics inherent in locomotion. The learned world model cannot easily represent the discrete contact mode switches (foot touch-down, foot lift-off) that are fundamental to walking. Hybrid approaches combining learned world models with model-free RL represent a promising direction, and TWIST (2023) demonstrates that teacher-student world model distillation can efficiently transfer knowledge from simulation to reality. For HDR specifically, sample efficiency is critical because each HDR iteration requires a complete training run. Reducing per-iteration cost from 20 minutes to 5 minutes would quadruple the number of design points that can be explored in a given wall-clock budget.

### Generalization Across Terrains

Current policies are trained on procedurally generated terrains (stairs, slopes, rough ground) but can fail on out-of-distribution surfaces (ice, mud, deep snow, deformable terrain). The gap between the procedural terrain generation used in simulation (typically heightfield-based with parameterized roughness, step heights, and slopes) and real-world terrain diversity (which includes deformable substrates, loose rubble, vegetation, and wet surfaces) remains significant. GROQLoco (2025) achieves 85% success rate on rubble with a generalist policy, but this required careful multi-terrain training. Learning Terrain-Specialized Policies (2025) takes the alternative approach of training separate policies for different terrain types with a switching mechanism, achieving higher per-terrain performance at the cost of requiring terrain classification. The optimal approach for HDR may be to optimize a single policy's terrain generalization through careful curriculum and domain randomization tuning.

### Multi-Skill Policies

Training a single policy that can seamlessly walk, run, jump, climb, crawl, and recover from falls remains challenging. Each skill requires different coordination patterns, and the reward function must balance multiple competing objectives. Current solutions include: skill libraries with switching logic (ANYmal Parkour), multiplicity-of-behavior approaches encoding diverse strategies in a single policy (Walk These Ways), gait-conditioned policies with explicit gait encoding (gait-conditioned RL, 2025), and pseudo-siamese architectures combining supervised and contrastive learning (MOVE, 2024). The fundamental challenge is that the policy must learn discontinuous behavior boundaries -- the transition from walking to jumping requires a qualitative change in control strategy, not just a smooth interpolation. HDR can contribute by optimizing the reward function to encourage smooth skill transitions and by tuning the gait conditioning parameters.

### Long-Horizon Planning

RL excels at reactive control (responding to the current state within milliseconds) but struggles with long-horizon planning (navigate through a building, plan a route across varied terrain, sequence multiple manipulation actions). The temporal credit assignment problem becomes severe over horizons of thousands of timesteps. Hierarchical approaches decomposing planning (high-level path selection, operating at ~1Hz) from control (low-level motor commands, operating at ~50Hz) are the current solution, but the interface between levels is often brittle. Recent integration of foundation models (LLMs and VLMs) for high-level planning with RL for low-level execution (WholeBodyVLA, 2026) represents a promising direction, but these systems are still in early stages. For HDR, long-horizon planning is primarily relevant when the evaluation function includes multi-step navigation tasks rather than steady-state locomotion.

### Real-Time Adaptation

Adapting to unexpected changes (broken actuator, sudden load change, novel terrain) in real-time requires fast online system identification or meta-learning. Current approaches rely on implicit adaptation through RNN hidden states -- the recurrent network's internal state encodes an implicit estimate of environmental parameters that evolves as new observations arrive. The dual-history architecture (Li et al., 2024, Cassie) separates short-term (5 steps for fast reflexes) from long-term (50 steps for slow adaptation) memory, providing different timescales of adaptation. Explicit system identification approaches (PACE, 2024; SPI-Active, 2025) measure physical parameters online and adjust simulation or control accordingly. The "Dynamics as Prompts" approach (2024) uses in-context learning with transformers to perform real-time system identification without iterative optimization, treating each new dynamics observation as a "prompt" that conditions the policy. HDR could optimize the history encoding architecture and timescales to improve adaptation speed.

### Hardware-Aware Optimization

Policies trained in simulation often demand motor performance that damages hardware. Common issues include high-frequency oscillations (jitter) that cause motor overheating, peak torque demands that exceed actuator limits during transients, and rapid direction changes that stress gears and bearings. Lipschitz-constrained policies (Chen et al., 2024) address jitter by bounding the policy's output sensitivity, and spectral normalization (2025) provides an alternative implementation. However, comprehensive hardware-aware training that incorporates thermal models (preventing motor overheating during sustained operation), gear wear models (minimizing mechanical wear through smooth torque profiles), and energy budgets (maximizing operational time on battery) is largely underexplored. Fault-tolerant locomotion (AcL, 2025) addresses the related challenge of maintaining locomotion when individual motors fail, achieving robust walking despite actuator faults. For HDR, hardware-aware constraints should be encoded as additional reward terms or hard constraints on the policy output.

### Energy Efficiency

Current learned locomotion policies have Cost of Transport 3-5x higher than biological counterparts (robot CoT ~0.7-2.0 vs human CoT ~0.2, horse CoT ~0.2). Achieving energy-optimal gaits through learned locomotion -- matching the natural speed-gait relationships that animals exploit -- is an important practical challenge for battery-powered mobile robots. The energy efficiency principles survey (2018) identifies that optimal gait selection (walk at slow speeds, trot at moderate, gallop at high) can save 7-21% energy compared to using a single gait. Recent work on adaptive energy regularization (ICRA 2025) implements speed-dependent gait switching in RL, and multi-gait CoT minimization (2025) demonstrates robust multi-gait locomotion with minimized transport cost. Impact mitigation rewards (2025) specifically target the energy loss at foot impact, which is a major contributor to locomotion inefficiency. For HDR, energy efficiency is a natural secondary objective that can be optimized alongside task performance through reward weight tuning.

### Foundation Models for Locomotion

Can a single foundation model control any legged robot on any terrain? URMA (One Policy to Run Them All, 2024) demonstrates multi-embodiment locomotion control with a single neural network, and X-Loco (2026) pursues generalist humanoid locomotion through synergetic policy distillation. The vision is a pre-trained locomotion foundation model that can be quickly fine-tuned for any specific robot and task, analogous to how language models are pre-trained then fine-tuned. The deep RL survey (2025) notes that "Foundation Models such as Large Language Models and Vision Language Models present a transformative opportunity for bipedal locomotion, with their reasoning capabilities enabling sophisticated high-level task planning and novel solutions for automated reward design." For HDR, foundation model integration is a longer-term opportunity: a pre-trained locomotion model could serve as the starting point for HDR optimization, reducing the search space to fine-tuning a smaller number of adaptation parameters.

### Safety and Robustness

Ensuring that a learned policy never catastrophically fails is critical for real-world deployment, especially in environments where falls can damage expensive hardware or endanger nearby humans. Fall recovery has improved significantly: HiFAR (2025) achieves 100% recovery rate across randomized initial poses through multi-stage curriculum learning, and balance-informed RL (2026) embeds classical stability metrics (capture point, center-of-mass state, whole-body momentum) as privileged critic inputs. HWC-Loco (2025) reformulates locomotion policy learning as a robust optimization problem, explicitly learning recovery from safety-critical scenarios including ankle/hip strategies for small disturbances, corrective stepping for large pushes, and compliant falling with multi-contact stand-up using hands, elbows, and knees. SAC-Loco (2025) enables compliant locomotion for safe interaction with humans and environments. Despite these advances, formal safety guarantees for neural network policies remain an open challenge -- current verification methods do not scale to the size and complexity of locomotion control networks. For HDR, safety can be incorporated as a constraint (minimum survival rate on test scenarios) rather than optimized directly.

### Sim-to-Real for Contact-Rich Tasks

While flat-ground locomotion transfers well, contact-rich scenarios (climbing, manipulation while walking, interaction with deformable objects) have much larger sim-to-real gaps due to the difficulty of modeling complex contact phenomena. Simulation engines use simplified point contact models that fail to capture the complexity of real-world interactions, particularly patch contacts (distributed contact over foot surfaces), deformable terrain (sand, mud, grass), and multi-body contact chains (climbing over irregular objects). The humanoid locomotion survey (2025) identifies contact modeling limitations as a critical bottleneck for advancing loco-manipulation capabilities.

### Connections to HDR Methodology

The landscape of robot locomotion optimization maps naturally onto the HDR framework. The evaluation function is the physics simulation itself -- given a complete configuration (reward weights, observation space, action parameterization, network architecture, training hyperparameters, domain randomization settings, and optionally morphology parameters), we run RL training in a GPU-accelerated simulator and evaluate the resulting policy on held-out test scenarios. The HDR loop iterates on the design variables documented in design_variables.md, using the research hypotheses in research_queue.md to guide exploration.

The key advantage of HDR for locomotion is that the evaluation function is cheap (minutes, not hours) thanks to GPU-accelerated simulation, yet the design space is enormous (~60+ continuous variables, ~12 categorical choices). Human experts have developed good intuitions for individual design choices (see knowledge_base.md), but the interaction effects between variables are poorly understood and hard to predict. Systematic HDR exploration can discover configurations that human designers would not consider, particularly non-obvious combinations of reward weights, domain randomization ranges, and training hyperparameters.

The most promising HDR targets, based on this review, are: (1) reward weight optimization (highest impact, continuous variables, well-defined evaluation), (2) domain randomization range optimization (critical for transfer, directly impacts real-world performance), (3) curriculum schedule design (affects training stability and final performance), and (4) network architecture search (moderate impact but potentially dramatic improvements in specific cases). Morphology co-optimization is a compelling but harder target that should be attempted only after the policy optimization loop is well-characterized.
