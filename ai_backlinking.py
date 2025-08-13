#Problem:
#
#Finding websites for guest posts is manual, tedious, and time-consuming. Communicating with webmasters, maintaining conversations, and keeping track of backlinking opportunities is difficult to scale. Content creators and marketers struggle with discovering new websites and consistently getting backlinks.
#Solution:
#
#An AI-powered backlinking app that automates web research, scrapes websites, extracts contact information, and sends personalized outreach emails to webmasters. This would simplify the entire process, allowing marketers to scale their backlinking strategy with minimal manual intervention.
#Core Workflow:
#
#    User Input:
#        Keyword Search: The user inputs a keyword (e.g., "AI writers").
#        Search Queries: Your app will append various search strings to this keyword to find backlinking opportunities (e.g., "AI writers + 'Write for Us'").
#
#    Web Research:
#
#        Use search engines or web scraping to run multiple queries:
#            Keyword + "Guest Contributor"
#            Keyword + "Add Guest Post"
#            Keyword + "Write for Us", etc.
#
#        Collect URLs of websites that have pages or posts related to guest post opportunities.
#
#    Scrape Website Data:
#        Contact Information Extraction:
#            Scrape the website for contact details (email addresses, contact forms, etc.).
#            Use natural language processing (NLP) to understand the type of content on the website and who the contact person might be (webmaster, editor, or guest post manager).
#        Website Content Understanding:
#            Scrape a summary of each website's content (e.g., their blog topics, categories, and tone) to personalize the email based on the site's focus.
#
#    Personalized Outreach:
#        AI Email Composition:
#            Compose personalized outreach emails based on:
#                The scraped data (website content, topic focus, etc.).
#                The user's input (what kind of guest post or content they want to contribute).
#            Example: "Hi [Webmaster Name], I noticed that your site [Site Name] features high-quality content about [Topic]. I would love to contribute a guest post on [Proposed Topic] in exchange for a backlink."
#
#    Automated Email Sending:
#        Review Emails (Optional HITL):
#            Let users review and approve the personalized emails before they are sent, or allow full automation.
#        Send Emails:
#            Automate email dispatch through an integrated SMTP or API (e.g., Gmail API, SendGrid).
#            Keep track of which emails were sent, bounced, or received replies.
#
#    Scaling the Search:
#        Repeat for Multiple Keywords:
#            Run the same scraping and outreach process for a list of relevant keywords, either automatically suggested or uploaded by the user.
#        Keep Track of Sent Emails:
#            Maintain a log of all sent emails, responses, and follow-up reminders to avoid repetition or forgotten leads.
#
#    Tracking Responses and Follow-ups:
#        Automated Responses:
#            If a website replies positively, AI can respond with predefined follow-up emails (e.g., proposing topics, confirming submission deadlines).
#        Follow-up Reminders:
#            If there's no reply, the system can send polite follow-up reminders at pre-set intervals.
#
#Key Features:
#
#    Automated Web Scraping:
#        Scrape websites for guest post opportunities using a predefined set of search queries based on user input.
#        Extract key information like email addresses, names, and submission guidelines.
#
#    Personalized Email Writing:
#        Leverage AI to create personalized emails using the scraped website information.
#        Tailor each email to the tone, content style, and focus of the website.
#
#    Email Sending Automation:
#        Integrate with email platforms (e.g., Gmail, SendGrid, or custom SMTP).
#        Send automated outreach emails with the ability for users to review first (HITL - Human-in-the-loop) or automate completely.
#
#    Customizable Email Templates:
#        Allow users to customize or choose from a set of email templates for different types of outreach (e.g., guest post requests, follow-up emails, submission offers).
#
#    Lead Tracking and Management:
#        Track all emails sent, monitor replies, and keep track of successful backlinks.
#        Log each lead's status (e.g., emailed, responded, no reply) to manage future interactions.
#
#    Multiple Keywords/Queries:
#        Allow users to run the same process for a batch of keywords, automatically generating relevant search queries for each.
#
#    AI-Driven Follow-Up:
#        Schedule follow-up emails if there is no response after a specified period.
#
#    Reports and Analytics:
#        Provide users with reports on how many emails were sent, opened, replied to, and successful backlink placements.
#
#Advanced Features (for Scaling and Optimization):
#
#    Domain Authority Filtering:
#        Use SEO APIs (e.g., Moz, Ahrefs) to filter websites based on their domain authority or backlink strength.
#        Prioritize high-authority websites to maximize the impact of backlinks.
#
#    Spam Detection:
#        Use AI to detect and avoid spammy or low-quality websites that might harm the user's SEO.
#
#    Contact Form Auto-Fill:
#        If the site only offers a contact form (without email), automatically fill and submit the form with AI-generated content.
#
#    Dynamic Content Suggestions:
#        Suggest guest post topics based on the website's focus, using NLP to analyze the site's existing content.
#
#    Bulk Email Support:
#        Allow users to bulk-send outreach emails while still personalizing each message for scalability.
#
#    AI Copy Optimization:
#        Use copywriting AI to optimize email content, adjusting tone and CTA based on the target audience.
#
#Challenges and Considerations:
#
#    Legal Compliance:
#        Ensure compliance with anti-spam laws (e.g., CAN-SPAM, GDPR) by including unsubscribe options or manual email approval.
#
#    Scraping Limits:
#        Be mindful of scraping limits on certain websites and employ smart throttling or use API-based scraping for better reliability.
#
#    Deliverability:
#        Ensure emails are delivered properly without landing in spam folders by integrating proper email authentication (SPF, DKIM) and using high-reputation SMTP servers.
#
#    Maintaining Email Personalization:
#        Striking the balance between automating the email process and keeping each message personal enough to avoid being flagged as spam.
#
#Technology Stack:
#
#    Web Scraping: BeautifulSoup, Scrapy, or Puppeteer for scraping guest post opportunities and contact information.
#    Email Automation: Integrate with Gmail API, SendGrid, or Mailgun for sending emails.
#    NLP for Personalization: GPT-based models for email generation and web content understanding.
#    Frontend: React or Vue for the user interface.
#    Backend: Python/Node.js with Flask or Express for the API and automation logic.
#    Database: MongoDB or PostgreSQL to track leads, emails, and responses.
#
#This solution will significantly streamline the backlinking process by automating the most tedious tasks, from finding sites to personalizing outreach, enabling marketers to focus on content creation and high-level strategies.


