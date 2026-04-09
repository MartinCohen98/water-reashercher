import os
from typing import List

from openai import OpenAI
from .base import SearchProvider, SearchResult, TestResult, PROMPT_COMMON_DIRECTIONS
from .response_verifier import verify_model_response


class GroqSearchProvider(SearchProvider):
    name = "groq"
    env_var = "GROQ_API_KEY"
    base_url = "https://api.groq.com/openai/v1"
    model = "openai/gpt-oss-20b"

    def __init__(self, num_results: int = 1, model: str | None = None):
        self.num_results = num_results
        self.model = model or self.model
        self._client = None

    def is_available(self) -> bool:
        return bool(os.environ.get(self.env_var))

    def _get_client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=os.environ.get(self.env_var),
                base_url=self.base_url,
            )
        return self._client

    def _extract_output_text(self, response) -> str:
        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text

        output = getattr(response, "output", None)
        if not output:
            return str(response)

        if isinstance(output, str):
            return output

        if isinstance(output, list):
            fragments = []
            for item in output:
                if isinstance(item, dict):
                    fragments.append(item.get("content", str(item)))
                else:
                    fragments.append(str(item))
            return "\n".join(filter(None, fragments))

        if isinstance(output, dict):
            return output.get("content", str(output))

        return str(output)

    def search(self, query: str, test=False) -> List[SearchResult]:
        search_query = query
        if not test:
            search_query = query + PROMPT_COMMON_DIRECTIONS
        results: List[SearchResult] = []
        if not self.is_available():
            return results

        try:
            client = self._get_client()
            response = client.responses.create(
                input=search_query,
                model=self.model,
            )
            output_text = self._extract_output_text(response)
            parsed_response = None
            if not test:
                verification = verify_model_response(output_text)
                if verification.valid:
                    parsed_response = verification.parsed
            results.append(SearchResult(
                title=query,
                url="",
                snippet=output_text,
                source=self.name,
                parsed_response=parsed_response,
            ))
        except Exception as e:
            print(f"Groq search error: {e}")

        return results

    def test(self) -> TestResult:
        if not self.is_available():
            return TestResult(query="", response="", working=False)
        query = "What is 2+2? Answer only with a number"
        try:
            results = self.search(query, test=True)
            response = results[0].snippet if results else ""
            return TestResult(query=query, response=response, working=len(results) > 0)
        except:
            return TestResult(query=query, response="", working=False)
