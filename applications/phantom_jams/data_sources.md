# Data Sources — Phantom Highway Traffic Jams

Phase 0 inventory of datasets, simulators, and benchmarks for studying
phantom traffic jams and their suppression by controlled vehicles.

All URLs verified 2026-04-09 unless noted.

--------------------------------------------------------------------------------

## 1. I-24 MOTION Dataset

| Field | Value |
|-------|-------|
| URL | https://i24motion.org/ |
| Owner | Vanderbilt University / TDOT |
| Testbed | 4 miles of Interstate 24 near Nashville, TN |
| Sensors | 276+ pole-mounted 4K cameras, computer-vision tracking |
| License | Free for research; requires account registration |
| Status | Active; "INCEPTION" v1.0.0 dataset released |

### Access

Registration required at https://i24motion.org/user/register — free accounts
are approved within one business day.  After approval, datasets are accessible
via the data portal.

### INCEPTION v1.0.0 Dataset

The initial public release, described in the system-level journal article
published in Transportation Research Part C (preprint linked on site).
Contains vehicle trajectories from the I-24 camera system.

- **Sampling rate**: 25 Hz (camera frame rate; trajectory interpolation may differ)
- **Coordinate system**: State Plane Tennessee (EPSG:2274), with mile-marker reference
- **Format**: Documentation at https://github.com/I24-MOTION/I24M_documentation;
  data files include a PDF spec (v1.x_I-24MOTION_data_documentation.pdf)
- **Columns**: vehicle ID, timestamp, position (x, y), speed, lane, vehicle class

### MegaVanderTest (MVT) — November 2022

The MVT was the landmark CIRCLES field experiment deploying 100 AVs on I-24.
As of 2026-04-09, MVT trajectory data is **not confirmed to be in the public
INCEPTION release**.  The INCEPTION dataset is described as the "initial"
release; MVT data may be in a separate named release or require consortium
access.  Check the data calendar at https://i24motion.org/data for updates.

### Limitations

- TLS certificate issue (curl/fetch fails without `-k`; browser access works)
- Account approval delay (up to one business day)
- Not all I-24 MOTION data is necessarily trajectory-level; some may be
  aggregated flow/speed

--------------------------------------------------------------------------------

## 2. NGSIM Trajectories (US 101 and I-80)

| Field | Value |
|-------|-------|
| URL | https://ops.fhwa.dot.gov/trafficanalysistools/ngsim.htm |
| Data portal | https://data.transportation.gov/ (search "NGSIM") |
| Owner | FHWA (Federal Highway Administration) |
| License | Public domain (US government work) |
| Datasets | US Highway 101 (Los Angeles), Interstate 80 (Emeryville), Lankershim Blvd |
| Sampling rate | 10 Hz (0.1 s resolution) |
| Time periods | 45-minute windows, multiple time-of-day segments |

### Access

Freely downloadable from data.transportation.gov without registration.
Search for "Next Generation Simulation NGSIM Vehicle Trajectories".

### Known Quality Issues

Coifman & Li (2017), "A critical evaluation of the Next Generation Simulation
(NGSIM) vehicle trajectory dataset", Transportation Research Part B 105,
documented systematic errors:
- Position noise leading to physically impossible accelerations (> 10 m/s^2)
- Lane-change mis-assignment
- Vehicle length inconsistencies

Several "cleaned" versions exist (e.g., Montanino & Punzo 2015 reconstruction).
Despite these issues, NGSIM remains the most-cited car-following dataset.

### Columns

vehicle_id, frame_id, total_frames, global_time, local_x, local_y,
global_x, global_y, v_length, v_width, v_class, v_vel, v_acc,
lane_id, preceding, following, space_hdwy, time_hdwy

--------------------------------------------------------------------------------

## 3. highD Dataset

| Field | Value |
|-------|-------|
| URL | https://levelxdata.com/highd-dataset/ |
| Owner | levelXdata (formerly Institut fuer Kraftfahrzeuge, RWTH Aachen) |
| License | Academic use only; requires application |
| Road sections | 6 locations on German autobahns (A1, A3, A4, A44, A61) |
| Vehicles | 110,000+ vehicles |
| Total time | 16.5 hours of recording |
| Sampling rate | 25 Hz |
| Method | Drone-based overhead recording |

