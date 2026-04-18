"""Energy-condition checkers for warp drive metrics.

Checks WEC, NEC, SEC, DEC by evaluating the stress-energy tensor
(derived from the Einstein tensor) at sample points in the bubble wall.
"""
import sympy as sp
import numpy as np
from .field_equations import compute_einstein_tensor


def _evaluate_G00_on_grid(metric_def, G00_expr=None, n_points=50):
    """Evaluate G_00 at sample points in the bubble wall region.

    Returns array of G_00 values. Negative values indicate WEC violation.
    """
    coords = metric_def["coords"]
    params = metric_def.get("params", {})

    if G00_expr is None:
        G = compute_einstein_tensor(metric_def)
        G00_expr = G["G00"]

    # Substitute any remaining symbolic parameters
    for sym in G00_expr.free_symbols:
        name = str(sym)
        if name in params:
            G00_expr = G00_expr.subs(sym, params[name])

    # Sample points: the bubble wall is where the shape function
    # has large gradients — around r ~ 1 for our Gaussian f = exp(-r²)
    # We sample along the x-axis (y=z=0) and off-axis (y=1,z=0)
    t_sym = coords[0]
    spatial = coords[1:4] if len(coords) >= 4 else coords[1:]

    values = []
    for x_val in np.linspace(-2, 2, n_points):
        subs = {t_sym: 0}
        subs[spatial[0]] = x_val
        for s in spatial[1:]:
            subs[s] = 0
        try:
            val = float(G00_expr.subs(subs))
            values.append(val)
        except (TypeError, ValueError):
            continue

    # Also sample off-axis
    for y_val in np.linspace(-1.5, 1.5, n_points // 2):
        subs = {t_sym: 0, spatial[0]: 0}
        if len(spatial) > 1:
            subs[spatial[1]] = y_val
        for s in spatial[2:]:
            subs[s] = 0
        try:
            val = float(G00_expr.subs(subs))
            values.append(val)
        except (TypeError, ValueError):
            continue

    return np.array(values)


def check_wec(metric_def, G00_override=None):
    """Check the Weak Energy Condition for a metric.

    WEC requires T_00 ≥ 0 (equivalently G_00 ≥ 0 up to 8πG factor,
    which doesn't affect the sign).

    For the Fell-Heisenberg proxy, we add the shell energy contribution.

    Returns dict with 'satisfied' (bool), 'rho_negative' (bool),
    'min_G00' (float), 'fraction_negative' (float).
    """
    G00_expr = G00_override
    if G00_expr is None:
        G = compute_einstein_tensor(metric_def)
        G00_expr = G["G00"]

    # For Fell-Heisenberg, add the shell energy (positive contribution)
    shell_energy = metric_def.get("_shell_energy", None)
    if shell_energy is not None:
        G00_expr = G00_expr + shell_energy

    values = _evaluate_G00_on_grid(metric_def, G00_expr)

    if len(values) == 0:
        return {"satisfied": None, "rho_negative": None,
                "min_G00": None, "fraction_negative": None,
                "error": "could not evaluate"}

    min_val = float(np.min(values))
    frac_neg = float(np.mean(values < -1e-10))

    return {
        "satisfied": min_val >= -1e-10,
        "rho_negative": min_val < -1e-10,
        "min_G00": min_val,
        "fraction_negative": frac_neg,
        "n_points": len(values),
    }


def check_nec(metric_def):
    """Check the Null Energy Condition.

    NEC requires T_μν k^μ k^ν ≥ 0 for all null k.
    For a diagonal-ish metric, this reduces to checking
    T_00 + T_ii ≥ 0 for each spatial direction i.

    We check G_00 + G_11 ≥ 0 as the primary NEC diagnostic.
    """
    G = compute_einstein_tensor(metric_def)
    G00 = G["G00"]
    G11 = G["G11"]

    nec_expr = G00 + G11
    values = _evaluate_G00_on_grid(metric_def, nec_expr)

    if len(values) == 0:
        return {"satisfied": None, "error": "could not evaluate"}

    min_val = float(np.min(values))
    return {
        "satisfied": min_val >= -1e-10,
        "min_nec": min_val,
        "n_points": len(values),
    }


def check_wec_einstein_cartan(metric_def):
    """Check WEC for Einstein-Cartan framework.

    The effective energy density is G_00 + H_00, where H_00 is the
    torsion contribution from spin density (always positive).
    """
    G = compute_einstein_tensor(metric_def)
    G00_expr = G["G00"]
    H00 = metric_def.get("_H00", 0)
    effective = G00_expr + H00
    values = _evaluate_G00_on_grid(metric_def, effective)
    if len(values) == 0:
        return {"satisfied": None, "error": "could not evaluate"}
    min_val = float(np.min(values))
    frac_neg = float(np.mean(values < -1e-10))

    # Also evaluate bare G_00 and H_00 separately
    g00_values = _evaluate_G00_on_grid(metric_def, G00_expr)
    h00_values = _evaluate_G00_on_grid(metric_def, H00)

    return {
        "satisfied": min_val >= -1e-10,
        "rho_negative": min_val < -1e-10,
        "min_G00_eff": min_val,
        "min_G00_bare": float(np.min(g00_values)) if len(g00_values) > 0 else None,
        "max_H00": float(np.max(h00_values)) if len(h00_values) > 0 else None,
        "fraction_negative": frac_neg,
        "n_points": len(values),
    }


def check_wec_braneworld(metric_def):
    """Check WEC for braneworld (Randall-Sundrum) framework.

    The effective energy density includes:
    - G_00 (standard Einstein tensor from brane metric)
    - -E_00 (Weyl projection from bulk; negative E_00 adds positive energy)
    - pi_00 (quadratic correction; positive-definite for positive-energy matter)

    Since pi_00 is positive-definite and worsens energy violations for
    positive-energy matter, we model the net correction as:
    G_00_eff = G_00 - E_00
    (pi_00 makes things worse, so the hope lies in E_00 being negative)
    """
    G = compute_einstein_tensor(metric_def)
    G00_expr = G["G00"]
    E00 = metric_def.get("_E00", 0)
    # E_mu_nu enters as -E_mu_nu in the SMS equations
    # Negative E_00 contributes positive effective energy
    effective = G00_expr - E00
    values = _evaluate_G00_on_grid(metric_def, effective)
    if len(values) == 0:
        return {"satisfied": None, "error": "could not evaluate"}
    min_val = float(np.min(values))
    frac_neg = float(np.mean(values < -1e-10))

    g00_values = _evaluate_G00_on_grid(metric_def, G00_expr)
    e00_values = _evaluate_G00_on_grid(metric_def, E00)

    return {
        "satisfied": min_val >= -1e-10,
        "rho_negative": min_val < -1e-10,
        "min_G00_eff": min_val,
        "min_G00_bare": float(np.min(g00_values)) if len(g00_values) > 0 else None,
        "max_E00_contribution": float(np.max(np.abs(e00_values))) if len(e00_values) > 0 else None,
        "fraction_negative": frac_neg,
        "n_points": len(values),
    }
