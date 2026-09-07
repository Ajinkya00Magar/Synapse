"""
Web-related action handlers.
Supports opening URLs and querying search engines in the default web browser.
"""

import urllib.parse
import webbrowser


def open_browser_url(url: str) -> str:
    """
    Opens a specific URL in the user's default web browser.
    
    Args:
        url: The web address to open (e.g. 'https://github.com')
    Returns:
        Confirmation message.
    """
    target = url.strip()
    if not (target.startswith("http://") or target.startswith("https://")):
        target = f"https://{target}"

    webbrowser.open(target)
    return f"Opened URL in browser: {target}"


def search_web_engine(query: str, engine: str = "google") -> str:
    """
    Performs a web search using the specified search engine.
    
    Args:
        query: The search keywords or question.
        engine: 'google' or 'youtube'
    Returns:
        Confirmation message.
    """
    clean_query = query.strip()
    encoded = urllib.parse.quote_plus(clean_query)

    if engine.lower() == "youtube":
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
    else:
        search_url = f"https://www.google.com/search?q={encoded}"

    webbrowser.open(search_url)
    return f"Searched {engine.capitalize()} for: '{clean_query}'"
