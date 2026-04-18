"""Compute field equations (Einstein tensor, effective stress-energy) for each framework."""
import sympy as sp
from einsteinpy.symbolic import MetricTensor, EinsteinTensor, RicciTensor, RicciScalar
from functools import lru_cache
import hashlib
import json


def _metric_key(metric_def):
    """Hashable key for caching."""
    return str(metric_def["metric"]) + str(metric_def["coords"])


_cache = {}


def compute_einstein_tensor(metric_def):
    """Compute the Einstein tensor G_μν for a given metric definition.

    Returns a dict with G_μν components accessible as G['G00'], G['G01'], etc.
    """
    key = _metric_key(metric_def)
    if key in _cache:
        return _cache[key]

    mt = MetricTensor(metric_def["metric"], metric_def["coords"])
    et = EinsteinTensor.from_metric(mt)
    tensor = et.tensor()

    n = len(metric_def["coords"])
    result = {}
    for i in range(n):
        for j in range(n):
            result[f"G{i}{j}"] = tensor[i, j]

    result["_metric_tensor"] = mt
    result["_einstein_tensor"] = et
    result["_dims"] = n
    _cache[key] = result
    return result


def compute_ricci_scalar(metric_def):
    """Compute the Ricci scalar R for a metric."""
    mt = MetricTensor(metric_def["metric"], metric_def["coords"])
    rs = RicciScalar.from_metric(mt)
    return rs.expr


def compute_effective_stress_energy_fR(metric_def):
    """Compute effective stress-energy for f(R) = R + alpha*R² gravity.

    In f(R) gravity, the field equations are:
    f'(R) R_μν - ½ f(R) g_μν + (g_μν □ - ∇_μ∇_ν) f'(R) = 8π T_μν

    The effective stress-energy T_eff_μν includes geometric terms:
    T_eff_μν = T_matter_μν + T_geometric_μν

    where T_geometric comes from the extra f(R) terms and can be
    negative even when T_matter is positive.
    """
    alpha_R2 = metric_def.get("_alpha_R2", sp.Rational(1, 10))

    # Compute standard Einstein tensor (= 8π T_matter for standard GR)
    G = compute_einstein_tensor(metric_def)

    # Compute Ricci scalar
    R = compute_ricci_scalar(metric_def)

    # f(R) = R + alpha * R²
    # f'(R) = 1 + 2*alpha*R
    # The geometric correction to G_00 is approximately:
    # ΔG_00 ≈ 2*alpha * (R * R_00 - ¼ R² g_00 + ∇²R terms)
    # For a first-order estimate, we compute the R² contribution
    mt = G["_metric_tensor"]
    rt = RicciTensor.from_metric(mt)
    R00 = rt.tensor()[0, 0]
    g00 = metric_def["metric"][0][0]

    # Leading-order f(R) correction to the effective energy density
    delta_G00 = 2 * alpha_R2 * (R * R00 - sp.Rational(1, 4) * R**2 * g00)

    return {
        "G00_standard": G["G00"],
        "G00_fR_correction": delta_G00,
        "G00_effective": G["G00"] + delta_G00,
        "R": R,
        "alpha_R2": alpha_R2,
    }
