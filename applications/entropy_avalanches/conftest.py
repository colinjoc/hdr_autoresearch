"""pytest configuration for entropy_avalanches — register custom markers."""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "network: test requires internet access (HuggingFace / Gemma Scope)",
    )
    config.addinivalue_line(
        "markers",
        "slow: test takes > 30 seconds (model load, tokenisation pass)",
    )
    config.addinivalue_line(
        "markers",
        "gpu: test requires CUDA",
    )
