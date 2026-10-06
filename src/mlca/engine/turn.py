from ulid import ULID
from mlca.errors import MlcaUserError
from mlca.engine import checks,facts
from mlca.project.files import materialise
from mlca.runner.run_step import run_step
from mlca.roles.navigator import Navigator


def execute(session,action,params):
    session.turn_id=str(ULID())
    session.emit('TurnStarted',{'turn_id':session.turn_id})
    try:
        observation=run_step(session,action,params)
        candidates=[]
        if 'navigator' in session.config.roles:
            try:
                candidates=Navigator(session).extract_facts(observation,action,observation['step_id'])
            except MlcaUserError as exc:
                session.emit('Note',{'text':'Fact extraction unavailable: '+str(exc)})
        # Runtime candidates retain exact source linkage; still subject to evidence validation.
        for candidate in observation.get('facts',[]):
            output=next((o for o in observation['outputs'] if o['name']==candidate.get('source')),None)
            if output:
                candidates.append({**candidate,'source':output['path'],'sha256':output['sha256'],
                                   'step_id':observation['step_id']})
        for candidate in candidates:
            valid,reason=facts.validate(candidate,session.root,session.state)
            if candidate.get('key') not in action.fact_candidates:
                valid,reason=False,'Fact key not declared by action'
            session.emit('FactRecorded' if valid else 'FactRejected',candidate if valid else
                         {'candidate':candidate,'reason':reason},step_id=observation['step_id'],actor='navigator')
        if 'inspector' in session.config.roles:
            from mlca.roles.inspector import Inspector
            for figure in observation['figures']:
                if figure['name'].endswith('.png'):
                    try:
                        note=Inspector(session).describe_figure(session.root/figure['path'],figure.get('caption',''),observation['step_id'])
                        session.emit('ObservationRecorded',{'step_id':observation['step_id'],'note':note},actor='inspector')
                    except MlcaUserError as exc:
                        session.emit('Note',{'text':'Figure inspection unavailable: '+str(exc)})
        checks.run_all(session.state,session.workflow,session.root,session.emit)
        edits=materialise(session.root,session.state,session.emit)
        return {'step_id':observation['step_id'],'status':'completed','observation':observation,'view_edits':edits}
    finally:
        session.emit('TurnEnded',{'turn_id':session.turn_id})
        session.turn_id=None
