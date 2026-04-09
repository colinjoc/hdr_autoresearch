"""
diagnose_converter.py — build a simple 2-mirror arm cavity by hand in Differometor,
then in kat, then convert. Compare.
"""
from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import jax.numpy as jnp
import differometor as df
from differometor.setups import Setup

from kat_parser import parse_kat
from kat_to_differometor import kat_to_differometor


# ----- 1. Hand-built Differometor cavity -----
print("=" * 60)
print("Hand-built MICHELSON with balanced readout in Differometor")
print("=" * 60)
S1 = Setup()
S1.add("laser", "l0", power=125.0)
S1.add("beamsplitter", "bs", reflectivity=0.5, loss=5e-6, alpha=45, tuning=0)
S1.add("mirror", "itmx", transmissivity=0.014, loss=5e-6, tuning=90)
S1.add("mirror", "etmx", transmissivity=5e-6, loss=5e-6, tuning=89.999875)
S1.add("mirror", "itmy", transmissivity=0.014, loss=5e-6, tuning=0)
S1.add("mirror", "etmy", transmissivity=5e-6, loss=5e-6, tuning=0.000125)
S1.space("l0", "bs", length=1)
S1.space("bs", "itmx", length=4.5)
S1.space("itmx", "etmx", length=4000)
S1.space("bs", "itmy", length=4.5, source_port="top")
S1.space("itmy", "etmy", length=4000)
S1.add("free_mass", "itmxsus", mass=40, target="itmx")
S1.add("free_mass", "etmxsus", mass=40, target="etmx")
S1.add("free_mass", "itmysus", mass=40, target="itmy")
S1.add("free_mass", "etmysus", mass=40, target="etmy")
S1.add("frequency", "f", frequency=1)
S1.add("signal", "sigx", target="itmx_etmx")
S1.add("signal", "sigy", target="itmy_etmy", phase=180)
S1.add("qnoised", "ns", target="bs", port="bottom", direction="out", auxiliary=True)
S1.add("detector", "det", target="bs", port="bottom", direction="out")

freqs = jnp.logspace(jnp.log10(800), jnp.log10(3000), 20)
carrier, signal, noise, dp, *_ = df.run(S1, [("f", "frequency")], freqs)
powers = df.power_detector(carrier)
print(f"  max carrier power: {float(powers.max()):.3e} W  (expect arm buildup)")
print(f"  detector_ports: {dp}")
sig_d = df.signal_detector(carrier, signal)[dp].squeeze()
sens1 = noise / jnp.abs(sig_d)
print(f"  sensitivity median: {float(jnp.exp(jnp.mean(jnp.log(sens1)))):.3e} /√Hz")


# ----- 2. Equivalent kat file (written as a string), parsed, converted -----
print()
print("=" * 60)
print("Kat string -> parser -> kat_to_differometor")
print("=" * 60)

KAT_TEXT = """
const param0000 0.99
const param0001 0.99
const param0002 40.0
const param0003 40.0
l l0 1.0 0.0 0.0 nl0
m1 m0 $param0000 5e-06 0.0 nl0 nm0_arm
attr m0 mass $param0002
m1 m1 $param0001 5e-06 0.0 nm0_arm nm1_out
attr m1 mass $param0003
s sl0 1.0 nl0 nl0
s sarm 4000.0 nm0_arm nm0_arm
fsig sig sarm phase 1.0 180.0 1.0
qhd detqhd 180.0 nm1_out nm1_out
"""
# Actually kat files need spaces to link DIFFERENT node names, and the
# parser expects specific formats. Let me write this differently.

# Build a valid minimal kat:
KAT_TEXT = """
% Simple cavity kat
const param0000 0.99
const param0001 0.99
l l0 1.0 0.0 0.0 nl0
m1 m0 $param0000 5e-06 0.0 nm0front nm0back
attr m0 mass 40.0
s sl0 1.0 nl0 nm0front
m1 m1 $param0001 5e-06 0.0 nm1front nm1back
attr m1 mass 40.0
s sarm 4000.0 nm0back nm1front
fsig sig sarm phase 1.0 180.0 1.0
qhd qdet 180.0 nm1back nm1back
"""

doc = parse_kat(KAT_TEXT)
print(f"parsed {len(doc.components)} components, {len(doc.spaces)} spaces, {len(doc.signal_injections)} fsigs")
for c in doc.components:
    print(f"  {c.name}: type={c.type} ports={c.ports}")
for s in doc.spaces:
    print(f"  space {s.name}: {s.length}m  {s.node_a} <-> {s.node_b}")

S2, meta = kat_to_differometor(doc)
print(f"Converter placed {meta['n_space_edges_placed']} edges, {meta['n_signal_nodes']} signals, {meta['n_detectors_attached']} detectors")

try:
    carrier2, signal2, noise2, dp2, *_ = df.run(S2, [("f", "frequency")], freqs)
    powers2 = df.power_detector(carrier2)
    print(f"  max carrier power: {float(powers2.max()):.3e} W  (should match Differometor run above)")
    print(f"  detector_ports: {dp2}")
    sig_d2 = df.signal_detector(carrier2, signal2)[dp2]
    if len(dp2) >= 2:
        bal2 = sig_d2[0] - sig_d2[1]
    else:
        bal2 = sig_d2.squeeze()
    sens2 = noise2 / jnp.abs(bal2)
    print(f"  sensitivity median: {float(jnp.exp(jnp.mean(jnp.log(sens2)))):.3e} /√Hz")
except Exception as e:
    print(f"  df.run() FAILED: {e}")
    import traceback; traceback.print_exc()
