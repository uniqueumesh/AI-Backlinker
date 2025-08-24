"""
Serper Search Provider Module - Handles Google search functionality via Serper API

This module contains all Serper-specific functions for search query generation,
API connectivity testing, and API key management. Separated from core scraping
to enable future extensibility with alternative search providers.
"""
import os
import httpx
from loguru import logger


def _get_serper_api_key():
    """Get SERPER_API_KEY dynamically from environment"""
    return os.getenv("SERPER_API_KEY")


def _serper_reachable(api_key: str) -> bool:
    """Best-effort check to avoid spamming errors when offline or DNS fails.
    Returns False quickly if https://google.serper.dev is not reachable.
    """
    try:
        # Lightweight GET to the root with short timeout. Some environments block HEAD.
        httpx.get(
            "https://google.serper.dev",
            timeout=3,
            headers={"X-API-KEY": api_key} if api_key else None,
        )
        return True
    except Exception as exc:
        logger.warning(f"Serper appears unreachable (network/DNS): {exc}. Skipping search.")
        return False


def _sanitize_keyword(keyword):
    """Sanitize keyword by removing common guest post footprints."""
    base = keyword or ""
    footprints = [
        "write for us", "guest post", "submit guest post", "guest contributor",
        "become a guest blogger", "editorial guidelines", "contribute", "submit article",
        "inurl:write-for-us", "intitle:write for us"
    ]
    low = base.lower()
    for f in footprints:
        low = low.replace(f, " ")
    # collapse spaces
    cleaned = " ".join(low.split())
    return cleaned


def generate_search_queries(keyword):
    keyword = _sanitize_keyword(keyword)
    """
    Generate a list of search queries for finding guest post opportunities.

    Args:
        keyword (str): The keyword to base the search queries on.

    Returns:
        list: A list of search queries.
    """
    return [
        f"{keyword} 'write for us'",
        f"{keyword} 'guest post'",
        f"{keyword} 'submit guest post'",
        f"{keyword} 'guest contributor'",
        f"{keyword} 'become a guest blogger'",
        f"{keyword} 'editorial guidelines'",
        f"{keyword} 'contribute'",
        f"{keyword} 'submit article'",
    ]
