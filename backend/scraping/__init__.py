"""
Scraping Module Package - web scraping functions
"""
from .core import (
    find_backlink_opportunities, 
    generate_search_queries, 
    search_for_urls, 
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

__all__ = [
    'find_backlink_opportunities',
    'generate_search_queries',
    'search_for_urls',
    'scrape_website',
    '_collect_page_text',
    '_strip_html_tags',
    '_collapse_whitespace',
    '_http_fetch_text',
    '_extract_emails',
    '_extract_links',
    '_choose_best_email',
    '_classify_support_links'
]
