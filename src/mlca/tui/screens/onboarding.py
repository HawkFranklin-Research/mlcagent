from mlca.ui_text import text
from .brief import FormScreen


class OnboardingScreen(FormScreen):
    def __init__(self,config):
        provider=next(iter(config.providers.values()),None)
        navigator=config.roles.get('navigator')
        worker=config.roles.get('worker')
        super().__init__(text('configure'),[
            ('kind',text('provider'),provider.kind if provider else 'openai_api'),
            ('api_env',text('key_env'),provider.api_key_env or '' if provider else 'OPENAI_API_KEY'),
            ('base_url',text('base_url'),provider.base_url or '' if provider else ''),
            ('navigator_model',text('navigator_model'),navigator.model if navigator else ''),
            ('worker_model',text('worker_model'),worker.model if worker else ''),
            ('request_bound',text('budget_bound'),str(provider.request_cost_bound_usd or '') if provider else ''),
            ('allow_b',text('allow_b'),'yes' if config.sandbox.allow_level_b else 'no')])