import os
import sys
from loguru import logger
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import email as email_module
import httpx
import re
from urllib.parse import urljoin, urlparse

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def llm_text_gen(
    prompt: str,
    provider: str = "gemini",
    model: str | None = None,
    openai_api_key: str | None = None,
    gemini_api_key: str | None = None,
) -> str:
    """Generate text using selected provider (Gemini or OpenAI), with graceful fallback."""
    provider_normalized = (provider or "").strip().lower()
    if provider_normalized in ("gemini", "google", "google-gemini"):
        key = gemini_api_key or GEMINI_API_KEY
        if not key:
            return f"[AI Draft]\n{prompt.strip()}\n\n--\nThis is a placeholder draft (no Gemini API key)."
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=key)
            model_name = model or "gemini-2.5-flash"
            gmodel = genai.GenerativeModel(model_name)
            resp = gmodel.generate_content(prompt)
            text = getattr(resp, "text", None)
            return (text or "").strip() or f"[AI Draft]\n{prompt.strip()}\n\n--\nNo content returned."
        except Exception as exc:
            logger.warning(f"Gemini generation failed: {exc}")
            return f"[AI Draft]\n{prompt.strip()}\n\n--\nThis is a placeholder draft (Gemini error)."

    # Default to OpenAI
    key = openai_api_key or OPENAI_API_KEY
    if not key:
        return f"[AI Draft]\n{prompt.strip()}\n\n--\nThis is a placeholder draft (no OpenAI API key)."
    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=key)
        model_name = model or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model_name,
            temperature=0.7,
            max_tokens=700,
            messages=[
                {"role": "system", "content": "You are a helpful outreach assistant who writes concise, friendly, highly personalized guest-post outreach emails."},
                {"role": "user", "content": prompt},
            ],
        )
        content = (response.choices[0].message.content or "").strip()
        return content or f"[AI Draft]\n{prompt.strip()}\n\n--\nNo content returned."
    except Exception as exc:
        logger.warning(f"OpenAI generation failed: {exc}")
        return f"[AI Draft]\n{prompt.strip()}\n\n--\nThis is a placeholder draft (OpenAI error)."


def scrape_website(url: str, firecrawl_api_key: str | None = None):
    """Scrape a URL via Firecrawl if configured; otherwise return empty dict."""
    key = firecrawl_api_key or FIRECRAWL_API_KEY
    if not key:
        return {}
    try:
        # Firecrawl Python SDK import at runtime to avoid hard dep if absent
        from firecrawl import FirecrawlApp
        app = FirecrawlApp(api_key=key)
        data = app.scrape_url(url, formats=["markdown", "html"])  # type: ignore
        return data or {}
    except Exception as exc:
        logger.warning(f"Firecrawl scrape failed for {url}: {exc}")
        return {}


