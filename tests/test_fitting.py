"""
Unit tests for the exponential_fit package.

Run with:
    python -m pytest tests/ -v
"""
import numpy as np
import pytest

from exponential_fit.model import double_exponential
from exponential_fit.sample_data import generate_sample_data
from exponential_fit.fitting import fit_double_exponential, compute_r_squared
from exponential_fit.constraints import parse_constraints, validate_constraints
from exponential_fit.data_loader import _make_download_url


# ── model ─────────────────────────────────────────────────────────────────────

class TestModel:
    def test_scalar(self):
        # f(0) = a * 1 + c * 1 = a + c
        assert double_exponential(0, 2, -1, 3, -0.5) == pytest.approx(5.0)

    def test_array(self):
        x = np.array([0.0, 1.0])
        result = double_exponential(x, 1, 0, 1, 0)
        np.testing.assert_allclose(result, [2.0, 2.0])

    def test_shape_preserved(self):
        x = np.linspace(0, 5, 50)
        y = double_exponential(x, 1, -0.5, 2, -0.1)
        assert y.shape == x.shape


# ── compute_r_squared ─────────────────────────────────────────────────────────

class TestRSquared:
    def test_perfect_fit(self):
        y = np.array([1.0, 2.0, 3.0])
        assert compute_r_squared(y, y) == pytest.approx(1.0)

    def test_constant_prediction(self):
        y = np.array([1.0, 2.0, 3.0])
        y_mean = np.full_like(y, y.mean())
        assert compute_r_squared(y, y_mean) == pytest.approx(0.0)


# ── generate_sample_data ──────────────────────────────────────────────────────

class TestSampleData:
    def test_shapes_match(self):
        x, y, _ = generate_sample_data(n_points=50)
        assert x.shape == y.shape == (50,)

    def test_true_params_returned(self):
        _, _, tp = generate_sample_data(a=2.0, b=-1.0, c=0.5, d=-0.1)
        assert tp == (2.0, -1.0, 0.5, -0.1)

    def test_reproducible(self):
        _, y1, _ = generate_sample_data(random_seed=0)
        _, y2, _ = generate_sample_data(random_seed=0)
        np.testing.assert_array_equal(y1, y2)


# ── fitting (unconstrained) ───────────────────────────────────────────────────

class TestFitting:
    def setup_method(self):
        self.x, self.y, self.tp = generate_sample_data()

    def test_returns_correct_shapes(self):
        popt, pcov, r2 = fit_double_exponential(self.x, self.y)
        assert popt.shape == (4,)
        assert pcov.shape == (4, 4)
        assert isinstance(r2, float)

    def test_r_squared_high(self):
        _, _, r2 = fit_double_exponential(self.x, self.y)
        assert r2 > 0.95

    def test_params_close_to_truth(self):
        popt, _, _ = fit_double_exponential(self.x, self.y)
        # Parameters might be swapped between the two exponential terms;
        # check that each fitted value is within 20 % of at least one true value.
        true = np.array(self.tp)
        close = sum(
            any(abs(p - t) <= 0.2 * max(abs(t), 0.1) for t in true)
            for p in popt
        )
        assert close >= 3


# ── fitting (constrained) ─────────────────────────────────────────────────────

class TestConstrainedFitting:
    def test_sum_constraint_satisfied(self):
        x, y, _ = generate_sample_data()
        popt, _, _ = fit_double_exponential(
            x, y,
            p0=[2.0, -0.5, 1.0, -0.05],
            constraint_exprs=["a + c = 4.5"],
        )
        assert abs(popt[0] + popt[2] - 4.5) < 1e-4


# ── constraints ───────────────────────────────────────────────────────────────

class TestConstraints:
    def test_equation_form(self):
        cs = parse_constraints(["a + c = 1"])
        assert len(cs) == 1
        # At a=0.5, c=0.5 the constraint should be zero
        assert cs[0]["fun"]([0.5, -1, 0.5, -0.1]) == pytest.approx(0.0)

    def test_expression_form(self):
        cs = parse_constraints(["a + c - 1"])
        assert cs[0]["fun"]([0.5, -1, 0.5, -0.1]) == pytest.approx(0.0)

    def test_empty_input(self):
        assert parse_constraints([]) == []

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError, match="Unknown name"):
            validate_constraints(["z = 1"])

    def test_invalid_function_raises(self):
        with pytest.raises(ValueError, match="Unknown function"):
            validate_constraints(["eval(a)"])

    def test_multiple_constraints(self):
        cs = parse_constraints(["a + c = 1", "b = -2 * d"])
        assert len(cs) == 2


# ── URL conversion ────────────────────────────────────────────────────────────

class TestMakeDownloadUrl:
    def test_google_sheets(self):
        url = "https://docs.google.com/spreadsheets/d/SHEET_ID/edit?usp=sharing"
        result = _make_download_url(url)
        assert "export?format=csv" in result
        assert "SHEET_ID" in result

    def test_google_sheets_with_gid(self):
        url = "https://docs.google.com/spreadsheets/d/ID/edit#gid=123"
        result = _make_download_url(url)
        assert "gid=123" in result

    def test_onedrive_adds_download(self):
        url = "https://onedrive.live.com/view?resid=XYZ"
        result = _make_download_url(url)
        assert "download=1" in result

    def test_direct_csv_unchanged(self):
        url = "https://example.com/data.csv"
        assert _make_download_url(url) == url

    def test_direct_xlsx_unchanged(self):
        url = "https://example.com/data.xlsx"
        assert _make_download_url(url) == url
