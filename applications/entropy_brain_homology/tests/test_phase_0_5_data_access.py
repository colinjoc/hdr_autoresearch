"""Phase 0.5 data-access smoke tests for Allen Neuropixels via DANDI.

Why DANDI instead of allensdk: allensdk has a hard Python-3.12 compat
issue (requires pre-pkgutil.ImpImporter-removal numpy). DANDI hosts the
same Allen Institute Neuropixels Visual Coding data as native NWB files
under dandisets 000021 (Brain Observatory 1.1) and 000022 (Functional
Connectivity). `dandi` + `pynwb` are Python-3.12-clean.

Per CLAUDE.md TDD rule and memory feedback_verify_data_access_before_phase_0:
these tests MUST pass before Phase 1 pipeline code is written.

Run:  ./venv/bin/python -m pytest tests/test_phase_0_5_data_access.py -x --tb=short
Slow gate: ./venv/bin/python -m pytest tests/ -m slow
"""

from __future__ import annotations

import pathlib

import pytest

ALLEN_VISUAL_CODING_DANDISET = "000021"  # Allen Brain Observatory 1.1 Neuropixels


def test_dandi_importable():
    """dandi + pynwb install cleanly and the client symbol imports."""
    from dandi.dandiapi import DandiAPIClient
    import pynwb
    assert DandiAPIClient is not None
    assert pynwb.__version__.startswith("3.")


@pytest.mark.network
def test_dandiset_resolves():
    """The Allen Visual Coding dandiset 000021 metadata fetches from DANDI API."""
    from dandi.dandiapi import DandiAPIClient
    with DandiAPIClient() as client:
        dandiset = client.get_dandiset(ALLEN_VISUAL_CODING_DANDISET, "draft")
        meta = dandiset.get_raw_metadata()
        assert meta["name"]
        assert "Allen" in meta["name"] or "Neuropixels" in meta.get(
            "description", ""
        )


@pytest.mark.network
def test_asset_list_nonempty():
    """Dandiset 000021 has NWB assets — at least the 58 expected sessions."""
    from dandi.dandiapi import DandiAPIClient
    with DandiAPIClient() as client:
        dandiset = client.get_dandiset(ALLEN_VISUAL_CODING_DANDISET, "draft")
        assets = list(dandiset.get_assets())
    assert len(assets) >= 50, f"expected 50+ NWB sessions, got {len(assets)}"
    nwb_assets = [a for a in assets if a.path.endswith(".nwb")]
    assert len(nwb_assets) >= 50


@pytest.mark.network
def test_asset_download_url_reachable():
    """An asset's content-download URL resolves — proves the Phase 1 path exists.

    We don't actually download here (full NWB files are ~2 GB each and
    Phase 0.5 is a 15-minute reachability gate). Phase 1 will select the
    specific session(s) with suitable units tables and stream or download
    them; that's where data-selection logic belongs.
    """
    from dandi.dandiapi import DandiAPIClient
    import requests
    with DandiAPIClient() as client:
        dandiset = client.get_dandiset(
            ALLEN_VISUAL_CODING_DANDISET, "draft"
        )
        assets = list(dandiset.get_assets())
        nwb_assets = [a for a in assets if a.path.endswith(".nwb")]
        asset = nwb_assets[0]
        url = asset.get_content_url(follow_redirects=1, strip_query=False)
    # Range GET first 8 KB — proves the data channel works without downloading GB.
    # (S3-signed URLs reject HEAD without SigV4, so we skip HEAD.)
    resp = requests.get(
        url,
        headers={"Range": "bytes=0-8191"},
        allow_redirects=True,
        timeout=60,
    )
    assert resp.status_code in (200, 206), (
        f"expected 200/206, got {resp.status_code}"
    )
    assert len(resp.content) > 1000, f"got only {len(resp.content)} bytes"
    # NWB files are HDF5 — first bytes are the HDF5 magic number.
    assert resp.content[:8] == b"\x89HDF\r\n\x1a\n", "not an HDF5 file"
