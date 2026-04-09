"""
test_light_path_trace.py — TDD anchor for light_path_trace.py.

The topology tracer must build an optical graph from a parsed KatDocument:
  - Nodes  : components (mirror, beamsplitter, laser, dbs, pd, qhd, ...)
  - Edges  : free-spaces, which have two endpoint "nodeXXX" strings that
             each correspond to a named port on a component.

The tracer answers:
  1. Which components are in the same connected component as each laser?
  2. Which mirrors are "active" (reachable from a laser via spaces)?
  3. Which of the 6 arm-cavity-class spaces connect active components, and
     which endpoint-component pairs do they couple?
  4. Are any pair of moderate-R mirrors in series on an active light path,
     implying compound-cavity coupling?

Tests pin the canonical sol00 numbers. The test file is written BEFORE the
implementation; all asserts are against numbers we can derive by hand
from sol00's .kat file.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from kat_parser import KatDocument, parse_kat
from light_path_trace import (
    OpticalGraph,
    build_optical_graph,
    active_components,
    arm_cavity_endpoints,
    is_arm_cavity_length,
    series_mirror_pairs_on_active_path,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZOO_DIR = PROJECT_ROOT / "GWDetectorZoo"
SOL00_KAT = ZOO_DIR / "solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"


@pytest.fixture(scope="module")
def sol00_doc() -> KatDocument:
    return parse_kat(SOL00_KAT.read_text())


@pytest.fixture(scope="module")
def sol00_graph(sol00_doc: KatDocument) -> OpticalGraph:
    return build_optical_graph(sol00_doc)


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def test_graph_has_all_components_as_nodes(sol00_doc, sol00_graph):
    """Every component in the parsed document becomes a node."""
    # 57 mirrors + 13 bs + 1 dbs + 3 lasers + 2 pd1 + 2 pd0 + 1 qhd = 79
    assert sol00_graph.num_nodes() == len(sol00_doc.components)
    for c in sol00_doc.components:
        assert c.name in sol00_graph.nodes


def test_graph_edges_are_free_spaces(sol00_doc, sol00_graph):
    """Every parsed `s` free-space becomes an undirected edge between two nodes,
    provided both port-nodes reference a component port that actually exists."""
    # We allow edges to be dropped if they reference orphan ports that no
    # component declares (the kat format is permissive). But the bulk of the
    # 78 spaces must map to edges.
    assert sol00_graph.num_edges() >= 60


def test_graph_edge_carries_length(sol00_graph):
    """Each edge records its free-space length so the caller can filter by it."""
    for u, v, data in sol00_graph.iter_edges():
        assert "length" in data
        assert isinstance(data["length"], float)
        assert data["length"] >= 0


# ---------------------------------------------------------------------------
# Connected components and active topology
# ---------------------------------------------------------------------------

def test_lasers_are_connected_to_mirrors(sol00_doc, sol00_graph):
    """The 3 lasers each sit in a connected component of the optical graph that
    contains at least one mirror (otherwise the laser has nothing to illuminate)."""
    laser_names = [c.name for c in sol00_doc.components if c.type == "laser"]
    assert len(laser_names) == 3
    for L in laser_names:
        cc = sol00_graph.connected_component(L)
        mirrors_in_cc = [n for n in cc if sol00_graph.nodes[n]["type"] == "mirror"]
        assert len(mirrors_in_cc) > 0, f"laser {L} is isolated — no mirrors reachable"


def test_active_components_is_union_of_laser_ccs(sol00_doc, sol00_graph):
    """The 'active' topology is the union of connected components containing
    at least one laser. The test is: every component in the union is reachable
    from some laser."""
    active = active_components(sol00_graph)
    laser_names = [c.name for c in sol00_doc.components if c.type == "laser"]
    for name in active:
        reach_from_any = any(
            name in sol00_graph.connected_component(L) for L in laser_names
        )
        assert reach_from_any, f"{name} claimed active but unreachable from any laser"


def test_active_mirror_count_is_positive_but_not_all(sol00_doc, sol00_graph):
    """Some mirrors should be in the active (laser-reachable) subgraph and
    some should not — sol00 has 20 transparent R<0.001 mirrors that may or
    may not be in the active graph. The test only checks the count is in a
    sane range (1..57)."""
    active = active_components(sol00_graph)
    active_mirrors = [
        n for n in active if sol00_graph.nodes[n]["type"] == "mirror"
    ]
    assert 1 <= len(active_mirrors) <= 57


# ---------------------------------------------------------------------------
# Arm-cavity class spaces
# ---------------------------------------------------------------------------

def test_is_arm_cavity_length_filter():
    """Arm-cavity class is length > 1000 m."""
    assert is_arm_cavity_length(3670.8421641502273)
    assert is_arm_cavity_length(3846.9567246813313)
    assert not is_arm_cavity_length(276.0653407423848)
    assert not is_arm_cavity_length(1.0)


def test_six_arm_cavity_spaces(sol00_doc):
    """sol00 has exactly 6 spaces at arm-cavity-class length (3670 or 3847 m)."""
    arm_spaces = [s for s in sol00_doc.spaces if is_arm_cavity_length(s.length)]
    assert len(arm_spaces) == 6

    # 3 at ~3670.84 (rounds to 3671), 3 at ~3846.96 (rounds to 3847)
    lens = sorted(round(s.length) for s in arm_spaces)
    assert lens == [3671, 3671, 3671, 3847, 3847, 3847]


def test_arm_cavity_endpoint_components(sol00_doc, sol00_graph):
    """Each arm-cavity space connects two specific components. Map each arm
    space to (component_a, component_b). All 6 should connect two named
    components (no orphans)."""
    endpoints = arm_cavity_endpoints(sol00_doc, sol00_graph)
    assert len(endpoints) == 6
    for sp_name, (ca, cb, length) in endpoints.items():
        assert ca is not None and cb is not None, (
            f"arm space {sp_name} has an orphan endpoint: ({ca}, {cb})"
        )
        assert length > 1000


# ---------------------------------------------------------------------------
# Compound-cavity candidates
# ---------------------------------------------------------------------------

def test_series_mirror_pairs_exist(sol00_doc, sol00_graph):
    """If two moderate-R mirrors sit at opposite ends of the same (non-1m
    default, non-arm-class) free space on the active path, they form a
    compound-cavity candidate. We don't pin the exact count — just that the
    helper runs and returns a list of (m1, m2, length) tuples."""
    pairs = series_mirror_pairs_on_active_path(
        sol00_doc,
        sol00_graph,
        r_min=0.05,
        r_max=0.95,
    )
    assert isinstance(pairs, list)
    for m1, m2, length in pairs:
        assert m1 in sol00_graph.nodes
        assert m2 in sol00_graph.nodes
        assert sol00_graph.nodes[m1]["type"] == "mirror"
        assert sol00_graph.nodes[m2]["type"] == "mirror"
        assert length > 0
