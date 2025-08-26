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
from typing import List, Dict, Any

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
            timeout=15,
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
    Generate comprehensive search queries for finding guest post opportunities.
    
    Enhanced with extensive guest post keyword combinations for maximum coverage.

    Args:
        keyword (str): The keyword to base the search queries on.

    Returns:
        list: A comprehensive list of guest post search queries.
    """
    # Comprehensive guest post queries
    guest_post_queries = [
        f"{keyword} 'Guest Contributor'",
        f"{keyword} 'Add Guest Post'",
        f"{keyword} 'Guest Bloggers Wanted'",
        f"{keyword} 'Guest Posts Roundup'",
        f"{keyword} 'Write for Us'",
        f"{keyword} 'Submit Guest Post'",
        f"{keyword} 'Submit a Guest Article'",
        f"{keyword} 'Guest Bloggers Wanted'",
        f"{keyword} 'Submit an article'",
        f"{keyword} 'Suggest a guest post'",
        f"{keyword} 'Send a guest post'",
        f"{keyword} 'Become a Guest Blogger'",
        f"{keyword} 'guest post opportunities'",
        f"{keyword} 'this is a guest post by'",
        f"{keyword} 'This post was written by'",
        f"{keyword} 'guest post courtesy of'",
        f"{keyword} 'submit article'",
        f"{keyword} 'write for us'",
        f"{keyword} 'guest post'",
        f"{keyword} 'submit guest post'",
        f"{keyword} 'guest contributor'",
        f"{keyword} 'become a guest blogger'",
        f"{keyword} 'editorial guidelines'",
        f"{keyword} 'contribute'",
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
    all_queries = guest_post_queries + industry_queries + contact_queries
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for query in all_queries:
        if query not in seen:
            seen.add(query)
            unique_queries.append(query)
    
    return unique_queries


async def _probe_domain_for_guidelines(domain: str, api_key: str) -> str:
    """
    Probe a domain for common guest post guideline paths.
    
    Args:
        domain (str): Domain to probe (e.g., 'example.com')
        api_key (str): Exa API key
    
    Returns:
        str: URL of guidelines page if found, empty string otherwise
    """
    common_paths = [
        "/write-for-us",
        "/guest-post",
        "/submit-article", 
        "/contribute",
        "/submission-guidelines",
        "/editorial-guidelines",
        "/guest-blogger",
        "/guest-contributor",
        "/write-for-us/",
        "/guest-post/",
        "/submit-article/",
        "/contribute/",
        "/submission-guidelines/",
        "/editorial-guidelines/",
        "/guest-blogger/",
        "/guest-contributor/"
    ]
    
    for path in common_paths:
        try:
            test_url = f"https://{domain}{path}"
            response = _make_exa_request_with_retry(
                "https://api.exa.ai/search",
                headers={"X-API-KEY": api_key},
                json_data={
                    "query": f"site:{domain} {path}",
                    "type": "neural",
                    "numResults": 1,
                    "text": True
                }
            )
            
            if response and response.json().get("results"):
                result = response.json()["results"][0]
                if result.get("url") and any(indicator in result.get("url", "").lower() for indicator in ["write-for-us", "guest-post", "submit", "guidelines", "contribute"]):
                    logger.info(f"Found guidelines page for {domain}: {result['url']}")
                    return result["url"]
                    
        except Exception as e:
            logger.debug(f"Error probing {domain}{path}: {e}")
            continue
    
    return ""


async def _probe_domain_for_contact_forms(domain: str, api_key: str) -> str:
    """
    Probe a domain for common contact form and submission paths.
    
    Args:
        domain (str): Domain to probe (e.g., 'example.com')
        api_key (str): Exa API key
    
    Returns:
        str: URL of contact form page if found, empty string otherwise
    """
    common_paths = [
        "/contact",
        "/contact-us",
        "/get-in-touch",
        "/reach-us",
        "/write-to-us",
        "/submit",
        "/submission",
        "/pitch",
        "/proposal",
        "/inquiry",
        "/editorial-team",
        "/editorial team",
        "/contact/",
        "/contact-us/",
        "/get-in-touch/",
        "/reach-us/",
        "/write-to-us/",
        "/submit/",
        "/submission/",
        "/pitch/",
        "/proposal/",
        "/inquiry/",
        "/editorial-team/",
        "/editorial team/"
    ]
    
    for path in common_paths:
        try:
            test_url = f"https://{domain}{path}"
            response = _make_exa_request_with_retry(
                "https://api.exa.ai/search",
                headers={"X-API-KEY": api_key},
                json_data={
                    "query": f"site:{domain} {path}",
                    "type": "neural",
                    "numResults": 1,
                    "text": True
                }
            )
            
            if response and response.json().get("results"):
                result = response.json()["results"][0]
                if result.get("url") and any(indicator in result.get("url", "").lower() for indicator in ["contact", "submit", "pitch", "proposal", "inquiry", "editorial"]):
                    logger.info(f"Found contact form page for {domain}: {result['url']}")
                    return result["url"]
                    
        except Exception as e:
            logger.debug(f"Error probing {domain}{path}: {e}")
            continue
    
    return ""


async def search_with_exa(keyword: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search for backlink opportunities using Exa API.
    
    Args:
        keyword: Search keyword
        max_results: Maximum number of results to return
    
    Returns:
        List of search result dictionaries
    """
    api_key = _get_exa_api_key()
    if not api_key:
        logger.error("EXA_API_KEY: NOT SET")
        return []
    
    if not _exa_reachable(api_key):
        logger.error("Exa API is not reachable")
        return []
    
    # Generate optimized search queries
    queries = generate_exa_search_queries(keyword)
    logger.info(f"Generated {len(queries)} search queries for keyword: {keyword}")
    
    all_results = []
    
    for i, query in enumerate(queries):
        if len(all_results) >= max_results:
            break
            
        logger.info(f"Executing query {i+1}/{len(queries)}: {query}")
        
        try:
            # Make API request with retry logic
            response = _make_exa_request_with_retry(
                "https://api.exa.ai/search",
                headers={"X-API-KEY": api_key},
                json_data={
                    "query": query,
                    "type": "neural",
                    "useAutoprompt": True,
                    "numResults": min(25, max_results - len(all_results)),
                    "text": True,
                    "highlights": True,
                    "includeDomains": [],
                    "excludeDomains": []
                }
            )
            
            if not response:
                logger.warning(f"Query failed: {query}")
                continue
            
            # Process search results
            for result in response.json().get("results", []):
                if len(all_results) >= max_results:
                    break
                
                # Debug: Log what fields are available in search result
                if i == 0:  # Only log for first result to avoid spam
                    logger.info(f"Search result fields: {list(result.keys())}")
                    logger.info(f"Text field content: {result.get('text', 'EMPTY')[:100]}...")
                
                # Create result row with enhanced content fields
                row = {
                    "url": result.get("url", ""),
                    "domain": result.get("url", "").split("//")[-1].split("/")[0] if result.get("url") else "",
                    "title": result.get("title", ""),
                    "contact_email": "",
                    "contact_emails_all": "",
                    "contact_form_url": "",
                    "guidelines_url": "",
                    "context_source": "exa_search",
                    "page_excerpt": result.get("text", ""),
                    "notes": "",
                    
                    # Enhanced content fields
                    "highlights": result.get("highlights", []),
                    "needs_content_retrieval": True,  # Will be filled by content retrieval
                    "full_page_text": "",  # Will be filled by content retrieval
                    "page_summary": "",  # Will be filled by content retrieval
                    "content_highlights": [],  # Will be filled by content retrieval
                    "page_author": "",  # Will be filled by content retrieval
                    "published_date": "",  # Will be filled by content retrieval
                    "subpages": [],  # Will be filled by content retrieval
                    "content_extras": {}  # Will be filled by content retrieval
                }
                
                # Extract guidelines URL if result itself looks like a guidelines/guest-post page
                try:
                    url_lower = (row["url"] or "").lower()
                    title_lower = (row["title"] or "").lower()
                    guideline_indicators = [
                        "write-for-us", "write for us", "guest-post", "guest post",
                        "submit-guest-post", "submit a guest article", "submit article",
                        "submission-guidelines", "submission guidelines", "editorial-guidelines",
                        "editorial guidelines", "contribute", "become-a-guest-blogger",
                        "guest blogger", "guest contributor", "guest bloggers wanted",
                        "guest posts roundup"
                    ]
                    if any(ind in url_lower for ind in guideline_indicators) or any(ind in title_lower for ind in guideline_indicators):
                        row["guidelines_url"] = row["url"]
                        logger.info(f"Detected guidelines page from result: {row['guidelines_url']}")
                except Exception:
                    pass
                
                # Extract contact form URL if result looks like a contact/submission page
                try:
                    contact_indicators = [
                        "contact", "contact-us", "contact us", "get-in-touch", "get in touch",
                        "reach-us", "reach us", "submit", "submission", "write-to-us", "write to us",
                        "editorial-team", "editorial team", "pitch", "proposal", "inquiry"
                    ]
                    if any(ind in url_lower for ind in contact_indicators) or any(ind in title_lower for ind in contact_indicators):
                        row["contact_form_url"] = row["url"]
                        logger.info(f"Detected contact page from result: {row['contact_form_url']}")
                except Exception:
                    pass
                
                all_results.append(row)
            
            # Rate limiting delay between queries
            if i < len(queries) - 1:  # Don't delay after the last query
                time.sleep(RATE_LIMIT_DELAY)
                
        except Exception as e:
            logger.error(f"Error executing query '{query}': {e}")
            continue
    
    # Probe domains without guidelines URLs for common guest post paths
    logger.info("Probing domains without guidelines URLs for common guest post paths...")
    for result in all_results:
        if not result.get("guidelines_url") and result.get("domain"):
            logger.info(f"Probing {result['domain']} for guidelines pages...")
            guidelines_url = await _probe_domain_for_guidelines(result["domain"], api_key)
            if guidelines_url:
                result["guidelines_url"] = guidelines_url
                logger.info(f"Found guidelines URL for {result['domain']}: {guidelines_url}")
    
    # Probe domains without contact form URLs for common contact paths
    logger.info("Probing domains without contact form URLs for common contact paths...")
    for result in all_results:
        if not result.get("contact_form_url") and result.get("domain"):
            logger.info(f"Probing {result['domain']} for contact form pages...")
            contact_form_url = await _probe_domain_for_contact_forms(result["domain"], api_key)
            if contact_form_url:
                result["contact_form_url"] = contact_form_url
                logger.info(f"Found contact form URL for {result['domain']}: {contact_form_url}")
    
    logger.info(f"Exa search completed. Found {len(all_results)} results")
    return all_results


async def get_exa_content(urls, exa_api_key: str | None = None):
    """
    Get full page content using Exa Get Contents API.
    
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
    
    logger.info(f"Starting content retrieval for {len(urls)} URLs")
    
    try:
        headers = {"x-api-key": key, "Content-Type": "application/json"}
        
        # Exa Get Contents API call with retry logic
        logger.info("Calling Exa Get Contents API...")
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
        
        logger.info(f"Got response with status: {response.status_code}")
        
        try:
            data = response.json()
            logger.info(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        except Exception as json_exc:
            logger.error(f"Failed to parse JSON response: {json_exc}")
            logger.error(f"Response text: {response.text[:500]}")
            return {}
        
        content_map = {}
        results = data.get("results", [])
        logger.info(f"Found {len(results)} results in response")
        
        for result in results:
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
                logger.info(f"Processed content for {url}: text_length={len(content_map[url]['full_text'])}, highlights={len(content_map[url]['highlights'])}")
        
        logger.info(f"Successfully processed {len(content_map)} URLs")
        return content_map
        
    except Exception as exc:
        logger.error(f"Exa content retrieval failed: {exc}")
        return {}
