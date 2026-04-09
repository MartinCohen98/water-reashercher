from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    parsed_response: dict = None


@dataclass
class TestResult:
    query: str
    response: str
    working: bool


PROMPT_COMMON_DIRECTIONS = """
Give response as ONLY a json with no additional text in the following format:
{
    "Data": "answer in 10 words or less",
    "Sources": [
        "Source": "url",
        "Excerpt": "Excerpt of the source witch confirms the data",
        "Relevance": "How relevant is the source to confirme the data out of 10"
    ]
}
The data should give what the prompt is asking for in 10 words or less. The answer should have at least two sources. Make sure the sources are relevan to the question.
"""


class SearchProvider(ABC):
    name: str

    @abstractmethod
    def search(self, query: str) -> List[SearchResult]:
        pass

    def is_available(self) -> bool:
        return True

    def test(self) -> TestResult:
        if not self.is_available():
            return TestResult(query="", response="", working=False)
        query = "test"
        try:
            results = self.search(query)
            response = results[0].snippet if results else ""
            return TestResult(query=query, response=response, working=len(results) > 0)
        except:
            return TestResult(query=query, response="", working=False)
