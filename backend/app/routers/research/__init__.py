"""
Research router package - handles backlink research operations
"""
from .start_research import start_research
from .status import research_status

__all__ = ['start_research', 'research_status']
