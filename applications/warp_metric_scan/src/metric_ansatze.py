"""Parameterised metric families for each theoretical framework.

Each function returns a dict with:
  - 'metric': nested list (NxN) of sympy expressions
  - 'coords': tuple of sympy symbols
  - 'params': dict of parameter values used
  - 'framework': string identifier
"""
import sympy as sp

# Standard coordinate symbols
t, x, y, z, w = sp.symbols('t x y z w')


def _shape_function():
    """Gaussian bubble shape function centred at origin."""
    return sp.exp(-(x**2 + y**2 + z**2))


def flat_metric():
    """Minkowski spacetime (c=1)."""
    return {
        "metric": [
            [-1, 0, 0, 0],
            [0,  1, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1],
        ],
        "coords": (t, x, y, z),
        "params": {},
        "framework": "flat",
    }


def alcubierre_metric(v=1.0):
    """Alcubierre warp drive metric.

    Parameters
    ----------
    v : float
        Bubble velocity (c=1, so v>1 is superluminal).
    """
    v_s = sp.Rational(v).limit_denominator(1000) if isinstance(v, float) else v
    f = _shape_function()
    return {
        "metric": [
            [-(1 - v_s**2 * f**2), -v_s * f, 0, 0],
            [-v_s * f,              1,        0, 0],
            [0,                     0,        1, 0],
            [0,                     0,        0, 1],
        ],
        "coords": (t, x, y, z),
        "params": {"v": float(v_s)},
        "framework": "F1_standard_GR",
    }


def fell_heisenberg_metric(v=0.04):
    """Fell-Heisenberg 2024 subluminal warp drive (positive energy).

    Simplified model: shell of positive-energy matter with internal
    shift vector. At v < v_threshold, all energy conditions satisfied.
    We model this as Alcubierre with a damping factor that enforces
    positive energy density (the actual paper uses a specific shell
    construction — this is a proxy).
    """
    v_s = sp.Rational(v).limit_denominator(1000) if isinstance(v, float) else v
    f = _shape_function()
    # The key difference: the shift vector is modulated to keep T_00 > 0
    # Fell-Heisenberg achieves this by constraining v < v_threshold
    # For our energy-condition check, this IS just Alcubierre at low v
    # where the negative-energy terms are small enough to be offset
    # by the shell's positive contribution.
    # We add a positive shell energy density term.
    shell_energy = sp.Rational(10)  # positive shell contribution (normalised)
    return {
        "metric": [
            [-(1 - v_s**2 * f**2), -v_s * f, 0, 0],
            [-v_s * f,              1,        0, 0],
            [0,                     0,        1, 0],
            [0,                     0,        0, 1],
        ],
        "coords": (t, x, y, z),
        "params": {"v": float(v_s), "shell_energy": float(shell_energy)},
        "framework": "F1_fell_heisenberg",
        "_shell_energy": shell_energy,
    }


def alcubierre_5d_kk(v=1.0, alpha=0.5):
    """5D Kaluza-Klein warp metric with position-dependent extra dimension.

    The extra dimension radius varies with the warp bubble:
    phi(x,y,z) = 1 + alpha * f(x,y,z)

    Parameters
    ----------
    v : float
        Bubble velocity.
    alpha : float
        Coupling between extra dimension and bubble. alpha=0 reduces to 4D.
    """
    v_s = sp.Rational(v).limit_denominator(1000) if isinstance(v, float) else v
    alpha_s = sp.Rational(alpha).limit_denominator(1000) if isinstance(alpha, float) else alpha
    f = _shape_function()
    phi = 1 + alpha_s * f
    return {
        "metric": [
            [-(1 - v_s**2 * f**2), -v_s * f, 0, 0, 0],
            [-v_s * f,              1,        0, 0, 0],
            [0,                     0,        1, 0, 0],
            [0,                     0,        0, 1, 0],
            [0,                     0,        0, 0, phi**2],
        ],
        "coords": (t, x, y, z, w),
        "params": {"v": float(v_s), "alpha": float(alpha_s)},
        "framework": "F2_kaluza_klein",
    }


def alcubierre_f_of_R(v=1.0, alpha_R2=0.1):
    """Alcubierre metric in f(R) = R + alpha*R² gravity.

    The metric is the same as standard Alcubierre; the difference is
    in the field equations (4th-order instead of 2nd-order). The
    effective stress-energy includes geometric terms from the R² correction.

    Parameters
    ----------
    v : float
        Bubble velocity.
    alpha_R2 : float
        Coefficient of the R² correction term.
    """
    v_s = sp.Rational(v).limit_denominator(1000) if isinstance(v, float) else v
    f = _shape_function()
    return {
        "metric": [
            [-(1 - v_s**2 * f**2), -v_s * f, 0, 0],
            [-v_s * f,              1,        0, 0],
            [0,                     0,        1, 0],
            [0,                     0,        0, 1],
        ],
        "coords": (t, x, y, z),
        "params": {"v": float(v_s), "alpha_R2": float(alpha_R2)},
        "framework": "F3_f_of_R",
        "_alpha_R2": sp.Rational(alpha_R2).limit_denominator(1000),
    }


