"""
Baselines for drift-tracking comparison.

- SlidingWindowMLE:  maximum-likelihood per-edge rate on a sliding window of
                     W detector-event streams. (arXiv:2511.09491 reimplementation.)
- StaticBayesianMCMC: treat the entire observation stream as a single
                      stationary noise model; MAP via conjugate-prior Beta
                      update. (arXiv:2406.08981 baseline proxy — the full
                      TN+MCMC implementation is Phase 2.)
- PeriodicDEMRefit:   refit the DEM at a fixed cadence (e.g. 1/hour) using
                      the sliding-window estimator. Matches Willow-2024
                      operational practice.
"""

from __future__ import annotations
import numpy as np


class SlidingWindowMLE:
    """Per-edge rate MLE from detector-event co-occurrence on a sliding window.

    Pseudo-inverse attribution variant — kept as a conservative reimplementation
    of arXiv:2511.09491. The correlated-pair variant is `CorrelatedPairMLE` below.
    """

    def __init__(self, n_errors: int, window_size: int = 1000):
        self.E = n_errors
        self.W = window_size
        self.buffer: list[np.ndarray] = []
        self.current_rates = np.full(n_errors, 1e-3)

    def update(self, detector_events: np.ndarray, H: np.ndarray):
        self.buffer.append(detector_events.astype(np.uint8))
        if len(self.buffer) > self.W:
            self.buffer.pop(0)
        if len(self.buffer) >= self.W:
            self._refit(H)

    def _refit(self, H: np.ndarray):
        stream = np.array(self.buffer, dtype=np.uint8)
        p_det = stream.mean(axis=0)
        try:
            p_edge, *_ = np.linalg.lstsq(H.astype(float), p_det, rcond=None)
            self.current_rates = np.clip(p_edge, 1e-8, 0.499)
        except Exception:
            pass

    def posterior_mean(self) -> np.ndarray:
        return self.current_rates.copy()


class CorrelatedPairMLE:
    """Sliding-window MLE on detector-pair covariance (arXiv:2511.09491 variant).

    Key observation: for detector pair (i, j) connected by edges E_{ij} = {e : H_{i,e} = H_{j,e} = 1},
        Cov(s_i, s_j)  ≈  Σ_{e ∈ E_{ij}} θ_e   (at low rates, higher-order corrections O(θ²))
    So the full covariance matrix gives a linear system C = M θ where M is the pair-edge
    incidence matrix. Solve via non-negative least squares (rates must be ≥ 0).
    """

    def __init__(self, n_errors: int, n_detectors: int, window_size: int = 1000):
        self.E = n_errors
        self.D = n_detectors
        self.W = window_size
        self.buffer: list[np.ndarray] = []
        self.current_rates = np.full(n_errors, 1e-3)
        self._M = None
        self._pair_idx = None

    def _build_pair_incidence(self, H: np.ndarray):
        """Build M: row p indexes pairs (i, j), column e is 1 iff H[i,e] = H[j,e] = 1."""
        D = H.shape[0]
        E = H.shape[1]
        pairs = [(i, j) for i in range(D) for j in range(i + 1, D)]
        M = np.zeros((len(pairs), E), dtype=np.float64)
        for p_idx, (i, j) in enumerate(pairs):
            M[p_idx] = H[i] * H[j]
        self._M = M
        self._pair_idx = np.array(pairs, dtype=np.int64)

    def update(self, detector_events: np.ndarray, H: np.ndarray):
        self.buffer.append(detector_events.astype(np.uint8))
        if len(self.buffer) > self.W:
            self.buffer.pop(0)
        if len(self.buffer) >= self.W:
            if self._M is None:
                self._build_pair_incidence(H)
            self._refit()

    def _refit(self):
        stream = np.array(self.buffer, dtype=np.float64)
        p_i = stream.mean(axis=0)
        C = (stream.T @ stream) / stream.shape[0] - np.outer(p_i, p_i)
        c_pairs = np.array([C[i, j] for i, j in self._pair_idx])
        # Least-squares (clipped to non-negative).
        # NNLS would be exact but slower; lstsq + clip is adequate in low-rate regime.
        try:
            p_edge, *_ = np.linalg.lstsq(self._M, c_pairs, rcond=None)
            self.current_rates = np.clip(p_edge, 1e-8, 0.499)
        except Exception:
            pass

    def posterior_mean(self) -> np.ndarray:
        return self.current_rates.copy()


class StaticBayesianRates:
    """Beta-prior posterior on per-edge rates — simpler than full TN+MCMC.

    Each edge's rate is modelled as Beta(α, β) with α, β updated online.
    """

    def __init__(self, n_errors: int, alpha_prior: float = 2.0, beta_prior: float = 2000.0):
        self.E = n_errors
        self.alpha = np.full(n_errors, alpha_prior)
        self.beta = np.full(n_errors, beta_prior)

    def update(self, detector_events: np.ndarray, H: np.ndarray):
        p_det = detector_events.astype(float)
        # Pseudo-inverse attribution; bin events to edges
        try:
            attrib, *_ = np.linalg.lstsq(H.astype(float), p_det, rcond=None)
            attrib = np.clip(attrib, 0, 1)
        except Exception:
            attrib = np.zeros(self.E)
        self.alpha = self.alpha + attrib
        self.beta = self.beta + (1 - attrib)

    def posterior_mean(self) -> np.ndarray:
        return np.clip(self.alpha / (self.alpha + self.beta), 1e-8, 0.499)


class PeriodicDEMRefit:
    """Refit the DEM at a fixed wall-clock cadence. Matches Willow operational practice."""

    def __init__(self, n_errors: int, refit_cadence_s: float = 3600.0,
                 window_size: int = 5000, dt_per_shot_s: float = 1e-3):
        self.E = n_errors
        self.cadence = refit_cadence_s
        self.dt = dt_per_shot_s
        self.mle = SlidingWindowMLE(n_errors, window_size=window_size)
        self.shots_since_refit = 0
        self.shots_per_refit = int(refit_cadence_s / dt_per_shot_s)

    def update(self, detector_events: np.ndarray, H: np.ndarray):
        self.shots_since_refit += 1
        # We accumulate but only refit at cadence boundaries
        self.mle.buffer.append(detector_events.astype(np.uint8))
        if len(self.mle.buffer) > self.mle.W:
            self.mle.buffer.pop(0)
        if self.shots_since_refit >= self.shots_per_refit and len(self.mle.buffer) >= self.mle.W:
            self.mle._refit(H)
            self.shots_since_refit = 0

    def posterior_mean(self) -> np.ndarray:
        return self.mle.posterior_mean()


if __name__ == "__main__":
    # Smoke test all three baselines on random streams.
    rng = np.random.default_rng(42)
    E, n_det = 50, 10
    H = (rng.random((n_det, E)) < 0.15).astype(np.uint8)

    mle = SlidingWindowMLE(E, window_size=200)
    bay = StaticBayesianRates(E)
    ref = PeriodicDEMRefit(E, refit_cadence_s=1.0, window_size=200, dt_per_shot_s=1e-3)

    for _ in range(500):
        s = (rng.random(n_det) < 0.05).astype(np.uint8)
        mle.update(s, H)
        bay.update(s, H)
        ref.update(s, H)

    print(f"[smoke] MLE mean={mle.posterior_mean().mean():.4e}")
    print(f"[smoke] Bay mean={bay.posterior_mean().mean():.4e}")
    print(f"[smoke] Ref mean={ref.posterior_mean().mean():.4e}")
