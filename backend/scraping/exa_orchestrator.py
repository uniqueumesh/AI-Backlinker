"""
Exa Research Orchestrator Module - Handles Exa research workflow coordination and management

This module contains the Exa research orchestration function that coordinates
the Exa backlink research process, managing search queries, scraping,
and data compilation. Separated from core scraping to enable future
extensibility and cleaner architecture.
"""
import asyncio
import time
from typing import List, Dict, Any
from loguru import logger
from .exa import search_with_exa, get_exa_content

async def find_backlink_opportunities_exa(
    keywords: List[str],
    max_results: int = 3,
    search_depth: int = 2
) -> List[Dict[str, Any]]:
    """
    Find backlink opportunities using Exa search provider.
    
    Args:
        keywords: List of keywords to search for
        max_results: Maximum number of results to return
        search_depth: How deep to search (1 = basic, 2 = enhanced)
    
    Returns:
        List of opportunity dictionaries
    """
    logger.info(f"Starting Exa research with {len(keywords)} keywords, max_results={max_results}")
    
    results = []
    
    for keyword in keywords:
        logger.info(f"Processing keyword: {keyword}")
        
        try:
            # Basic search and content retrieval
            search_results = await search_with_exa(keyword, max_results)
            
            if not search_results:
                logger.warning(f"No search results found for keyword: {keyword}")
                continue
            
            logger.info(f"Found {len(search_results)} search results for keyword: {keyword}")
            
            # Enhanced content retrieval (if search_depth > 1)
            if search_depth > 1:
                logger.info("Starting enhanced content retrieval")
                
                # Get URLs for content retrieval
                urls = [result.get('url', '') for result in search_results if result.get('url')]
                
                if urls:
                    logger.info(f"Retrieving full content for {len(urls)} URLs")
                    
                    try:
                        # Get full content for these URLs
                        content_results = await get_exa_content(urls)
                        
                        if content_results:
                            logger.info(f"Successfully retrieved content for {len(content_results)} URLs")
                            
                            # Merge content with search results
                            for result in search_results:
                                url = result.get('url')
                                if url and url in content_results:
                                    content_data = content_results[url]
                                    # Update with enhanced content data
                                    result.update({
                                        'full_page_text': content_data.get('full_text', ''),
                                        'page_summary': content_data.get('summary', ''),
                                        'content_highlights': content_data.get('highlights', []),
                                        'page_author': content_data.get('author', ''),
                                        'published_date': content_data.get('published_date', ''),
                                        'subpages': content_data.get('subpages', []),
                                        'content_extras': content_data.get('extras', {}),
                                        'context_source': 'exa_enhanced'
                                    })
                                    # Populate page_excerpt if search didn't provide it
                                    if not result.get('page_excerpt'):
                                        summary = content_data.get('summary', '')
                                        if summary:
                                            result['page_excerpt'] = summary
                                        else:
                                            full_text = content_data.get('full_text', '')
                                            if full_text:
                                                result['page_excerpt'] = full_text[:300]
                                    
                                    # Debug logging for highlights
                                    logger.info(f"Highlights for {url}: {result.get('highlights', 'NOT_FOUND')}")
                                    
                                    # Populate highlights if search didn't provide them
                                    if not result.get('highlights') or len(result.get('highlights', [])) == 0:
                                        logger.info(f"Highlights empty for {url}, applying fallback logic")
                                        content_highlights = content_data.get('highlights', [])
                                        if content_highlights and len(content_highlights) > 0:
                                            result['highlights'] = content_highlights
                                            logger.info(f"Using content highlights for {url}: {content_highlights}")
                                        else:
                                            # Fallback: create basic highlights from summary
                                            summary = content_data.get('summary', '')
                                            if summary:
                                                result['highlights'] = [summary[:100] + "..."]
                                                logger.info(f"Created highlights from summary for {url}")
                                            else:
                                                logger.info(f"No summary available for {url}, trying excerpt fallback")
                                    
                                    # Ensure highlights are always populated (final fallback)
                                    if not result.get('highlights') or len(result.get('highlights', [])) == 0:
                                        logger.info(f"Final highlights fallback for {url}")
                                        # Create highlights from page_excerpt if available
                                        excerpt = result.get('page_excerpt', '')
                                        if excerpt:
                                            result['highlights'] = [excerpt[:100] + "..."]
                                            logger.info(f"Created highlights from excerpt for {url}")
                                        else:
                                            # Last resort: create from title
                                            title = result.get('title', '')
                                            if title:
                                                result['highlights'] = [title + " - Guest post opportunity"]
                                                logger.info(f"Created highlights from title for {url}")
                                            else:
                                                result['highlights'] = ["Guest post opportunity available"]
                                                logger.info(f"Created generic highlights for {url}")
                                    
                                    # Final debug logging for highlights
                                    logger.info(f"Final highlights for {url}: {result.get('highlights', 'STILL_NOT_FOUND')}")
                                    
                                    # Mark as not needing content retrieval since we have it
                                    result['needs_content_retrieval'] = False
                                else:
                                    result['context_source'] = 'exa_basic'
                        else:
                            logger.warning("Content retrieval returned empty results")
                            for result in search_results:
                                result['context_source'] = 'exa_basic'
                    except Exception as e:
                        logger.error(f"Error during content retrieval: {e}")
                        for result in search_results:
                            result['context_source'] = 'exa_basic'
                else:
                    logger.warning("No valid URLs found for content retrieval")
                    for result in search_results:
                        result['context_source'] = 'exa_basic'
            else:
                # Basic search only
                for result in search_results:
                    result['context_source'] = 'exa_basic'
                    
                    # Ensure highlights are populated for basic search too
                    if not result.get('highlights') or len(result.get('highlights', [])) == 0:
                        # Try to create highlights from available data
                        excerpt = result.get('page_excerpt', '')
                        if excerpt:
                            result['highlights'] = [excerpt[:100] + "..."]
                        else:
                            title = result.get('title', '')
                            if title:
                                result['highlights'] = [title + " - Guest post opportunity"]
                            else:
                                result['highlights'] = ["Guest post opportunity available"]
            
            results.extend(search_results)
            
        except Exception as e:
            logger.error(f"Error processing keyword '{keyword}': {e}")
            continue
    
    logger.info(f"Exa research completed. Total results: {len(results)}")
    return results