def scrape_url(url: str, firecrawl_api_key: str | None = None):
    return scrape_website(url, firecrawl_api_key)


def _collect_page_text(page: object | None) -> tuple[str, str]:
    """Return (markdown_text, html_text) from Firecrawl payload (dict/object) or raw string."""
    if page is None:
        return "", ""
    if isinstance(page, str):
        # best effort: assume raw text/markdown
        return page, ""
    md_text = ""
    html_text = ""
    # dict-like
    if isinstance(page, dict):
        for k in ("markdown", "md", "content", "text"):
            v = page.get(k)
            if isinstance(v, str):
                md_text += "\n" + v
        v_html = page.get("html")
        if isinstance(v_html, str):
            html_text = v_html
        return md_text, html_text
    # object-like (e.g., Firecrawl ScrapeResponse)
    for k in ("markdown", "md", "content", "text"):
        v = getattr(page, k, None)
        if isinstance(v, str):
            md_text += "\n" + v
    v_html = getattr(page, "html", None)
    if isinstance(v_html, str):
        html_text = v_html
    return md_text, html_text


def _strip_html_tags(html: str) -> str:
    try:
        return re.sub(r"<[^>]+>", " ", html or "")
    except Exception:
        return html or ""


def _collapse_whitespace(text: str) -> str:
    return " ".join((text or "").split())


def _http_fetch_text(url: str, timeout_s: int = 15) -> tuple[str, str]:
    """Fetch raw HTML via httpx and return (text, html). Safe, best-effort."""
    try:
        resp = httpx.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml",
            },
            follow_redirects=True,
            timeout=timeout_s,
        )
        if resp.status_code >= 400:
            return "", ""
        html = resp.text or ""
        text = _strip_html_tags(html)
        return _collapse_whitespace(text), html
    except Exception as exc:
        logger.warning(f"HTTP fallback fetch failed for {url}: {exc}")
        return "", ""


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _extract_emails(text: str) -> list[str]:
    emails = set(e.lower() for e in _EMAIL_RE.findall(text or ""))
    # filter obvious placeholders
    filtered = [e for e in emails if not any(bad in e for bad in ("example.com", "no-reply", "noreply"))]
    return sorted(filtered)


def _extract_links(html: str, base_url: str) -> list[str]:
    links = re.findall(r'href=[\"\']([^\"\']+)', html or "")
    normalized = []
    for href in links:
        if href.startswith("javascript:"):
            continue
        try:
            normalized.append(urljoin(base_url, href))
        except Exception:
            continue
    # dedupe while preserving order
    seen, out = set(), []
    for u in normalized:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _is_same_domain(email_addr: str, domain: str) -> bool:
    try:
        email_domain = email_addr.split("@", 1)[1]
        return email_domain.endswith(domain)
    except Exception:
        return False


def _choose_best_email(emails: list[str], domain: str) -> str:
    if not emails:
        return ""
    positive = ("editor", "content", "submit", "contrib", "press", "contact", "info")
    negative = ("sales", "job", "career", "support")
    # Prefer same-domain + positive keywords
    ranked = []
    for e in emails:
        score = 0
        if domain and _is_same_domain(e, domain):
            score += 3
        if any(p in e for p in positive):
            score += 2
        if any(n in e for n in negative):
            score -= 1
        ranked.append((score, e))
    ranked.sort(reverse=True)
    return ranked[0][1]


def _classify_support_links(links: list[str]) -> tuple[str, str]:
    """Return (guidelines_url, contact_form_url) from list of links."""
    guidelines_kw = ("write-for-us", "write for us", "guest", "contribute", "submission", "submit", "guidelines", "editorial")
    contact_kw = ("contact", "contact-us", "contactus", "contact_us", "form")
    g_url = ""
    c_url = ""
    for u in links:
        low = u.lower()
        if not g_url and any(k in low for k in guidelines_kw):
            g_url = u
        if not c_url and any(k in low for k in contact_kw):
            c_url = u
        if g_url and c_url:
            break
    return g_url, c_url


def _keyword_in(text: str, keyword: str) -> bool:
    try:
        return keyword.lower().split(" ")[0] in (text or "").lower()
    except Exception:
        return False


