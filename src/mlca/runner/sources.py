"""Script sources share run_step.run_attempt; neither source can waive engine checks."""

from mlca.roles.worker import Worker


class ExternalSource:
    """Persist the work order and wait; never invokes a model."""


class WorkerSource:
    def __init__(self, session):
        self.worker = Worker(session)

    def script(self, action, params, inputs, state, step_id, previous, error):
        if error is None:
            return self.worker.write_script(action, params, inputs, state, step_id)
        return self.worker.repair_script(action, previous, error, step_id)
