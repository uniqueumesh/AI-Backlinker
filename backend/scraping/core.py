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





def _compose_notes(row: dict, keyword: str) -> str:
    """Compose notes based on the row data and keyword."""
    notes = []
    
    if row.get('contact_email'):
        notes.append(f"Contact email found: {row['contact_email']}")
    
    if row.get('guidelines_url'):
        notes.append(f"Guidelines available at: {row['guidelines_url']}")
    
    if row.get('contact_form_url'):
        notes.append(f"Contact form available at: {row['contact_form_url']}")
    
    if row.get('page_excerpt'):
        excerpt = row['page_excerpt'][:100] + "..." if len(row['page_excerpt']) > 100 else row['page_excerpt']
        notes.append(f"Page excerpt: {excerpt}")
    
    return "; ".join(notes) if notes else "No additional notes"


def find_backlink_opportunities(
    keyword,
    serper_api_key: str | None = None,
    firecrawl_api_key: str | None = None,
    max_results: int = 10,
):
    """
    Find backlink opportunities by scraping websites based on search queries.

    Args:
        keyword (str): The keyword to search for backlink opportunities.

    Returns:
        list: A list of results from the scraped websites.
    """
    search_queries = generate_search_queries(keyword)
    results: list[dict] = []
    unique: dict[str, dict] = {}

    serper_key = serper_api_key or _get_serper_api_key()
    firecrawl_key = firecrawl_api_key or _get_firecrawl_api_key()

    if serper_key and _serper_reachable(serper_key):
        headers = {"X-API-KEY": serper_key, "Content-Type": "application/json"}
        unique = {}
        for q in search_queries:
            if len(unique) >= max_results:
                break
            try:
                resp = httpx.post(
                    "https://google.serper.dev/search",
                    headers=headers,
                    json={"q": q, "num": 10},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                for item in (data.get("organic") or []):
                    if len(unique) >= max_results:
                        break
                    url = item.get("link")
                    title = item.get("title")
                    if not url:
                        continue
                    page = scrape_website(url, firecrawl_key)
                    md_text, html_text = _collect_page_text(page)
                    context_source = "firecrawl"
                    # best-effort excerpt for LLM insights
                    raw_text = (md_text or "").strip()
                    if not raw_text and html_text:
                        raw_text = _strip_html_tags(html_text)
                    excerpt = _collapse_whitespace(raw_text)[:1500]
                    # If Firecrawl yielded nothing, try HTTP fallback
                    if not excerpt:
                        context_source = "httpx"
                        http_text, http_html = _http_fetch_text(url)
                        if http_text:
                            excerpt = http_text[:1500]
                            html_text = http_html or html_text
                        else:
                            # Last resort: use Serper organic snippet
                            snippet = item.get("snippet") or item.get("description") or ""
                            if snippet:
                                context_source = "serper_snippet"
                                excerpt = _collapse_whitespace(snippet)[:600]
                            else:
                                context_source = "empty"
                    # emails
                    emails = _extract_emails((md_text + "\n" + html_text))
                    domain = urlparse(url).netloc
                    best_email = _choose_best_email(emails, domain)
                    # support links
                    links = _extract_links(html_text, url)
                    g_url, c_url = _classify_support_links(links)
                    if not g_url and title and "write" in title.lower():
                        g_url = url
                    row = {
                        "url": url,
                        "title": title or "",
                        "contact_email": best_email,
                        "contact_emails_all": ", ".join(emails[:5]) if emails else "",
                        "contact_form_url": c_url,
                        "guidelines_url": g_url,
                        "domain": domain or url,
                        "notes": "",
                        "page_excerpt": excerpt,
                        "context_source": context_source,
                    }
                    row["notes"] = _compose_notes(row, keyword)
                    unique[url] = row
            except Exception as exc:
                logger.warning(f"Serper fetch failed for '{q}': {exc}")

    # Finalize (deduped + capped)
    if serper_key:
        return list(unique.values()) if unique else results
    return results


def search_for_urls(query):
    """
    Search for URLs using Google search.
    
    Args:
        query (str): The search query.
        
    Returns:
        list: List of URLs found.
    """
    # Temporarily disabled Google search functionality
    # return list(search(query, num_results=10))
    return []
