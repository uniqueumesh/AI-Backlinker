"""
Core Email Functions - extracted from ai_backlinking_emails.py
"""
import smtplib
import imaplib
import email as email_module
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger

# Import from the modularized LLM package
from llm import compose_personalized_email


def send_email(smtp_server, smtp_port, smtp_user, smtp_password, to_email, subject, body):
    """
    Send an email using an SMTP server.

    Args:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        smtp_user (str): The SMTP server username.
        smtp_password (str): The SMTP server password.
        to_email (str): The recipient's email address.
        subject (str): The email subject.
        body (str): The email body.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_follow_up_email(smtp_server, smtp_port, smtp_user, smtp_password, to_email, subject, body):
    """
    Send a follow-up email using an SMTP server.

    Args:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        smtp_user (str): The SMTP server username.
        smtp_password (str): The SMTP server password.
        to_email (str): The recipient's email address.
        subject (str): The email subject.
        body (str): The email body.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    return send_email(smtp_server, smtp_port, smtp_user, smtp_password, to_email, subject, body)


def check_email_responses(imap_server, imap_user, imap_password):
    """
    Check email responses using an IMAP server.

    Args:
        imap_server (str): The IMAP server address.
        imap_user (str): The IMAP server username.
        imap_password (str): The IMAP server password.

    Returns:
        list: A list of email responses.
    """
    responses = []
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(imap_user, imap_password)
        mail.select('inbox')

        status, data = mail.search(None, 'UNSEEN')
        mail_ids = data[0]
        id_list = mail_ids.split()

        for mail_id in id_list:
            status, data = mail.fetch(mail_id, '(RFC822)')
            msg = email_module.message_from_bytes(data[0][1])
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        responses.append(part.get_payload(decode=True).decode())
            else:
                responses.append(msg.get_payload(decode=True).decode())

        mail.logout()
    except Exception as e:
        logger.error(f"Failed to check email responses: {e}")

    return responses


def extract_contact_info(website_data):
    """
    Extract contact information from website data.

    Args:
        website_data (dict): Scraped data from the website.

    Returns:
        dict: Extracted contact information such as name, email, etc.
    """
    return {
        "name": website_data.get("contact", {}).get("name", "Webmaster"),
        "email": website_data.get("contact", {}).get("email", ""),
    }


def log_sent_email(keyword, email_info):
    """
    Log the information of a sent email.

    Args:
        keyword (str): The keyword associated with the email.
        email_info (dict): Information about the sent email (e.g., recipient, subject, body).
    """
    with open(f"{keyword}_sent_emails.log", "a") as log_file:
        log_file.write(f"{email_info}\n")


def _strip_subject_prefix(text: str) -> str:
    t = (text or "").lstrip()
    if t.lower().startswith("subject:"):
        parts = t.splitlines()
        return "\n".join(parts[1:]).lstrip()
    return text


def generate_emails_for_rows(
    rows: list[dict],
    subject: str,
    your_name: str,
    your_email: str,
    proposed_topic: str | None,
    provider: str = "gemini",
    model: str | None = None,
    serper_api_key: str | None = None,  # unused here but kept for parity
    firecrawl_api_key: str | None = None,  # unused here but kept for parity
    gemini_api_key: str | None = None,
    openai_api_key: str | None = None,
) -> list[dict]:
    generated: list[dict] = []
    for row in rows:
        insights = row.get("page_excerpt") or row.get("notes") or f"Page: {row.get('url','')}"
        body = compose_personalized_email(
            row,
            insights,
            {
                "user_name": your_name,
                "user_email": your_email,
                "topic": proposed_topic or "a guest post",
            },
            provider=provider,
            model=model,
            openai_api_key=openai_api_key,
            gemini_api_key=gemini_api_key,
        )
        body = _strip_subject_prefix(body)
        status = "ok"
        note = ""
        if body.startswith("[AI Draft]"):
            status = "fallback"
            note = "LLM placeholder (missing key or error)"
        generated.append(
            {
                "to_email": row.get("contact_email", ""),
                "subject": subject,
                "body": body,
                "url": row.get("url", ""),
                "domain": row.get("domain", ""),
                "title": row.get("title", ""),
                "context_source": row.get("context_source", ""),
                "excerpt_chars": len(row.get("page_excerpt") or ""),
                "status": status,
                "note": note,
                "provider": provider,
                "model": model or "",
            }
        )
    return generated
