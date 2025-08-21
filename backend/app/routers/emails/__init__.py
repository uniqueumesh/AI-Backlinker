"""
Emails router package - handles email generation operations
"""
from .start_generation import start_email_generation
from .status import email_generation_status

__all__ = ['start_email_generation', 'email_generation_status']
