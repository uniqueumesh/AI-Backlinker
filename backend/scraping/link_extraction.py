"""
Link Extraction Functions - extracted from core.py
"""
from urllib.parse import urljoin
import re


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
