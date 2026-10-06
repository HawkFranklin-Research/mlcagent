from mlca.log.schema import StrictModel
from mlca.llm.structured import complete
from mlca.engine.options import OptionsResponse,validate
from mlca.engine.scope_guard import ScopeDecision
from mlca.engine.state_view import build
from .base import Role,prompt


class FactsResponse(StrictModel):
    facts: list[dict]


class RecapResponse(StrictModel):
    text: str


class Navigator(Role):
    name='navigator'

    def propose_options(self):
        state=self.session.state
        messages=[{'role':'user','content':prompt('navigator_options.md',state=build(state,self.session.workflow),
                                                schema=OptionsResponse.model_json_schema())}]
        context=self.context('options')
        for attempt in range(2):
            response=self.session.client.complete(self.name,messages,schema=OptionsResponse,
                                                   context=context,categories=['template_spec','facts','inventory_summary','user_text'])
            try:
                from mlca.llm.structured import decode
                parsed=OptionsResponse.model_validate(decode(response.text))
                options=validate(parsed.options,state,self.session.workflow)
                return options,response.request_id
            except (ValueError,TypeError) as exc:
                if attempt==0:
                    messages.extend([{'role':'assistant','content':response.text},
                                     {'role':'user','content':'Repair the options: '+str(exc)[:1200]}])
                else:
                    raise
            except Exception as exc:
                from mlca.errors import MlcaUserError
                if not isinstance(exc,MlcaUserError):
                    raise
                if attempt==0:
                    messages.extend([{'role':'assistant','content':response.text},
                                     {'role':'user','content':'Repair the options: '+str(exc)[:1200]}])
                else:
                    raise

    def classify_scope(self,text):
        response=complete(self.session.client,self.name,[{'role':'user','content':prompt('navigator_scope.md',
                          instruction=text,event=self.session.workflow.events[self.session.state.current_event].model_dump(),
                          schema=ScopeDecision.model_json_schema())}],ScopeDecision,self.context('scope'),['template_spec','user_text'])
        return response.parsed

    def extract_facts(self,observation,action,step_id):
        if not action.fact_candidates:
            return []
        response=complete(self.session.client,self.name,[{'role':'user','content':prompt('navigator_facts.md',
                          observation=observation,allowed=action.fact_candidates,step_id=step_id,
                          schema=FactsResponse.model_json_schema())}],FactsResponse,self.context('facts',action.id,step_id),['facts'])
        return response.parsed.facts

    def summarise_session(self,records):
        response=complete(self.session.client,self.name,[{'role':'user','content':prompt('navigator_recap.md',
                          records=[r.model_dump(mode='json') for r in records[-12:]],schema=RecapResponse.model_json_schema())}],
                          RecapResponse,self.context('recap'),['facts','user_text'])
        return response.parsed.text