def _compose_notes(row: dict, keyword: str) -> str:
    parts: list[str] = []
    if row.get("guidelines_url"):
        parts.append("guidelines page")
    if row.get("contact_email"):
        parts.append("email found")
    elif row.get("contact_form_url"):
        parts.append("contact form")
    else:
        parts.append("no contact")
    if _keyword_in(row.get("title", ""), keyword):
        parts.append("keyword in title")
    return ", ".join(parts)

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
           colorize=True,
           format="<level>{level}</level>|<green>{file}:{line}:{function}</green>| {message}"
           )


def _sanitize_keyword(keyword: str) -> str:
    """Remove common footprints from user input so we add them ourselves.
    Examples removed: write for us, guest post, submit guest post, become a guest blogger, etc.
    """
    base = (keyword or "").strip()
    # remove quotes and pluses users might add
    base = base.replace("+", " ").replace("\"", "").replace("'", "")
    footprints = [
        "write for us", "guest post", "guest posts", "submit guest post", "guest blogger",
        "become a guest blogger", "guest contributor", "submission", "guidelines", "submit article",
        "inurl:write-for-us", "intitle:write for us"
    ]
    low = base.lower()
    for f in footprints:
        low = low.replace(f, " ")
    # collapse spaces
    cleaned = " ".join(low.split())
    return cleaned


def generate_search_queries(keyword):
    keyword = _sanitize_keyword(keyword)
    """
    Generate a list of search queries for finding guest post opportunities.

    Args:
        keyword (str): The keyword to base the search queries on.

    Returns:
        list: A list of search queries.
    """
    return [
        f"{keyword} 'write for us'",
        f"{keyword} 'guest post'",
        f"{keyword} 'submit guest post'",
        f"{keyword} 'guest contributor'",
        f"{keyword} 'become a guest blogger'",
        f"{keyword} 'editorial guidelines'",
        f"{keyword} 'contribute'",
        f"{keyword} 'submit article'",
    ]


def _serper_reachable(api_key: str) -> bool:
    """Best-effort check to avoid spamming errors when offline or DNS fails.
    Returns False quickly if https://google.serper.dev is not reachable.
    """
    try:
        # Lightweight GET to the root with short timeout. Some environments block HEAD.
        httpx.get(
            "https://google.serper.dev",
            timeout=3,
            headers={"X-API-KEY": api_key} if api_key else None,
        )
        return True
    except Exception as exc:
        logger.warning(f"Serper appears unreachable (network/DNS): {exc}. Skipping search.")
        return False


