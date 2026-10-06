from .openai_compatible import CompatibleProvider


class OpenRouterProvider(CompatibleProvider):
    def __init__(self, config):
        config = config.model_copy(update={'base_url':config.base_url or 'https://openrouter.ai/api/v1'})
        super().__init__(config)
