# Research Queue — Flight Delay Propagation

## Format: ID | Status | Hypothesis | Prior (%) | Mechanism | Expected Delta

### Tail Number Rotation Chain (Flagship Theme)
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H001 | KEEP | Rotation position captures cascade depth | 65% | Later legs accumulate more delay | -0.35 MAE |
| H002 | KEEP | Previous leg late_aircraft code adds signal | 70% | Direct BTS propagation code | -0.28 MAE |
| H006 | KEEP | Prev delay x buffer interaction is key mechanism | 75% | Tight-buffer carriers propagate more | -0.85 MAE |
| H010 | KEEP | Log transform of previous delay | 60% | Diminishing marginal impact of large delays | -0.42 MAE |
| H031 | REVERT | Binary severe delay flag (>30 min) | 40% | Qualitatively different cascades | Near noise |
| H036 | REVERT | Quadratic previous delay | 35% | Disproportionate large-delay effect | Near noise |
| H041 | OPEN | Cascade depth: how many legs back is root cause? | 50% | Deep cascades may mean infrastructure issue | Moderate |
| H042 | OPEN | Time since last on-time arrival for this tail | 45% | Accumulated delay history beyond 1 leg | Small |
| H043 | OPEN | Previous leg departure delay (not just arrival) | 40% | Dep delay may differ from arr delay signal | Small |
| H044 | OPEN | Interaction: rotation_position x prev_delay | 55% | Later legs lose more recovery opportunity | Moderate |

### Airport Congestion
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H003 | KEEP | Destination congestion adds delay | 55% | Metered arrivals at busy airports | -0.15 MAE |
| H004 | KEEP | Destination hub flag | 45% | Hub destinations affect more connections | -0.12 MAE |
| H011 | KEEP | Congestion ratio (relative to typical) | 55% | Unusual crowding more informative than absolute | -0.14 MAE |
| H021 | REVERT | Same-origin previous-hour mean delay | 55% | Airport-level delay state | Leakage risk |
| H029 | REVERT | Origin airport degree centrality | 45% | More routes = more propagation potential | Redundant with hub |
| H045 | OPEN | Gate utilization proxy (flights/hour at origin) | 40% | Gate conflicts cause turnaround delays | Small |
| H046 | OPEN | Arrival rate at dest in 30-min window | 50% | Finer congestion granularity | Moderate |
| H047 | OPEN | Origin taxi-out proxy (recent departures count) | 45% | Taxi congestion adds departure delay | Small |

### Carrier Operations
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H005 | KEEP | Schedule buffer minutes | 60% | Padding absorbs incoming delay | -0.22 MAE |
| H007 | KEEP | Hub-to-hub route indicator | 50% | Highest-traffic corridors | -0.10 MAE |
| H012 | KEEP | Regional carrier flag | 45% | Tighter operations, less buffer | -0.11 MAE |
| H014 | REVERT | Carrier one-hot encoding (top 5) | 45% | Carrier-specific patterns | Redundant with buffer |
| H033 | REVERT | Carrier x prev_delay interaction | 40% | Carrier-specific propagation rates | Already in buffer factor |
| H048 | OPEN | Carrier market share at origin | 35% | Dominant carrier may control ground ops | Small |
| H049 | OPEN | Load factor proxy (flights/route/day) | 40% | Higher load = more passengers at risk | Small |
| H050 | OPEN | Codeshare flight indicator | 30% | Codeshares may have different buffer | Small |

### Temporal Patterns
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H008 | KEEP | Morning flight indicator (06:00-09:00) | 55% | First-wave clean start | -0.18 MAE |
| H009 | KEEP | Evening flight indicator (18:00-22:00) | 50% | End-of-day cascade peak | -0.08 MAE |
| H013 | REVERT | Holiday indicator | 40% | Higher load factors | Too sparse |
| H020 | REVERT | Minutes since midnight (continuous) | 35% | Continuous time | Redundant with sin/cos |
| H026 | REVERT | Day-of-week x prev_delay interaction | 40% | Weekday propagation differences | Tree captures implicitly |
| H051 | OPEN | Peak season indicator (Jun-Aug, Dec) | 40% | Seasonal congestion peaks | Small |
| H052 | OPEN | Day-of-week x congestion interaction | 35% | Monday congestion worse | Small |
| H053 | OPEN | Red-eye flight indicator (22:00-06:00) | 30% | Red-eye flights cross midnight boundary | Small |
| H054 | OPEN | Last flight of day flag | 45% | Last flights cannot propagate to next day | Moderate |