def find_backlink_opportunities(
    keyword,
    serper_api_key: str | None = None,
    firecrawl_api_key: str | None = None,
    max_results: int = 10,
):
    """
    Find backlink opportunities by scraping websites based on search queries.

    Args:
        keyword (str): The keyword to search for backlink opportunities.

    Returns:
        list: A list of results from the scraped websites.
    """
    search_queries = generate_search_queries(keyword)
    results: list[dict] = []

    serper_key = serper_api_key or SERPER_API_KEY
    firecrawl_key = firecrawl_api_key or FIRECRAWL_API_KEY

    if serper_key and _serper_reachable(serper_key):
        headers = {"X-API-KEY": serper_key, "Content-Type": "application/json"}
        unique: dict[str, dict] = {}
        for q in search_queries:
            if len(unique) >= max_results:
                break
            try:
                resp = httpx.post(
                    "https://google.serper.dev/search",
                    headers=headers,
                    json={"q": q, "num": 10},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                for item in (data.get("organic") or []):
                    if len(unique) >= max_results:
                        break
                    url = item.get("link")
                    title = item.get("title")
                    if not url:
                        continue
                    page = scrape_website(url, firecrawl_key)
                    md_text, html_text = _collect_page_text(page)
                    context_source = "firecrawl"
                    # best-effort excerpt for LLM insights
                    raw_text = (md_text or "").strip()
                    if not raw_text and html_text:
                        raw_text = _strip_html_tags(html_text)
                    excerpt = _collapse_whitespace(raw_text)[:1500]
                    # If Firecrawl yielded nothing, try HTTP fallback
                    if not excerpt:
                        context_source = "httpx"
                        http_text, http_html = _http_fetch_text(url)
                        if http_text:
                            excerpt = http_text[:1500]
                            html_text = http_html or html_text
                        else:
                            # Last resort: use Serper organic snippet
                            snippet = item.get("snippet") or item.get("description") or ""
                            if snippet:
                                context_source = "serper_snippet"
                                excerpt = _collapse_whitespace(snippet)[:600]
                            else:
                                context_source = "empty"
                    # emails
                    emails = _extract_emails((md_text + "\n" + html_text))
                    domain = urlparse(url).netloc
                    best_email = _choose_best_email(emails, domain)
                    # support links
                    links = _extract_links(html_text, url)
                    g_url, c_url = _classify_support_links(links)
                    if not g_url and title and "write" in title.lower():
                        g_url = url
                    row = {
                        "url": url,
                        "title": title or "",
                        "contact_email": best_email,
                        "contact_emails_all": ", ".join(emails[:5]) if emails else "",
                        "contact_form_url": c_url,
                        "guidelines_url": g_url,
                        "domain": domain or url,
                        "notes": "",
                        "page_excerpt": excerpt,
                        "context_source": context_source,
                    }
                    row["notes"] = _compose_notes(row, keyword)
                    unique[url] = row
            except Exception as exc:
                logger.warning(f"Serper fetch failed for '{q}': {exc}")

    # Finalize (deduped + capped)
    if serper_key:
        return list(unique.values())
    return results


def search_for_urls(query):
    """
    Search for URLs using Google search.
    
    Args:
        query (str): The search query.
        
    Returns:
        list: List of URLs found.
    """
    # Temporarily disabled Google search functionality
    # return list(search(query, num_results=10))
    return []


def compose_personalized_email(
    website_data,
    insights,
    user_proposal,
    provider: str = "gemini",
    model: str | None = None,
    openai_api_key: str | None = None,
    gemini_api_key: str | None = None,
):
    """
    Compose a personalized outreach email using AI LLM based on website data, insights, and user proposal.

    Args:
        website_data (dict): The data of the website including metadata and contact info.
        insights (str): Insights generated by the LLM about the website.
        user_proposal (dict): The user's proposal for a guest post or content contribution.

    Returns:
        str: A personalized email message.
    """
    contact_name = website_data.get("contact_info", {}).get("name", "Webmaster")
    # Prefer explicit metadata title, else domain as site name
    site_name = website_data.get("metadata", {}).get("title") or website_data.get("domain") or "your site"
    proposed_topic = user_proposal.get("topic", "a guest post")
    user_name = user_proposal.get("user_name", "Your Name")
    user_email = user_proposal.get("user_email", "your_email@example.com")

    email_prompt = f"""
You are an AI assistant tasked with composing a highly personalized outreach email for guest posting.

Contact Name: {contact_name}
Website Name: {site_name}
Proposed Topic: {proposed_topic}

User Details:
Name: {user_name}
Email: {user_email}

Website Insights: {insights}

Please compose a professional and engaging email that includes:
1. A personalized introduction addressing the recipient.
2. A mention of the website's content focus.
3. A proposal for a guest post.
4. A call to action to discuss the guest post opportunity.
5. A polite closing with user contact details.
"""

    return llm_text_gen(
        email_prompt,
        provider=provider,
        model=model,
        openai_api_key=openai_api_key,
        gemini_api_key=gemini_api_key,
    )


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


def find_backlink_opportunities_for_keywords(keywords):
    """
    Find backlink opportunities for multiple keywords.

    Args:
        keywords (list): A list of keywords to search for backlink opportunities.

    Returns:
        dict: A dictionary with keywords as keys and a list of results as values.
    """
    all_results = {}
    for keyword in keywords:
        results = find_backlink_opportunities(keyword)
        all_results[keyword] = results
    return all_results


def log_sent_email(keyword, email_info):
    """
    Log the information of a sent email.

    Args:
        keyword (str): The keyword associated with the email.
        email_info (dict): Information about the sent email (e.g., recipient, subject, body).
    """
    with open(f"{keyword}_sent_emails.log", "a") as log_file:
        log_file.write(f"{email_info}\n")


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


# ----------------------------
# CLI helpers for terminal use
# ----------------------------

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


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import csv
    from pathlib import Path

    parser = argparse.ArgumentParser(description="AI Backlinker CLI (Phase 2 + Phase 3)")
    parser.add_argument("keyword", help="Seed keyword, e.g. 'AI tools'")
    parser.add_argument("--max-results", type=int, default=10, dest="max_results")
    parser.add_argument("--subject", default="Guest post collaboration")
    parser.add_argument("--your-name", default=os.getenv("YOUR_NAME", "John Doe"))
    parser.add_argument("--your-email", default=os.getenv("YOUR_EMAIL", "john@example.com"))
    parser.add_argument("--topic", default="a guest post")

    parser.add_argument("--provider", default=os.getenv("LLM_PROVIDER", "gemini"))
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", "gemini-2.5-flash"))

    parser.add_argument("--serper-key", default=os.getenv("SERPER_API_KEY"))
    parser.add_argument("--firecrawl-key", default=os.getenv("FIRECRAWL_API_KEY"))
    parser.add_argument("--gemini-key", default=os.getenv("GEMINI_API_KEY"))
    parser.add_argument("--openai-key", default=os.getenv("OPENAI_API_KEY"))

    parser.add_argument("--take", type=int, default=5, help="Generate emails for top N rows with contact emails (fallback to others if fewer)")
    parser.add_argument("--urls", default="", help="Comma-separated URLs to use instead of search (for offline testing)")
    parser.add_argument("--out-csv", default="generated_emails_cli.csv", help="Path to save CSV output")

    args = parser.parse_args()

    def build_row_from_url(u: str) -> dict:
        page = scrape_website(u, args.firecrawl_key)
        md_text, html_text = _collect_page_text(page)
        # Excerpt
        raw_text = (md_text or "").strip()
        context_source = "firecrawl" if raw_text or html_text else "httpx"
        if not raw_text and html_text:
            raw_text = _strip_html_tags(html_text)
        if not raw_text:
            text_http, html_http = _http_fetch_text(u)
            raw_text = text_http
            html_text = html_http or html_text
        excerpt = _collapse_whitespace(raw_text)[:1500]
        # Emails / links
        emails = _extract_emails((md_text + "\n" + html_text))
        domain = urlparse(u).netloc
        best_email = _choose_best_email(emails, domain)
        links = _extract_links(html_text, u)
        g_url, c_url = _classify_support_links(links)
        row = {
            "url": u,
            "title": "",
            "contact_email": best_email,
            "contact_emails_all": ", ".join(emails[:5]) if emails else "",
            "contact_form_url": c_url,
            "guidelines_url": g_url,
            "domain": domain or u,
            "notes": "",
            "page_excerpt": excerpt,
            "context_source": context_source,
        }
        return row

    urls_override = [s.strip() for s in (args.urls or "").split(",") if s.strip()]
    if urls_override:
        logger.info("CLI: Phase 2 bypass (URLs provided): count={n}", n=len(urls_override))
        results = [build_row_from_url(u) for u in urls_override]
    else:
        logger.info("CLI: Phase 2 starting: keyword='{kw}' max_results={mr}", kw=args.keyword, mr=args.max_results)
        results = find_backlink_opportunities(
            args.keyword,
            serper_api_key=args.serper_key,
            firecrawl_api_key=args.firecrawl_key,
            max_results=args.max_results,
        )
    logger.info("CLI: Phase 2 done: results={n}", n=len(results))
    if not results:
        logger.warning("CLI: no results found")
        sys.exit(0)

    # Prefer rows with contact_email
    with_email = [r for r in results if r.get("contact_email")]
    others = [r for r in results if not r.get("contact_email")]
    selected = (with_email + others)[: args.take]

    logger.info(
        "CLI: Phase 3 starting: provider={prov} model={model} rows={rows}",
        prov=args.provider,
        model=args.model,
        rows=len(selected),
    )
    emails = generate_emails_for_rows(
        selected,
        subject=args.subject,
        your_name=args.your_name,
        your_email=args.your_email,
        proposed_topic=args.topic,
        provider=args.provider,
        model=args.model,
        gemini_api_key=args.gemini_key,
        openai_api_key=args.openai_key,
    )

    ok = sum(1 for e in emails if e["status"] == "ok")
    fb = sum(1 for e in emails if e["status"] == "fallback")
    er = sum(1 for e in emails if e["status"] == "error")
    logger.info("CLI: Phase 3 done: ok={ok} fallback={fb} error={er}", ok=ok, fb=fb, er=er)

    out_path = Path(args.out_csv)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "to_email",
                "subject",
                "body",
                "url",
                "domain",
                "title",
                "context_source",
                "excerpt_chars",
                "status",
                "note",
                "provider",
                "model",
            ],
        )
        writer.writeheader()
        for e in emails:
            writer.writerow(e)
    logger.info("CLI: wrote CSV -> {p}", p=str(out_path.resolve()))
