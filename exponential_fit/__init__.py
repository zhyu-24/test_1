"""
exponential_fit — Double-Exponential Curve Fitting
====================================================

Public API
----------
Model
    double_exponential(x, a, b, c, d)

Fitting
    fit_double_exponential(x, y, p0=None, bounds=..., constraint_exprs=None)
    compute_r_squared(y_true, y_pred)

Constraints
    parse_constraints(constraint_exprs)
    validate_constraints(constraint_exprs, test_params=...)

Data loading
    load_data_from_url(url, x_col=0, y_col=1, sheet_name=0)

Sample data / demo
    generate_sample_data(a, b, c, d, ...)

Output
    print_results(popt, pcov, r_squared, ...)
    plot_fit(x, y, popt, r_squared, ...)

CLI
    main()   — interactive command-line session
"""

from .model import double_exponential
from .constraints import parse_constraints, validate_constraints
from .data_loader import load_data_from_url
from .fitting import fit_double_exponential, compute_r_squared
from .output import print_results, plot_fit
from .sample_data import generate_sample_data
from .cli import main

__all__ = [
    "double_exponential",
    "parse_constraints",
    "validate_constraints",
    "load_data_from_url",
    "fit_double_exponential",
    "compute_r_squared",
    "print_results",
    "plot_fit",
    "generate_sample_data",
    "main",
]
