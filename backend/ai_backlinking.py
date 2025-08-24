"""
AI Backlinker - Main entry point for CLI and imports
"""
from . import (
    main,
    find_backlink_opportunities,
    scrape_website,
    llm_text_gen,
    compose_personalized_email,
    generate_emails_for_rows,
    send_email,
    send_follow_up_email,
    find_backlink_opportunities_for_keywords,
    build_row_from_url,
    send_bulk_smtp,
    send_bulk_sendgrid,
    send_bulk_mailersend
)

# Re-export main functions for backward compatibility
__all__ = [
    'main',
    'find_backlink_opportunities',
    'scrape_website',
    'llm_text_gen',
    'compose_personalized_email',
    'generate_emails_for_rows',
    'send_email',
    'send_follow_up_email',
    'find_backlink_opportunities_for_keywords',
    'build_row_from_url',
    'send_bulk_smtp',
    'send_bulk_sendgrid',
    'send_bulk_mailersend'
]

if __name__ == "__main__":
    main()
