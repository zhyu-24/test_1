"""
双指数函数线性组合数据拟合
Data fitting using a linear combination of two exponential functions.

Model: f(x) = a * exp(b * x) + c * exp(d * x)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def double_exponential(x, a, b, c, d):
    """
    线性组合双指数函数模型
    Linear combination of two exponential functions.

    f(x) = a * exp(b * x) + c * exp(d * x)

    Parameters
    ----------
    x : array-like
        自变量 / Independent variable.
    a : float
        第一指数项的幅值 / Amplitude of the first exponential term.
    b : float
        第一指数项的衰减/增长率 / Rate of the first exponential term.
    c : float
        第二指数项的幅值 / Amplitude of the second exponential term.
    d : float
        第二指数项的衰减/增长率 / Rate of the second exponential term.

    Returns
    -------
    numpy.ndarray
        模型预测值 / Model predictions.
    """
    return a * np.exp(b * x) + c * np.exp(d * x)


def compute_r_squared(y_true, y_pred):
    """
    计算决定系数 R²
    Compute the coefficient of determination R².

    Parameters
    ----------
    y_true : array-like
        真实观测值 / Observed values.
    y_pred : array-like
        模型预测值 / Predicted values.

    Returns
    -------
    float
        R² 值 / R² value.
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot


def fit_double_exponential(x, y, p0=None, bounds=(-np.inf, np.inf)):
    """
    对数据进行双指数函数拟合
    Fit data using a linear combination of two exponential functions.

    Parameters
    ----------
    x : array-like
        自变量数据 / Independent variable data.
    y : array-like
        因变量数据 / Dependent variable data.
    p0 : array-like, optional
        初始参数猜测值 [a, b, c, d]，默认为 [1, -1, 1, -0.1]
        Initial parameter guesses [a, b, c, d]. Defaults to [1, -1, 1, -0.1].
    bounds : 2-tuple, optional
        参数的上下界 / Bounds for the parameters.

    Returns
    -------
    popt : numpy.ndarray
        拟合参数 [a, b, c, d] / Fitted parameters [a, b, c, d].
    pcov : numpy.ndarray
        参数的协方差矩阵 / Covariance matrix of the parameters.
    r_squared : float
        R² 值 / R² value.
    """
    if p0 is None:
        p0 = [1.0, -1.0, 1.0, -0.1]

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    popt, pcov = curve_fit(double_exponential, x, y, p0=p0, bounds=bounds, maxfev=10000)
    y_pred = double_exponential(x, *popt)
    r_squared = compute_r_squared(y, y_pred)

    return popt, pcov, r_squared


def plot_fit(x, y, popt, r_squared, title="Double-Exponential Fit"):
    """
    绘制原始数据与拟合曲线
    Plot the raw data and the fitted curve.

    Parameters
    ----------
    x : array-like
        自变量数据 / Independent variable data.
    y : array-like
        因变量数据 / Dependent variable data.
    popt : array-like
        拟合参数 [a, b, c, d] / Fitted parameters [a, b, c, d].
    r_squared : float
        R² 值 / R² value.
    title : str, optional
        图表标题 / Plot title.
    """
    x = np.asarray(x, dtype=float)
    x_smooth = np.linspace(x.min(), x.max(), 500)
    y_fit = double_exponential(x_smooth, *popt)

    a, b, c, d = popt
    equation = (
        f"f(x) = {a:.4f}·exp({b:.4f}·x) + {c:.4f}·exp({d:.4f}·x)"
    )

    plt.figure(figsize=(9, 5))
    plt.scatter(x, y, color="steelblue", label="Observed data", zorder=5)
    plt.plot(x_smooth, y_fit, color="tomato", linewidth=2,
             label=f"Fitted curve\n{equation}\nR\u00b2 = {r_squared:.6f}")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig("exponential_fit_result.png", dpi=150)
    plt.show()
    print("图像已保存至 exponential_fit_result.png")
    print("Plot saved to exponential_fit_result.png")


def generate_sample_data(a=3.0, b=-0.5, c=1.5, d=-0.05,
                         x_start=0.0, x_end=10.0, n_points=80,
                         noise_std=0.15, random_seed=42):
    """
    生成带噪声的双指数示例数据
    Generate noisy sample data from a double-exponential model.

    Parameters
    ----------
    a, b, c, d : float
        真实参数值 / True parameter values.
    x_start, x_end : float
        自变量范围 / Range of the independent variable.
    n_points : int
        数据点数量 / Number of data points.
    noise_std : float
        噪声标准差（相对于信号均值的比例）/ Noise std dev (fraction of mean signal).
    random_seed : int
        随机种子 / Random seed for reproducibility.

    Returns
    -------
    x : numpy.ndarray
    y : numpy.ndarray
    true_params : tuple
        真实参数 (a, b, c, d) / True parameters (a, b, c, d).
    """
    rng = np.random.default_rng(random_seed)
    x = np.linspace(x_start, x_end, n_points)
    y_clean = double_exponential(x, a, b, c, d)
    noise = rng.normal(0, noise_std * np.abs(y_clean).mean(), size=n_points)
    y = y_clean + noise
    return x, y, (a, b, c, d)


def print_results(popt, pcov, r_squared, true_params=None):
    """
    打印拟合结果
    Print the fitting results.
    """
    param_names = ["a", "b", "c", "d"]
    param_std = np.sqrt(np.diag(pcov))

    print("\n" + "=" * 55)
    print("  双指数函数拟合结果 / Double-Exponential Fit Results")
    print("=" * 55)
    print(f"  模型 / Model: f(x) = a·exp(b·x) + c·exp(d·x)")
    print("-" * 55)
    print(f"  {'参数':>4}  {'拟合值':>12}  {'标准误差':>12}", end="")
    if true_params is not None:
        print(f"  {'真实值':>10}", end="")
    print()
    print("-" * 55)
    for i, name in enumerate(param_names):
        line = f"  {name:>4}  {popt[i]:>12.6f}  ±{param_std[i]:>11.6f}"
        if true_params is not None:
            line += f"  {true_params[i]:>10.6f}"
        print(line)
    print("-" * 55)
    print(f"  R²  =  {r_squared:.8f}")
    print("=" * 55 + "\n")


def main():
    print("生成示例数据 / Generating sample data ...")
    x, y, true_params = generate_sample_data()

    print("执行双指数拟合 / Fitting double-exponential model ...")
    popt, pcov, r_squared = fit_double_exponential(x, y)

    print_results(popt, pcov, r_squared, true_params=true_params)

    plot_fit(x, y, popt, r_squared)


if __name__ == "__main__":
    main()
