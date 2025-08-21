"""
MailerSend Email Provider Package
"""
from .single_sender import send_one_mailersend
from .bulk_sender import send_bulk_mailersend

__all__ = [
    'send_one_mailersend',
    'send_bulk_mailersend'
]
