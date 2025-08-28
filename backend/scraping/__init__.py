"""
Scraping Module Package - web scraping functions
"""
from .core import (
    find_backlink_opportunities,
)
from .serper import generate_search_queries
from .firecrawl import scrape_website


from .content_extraction import (
    _collect_page_text,
    _strip_html_tags,
    _collapse_whitespace,
    _http_fetch_text,
)

from .email_extraction import (
    _extract_emails,
    _choose_best_email,
)

from .link_extraction import (
    _extract_links,
    _classify_support_links
)

__all__ = [
    'find_backlink_opportunities',
    'generate_search_queries',
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
