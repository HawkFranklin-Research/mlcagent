from pathlib import Path
import sys
from mlca.errors import MlcaUserError


def build(python: Path, step: Path, declared: list[Path], env_root: Path,
          runtime: Path, style: Path, allow_network=False) -> list[str]:
    command = ['bwrap','--die-with-parent','--new-session','--unshare-user','--unshare-pid',
               '--unshare-ipc','--unshare-uts','--proc','/proc','--dev','/dev','--tmpfs','/tmp']
    if not allow_network:
        command += ['--unshare-net']
    # Do not bind / or a home directory. Python binaries may point into a base interpreter.
    candidates = [Path('/usr'),Path('/bin'),Path('/lib'),Path('/lib64'),
                  Path(sys.base_prefix)/'bin',Path(sys.base_prefix)/'lib',env_root,runtime,style]
    mounted = set()
    for path in candidates + declared:
        path = path.absolute()
        if not path.exists():
            if path in declared:
                raise MlcaUserError(f'Declared input is missing: {path}')
            continue
        text = str(path)
        if text in mounted:
            continue
        command += ['--ro-bind',text,text]
        mounted.add(text)
    command += ['--bind',str(step),str(step),'--chdir',str(step),str(python),str(step/'script.py')]
    return command
