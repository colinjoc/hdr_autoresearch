# Literature Review — gw_detectors

**RECONSTRUCTED SKELETON.** The original `literature_review.md` (~40 KB across 7 themes) was lost on 2026-04-09. This file is a thin scaffolding tied to the references that survived in `paper.md` and `papers.csv`. The full review needs to be rebuilt — see Phase 0 Quality Gate in `program.md` for the standard.

## Theme 1: Domain fundamentals — interferometric gravitational wave detection

A modern gravitational-wave detector is a power-recycled, signal-recycled Fabry-Perot Michelson interferometer with squeezed-light injection and frequency-dependent squeezing for quantum-noise reduction. Saulson's textbook [7] is the standard reference for the fundamentals; Braginsky & Khalili [8] is the standard for quantum measurement theory in this context. Drever's foundational chapter [15] established the topology that all subsequent detectors are extensions of. Meers [16] introduced power recycling.

## Theme 2: Phenomena of interest — quantum noise, thermal noise, seismic noise

Strain sensitivity in current detectors is limited by three noise floors:
- **Quantum noise** (shot noise + radiation pressure noise) [5,17]. Sets the SQL.
- **Thermal noise** in mirror coatings [6]. Dominant at mid-frequencies (~100 Hz).
- **Seismic noise** [7]. Dominant below ~10 Hz.

## Theme 3: Candidate features and design variables

The UIFO parameterisation is the relevant "feature space" for an AI-discovered design. Each mirror, beamsplitter, laser, squeezer, and cavity in the grid exposes a small set of physical parameters; the optimiser searches over their joint space. See `design_variables.md` for the full enumeration.

## Theme 4: ML/optimisation for this problem

Krenn, Drori, and Adhikari [1] introduced gradient-based optimisation over UIFOs (BFGS with 1000 random restarts) and produced 50 published designs in the GW Detector Zoo [19]. To our knowledge, no one has previously published a systematic decomposition of these AI-discovered designs to identify the responsible physical mechanisms.

## Theme 5: Objective function design

The standard figure of merit for a GW detector design is the strain noise spectral density h(f) [strain/√Hz]. The improvement factor over a baseline is taken in log space averaged over the target frequency band.

## Theme 6: Transfer / generalisation across conditions

Open question: do the mechanisms identified in one solution family (e.g. type8 noise suppression) transfer to other frequency bands by scaling the responsible parameters (test mass, cavity finesse)? See `research_queue.md` H02.

## Theme 7: Related problems — AI-discovered scientific designs in other domains

Decomposition of AI-discovered solutions is a young methodology. The current work is, to our knowledge, the first published systematic ablation of an AI-discovered GW detector design. The approach (component ablation before parameter sweeps; cross-validation against an independent simulator; family classification) is broadly applicable to AI-discovered designs in other physics domains.

## Reference list

See `papers.csv` for the 22 references currently catalogued. The original `papers.csv` had ~110 entries — the rest must be re-collected.