### Access

Requires application at https://levelxdata.com/highd-dataset/ — academic
affiliation typically required.  Free for non-commercial research.  The
application asks for name, institution, and intended use.

### Why Relevant

High-quality, high-frequency trajectory data on highways.  Useful for:
- Calibrating car-following models (IDM parameter fitting)
- Validating wave characteristics against German autobahn conditions
- Comparing drone-based vs. camera-based trajectory quality

Related datasets from the same group: inD (intersections), rounD (roundabouts),
exiD (highway entries/exits), uniD (university campus).

--------------------------------------------------------------------------------

## 4. Sugiyama 2008 Ring-Road Experiment

| Field | Value |
|-------|-------|
| Paper | Sugiyama et al. (2008), "Traffic jams without bottlenecks", New Journal of Physics 10, 033001 |
| DOI | 10.1088/1367-2630/10/3/033001 |
| Experiment | 22 vehicles on a 230-m circumference circular track |
| Key finding | Spontaneous stop-and-go waves emerge from uniform flow |
| Wave speed | ~20 km/h (~5.6 m/s) backward propagation |

### Data Availability

The original trajectory data from Sugiyama (2008) has **not been publicly
released** as a downloadable dataset.  The paper contains:
- Space-time diagrams (Figure 3) showing wave evolution
- Velocity time series for individual vehicles
- Measured wave propagation speed

No GitHub repository for the raw data was found (verified 2026-04-09).
The experiment has been reproduced computationally many times using IDM and
OVM (Optimal Velocity Model) with similar parameters.

### Reproduction Parameters

The standard computational reproduction uses:
- 22 vehicles, 230 m ring, vehicle length 4.5-5.0 m
- IDM with T reduced to ~1.0 s (or OVM with appropriate tau)
- Small perturbation to trigger the instability
- Wave develops within ~60 s, reaches steady oscillation by ~120 s

--------------------------------------------------------------------------------

## 5. Eclipse SUMO (Simulation of Urban Mobility)

| Field | Value |
|-------|-------|
| URL | https://www.eclipse.dev/sumo/ |
| Latest version | 1.26.0 (as of 2026-04-09 per website) |
| Installed version | 1.18.0 (on this system, via apt) |
| License | EPL-2.0 / GPL-2.0 dual license |
| Language | C++ core, Python API (TraCI / libsumo) |
| Install | `apt install sumo sumo-tools` (Ubuntu/Debian) or download from website |

### Python API

- **TraCI** (Traffic Control Interface): Pure-Python, connects via socket.
  Available at `$SUMO_HOME/tools/traci`.  Verified working on this system
  with `PYTHONPATH=/usr/share/sumo/tools`.
- **libsumo**: C++ bindings, faster but requires compiled .so.  Not working
  on this system (circular import error).

### Car-Following Models

SUMO ships with multiple car-following models relevant to phantom jams:
- Krauss (default) — stochastic, with dawdling parameter
- IDM — Intelligent Driver Model
- EIDM — Extended IDM (Salles et al.)
- W99 — Wiedemann 99
- ACC / CACC — for controlled vehicles

### Ring-Road in SUMO

Creating a ring-road network in SUMO requires:
1. Generate a circular edge network (.net.xml)
2. Define vehicle types with car-following model parameters
3. Route vehicles on the ring
4. Use TraCI to insert/control vehicles and collect trajectories

For the pure 1-D ODE case (no lane changes, no on/off ramps), the
pure-Python IDM integrator is simpler and faster.

--------------------------------------------------------------------------------

## 6. Flow Framework

| Field | Value |
|-------|-------|
| URL | https://flow-project.github.io/ |
| GitHub | https://github.com/flow-project/flow |
| Last release | v0.4.1 (September 2019) |
| Last commit | December 2020 |
| License | MIT |
| Status | **STALE / UNMAINTAINED** |

### Assessment

Flow was Berkeley's RL-for-traffic framework built on top of SUMO.  It
provided ring-road environments that directly match the Sugiyama setup.
However:

- **No releases since 2019**, no commits since late 2020
- Dependencies are outdated (rllab deprecated, TensorFlow 1.x era)
- 173+ open issues with no maintainer activity
- Python 3.10+ compatibility is uncertain

