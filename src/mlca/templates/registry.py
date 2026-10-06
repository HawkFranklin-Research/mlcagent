from pathlib import Path
from mlca.paths import resource, user_config_dir
from mlca.errors import MlcaUserError
from .loader import load


def available() -> dict[str, Path]:
    result = {}
    for root in [resource('templates'), user_config_dir()/'templates']:
        if root.exists():
            for path in sorted(root.iterdir()):
                if (path/'template.yaml').is_file():
                    result[path.name] = path
    return result


def get(identifier: str):
    path = Path(identifier)
    if path.is_dir():
        return load(path)
    choices = available()
    if identifier not in choices:
        raise MlcaUserError(f'Unknown workflow template: {identifier}')
    return load(choices[identifier])
