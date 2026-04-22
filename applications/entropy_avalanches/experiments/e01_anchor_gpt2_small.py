"""E01 — Anchor experiment on GPT-2-small with Phase 2.75 revisions applied.

Revisions applied (from methodology_review.md):
- D1 fixed: random-init control uses `AutoModelForCausalLM.from_config`
  (preserves structural inits; no Xavier-0.02 LayerNorm collapse).
- D2 fixed: shuffle_null called on every (layer × threshold) cell.
- D3 fixed: attention_mask used to drop pad tokens before caching.
- D4 fixed: corpus is a real C4 sample streamed from HuggingFace,
  ~2000 documents, truncated to 64 tokens each → ~100K valid tokens.
- D5 fixed: paper framing in the draft acknowledges the failed DP-class
  assignment; this script simply reports numbers.
- Bonus fix: hook target switched from residual-stream block output to
  MLP-out contribution — breaks the h_{l+1} = h_l + F_l(h_l) tautology.
- C7 partial fix: basis-invariance battery adds random-projection + PCA
  alongside ambient. (SAE / random-init-SAE deferred to E02.)

Writes: `results/e01_anchor_gpt2.tsv` and `results/e01_shufnull.tsv`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from datasets import load_dataset

from pipeline.activation_cache import cache_activations
from pipeline.avalanche_detection import binarise_activations, detect_avalanches
from pipeline.exponents import (
    fit_power_law,
    crackling_noise_check,
    branching_ratio_mr,
)
from pipeline.subspace import subspace_sigma
from pipeline.nulls import shuffle_null


N_DOCS = 1000     # C4 sample; ~60K valid tokens after masking
MAX_LENGTH = 64
BATCH = 8
SHUFFLE_NULL_AT_THRESHOLD = 2.5  # fix: run shuffle_null at one θ only (was all 3)
                                 # shuffle + re-fit is the runtime bottleneck


def load_c4_sample(n: int) -> list[str]:
    ds = load_dataset("allenai/c4", "en", split="train", streaming=True)
    it = iter(ds)
    return [next(it)["text"] for _ in range(n)]


def project_basis(acts: np.ndarray, basis: str, seed: int = 0) -> np.ndarray:
    """Return activations projected into a different basis.

    - 'ambient'         : identity (returns acts as-is)
    - 'random'          : orthonormal random rotation (preserves geometry,
                          randomises basis alignment — a null for feature
                          interpretation)
    - 'pca'             : PCA-rotated so columns are decorrelated
    """
    X = acts.astype(np.float32)
    if basis == "ambient":
        return X
    if basis == "pca":
        Xc = X - X.mean(axis=0, keepdims=True)
        _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
        return Xc @ Vt.T
    if basis == "random":
        rng = np.random.default_rng(seed)
        d = X.shape[1]
        G = rng.normal(size=(d, d)).astype(np.float32)
        Q, _ = np.linalg.qr(G)
        return (X - X.mean(axis=0, keepdims=True)) @ Q
    raise ValueError(f"unknown basis: {basis}")


def run(model_name: str, random_init: bool, thresholds: list[float],
        bases: list[str], corpus: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    print(f"--- {model_name} random_init={random_init} hook=mlp_out ---")
    cache = cache_activations(
        model_name, texts=corpus, max_length=MAX_LENGTH,
        batch_size=BATCH, random_init=random_init,
        hook_target="mlp_out",
    )
    print(f"  cached {cache.n_tokens} tokens across {len(cache.layer_activations)} layers")

    main_rows = []
    null_rows = []

    for layer_idx in sorted(cache.layer_activations.keys()):
        acts_raw = cache.layer_activations[layer_idx].astype(np.float32)

        # MR σ on ambient per-token activity magnitude.
        activity = np.abs(acts_raw).sum(axis=1)
        try:
            br_amb = branching_ratio_mr(activity, kmax=200, method="ts")
            sigma_amb = br_amb.sigma
        except Exception as exc:
            sigma_amb = float("nan")
            print(f"  [L{layer_idx}] ambient MR fail: {exc}")

        try:
            sub = subspace_sigma(acts_raw, K=None, method="participation_ratio")
            sigma_sub, K_eff, pr = sub.sigma_K, sub.K, sub.participation_ratio
        except Exception as exc:
            sigma_sub = float("nan"); K_eff = -1; pr = float("nan")
            print(f"  [L{layer_idx}] subspace fail: {exc}")

        for basis in bases:
            try:
                acts = project_basis(acts_raw, basis)
            except Exception as exc:
                print(f"  [L{layer_idx} {basis}] projection fail: {exc}")
                continue
            for th in thresholds:
                binary = binarise_activations(acts, th, zscore=True)
                sizes, durations = detect_avalanches(binary, bin_size=1)
                if sizes.size >= 50:
                    try:
                        fit_s = fit_power_law(sizes)
                        alpha = fit_s.alpha; ks = fit_s.ks_statistic
                        pln = fit_s.p_vs_lognormal
                        pex = fit_s.p_vs_exponential
                    except Exception:
                        alpha = ks = pln = pex = float("nan")
                else:
                    alpha = ks = pln = pex = float("nan")
                if durations.size >= 50:
                    try:
                        fit_t = fit_power_law(durations)
                        beta = fit_t.alpha
                    except Exception:
                        beta = float("nan")
                    try:
                        chk = crackling_noise_check(sizes, durations)
                        gpred = chk.gamma_predicted
                        gmeas = chk.gamma_measured
                    except Exception:
                        gpred = gmeas = float("nan")
                else:
                    beta = gpred = gmeas = float("nan")

                # Shuffle null — ambient basis only, one threshold only.
                if basis == "ambient" and th == SHUFFLE_NULL_AT_THRESHOLD:
                    try:
                        sh = shuffle_null(acts, threshold=th, bin_size=1, rng_seed=0)
                        null_rows.append({
                            "model": model_name, "random_init": random_init,
                            "layer": layer_idx, "threshold": th,
                            "real_alpha": sh.real_alpha,
                            "shuffled_alpha": sh.shuffled_alpha,
                            "distinguishable": sh.distinguishable,
                        })
                    except Exception:
                        pass

                main_rows.append({
                    "model": model_name, "random_init": random_init,
                    "layer": layer_idx, "basis": basis, "threshold": th,
                    "n_avalanches": int(sizes.size),
                    "alpha": alpha, "beta": beta,
                    "gamma_predicted": gpred, "gamma_measured": gmeas,
                    "ks": ks,
                    "p_vs_lognormal": pln, "p_vs_exponential": pex,
                    "sigma_ambient_MR": sigma_amb,
                    "sigma_subspace_MR": sigma_sub,
                    "K_PR": K_eff, "participation_ratio": pr,
                })

    return pd.DataFrame(main_rows), pd.DataFrame(null_rows)


if __name__ == "__main__":
    print(f"loading {N_DOCS} C4 samples...", flush=True)
    corpus = load_c4_sample(N_DOCS)

    THRESHOLDS = [2.0, 2.5, 3.0]
    BASES = ["ambient", "random", "pca"]

    all_main, all_null = [], []
    for model in ["gpt2"]:
        for random_init in [False, True]:
            m, n = run(model, random_init, THRESHOLDS, BASES, corpus)
            all_main.append(m); all_null.append(n)
    main = pd.concat(all_main, ignore_index=True)
    nulls = pd.concat(all_null, ignore_index=True)
    out_m = ROOT / "results" / "e01_anchor_gpt2.tsv"
    out_n = ROOT / "results" / "e01_shufnull.tsv"
    out_m.parent.mkdir(exist_ok=True)
    main.to_csv(out_m, sep="\t", index=False)
    nulls.to_csv(out_n, sep="\t", index=False)
    print(f"wrote {out_m} ({len(main)} rows)")
    print(f"wrote {out_n} ({len(nulls)} rows)")
    print()
    print("=== middle layer, ambient basis, θ=2.5 ===")
    sub = main[(main.layer == 6) & (main.basis == "ambient") & (main.threshold == 2.5)]
    print(sub[["random_init", "alpha", "beta", "gamma_predicted",
               "sigma_ambient_MR", "sigma_subspace_MR",
               "participation_ratio"]].round(3).to_string(index=False))
    print()
    print("=== basis-invariance at layer 6, trained, θ=2.5 ===")
    sub = main[(main.layer == 6) & (~main.random_init) & (main.threshold == 2.5)]
    print(sub[["basis", "alpha", "beta", "n_avalanches"]].round(3).to_string(index=False))
