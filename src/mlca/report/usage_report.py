from mlca.llm.usage import summary


def build(state,requests,records):
    return {**summary(requests), 'steps_completed':sum(s['status']=='completed' for s in state.steps),
            'steps_failed':sum(s['status']=='failed' for s in state.steps),
            'worker_attempts':sum(len(s.get('scripts',[])) for s in state.steps),
            'repairs':sum(max(0,len(s.get('scripts',[]))-1) for s in state.steps),
            'wall_time_s':sum(r.get('duration',0) for s in state.steps for r in s.get('runs',[])),
            'human_interventions':{k:state.counts.get(k,0) for k in ['OptionChosen','CustomInstructionSubmitted',
                 'UserConfirmed','PackageApproved','ScriptEditedByUser','TestUnlocked']},
            'scope_rejections':sum(r.type.value=='ScopeDecision' and r.payload['decision']=='reject' for r in records)}
