"""Phase 0.5 data-access smoke tests for entropy_effective_dimension.

Substrate: Pythia training-checkpoint suite (Biderman et al. 2023,
arXiv:2304.01373). 154 checkpoints per scale × 5 scales (70M, 160M,
410M, 1B, 1.4B fp16) = 770 model loads over the 100-cell (N, t) grid.

We must verify:
1. Pythia weights load at the smallest scale (70M).
2. Intermediate-checkpoint access path works (HuggingFace revision= tags).
3. Residual-stream activations can be hooked with PyTorch forward hooks
   (the streaming covariance accumulator path).
"""

from __future__ import annotations

import pytest


def test_torch_cuda_available():
    """RTX 3060 detected; fp16 works."""
    import torch
    assert torch.cuda.is_available()
    assert "RTX" in torch.cuda.get_device_name(0) or "GPU" in torch.cuda.get_device_name(0)


def test_stack_imports():
    import transformers
    import powerlaw
    import mrestimator
    assert transformers.__version__.startswith(("4.", "5."))
    assert powerlaw.__version__.startswith("2.")
    assert mrestimator.__version__.startswith("0.")


@pytest.mark.network
def test_pythia_70m_final_loads():
    """Smallest Pythia model loads and exposes residual-stream shape d_model."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    name = "EleutherAI/pythia-70m"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(
        name, torch_dtype=torch.float16
    ).cuda()
    model.eval()
    ids = tok("hello world", return_tensors="pt").input_ids.cuda()
    with torch.no_grad():
        out = model(ids, output_hidden_states=True)
    # Pythia-70M has 6 layers; 7 hidden states (embedding + 6 blocks)
    assert len(out.hidden_states) == 7
    # d_model = 512 for pythia-70m
    assert out.hidden_states[-1].shape[-1] == 512


@pytest.mark.network
def test_pythia_intermediate_checkpoint_loads():
    """A mid-training Pythia checkpoint loads via revision= tag.

    Biderman 2023 publishes 154 revisions per scale: step1, step2, step4,
    ..., step143000. Test one of the log-spaced early ones — these are the
    checkpoints the induction-head-emergence and ICL dynamics live in.
    """
    import torch
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(
        "EleutherAI/pythia-70m",
        revision="step1000",
        torch_dtype=torch.float16,
    ).cuda()
    assert next(model.parameters()).dtype == torch.float16


@pytest.mark.network
def test_forward_hooks_capture_residual_stream():
    """Streaming covariance accumulator relies on PyTorch forward hooks
    producing layer-resolved residual-stream tensors.

    This is the hook-path smoke test — if activations can't be
    captured this way, the streaming covariance plan fails.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    name = "EleutherAI/pythia-70m"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(
        name, torch_dtype=torch.float16
    ).cuda().eval()

    captured = {}

    def hook(module, inputs, output):
        # Pythia GPTNeoXBlock returns a tuple; residual stream is output[0].
        tensor = output[0] if isinstance(output, tuple) else output
        captured["shape"] = tuple(tensor.shape)
        captured["dtype"] = tensor.dtype

    # Pythia layers: model.gpt_neox.layers[0..5]
    handle = model.gpt_neox.layers[3].register_forward_hook(hook)
    try:
        ids = tok("testing residual stream", return_tensors="pt").input_ids.cuda()
        with torch.no_grad():
            model(ids)
    finally:
        handle.remove()
    assert "shape" in captured
    assert captured["shape"][-1] == 512  # d_model
    assert captured["dtype"] == torch.float16
