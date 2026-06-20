import os
import requests
from dotenv import load_dotenv

from langchain.tools import tool
from tavily import TavilyClient

from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re


load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """
    Search the web for recent and reliable information on a topic. Returns Titles and URLs of the top results.
    """
    results = tavily.search(query=query, max_results=5)

    out = []

    for r in  results['results']:
        out.append(
            f"Title: {r['title']} \nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)

@tool
def scrape_url(url: str, max_chars: int = 8000) -> str:
    """
    Fetch a web page and extract its main readable text content as plain text.

    Use this tool AFTER `web_search` when you have a specific URL and need the
    full article/page body (not just the snippet). Good for reading articles,
    documentation, blog posts, or news pages. It strips navigation, ads, scripts
    and boilerplate, returning only the core content.

    It does NOT execute JavaScript, so heavily client-rendered pages (SPAs) or
    pages behind logins/paywalls may return little or no text. It cannot read
    PDFs, images, or other non-HTML files.

    Args:
        url: The full URL to scrape. If the scheme is missing, "https://" is
            assumed.
        max_chars: Maximum number of characters to return. Long pages are
            truncated to keep the response within the context budget
            (default 8000).

    Returns:
        The cleaned page text, or a message starting with "ERROR:" / "NOTE:"
        describing why no usable content was returned (e.g. unreachable URL,
        non-HTML content, or an empty/JS-rendered page).
    """

    def _clean(text: str) -> str:
        # Collapse runs of blank lines and trim trailing whitespace per line.
        lines = [ln.strip() for ln in text.splitlines()]
        text = "\n".join(ln for ln in lines if ln)
        return re.sub(r"\n{3,}", "\n\n", text).strip()

    def _finalize(text: str) -> str:
        text = _clean(text)
        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "\n\n[...truncated...]"
        return text

    url = url.strip()
    if not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = "https://" + url

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return f"ERROR: timed out while fetching {url}"
    except requests.exceptions.RequestException as e:
        return f"ERROR: could not fetch {url}: {e}"

    content_type = response.headers.get("Content-Type", "").lower()
    if content_type and "html" not in content_type and "text" not in content_type:
        return (
            f"ERROR: {url} returned non-HTML content "
            f"({content_type.split(';')[0] or 'unknown'}); cannot extract text."
        )

    html = response.text

    # Strategy 1: trafilatura (best at isolating main article content).
    try:
        content = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )
        if content and len(content.strip()) > 200:
            return _finalize(content)
    except Exception:
        pass

    # Strategy 2: readability (Document) for article-style pages.
    try:
        article_html = Document(html).summary()
        text = BeautifulSoup(article_html, "lxml").get_text("\n", strip=True)
        if text and len(text) > 200:
            return _finalize(text)
    except Exception:
        pass

    # Strategy 3: raw soup fallback — strip boilerplate tags, keep all text.
    try:
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "noscript", "aside"]
        ):
            tag.decompose()
        text = _finalize(soup.get_text("\n", strip=True))
        if text:
            return text
    except Exception:
        pass

    return (
        f"NOTE: no readable text could be extracted from {url}. "
        "The page may be empty, require JavaScript, or be behind a login/paywall."
    )
