"""
Output helpers: console results table and matplotlib plot.
"""
import numpy as np
import matplotlib.pyplot as plt

from .model import double_exponential


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
