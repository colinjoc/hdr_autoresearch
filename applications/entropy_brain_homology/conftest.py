"""pytest configuration — register custom markers for network / slow tests."""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "network: test requires internet access (DANDI API)",
    )
    config.addinivalue_line(
        "markers",
        "slow: test takes > 30 seconds (full NWB stream or session download)",
    )
