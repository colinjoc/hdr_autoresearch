# Design Variables for HDR: Traffic Signal Timing Optimisation

## Overview

These are the variables that HDR will systematically iterate on. Each variable has a defined range, literature-informed defaults, and expected interactions with other variables.

---

## 1. Reward Function Components

The most impactful design variable. Literature shows minor weight changes produce dramatically different policies.

### 1.1 Reward Type
| Variable | Range | Default | Source |
|----------|-------|---------|--------|
| `reward_fn` | {diff-waiting-time, queue, pressure, average-speed, throughput, custom} | diff-waiting-time | sumo-rl default |

### 1.2 Composite Reward Weights
For custom multi-objective rewards: `R = w1*R_queue + w2*R_wait + w3*R_speed + w4*R_pressure + w5*R_emissions`

| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `w_queue` | [0.0, 1.0] | 0.3 | Negative queue length |
| `w_wait` | [0.0, 1.0] | 0.3 | Change in cumulative waiting time |
| `w_speed` | [0.0, 1.0] | 0.2 | Average speed of approaching vehicles |
| `w_pressure` | [0.0, 1.0] | 0.2 | Pressure = incoming - outgoing vehicles |
| `w_emissions` | [0.0, 0.5] | 0.0 | CO2/fuel from SUMO emission model |
| `w_throughput` | [0.0, 1.0] | 0.0 | Vehicles cleared per step |

**Key hypothesis:** Pressure-based reward is equivalent to optimising global travel time in multi-intersection scenarios (proven in literature), but composite rewards may outperform single-metric rewards under specific traffic patterns.

### 1.3 Reward Normalisation
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `reward_norm` | {none, z-score, min-max, per-lane} | none | Normalisation method |
| `reward_clip` | [-inf, inf] | [-10, 10] | Clip extreme values |
| `reward_discount` | [0.9, 0.999] | 0.99 | Discount factor gamma |

---

## 2. Phase Structure and Configuration

### 2.1 Phase Definition
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `num_phases` | {2, 4, 6, 8} | 4 | Number of green phases per cycle |
| `phase_type` | {standard, protected, protected-permissive, split-phasing} | standard | Phase movement type |
| `skip_phases` | {true, false} | false | Allow RL to skip low-demand phases |
| `phase_sequence` | {fixed, learned, NEMA-compatible} | fixed | Whether RL can reorder phases |

### 2.2 Timing Constraints
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `min_green` | [5, 15] seconds | 5 | Minimum green time (safety) |
| `max_green` | [30, 90] seconds | 60 | Maximum green time |
| `yellow_time` | [3, 5] seconds | 4 | Fixed yellow interval |
| `all_red_time` | [1, 3] seconds | 2 | All-red clearance interval |
| `pedestrian_phase` | [7, 30] seconds | 15 | Pedestrian crossing time |

---

## 3. Cycle Length and Decision Frequency

### 3.1 Cycle Parameters
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `delta_time` | [3, 15] seconds | 5 | RL decision interval |
| `target_cycle` | [30, 180] seconds | variable | Target cycle length (if enforced) |
| `cycle_enforcement` | {none, soft, hard} | none | Whether to constrain cycle length |

### 3.2 Action Space Design
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `action_type` | {next-phase, set-phase, phase-duration, adjust-all} | next-phase | How actions map to signal changes |
| `action_frequency` | {fixed-delta, variable, per-cycle} | fixed-delta | When decisions are made |

**Key hypothesis:** `delta_time` interacts strongly with cycle length. Too-frequent decisions (small delta_time) cause oscillation; too-infrequent decisions (large delta_time) miss demand changes.

---

## 4. Observation Space

### 4.1 Local Observations
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `obs_lane_density` | {true, false} | true | Normalised vehicle count per lane |
| `obs_lane_queue` | {true, false} | true | Normalised halting vehicles per lane |
| `obs_phase_onehot` | {true, false} | true | Current phase one-hot encoding |
| `obs_min_green_flag` | {true, false} | true | Whether min green has been served |
| `obs_avg_speed` | {true, false} | false | Average speed per lane |
| `obs_waiting_time` | {true, false} | false | Cumulative waiting time per lane |
| `obs_pressure` | {true, false} | false | Per-lane pressure |
| `obs_elapsed_phase` | {true, false} | false | Time since last phase change |
| `obs_time_of_day` | {true, false} | false | Hour of day encoding |
| `obs_demand_history` | {0, 5, 10, 20} steps | 0 | Historical demand window |

### 4.2 Neighbour Observations (multi-intersection)
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `obs_neighbour_queues` | {true, false} | false | Queue lengths at adjacent intersections |
| `obs_neighbour_phases` | {true, false} | false | Current phase at neighbours |
| `obs_neighbour_hops` | {0, 1, 2, 3} | 0 | How many hops of neighbourhood info |

