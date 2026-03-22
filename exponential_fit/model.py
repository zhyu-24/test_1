"""
Model definition: f(x) = a * exp(b*x) + c * exp(d*x)
"""
import numpy as np


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
