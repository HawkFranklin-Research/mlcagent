from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from mlca.sandbox.bwrap import build
from mlca.sandbox.audit_hook import install

CAP = 1024 * 1024


def execute(python: Path, step: Path, declared: list[Path], env_root: Path, runtime: Path,
            style: Path, level: str, timeout_s: int, train_index_sha256='', allow_network=False,
            callback=None) -> dict:
    with tempfile.TemporaryDirectory(prefix='mlca-home-') as temporary:
        env = {'PATH':str(python.parent)+os.pathsep+'/usr/bin:/bin', 'HOME':temporary,
               'LANG':'C.UTF-8','MPLBACKEND':'Agg','PYTHONHASHSEED':'0','PYTHONDONTWRITEBYTECODE':'1',
               'MLCA_STEP_DIR':str(step),'MLCA_STYLE':str(style),
               'MLCA_TRAIN_INDEX_SHA256':train_index_sha256,'TMPDIR':'/tmp'}
        hooks = install(step/'hooks')
        read_roots = [str(p) for p in declared]+[str(step),str(env_root),str(runtime),str(style),
                      '/usr','/lib','/lib64','/bin',str(Path(sys.base_prefix)/'lib'),
                      str(Path(sys.base_prefix)/'bin'),'/dev/null','/dev/urandom','/tmp']
        env['PYTHONPATH'] = str(hooks)
        env['MLCA_AUDIT_RULES'] = json.dumps({'read_roots':read_roots,
                                            'write_roots':[str(step/'outputs'),str(step/'manifest.json'),str(step/'scratch'),'/tmp'],
                                            'network':allow_network})
        # Both levels use the hook. A also has filesystem/network namespaces.
        args = build(python,step,declared,env_root,runtime,style,allow_network) if level=='A' else [str(python),str(step/'script.py')]
        start = time.monotonic()
        proc = subprocess.Popen(args,cwd=step,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                start_new_session=True)
        buffers, counts = {'stdout':bytearray(),'stderr':bytearray()}, {'stdout':0,'stderr':0}
        def drain(stream, name):
            with (step/f'{name}.txt').open('wb') as output:
                while chunk := stream.read(8192):
                    counts[name]+=len(chunk)
                    remaining = max(0,CAP-output.tell())
                    output.write(chunk[:remaining])
                    buffers[name].extend(chunk)
                    if len(buffers[name])>CAP:
                        del buffers[name][:-CAP]
                    if callback:
                        callback(name,chunk.decode(errors='replace'))
        threads = [threading.Thread(target=drain,args=(stream,name),daemon=True)
                   for stream,name in [(proc.stdout,'stdout'),(proc.stderr,'stderr')]]
        for thread in threads:
            thread.start()
        timeout = False
        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(proc.pid,signal.SIGKILL) if os.name=='posix' else proc.kill()
            proc.wait()
        except BaseException:
            os.killpg(proc.pid,signal.SIGKILL) if os.name=='posix' else proc.kill()
            proc.wait()
            raise
        finally:
            # Terminate surviving children before joining pipe readers.
            if os.name=='posix':
                try:
                    os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError:
                    pass
            for thread in threads:
                thread.join(timeout=5)
        return {'exit_status':proc.returncode,'duration':time.monotonic()-start,'timed_out':timeout,
                'sandbox_level':level,**{k:bytes(v).decode(errors='replace') for k,v in buffers.items()},
                **{f'{k}_clipped':n>CAP for k,n in counts.items()}}