### 4.3 Observation Encoding
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `obs_encoding` | {flat-vector, image, graph} | flat-vector | State representation format |
| `obs_normalisation` | {none, z-score, min-max} | min-max | Observation normalisation |
| `obs_history_length` | {1, 3, 5, 10} frames | 1 | Frame stacking |

**Key hypothesis:** Literature shows "expression is enough" -- simple but well-chosen features can match complex representations. The key question is which features carry signal for which traffic patterns.

---

## 5. Coordination Strategy (Multi-Intersection)

### 5.1 Agent Structure
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `coordination` | {independent, shared-reward, CTDE, centralised, hierarchical} | independent | Multi-agent paradigm |
| `parameter_sharing` | {none, full, partial} | none | Weight sharing across agents |
| `communication` | {none, message-passing, graph-attention, broadcast} | none | Inter-agent communication |

### 5.2 Coordination Parameters
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `neighbour_reward_weight` | [0.0, 1.0] | 0.0 | Weight on neighbour performance in reward |
| `global_reward_weight` | [0.0, 1.0] | 0.0 | Weight on network-wide metrics in reward |
| `coordination_radius` | {1, 2, 3, all} hops | 1 | Spatial extent of coordination |

### 5.3 Graph Structure (if using GNN)
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `graph_type` | {adjacency, distance-weighted, demand-weighted} | adjacency | How intersection graph is constructed |
| `gnn_layers` | {1, 2, 3} | 2 | GNN depth |
| `attention_heads` | {1, 2, 4, 8} | 4 | Number of attention heads in GAT |

---

## 6. Network Architecture (RL Agent)

### 6.1 Policy Network
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `algorithm` | {DQN, DDQN, Dueling-DQN, PPO, A2C, SAC} | DQN | RL algorithm |
| `hidden_layers` | {[64], [128,64], [256,128], [256,128,64]} | [128,64] | MLP hidden layer sizes |
| `activation` | {ReLU, ELU, Tanh} | ReLU | Activation function |
| `learning_rate` | [1e-5, 1e-2] | 1e-3 | Learning rate |
| `batch_size` | {32, 64, 128, 256} | 64 | Training batch size |
| `buffer_size` | [1e4, 1e6] | 1e5 | Replay buffer size (if applicable) |

### 6.2 Exploration
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `epsilon_start` | [0.5, 1.0] | 1.0 | Initial exploration rate |
| `epsilon_end` | [0.01, 0.1] | 0.05 | Final exploration rate |
| `epsilon_decay` | [1e3, 1e5] steps | 1e4 | Decay schedule |

### 6.3 Training Parameters
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `train_episodes` | [100, 10000] | 1000 | Number of training episodes |
| `episode_length` | [1000, 7200] seconds | 3600 | Simulation duration per episode |
| `eval_frequency` | [10, 100] episodes | 50 | How often to evaluate |
| `target_update` | [100, 10000] steps | 1000 | Target network update frequency |

---

## 7. Traffic Scenario Parameters

### 7.1 Demand Patterns
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `demand_level` | {low, medium, high, oversaturated} | medium | Overall traffic volume |
| `demand_pattern` | {uniform, peak-hour, time-varying, stochastic} | uniform | Temporal demand pattern |
| `turning_ratios` | {balanced, left-heavy, through-heavy} | balanced | Movement distribution |
| `demand_asymmetry` | [0.5, 2.0] | 1.0 | Ratio of major/minor road demand |

### 7.2 Network Topology
| Variable | Range | Default | Notes |
|----------|-------|---------|-------|
| `network` | {single-intersection, 2x2-grid, 4x4-grid, arterial, RESCO-Ingolstadt, RESCO-Cologne} | single-intersection | Network scenario |
| `intersection_type` | {4-way, 3-way, 5-way, mixed} | 4-way | Intersection geometry |

---

## Design Variable Interactions (Key Hypotheses)

1. **reward_fn x coordination:** Pressure-based rewards should excel in multi-intersection; queue-based in single
2. **delta_time x target_cycle:** Decision frequency must be compatible with realistic cycle lengths
3. **obs_neighbour_hops x coordination:** More neighbourhood info only helps with coordination
4. **algorithm x action_type:** PPO may handle continuous action spaces (phase-duration) better than DQN
5. **hidden_layers x network:** Larger networks need more model capacity
6. **demand_pattern x obs_history_length:** Time-varying demand benefits from temporal context
7. **phase_sequence x skip_phases:** Flexible phase ordering with skipping could reduce delay but may cause confusion

---

## Priority Ordering for HDR Exploration

**Phase 1 (highest impact, explore first):**
1. Reward function type and weights
2. Observation space components
3. RL algorithm selection

**Phase 2 (medium impact):**
4. Phase structure and timing constraints
5. Delta time / decision frequency
6. Network architecture (hidden layers, learning rate)

**Phase 3 (multi-intersection focus):**
7. Coordination strategy
8. Communication mechanism
9. Graph structure

**Phase 4 (robustness and transfer):**
10. Demand pattern variation
11. Network topology generalisation
12. Scenario-specific vs shared knowledge
