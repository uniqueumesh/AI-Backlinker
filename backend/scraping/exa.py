"""
Exa Search Provider Module - Handles semantic search functionality via Exa API

This module contains all Exa-specific functions for search query generation,
API connectivity testing, and API key management. Separated from core scraping
to enable future extensibility with alternative search providers.
"""
import os
import time
import httpx
from loguru import logger

# Rate limiting configuration
RATE_LIMIT_DELAY = 0.1  # 100ms between requests
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # Start with 1 second delay


def _get_exa_api_key():
    """Get EXA_API_KEY dynamically from environment"""
    return os.getenv("EXA_API_KEY")


def _exa_reachable(api_key: str) -> bool:
    """Best-effort check to avoid spamming errors when offline or DNS fails.
    Returns False quickly if Exa API is not reachable.
    """
    try:
        # Test the actual working search endpoint instead of root domain
        response = httpx.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json={"query": "test", "text": True},
            timeout=5,
        )
        # If we get any response (even error), the API is reachable
        return True
    except Exception as exc:
        logger.warning(f"Exa appears unreachable (network/DNS): {exc}. Skipping search.")
        return False


def _make_exa_request_with_retry(url, headers, json_data, max_retries=MAX_RETRIES):
    """
    Make Exa API request with exponential backoff retry logic.
    
    Args:
        url (str): API endpoint URL
        headers (dict): Request headers
        json_data (dict): Request payload
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        httpx.Response: API response or None if all retries failed
    """
    for attempt in range(max_retries + 1):
        try:
            response = httpx.post(url, headers=headers, json=json_data, timeout=30)
            
            # Check for rate limiting (429 status)
            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Rate limit exceeded, max retries reached")
                    return None
            
            # Check for other HTTP errors
            if response.status_code >= 400:
                logger.warning(f"HTTP {response.status_code} error: {response.text}")
                if attempt < max_retries:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"HTTP error after {max_retries} retries")
                    return None
            
            return response
            
        except httpx.TimeoutException:
            if attempt < max_retries:
                wait_time = RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                continue
            else:
                logger.error("Timeout after all retries")
                return None
                
        except Exception as exc:
            if attempt < max_retries:
                wait_time = RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Request failed: {exc}, retrying in {wait_time}s (attempt {attempt + 1})")
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Request failed after {max_retries} retries: {exc}")
                return None
    
    return None


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


def generate_exa_search_queries(keyword):
    keyword = _sanitize_keyword(keyword)
    """
    Generate optimized search queries for finding guest post opportunities.
    
    Enhanced with industry targeting, content type focus, and contact discovery.

    Args:
        keyword (str): The keyword to base the search queries on.

    Returns:
        list: A list of optimized search queries.
    """
    # Base guest post queries
    base_queries = [
        f"{keyword} 'write for us'",
        f"{keyword} 'guest post'",
        f"{keyword} 'submit guest post'",
        f"{keyword} 'guest contributor'",
        f"{keyword} 'become a guest blogger'",
        f"{keyword} 'editorial guidelines'",
        f"{keyword} 'contribute'",
        f"{keyword} 'submit article'",
    ]
    
    # Industry and content type targeting
    industry_queries = [
        f"{keyword} 'blog' 'write for us'",
        f"{keyword} 'magazine' 'guest post'",
        f"{keyword} 'publication' 'submit article'",
        f"{keyword} 'content marketing' 'guest contributor'",
        f"{keyword} 'industry blog' 'write for us'",
    ]
    
    # Contact and submission discovery
    contact_queries = [
        f"{keyword} 'contact us' 'editorial team'",
        f"{keyword} 'submission guidelines' 'guest post'",
        f"{keyword} 'write for us' 'contact'",
        f"{keyword} 'guest post' 'submission process'",
        f"{keyword} 'contribute' 'editorial guidelines'",
    ]
    
    # Combine all query types
    all_queries = base_queries + industry_queries + contact_queries
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for query in all_queries:
        if query not in seen:
            seen.add(query)
            unique_queries.append(query)
    
    return unique_queries


