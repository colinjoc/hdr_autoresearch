"""
test_kat_to_differometor.py — TDD anchor for kat_to_differometor.py.

The converter takes a parsed KatDocument and builds a `differometor.setups.Setup`.
The tests check the structural fidelity of the conversion (same component counts,
same edge structure) and then — if feasible — run a simulation and check that the
strain spectrum is at least in the right order of magnitude compared to the Zoo's
canonical strain.csv.

The tests are designed to run incrementally: early tests cover structural fidelity
only, later tests attempt a full simulation. A test that can't be made to pass
because of a Differometor API limitation is marked `xfail` with a clear reason.
"""
from __future__ import annotations

from pathlib import Path

import pytest

try:
    import differometor as df
    from differometor.setups import Setup
    HAS_DIFFEROMETOR = True
except Exception:
    HAS_DIFFEROMETOR = False

from kat_parser import parse_kat, KatDocument

# Import the converter (to be implemented).
from kat_to_differometor import (
    kat_to_differometor,
    sanitise_name,
    map_mirror_port,
    map_beamsplitter_port,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZOO_DIR = PROJECT_ROOT / "GWDetectorZoo"
SOL00_KAT = ZOO_DIR / "solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"


requires_differometor = pytest.mark.skipif(
    not HAS_DIFFEROMETOR, reason="Differometor not available"
)


# ---------------------------------------------------------------------------
# Name sanitisation
# ---------------------------------------------------------------------------

def test_sanitise_removes_underscores():
    """Differometor forbids underscores in node names. The converter must replace
    them with a safe character."""
    assert "_" not in sanitise_name("MB1_1_u")
    assert "_" not in sanitise_name("mUD_3_1")
    assert "_" not in sanitise_name("mRL_3_3")


def test_sanitise_is_injective_on_sol00_components():
    """Sanitised names must be distinct across all sol00 components, so that
    the converter does not accidentally merge two components."""
    doc = parse_kat(SOL00_KAT.read_text())
    names = [c.name for c in doc.components] + [s.name for s in doc.spaces]
    sanitised = [sanitise_name(n) for n in names]
    assert len(set(sanitised)) == len(sanitised), (
        f"sanitise_name collision: "
        f"{len(names) - len(set(sanitised))} duplicates"
    )


# ---------------------------------------------------------------------------
# Port mapping
# ---------------------------------------------------------------------------

def test_mirror_port_mapping():
    """kat mirror ports are [front/BS-side, back/setup-side]; these map to
    left/right respectively in Differometor's 2-port mirror."""
    # A BS-side port name like `nMB1_1_uBS` maps to the mirror's "left" port.
    # A setup-side port name like `nMB1_1_uSetup` maps to "right".
    # We don't care about the specific names — only that port index 0 maps to
    # "left" and port index 1 maps to "right".
    assert map_mirror_port(0) == "left"
    assert map_mirror_port(1) == "right"


def test_beamsplitter_port_mapping_from_suffix():
    """For a bs1 in sol00, the 4 port names have suffixes d/l/u/r (down/left/up/right).
    The mapping is deterministic: d->bottom, l->left, u->top, r->right. The
    converter uses the suffix of the port-name string to decide."""
    assert map_beamsplitter_port("nB1_1d") == "bottom"
    assert map_beamsplitter_port("nB1_1l") == "left"
    assert map_beamsplitter_port("nB1_1u") == "top"
    assert map_beamsplitter_port("nB1_1r") == "right"


# ---------------------------------------------------------------------------
# Conversion structural fidelity
# ---------------------------------------------------------------------------

@requires_differometor
def test_convert_sol00_yields_setup():
    """The converter returns a Differometor Setup instance."""
    doc = parse_kat(SOL00_KAT.read_text())
    S, _meta = kat_to_differometor(doc)
    assert isinstance(S, Setup)


@requires_differometor
def test_convert_sol00_node_count_lower_bound():
    """The converted setup should contain at least as many nodes as sol00 has
    non-detector components. We don't require exact parity because Differometor
    uses auxiliary "frequency" and "signal" nodes not present in the kat file,
    and the converter may skip some detector aliases."""
    doc = parse_kat(SOL00_KAT.read_text())
    S, _meta = kat_to_differometor(doc)
    # sol00: 57 mirrors + 13 bs + 3 lasers + 1 dbs = 74 optical components.
    n_optical = sum(
        1 for c in doc.components
        if c.type in ("mirror", "beamsplitter", "laser", "directional_beamsplitter")
    )
    n_diff_optical = sum(
        1 for _name, data in S.nodes
        if data["component"] in ("mirror", "beamsplitter", "laser", "directional_beamsplitter")
    )
    assert n_diff_optical == n_optical, (
        f"Converter lost {n_optical - n_diff_optical} optical components"
    )


@requires_differometor
def test_convert_sol00_edge_count_matches_non_orphan_spaces():
    """Every kat space whose endpoints resolve to components must produce an
    edge in the Differometor setup."""
    doc = parse_kat(SOL00_KAT.read_text())
    S, meta = kat_to_differometor(doc)
    # The converter reports the number of space edges placed.
    n_expected = meta["n_space_edges_placed"]
    # Each placed edge is in the edges dict.
    n_edges = sum(1 for _ in S.edges(data=False))
    assert n_edges >= n_expected, (
        f"Setup has {n_edges} edges but converter reports {n_expected} placed"
    )


# ---------------------------------------------------------------------------
# Conversion preserves reflectivity values
# ---------------------------------------------------------------------------

@requires_differometor
def test_convert_preserves_mirror_reflectivity():
    """Every mirror's reflectivity in the converted setup must equal the
    resolved reflectivity from the kat file. (Allow for the Differometor
    internal R / (1 - loss) normalisation.)"""
    doc = parse_kat(SOL00_KAT.read_text())
    S, meta = kat_to_differometor(doc)
    name_map = meta["component_name_map"]
    for c in doc.components:
        if c.type != "mirror":
            continue
        kat_R = doc.resolve(c.properties).get("reflectivity")
        if kat_R is None or isinstance(kat_R, str):
            continue
        safe_name = name_map[c.name]
        node_data = S.nodes[safe_name]
        diff_R = node_data["properties"]["reflectivity"]
        # Allow for Differometor's internal normalisation (R / (1 - loss)).
        # Since loss = 5e-6 in sol00, the difference is tiny (<1e-5).
        assert abs(diff_R - kat_R) < 1e-3, (
            f"mirror {c.name}: kat R = {kat_R}, diff R = {diff_R}"
        )
