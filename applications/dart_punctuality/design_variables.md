# Design Variables — DART Punctuality Cascade Prediction

## Overview

The prediction target is binary: **bad_day** = 1 if afternoon (16:00-19:00) DART punctuality falls below 85% (>15% of services delayed more than 5 minutes). Features must be available by mid-morning to enable actionable prediction.

## Feature Categories

### 1. Temporal Features
| Variable | Formula | Justification |
|---|---|---|
| `dow_sin`, `dow_cos` | sin/cos encoding of day-of-week | Cyclic representation; Monday worst, weekends best |
| `month_sin`, `month_cos` | sin/cos encoding of month | Seasonal cycle; winter worse than summer |
| `is_weekend` | Binary (Sat/Sun) | Weekend service reduced, fewer passengers |
| `is_monday` | Binary | Monday consistently worst day for DART |
| `is_friday` | Binary | Friday variable; mixed commuter/leisure pattern |
| `year` | Integer | Secular trend capture |

### 2. Weather Features
| Variable | Source | Justification |
|---|---|---|
| `wind_speed_kmh` | Met Eireann forecast | Bray-Greystones speed restrictions at >50 km/h |
| `rainfall_mm` | Met Eireann forecast | Rail adhesion, signal failures, flooding |
| `temperature_c` | Met Eireann forecast | Frozen points, rail buckling (extreme heat) |
| `wind_dir_deg` | Met Eireann forecast | Easterly exposure on coastal section |
| `is_stormy` | wind > 60 km/h | Binary extreme weather flag |
| `is_frost` | temp < 0C | Binary frost flag for frozen points |
| `wind_above_50` | wind > 50 km/h | **HDR H001 KEEP** — speed restriction threshold |
| `rain_above_10` | rainfall > 10mm | **HDR H002 KEEP** — heavy rain threshold |
| `wind_dir_coastal_exposure` | cos(angle from east) | **HDR H008 KEEP** — easterly exposure Bray-Greystones |

### 3. Timetable Regime Features
| Variable | Formula | Justification |
|---|---|---|
| `post_timetable_change` | Binary (after Sep 2024) | Structural regime change; reduced buffer times |
| `post_change_x_wind` | post_change * wind_speed | **HDR H005 KEEP** — reduced buffers amplify weather sensitivity |

### 4. System State Features (Autocorrelation)
| Variable | Formula | Justification |
|---|---|---|
| `prev_day_punct` | Yesterday's punctuality | Autocorrelation; incomplete recovery carries over |
| `prev_day_bad` | Yesterday bad_day (binary) | Binary autocorrelation signal |
| `rolling_7d_punct` | Mean punct over previous 7 days | System health proxy |
| `rolling_7d_bad_count` | Sum of bad_day over previous 7 days | Cluster detection |
| `rolling_7d_bad_rate` | bad_count / 7 | **HDR H004 KEEP** — normalised system health |
| `rolling_3d_punct` | Mean punct over previous 3 days | **HDR H009 KEEP** — acute disruption memory |
| `morning_punct` | Morning (06-09) punctuality | **Key leading indicator** — morning cascade predicts afternoon |
| `morning_afternoon_gap` | morning_punct - afternoon_punct | **HDR H003 KEEP** — cascade magnitude |

### 5. Demand Proxy Features
| Variable | Formula | Justification |
|---|---|---|
| `is_school_term` | Binary | **HDR H006 KEEP** — school term = higher load = more sensitivity |
| `is_holiday` | Binary | Bank holidays = different demand (REVERTED — too sparse) |

### 6. Interaction Features
| Variable | Formula | Justification |
|---|---|---|
| `prev_day_bad_x_monday` | prev_day_bad * is_monday | **HDR H007 KEEP** — Monday after disrupted weekend |

## Feature Importance Ranking (from trained XGBoost model)

1. **post_timetable_change** (0.493) — Dominant predictor
2. **post_change_x_wind** (0.253) — Timetable-weather interaction
3. **morning_punct** (0.106) — Morning cascade indicator
4. **morning_afternoon_gap** (0.027) — Cascade magnitude
5. **is_friday** (0.014), **is_monday** (0.014) — Day-of-week effects
6. **rolling_7d_punct** (0.013) — System health
7. Remaining features contribute <1% each

## Key Insight

The feature importance confirms that the punctuality collapse is primarily structural (timetable change) amplified by weather. Morning punctuality is the strongest operational predictor — a bad morning strongly predicts a bad afternoon.
