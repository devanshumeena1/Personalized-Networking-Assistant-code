import urllib.parse
import requests
import logging

logger = logging.getLogger(__name__)

def verify_fact_wikipedia(query: str) -> dict:
    """
    Queries the Wikipedia API to find a summary and a reference URL for the given query.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 1,
        "prop": "extracts|info",
        "inprop": "url",
        "exintro": True,
        "explaintext": True,
        "exchars": 500
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        if not pages or "-1" in pages:
            logger.info(f"No Wikipedia pages found for query: {query}")
            return {
                "query": query,
                "verified": False,
                "summary": "Could not find any reliable matching page on Wikipedia.",
                "source_url": f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}"
            }

        page_id = list(pages.keys())[0]
        page_data = pages[page_id]
        
        title = page_data.get("title", "")
        summary = page_data.get("extract", "").strip()
        source_url = page_data.get("fullurl", f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}")

        if not summary:
            summary = f"Page found: {title}, but no summary text was available."

        return {
            "query": title,
            "verified": True,
            "summary": summary,
            "source_url": source_url
        }
    except Exception as e:
        logger.error(f"Error calling Wikipedia API for query '{query}': {e}")
        return {
            "query": query,
            "verified": False,
            "summary": f"Network or service error while performing factcheck: {str(e)}",
            "source_url": f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}"
        }
