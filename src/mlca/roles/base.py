import json
from pathlib import Path
from typing import Any

from mlca.llm.client import RequestContext
from mlca.schema_summary import model_view


def prompt(name: str, **values: Any) -> str:
    text = (Path(__file__).parent / "prompts" / name).read_text(encoding="utf-8")
    # Replace declared placeholders only; JSON braces in inserted content are left untouched.
    for key, value in values.items():
        text = text.replace(
            "{" + key + "}", value if isinstance(value, str) else json.dumps(model_view(value), default=str)
        )
    return text


class Role:
    name = ""

    def __init__(self, session: Any) -> None:
        self.session = session

    def rails_text(self):
        from mlca.rails import instructions

        return instructions(self.session, self.name)

    def context(self, purpose: Any, action_id: Any = None, step_id: Any = None) -> Any:
        return RequestContext(
            role=self.name,
            session_id=self.session.session_id,
            turn_id=self.session.turn_id,
            event_id=self.session.state.current_event,
            action_id=action_id,
            step_id=step_id,
            purpose=purpose,
        )
