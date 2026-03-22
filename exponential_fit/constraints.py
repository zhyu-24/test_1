"""
Safe mathematical expression evaluator and parameter-constraint helpers.

The evaluator parses expressions via the Python AST and supports only a
tightly controlled subset of nodes: arithmetic operators, the four model
parameters (a, b, c, d), numeric constants, and a fixed whitelist of
mathematical functions.  No Python built-ins are accessible.
"""
import ast
import operator
import re
import numpy as np

# ── Whitelisted names and operators ───────────────────────────────────────────

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
