# Observations — qec_resource_est

Consolidated summary of Phase 0.5 + Phase 1 experimental findings. See `phase_0_5_findings.md` and `phase_1_findings.md` for full narrative and `results.tsv` for raw data.

## Experiments run (2026-04-21, RTX 3060 12 GB, Python 3.12)

| ID | What | Code | Noise | Shots | Headline |
|----|------|------|-------|-------|----------|
| E00 | GPU vs CPU BP+OSD | surface d∈{3..13} | code-capacity p=0.05 | 1000 | GPU/CPU ratio decreases 44×→2.6× as H grows; crossover ~d=15 |
| E00_azure | Azure Estimator on RSA-2048 | Shor 2048 | various qubit presets | N/A | 6 qubit-model cells: ~6M physical qubits for gate_ns_e4 surface at 20 hours |
| E01 | BB [[144,12,12]] code-capacity | BB gross | code-capacity p∈{0.01, 0.05} iter∈{30,100} | 500 | GPU still 2.5-4.9× slower than CPU at d=12 BB code-capacity |
| E02 | BB [[144,12,12]] circuit-level | BB gross | SI1000 p=1e-3, 12 rounds | 300 | GPU wins 146× (H grows to 936×10,512) |
| E03 | Matched-overhead surface | 12 × surface d=12 | SI1000 p=1e-3, 12 rounds | 300 | 12×surface CPU MWPM (227 μs/shot) beats BB GPU (3710 μs/shot) by 16× |
| E04 | Energy per shot | BB + 12×surface | matched to E02/E03 | 3000/300 | BB GPU 233 mJ/shot (gross); 12×surface CPU 1.84 mJ/shot → 127× energy advantage for surface |

## Central finding

**Bravyi 2024's 12× BB-over-surface qubit-count advantage inverts when classical decoder compute is folded in.** On RTX 3060 at circuit-level SI1000 p=1e-3, 12 rounds, the matched-surface-code encoding of 12 logical qubits is 16× faster and 127× more energy-efficient per shot than the [[144,12,12]] BB gross code, per logical-qubit-round.

## Implications for the paper

1. **Pre-registered 2× shrinkage threshold triggered with 6-60× margin.** proposal_v3 §2 kill is NOT triggered; headline claim validated.
2. **Consumer-GPU floor story is independently publishable.** RTX 3060 numbers document the regime where any GPU advantage vanishes — academic readers without A100 access get a ground truth.
3. **Virgin-literature axis — per-shot decoder energy** — is quantified for the first time for BB vs surface at a matched operating point.
4. **A100 upper bound.** Even if an A100 delivers 10× wall-time reduction for BB GPU BP+OSD (optimistic), the 16× BB-vs-surface time disadvantage shrinks to ~1.6× — still a disadvantage.
5. **Publication-ready with further Phase 1 work.** Remaining: iteration-count ablation, hybrid Ising-CNN-predecoder + PyMatching for surface on GPU, reaction-time sensitivity sweep, logical-qubit-second-×-J composite applied to RSA-2048.
