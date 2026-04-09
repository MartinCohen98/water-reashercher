from .openai_search_provider import OpenAISearchProvider


class GroqSearchProvider(OpenAISearchProvider):
    name = "groq"
    env_var = "GROQ_API_KEY"
    base_url = "https://api.groq.com/openai/v1"
    model = "openai/gpt-oss-20b"
