# HDR Project Candidates

Identified 2026-04-08. Simulation-based problems suitable for HDR methodology.
All require GPU-accelerated differentiable simulation as the evaluation function.

## Tier 1 — High Impact, High Feasibility

### 1. Quantum Gate Pulse Optimization
- **Domain**: Quantum Computing
- **Simulation**: Evolve qubit Hamiltonian under candidate pulse → compute gate fidelity
- **Tools**: Dynamiqs (JAX), SuperGrad, Qontrol
- **Eval speed**: Seconds per pulse on 1 GPU
- **Status**: IN PROGRESS (literature review started)

### 2. Robot Locomotion Policy Optimization
- **Domain**: Robotics / Control
- **Simulation**: Physics engine (MuJoCo) executes policy → reward (velocity, efficiency, stability)
- **Tools**: MuJoCo XLA (MJX), Brax (JAX)
- **Eval speed**: Trains in <10 min on 1 GPU
- **Refs**: MuJoCo Playground (RSS 2025), Brax

### 3. Photonic Nanostructure Inverse Design
- **Domain**: Photonics / Optics
- **Simulation**: FDTD solves Maxwell's equations for device geometry → transmission/coupling metrics
- **Tools**: FDTDX (JAX, 10x faster than Meep), Tidy3D
- **Eval speed**: Seconds per 2D device
- **Refs**: Mahlau et al. 2024, Deng et al. 2024

### 4. Structural Topology Optimization
- **Domain**: Mechanical / Civil Engineering
- **Simulation**: FEM solves elasticity PDE → compliance (strain energy) under loads
- **Tools**: JAX-FEM, JAX-SSO
- **Eval speed**: Seconds for 2D, minutes for 3D (7.7M DOF)
- **Refs**: Xue et al. 2023 (JAX-FEM), Wu et al. 2024

### 5. RNA Sequence Design
- **Domain**: Computational Biology
- **Simulation**: Differentiable folding predicts MFE structure → match to target
- **Tools**: JAX-RNAfold (scales to 1250 nt on 1 GPU)
- **Eval speed**: Seconds per sequence
- **Refs**: Krueger & Ward, Bioinformatics May 2025

## Tier 2 — High Impact, Moderate Feasibility

### 6. Differentiable CFD Shape Optimization
- **Domain**: Aerospace / Fluid Mechanics
- **Simulation**: Solve Navier-Stokes around parameterized body → lift/drag
- **Tools**: JAX-Fluids (TU Munich), PhiFlow, Diff-FlowFSI
- **Eval speed**: Seconds (2D), minutes (3D)
- **Refs**: Bezgin et al. 2025, JAX-Shock 2026

### 7. Catalyst Surface Design
- **Domain**: Chemistry / Materials / Energy
- **Simulation**: ML force field predicts adsorption energy on candidate surface → catalytic activity
- **Tools**: MACE (PyTorch), Open Catalyst models (EquiformerV2)
- **Eval speed**: Seconds per relaxation
- **Refs**: OC25 (Meta FAIR 2025), MACE-OFF 2024

### 8. Seismic Full Waveform Inversion
- **Domain**: Geophysics
- **Simulation**: Propagate seismic waves through velocity model → compare with observed seismograms
- **Tools**: Devito (Python DSL, GPU stencil code)
- **Eval speed**: Seconds (2D), minutes (3D)
- **Refs**: Taichi-driven seismic modeling 2026, Devito project

### 9. Optical Lens System Design
- **Domain**: Optics / Computational Photography
- **Simulation**: Differentiable ray tracing through multi-element lens → image quality metrics
- **Tools**: DeepLens (PyTorch), Optiland (150M+ ray-surfaces/sec)
- **Eval speed**: Milliseconds to seconds
- **Refs**: DeepLens (SIGGRAPH), freeform spectacle lenses 2025

## Tier 3 — High Impact, Higher Difficulty

### 10. Microstructure Phase Field Simulation
- **Domain**: Materials Science / Metallurgy
- **Simulation**: Solve Cahn-Hilliard/Allen-Cahn equations → predict grain structure & properties
- **Tools**: JAX-PF, JAX-CPFEM
- **Eval speed**: Minutes
- **Refs**: JAX-PF (Dec 2025), JAX-CPFEM 2025

### 11. Differentiable Fluid Control
- **Domain**: Fluid Mechanics / Engineering
- **Simulation**: Simulate flow with controllable boundaries → drag/mixing/heat transfer
- **Tools**: PhiFlow (JAX/PyTorch), textbook: Physics-based Deep Learning
- **Eval speed**: Seconds (2D)
- **Refs**: Thuerey et al. textbook, PhiFlow

### 12. Climate Model Emulation
- **Domain**: Earth Sciences / Climate
- **Simulation**: Neural emulator runs decades of climate → compare statistics with reanalysis
- **Tools**: ACE2 (450M params, 1500 sim-years/day on 1 GPU)
- **Eval speed**: Fast inference, but training the emulator is expensive
- **Refs**: ACE2 2025, SamudrACE 2025

### 13. Spacecraft Trajectory Optimization
- **Domain**: Aerospace Engineering
- **Simulation**: 6-DOF dynamics under thrust profile → fuel + landing accuracy
- **Tools**: JAX/PyTorch differentiable dynamics, DiffOG
- **Eval speed**: Seconds to minutes
- **Refs**: Starship flip-landing optimization (Aug 2025), DiffOG T-RO 2025
