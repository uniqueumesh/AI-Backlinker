"""
Core Scraping Functions - extracted from ai_backlinking_scraper.py
"""
import os
import re
import httpx
from urllib.parse import urljoin, urlparse
from loguru import logger

# Remove static environment variable loading - will read dynamically
# SERPER_API_KEY = os.getenv("SERPER_API_KEY")
# FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

def _get_serper_api_key():
    """Get SERPER_API_KEY dynamically from environment"""
    return os.getenv("SERPER_API_KEY")

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


def _collect_page_text(page: object | None) -> tuple[str, str]:
    """Return (markdown_text, html_text) from Firecrawl payload (dict/object) or raw string."""
    if page is None:
        return "", ""
    if isinstance(page, str):
        # best effort: assume raw text/markdown
        return page, ""
    md_text = ""
    html_text = ""
    # dict-like
    if isinstance(page, dict):
        for k in ("markdown", "md", "content", "text"):
            v = page.get(k)
            if isinstance(v, str):
                md_text += "\n" + v
        v_html = page.get("html")
        if isinstance(v_html, str):
            html_text = v_html
        return md_text, html_text
    # object-like (e.g., Firecrawl ScrapeResponse)
    for k in ("markdown", "md", "content", "text"):
        v = getattr(page, k, None)
        if isinstance(v, str):
            md_text += "\n" + v
    v_html = getattr(page, "html", None)
    if isinstance(v_html, str):
        html_text = v_html
    return md_text, html_text


def _strip_html_tags(html: str) -> str:
    try:
        return re.sub(r"<[^>]+>", " ", html or "")
    except Exception:
        return html or ""


def _collapse_whitespace(text: str) -> str:
    return " ".join((text or "").split())


def _http_fetch_text(url: str, timeout_s: int = 15) -> tuple[str, str]:
    """Fetch raw HTML via httpx and return (text, html). Safe, best-effort."""
    try:
        resp = httpx.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml",
            },
            follow_redirects=True,
            timeout=timeout_s,
        )
        if resp.status_code >= 400:
            return "", ""
        html = resp.text or ""
        text = _strip_html_tags(html)
        return _collapse_whitespace(text), html
    except Exception as exc:
        logger.warning(f"HTTP fallback fetch failed for {url}: {exc}")
        return "", ""


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _extract_emails(text: str) -> list[str]:
    emails = set(e.lower() for e in _EMAIL_RE.findall(text or ""))
    # filter obvious placeholders
    filtered = [e for e in emails if not any(bad in e for bad in ("example.com", "no-reply", "noreply"))]
    return filtered


def _choose_best_email(emails: list[str], domain: str) -> str:
    """Choose the best email from a list, preferring domain-matching ones."""
    if not emails:
        return ""
    # Prefer emails matching the domain
    domain_emails = [e for e in emails if domain in e]
    if domain_emails:
        return domain_emails[0]
    # Fall back to first email
    return emails[0]


def _extract_links(html: str, base_url: str) -> list[str]:
    """Extract all links from HTML."""
    if not html:
        return []
    links = []
    # Simple regex-based link extraction
    link_pattern = r'href=["\']([^"\']+)["\']'
    for match in re.finditer(link_pattern, html):
        link = match.group(1)
        if link.startswith(('http://', 'https://')):
            links.append(link)
        elif link.startswith('/'):
            links.append(urljoin(base_url, link))
    return links


def _classify_support_links(links: list[str]) -> tuple[str, str]:
    """Classify links as guidelines or contact forms."""
    guidelines_url = ""
    contact_url = ""
    
    for link in links:
        lower_link = link.lower()
        if any(term in lower_link for term in ['write-for-us', 'guest-post', 'contribute', 'guidelines', 'submit']):
            if not guidelines_url:
                guidelines_url = link
        elif any(term in lower_link for term in ['contact', 'about', 'write-to-us']):
            if not contact_url:
                contact_url = link
    
    return guidelines_url, contact_url


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
