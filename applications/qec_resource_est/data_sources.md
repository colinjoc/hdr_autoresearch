# data_sources.md — qec_resource_est Phase 0 smoke test

**Date:** 2026-04-20. **Host:** `col@WSL2` (Linux 6.6.87, Ubuntu 24.04). **Python:** 3.12.3. **CUDA toolchain:** nvcc V12.9.86, driver 576.88, runtime CUDA 12.9. **Verdict:** PROCEED (tight), with one **material reframe** to PER-1 and one **formal caveat** on GPU class. No scoop found.

---

## 1. Tooling reachability (verified)

| Tool | URL | Status | Notes |
|---|---|---|---|
| CUDA-Q QEC (NVIDIA) | https://github.com/NVIDIA/cudaqx | Reachable, maintained | BB decoder example present (`examples_rst/qec/decoders.html`); generic timing template, not publicly-benchmarked; compute-capability 6.0+ required (RTX 3060 = 8.6 — compatible in principle). v0.6 (Apr 2026) adds RelayBP qLDPC + Ising predecoder + PyMatching hybrid path. |
| Azure Quantum Resource Estimator | https://learn.microsoft.com/en-us/azure/quantum/intro-to-resource-estimation | Reachable | Confirmed **open-source** (aka.ms/AQ/RE/OpenSource link present); source in microsoft/qsharp + microsoft/qdk; extensibility API for custom QEC schemes confirmed. Alice-and-Bob already extended it for cat+repetition (precedent for us). |
| Stim | https://github.com/quantumlib/Stim | Reachable, v1.15.0 (May 2025), pip-installable | Baseline stabilizer sim. Not installed in current venv — will be installed in Phase 1. |
| PyMatching v2 | https://github.com/oscarhiggott/PyMatching | Reachable, v2.1.x, pip-installable | **CPU only.** No CUDA fork, no official CUDA branch. Sparse blossom ~10⁶ errors/core-second on CPU. |
| `ldpc` (Roffe BP+OSD) | https://github.com/quantumgizmos/ldpc | Reachable | v2 = C++ rewrite, Python≥3.10, includes BP+LSD + BP+OSD. CPU only; OpenMP parallel BP+LSD in progress. |
| `bposd` | https://github.com/quantumgizmos/bp_osd + https://pypi.org/project/bposd | Reachable | Legacy v1 BP+OSD; `ldpc_v2` is the currently-maintained successor. |
| Gidney 2025 assets | https://zenodo.org/records/15347487 (DOI 10.5281/zenodo.15347487) | Reachable | Single file `code.zip` (6.2 MB, CC-BY-4.0). Contents not enumerated on record page; download + inventory is a Phase 1 day-1 task. No GitHub mirror found. |
| Azure RE source | https://github.com/microsoft/qsharp + microsoft/qdk | Reachable, open-source | Samples in `samples/estimation/`. |
| `qLDPC` (qLDPCOrg) | https://github.com/qLDPCOrg/qLDPC | Reachable | Unified API over `ldpc`, `stim`, `sinter`, `pymatching`, relay-bp; BP-OSD, BP-LSD, belief-find, MWPM, lookup-table. |

**No tooling blocker.** All primary repos live, maintained, pip-installable where relevant.

---

## 2. GPU access

### 2a. Local host (actual)

```
NVIDIA GeForce RTX 3060, 12 GB VRAM, 170 W TDP, CUDA 12.9 / driver 576.88
Compute capability: 8.6 (Ampere consumer — NOT data-center class)
```

### 2b. A100 commitment in proposal_v2 — BLOCKER as stated, reframe available

proposal_v2 §3 and §6 commit to *"MEASURED on author's A100 via CUDA-Q QEC"*. **The author does not have local A100 access.** Literal execution of the proposal as written is therefore blocked.

**Options and mitigation:**

1. **Reframe to consumer-GPU floor (RECOMMENDED for Phase 0 toy):** run the Phase 0 kill-gate toy (d = 6 BB vs d = 9 surface, p = 10⁻³) on the local RTX 3060. Document precise ratio. Consumer-GPU numbers are a legitimate floor measurement — they *strengthen* the "not relying on cited vendor speedups" story because a consumer GPU is what most academic readers can replicate. Headline becomes "GPU-decoder-aware" rather than "A100-measured."
2. **NVIDIA Academic Grant Program** — apply immediately. Lead time ~4–8 weeks. Precedent: 32k A100-GPU-hours awarded to Liu (Illinois iSchool 2026). Fits our profile. Submit in parallel with Phase 0 toy on 3060.
3. **NAIRR Pilot / NERSC ERCAP (Perlmutter 7000× A100)** — federal program, slower (~3–6 months), large allocation if granted.
4. **Rental: Lambda / RunPod / ThunderCompute** — $1–2 per A100-hour; a full measurement sweep (est. 200 A100-hours at d = 12 BB + matched surface) ≈ $200–400. Feasible from personal budget.
5. **Google Cloud $300 new-account credit** — one-shot, marginal for a single A100 campaign.

