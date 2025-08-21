"""
Emails Module Package - email management functions
"""
from .core import generate_emails_for_rows, send_email, send_follow_up_email

__all__ = [
    'generate_emails_for_rows',
    'send_email',
    'send_follow_up_email'
]
