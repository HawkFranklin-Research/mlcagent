from pathlib import Path
import shutil
from mlca.errors import IntegrityError
from mlca.paths import atomic_json, sha256, contained


def materialise(root: Path, state, emit=None) -> list[dict]:
    cache = root/'.mlca/views.json'
    import json
    previous = json.loads(cache.read_text()) if cache.exists() else {}
    changes = []
    for relative,expected in previous.items():
        path = root/relative
        if path.exists() and sha256(path)!=expected:
            change = {'step_id':relative,'old_sha256':expected,'new_sha256':sha256(path)}
            if emit:
                emit('ScriptEditedByUser',change)
            changes.append(change)
    if changes:
        return changes  # Never silently overwrite user changes.
    desired = {}
    for step in state.steps:
        if step['status']!='completed':
            continue
        src = root/'.mlca/steps'/step['step_id']/'script.py'
        if src.exists():
            script_record = step.get('scripts',[])
            if script_record and sha256(src)!=script_record[-1]['sha256']:
                raise IntegrityError('Completed step script changed')
            destination = root/'scripts'/f'{step["number"]:02d}_{step["event_id"]}_{step["action_id"]}.py'
            desired[str(destination.relative_to(root))] = src
        for output in step.get('outputs',[]):
            source = root/output['path']
            if not contained(source,root/'.mlca/steps') or sha256(source)!=output['sha256']:
                raise IntegrityError('Recorded artifact changed')
            folder = 'figures' if output['kind']=='figure' else 'tables' if output['kind']=='table' else 'reports'
            destination = root/folder/step['step_id']/output['name']
            desired[str(destination.relative_to(root))] = source
    for relative in previous:
        if relative not in desired:
            (root/relative).unlink(missing_ok=True)
    hashes = {}
    for relative,source in desired.items():
        destination = root/relative
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination)
        hashes[relative] = sha256(destination)
    atomic_json(cache,hashes)
    atomic_json(root/'.mlca/state.json',state.model_dump(mode='json'))
    lines = ['# Project log','',f'Event: {state.current_event}','']
    lines.extend(f'- {s["step_id"]}: {s["status"]}' for s in state.steps)
    (root/'PROJECT_LOG.md').write_text('\n'.join(lines)+'\n')
    return []
