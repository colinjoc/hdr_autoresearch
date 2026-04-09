"""
kat_parser.py — minimal PyKat .kat parser for the GWDetectorZoo.

Parses the small subset of the kat (Finesse) language used by the
GWDetectorZoo solutions. The parser is not a full Finesse implementation
— it understands only the statements present in the Zoo `.kat` files,
and rejects nothing it does not recognise (unknown lines are stored as
raw `Unknown` components rather than dropped, so we can audit them).

The output is a `KatDocument` that exposes:
  - `parameters`: dict {param_name: float}
  - `components`: list of `Component(type, name, properties, ports)`
  - `spaces`:     list of `Space(name, length, node_a, node_b)`
  - `signal_injections`: list of `SignalInjection`
  - `resolve(props)`: substitute every "$paramXXXX" reference with the float

Parsing is done by recognising the leading keyword on each line. The
shape of the rest of the line (positional args + node names) follows
PyKat conventions described in `design_variables.md`.

This file is the Phase 0.5 baseline-audit deliverable. The TDD test
suite is at `tests/test_kat_parser.py` — run with `pytest tests/`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

# A property value is either a float (literal) or a string of the form
# "$paramXXXX" (a parameter reference to be resolved later).
PropValue = Union[float, str]


@dataclass
class Component:
    type: str                          # "mirror" / "beamsplitter" / "laser" / ...
    name: str                          # the component name from the kat file
    properties: Dict[str, PropValue] = field(default_factory=dict)
    ports: List[str] = field(default_factory=list)


@dataclass
class Space:
    name: str
    length: float
    node_a: str
    node_b: str


@dataclass
class SignalInjection:
    name: str
    target: str        # the component being perturbed (typically a free-space name)
    perturbation_type: str   # "phase", "amplitude", etc.
    amplitude: float
    phase_deg: float
    frequency: float


@dataclass
class KatDocument:
    parameters: Dict[str, float] = field(default_factory=dict)
    components: List[Component] = field(default_factory=list)
    spaces: List[Space] = field(default_factory=list)
    signal_injections: List[SignalInjection] = field(default_factory=list)
    raw_unknown_lines: List[str] = field(default_factory=list)

    @property
    def n_parameters(self) -> int:
        return len(self.parameters)

    def resolve(self, props: Dict[str, PropValue]) -> Dict[str, Any]:
        """Substitute every $paramXXXX reference with its float value.

        Only `$paramXXXX` references are resolved. Other `$xxx` runtime
        variables (e.g. `$fs` for the signal frequency) are passed through
        unchanged.
        """
        resolved: Dict[str, Any] = {}
        for k, v in props.items():
            if isinstance(v, str) and v.startswith("$param"):
                ref = v[1:]
                if ref not in self.parameters:
                    raise KeyError(f"Unresolved parameter reference: {v}")
                resolved[k] = self.parameters[ref]
            elif isinstance(v, str):
                # runtime variable like $fs — leave alone
                resolved[k] = v
            else:
                resolved[k] = float(v)
        return resolved


def _parse_value(token: str) -> PropValue:
    """Parse a single token: either a $paramXXXX reference or a float literal."""
    if token.startswith("$"):
        return token  # keep as a reference, resolved later
    return float(token)


def parse_kat(text: str) -> KatDocument:
    """Parse a PyKat .kat file (as a string) into a KatDocument."""
    doc = KatDocument()

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%") or line.startswith("#"):
            continue
        tokens = line.split()
        if not tokens:
            continue
        kw = tokens[0]

        # ----- parameter declarations -----
        if kw == "const" and len(tokens) >= 3:
            name = tokens[1]
            try:
                value = float(tokens[2])
            except ValueError:
                doc.raw_unknown_lines.append(line)
                continue
            doc.parameters[name] = value
            continue

        # ----- mirror -----
        # Format: m1 <name> <R> <loss> <tuning> <node1> <node2>
        if kw == "m1" and len(tokens) >= 7:
            comp = Component(
                type="mirror",
                name=tokens[1],
                properties={
                    "reflectivity": _parse_value(tokens[2]),
                    "loss": _parse_value(tokens[3]),
                    "tuning": _parse_value(tokens[4]),
                },
                ports=[tokens[5], tokens[6]],
            )
            doc.components.append(comp)
            continue

        # Some Zoo files use plain `m` instead of `m1`
        if kw == "m" and len(tokens) >= 7:
            comp = Component(
                type="mirror",
                name=tokens[1],
                properties={
                    "reflectivity": _parse_value(tokens[2]),
                    "transmission": _parse_value(tokens[3]),
                    "tuning": _parse_value(tokens[4]),
                },
                ports=[tokens[5], tokens[6]],
            )
            doc.components.append(comp)
            continue

        # ----- beamsplitter -----
        # Format: bs1 <name> <R> <loss> <tuning> <angle> <n1> <n2> <n3> <n4>
        if kw == "bs1" and len(tokens) >= 10:
            comp = Component(
                type="beamsplitter",
                name=tokens[1],
                properties={
                    "reflectivity": _parse_value(tokens[2]),
                    "loss": _parse_value(tokens[3]),
                    "tuning": _parse_value(tokens[4]),
                    "angle": _parse_value(tokens[5]),
                },
                ports=tokens[6:10],
            )
            doc.components.append(comp)
            continue

        if kw == "bs" and len(tokens) >= 10:
            # Equivalent to bs1 in this format
            comp = Component(
                type="beamsplitter",
                name=tokens[1],
                properties={
                    "reflectivity": _parse_value(tokens[2]),
                    "transmission": _parse_value(tokens[3]),
                    "tuning": _parse_value(tokens[4]),
                    "angle": _parse_value(tokens[5]),
                },
                ports=tokens[6:10],
            )
            doc.components.append(comp)
            continue

        # ----- directional beamsplitter (Faraday-isolator-like) -----
        # Format: dbs <name> <n1> <n2> <n3> <n4>
        if kw == "dbs" and len(tokens) >= 6:
            comp = Component(
                type="directional_beamsplitter",
                name=tokens[1],
                properties={},
                ports=tokens[2:6],
            )
            doc.components.append(comp)
            continue

        # ----- laser -----
        # Format: l <name> <power> <frequency> <phase> <node>
        if kw == "l" and len(tokens) >= 6:
            comp = Component(
                type="laser",
                name=tokens[1],
                properties={
                    "power": _parse_value(tokens[2]),
                    "frequency": _parse_value(tokens[3]),
                    "phase": _parse_value(tokens[4]),
                },
                ports=[tokens[5]],
            )
            doc.components.append(comp)
            continue

        # ----- squeezer (rare in type8/sol00 but supported for other Zoo families) -----
        # Format: sq <name> <freq> <db> <phase> <node>
        if kw == "sq" and len(tokens) >= 6:
            comp = Component(
                type="squeezer",
                name=tokens[1],
                properties={
                    "frequency": _parse_value(tokens[2]),
                    "db": _parse_value(tokens[3]),
                    "phase": _parse_value(tokens[4]),
                },
                ports=[tokens[5]],
            )
            doc.components.append(comp)
            continue

        # ----- free space (edge) -----
        # Format: s <name> <length> <node1> <node2>
        if kw == "s" and len(tokens) >= 5:
            try:
                length = float(tokens[2])
            except ValueError:
                # length might be a $param ref
                length_val = _parse_value(tokens[2])
                # We can't resolve here without the full parameter table; defer.
                # Store as 0.0 with the ref retained in raw_unknown_lines.
                doc.raw_unknown_lines.append(line)
                continue
            doc.spaces.append(Space(
                name=tokens[1],
                length=length,
                node_a=tokens[3],
                node_b=tokens[4],
            ))
            continue

        # ----- attribute (typically `attr <name> mass <value>`) -----
        if kw == "attr" and len(tokens) >= 4:
            target_name = tokens[1]
            attr_name = tokens[2]
            attr_value = _parse_value(tokens[3])
            # find the most recently defined component with this name and attach
            for comp in reversed(doc.components):
                if comp.name == target_name:
                    comp.properties[attr_name] = attr_value
                    break
            continue

        # ----- DC photodetector -----
        # Format: pd0 <name> <node>
        if kw == "pd0" and len(tokens) >= 3:
            comp = Component(
                type="dc_photodetector",
                name=tokens[1],
                properties={},
                ports=[tokens[2]],
            )
            doc.components.append(comp)
            continue

        # ----- AC photodetector -----
        # Format: pd1 <name> <freq> <node>
        if kw == "pd1" and len(tokens) >= 4:
            comp = Component(
                type="ac_photodetector",
                name=tokens[1],
                properties={"frequency_ref": tokens[2]},
                ports=[tokens[3]],
            )
            doc.components.append(comp)
            continue

        # ----- quantum noise detector -----
        # Format: qnoised <name> <order> <freq> <node>
        if kw == "qnoised" and len(tokens) >= 5:
            comp = Component(
                type="quantum_noise_detector",
                name=tokens[1],
                properties={
                    "order": _parse_value(tokens[2]),
                    "frequency_ref": tokens[3],
                },
                ports=[tokens[4]],
            )
            doc.components.append(comp)
            continue

        # ----- quantum balanced-homodyne detector -----
        # Format: qhd <name> <homodyne_angle> <node1> <node2>
        if kw == "qhd" and len(tokens) >= 5:
            comp = Component(
                type="homodyne_detector",
                name=tokens[1],
                properties={"homodyne_angle": _parse_value(tokens[2])},
                ports=[tokens[3], tokens[4]],
            )
            doc.components.append(comp)
            continue

        # ----- signal injection -----
        # Format: fsig <name> <target> <type> <amp> <phase> <freq>
        if kw == "fsig" and len(tokens) >= 7:
            doc.signal_injections.append(SignalInjection(
                name=tokens[1],
                target=tokens[2],
                perturbation_type=tokens[3],
                amplitude=float(tokens[4]),
                phase_deg=float(tokens[5]),
                frequency=float(tokens[6]),
            ))
            continue

        # ----- output / formatting / control statements (recognised but not stored) -----
        if kw in ("phase", "maxtem", "yaxis", "xaxis", "noxaxis", "trace", "lambda",
                  "scale", "func", "set", "lock", "diff", "deriv_h", "put", "noplot"):
            # These are simulation-control directives, not setup components.
            continue

        doc.raw_unknown_lines.append(line)

    return doc
