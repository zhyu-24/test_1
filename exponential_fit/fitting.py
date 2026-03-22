"""
Core fitting routines: R², Jacobian covariance, and the main fit function.
"""
import numpy as np
from scipy.optimize import curve_fit, minimize

from .model import double_exponential
from .constraints import validate_constraints


def compute_r_squared(y_true, y_pred):
    """
    Compute the coefficient of determination R².

    Parameters
    ----------
    y_true : array-like
    y_pred : array-like

    Returns
    -------
    float
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1.0 - ss_res / ss_tot


def _jacobian_covariance(x, y, popt):
    """
    Estimate the parameter covariance matrix from the finite-difference Jacobian.

    Uses the approximation: cov ≈ σ² · (Jᵀ J)⁻¹ where σ² is the residual
    variance and J is the Jacobian of the model with respect to the parameters.
    """
    n, p = len(y), len(popt)
    J = np.zeros((n, p))
    eps = np.sqrt(np.finfo(float).eps)

    for i in range(p):
        p_plus = popt.copy()
        p_plus[i] += eps
        p_minus = popt.copy()
        p_minus[i] -= eps
        J[:, i] = (
            double_exponential(x, *p_plus) - double_exponential(x, *p_minus)
        ) / (2 * eps)

    residuals = y - double_exponential(x, *popt)
    dof = max(n - p, 1)
    residual_variance = np.sum(residuals ** 2) / dof

    try:
        pcov = residual_variance * np.linalg.pinv(J.T @ J)
    except np.linalg.LinAlgError:
        pcov = np.full((p, p), np.inf)

    return pcov


def fit_double_exponential(x, y, p0=None, bounds=(-np.inf, np.inf),
                           constraint_exprs=None):
    """
    Fit f(x) = a·exp(b·x) + c·exp(d·x) to data.

    When ``constraint_exprs`` is provided, the fit is performed using
    ``scipy.optimize.minimize`` (SLSQP method) with the given equality
    constraints.  Without constraints, ``scipy.optimize.curve_fit`` is used
    (gives better covariance estimates).

    Parameters
    ----------
    x : array-like
        Independent variable data.
    y : array-like
        Dependent variable data.
    p0 : array-like, optional
        Initial parameter guesses ``[a, b, c, d]``.
        Defaults to ``[1.0, -1.0, 1.0, -0.1]``.
    bounds : 2-tuple, optional
        ``(lower, upper)`` bounds for ``[a, b, c, d]``.
        Each bound can be a scalar (applied to all parameters) or a
        length-4 sequence.  Use ``±np.inf`` for no bound.
    constraint_exprs : list of str, optional
        Mathematical equality constraints, e.g.::

            ["a + c = 1", "b = -2 * d"]

        Allowed names: a, b, c, d, exp, log, sqrt, abs, sin, cos, tan, pi, e.

    Returns
    -------
    popt : numpy.ndarray, shape (4,)
        Optimal parameters ``[a, b, c, d]``.
    pcov : numpy.ndarray, shape (4, 4)
        Estimated parameter covariance matrix.
    r_squared : float
        Coefficient of determination R².
    """
    if p0 is None:
        p0 = [1.0, -1.0, 1.0, -0.1]

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    p0 = np.asarray(p0, dtype=float)

    if constraint_exprs:
        scipy_constraints = validate_constraints(constraint_exprs, p0)

        def residuals_ss(params):
            return np.sum((y - double_exponential(x, *params)) ** 2)

        # Normalise bounds to per-parameter (lo, hi) pairs
        lo, hi = bounds
        lo_arr = [lo] * 4 if np.isscalar(lo) else list(lo)
        hi_arr = [hi] * 4 if np.isscalar(hi) else list(hi)
        scipy_bounds = list(zip(lo_arr, hi_arr))

        result = minimize(
            residuals_ss,
            p0,
            method="SLSQP",
            bounds=scipy_bounds,
            constraints=scipy_constraints,
            options={"ftol": 1e-12, "maxiter": 10000},
        )

        if not result.success:
            raise RuntimeError(
                f"Constrained optimization did not converge: {result.message}\n"
                "Try different initial parameter guesses (p0)."
            )

        popt = result.x
        pcov = _jacobian_covariance(x, y, popt)

    else:
        popt, pcov = curve_fit(
            double_exponential, x, y, p0=p0, bounds=bounds, maxfev=10000
        )

    r_squared = compute_r_squared(y, double_exponential(x, *popt))
    return popt, pcov, r_squared
