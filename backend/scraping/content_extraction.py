"""
Content Extraction Functions - extracted from core.py
"""
import re
import httpx
from loguru import logger


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
