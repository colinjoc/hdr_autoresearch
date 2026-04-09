"""
test_kat_parser.py — TDD anchor for the kat parser.

The parser must read PyKat-format `.kat` config files from the
GWDetectorZoo and produce a structured representation
(`KatDocument`) that lists every parameter, every component, and
every space connection. The parser MUST NOT crash on any of the
50 Zoo solutions.

Tests are designed to be runnable BEFORE the parser is implemented:
all the asserts are against the canonical type8/sol00 numbers from
the Zoo README, plus a few hand-checked structural facts from the
.kat file itself.
"""
import os
from pathlib import Path

import pytest

from kat_parser import KatDocument, parse_kat


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ZOO_DIR = PROJECT_ROOT / "GWDetectorZoo"
SOL00_KAT = ZOO_DIR / "solutions/type8/sol00/CFGS_8_-85.46_120_1656378400_0_2318771219.txt"


@pytest.fixture(scope="module")
def sol00_doc() -> KatDocument:
    """Parsed type8/sol00 document, computed once per test session."""
    assert SOL00_KAT.exists(), f"Zoo file missing: {SOL00_KAT}"
    return parse_kat(SOL00_KAT.read_text())


# ---------------------------------------------------------------------------
# Parameter parsing
# ---------------------------------------------------------------------------

def test_parameter_count(sol00_doc: KatDocument):
    """The .kat file has exactly 108 `const param0XXX` declarations.

    The Zoo README claims 120 parameters. This is a discrepancy: only 108
    of the 134 possible IDs (0000–0133) are actually used in the file. The
    .kat file is the authoritative source for what gets simulated; the README
    appears to count something else (perhaps the original UIFO grid size
    before some parameters were pinned during optimisation).

    See knowledge_base.md §1.4 for the discrepancy note.
    """
    assert sol00_doc.n_parameters == 108, (
        f"Got {sol00_doc.n_parameters} parameters, .kat file has 108 "
        f"const param0XXX lines (Zoo README claims 120 but is at odds with the file)"
    )


def test_parameter_values_are_floats(sol00_doc: KatDocument):
    """Every parameter value must parse as a Python float."""
    for name, value in sol00_doc.parameters.items():
        assert isinstance(value, float), f"{name}={value!r} is not a float"


def test_parameter_known_value(sol00_doc: KatDocument):
    """Hand-checked: param0133 should equal 131.49889722959753 in the .kat file."""
    assert sol00_doc.parameters["param0133"] == pytest.approx(131.49889722959753)


# ---------------------------------------------------------------------------
# Component counts (canonical Zoo README numbers)
# ---------------------------------------------------------------------------

def test_mirror_count_matches_zoo_readme(sol00_doc: KatDocument):
    """Zoo README says 57 mirrors."""
    n_mirrors = sum(1 for c in sol00_doc.components if c.type == "mirror")
    assert n_mirrors == 57, f"Got {n_mirrors} mirrors, Zoo README says 57"


def test_beamsplitter_count_matches_zoo_readme(sol00_doc: KatDocument):
    """Zoo README says 13 beamsplitters (regular bs1, not directional dbs)."""
    n_bs = sum(1 for c in sol00_doc.components if c.type == "beamsplitter")
    assert n_bs == 13, f"Got {n_bs} beamsplitters, Zoo README says 13"


def test_laser_count_matches_zoo_readme(sol00_doc: KatDocument):
    """Zoo README says 3 lasers."""
    n_lasers = sum(1 for c in sol00_doc.components if c.type == "laser")
    assert n_lasers == 3, f"Got {n_lasers} lasers, Zoo README says 3"


def test_squeezer_count_matches_zoo_readme(sol00_doc: KatDocument):
    """Zoo README says ZERO squeezers (no `sq` statements in the .kat file)."""
    n_sq = sum(1 for c in sol00_doc.components if c.type == "squeezer")
    assert n_sq == 0, f"Got {n_sq} squeezers, Zoo README says 0"


def test_faraday_isolator_count_matches_zoo_readme(sol00_doc: KatDocument):
    """Zoo README says 1 Faraday isolator (encoded as a `dbs` directional beamsplitter)."""
    n_dbs = sum(1 for c in sol00_doc.components if c.type == "directional_beamsplitter")
    assert n_dbs == 1, f"Got {n_dbs} directional beamsplitters, Zoo README says 1"


# ---------------------------------------------------------------------------
# Reference resolution
# ---------------------------------------------------------------------------

def test_param_references_resolve(sol00_doc: KatDocument):
    """Every $paramXXXX reference inside any component must resolve to a defined parameter."""
    for c in sol00_doc.components:
        for prop_name, prop_value in c.properties.items():
            if isinstance(prop_value, str) and prop_value.startswith("$param"):
                ref_name = prop_value[1:]  # strip the $
                assert ref_name in sol00_doc.parameters, (
                    f"Component {c.name} property {prop_name} references "
                    f"undefined parameter {ref_name}"
                )


def test_resolve_returns_floats(sol00_doc: KatDocument):
    """KatDocument.resolve() must replace every $paramXXXX with the actual float value.

    Runtime variables like $fs (signal frequency) are passed through as strings.
    """
    for c in sol00_doc.components:
        resolved = sol00_doc.resolve(c.properties)
        for prop_name, prop_value in resolved.items():
            if isinstance(prop_value, str):
                assert not prop_value.startswith("$param"), (
                    f"After resolve, {c.name}.{prop_name}={prop_value!r} still has a $param reference"
                )


