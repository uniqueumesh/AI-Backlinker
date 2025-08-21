"""
Core Utility Functions - extracted from ai_backlinking_utils.py
"""
import sys
from loguru import logger
from urllib.parse import urlparse

# Import from the modularized scraping package
from scraping import (
    scrape_website, 
    _collect_page_text, 
    _strip_html_tags, 
    _collapse_whitespace, 
    _http_fetch_text, 
    _extract_emails, 
    _extract_links, 
    _choose_best_email, 
    _classify_support_links
)


def find_backlink_opportunities_for_keywords(keywords):
    """
    Find backlink opportunities for multiple keywords.

    Args:
        keywords (list): A list of keywords to search for backlink opportunities.

    Returns:
        dict: A dictionary with keywords as keys and a list of results as values.
    """
    from scraping import find_backlink_opportunities
    
    all_results = {}
    for keyword in keywords:
        results = find_backlink_opportunities(keyword)
        all_results[keyword] = results
    return all_results


def build_row_from_url(url: str, firecrawl_key: str | None = None) -> dict:
    """Build a data row from a single URL for CLI testing."""
    page = scrape_website(url, firecrawl_key)
    md_text, html_text = _collect_page_text(page)
    # Excerpt
    raw_text = (md_text or "").strip()
    context_source = "firecrawl" if raw_text or html_text else "httpx"
    if not raw_text and html_text:
        raw_text = _strip_html_tags(html_text)
    if not raw_text:
        text_http, html_http = _http_fetch_text(url)
        raw_text = text_http
        html_text = html_http or html_text
    excerpt = _collapse_whitespace(raw_text)[:1500]
    # Emails / links
    emails = _extract_emails((md_text + "\n" + html_text))
    domain = urlparse(url).netloc
    best_email = _choose_best_email(emails, domain)
    links = _extract_links(html_text, url)
    g_url, c_url = _classify_support_links(links)
    row = {
        "url": url,
        "title": "",
        "contact_email": best_email,
        "contact_emails_all": ", ".join(emails[:5]) if emails else "",
        "contact_form_url": c_url,
        "guidelines_url": g_url,
        "domain": domain or url,
        "notes": "",
        "page_excerpt": excerpt,
        "context_source": context_source,
    }
    return row


# Configure logger
def setup_logger():
    """Configure the logger for the application."""
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}"
    )
