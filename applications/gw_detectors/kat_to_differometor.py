"""
kat_to_differometor.py — convert a parsed GWDetectorZoo `.kat` document into a
`differometor.setups.Setup`.

Scope:
- mirror (`m1`)              → differometor "mirror"
- beamsplitter (`bs1`)       → differometor "beamsplitter"
- laser (`l`)                → differometor "laser"
- directional_beamsplitter (`dbs`)  → differometor "directional_beamsplitter"
- space (`s`)                → differometor "space" edge, with source/target ports
- fsig injections            → differometor "signal" on the corresponding edge
- balanced homodyne (`qhd`)  → differometor "qhd" + two "qnoised" detectors

Not handled:
- photodetector / qnoised alone (no equivalent except as a direct "detector"
  attached to a target node/port — we approximate by attaching one `detector`
  to each of the two homodyne legs)

Naming:
- Differometor forbids `_` in node names. We replace `_` → `-`. Since kat
  components also don't use `-`, this is collision-free on sol00.

Port mapping:
- For mirrors (2 kat ports [port0, port1]):
    port0 → Differometor "left"
    port1 → Differometor "right"
- For beamsplitters (4 kat ports, named with suffix d/l/u/r):
    suffix d → "bottom"
    suffix l → "left"
    suffix u → "top"
    suffix r → "right"
- For lasers and dbs we use defaults.

Returns (Setup, meta) where `meta` is a dict with diagnostic information:
- `component_name_map`: {kat_name: safe_name}
- `space_edge_map`:     {kat_space_name: (src_safe, tgt_safe)}
- `n_space_edges_placed`: int
- `n_orphan_spaces`: int  (spaces whose endpoints don't map to components)
"""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

import differometor as df
from differometor.setups import Setup

from kat_parser import KatDocument


def sanitise_name(name: str) -> str:
    """Convert a kat name to a Differometor-safe name (no underscores)."""
    return name.replace("_", "-")


def map_mirror_port(kat_port_index: int) -> str:
    """Mirror ports: kat index 0 -> 'left', 1 -> 'right'."""
    return {0: "left", 1: "right"}[kat_port_index]


def map_beamsplitter_port(kat_port_name: str, port_index: Optional[int] = None) -> str:
    """Map a kat BS port to Differometor's bottom/left/top/right.

    In sol00 the port-name string has a trailing suffix d/l/u/r encoding the
    spatial orientation (down/left/up/right) of the attached mirror. For
    solutions where the suffix convention is not used (sol01 etc.), fall
    back to mapping port_index 0..3 -> left/top/right/bottom.
    """
    suffix_map = {
        "d": "bottom",
        "l": "left",
        "u": "top",
        "r": "right",
    }
    last = kat_port_name[-1]
    if last in suffix_map:
        return suffix_map[last]
    # Fallback to positional mapping
    index_map = {0: "left", 1: "top", 2: "right", 3: "bottom"}
    if port_index is not None and port_index in index_map:
        return index_map[port_index]
    return "left"


def _build_port_to_component_map(doc: KatDocument) -> Dict[str, Tuple[str, int]]:
    """Map each kat port-name string to (component_name, port_index).

    If multiple components share the same port string (e.g. several detectors
    at AtPD1 in sol00), the first one seen wins — subsequent ones are still
    recorded in `dupes` for later.
    """
    port_map: Dict[str, Tuple[str, int]] = {}
    for c in doc.components:
        for i, p in enumerate(c.ports):
            if p not in port_map:
                port_map[p] = (c.name, i)
    return port_map


def _safe_reflectivity(value, loss=5e-6) -> float:
    """Clamp reflectivity to Differometor's valid range."""
    if value is None:
        return 0.5
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.5
    # Differometor normalises reflectivity by (1 - loss). Values of exactly
    # 1.0 cause divisions-by-near-zero; clamp tight.
    if v < 0.0:
        return 0.0
    if v > 1.0 - loss - 1e-9:
        return 1.0 - loss - 1e-9
    return v


