from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, create_model, model_validator
from ulid import ULID


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


# Required payload fields, supplemented by independently validated engine contracts.
PAYLOAD_FIELDS = {
    'ProjectCreated': ['project_id','mlca_version','template_id','template_version','template_sha256'],
    'DataRegistered': ['name','original_path','sha256','size','read_only'],
    'InventoryRecorded': ['files','sha256'], 'BriefRecorded': ['answers'],
    'SessionStarted': ['client','mlca_version','config_hash'], 'SessionEnded': ['client'],
    'EventEntered': ['event_id','via'], 'GateBlocked': ['target_event_id','failing_conditions'],
    'OptionsProposed': ['options','source'], 'OptionChosen': ['option_id'],
    'CustomInstructionSubmitted': ['text'], 'ScopeDecision': ['layer','decision','reason'],
    'StepStarted': ['step_id','action_id','params','inputs','outputs','number'],
    'ScriptWritten': ['attempt','sha256','path'], 'StaticCheckFailed': ['attempt','violations'],
    'RunFinished': ['attempt','exit_status','duration','sandbox_level'],
    'StepCompleted': ['step_id','outputs','metrics','figures'],
    'StepFailed': ['step_id','attempts','last_error'],
    'FactRecorded': ['key','value','source','sha256','step_id'], 'FactRejected': ['candidate','reason'],
    'SubgoalChecked': ['subgoal_id','check_type','passed','detail'],
    'UserConfirmed': ['subgoal_id','note'], 'TestUnlocked': ['confirmation','split_sha256','reason'],
    'PackageRequested': ['package','reason'], 'PackageApproved': ['package'],
    'PackageDenied': ['package'], 'BranchCreated': ['name','from_record_id'],
    'BranchCheckedOut': ['name'], 'ScriptEditedByUser': ['step_id','old_sha256','new_sha256'],
    'Note': ['text'], 'BudgetStopped': ['reason'],
    'SplitFrozen': ['sha256','manifest','train','val','vault','parameters','train_index_sha256'],
    'EnvironmentRecorded': ['lock_sha256','packages'],
    'ObservationRecorded': ['step_id','note'], 'TestRead': ['step_id','split_sha256'],
    'TurnStarted': ['turn_id'], 'TurnEnded': ['turn_id'],
}
RecordType = Enum('RecordType', {name: name for name in PAYLOAD_FIELDS}, type=str)


class Payload(BaseModel):
    model_config = ConfigDict(extra='allow')


PAYLOAD_MODELS = {
    name: create_model(name + 'Payload', __base__=Payload, **{field: (Any, ...) for field in fields})
    for name, fields in PAYLOAD_FIELDS.items()
}


class Record(StrictModel):
    id: str = Field(default_factory=lambda: str(ULID()))
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: RecordType
    parent_id: str | None = None
    branch: str = 'main'
    session_id: str
    actor: Literal['engine','user','navigator','worker','inspector','illustrator'] = 'engine'
    event_id: str | None = None
    step_id: str | None = None
    payload: dict
    prev_hash: str = ''

    @model_validator(mode='after')
    def validate_payload(self):
        PAYLOAD_MODELS[self.type.value].model_validate(self.payload)
        return self


class ProjectState(StrictModel):
    project_id: str = ''
    template_id: str = ''
    template_version: str = ''
    current_event: str | None = None
    event_statuses: dict[str, str] = Field(default_factory=dict)
    subgoals: dict[str, dict] = Field(default_factory=dict)
    facts: dict[str, dict] = Field(default_factory=dict)
    steps: list[dict] = Field(default_factory=list)
    artefacts: dict[str, dict] = Field(default_factory=dict)
    data: dict[str, dict] = Field(default_factory=dict)
    inventory: list[dict] = Field(default_factory=list)
    brief: dict = Field(default_factory=dict)
    split: dict | None = None
    test_unlocked: bool = False
    pending_options: list[dict] | None = None
    confirmations: dict[str, dict] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)
    lock_sha256: str | None = None
    head: str | None = None
