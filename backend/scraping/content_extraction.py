"""
Content Extraction Functions - extracted from core.py
"""
import re
import httpx
from loguru import logger
from typing import Optional, Tuple

# Lazy import to avoid dependency issues
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    BeautifulSoup = None


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


def _extract_main_content(html: str) -> str:
    """
    Extract main content from HTML using BeautifulSoup.
    Focuses on semantic HTML structure and removes navigation/footers.
    """
    if not html or not BEAUTIFULSOUP_AVAILABLE:
        return _strip_html_tags(html)  # Fallback to original method
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript", "iframe", "embed"]):
            script.decompose()
        
        # Priority content selectors (most to least important)
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.main-content',
            '#content',
            '#main',
            '.post',
            '.entry',
            'section',
            '.text-content'
        ]
        
        # Try to find main content using selectors
        main_content = None
        for selector in content_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # Find the element with the most text content
                    best_element = max(elements, key=lambda el: len(el.get_text(strip=True)))
                    if len(best_element.get_text(strip=True)) > 100:  # Minimum content threshold
                        main_content = best_element
                        break
            except Exception:
                continue
        
        # If no main content found, try body or fallback to original method
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body
            else:
                return _strip_html_tags(html)
        
        # Extract text and clean it
        text = main_content.get_text(separator=' ', strip=True)
        return _clean_content_text(text)
        
    except Exception as e:
        logger.warning(f"BeautifulSoup content extraction failed: {e}")
        return _strip_html_tags(html)  # Fallback to original method


def _clean_content_text(text: str) -> str:
    """
    Clean extracted text by removing code artifacts and formatting issues.
    """
    if not text:
        return ""
    
    # Remove JavaScript function definitions
    text = re.sub(r'function\s+\w*\s*\([^)]*\)\s*\{[^}]*\}', '', text)
    
    # Remove CSS style blocks
    text = re.sub(r'\{[^}]*:\s*[^}]*\}', '', text)
    
    # Remove variable declarations and data objects
    text = re.sub(r'var\s+\w+\s*=\s*[^;]+;', '', text)
    text = re.sub(r'const\s+\w+\s*=\s*[^;]+;', '', text)
    text = re.sub(r'let\s+\w+\s*=\s*[^;]+;', '', text)
    
    # Remove object literals
    text = re.sub(r'\{[^{}]*"[^"]*"[^{}]*\}', '', text)
    
    # Remove function calls
    text = re.sub(r'\w+\([^)]*\)', '', text)
    
    # Remove remaining code-like patterns
    text = re.sub(r'[a-zA-Z_]\w*\s*[=<>!]=?\s*[^;\n]+', '', text)
    
    # Clean up excessive whitespace and formatting
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-.,!?;:()]', '', text)
    
    return text.strip()


def _score_content_quality(text: str) -> float:
    """
    Score content quality from 0.0 (poor) to 1.0 (excellent).
    Higher scores indicate better, more readable content.
    """
    if not text:
        return 0.0
    
    score = 0.0
    
    # Length scoring (optimal range: 100-1500 characters)
    length = len(text)
    if 100 <= length <= 1500:
        score += 0.3
    elif 50 <= length < 100 or 1500 < length <= 3000:
        score += 0.2
    elif length > 3000:
        score += 0.1
    
    # Sentence structure scoring
    sentences = re.split(r'[.!?]+', text)
    if len(sentences) >= 3:
        score += 0.2
    
    # Word diversity scoring
    words = text.lower().split()
    unique_words = set(words)
    if len(words) > 0:
        diversity_ratio = len(unique_words) / len(words)
        if diversity_ratio > 0.7:
            score += 0.2
        elif diversity_ratio > 0.5:
            score += 0.1
    
    # Content vs. boilerplate scoring
    content_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    content_word_count = sum(1 for word in words if word.lower() not in content_words)
    if len(words) > 0:
        content_ratio = content_word_count / len(words)
        if content_ratio > 0.6:
            score += 0.3
        elif content_ratio > 0.4:
            score += 0.2
    
    return min(score, 1.0)


def _fallback_content_extraction(html: str) -> str:
    """
    Backup extraction method when main content extraction fails.
    Uses alternative strategies to ensure we always return some content.
    """
    if not html:
        return ""
    
    try:
        soup = BeautifulSoup(html, 'html.parser') if BEAUTIFULSOUP_AVAILABLE else None
        
        if soup:
            # Try to find any content divs
            content_divs = soup.find_all('div', class_=re.compile(r'content|post|article|text', re.I))
            if content_divs:
                # Get the div with the most text
                best_div = max(content_divs, key=lambda el: len(el.get_text(strip=True)))
                text = best_div.get_text(separator=' ', strip=True)
                if len(text) > 50:
                    return _clean_content_text(text)
            
            # Try paragraphs
            paragraphs = soup.find_all('p')
            if paragraphs:
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                if len(text) > 50:
                    return _clean_content_text(text)
        
        # Final fallback: use original method
        return _strip_html_tags(html)
        
    except Exception as e:
        logger.warning(f"Fallback content extraction failed: {e}")
        return _strip_html_tags(html)


def _strip_html_tags(html: str) -> str:
    """
    Enhanced HTML tag stripping with fallback to original method.
    Now uses intelligent content extraction when possible.
    """
    if not html:
        return ""
    
    # Try enhanced extraction first
    try:
        enhanced_content = _extract_main_content(html)
        quality_score = _score_content_quality(enhanced_content)
        
        # If quality is good enough, use enhanced content
        if quality_score >= 0.4:
            logger.debug(f"Using enhanced content extraction (quality: {quality_score:.2f})")
            return enhanced_content
        
        # If enhanced extraction quality is poor, try fallback
        fallback_content = _fallback_content_extraction(html)
        fallback_score = _score_content_quality(fallback_content)
        
        # Use the better of the two
        if fallback_score > quality_score:
            logger.debug(f"Using fallback content extraction (quality: {fallback_score:.2f})")
            return fallback_content
        else:
            logger.debug(f"Using enhanced content extraction (quality: {quality_score:.2f})")
            return enhanced_content
            
    except Exception as e:
        logger.warning(f"Enhanced content extraction failed, using original method: {e}")
        # Fallback to original method
        try:
            return re.sub(r"<[^>]+>", " ", html)
        except Exception:
            return html


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
