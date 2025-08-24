"""
Build research row from URL - extracts website data and contact information
"""
from scraping import scrape_website, _collect_page_text, _strip_html_tags, _collapse_whitespace, _extract_emails, _http_fetch_text, _choose_best_email, _extract_links, _classify_support_links
from urllib.parse import urlparse

def _build_row_from_url(url: str, firecrawl_key: str | None) -> dict:
    """
    Build a research row by scraping a URL and extracting relevant information.
    
    Args:
        url: The URL to scrape
        firecrawl_key: Optional Firecrawl API key
        
    Returns:
        dict: Research row with extracted data
    """
    page = scrape_website(url, firecrawl_key)
    md_text, html_text = _collect_page_text(page)
    raw_text = (md_text or "").strip()
    context_source = "firecrawl" if raw_text or html_text else "httpx"
    if not raw_text and html_text:
        raw_text = _strip_html_tags(html_text)
    if not raw_text:
        # HTTP fallback similar to CLI behavior
        text_http, html_http = _http_fetch_text(url)
        raw_text = text_http
        if html_http:
            html_text = html_http
    excerpt = _collapse_whitespace(raw_text)[:1500]
    emails = _extract_emails((md_text + "\n" + html_text))
    domain = urlparse(url).netloc
    best_email = _choose_best_email(emails, domain)
    links = _extract_links(html_text, url)
    g_url, c_url = _classify_support_links(links)
    return {
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
