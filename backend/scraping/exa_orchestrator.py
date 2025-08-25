"""
Exa Research Orchestrator Module - Handles Exa research workflow coordination and management

This module contains the Exa research orchestration function that coordinates
the Exa backlink research process, managing search queries, scraping,
and data compilation. Separated from core scraping to enable future
extensibility and cleaner architecture.
"""
import httpx
from urllib.parse import urlparse
from loguru import logger

# Import required functions from other modules
from .exa import generate_exa_search_queries, _get_exa_api_key, _exa_reachable, search_with_exa, get_exa_content
# DISABLED: Firecrawl imports temporarily
# from .firecrawl import _get_firecrawl_api_key, scrape_website
# from .content_extraction import _collect_page_text, _strip_html_tags, _collapse_whitespace, _http_fetch_text
from .email_extraction import _extract_emails, _choose_best_email
# DISABLED: Link extraction temporarily
# from .link_extraction import _extract_links, _classify_support_links
from .data_processing import _compose_notes


def find_backlink_opportunities_exa(
    keyword,
    exa_api_key: str | None = None,
    firecrawl_api_key: str | None = None,
    max_results: int = 10,
):
    """
    Find backlink opportunities using Exa search with two-phase content retrieval.

    Args:
        keyword (str): The keyword to search for backlink opportunities.
        exa_api_key (str, optional): Exa API key. If not provided, gets from environment.
        firecrawl_api_key (str, optional): Firecrawl API key. If not provided, gets from environment.
        max_results (int): Maximum number of results to return.

    Returns:
        list: A list of results from the Exa research with enhanced content.
    """
    # Phase 1: Enhanced Exa search with optimized parameters
    logger.info(f"Phase 1: Starting enhanced Exa search for keyword: {keyword}")
    exa_results = search_with_exa(keyword, exa_api_key, max_results)
    
    if not exa_results:
        logger.info("No Exa search results found.")
        return []
    
    logger.info(f"Phase 1 complete: Found {len(exa_results)} search results")
    
    # Phase 2: Get full page content using Exa Get Contents API
    logger.info("Phase 2: Starting full content retrieval")
    urls_to_retrieve = [result.get("url") for result in exa_results if result.get("url")]
    
    if urls_to_retrieve:
        content_map = get_exa_content(urls_to_retrieve, exa_api_key)
        logger.info(f"Phase 2 complete: Retrieved content for {len(content_map)} URLs")
    else:
        content_map = {}
    
    # Process and enhance results with full content
    processed_results = []
    
    for result in exa_results:
        if len(processed_results) >= max_results:
            break
            
        url = result.get("url")
        if not url:
            continue
            
        try:
            # Get enhanced content if available
            enhanced_content = content_map.get(url, {})
            
            # Use full text if available, fallback to excerpt
            full_text = enhanced_content.get("full_text", "")
            page_text = full_text if full_text else result.get("page_excerpt", "")
            
            # Extract emails from enhanced content
            emails = _extract_emails(page_text)
            domain = urlparse(url).netloc
            best_email = _choose_best_email(emails, domain)
            
            # Update result with enhanced information
            result.update({
                "contact_email": best_email,
                "contact_emails_all": ", ".join(emails[:5]) if emails else "",
                "contact_form_url": "",  # Will be enhanced in Phase 2
                "guidelines_url": "",    # Will be enhanced in Phase 2
                "page_excerpt": page_text,
                "context_source": "exa_enhanced",
                # Enhanced content fields
                "full_page_text": full_text,
                "page_summary": enhanced_content.get("summary", ""),
                "content_highlights": enhanced_content.get("highlights", []),
                "page_author": enhanced_content.get("author", ""),
                "published_date": enhanced_content.get("published_date", ""),
                "subpages": enhanced_content.get("subpages", []),
                "content_extras": enhanced_content.get("extras", {})
            })
            
            # Compose notes with enhanced content
            result["notes"] = _compose_notes(result, keyword)
            
            processed_results.append(result)
            
        except Exception as exc:
            logger.warning(f"Failed to process Exa result {url}: {exc}")
            # Still include the result with basic information
            result["notes"] = _compose_notes(result, keyword)
            processed_results.append(result)
    
    logger.info(f"Processing complete: {len(processed_results)} results ready")
    return processed_results
