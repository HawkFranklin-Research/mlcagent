"""Direct DeepSeek API transport; credentials and accounting use the shared adapter."""

from .openai_compatible import CompatibleProvider


class DeepSeekProvider(CompatibleProvider):
    pass
