import re
from pathlib import Path
from mlca.log.schema import StrictModel
from typing import Literal


class ScopeDecision(StrictModel):
    decision: Literal['in_scope','other_event','reject']
    target_event: str | None = None
    reason: str


def layer_one(text: str,event,state,allowed_paths: list[Path]):
    if not text.strip() or len(text)>2000:
        return 'Instruction must contain 1–2000 characters'
    for pattern in event.custom_scope.deny_patterns:
        if re.search(pattern,text):
            return 'Instruction conflicts with the current event scope'
    if not state.test_unlocked and re.search(r'(?i)\btest[ _-](set|split|partition|parquet)\b|\.mlca/vault',text):
        return 'Test partition is locked'
    # Path-like references are never permission grants; compare their canonical targets.
    paths=re.findall(r'(?:~?/|\.{1,2}/)[\w./ -]+?(?=[\s,;"\']|$)',text)
    for token in paths:
        requested=Path(token.strip()).expanduser().resolve()
        if requested not in {p.resolve() for p in allowed_paths}:
            return 'Instruction names an undeclared path'
    return None
