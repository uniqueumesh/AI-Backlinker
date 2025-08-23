"""
Email Extraction Functions - extracted from core.py
"""
import re


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _extract_emails(text: str) -> list[str]:
    emails = set(e.lower() for e in _EMAIL_RE.findall(text or ""))
    # filter obvious placeholders
    filtered = [e for e in emails if not any(bad in e for bad in ("example.com", "no-reply", "noreply"))]
    return filtered


def _choose_best_email(emails: list[str], domain: str) -> str:
    """Choose the best email from a list, preferring domain-matching ones."""
    if not emails:
        return ""
    # Prefer emails matching the domain
    domain_emails = [e for e in emails if domain in e]
    if domain_emails:
        return domain_emails[0]
    # Fall back to first email
    return emails[0]