# ---------------------------------------------------------------------------
# Spaces (edges)
# ---------------------------------------------------------------------------

def test_some_spaces_present(sol00_doc: KatDocument):
    """sol00 has many `s` (space) statements connecting nodes — there must be at least 30."""
    assert len(sol00_doc.spaces) >= 30, f"Only {len(sol00_doc.spaces)} spaces parsed"


def test_arm_length_spaces_present(sol00_doc: KatDocument):
    """The 4 km arm cavities should appear as spaces with length ≈ 3670 m
    (the 'mUD_1_1' free space between mirror grid rows in sol00)."""
    long_spaces = [s for s in sol00_doc.spaces if s.length > 1000]
    assert len(long_spaces) > 0, "No long-arm spaces found"


# ---------------------------------------------------------------------------
# Detectors and signal injection
# ---------------------------------------------------------------------------

def test_balanced_homodyne_detector_present(sol00_doc: KatDocument):
    """sol00 uses balanced homodyne detection (a `qhd` line)."""
    n_qhd = sum(1 for c in sol00_doc.components if c.type == "homodyne_detector")
    assert n_qhd >= 1, "No qhd (balanced homodyne) detector found"


def test_signal_injections_present(sol00_doc: KatDocument):
    """sol00 has fsig signal injections on free spaces (representing strain perturbation)."""
    assert len(sol00_doc.signal_injections) >= 5, (
        f"Only {len(sol00_doc.signal_injections)} fsig injections parsed"
    )


# ---------------------------------------------------------------------------
# Robustness across the family
# ---------------------------------------------------------------------------

def test_parser_handles_all_25_type8_solutions():
    """The parser must not crash on any of the 25 type8 solutions in the Zoo."""
    type8_dir = ZOO_DIR / "solutions/type8"
    sol_dirs = sorted(d for d in type8_dir.iterdir() if d.is_dir() and d.name.startswith("sol"))
    assert len(sol_dirs) == 25, f"Expected 25 type8 solutions, found {len(sol_dirs)}"
    failures = []
    for d in sol_dirs:
        kat_files = list(d.glob("CFGS_8_*.txt"))
        if not kat_files:
            failures.append((d.name, "no .kat file"))
            continue
        try:
            doc = parse_kat(kat_files[0].read_text())
            assert doc.n_parameters > 0
        except Exception as e:
            failures.append((d.name, repr(e)))
    assert not failures, f"Parser failed on: {failures}"


# ---------------------------------------------------------------------------
# Cross-validation against PyKat (the canonical Finesse parser)
# ---------------------------------------------------------------------------

def _try_load_pykat():
    """Try to import pykat and create a kat parser. Return None if PyKat is unusable.

    PyKat is unmaintained and broken on Python ≥ 3.12 by default. The venv used
    by this project applies two small patches (imp → importlib, distutils.spawn
    → shutil.which, and tolerating MissingFinesse at init). If those patches
    are not in place, this test is skipped.
    """
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from pykat import finesse
        from pykat.components import mirror, beamSplitter, space, laser
        return finesse, (mirror, beamSplitter, space, laser)
    except Exception:
        return None


def _filter_kat_for_pykat(text: str) -> str:
    """Strip output/control directives that the canonical PyKat parser
    refuses to process. Components and parameters parse fine without them."""
    skip = ("xaxis", "noxaxis", "yaxis", "put", "set", "func", "lock",
            "noplot", "trace", "maxtem", "phase")
    out = []
    for line in text.splitlines():
        s = line.strip()
        if any(s.startswith(k + " ") or s == k for k in skip):
            continue
        out.append(line)
    return "\n".join(out)


def test_cross_validate_against_pykat(sol00_doc: KatDocument):
    """Both parsers must agree on the basic component counts in sol00.

    This is the strongest correctness test for our parser: agreement with
    the canonical PyKat library (the same library the GWDetectorZoo authors
    used to generate the .kat files).
    """
    py = _try_load_pykat()
    if py is None:
        pytest.skip("PyKat not available; this test requires the patched venv.")
    finesse, (mirror, beamSplitter, space, laser) = py

    text = SOL00_KAT.read_text()
    k = finesse.kat()
    k.parse(_filter_kat_for_pykat(text))

    pykat_mirrors = sum(1 for _, c in k.components.items() if isinstance(c, mirror))
    pykat_bs = sum(1 for _, c in k.components.items() if isinstance(c, beamSplitter))
    pykat_spaces = sum(1 for _, c in k.components.items() if isinstance(c, space))
    pykat_lasers = sum(1 for _, c in k.components.items() if isinstance(c, laser))

    my_mirrors = sum(1 for c in sol00_doc.components if c.type == "mirror")
    my_bs = sum(1 for c in sol00_doc.components if c.type == "beamsplitter")
    my_spaces = len(sol00_doc.spaces)
    my_lasers = sum(1 for c in sol00_doc.components if c.type == "laser")

    assert pykat_mirrors == my_mirrors == 57, (
        f"mirror disagreement: pykat={pykat_mirrors}, mine={my_mirrors}"
    )
    assert pykat_bs == my_bs == 13, (
        f"beamsplitter disagreement: pykat={pykat_bs}, mine={my_bs}"
    )
    assert pykat_spaces == my_spaces == 78, (
        f"space disagreement: pykat={pykat_spaces}, mine={my_spaces}"
    )
    assert pykat_lasers == my_lasers == 3, (
        f"laser disagreement: pykat={pykat_lasers}, mine={my_lasers}"
    )