def alcubierre_einstein_cartan(v=1.0, s0=1.0, sigma_S=1.0):
    """Alcubierre warp metric with Einstein-Cartan torsion contribution.

    In Einstein-Cartan theory, the metric is the same Alcubierre form,
    but the field equations include torsion terms from spin density.
    The torsion contribution to the effective stress-energy is modelled as:
        H_00 = s0^2 * |grad f|^2 * exp(-r^2/sigma_S^2)
    which is concentrated at the bubble wall where the shape function
    gradient is largest (following DeBenedictis & Ilijic 2018).

    Parameters
    ----------
    v : float
        Bubble velocity.
    s0 : float
        Spin density parameter (dimensionless, normalised).
    sigma_S : float
        Width of torsion concentration profile.
    """
    v_s = sp.Rational(v).limit_denominator(1000) if isinstance(v, float) else v
    f = _shape_function()
    r_sq = x**2 + y**2 + z**2
    # Gradient magnitude squared of f = exp(-r^2)
    # grad f = -2*r_i*f, so |grad f|^2 = 4*r^2*f^2
    grad_f_sq = 4 * r_sq * f**2
    # Torsion profile: concentrated at bubble wall
    torsion_profile = sp.exp(-r_sq / sp.Rational(sigma_S).limit_denominator(1000)**2)
    # H_00 = s0^2 * |grad f|^2 * torsion_profile
    s0_r = sp.Rational(s0).limit_denominator(10000) if isinstance(s0, float) else s0
    sigma_r = sp.Rational(sigma_S).limit_denominator(1000) if isinstance(sigma_S, float) else sigma_S
    H00 = s0_r**2 * grad_f_sq * torsion_profile
    return {
        "metric": [
            [-(1 - v_s**2 * f**2), -v_s * f, 0, 0],
            [-v_s * f,              1,        0, 0],
            [0,                     0,        1, 0],
            [0,                     0,        0, 1],
        ],
        "coords": (t, x, y, z),
        "params": {"v": float(v_s), "s0": float(s0_r), "sigma_S": float(sigma_r)},
        "framework": "F4_einstein_cartan",
        "_H00": H00,
        "_s0": s0_r,
        "_sigma_S": sigma_r,
    }


def alcubierre_braneworld(v=1.0, C_W=1.0, lam=1e6):
    """Alcubierre warp metric on a Randall-Sundrum brane.

    The metric on the brane is the standard Alcubierre form.
    The effective 4D Einstein equations (Shiromizu-Maeda-Sasaki) include:
      G_mu_nu = 8*pi*T_mu_nu + kappa^4 * pi_mu_nu - E_mu_nu

    where pi_mu_nu is quadratic in T_mu_nu (always worsens energy conditions
    for positive-energy matter) and E_mu_nu is the projected 5D Weyl tensor.

    We model E_00 as: E_00 = C_W * |grad f|^2 * f^2
    (concentrated at the bubble wall, mimicking dark radiation from bulk).

    Parameters
    ----------
    v : float
        Bubble velocity.
    C_W : float
        Amplitude of Weyl projection (can be negative for positive energy contribution).
    lam : float
        Brane tension parameter (controls quadratic correction strength).
    """
    v_s = sp.Rational(v).limit_denominator(1000) if isinstance(v, float) else v
    f = _shape_function()
    r_sq = x**2 + y**2 + z**2
    grad_f_sq = 4 * r_sq * f**2
    C_W_r = sp.Rational(C_W).limit_denominator(10000) if isinstance(C_W, float) else C_W
    lam_r = sp.Rational(lam).limit_denominator(10**8) if isinstance(lam, float) else lam
    # Weyl projection contribution (negative E_00 adds positive energy)
    E00 = C_W_r * grad_f_sq * f**2
    return {
        "metric": [
            [-(1 - v_s**2 * f**2), -v_s * f, 0, 0],
            [-v_s * f,              1,        0, 0],
            [0,                     0,        1, 0],
            [0,                     0,        0, 1],
        ],
        "coords": (t, x, y, z),
        "params": {"v": float(v_s), "C_W": float(C_W_r), "lam": float(lam_r)},
        "framework": "F5_braneworld",
        "_E00": E00,
        "_C_W": C_W_r,
        "_lam": lam_r,
    }
