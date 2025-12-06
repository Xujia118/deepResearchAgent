from bs4 import BeautifulSoup
from ddgs import DDGS
import requests


def register(tools):
    @tools.register_tool(
        name="search_web",
        description="Search the web for a query and return the top result URL.",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    )
    def search_web(query: str):
        print(f"Searching for: {query}")
        try:
            results = DDGS().text(query, max_results=3)
            # Format results as a string for the LLM
            formatted = "\n".join(
                [f"- {r['title']}: {r['href']}" for r in results])
            return formatted
        except Exception as e:
            return f"Search failed: {e}"

    @tools.register_tool(
        name="extract_text",
        description="Extract all text content from a given webpage URL.",
        parameters={
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    )
    def extract_text(url: str):
        print(f"Extracting text from: {url}")
        try:
            resp = requests.get(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup.get_text(separator="\n")
        except Exception as e:
            return f"Failed to extract: {e}"
