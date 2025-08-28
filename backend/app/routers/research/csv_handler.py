"""
CSV handling utilities for research results
"""
import csv
import os
from typing import List, Dict, Any
from loguru import logger
from ...models import ResearchResultRow

def save_research_results_to_csv(
    results: List[ResearchResultRow],
    output_dir: str,
    filename: str
) -> str:
    """
    Save research results to a CSV file.
    
    Args:
        results: List of ResearchResultRow objects
        output_dir: Directory to save the CSV file
        filename: Name of the CSV file
        
    Returns:
        Full path to the saved CSV file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create full file path
    file_path = os.path.join(output_dir, filename)
    
    # Define field names based on the simplified model
    fieldnames = [
        'url', 'domain', 'title', 'contact_email', 'contact_emails_all',
        'contact_form_url', 'guidelines_url', 'context_source', 'page_excerpt',
        'highlights', 'needs_content_retrieval', 'full_page_text', 'page_summary',
        'content_highlights', 'page_author', 'published_date', 'subpages',
        'content_extras', 'notes'
    ]
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in results:
                # Convert Pydantic model to dict and handle list/dict types
                row_out = {}
                
                # Basic fields
                row_out['url'] = row.url
                row_out['domain'] = row.domain
                row_out['title'] = row.title
                row_out['contact_email'] = row.contact_email
                row_out['contact_emails_all'] = row.contact_emails_all
                row_out['contact_form_url'] = row.contact_form_url
                row_out['guidelines_url'] = row.guidelines_url
                row_out['context_source'] = row.context_source
                row_out['page_excerpt'] = row.page_excerpt
                
                # Enhanced content fields
                row_out['highlights'] = ' | '.join(row.highlights) if row.highlights else ''
                row_out['needs_content_retrieval'] = str(row.needs_content_retrieval)
                row_out['full_page_text'] = row.full_page_text[:500] if row.full_page_text else ''  # Limit length
                row_out['page_summary'] = row.page_summary
                row_out['content_highlights'] = ' | '.join(row.content_highlights) if row.content_highlights else ''
                row_out['page_author'] = row.page_author
                row_out['published_date'] = row.published_date
                row_out['subpages'] = ' | '.join(row.subpages) if row.subpages else ''
                row_out['content_extras'] = str(row.content_extras) if row.content_extras else ''
                
                # Notes field
                row_out['notes'] = row.notes
                
                writer.writerow(row_out)
        
        logger.info(f"Research results saved to CSV: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving research results to CSV: {e}")
        raise
