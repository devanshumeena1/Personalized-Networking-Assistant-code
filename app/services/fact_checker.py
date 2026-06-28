import urllib.parse
import logging
import wikipedia

logger = logging.getLogger(__name__)

def verify_fact_wikipedia(query: str) -> dict:
    """
    Queries the Wikipedia API using the wikipedia python library wrapper
    to find a summary and a reference URL for the given query.
    """
    try:
        # Set user agent as recommended by Wikipedia API rules
        wikipedia.set_user_agent("PNS-FactChecker/1.0 (contact@example.com)")
        
        search_results = wikipedia.search(query)
        if not search_results:
            logger.info(f"No Wikipedia pages found for query: {query}")
            return {
                "query": query,
                "verified": False,
                "summary": "Could not find any reliable matching page on Wikipedia.",
                "source_url": f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}"
            }
            
        page_title = search_results[0]
        try:
            # Get the page directly without auto suggest to avoid finding unrelated pages
            page = wikipedia.page(page_title, auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            # In case of disambiguation, try the first option
            if e.options:
                page = wikipedia.page(e.options[0], auto_suggest=False)
            else:
                raise e
        except wikipedia.PageError:
            # Fallback if page not found
            return {
                "query": query,
                "verified": False,
                "summary": "Could not find any reliable matching page on Wikipedia.",
                "source_url": f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}"
            }

        title = page.title
        summary = page.summary
        
        # Limit to 500 characters
        if len(summary) > 500:
            summary = summary[:500] + "..."
            
        return {
            "query": title,
            "verified": True,
            "summary": summary,
            "source_url": page.url
        }
    except Exception as e:
        logger.error(f"Error calling Wikipedia API via wrapper for query '{query}': {e}")
        return {
            "query": query,
            "verified": False,
            "summary": f"Network or service error while performing factcheck: {str(e)}",
            "source_url": f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}"
        }