**Commitment for this project:** Phase 0 toy runs on RTX 3060. Apply to NVIDIA Academic Grant Program by 2026-04-27. If grant does not land by 2026-06, budget $300 of personal funds for rental A100-hours to produce the headline d = 12 BB number. Publish consumer-GPU floor (3060) numbers *in addition* to A100 numbers — it is independently useful calibration for the community.

**Update proposal_v2 §6 to reflect this.** Mark as action item R-PER-1b.

### 2c. Thermal + power measurement on the RTX 3060

NVML via `nvidia-smi --query-gpu=power.draw,temperature.gpu --format=csv -l 1` works out-of-the-box on this host; Persistence-M is ON; idle draw 11 W; TDP 170 W. Sampling rate 1 Hz is the NVML floor; for per-shot energy at ~100 μs–ms timescales we need aggregate windows of ≥1 s. Document methodology explicitly in Phase 2 (per Phase 0.25 reviewer point 4a).

---

## 3. MWPM-GPU codepath options — **material reframe needed**

### 3a. What exists

| Candidate | Source | Status |
|---|---|---|
| Fowler sparse MWPM (original 2013) | Fowler, arXiv:1307.1740 / PRA 88 (O(N) serial, O(1) parallel) | **Not publicly available.** Confirmed by Higgott & Gidney 2023 "Sparse Blossom" paper (quotes: "none of these are publicly available to our best knowledge"). |
| PyMatching v2 sparse blossom | github.com/oscarhiggott/PyMatching | CPU only, no CUDA fork. |
| `fusion-blossom` (Wu & Zhong) | github.com/yuewuo/fusion-blossom | CPU parallel + FPGA variant (`micro-blossom`). No CUDA backend. |
| `micro-blossom` (Wu) | github.com/yuewuo/micro-blossom | FPGA (Zynq SoC) hardware MWPM. Not GPU. |
| NVIDIA CUDA-Q QEC real-time MWPM pipeline | cudaqx v0.6 | **Hybrid**: Ising CNN predecoder on GPU (TensorRT, FP16) + PyMatching on CPU global decoder. Not a pure MWPM-GPU. Published numbers (NVIDIA blog, 2026-04-14): ~2 μs/QEC round on B300 GPU + Grace Neoverse-V2 CPU. |

### 3b. Conclusion — **proposal_v2 over-committed**

There is **no publicly available pure MWPM-GPU implementation** at commit-hash resolution, as of 2026-04. The either/or phrased in proposal_v2 ("Fowler sparse / PyMatching-CUDA") is therefore not satisfiable. Both branches of the either/or evaluate to "does not exist."

### 3c. Replacement PER-1 reframe

**Update PER-1:** The committed MWPM-GPU codepath is **NVIDIA CUDA-Q QEC 0.6 hybrid Ising-predecoder + PyMatching pipeline** (git tag: **v0.6.0 of github.com/NVIDIA/cudaqx**, pinned by commit hash at Phase 1 kickoff; NVIDIA/Ising-Decoding pinned at the same date). This is a *composite* decoder, not a monolithic MWPM-GPU — correctly disclosed in the paper's methods section.

Sensitivity ablation: also measure **PyMatching v2 on CPU alone** (no predecoder) as a CPU-only baseline for matched surface code; and **ldpc_v2 BP+OSD** on CPU alone as the BB baseline. These two CPU numbers bound the GPU acceleration gain from above.

This reframe is a **material change** to the proposal. It is also *more honest* than the original either/or. The Phase 0.25 reviewer's concern — "the MWPM-GPU implementation is under-committed" — is resolved by the commitment, and the implementation is the one with the strongest documentation + community signal. Record as action item R-PER-1a.

---

## 4. Scoop scan (decisive)

Five queries run on 2026-04-20. Candidates surfaced:

