from .openai_search_provider import OpenAISearchProvider


class GemmaSearchProvider(OpenAISearchProvider):
    name = "google-openrouter"
    env_var = "OPENROUTER_API_KEY"
    base_url = "https://openrouter.ai/api/v1"
    model = "google/gemma-4-31b-it:free"
