"""
Firecrawl Scraping Provider Module - Handles website content extraction via Firecrawl API

This module contains all Firecrawl-specific functions for website scraping,
API key management, and content extraction. Separated from core scraping
to enable future extensibility with alternative scraping providers.
"""
import os
from loguru import logger


def _get_firecrawl_api_key():
    """Get FIRECRAWL_API_KEY dynamically from environment"""
    return os.getenv("FIRECRAWL_API_KEY")


def scrape_website(url: str, firecrawl_api_key: str | None = None):
    """Scrape a URL via Firecrawl if configured; otherwise return empty dict."""
    key = firecrawl_api_key or _get_firecrawl_api_key()
    if not key:
        return {}
    try:
        # Firecrawl Python SDK import at runtime to avoid hard dep if absent
        from firecrawl import FirecrawlApp
        app = FirecrawlApp(api_key=key)
        data = app.scrape_url(url, formats=["markdown", "html"])  # type: ignore
        return data or {}
    except Exception as exc:
        logger.warning(f"Firecrawl scrape failed for {url}: {exc}")
        return {}


def scrape_url(url: str, firecrawl_api_key: str | None = None):
    return scrape_website(url, firecrawl_api_key)