### Weather (Requires NOAA Data Join)
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H019 | REVERT | Previous leg weather delay code | 40% | Weather at hub persists | No additional signal |
| H055 | OPEN | Origin METAR ceiling < 1000 ft | 55% | IFR conditions reduce capacity | Moderate |
| H056 | OPEN | Destination METAR visibility < 3 mi | 50% | Low vis at dest causes holding | Moderate |
| H057 | OPEN | Origin wind speed > 20 kt | 45% | High winds reduce runway acceptance rate | Small |
| H058 | OPEN | Thunderstorm indicator (METAR TS code) | 50% | Convection closes airspace | Moderate |
| H059 | OPEN | Weather persistence (still bad 2h later?) | 55% | Persistent weather = sustained cascade | Moderate |
| H060 | OPEN | Temperature below freezing (de-icing) | 40% | De-icing adds 15-45 min to turnaround | Small |

### Route Characteristics
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H015 | REVERT | Distance squared | 30% | Nonlinear distance effect | No signal |
| H027 | REVERT | Month x distance interaction | 30% | Seasonal route-length effects | No signal |
| H034 | REVERT | Distance bucket categorical | 30% | Threshold effects | Redundant |
| H035 | REVERT | Hub-to-spoke/spoke-to-hub directional | 35% | Directional propagation | Near noise |
| H061 | OPEN | Distance-based buffer (long-haul has more) | 45% | Explicit distance-buffer interaction | Small |
| H062 | OPEN | Transcontinental flag (dist > 2000 mi) | 35% | Transcontinental flights differ structurally | Small |

### Network Science Features
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H063 | OPEN | Origin betweenness centrality | 45% | Critical network bottlenecks | Moderate |
| H064 | OPEN | Daily flight network PageRank | 40% | Importance in daily network | Small |
| H065 | OPEN | Connection count at origin (arriving within 90 min) | 50% | More connections = more propagation risk | Moderate |
| H066 | OPEN | Shortest path distance from origin to network periphery | 30% | Central airports vs edge airports | Small |

### Model/Training Improvements
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H016 | REVERT | n_estimators 300->500 | 25% | More trees | No improvement |
| H017 | REVERT | learning_rate 0.05->0.02 | 25% | Slower learning | Underfits |
| H018 | REVERT | max_depth 6->8 | 30% | Deeper trees | Overfits |
| H023 | REVERT | subsample 0.8->0.7 | 20% | Regularization | No effect |
| H024 | REVERT | colsample_bytree 0.8->0.6 | 20% | Regularization | Slightly worse |
| H025 | REVERT | min_child_weight 10->20 | 30% | Regularization | No effect |
| H032 | REVERT | Switch to LightGBM | 40% | Tournament runner-up | Marginal |
| H039 | REVERT | min_child_weight 10->5 | 25% | Less regularization | Overfits |
| H040 | REVERT | max_depth 6->5 | 30% | Less depth | Small regression |
| H067 | OPEN | Target transform: predict log(delay+15) | 35% | Compress right tail | Small |
| H068 | OPEN | Quantile regression instead of mean | 40% | Better for skewed delays | Moderate |
| H069 | OPEN | Two-stage: classifier (delayed?) then regressor (how much?) | 50% | Separate on-time vs delayed | Moderate |

### Cross-Domain and Creative
| ID | Status | Hypothesis | Prior | Mechanism | Expected |
|---|---|---|---|---|---|
| H070 | OPEN | Airport-specific propagation coefficient | 40% | Different airports absorb delay differently | Small |
| H071 | OPEN | Fleet age/type proxy from tail number prefix | 25% | Older aircraft may have more mechanical delays | Small |
| H072 | OPEN | Market concentration (HHI) at origin | 30% | Monopoly airports may have less congestion | Small |
| H073 | OPEN | Precipitation at connecting hub | 35% | Weather at hub affects inbound connecting flights | Moderate |
| H074 | OPEN | Time-of-year x carrier buffer interaction | 40% | Carriers may adjust buffers seasonally | Small |
| H075 | OPEN | Rolling 7-day delay rate at origin | 50% | Persistent infrastructure issues | Moderate (leakage risk) |
| H076 | OPEN | Number of cancelled flights at origin today | 45% | Cancellations free gates but strand passengers | Moderate |
| H077 | OPEN | Previous flight origin (where did the plane come from?) | 40% | Origin-of-origin weather/congestion | Small |

## Summary Statistics
- Total hypotheses: 77+
- Tested: 40 (H001-H040)
- Kept: 12
- Reverted: 25
- Skipped: 1
- Open: 37+
- Keep rate: 32%
