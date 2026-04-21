"""
Rao-Blackwellisable particle filter for online QEC noise-model drift tracking.

Two likelihood backends:

- `"independent_bernoulli"` — marginal per-detector Bernoulli. Low-rate-flatness-prone
  (fails Phase 3.5 null-hypothesis test).

- `"pair_correlation"` — evaluates each particle on the empirical detector-pair
  covariance over a sliding window. Detector pair (i, j) covariance is dominated by
  the shared edge(s) between them, giving a signal proportional to θ_e directly rather
  than summed over all error mechanisms. This is the fix for the Phase 3.5 reviewer's
  low-rate flatness diagnosis.

State: per-error-mechanism rate vector θ ∈ [0, 1]^E.
Propagation: OU drift on log θ.
"""

from __future__ import annotations
import dataclasses
from typing import Optional

import numpy as np


@dataclasses.dataclass
class DriftKernel:
    """Ornstein-Uhlenbeck drift kernel on log per-edge rates."""
    timescale_s: float
    amplitude: float
    dt_s: float = 1e-3

    def propagate(self, theta: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        noise = rng.normal(0, self.amplitude * np.sqrt(self.dt_s / max(self.timescale_s, self.dt_s)),
                          size=theta.shape)
        decay = np.exp(-self.dt_s / max(self.timescale_s, self.dt_s))
        return theta * decay + theta.mean() * (1 - decay) * np.exp(noise)


class ParticleFilter:
    def __init__(self, n_particles: int, n_errors: int, drift: DriftKernel,
                 prior_mean: Optional[np.ndarray] = None,
                 prior_std_log: float = 0.5,
                 likelihood: str = "pair_correlation",
                 batch_size: int = 100,
                 seed: int = 42):
        self.N = n_particles
        self.E = n_errors
        self.drift = drift
        self.rng = np.random.default_rng(seed)
        self.likelihood_kind = likelihood
        self.batch_size = batch_size
        self._window: list[np.ndarray] = []  # for pair-correlation

        if prior_mean is None:
            prior_mean = np.full(n_errors, 1e-3)
        log_mean = np.log(prior_mean + 1e-12)
        self.theta = np.exp(
            log_mean[None, :]
            + prior_std_log * self.rng.normal(size=(self.N, self.E))
        )
        self.log_w = np.full(self.N, -np.log(self.N))

    def step(self, detector_events: np.ndarray, H: np.ndarray,
             obs_mat: np.ndarray, true_obs_flip: int):
        # 1. Propagate
        self.theta = np.stack([
            self.drift.propagate(self.theta[p], self.rng) for p in range(self.N)
        ])
        self.theta = np.clip(self.theta, 1e-8, 0.499)

        s = detector_events.astype(np.uint8)
        self._window.append(s)
        if len(self._window) > self.batch_size:
            self._window.pop(0)

        if self.likelihood_kind == "pair_correlation":
            # Only evaluate once per batch_size shots to amortise cost
            if len(self._window) < self.batch_size:
                return  # accumulate until window is full
            log_liks = self._pair_correlation_log_lik(H, self._window)
            # reset window after using it so likelihood updates are independent
            self._window = self._window[self.batch_size // 2:]  # 50% overlap
        else:
            log_liks = self._independent_bernoulli_log_lik(H, s)

        # 2. Apply likelihood and normalise weights
        self.log_w = self.log_w + log_liks
        lw_max = self.log_w.max()
        self.log_w -= lw_max
        w = np.exp(self.log_w)
        w /= w.sum() + 1e-16
        self.log_w = np.log(w + 1e-16)

        # 3. ESS-triggered resampling
        ess = 1.0 / (w ** 2).sum()
        if ess < 0.5 * self.N:
            idx = self.rng.choice(self.N, size=self.N, p=w)
            self.theta = self.theta[idx]
            self.log_w = np.full(self.N, -np.log(self.N))

    def _independent_bernoulli_log_lik(self, H: np.ndarray, s: np.ndarray) -> np.ndarray:
        """Per-detector marginal Bernoulli likelihood."""
        log_liks = np.zeros(self.N)
        for p in range(self.N):
            p_det = np.clip((H * self.theta[p][None, :]).sum(axis=1), 1e-8, 1 - 1e-8)
            log_liks[p] = np.sum(s * np.log(p_det) + (1 - s) * np.log(1 - p_det))
        return log_liks

    def _pair_correlation_log_lik(self, H: np.ndarray, window: list[np.ndarray]) -> np.ndarray:
        """Gaussian log-likelihood on the shot-averaged detector pair-covariance matrix.

        Empirical covariance: C_ij = <s_i s_j> - <s_i><s_j>
        Expected covariance under θ (linear low-rate approx):
            C_ij(θ) = Σ_e H[i,e] H[j,e] θ_e - O(θ²)
        Particles are scored by how closely C(θ) matches C_empirical.
        """
        W = np.array(window, dtype=np.uint8)  # (batch, n_det)
        p_i = W.mean(axis=0)                  # (n_det,)
        C_emp = (W.T @ W) / W.shape[0] - np.outer(p_i, p_i)  # (n_det, n_det)

        # Expected: H H^T ⊙ θ as outer products — vectorised below
        # For particle p: C_ij(θ) = Σ_e H_ie H_je θ_pe = (H * θ_p[None,:]) @ H.T / ...
        # but we need the edge-weighted bilinear form:
        HtT = H.astype(np.float64)  # (n_det, n_errors)

        log_liks = np.zeros(self.N)
        # Per-pair variance of an empirical covariance estimator:
        # Var(C_ij) ≈ p_i(1-p_i) p_j(1-p_j) / N ~ p_i p_j / N at low rates.
        # Critical fix: when empirical p_i = 0 (detector never fired in this window),
        # Laplace-smooth to (k+1)/(N+2) so a zero-count detector gets a realistic
        # uncertainty ≈ 1/N rather than a collapsing-to-1e-10 floor. Without this fix,
        # zero-count detectors wildly penalise any non-trivial predicted covariance —
        # see test_pair_correlation_likelihood_is_informative in tests/.
        n_batch = W.shape[0]
        p_i_smooth = (W.sum(axis=0) + 1.0) / (n_batch + 2.0)
        sigma2_pair = (p_i_smooth[:, None] * p_i_smooth[None, :]) / max(n_batch, 1)
        iu = np.triu_indices(C_emp.shape[0], k=1)
        for p in range(self.N):
            theta_p = self.theta[p]
            C_pred = (HtT * theta_p[None, :]) @ HtT.T  # (n_det, n_det)
            diff = C_emp - C_pred
            log_liks[p] = -0.5 * np.sum((diff[iu] ** 2) / sigma2_pair[iu])
        return log_liks

    def posterior_mean(self) -> np.ndarray:
        w = np.exp(self.log_w - self.log_w.max())
        w /= w.sum()
        return (w[:, None] * self.theta).sum(axis=0)


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    E, n_det = 50, 10
    H = (rng.random((n_det, E)) < 0.15).astype(np.uint8)
    obs_mat = (rng.random((1, E)) < 0.05).astype(np.uint8)
    drift = DriftKernel(timescale_s=3600.0, amplitude=0.2, dt_s=1e-3)

    for lk in ("independent_bernoulli", "pair_correlation"):
        pf = ParticleFilter(n_particles=500, n_errors=E, drift=drift, likelihood=lk,
                           batch_size=100, prior_mean=np.full(E, 1e-5))
        for t in range(500):
            s = (rng.random(n_det) < 0.05).astype(np.uint8)
            pf.step(s, H, obs_mat, true_obs_flip=0)
        post = pf.posterior_mean()
        print(f"[smoke] {lk:>24s}  post mean {post.mean():.3e}   (range [{post.min():.2e}, {post.max():.2e}])")
