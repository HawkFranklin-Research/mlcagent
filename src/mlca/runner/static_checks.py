import ast
import re
from typing import Any

FORBIDDEN = {"subprocess", "socket", "requests", "urllib", "http", "ctypes", "multiprocessing", "importlib"}


def check(source: str, allow_network: Any = False, require_fit: Any = False) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"Syntax error at line {exc.lineno}: {exc.msg}"]
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = (
                [a.name.split(".")[0] for a in node.names]
                if isinstance(node, ast.Import)
                else [(node.module or "").split(".")[0]]
            )
            for name in names:
                if name in FORBIDDEN and not (
                    allow_network and name in {"socket", "requests", "urllib", "http"}
                ):
                    violations.append(f"line {node.lineno}: forbidden import {name}")
        if isinstance(node, ast.Call):
            function = node.func
            name = (
                function.id
                if isinstance(function, ast.Name)
                else function.attr
                if isinstance(function, ast.Attribute)
                else ""
            )
            if name in {"exec", "eval", "__import__", "system", "popen", "spawn", "fork"}:
                violations.append(f"line {node.lineno}: forbidden call {name}")
            if require_fit and name in {"fit", "fit_transform", "partial_fit"}:
                violations.append(
                    f"line {node.lineno}: fit must use mlca_runtime.fit_record. "
                    "This includes temporary/univariable models and feature-selection fits. "
                    "Use fit_record(estimator, training_dataframe, 'train', y=target_if_needed, "
                    "**fit_kwargs); transform separately. For Cox fits, pass duration_col= and event_col=."
                )
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if ".mlca/vault" in value or ".mlca/data/splits" in value or "/keys/" in value:
                violations.append(f"line {node.lineno}: private path literal")
            # A path names something after the prefix; a bare "/" (k.split("/")) is a separator.
            if re.match(r"(/[^/\s]|~/|\.\./)", value):
                violations.append(
                    f"line {node.lineno}: path literal {value[:60]!r}; use declared runtime inputs, not absolute/parent paths"
                )
    if require_fit and not any(
        isinstance(n, ast.Call)
        and (
            (isinstance(n.func, ast.Attribute) and n.func.attr == "fit_record")
            or (isinstance(n.func, ast.Name) and n.func.id == "fit_record")
        )
        for n in ast.walk(tree)
    ):
        violations.append(
            "Steps in this event must fit on the training partition with fit_record. For read-only inspection, use the validate or interpret event."
        )
    return violations
