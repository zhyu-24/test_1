"""
Synthetic sample-data generator for demo / testing.
"""
import numpy as np
from .model import double_exponential


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
