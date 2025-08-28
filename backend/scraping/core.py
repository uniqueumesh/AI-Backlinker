"""
Core Scraping Functions - extracted from ai_backlinking_scraper.py
"""
import os
import re
import httpx
from urllib.parse import urljoin, urlparse
from loguru import logger

# Import moved functions from new modules
from .content_extraction import _collect_page_text, _strip_html_tags, _collapse_whitespace, _http_fetch_text
from .email_extraction import _extract_emails, _choose_best_email
from .link_extraction import _extract_links, _classify_support_links
from .serper import _get_serper_api_key, _serper_reachable, generate_search_queries, _sanitize_keyword
from .firecrawl import _get_firecrawl_api_key, scrape_website, scrape_url
from .data_processing import _compose_notes
from .research_orchestrator import find_backlink_opportunities






