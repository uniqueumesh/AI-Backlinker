"""
AI Backlinker Backend Package - Complete modularized backend
"""
# Core functions
from .ai_backlinking_core import main
from .scraping import (
    find_backlink_opportunities,
    scrape_website
)
from .llm import (
    llm_text_gen,
    compose_personalized_email
)
from .emails import (
    generate_emails_for_rows,
    send_email,
    send_follow_up_email
)
from .utils import (
    find_backlink_opportunities_for_keywords,
    build_row_from_url
)

# Email providers
from .email_providers import (
    send_bulk_smtp,
    send_bulk_sendgrid,
    send_bulk_mailersend
)

__all__ = [
    # Core functions
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
    # Email providers
    'send_bulk_smtp',
    'send_bulk_sendgrid',
    'send_bulk_mailersend'
]
