"""
light_path_trace.py — Path 1 topology analyser for GWDetectorZoo .kat files.

Builds an optical graph from a parsed `KatDocument`:
  - Nodes: components keyed by their declared name (mirror, beamsplitter,
           laser, directional_beamsplitter, pd0, pd1, qnoised, qhd, squeezer).
  - Edges: free spaces. A free space `s <name> <len> <nodeA> <nodeB>` becomes
           an undirected edge between the two components whose port-name
           strings nodeA / nodeB match component ports.

Exposes:
  - build_optical_graph(doc) -> OpticalGraph
  - active_components(graph) -> set[str] : components reachable from any laser
  - arm_cavity_endpoints(doc, graph) -> dict[space_name, (comp_a, comp_b, len)]
  - series_mirror_pairs_on_active_path(doc, graph, r_min, r_max) -> list
  - is_arm_cavity_length(length_m) -> bool

The graph implementation is deliberately minimal (no networkx dependency):
an adjacency dict + a BFS for connected components is sufficient for the
sol00 scale (~79 nodes, ~78 edges).
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from kat_parser import KatDocument


ARM_CAVITY_LENGTH_M = 1000.0  # anything longer than this counts as arm-class


def is_arm_cavity_length(length_m: float) -> bool:
    """Return True if a space length is arm-cavity-class (> 1 km)."""
    return length_m > ARM_CAVITY_LENGTH_M


@dataclass
class OpticalGraph:
    """Minimal undirected multigraph keyed on component names.

    `nodes` maps component name -> dict of attributes (including 'type').
    `edges_by_node` maps component name -> list of (other_name, edge_attrs).
    `edges` is a flat list of (comp_a, comp_b, edge_attrs) triples.
    `port_to_component` maps a port-name string to ONE representative
       component that owns it; when multiple components share the same port
       (e.g. several detectors attached at `AtPD1` in sol00), all of them are
       in `port_to_components_all`, and zero-length "coincidence" edges link
       them together in the graph so that the laser-reachability analysis
       can see that they are physically co-located on the same optical node.
    """
    nodes: Dict[str, Dict[str, Any]]
    edges_by_node: Dict[str, List[Tuple[str, Dict[str, Any]]]]
    edges: List[Tuple[str, str, Dict[str, Any]]]
    port_to_component: Dict[str, str]
    port_to_components_all: Dict[str, List[str]] = None  # type: ignore[assignment]

    def num_nodes(self) -> int:
        return len(self.nodes)

    def num_edges(self) -> int:
        return len(self.edges)

    def iter_edges(self):
        for u, v, data in self.edges:
            yield u, v, data

    def neighbours(self, name: str) -> List[Tuple[str, Dict[str, Any]]]:
        return self.edges_by_node.get(name, [])

    def connected_component(self, start: str) -> Set[str]:
        """BFS from `start`, return the set of reachable node names (including
        `start` itself). If `start` is not in the graph, returns empty set."""
        if start not in self.nodes:
            return set()
        seen: Set[str] = {start}
        queue: deque = deque([start])
        while queue:
            cur = queue.popleft()
            for nbr, _ in self.neighbours(cur):
                if nbr not in seen:
                    seen.add(nbr)
                    queue.append(nbr)
        return seen


def build_optical_graph(doc: KatDocument) -> OpticalGraph:
    """Convert a parsed KatDocument into an optical graph.

    Node attributes:
      - type:   component type (from the parser)
      - props:  the resolved property dict (references substituted)
      - ports:  list of port-name strings declared on the component
    Edge attributes:
      - length: free-space length in metres
      - name:   the `s` statement's name (useful for matching to fsig targets)
    """
    nodes: Dict[str, Dict[str, Any]] = {}
    port_to_component: Dict[str, str] = {}
    port_to_components_all: Dict[str, List[str]] = defaultdict(list)

    for c in doc.components:
        try:
            resolved = doc.resolve(c.properties)
        except (KeyError, ValueError):
            resolved = dict(c.properties)
        nodes[c.name] = {
            "type": c.type,
            "props": resolved,
            "ports": list(c.ports),
        }
        for port in c.ports:
            # If a port name is already registered, it is a shared node
            # between two (or more) components — which happens in sol00 where
            # e.g. AtPD1 is the port of pd0, pd1, qnoised, qhd all at once.
            # Record the first-seen component as the representative, but keep
            # the full list so we can link all co-located components.
            if port not in port_to_component:
                port_to_component[port] = c.name
            port_to_components_all[port].append(c.name)

    edges: List[Tuple[str, str, Dict[str, Any]]] = []
    edges_by_node: Dict[str, List[Tuple[str, Dict[str, Any]]]] = defaultdict(list)

    # (1) Zero-length "coincidence" edges between components sharing a port.
    # These are not physical free spaces; they represent the fact that several
    # components are wired to the same optical node.
    for port, comps in port_to_components_all.items():
        if len(comps) < 2:
            continue
        rep = comps[0]
        for other in comps[1:]:
            attrs = {"length": 0.0, "name": f"__coincidence_{port}",
                     "port_a": port, "port_b": port}
            edges.append((rep, other, attrs))
            edges_by_node[rep].append((other, attrs))
            edges_by_node[other].append((rep, attrs))

    # (2) Real free-space edges.
    for sp in doc.spaces:
        comp_a = port_to_component.get(sp.node_a)
        comp_b = port_to_component.get(sp.node_b)
        if comp_a is None or comp_b is None:
            # Orphan space — one or both endpoints do not reference any
            # declared component port. This happens in the kat files when
            # a grid-cell was pinned out during optimisation.
            continue
        attrs = {"length": float(sp.length), "name": sp.name,
                 "port_a": sp.node_a, "port_b": sp.node_b}
        edges.append((comp_a, comp_b, attrs))
        edges_by_node[comp_a].append((comp_b, attrs))
        edges_by_node[comp_b].append((comp_a, attrs))

    return OpticalGraph(
        nodes=nodes,
        edges_by_node=dict(edges_by_node),
        edges=edges,
        port_to_component=port_to_component,
        port_to_components_all=dict(port_to_components_all),
    )


def active_components(graph: OpticalGraph) -> Set[str]:
    """Return the set of components reachable from any laser via spaces."""
    active: Set[str] = set()
    for name, attrs in graph.nodes.items():
        if attrs["type"] == "laser":
            active |= graph.connected_component(name)
    return active


def arm_cavity_endpoints(
    doc: KatDocument,
    graph: OpticalGraph,
) -> Dict[str, Tuple[Optional[str], Optional[str], float]]:
    """For each arm-cavity-class (>1 km) space, return the pair of components
    at its endpoints.

    Keys: space name (the same string that appears in fsig targets).
    Values: (component_a_name, component_b_name, length_m).

    If a space endpoint does not resolve to any component, that side is None.
    """
    result: Dict[str, Tuple[Optional[str], Optional[str], float]] = {}
    for sp in doc.spaces:
        if not is_arm_cavity_length(sp.length):
            continue
        ca = graph.port_to_component.get(sp.node_a)
        cb = graph.port_to_component.get(sp.node_b)
        result[sp.name] = (ca, cb, float(sp.length))
    return result


def _resolve_R(doc: KatDocument, comp_name: str, graph: OpticalGraph) -> Optional[float]:
    """Return the resolved reflectivity of a mirror by name, or None."""
    if comp_name not in graph.nodes:
        return None
    props = graph.nodes[comp_name]["props"]
    R = props.get("reflectivity")
    if R is None:
        return None
    if isinstance(R, str):
        return None
    try:
        return float(R)
    except (TypeError, ValueError):
        return None


def series_mirror_pairs_on_active_path(
    doc: KatDocument,
    graph: OpticalGraph,
    r_min: float = 0.05,
    r_max: float = 0.95,
) -> List[Tuple[str, str, float]]:
    """Find pairs of moderate-R mirrors that sit at opposite ends of the same
    free space, both in the active (laser-reachable) subgraph.

    These are candidates for compound-cavity coupling: two mirrors at R=0.95
    in series behave differently from one R=0.9025 mirror, but the *intensity
    transmission* is the same as a single mirror at a different effective
    reflectivity.

    Returns a list of (mirror_a, mirror_b, length_m), sorted by length.
    """
    active = active_components(graph)
    pairs: List[Tuple[str, str, float]] = []
    seen_edges: Set[Tuple[str, str]] = set()
    for u, v, data in graph.iter_edges():
        if u not in active or v not in active:
            continue
        if graph.nodes[u]["type"] != "mirror" or graph.nodes[v]["type"] != "mirror":
            continue
        R_u = _resolve_R(doc, u, graph)
        R_v = _resolve_R(doc, v, graph)
        if R_u is None or R_v is None:
            continue
        if not (r_min <= R_u <= r_max and r_min <= R_v <= r_max):
            continue
        key = tuple(sorted([u, v]))
        if key in seen_edges:
            continue
        seen_edges.add(key)
        pairs.append((key[0], key[1], data["length"]))
    pairs.sort(key=lambda t: t[2])
    return pairs
