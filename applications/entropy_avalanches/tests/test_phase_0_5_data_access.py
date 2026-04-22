"""Phase 0.5 data-access smoke tests for entropy_avalanches.

The project's substrates are pretrained models (GPT-2, Pythia, Gemma-2) and
SAE weights (Gemma Scope). Per
`~/.claude/projects/-home-col/memory/feedback_verify_data_access_before_phase_0`,
these must pass before Phase 1 pipeline code is written.

Run:
    ./venv/bin/python -m pytest tests/test_phase_0_5_data_access.py -v
"""

from __future__ import annotations

import pytest


def test_torch_importable_with_gpu():
    """torch + CUDA both present; we need fp16 inference on the RTX 3060."""
    import torch
    assert torch.cuda.is_available(), (
        "CUDA unavailable — check driver / torch CUDA-version pairing"
    )
    dev = torch.cuda.get_device_name(0)
    assert "RTX" in dev or "GPU" in dev or "Tesla" in dev, f"unexpected: {dev}"
    # fp16 must work for Pythia-2.8B to fit.
    x = torch.zeros(1024, 1024, dtype=torch.float16, device="cuda")
    y = x @ x
    assert y.dtype == torch.float16


def test_transformers_and_powerlaw_importable():
    """Pipeline stack loads cleanly."""
    import transformers
    import powerlaw
    import mrestimator
    assert transformers.__version__.startswith(("4.", "5."))
    assert powerlaw.__version__.startswith("2.")
    assert mrestimator.__version__.startswith("0.")


@pytest.mark.network
def test_gpt2_small_loads():
    """GPT-2 small (124M) downloads and one forward pass produces activations."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained(
        "gpt2", torch_dtype=torch.float16
    ).cuda()
    model.eval()
    ids = tok("hello world", return_tensors="pt").input_ids.cuda()
    with torch.no_grad():
        out = model(ids, output_hidden_states=True)
    assert out.hidden_states is not None
    # 13 hidden states = embedding + 12 transformer blocks
    assert len(out.hidden_states) == 13
    # final hidden state shape = (batch, seq, d_model=768)
    assert out.hidden_states[-1].shape[-1] == 768


@pytest.mark.network
@pytest.mark.slow
def test_pythia_160m_loads():
    """Pythia-160M loads — confirms EleutherAI HuggingFace access path.

    We don't load 1.4B/2.8B in the smoke test — 160M is the smallest Pythia
    and adequate to prove the route. Larger scales in Phase 1.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    name = "EleutherAI/pythia-160m"
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(
        name, torch_dtype=torch.float16
    ).cuda()
    model.eval()
    ids = tok("hello world", return_tensors="pt").input_ids.cuda()
    with torch.no_grad():
        out = model(ids, output_hidden_states=True)
    assert out.hidden_states is not None
    assert len(out.hidden_states) >= 13  # 12 layers + embedding


@pytest.mark.network
def test_gemma_scope_weights_reachable():
    """Gemma Scope SAE weights are on HuggingFace at `google/gemma-scope`.

    We only check reachability via the hub-api, not download. Full SAE load
    is a Phase 1 step (1.2-2.4 GB per width × layer).
    """
    from huggingface_hub import HfApi
    api = HfApi()
    info = api.model_info("google/gemma-scope-2b-pt-res")
    assert info.sha is not None
    # Must have SAE files listed
    files = api.list_repo_files("google/gemma-scope-2b-pt-res")
    # Gemma Scope ships SAE weights as params.npz files under
    # {layer}/width_{w}/average_l0_{k}/ — not safetensors.
    has_sae = any(f.endswith("params.npz") for f in files)
    assert has_sae, f"expected params.npz SAE files, found e.g.: {files[:5]}"