def kat_to_differometor(doc: KatDocument) -> Tuple[Setup, Dict[str, Any]]:
    """Convert a parsed KatDocument into a Differometor Setup.

    Parameters
    ----------
    doc : KatDocument
        Parsed kat file.

    Returns
    -------
    setup : differometor.setups.Setup
    meta  : dict with diagnostic information
    """
    S = Setup()
    name_map: Dict[str, str] = {}
    port_map = _build_port_to_component_map(doc)

    # ----- PASS 1: add all optical components as nodes -----
    for c in doc.components:
        safe = sanitise_name(c.name)
        name_map[c.name] = safe
        props = doc.resolve(c.properties)

        if c.type == "mirror":
            R = _safe_reflectivity(props.get("reflectivity"))
            loss = float(props.get("loss", 5e-6))
            tuning = float(props.get("tuning", 0.0))
            S.add("mirror", safe, reflectivity=R, loss=loss, tuning=tuning)

        elif c.type == "beamsplitter":
            R = _safe_reflectivity(props.get("reflectivity"))
            loss = float(props.get("loss", 5e-6))
            tuning = float(props.get("tuning", 0.0))
            alpha = float(props.get("angle", 45.0))
            # Differometor uses positive alpha only
            alpha = abs(alpha) if alpha != 0 else 45.0
            S.add("beamsplitter", safe,
                  reflectivity=R, loss=loss, tuning=tuning, alpha=alpha)

        elif c.type == "laser":
            power = float(props.get("power", 1.0))
            phase = float(props.get("phase", 0.0))
            S.add("laser", safe, power=power, phase=phase)

        elif c.type == "directional_beamsplitter":
            S.add("directional_beamsplitter", safe)

        elif c.type == "squeezer":
            freq = float(props.get("frequency", 0.0))
            db = float(props.get("db", 0.0))
            phase = float(props.get("phase", 0.0))
            S.add("squeezer", safe, db=db, angle=phase)

        # Detectors (pd0, pd1, qnoised, qhd, homodyne_detector) are handled
        # separately below — they are not optical nodes in Differometor.

    # ----- PASS 2: add free_mass suspensions for mirrors with mass attribute -----
    for c in doc.components:
        if c.type != "mirror":
            continue
        mass = doc.resolve(c.properties).get("mass")
        if mass is None or isinstance(mass, str):
            continue
        try:
            m_val = float(mass)
        except (TypeError, ValueError):
            continue
        if m_val <= 0:
            continue
        safe_target = name_map[c.name]
        # Pick a unique name for the free mass: "sus" + short hash of target
        fm_name = sanitise_name(f"sus{c.name}")
        try:
            S.add("free_mass", fm_name, mass=m_val, target=safe_target)
        except ValueError:
            # If the target has no mass-bearing property in Differometor, skip
            pass

    # ----- PASS 3: add space edges -----
    n_space_edges = 0
    n_orphan = 0
    space_edge_map: Dict[str, Tuple[str, str]] = {}
    for sp in doc.spaces:
        a_info = port_map.get(sp.node_a)
        b_info = port_map.get(sp.node_b)
        if a_info is None or b_info is None:
            n_orphan += 1
            continue
        comp_a, port_a_idx = a_info
        comp_b, port_b_idx = b_info

        # Only optical components may be space endpoints in Differometor.
        kat_type_a = _component_type_of(doc, comp_a)
        kat_type_b = _component_type_of(doc, comp_b)
        if kat_type_a not in _OPTICAL_TYPES or kat_type_b not in _OPTICAL_TYPES:
            n_orphan += 1
            continue

        # Differometor lasers must be SOURCES of edges, never targets. If we
        # accidentally picked a laser on the target side, swap endpoints.
        if kat_type_b == "laser" and kat_type_a != "laser":
            comp_a, comp_b = comp_b, comp_a
            port_a_idx, port_b_idx = port_b_idx, port_a_idx
            kat_type_a, kat_type_b = kat_type_b, kat_type_a
            sp_node_a, sp_node_b = sp.node_b, sp.node_a
        else:
            sp_node_a, sp_node_b = sp.node_a, sp.node_b

        src_safe = name_map[comp_a]
        tgt_safe = name_map[comp_b]

        src_port = _component_port_label(doc, comp_a, port_a_idx, sp_node_a)
        tgt_port = _component_port_label(doc, comp_b, port_b_idx, sp_node_b)

        try:
            S.space(src_safe, tgt_safe,
                    length=float(sp.length),
                    source_port=src_port,
                    target_port=tgt_port)
        except (ValueError, KeyError) as e:
            # Fallback: try with default ports if the chosen port is invalid
            # for this component type.
            try:
                S.space(src_safe, tgt_safe, length=float(sp.length))
            except (ValueError, KeyError):
                n_orphan += 1
                continue
        n_space_edges += 1
        space_edge_map[sp.name] = (src_safe, tgt_safe)

    # ----- PASS 4: fsig signal injections -----
    # Differometor "signal" nodes are added with target=edge_name.
    # Add a frequency node first.
    try:
        S.add("frequency", "f", frequency=1)
    except ValueError:
        pass

    n_signal_nodes = 0
    for si in doc.signal_injections:
        edge = space_edge_map.get(si.target)
        if edge is None:
            continue
        src_safe, tgt_safe = edge
        edge_name = f"{src_safe}_{tgt_safe}"
        signal_name = sanitise_name(f"sig{si.name}")
        try:
            S.add("signal", signal_name, target=edge_name,
                  amplitude=si.amplitude, phase=si.phase_deg)
            n_signal_nodes += 1
        except (ValueError, KeyError):
            continue

    # ----- PASS 5: detectors at the qhd port(s) -----
    # In sol00, the qhd is `qhd nodeFinalDet 180 AtPD1 AtPD2`.
    # AtPD1 and AtPD2 are "pseudo-nodes" shared by multiple non-optical
    # detectors (pd0/pd1/qnoised/qhd). The actual optical signal arrives at
    # these nodes via short free spaces (e.g. `SDet1`, `SDet2` in sol00,
    # `stoPD1`, `stoPD2` in sol01). The other end of that space may be a
    # mirror (sol00) or a beamsplitter (sol01). We need to find it, and we
    # need the specific Differometor port (left/top/right/bottom) that
    # corresponds to the kat port on that optical component.
    def _optical_endpoint(pseudo_node: str) -> Optional[Tuple[str, str]]:
        """Given a pseudo-node port-name string, return (component_kat_name,
        Differometor_port_label) for the optical component reached via a
        single space from that node. If no such component exists, return
        None."""
        for sp in doc.spaces:
            for (a, b) in ((sp.node_a, sp.node_b), (sp.node_b, sp.node_a)):
                if a == pseudo_node:
                    info = port_map.get(b)
                    if info is None:
                        continue
                    comp, idx = info
                    if _component_type_of(doc, comp) in _OPTICAL_TYPES:
                        port_label = _component_port_label(doc, comp, idx, b)
                        return (comp, port_label)
        return None

    detectors_attached = []
    det_name_counter: Dict[str, int] = {}
    for c in doc.components:
        if c.type != "homodyne_detector":
            continue
        port_nodes = c.ports  # e.g. ['AtPD1', 'AtPD2']
        noise_names = []
        det_names = []
        for pn in port_nodes:
            endpoint = _optical_endpoint(pn)
            if endpoint is None:
                continue
            target_comp, port_label = endpoint
            safe = name_map[target_comp]

            # Generate unique names — even if two qhd ports resolve to the
            # same component at different ports, the detector names must be
            # distinct.
            key = f"det{target_comp}{port_label}"
            count = det_name_counter.get(key, 0)
            det_name_counter[key] = count + 1
            det_name = sanitise_name(key if count == 0 else f"{key}{count}")
            noise_name = sanitise_name(f"noise{det_name}")

            try:
                S.add("qnoised", noise_name,
                      target=safe, port=port_label, direction="out",
                      auxiliary=True)
                S.add("detector", det_name,
                      target=safe, port=port_label, direction="out")
                det_names.append(det_name)
                noise_names.append(noise_name)
            except (ValueError, KeyError):
                continue
        if len(noise_names) == 2:
            try:
                S.add("qhd", sanitise_name(c.name),
                      detector1=noise_names[0],
                      detector2=noise_names[1],
                      phase=180.0)
            except (ValueError, KeyError):
                pass
        detectors_attached.extend(det_names)

    meta = {
        "component_name_map": name_map,
        "space_edge_map": space_edge_map,
        "n_space_edges_placed": n_space_edges,
        "n_orphan_spaces": n_orphan,
        "n_signal_nodes": n_signal_nodes,
        "n_detectors_attached": len(detectors_attached),
    }
    return S, meta


# ---------- helpers ----------

_OPTICAL_TYPES = {
    "mirror", "beamsplitter", "laser", "directional_beamsplitter", "squeezer",
}


def _component_type_of(doc: KatDocument, name: str) -> Optional[str]:
    for c in doc.components:
        if c.name == name:
            return c.type
    return None


def _component_port_label(
    doc: KatDocument,
    comp_name: str,
    port_idx: int,
    port_name_string: str,
) -> str:
    """Map a kat port index (0..3) to the Differometor port label
    (left/top/right/bottom) for a given component type."""
    ctype = _component_type_of(doc, comp_name)
    if ctype == "mirror":
        return map_mirror_port(port_idx)
    if ctype == "beamsplitter":
        return map_beamsplitter_port(port_name_string, port_idx)
    if ctype == "laser":
        return "right"
    if ctype == "directional_beamsplitter":
        # Differometor's directional BS has 4 ports too
        return map_beamsplitter_port(port_name_string, port_idx)
    return "left"
