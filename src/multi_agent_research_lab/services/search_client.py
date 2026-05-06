"""Search client abstraction for ResearcherAgent."""

import json
import urllib.parse
import urllib.request

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""
    def __init__(self):
        self.settings = get_settings()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json&srlimit={max_results}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                results = []
                for item in data['query']['search']:
                    results.append(SourceDocument(
                        title=item['title'],
                        url=f"https://en.wikipedia.org/wiki/{urllib.parse.quote(item['title'].replace(' ', '_'))}",
                        snippet=item['snippet'].replace('<span class="searchmatch">', '').replace('</span>', ''),
                        metadata={"source": "wikipedia"}
                    ))
                return results
        except Exception:
            return [
                SourceDocument(
                    title=f"Mock Document for {query}",
                    url="https://example.com/mock",
                    snippet=f"This is a mock search result for the query: {query}. It contains some relevant information.",
                    metadata={"source": "mock"}
                )
            ]