def search_with_exa(keyword, exa_api_key: str | None = None, max_results: int = 10):
    """
    Search for backlink opportunities using Exa API with enhanced parameters.

    Args:
        keyword (str): The keyword to search for backlink opportunities.
        exa_api_key (str, optional): Exa API key. If not provided, gets from environment.
        max_results (int): Maximum number of results to return.

    Returns:
        list: A list of results from the Exa search.
    """
    key = exa_api_key or _get_exa_api_key()
    if not key:
        logger.warning("Exa API key not found. Skipping Exa search.")
        return []
    
    if not _exa_reachable(key):
        logger.warning("Exa API not reachable. Skipping Exa search.")
        return []
    
    search_queries = generate_exa_search_queries(keyword)
    results = []
    
    try:
        headers = {"x-api-key": key, "Content-Type": "application/json"}
        
        for i, query in enumerate(search_queries):
            if len(results) >= max_results:
                break
            
            # Rate limiting between requests
            if i > 0:
                time.sleep(RATE_LIMIT_DELAY)
                
            try:
                # Phase 1: Enhanced Exa search with optimized parameters
                response = _make_exa_request_with_retry(
                    "https://api.exa.ai/search",
                    headers=headers,
                    json_data={
                        "query": query,
                        "type": "neural",  # AI-powered semantic understanding
                        "useAutoprompt": True,  # Intelligent query expansion
                        "numResults": min(25, max_results - len(results)),  # Increased results
                        "text": True,  # Get text content for each result
                        "highlights": True,  # Key content identification
                        "includeDomains": [],  # Target specific website types
                        "excludeDomains": []  # Filter out irrelevant sites
                    }
                )
                
                if not response:
                    logger.warning(f"Exa search failed for '{query}' after retries")
                    continue
                
                data = response.json()
                
                # Process Exa results
                for result in data.get("results", []):
                    if len(results) >= max_results:
                        break
                        
                    url = result.get("url")
                    title = result.get("title")
                    text = result.get("text", "")
                    highlights = result.get("highlights", [])
                    
                    if not url:
                        continue
                        
                    # Create result in same format as Serper for consistency
                    row = {
                        "url": url,
                        "title": title or "",
                        "contact_email": "",  # Will be extracted later
                        "contact_emails_all": "",
                        "contact_form_url": "",
                        "guidelines_url": "",
                        "domain": url.split("//")[-1].split("/")[0] if "//" in url else url,
                        "notes": "",
                        "page_excerpt": text[:1500] if text else "",
                        "context_source": "exa",
                        "highlights": highlights,  # New field for key insights
                        "needs_content_retrieval": True  # Flag for Phase 2 content retrieval
                    }
                    
                    results.append(row)
                    
            except Exception as exc:
                logger.warning(f"Exa search failed for '{query}': {exc}")
                continue
                
    except Exception as exc:
        logger.error(f"Exa search failed: {exc}")
    
    return results


def get_exa_content(urls, exa_api_key: str | None = None):
    """
    Phase 2: Get full page content using Exa Get Contents API.
    
    Args:
        urls (list): List of URLs to get content for
        exa_api_key (str, optional): Exa API key. If not provided, gets from environment.
    
    Returns:
        dict: URL to content mapping with full page text and metadata
    """
    key = exa_api_key or _get_exa_api_key()
    if not key:
        logger.warning("Exa API key not found. Skipping content retrieval.")
        return {}
    
    if not _exa_reachable(key):
        logger.warning("Exa API not reachable. Skipping content retrieval.")
        return {}
    
    try:
        headers = {"x-api-key": key, "Content-Type": "application/json"}
        
        # Exa Get Contents API call with retry logic
        response = _make_exa_request_with_retry(
            "https://api.exa.ai/contents",
            headers=headers,
            json_data={
                "urls": urls,
                "text": True,  # Get full page text
                "highlights": True,  # Get content highlights
                "summary": True  # Get page summary
            }
        )
        
        if not response:
            logger.error("Exa content retrieval failed after retries")
            return {}
        
        data = response.json()
        
        content_map = {}
        for result in data.get("results", []):
            url = result.get("url")
            if url:
                content_map[url] = {
                    "full_text": result.get("text", ""),
                    "summary": result.get("summary", ""),
                    "highlights": result.get("highlights", []),
                    "title": result.get("title", ""),
                    "author": result.get("author", ""),
                    "published_date": result.get("publishedDate", ""),
                    "subpages": result.get("subpages", []),
                    "extras": result.get("extras", {})
                }
        
        return content_map
        
    except Exception as exc:
        logger.error(f"Exa content retrieval failed: {exc}")
        return {}
