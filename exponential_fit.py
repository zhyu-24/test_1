"""
双指数函数线性组合数据拟合 (增强版)
Data fitting using a linear combination of two exponential functions,
with support for:
  • loading data from an Excel Online / Google Sheets / direct file URL
  • user-defined mathematical constraints between the four parameters

Model: f(x) = a * exp(b * x) + c * exp(d * x)
"""

import ast
import io
import operator
import re
import numpy as np
import matplotlib.pyplot as plt
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
from scipy.optimize import curve_fit, minimize


# ── SAFE EXPRESSION EVALUATOR ─────────────────────────────────────────────────
# Parses mathematical expressions via the Python AST and evaluates only a
# tightly controlled subset of nodes: arithmetic operators, the four
# parameters (a, b, c, d), numeric constants, and a fixed whitelist of
# mathematical functions.  No Python built-ins are accessible.

_ALLOWED_FUNCS: dict = {
    "exp": np.exp,
    "log": np.log,
    "log2": np.log2,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": abs,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
}
_ALLOWED_NAMES: dict = {
    "pi": np.pi,
    "e": np.e,
}
_BINOPS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARYOPS: dict = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class _SafeEvaluator(ast.NodeVisitor):
    """Walk a parsed AST and evaluate only safe mathematical nodes."""

    def __init__(self, param_values: dict):
        self._env = {**_ALLOWED_NAMES, **param_values}

    def evaluate(self, expr: str) -> float:
        tree = ast.parse(expr, mode="eval")
        return self.visit(tree.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant: {node.value!r}")

    # Python < 3.8 compatibility
    def visit_Num(self, node):
        return float(node.n)

    def visit_Name(self, node):
        if node.id in self._env:
            return self._env[node.id]
        allowed = sorted(
            list(_ALLOWED_FUNCS) + list(_ALLOWED_NAMES) + ["a", "b", "c", "d"]
        )
        raise ValueError(
            f"Unknown name '{node.id}'. Allowed names: {', '.join(allowed)}"
        )

    def visit_BinOp(self, node):
        op_type = type(node.op)
        if op_type not in _BINOPS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return _BINOPS[op_type](self.visit(node.left), self.visit(node.right))

    def visit_UnaryOp(self, node):
        op_type = type(node.op)
        if op_type not in _UNARYOPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return _UNARYOPS[op_type](self.visit(node.operand))

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are allowed in constraints.")
        func_name = node.func.id
        if func_name not in _ALLOWED_FUNCS:
            raise ValueError(
                f"Unknown function '{func_name}'. "
                f"Allowed: {', '.join(sorted(_ALLOWED_FUNCS))}"
            )
        if node.keywords:
            raise ValueError("Keyword arguments are not allowed in constraint expressions.")
        args = [self.visit(arg) for arg in node.args]
        return _ALLOWED_FUNCS[func_name](*args)

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def _eval_constraint_expr(expr: str, a: float, b: float, c: float, d: float) -> float:
    """Safely evaluate a constraint expression string for given parameter values."""
    evaluator = _SafeEvaluator({"a": a, "b": b, "c": c, "d": d})
    return evaluator.evaluate(expr)



# ── MODEL ──────────────────────────────────────────────────────────────────────

def double_exponential(x, a, b, c, d):
    """
    Linear combination of two exponential functions.

    f(x) = a * exp(b * x) + c * exp(d * x)

    Parameters
    ----------
    x : array-like
        Independent variable.
    a : float
        Amplitude of the first exponential term.
    b : float
        Rate of the first exponential term.
    c : float
        Amplitude of the second exponential term.
    d : float
        Rate of the second exponential term.

    Returns
    -------
    numpy.ndarray
    """
    return a * np.exp(b * x) + c * np.exp(d * x)


# ── DATA LOADING ───────────────────────────────────────────────────────────────

def _make_download_url(url):
    """
    Convert an Excel Online / Google Sheets sharing URL to a direct download URL.

    Handles:
      - Google Sheets  → CSV export endpoint
      - OneDrive personal / SharePoint / 1drv.ms  → adds ``download=1``
      - Direct file URLs (.xlsx, .csv, …)  → returned unchanged
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    # Google Sheets: extract sheet ID and convert to CSV export link
    # Match exact domain or www subdomain only
    if netloc in ("docs.google.com", "www.docs.google.com"):
        m = re.search(r"/spreadsheets/d/([^/]+)", parsed.path)
        if m:
            sheet_id = m.group(1)
            gid_m = re.search(r"gid=(\d+)", url)
            gid_part = f"&gid={gid_m.group(1)}" if gid_m else ""
            return (
                f"https://docs.google.com/spreadsheets/d/{sheet_id}"
                f"/export?format=csv{gid_part}"
            )

    # OneDrive (consumer) / SharePoint (business) / short 1drv.ms links
    # Use exact match or proper suffix check to avoid substring spoofing
    _onedrive_hosts = {"onedrive.live.com", "1drv.ms"}
    is_onedrive = netloc in _onedrive_hosts
    is_sharepoint = netloc == "sharepoint.com" or netloc.endswith(".sharepoint.com")
    if is_onedrive or is_sharepoint:
        qs = parse_qs(parsed.query, keep_blank_values=True)
        qs["download"] = ["1"]
        return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))

    return url


def load_data_from_url(url, x_col=0, y_col=1, sheet_name=0):
    """
    Download x/y data from a URL.

    Supported sources
    -----------------
    • Excel Online (OneDrive / SharePoint) share link — publicly shared files
    • Google Sheets share link — must be shared as "Anyone with link can view"
    • Any direct URL ending in .xlsx, .xls, or .csv

    The first column (``x_col=0``) is used as x-axis data and the second
    column (``y_col=1``) is used as y-axis data.

    Parameters
    ----------
    url : str
        URL to the data source.
    x_col : int
        Zero-based column index for x data (default: 0).
    y_col : int
        Zero-based column index for y data (default: 1).
    sheet_name : int or str
        Sheet to read for Excel files (default: 0, first sheet).

    Returns
    -------
    x : numpy.ndarray
    y : numpy.ndarray
    """
    try:
        import requests
    except ImportError as exc:
        raise ImportError("Please install 'requests': pip install requests") from exc
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "Please install 'pandas' and 'openpyxl': pip install pandas openpyxl"
        ) from exc

    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    download_url = _make_download_url(url)
    print(f"  Fetching: {download_url}")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; ExponentialFit/2.0)"}
    resp = requests.get(download_url, headers=headers, timeout=60, allow_redirects=True)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    raw = io.BytesIO(resp.content)

    if "csv" in content_type or download_url.lower().endswith(".csv"):
        df = pd.read_csv(raw)
    elif download_url.lower().endswith(".xls"):
        df = pd.read_excel(raw, sheet_name=sheet_name, engine="xlrd")
    else:
        # Default: try Excel (xlsx); fall back to CSV if that fails
        try:
            df = pd.read_excel(raw, sheet_name=sheet_name, engine="openpyxl")
        except Exception:
            raw.seek(0)
            df = pd.read_csv(raw)

    x = pd.to_numeric(df.iloc[:, x_col], errors="coerce")
    y = pd.to_numeric(df.iloc[:, y_col], errors="coerce")
    # Drop rows where either column is NaN so x and y stay aligned
    valid = x.notna() & y.notna()
    return x[valid].values.astype(float), y[valid].values.astype(float)


# ── PARAMETER CONSTRAINTS ──────────────────────────────────────────────────────

def parse_constraints(constraint_exprs):
    """
    Convert a list of constraint expression strings into
    ``scipy.optimize.minimize`` equality-constraint dicts.

    Each string may be written as an equation::

        "a + c = 1"        →  a + c - 1 = 0
        "b = -2 * d"       →  b + 2*d   = 0

    or as an expression that must equal zero::

        "a + c - 1"

    Allowed names: ``a``, ``b``, ``c``, ``d``, ``exp``, ``log``, ``log2``,
    ``log10``, ``sqrt``, ``abs``, ``sin``, ``cos``, ``tan``, ``pi``, ``e``.

    Parameters
    ----------
    constraint_exprs : list of str

    Returns
    -------
    list of dict
        Each dict has keys ``'type'`` (``'eq'``) and ``'fun'``.
    """
    if not constraint_exprs:
        return []

    scipy_constraints = []
    for raw in constraint_exprs:
        raw = raw.strip()
        if not raw:
            continue

        # Split on a lone '=' (not part of ==, !=, <=, >=)
        eq_match = re.search(r"(?<![!<>=])=(?!=)", raw)
        if eq_match:
            pos = eq_match.start()
            lhs = raw[:pos].strip()
            rhs = raw[pos + 1:].strip()
            expr_zero = f"({lhs}) - ({rhs})"
        else:
            expr_zero = raw

        def _make_fun(expr):
            def fun(params):
                return _eval_constraint_expr(
                    expr,
                    float(params[0]),
                    float(params[1]),
                    float(params[2]),
                    float(params[3]),
                )
            return fun

        scipy_constraints.append({"type": "eq", "fun": _make_fun(expr_zero)})

    return scipy_constraints


def validate_constraints(constraint_exprs, test_params=(1.0, -1.0, 1.0, -0.1)):
    """
    Parse and sanity-check constraint expressions.

    Raises ``ValueError`` if any expression cannot be evaluated.

    Parameters
    ----------
    constraint_exprs : list of str
    test_params : tuple, optional
        Parameter values used for the trial evaluation.

    Returns
    -------
    list of dict
        Parsed scipy constraints ready for ``scipy.optimize.minimize``.
    """
    constraints = parse_constraints(constraint_exprs)
    for i, c in enumerate(constraints):
        try:
            val = c["fun"](test_params)
            float(val)
        except Exception as exc:
            raise ValueError(
                f"Constraint #{i + 1} '{constraint_exprs[i]}' could not be evaluated: {exc}"
            ) from exc
    return constraints


# ── FITTING ────────────────────────────────────────────────────────────────────

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


# ── OUTPUT ─────────────────────────────────────────────────────────────────────

def plot_fit(x, y, popt, r_squared, constraint_exprs=None,
             title="Double-Exponential Fit"):
    """
    Plot observed data alongside the fitted curve and save to PNG.

    Parameters
    ----------
    x : array-like
    y : array-like
    popt : array-like
        Fitted parameters ``[a, b, c, d]``.
    r_squared : float
    constraint_exprs : list of str, optional
        Constraint strings shown in the legend.
    title : str, optional
    """
    x = np.asarray(x, dtype=float)
    x_smooth = np.linspace(x.min(), x.max(), 500)
    y_fit = double_exponential(x_smooth, *popt)

    a, b, c, d = popt
    equation = (
        f"f(x) = {a:.4f}\u00b7exp({b:.4f}\u00b7x)"
        f" + {c:.4f}\u00b7exp({d:.4f}\u00b7x)"
    )
    label = f"Fitted curve\n{equation}\nR\u00b2 = {r_squared:.6f}"
    if constraint_exprs:
        label += "\nConstraints: " + " | ".join(constraint_exprs)

    plt.figure(figsize=(9, 5))
    plt.scatter(x, y, color="steelblue", label="Observed data", zorder=5)
    plt.plot(x_smooth, y_fit, color="tomato", linewidth=2, label=label)
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig("exponential_fit_result.png", dpi=150)
    plt.show()
    print("Plot saved to exponential_fit_result.png")


def print_results(popt, pcov, r_squared, constraint_exprs=None, true_params=None):
    """
    Print a formatted table of the fitting results.

    Parameters
    ----------
    popt : array-like
    pcov : array-like
    r_squared : float
    constraint_exprs : list of str, optional
    true_params : tuple, optional
        Known true parameter values for comparison (demo mode only).
    """
    param_names = ["a", "b", "c", "d"]
    param_std = np.sqrt(np.diag(pcov))

    print("\n" + "=" * 62)
    print("  Double-Exponential Fit Results  /  双指数函数拟合结果")
    print("=" * 62)
    print("  Model: f(x) = a\u00b7exp(b\u00b7x) + c\u00b7exp(d\u00b7x)")
    if constraint_exprs:
        print("  Constraints applied / 已施加约束条件:")
        for expr in constraint_exprs:
            print(f"    \u2022 {expr}")
    print("-" * 62)
    header = f"  {'Param':>5}  {'Fitted value':>14}  {'Std error':>12}"
    if true_params is not None:
        header += f"  {'True value':>12}"
    print(header)
    print("-" * 62)
    for i, name in enumerate(param_names):
        line = f"  {name:>5}  {popt[i]:>14.6f}  \u00b1{param_std[i]:>11.6f}"
        if true_params is not None:
            line += f"  {true_params[i]:>12.6f}"
        print(line)
    print("-" * 62)
    print(f"  R\u00b2 = {r_squared:.8f}")
    print("=" * 62 + "\n")


# ── SAMPLE DATA ────────────────────────────────────────────────────────────────

def generate_sample_data(a=3.0, b=-0.5, c=1.5, d=-0.05,
                         x_start=0.0, x_end=10.0, n_points=80,
                         noise_std=0.15, random_seed=42):
    """
    Generate noisy sample data from a known double-exponential model.

    Parameters
    ----------
    a, b, c, d : float
        True parameter values.
    x_start, x_end : float
        Range of the independent variable.
    n_points : int
        Number of data points.
    noise_std : float
        Noise level as a multiplier of the signal's standard deviation
        (i.e. the noise std dev = ``noise_std * std(y_clean)``).
    random_seed : int
        Random seed for reproducibility.

    Returns
    -------
    x : numpy.ndarray
    y : numpy.ndarray
    true_params : tuple
        ``(a, b, c, d)``
    """
    rng = np.random.default_rng(random_seed)
    x = np.linspace(x_start, x_end, n_points)
    y_clean = double_exponential(x, a, b, c, d)
    noise = rng.normal(0, noise_std * np.std(y_clean), size=n_points)
    return x, y_clean + noise, (a, b, c, d)


# ── INTERACTIVE MAIN ───────────────────────────────────────────────────────────

def main():
    print("=" * 62)
    print("  Double-Exponential Curve Fitting  /  双指数函数拟合")
    print("=" * 62)

    # ── Step 1: Data source ──────────────────────────────────────────────────
    print(
        "\n[1] Data source / 数据来源\n"
        "    Paste an Excel Online / Google Sheets / direct file URL,\n"
        "    or press Enter to use built-in sample data.\n"
        "    (Column 1 = x axis, Column 2 = y axis)\n"
    )
    url = input("  URL: ").strip()

    true_params = None
    if url:
        print("  Loading data from URL...")
        x, y = load_data_from_url(url)
        print(f"  Loaded {len(x)} data points.")
    else:
        print("  Using built-in sample data (a=3, b=-0.5, c=1.5, d=-0.05).")
        x, y, true_params = generate_sample_data()

    # ── Step 2: Parameter constraints ───────────────────────────────────────
    print(
        "\n[2] Parameter constraints / 参数约束条件\n"
        "    Write equality constraints between a, b, c, d.\n"
        "    Allowed functions: exp, log, sqrt, abs, sin, cos, tan, pi, e\n"
        "    Examples:\n"
        "      a + c = 1\n"
        "      b = -2 * d\n"
        "      a * d - b * c = 0\n"
        "    Enter one constraint per line; press Enter on a blank line when done.\n"
        "    (Press Enter immediately to fit without constraints.)\n"
    )
    constraint_exprs = []
    while True:
        line = input(f"  Constraint {len(constraint_exprs) + 1}: ").strip()
        if not line:
            break
        try:
            validate_constraints([line])
            constraint_exprs.append(line)
            print(f"    \u2713 Accepted: {line}")
        except ValueError as exc:
            print(f"    \u2717 Error: {exc}  — please re-enter.")

    # ── Step 3: Initial parameter guesses ────────────────────────────────────
    print(
        "\n[3] Initial parameter guesses / 初始参数猜测 [a, b, c, d]\n"
        "    Press Enter to use defaults [1.0, -1.0, 1.0, -0.1].\n"
    )
    p0_raw = input("  p0 (four comma-separated numbers): ").strip()
    p0 = None
    if p0_raw:
        try:
            vals = [float(v) for v in p0_raw.split(",")]
            if len(vals) != 4:
                raise ValueError("Exactly four values are required.")
            p0 = vals
        except ValueError as exc:
            print(f"  Invalid input ({exc}). Falling back to defaults.")

    # ── Step 4: Fit ──────────────────────────────────────────────────────────
    print("\nFitting / 正在拟合 ...")
    popt, pcov, r_squared = fit_double_exponential(
        x, y,
        p0=p0,
        constraint_exprs=constraint_exprs if constraint_exprs else None,
    )

    # ── Step 5: Results ──────────────────────────────────────────────────────
    print_results(
        popt, pcov, r_squared,
        constraint_exprs=constraint_exprs if constraint_exprs else None,
        true_params=true_params,
    )
    plot_fit(
        x, y, popt, r_squared,
        constraint_exprs=constraint_exprs if constraint_exprs else None,
    )


if __name__ == "__main__":
    main()
