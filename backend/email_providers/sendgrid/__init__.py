"""
SendGrid Email Provider Package
"""
from .single_sender import send_one_sendgrid
from .bulk_sender import send_bulk_sendgrid

__all__ = [
    'send_one_sendgrid',
    'send_bulk_sendgrid'
]
