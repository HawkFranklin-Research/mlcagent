from pathlib import Path

# Original hook, intentionally defensive; documented as weaker than namespace isolation.
SOURCE = '''import json, os, pathlib, sys
rules = json.loads(os.environ["MLCA_AUDIT_RULES"])
read_roots = [pathlib.Path(p).resolve() for p in rules["read_roots"]]
write_roots = [pathlib.Path(p).resolve() for p in rules["write_roots"]]
def inside(path, roots):
    return any(path == root or path.is_relative_to(root) for root in roots)
def guard(event, args):
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = pathlib.Path(os.fsdecode(args[0])).resolve()
        mode = args[1] or ""
        flags = args[2] if len(args)>2 else 0
        write = (isinstance(mode,str) and any(c in mode for c in "wax+")) or bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if not inside(path, write_roots if write else read_roots):
            raise PermissionError("MLCA blocked an undeclared file access")
    elif event in ("os.system", "subprocess.Popen", "os.posix_spawn"):
        raise PermissionError("MLCA blocked child process creation")
    elif event.startswith("socket.") and not rules["network"]:
        raise PermissionError("MLCA blocked network access")
sys.addaudithook(guard)
'''


def install(directory: Path) -> Path:
    directory.mkdir(parents=True,exist_ok=True)
    path = directory/'sitecustomize.py'
    path.write_text(SOURCE)
    return directory
