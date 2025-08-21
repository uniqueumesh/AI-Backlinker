"""
SMTP Email Provider Package
"""
from .single_sender import send_one_smtp
from .bulk_sender import send_bulk_smtp
from .dispatcher import send_bulk_emails

__all__ = [
    'send_one_smtp',
    'send_bulk_smtp',
    'send_bulk_emails'
]
