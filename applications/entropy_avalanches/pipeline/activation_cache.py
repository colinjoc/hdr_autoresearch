"""Activation caching for pretrained transformer language models.

Design:
- Load a HuggingFace model in fp16 on CUDA.
- Register forward hooks on each transformer block's output (the residual
  stream after that block).
- Tokenise a text corpus (default: a Pile-like sample; configurable).
- Cache per-layer residual-stream activations to disk as uint8 after a
  fixed threshold or as fp16 when basis-invariance calls for it.

Returns a layer-indexed dict of (tokens, d_model) tensors for downstream
avalanche detection + exponent fitting.
"""

from __future__ import annotations

import dataclasses
from typing import Iterable

import numpy as np
import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer


@dataclasses.dataclass
class ActivationCache:
    """Per-layer activations captured from a single forward pass."""

    model_name: str
    layer_activations: dict[int, np.ndarray]  # layer_idx -> (T, d_model) fp16
    d_model: int
    n_tokens: int
    hook_target: str  # 'block' (residual) | 'mlp_out' (MLP-only) | 'attn_out'


def _resolve_hook_modules(model, target: str) -> list[torch.nn.Module]:
    """Return the list of modules to hook for the given target.

    target:
    - 'block'    : block output (residual stream post-block). Convenient
                   but confounds upstream causality because h_{l+1} =
                   h_l + F_l(h_l).
    - 'mlp_out'  : block.mlp / block.ffn output. The MLP's *contribution*
                   F_l^{MLP}(h_l) — non-residual, avoids the σ tautology.
    """
    # GPT-2 family (transformer.h)
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        blocks = list(model.transformer.h)
        if target == "block":
            return blocks
        if target == "mlp_out":
            return [b.mlp for b in blocks]
        if target == "attn_out":
            return [b.attn for b in blocks]
    # Pythia / GPT-NeoX (gpt_neox.layers)
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        layers = list(model.gpt_neox.layers)
        if target == "block":
            return layers
        if target == "mlp_out":
            return [l.mlp for l in layers]
        if target == "attn_out":
            return [l.attention for l in layers]
    # Gemma / LLaMA / Mistral (model.layers)
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        layers = list(model.model.layers)
        if target == "block":
            return layers
        if target == "mlp_out":
            return [l.mlp for l in layers]
        if target == "attn_out":
            return [l.self_attn for l in layers]
    raise ValueError(f"Unknown architecture or target: {type(model).__name__}, {target}")


def cache_activations(
    model_name: str,
    texts: Iterable[str],
    max_length: int = 256,
    device: str = "cuda",
    batch_size: int = 4,
    random_init: bool = False,
    hook_target: str = "mlp_out",
) -> ActivationCache:
    """Forward-pass a corpus through a pretrained LM and cache activations.

    Parameters
    ----------
    model_name : HuggingFace model id
    texts      : iterable of strings
    max_length : truncate each input to this token length
    device     : 'cuda' or 'cpu'
    batch_size : mini-batch size (RTX 3060 constraint)
    random_init: if True, instantiate from config (preserves LayerNorm γ
                 and other structural inits). Avoids the degenerate
                 "xavier_normal + zero biases" collapse flagged in
                 Phase 2.75 D1.
    hook_target: 'mlp_out' (default — MLP contribution F_l^{MLP}(h_l); the
                 non-residual observable needed for causal σ — per
                 Phase 2.75 bonus finding), 'block' (residual stream,
                 confounded), or 'attn_out' (attention contribution).
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if random_init:
        # Fix for Phase 2.75 D1: instantiate from config only — preserves
        # the *structural* at-init distribution (LayerNorm γ=1, proper
        # Xavier/Kaiming scales as defined by the model's own _init_weights),
        # without touching pretrained values.
        config = AutoConfig.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_config(config).to(torch.float16)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16
        )
    model = model.to(device).eval()

    modules = _resolve_hook_modules(model, hook_target)
    captured: dict[int, list[np.ndarray]] = {i: [] for i in range(len(modules))}
    current_mask: list[np.ndarray] = []  # shared across hooks for current batch

    def make_hook(idx):
        def hook(_m, _inp, out):
            tensor = out[0] if isinstance(out, tuple) else out
            # (batch, seq, d_model) -> (batch, seq, d_model) float32.
            arr = tensor.detach().float().cpu().numpy()
            mask = current_mask[0]  # (batch, seq) bool
            # Flatten valid (non-pad) tokens only.
            valid = arr[mask]  # (n_valid, d_model)
            captured[idx].append(valid)
        return hook

    handles = [m.register_forward_hook(make_hook(i)) for i, m in enumerate(modules)]

    try:
        all_texts = list(texts)
        for i in range(0, len(all_texts), batch_size):
            batch = all_texts[i : i + batch_size]
            enc = tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                max_length=max_length,
                padding=True,
            )
            # Cache the attention-mask for hook-time filtering.
            mask_np = enc["attention_mask"].numpy().astype(bool)
            current_mask.clear()
            current_mask.append(mask_np)
            enc = {k: v.to(device) for k, v in enc.items()}
            with torch.no_grad():
                model(**enc)
    finally:
        for h in handles:
            h.remove()

    layer_arrays = {
        idx: np.concatenate(parts, axis=0).astype(np.float16)
        for idx, parts in captured.items()
        if parts
    }
    any_layer = next(iter(layer_arrays.values()))
    return ActivationCache(
        model_name=model_name,
        layer_activations=layer_arrays,
        d_model=int(any_layer.shape[-1]),
        n_tokens=int(any_layer.shape[0]),
        hook_target=hook_target,
    )
