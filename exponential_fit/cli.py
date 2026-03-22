"""
Interactive command-line interface.
"""
from .data_loader import load_data_from_url
from .sample_data import generate_sample_data
from .fitting import fit_double_exponential
from .constraints import validate_constraints
from .output import print_results, plot_fit


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
