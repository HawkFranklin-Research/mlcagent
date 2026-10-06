from contextlib import contextmanager
from pathlib import Path
import hashlib
import json
import shutil
import sys
import yaml
from filelock import FileLock
from ulid import ULID
from mlca import __version__
from mlca.config import load as load_config, redact
from mlca.errors import MlcaUserError, IntegrityError, BudgetError
from mlca.paths import canonical, sha256
from mlca.log.store import Store
from mlca.log.branches import Branches
from mlca.log.replay import replay
from mlca.templates.loader import load as load_template
from mlca.templates.model import ActionSpec
from mlca.llm.client import Client
from mlca.llm.usage import read as read_usage,summary
from mlca.engine import gates,checks
from mlca.engine.options import fallback,parameters
from mlca.engine.scope_guard import layer_one
from mlca.engine.turn import execute
from mlca.runner.run_step import inputs_for
from mlca.project.files import materialise


class Session:
    def __init__(self,path: Path,client='cli'):
        self.root=path.resolve()
        settings=self.root/'.mlca/project.yaml'
        if not settings.exists():
            raise MlcaUserError('No MLCA project here; initialize or open a project folder')
        self.settings=yaml.safe_load(settings.read_text())
        self.store=Store(self.root)
        self.branches=Branches(self.store)
        self.branch_name=self.branches.current()
        self.workflow=load_template(self.root/'.mlca/template')
        if self.workflow.sha256!=self.settings['template_sha256']:
            raise IntegrityError('Project workflow snapshot changed; start a new study for template changes')
        records=self.store.read()
        created=next((r for r in records if r.type.value=='ProjectCreated'),None)
        if not created or created.payload['template_sha256']!=self.workflow.sha256:
            raise IntegrityError('Project metadata disagrees with immutable log')
        self.config=load_config(self.root)
        self.session_id=str(ULID())
        self.turn_id=None
        self.output_callback=None
        self.client=Client(self.root,self.config,self.emit)
        self.client_name=client
        self.closed=False
        self.emit('SessionStarted',{'client':client,'mlca_version':__version__,
                  'config_hash':hashlib.sha256(canonical(self.config.model_dump(mode='json')).encode()).hexdigest()})

    @classmethod
    def open(cls,path,client='cli'):
        return cls(Path(path),client)

    @property
    def state(self):
        return replay(self.branches.records(self.branch_name))

    def redact(self,text):
        return redact(text,self.config)

    def emit(self,kind,payload,*,step_id=None,actor='engine',event_id=None):
        event_id=event_id if event_id is not None else self.state.current_event
        payload=json.loads(self.redact(canonical(payload)))
        return self.store.append(kind,payload,branch=self.branch_name,session_id=self.session_id,
                                 actor=actor,event_id=event_id,step_id=step_id)

    @contextmanager
    def mutation(self):
        with FileLock(str(self.root/'.mlca/action.lock'),timeout=0):
            yield

    def subscribe(self,callback):
        self.store.callbacks.append(callback)
        return lambda:self.store.callbacks.remove(callback)

    def packages(self):
        file=self.root/'.mlca/requirements.lock'
        return file.read_text().splitlines() if file.exists() else []

    def status(self,recheck=False):
        if recheck:
            with self.mutation():
                checks.run_all(self.state,self.workflow,self.root,self.emit)
        state=self.state
        return {**state.model_dump(mode='json'),'branch':self.branch_name,
                'usage':summary(read_usage(self.root)),'workflow':self.workflow.spec.model_dump(),
                'event_spec':self.workflow.events[state.current_event].model_dump()}

    def options(self):
        with self.mutation():
            state=self.state
            if state.pending_options is None:
                source,request_id='fallback',None
                if state.event_statuses.get(state.current_event)=='done':
                    options=[]
                elif 'navigator' in self.config.roles:
                    from mlca.roles.navigator import Navigator
                    try:
                        options,request_id=Navigator(self).propose_options()
                        source='navigator'
                    except BudgetError:
                        raise
                    except (MlcaUserError,ValueError,TypeError):
                        options=fallback(state,self.workflow)
                else:
                    options=fallback(state,self.workflow)
                self.emit('OptionsProposed',{'options':options,'source':source,'navigator_request_id':request_id})
            options=list(self.state.pending_options or [])
            state=self.state
            ids=self.workflow.spec.events
            index=ids.index(state.current_event)
            if state.event_statuses.get(state.current_event)=='done' and index+1<len(ids):
                target=ids[index+1]
                if gates.check(target,state,self.workflow,self.root)[0]:
                    options.append({'id':'next','title':f'Continue to {target}'})
            if state.current_event=='validate' and not self._ever_unlocked():
                for transition in self.workflow.spec.transitions.get('loops',[]):
                    if transition['from']=='validate':
                        for target in transition['to']:
                            options.append({'id':'loop:'+target,'title':f'Return to {target}'})
            options.append({'id':'custom','title':'Custom instruction (current event scope)'})
            return options

    def choose(self,n):
        options=self.options()
        choice=next((o for o in options if o['id']==str(n)),None)
        if choice is None:
            raise MlcaUserError('Choose an available option')
        if choice['id']=='next':
            return self.next()
        if choice['id'].startswith('loop:'):
            return self.loop(choice['id'].split(':',1)[1])
        if choice['id']=='custom':
            raise MlcaUserError('Use custom(text) to provide an instruction')
        with self.mutation():
            state=self.state
            action=self.workflow.actions[choice['action_id']]
            if action.id not in self.workflow.events[state.current_event].actions:
                raise MlcaUserError('Option is stale; request current options')
            values=parameters(action,choice['params'],state)
            self.emit('OptionChosen',{'option_id':choice['id']},actor='user')
            return execute(self,action,values)

    def custom(self,text):
        with self.mutation():
            state=self.state
            event=self.workflow.events[state.current_event]
            self.emit('CustomInstructionSubmitted',{'text':text},actor='user')
            refs=event.custom_scope.readable_inputs
            if state.split:
                refs=[r for r in refs if r!='registered_data']
            reads_test='test' in refs and event.id=='test' and state.test_unlocked
            if not reads_test:
                refs=[r for r in refs if r!='test']
            action=ActionSpec(id='custom',event=event.id,title='Custom instruction',
                              prompt=event.custom_scope.description+'\n'+text,
                              inputs=[{'ref':ref} for ref in refs],outputs=[],reads_test=reads_test)
            allowed=inputs_for(action,state,self.root)
            reason=layer_one(text,event,state,list(allowed.values()))
            if reason:
                self.emit('ScopeDecision',{'layer':1,'decision':'reject','reason':reason})
                return {'decision':'reject','reason':reason}
            self.emit('ScopeDecision',{'layer':1,'decision':'in_scope','reason':'Deterministic checks passed'})
            from mlca.roles.navigator import Navigator
            self.turn_id=str(ULID())
            decision=Navigator(self).classify_scope(text)
            self.emit('ScopeDecision',{'layer':2,**decision.model_dump()})
            self.turn_id=None
            if decision.decision!='in_scope':
                result=decision.model_dump()
                if decision.target_event in self.workflow.events:
                    result['gate']=gates.check(decision.target_event,state,self.workflow,self.root)
                return result
            return execute(self,action,{})

    def _ever_unlocked(self):
        return any(r.type.value=='TestUnlocked' for r in self.store.read())

    def _enter(self,target,via):
        state=self.state
        if target not in self.workflow.events:
            raise MlcaUserError('Unknown workflow event')
        if not gates.check(target,state,self.workflow,self.root,self.emit)[0]:
            return {'entered':False,'event':target}
        invalidate=[]
        if via=='loop':
            if self._ever_unlocked():
                raise MlcaUserError('Validation iteration is closed after test exposure; start a separate protocol')
            ids=self.workflow.spec.events
            invalidate=ids[ids.index(target):]
        self.emit('EventEntered',{'event_id':target,'via':via,'invalidate_events':invalidate},event_id=target)
        return {'entered':True,'event':target}

    def next(self):
        with self.mutation():
            checks.run_all(self.state,self.workflow,self.root,self.emit)
            state=self.state
            ids=self.workflow.spec.events
            index=ids.index(state.current_event)
            if state.event_statuses.get(state.current_event)!='done':
                raise MlcaUserError('Current event still has incomplete sub-goals')
            if index+1==len(ids):
                return {'complete':True}
            return self._enter(ids[index+1],'next')

    def loop(self,event):
        with self.mutation():
            if not any(t['from']==self.state.current_event and event in t['to'] for t in self.workflow.spec.transitions.get('loops',[])):
                raise MlcaUserError('Loop is not declared by the workflow template')
            return self._enter(event,'loop')

    def goto(self,event):
        with self.mutation():
            if not any(t['from']==self.state.current_event and event in t['to'] for t in self.workflow.spec.transitions.get('goto',[])):
                raise MlcaUserError('Transition is not declared by the workflow template')
            return self._enter(event,'goto')

    def confirm(self,subgoal,note):
        with self.mutation():
            event=self.workflow.events[self.state.current_event]
            if subgoal not in {s.id for s in event.subgoals if s.check.type=='user_confirm'} or not note.strip():
                raise MlcaUserError('Confirm a current user-confirmation sub-goal with a note')
            self.emit('UserConfirmed',{'subgoal_id':event.id+'.'+subgoal,'note':note},actor='user')
            checks.run_all(self.state,self.workflow,self.root,self.emit)
            return self.status()

    def unlock_test(self,phrase,reason='First planned test evaluation'):
        with self.mutation():
            state=self.state
            if state.current_event!='test' or not state.split or phrase!='UNLOCK TEST' or not reason.strip():
                raise MlcaUserError('In the test event, type UNLOCK TEST and provide the reason')
            self.emit('TestUnlocked',{'confirmation':phrase,'split_sha256':state.split['sha256'],'reason':reason},actor='user')
            return {'test_unlocked':True,'project_unlock_count':sum(r.type.value=='TestUnlocked' for r in self.store.read())}

    def branch(self,name,from_id):
        with self.mutation():
            self.branches.create(name,from_id,self.session_id)
            self.branch_name=name
            materialise(self.root,self.state,self.emit)
            return self.branches.list()

    def checkout(self,name):
        with self.mutation():
            self.branches.checkout(name,self.session_id)
            self.branch_name=name
            materialise(self.root,self.state,self.emit)
            return self.status()

    def report(self,kind='all'):
        from mlca.report import generate
        with self.mutation():
            return generate(self.root,self.state,self.workflow,self.branches.records(self.branch_name),kind)

    def package(self,spec,approve=False,reason='User package request'):
        with self.mutation():
            self.emit('PackageRequested',{'package':spec,'reason':reason},actor='user')
            self.emit('PackageApproved' if approve else 'PackageDenied',{'package':spec},actor='user')
            if approve:
                if self._ever_unlocked():
                    raise MlcaUserError('Environment changes are closed after test exposure')
                from mlca.project.env import install
                record=install(self.root,spec)
                self.emit('EnvironmentRecorded',record)
            return {'approved':approve,'package':spec}

    def verify_scripts(self):
        from mlca.runner.verify import verify
        with self.mutation():
            return verify(self)

    def close(self):
        if not self.closed:
            self.emit('SessionEnded',{'client':self.client_name})
            self.closed=True

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()
