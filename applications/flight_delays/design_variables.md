# Feature Candidates — Flight Delay Propagation

## Domain Quantity → Computable Proxy Mapping

### 1. Aircraft Rotation Chain (THE Primary Mechanism)
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Previous flight delay | `prev_leg_arr_delay` (minutes) | BTS tail_num + timestamps | Aircraft arriving late from prior leg cannot depart on time for next leg |
| Late aircraft delay code | `prev_leg_late_aircraft` (minutes) | BTS LATE_AIRCRAFT_DELAY column shifted by tail rotation | BTS-reported propagated delay from prior flight |
| Rotation chain position | `rotation_position` (1st, 2nd, 3rd... leg of day) | Cumulative count within (date, tail_num) group | Later legs accumulate more propagated delay; delays compound |
| Cascade depth | How many legs back does the root-cause originate | Recursive lookup through tail rotation chain | Deep cascades indicate systemic vs isolated delay |
| Turnaround time buffer | `schedule_buffer_min` (scheduled - minimum for distance bucket) | BTS scheduled elapsed time minus distance-bucket minimum | More buffer absorbs more of incoming delay |

### 2. Airport Congestion
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Departure congestion | `origin_hour_flights` (flights departing within +/- 1 hr) | Count from BTS data | More flights competing for runway/taxiway/gate capacity |
| Arrival congestion at dest | `dest_hour_flights` (flights arriving in estimated arrival hour) | Count from BTS data | Metered arrivals at congested destinations add holding delay |
| Relative congestion | `congestion_ratio` (flights / median for this hour) | origin_hour_flights / median by hour | Captures unusual crowding vs typical baseline |
| Hub status | `origin_is_hub`, `dest_is_hub` (binary) | HUB_AIRPORTS lookup | Hub airports have more connections, more congestion, more propagation |

### 3. Carrier Operations
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Schedule buffer strategy | `carrier_buffer_factor` (continuous) | Derived from carrier identity | Southwest pads more, Spirit pads less; buffer absorbs delay |
| Carrier-buffer interaction | `prev_leg_delay_x_buffer` | prev_leg_arr_delay * carrier_buffer_factor | Tight-buffer carriers propagate more of incoming delay |
| Regional carrier | `is_regional_carrier` (binary for MQ, OO, YX) | Carrier code lookup | Regional carriers have tighter operations, smaller aircraft |
| Hub-to-hub route | `is_hub_to_hub` (binary) | Both origin and dest in HUB_AIRPORTS | Highest-traffic corridors with most connections at risk |

### 4. Temporal Patterns
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Time of day | `dep_hour_sin`, `dep_hour_cos` (cyclic) | BTS CRS_DEP_TIME | Delays accumulate through the day; morning clean start, afternoon peak |
| Morning flight | `morning_flight` (binary, 06:00-09:00) | Departure hour threshold | First-wave flights have less propagated delay (rotation starts fresh) |
| Evening flight | `evening_flight` (binary, 18:00-22:00) | Departure hour threshold | End-of-day cascade peak; delays die at overnight reset |
| Day of week | `dow_sin`, `dow_cos` (cyclic) | BTS FL_DATE | Monday/Friday worse (business travel); weekends lighter |
| Season/month | `month_sin`, `month_cos` (cyclic) | BTS FL_DATE | Winter weather, summer convection, holiday peaks |
| Weekend flag | `is_weekend` (binary) | Day of week >= 5 | Weekend traffic ~80% of weekday; fewer connections |

### 5. Route Characteristics
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Route distance | `distance` (miles) | BTS DISTANCE | Long-haul flights have more en-route buffer to absorb delay |
| Scheduled flight time | `sched_elapsed_min` (minutes) | BTS CRS_ELAPSED_TIME | Longer flights have proportionally more slack |
| Log previous delay | `log_prev_delay` = log1p(prev_leg_arr_delay) | Log transform | Diminishing marginal impact: 10->20 min matters more than 110->120 |

### 6. Weather (Potential Phase 2 Enhancement)
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Airport weather | Ceiling, visibility, wind, precipitation | NOAA METAR/ISD data | Low ceiling/visibility triggers IFR, reduces capacity |
| Weather persistence | Same-hour weather vs 2-hours-later | METAR time series | Persistent storms cause sustained delay; passing storms recover |
| Convective weather | Thunderstorm indicators | METAR weather codes | Summer convection closes runways completely |

### 7. Network Centrality (Potential Phase 2 Enhancement)
| Domain quantity | Computable proxy | Source | Physics |
|---|---|---|---|
| Airport degree | Number of routes from airport | BTS route data | More connected airports propagate to more destinations |
| Betweenness centrality | Fraction of shortest paths through airport | Network computation | High-betweenness airports are critical bottlenecks |
