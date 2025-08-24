"""
Data Processing Module - Handles data formatting, note composition, and content structuring

This module contains all data processing functions for formatting scraped data,
creating human-readable notes, and structuring content for better readability.
Separated from core scraping to enable future extensibility and cleaner architecture.
"""


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
