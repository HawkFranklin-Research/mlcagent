

def build(state):
    return [{'step_id':s['step_id'],**figure} for s in state.steps if s['status']=='completed'
            for figure in s.get('figures',[])]
