from pathlib import Path
import shutil
import subprocess
import sys
import yaml
from mlca.errors import MlcaUserError
from mlca.paths import sha256


def python(env: Path) -> Path:
    return env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')


def command(args: list[str], root: Path) -> str:
    result = subprocess.run(args,cwd=root,capture_output=True,text=True)
    if result.returncode:
        raise MlcaUserError('Project environment command failed: ' + result.stderr[-2000:])
    return result.stdout


def create(root: Path, packages: list[str], frozen: Path | None = None) -> dict:
    uv = shutil.which('uv')
    if not uv:
        raise MlcaUserError('uv is required to create the separate analysis environment')
    env = root/'.mlca/env'
    if env.exists():
        raise MlcaUserError('Analysis environment already exists')
    command([uv,'venv',str(env),'--python',sys.executable],root)
    # Snapshot the standalone runtime package; no editable link to the whole harness.
    import mlca_runtime
    runtime = root/'.mlca/runtime'
    shutil.copytree(Path(mlca_runtime.__file__).parent,runtime/'mlca_runtime',
                    ignore=shutil.ignore_patterns('__pycache__'))
    (runtime/'pyproject.toml').write_text('[build-system]\nrequires=["hatchling"]\nbuild-backend="hatchling.build"\n'
                                       '[project]\nname="mlca-runtime"\nversion="0.2.0"\n'
                                       '[tool.hatch.build.targets.wheel]\npackages=["mlca_runtime"]\n')
    if frozen:
        command([uv,'pip','install','--python',str(python(env)),'-r',str(frozen)],root)
    elif packages:
        command([uv,'pip','install','--python',str(python(env)),*packages],root)
    command([uv,'pip','install','--python',str(python(env)),str(runtime)],root)
    return lock(root)


def lock(root: Path) -> dict:
    env = root/'.mlca/env'
    content = command(['uv','pip','freeze','--python',str(python(env))],root)
    file = root/'.mlca/requirements.lock'
    # Exclude the local runtime path; copied and installed separately during reproduction.
    lines = [line for line in content.splitlines() if not line.lower().startswith('mlca-runtime')]
    file.write_text('\n'.join(lines)+'\n')
    return {'lock_sha256':sha256(file),'packages':lines}


def install(root: Path, package: str) -> dict:
    if package.startswith('-') or any(c in package for c in '\n\r'):
        raise MlcaUserError('Invalid package specification')
    command(['uv','pip','install','--python',str(python(root/'.mlca/env')),package],root)
    return lock(root)
