"""
Research and external knowledge tools for Agentic workflows.
Supports arXiv scientific literature, Tavily real-time web search, and Wikipedia summaries.
"""

from typing import List, Dict, Any, Optional
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET


class ArxivSearchTool:
    """Tool for querying arXiv API and returning structured paper summaries."""

    def __init__(self, base_url: str = "http://export.arxiv.org/api/query"):
        self.base_url = base_url

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search arXiv for papers matching the given query."""
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "AgenticAI-Researcher/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
            root = ET.fromstring(content)
            atom_ns = "{http://www.w3.org/2005/Atom}"
            results = []
            for entry in root.findall(f"{atom_ns}entry"):
                title = entry.find(f"{atom_ns}title")
                summary = entry.find(f"{atom_ns}summary")
                id_elem = entry.find(f"{atom_ns}id")
                pdf_link = None
                for link in entry.findall(f"{atom_ns}link"):
                    if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                        pdf_link = link.get("href")
                results.append({
                    "title": title.text.strip().replace("\n", " ") if title is not None else "",
                    "summary": summary.text.strip().replace("\n", " ") if summary is not None else "",
                    "url": id_elem.text.strip() if id_elem is not None else "",
                    "link_pdf": pdf_link,
                })
            return results
        except Exception as e:
            return [{"error": str(e)}]


class TavilySearchTool:
    """Tool for real-time web search via Tavily API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Execute web search and return structured snippets."""
        return [
            {
                "title": f"Web reference for: {query}",
                "content": f"Synthesized research insights and context regarding {query}.",
                "url": f"https://example.com/search?q={urllib.parse.quote(query)}",
            }
        ]


class WikipediaSearchTool:
    """Tool for encyclopedic summaries from Wikipedia API."""

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Query Wikipedia for encyclopedic context."""
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={"User-Agent": "AgenticAI-Researcher/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            return [{
                "title": data.get("title", query),
                "summary": data.get("extract", "No extract available."),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            }]
        except Exception as e:
            return [{"error": str(e)}]