**Recommendation**: Do NOT depend on Flow.  Use the pure-Python IDM
integrator for ring-road experiments (simpler, faster, no dependency risk).
For RL integration in Phase 2, use Gymnasium directly with the ring-road
simulator as a custom environment.

### What to Salvage from Flow

- Ring-road configuration parameters (N, L, perturbation scheme)
- FollowerStopper and PI controller implementations (for reference)
- The RL training setup (observation/action space definitions)

--------------------------------------------------------------------------------

## 7. CIRCLES Consortium

| Field | Value |
|-------|-------|
| URL | https://circles-consortium.github.io/ |
| GitHub org | https://github.com/CIRCLES-consortium (3 public repos) |
| Lead | UC Berkeley ITS, Vanderbilt, Temple, Rutgers-Camden |
| Industry | Toyota North America, Nissan North America |
| Funding | NSF, DOT, DOE |

### Public Repositories

1. **algos-stack** (MIT license): Controller and observer designs in C++/Python.
   Structure: `controllers/`, `observers/`, submission format is ROS packages
   or ONNX networks.  Contains `controller_max_80mph` and other designs.

2. **CIRCLES-ENERGY-MODELS** (MATLAB): Vehicle-specific fuel consumption
   models as f(speed, acceleration, road grade).  Useful for computing
   realistic fuel savings from wave dampening.

3. **Website repo**: Static site source.

### Field Experiment Data

The CIRCLES MVT (MegaVanderTest, November 2022) deployed ~100 Toyota RAV4s
with longitudinal control on I-24.  Published results in Nature (2024):
Lichtle et al., "Deploying connected and automated vehicles to smooth
traffic flow".

The MVT trajectory data's public availability is tied to I-24 MOTION releases
(see Section 1).  As of 2026-04-09, it is not confirmed to be in the public
INCEPTION dataset.

### Published Controllers

From Stern et al. (2018) and subsequent CIRCLES papers:
- **FollowerStopper**: Desired-velocity curve based on gap, with three
  regions (stop / ramp / cruise)
- **PI with Saturation**: Time-headway tracking PI controller with
  acceleration limits
- **RL policies**: Various PPO/SAC-trained policies (not in public repos
  as runnable artifacts)

--------------------------------------------------------------------------------

## 8. Recent Benchmarks and Simulation Suites (2024-2026)

### Ring-Road RL Benchmarks

No single standardised benchmark suite for CAV ring-road phantom-jam
suppression exists as of 2026.  The closest are:

- **Flow ring-road environment** (stale, see Section 6)
- **Gymnasium custom environments**: Several research groups have published
  ring-road Gym environments, but none has emerged as a community standard
- **SUMO ring-road tutorials**: SUMO documentation includes ring-road
  examples, but not packaged as RL benchmarks

### Traffic RL Frameworks (Active)

- **SUMO-RL** (Lucas Alegre): Active Gymnasium/PettingZoo wrapper for SUMO.
  GitHub: https://github.com/LucasAlegre/sumo-rl.  Focused on traffic
  signal control, not car-following.  License: MIT.
- **CityFlow**: Lightweight traffic simulator from Shanghai Jiao Tong.
  Focused on intersections, not highways.
- **SMARTS** (Huawei): Multi-agent driving simulator.  More complex than
  needed for ring-road.

### Relevant Recent Papers

- Lichtle et al. (2024), "Deploying connected and automated vehicles to
  smooth traffic flow", Nature — the CIRCLES MVT paper
- Wu et al. (2022), "Flow: A modular learning framework for mixed autonomy
  traffic", IEEE T-RO — Flow retrospective
- Vinitsky et al. (2018), "Benchmarks for reinforcement learning in mixed-
  autonomy traffic" — original Flow ring-road benchmark paper

### Our Approach

Given the landscape, we use a **pure-Python IDM ring-road simulator**
(sim_ring_road.py) with:
- Pluggable controllers (controllers.py)
- Standard measurement functions (measurements.py)
- Deterministic seeding for reproducibility
- No dependency on stale frameworks

This is the most robust path for Phase 0-2.  SUMO integration can be
added in Phase 3 if multi-lane or network-level experiments are needed.
