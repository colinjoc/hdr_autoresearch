"""pytest configuration — register custom markers."""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "network: test requires internet access (HuggingFace Pythia)",
    )
    config.addinivalue_line(
        "markers",
        "slow: test takes > 30 seconds (model load)",
    )
    config.addinivalue_line(
        "markers",
        "gpu: test requires CUDA",
    )
