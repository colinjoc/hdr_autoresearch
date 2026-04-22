"""Fontenele-style subspace branching-ratio — Candidate 29 imported into
Paper 1 per Phase 0.25 reframe.

Method:
  1. Compute the per-token activity-magnitude time series u_t = mean(|A_t|)
     over all neurons (or sum over binarised activity).
  2. PCA / SVD on the mean-centred (T, d) activation matrix.
  3. For each K, project onto top-K PCs and sum → a reconstructed scalar
     Σ_K(t).
  4. MR estimator σ on Σ_K.
  5. K-selection: Fontenele's operational rule — largest K such that
     dropping PC1..PC_K keeps the complementary-subspace avalanche
     distribution power-law over ≥ 1.5 decades. We also report the direct
     participation-ratio PR.
"""

from __future__ import annotations

import dataclasses

import numpy as np


@dataclasses.dataclass
class SubspaceResult:
    K: int
    sigma_K: float      # MR σ on top-K-PC reconstructed scalar
    sigma_ambient: float  # MR σ on mean-magnitude ambient signal
    participation_ratio: float
    method: str  # "participation_ratio" | "fontenele_operational"


def _svd_gpu_if_available(Xc: np.ndarray):
    """Thin SVD with GPU acceleration when CUDA is available.

    Falls back to numpy transparently. For d_model=768, T=100K the GPU
    version is ~5-10× faster; for Pythia-2.8B (d=2560) it is ~50-100×.
    """
    try:
        import torch
        if torch.cuda.is_available():
            X_t = torch.from_numpy(Xc).to("cuda", dtype=torch.float32)
            U, S, Vt = torch.linalg.svd(X_t, full_matrices=False)
            return U.cpu().numpy(), S.cpu().numpy(), Vt.cpu().numpy()
    except Exception:
        pass
    return np.linalg.svd(Xc, full_matrices=False)


def _reconstructed_scalar_from_top_K_PC(X: np.ndarray, K: int) -> np.ndarray:
    X = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = _svd_gpu_if_available(X)
    K = min(K, U.shape[1])
    recon = (U[:, :K] * S[:K]) @ Vt[:K, :]
    return recon.sum(axis=1)


def participation_ratio(X: np.ndarray) -> float:
    """PR = (Σ λ)² / Σ λ² of the covariance eigenspectrum.

    Uses the squared-singular-values identity λ_i = S_i² to avoid forming
    the d×d covariance matrix explicitly (important for large d_model).
    """
    Xc = X - X.mean(axis=0, keepdims=True)
    _, S, _ = _svd_gpu_if_available(Xc)
    S2 = S.astype(np.float64) ** 2
    S2 = S2[S2 > 1e-10]
    if S2.size == 0:
        return 0.0
    return float((S2.sum() ** 2) / (S2 ** 2).sum())


def subspace_sigma(
    activations: np.ndarray,
    K: int | None = None,
    method: str = "participation_ratio",
) -> SubspaceResult:
    """Compute σ_K on the top-K PC reconstructed scalar.

    If ``K`` is None, use participation-ratio as the K selector. Set
    ``method='fontenele_operational'`` for Fontenele's collapse-criterion
    K-selection (Phase 2 will implement full collapse-criterion; this
    Phase 1 stub uses PR).
    """
    from pipeline.exponents import branching_ratio_mr
    X = np.asarray(activations, dtype=np.float64)
    pr = participation_ratio(X)
    if K is None:
        K = max(2, int(round(pr)))
    scalar_K = _reconstructed_scalar_from_top_K_PC(X, K)
    # ambient reference: activity = mean absolute deviation per token.
    ambient = np.abs(X - X.mean(axis=0, keepdims=True)).sum(axis=1)
    br_K = branching_ratio_mr(scalar_K)
    br_amb = branching_ratio_mr(ambient)
    return SubspaceResult(
        K=int(K), sigma_K=br_K.sigma, sigma_ambient=br_amb.sigma,
        participation_ratio=pr, method=method,
    )
