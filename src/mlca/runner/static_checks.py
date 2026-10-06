import ast
from pathlib import Path

FORBIDDEN = {'subprocess','socket','requests','urllib','http','ctypes','multiprocessing','importlib'}


def check(source: str, allow_network=False, require_fit=False) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f'Syntax error at line {exc.lineno}: {exc.msg}']
    violations = []
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names = [a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else [(node.module or '').split('.')[0]]
            for name in names:
                if name in FORBIDDEN and not (allow_network and name in {'socket','requests','urllib','http'}):
                    violations.append(f'line {node.lineno}: forbidden import {name}')
        if isinstance(node,ast.Call):
            function = node.func
            name = function.id if isinstance(function,ast.Name) else function.attr if isinstance(function,ast.Attribute) else ''
            if name in {'exec','eval','__import__','system','popen','spawn','fork'}:
                violations.append(f'line {node.lineno}: forbidden call {name}')
            if require_fit and name in {'fit','fit_transform','partial_fit'}:
                violations.append(f'line {node.lineno}: fit must use mlca_runtime.fit_record')
        if isinstance(node,ast.Constant) and isinstance(node.value,str):
            value = node.value
            if '.mlca/vault' in value or '.mlca/data/splits' in value or '/keys/' in value:
                violations.append(f'line {node.lineno}: private path literal')
            if value.startswith(('/', '~/', '../')):
                violations.append(f'line {node.lineno}: use declared runtime inputs, not absolute/parent paths')
    if require_fit and not any(isinstance(n,ast.Call) and
                              ((isinstance(n.func,ast.Attribute) and n.func.attr=='fit_record') or
                               (isinstance(n.func,ast.Name) and n.func.id=='fit_record')) for n in ast.walk(tree)):
        violations.append('Fit stage must record at least one fit via mlca_runtime.fit_record')
    return violations
