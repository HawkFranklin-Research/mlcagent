from .checks import evaluate


def check(event_id, state, workflow, root, emit=None):
    failures = []
    for condition in workflow.events[event_id].gate:
        passed, detail = evaluate(condition,state,root,workflow,event_id)
        if not passed:
            failures.append(detail)
    if failures and emit:
        emit('GateBlocked',{'target_event_id':event_id,'failing_conditions':failures})
    return not failures, failures
