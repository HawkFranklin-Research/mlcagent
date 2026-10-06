from pathlib import Path
import json
from mlca.llm.client import RequestContext


def prompt(name: str, **values) -> str:
    text = (Path(__file__).parent/'prompts'/name).read_text()
    # Replace declared placeholders only; JSON braces in inserted content are left untouched.
    for key,value in values.items():
        text = text.replace('{'+key+'}',value if isinstance(value,str) else json.dumps(value,default=str))
    return text


class Role:
    name = ''
    def __init__(self,session):
        self.session = session

    def context(self,purpose,action_id=None,step_id=None):
        return RequestContext(role=self.name,session_id=self.session.session_id,turn_id=self.session.turn_id,
                              event_id=self.session.state.current_event,action_id=action_id,
                              step_id=step_id,purpose=purpose)
