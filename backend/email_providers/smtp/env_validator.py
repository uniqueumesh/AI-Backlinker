"""
Environment variable validation for SMTP configuration
"""
import os
from loguru import logger

def _require_env(name: str) -> str:
    """
    Require an environment variable to be set.
    
    Args:
        name: Name of the environment variable
        
    Returns:
        Value of the environment variable
        
    Raises:
        ValueError: If environment variable is not set
    """
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value
