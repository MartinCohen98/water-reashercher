from .openai_search_provider import OpenAISearchProvider


class GptSearchProvider(OpenAISearchProvider):
    name = "gpt"
    env_var = "OPENROUTER_API_KEY"
    base_url = "https://openrouter.ai/api/v1"
    model = "openai/gpt-oss-120b:free"