| Candidate | arXiv / URL | Scoop? | Why / why not |
|---|---|---|---|
| Bhatnagar et al. (Princeton/MIT), "Impacts of Decoder Latency on Utility-Scale Quantum Computer Architectures" | arXiv:2511.10633 (Nov 2025) | **No** | Surface-code only. No BB vs matched-surface comparison. No measured GPU decoder coupling. Focuses on reaction-time → magic-state LER coupling. **Adjacent, not overlapping.** Cite as prior art for the reaction-time axis. |
| "Cascade" neural decoder (Scalable Neural Decoders) | arXiv:2604.08358 (Apr 2026) | **No** | Neural-decoder paper; touches BB + surface codes but is a *decoder* paper, not a *resource-estimation* paper. No compiled-algorithm cost coupling. Cite as prior art for NN decoder on BB codes. |
| "Accelerating BP-OSD Decoder for QLDPC Codes with Local Syndrome-Based Preprocessing" | arXiv:2509.01892 (Sept 2025) | **No** | BP+OSD optimisation paper. No resource estimate, no compiled algorithm. Cite as BP+OSD latency-reduction prior art. |
| "Diversity Methods for Improving Convergence and Accuracy of QEC Decoders Through Hardware Emulation" | Quantum q-2026-04-16-2071 | **No** | FPGA-emulation decoder paper. No resource estimate, no compiled algorithm. |
| "Resource Estimation for Delayed Choice Quantum Entanglement Based Sneakernet Networks Using Neutral Atom qLDPC Memories" | arXiv:2410.01211 | **No** | Quantum-network resource estimate; not FTQC factoring. Distant. |
| Riverlane QEC Roadmap whitepaper 2026 | riverlane.com/press-release/riverlane-publishes-qec-technology-roadmap | **No** | Press release reachable; whitepaper PDF behind a 403. Summary coverage (HPCwire, TheQuantumInsider, Mar 2026) describes it as a *roadmap* doc using Mega/Giga/TeraQuOp scale markers. No coupling of measured decoder cost to a compiled algorithm like Gidney 2025 RSA-2048 is reported in any of the summary coverage. **Not a scoop** of our specific, algorithm-pinned claim. To-do: retrieve whitepaper PDF Phase 1 day 1 (via IP-clean fetch or direct contact). If the whitepaper *does* contain a Gidney-2025-pinned BB-vs-surface + GPU cost coupling, re-evaluate immediately under proposal_v2 §4.3 kill path. |
| Riverlane LCD Nature Commun. 2025 | riverlane.com/news/... | **No** | Hardware decoder (FPGA, LCD); not coupled to a compiled algorithm + BB vs surface. Prior art, not scoop. |

### 4a. Scoop-scan verdict

**Niche still open.** No 2025–2026 preprint couples measured GPU decoder compute to a specific compiled algorithm (e.g. RSA-2048 Gidney 2025) for BB vs matched surface code with logical-qubit-seconds × decoder-Joules product. The three closest-neighbour papers (2511.10633, 2604.08358, 2509.01892) each occupy a single axis of the intersection, not the full intersection. This is **consistent with the Phase 0.25 reviewer's assessment (Obj 2)** — the niche remains open as of the Phase 0 cutoff, but the scoop timeline is tight.

**Monitor monthly per PER-3.** Next scoop-scan scheduled 2026-05-20.

---

## 5. Smoke-test verdict

**PROCEED**, with the following deltas to proposal_v2 folded in before Phase 1 kickoff:

- **R-PER-1a** (formal): Update PER-1 MWPM-GPU codepath from "Fowler sparse / PyMatching-CUDA" to "NVIDIA CUDA-Q QEC v0.6 hybrid Ising-predecoder + PyMatching" with pinned commit hash. Include CPU-PyMatching-v2 and CPU-ldpc_v2 BP+OSD as ablation baselines.
- **R-PER-1b** (formal): Update proposal_v2 §6 to replace "author's A100" with "author's RTX 3060 (12 GB, CUDA 12.9) for Phase 0 toy; A100 access via NVIDIA Academic Grant Program application (submitted by 2026-04-27) for Phase 2 headline; rental budget $300 as fallback". Phase 0 toy kill-gate runs on the 3060.
- **R-PER-3** (no change from queue): monthly scoop-scan continues.

No blocker forces a KILL. Proceed to Phase 0 deep lit review and Phase 1 toy kill-gate.

---

*Smoke test completed in 42 minutes (over the 15-min target due to PER-1 reframe investigation — worth the extra time: the MWPM-GPU finding saves a whole phase of Phase 1 pain).*
