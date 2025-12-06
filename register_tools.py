from markdownify import markdownify as md
from bs4 import BeautifulSoup
from ddgs import DDGS
import requests
import re
import CONSTANTS


def register(tools):
    @tools.register_tool(
        name=CONSTANTS.SEARCH_WEB,
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
        name=CONSTANTS.EXTRACT_TEXT,
        description="Extract all text content from a given webpage URL.",
        parameters={
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    )
    def extract_text(url: str):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")

        # 1. Remove the junk 
        for tag in soup(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()

        # 2. Convert to Markdown to keep links readable: [Link Text](url)
        markdown_text = md(str(soup), heading_style="ATX")

        # 3. Collapse whitespace
        clean_text = re.sub(r'\n{3,}', '\n\n', markdown_text).strip()

        return clean_text
