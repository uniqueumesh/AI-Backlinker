from typing import Optional, List
from pydantic import BaseModel, Field


class ResearchStartRequest(BaseModel):
    keyword: Optional[str] = Field(None, description="Seed keyword for research")
    max_results: int = Field(10, ge=1, le=50)
    urls: Optional[List[str]] = Field(None, description="Override: scrape these URLs instead of searching")

    # Optional API keys per request (or rely on env)
    serper_key: Optional[str] = None
    firecrawl_key: Optional[str] = None

    # Optional CSV output path; if not set, defaults to data/research_{job_id}.csv
    out_csv: Optional[str] = Field(None, description="Optional path to auto-save results as CSV")


class ResearchResultRow(BaseModel):
    url: str
    title: str = ""
    contact_email: str = ""
    contact_emails_all: str = ""
    contact_form_url: str = ""
    guidelines_url: str = ""
    domain: str = ""
    notes: str = ""
    page_excerpt: str = ""
    context_source: str = ""


class ResearchStartResponse(BaseModel):
    job_id: str


class ResearchJobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    error: Optional[str] = None
    results: Optional[List[ResearchResultRow]] = None
    saved_csv_path: Optional[str] = None


# Phase 3: Email generation

class EmailGenerateStartRequest(BaseModel):
    # Source of rows to generate from
    research_job_id: Optional[str] = Field(None, description="Use results from a completed research job")
    rows: Optional[List[ResearchResultRow]] = Field(None, description="Alternatively, provide rows directly")
    selected_urls: Optional[List[str]] = Field(None, description="Optional: limit to these URLs from the research results")

    # Email parameters
    subject: str = Field("Guest post collaboration")
    your_name: str = Field("John Doe")
    your_email: str = Field("john@example.com")
    topic: Optional[str] = Field(None, description="Proposed topic (optional)")
    take: int = Field(5, ge=1, le=100)

    # LLM config
    provider: str = Field("gemini")
    model: Optional[str] = Field(None)


class EmailRow(BaseModel):
    to_email: str
    subject: str
    body: str
    url: str
    domain: str
    title: str
    context_source: str
    excerpt_chars: int
    status: str
    note: str
    provider: str
    model: str


class EmailGenerateStartResponse(BaseModel):
    job_id: str


class EmailGenerateStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    error: Optional[str] = None
    results: Optional[List[EmailRow]] = None
    saved_csv_path: Optional[str] = None


# Phase 4: Sending

class SendEmailRow(BaseModel):
    to_email: str
    subject: str
    body: str


class SendStartRequest(BaseModel):
    provider: str = Field("smtp", description="sendgrid | mailersend | smtp")
    from_email: str

    # Input source
    in_csv: Optional[str] = Field(None, description="Path to CSV with to_email,subject,body")
    rows: Optional[List[SendEmailRow]] = Field(None, description="Inline rows to send if no CSV provided")

    rate_limit_per_sec: float = Field(10.0, ge=0.1, le=100.0)
    dry_run: bool = False

    # Provider-specific (optional - will use environment variables for SMTP)
    sandbox: Optional[bool] = Field(None, description="SendGrid sandbox mode")
    sendgrid_key: Optional[str] = None
    mailersend_key: Optional[str] = None

    # SMTP fields are now optional - will use environment variables if not provided
    smtp_host: Optional[str] = Field(None, description="SMTP server (optional - uses SMTP_HOST from .env)")
    smtp_port: Optional[int] = Field(None, description="SMTP port (optional - uses SMTP_PORT from .env)")
    smtp_user: Optional[str] = Field(None, description="SMTP username (optional - uses SMTP_USER from .env)")
    smtp_pass: Optional[str] = Field(None, description="SMTP password (optional - uses SMTP_PASS from .env)")

    # Output
    out_csv: Optional[str] = Field(None, description="Where to save outcomes CSV (default data/send_{job_id}.csv)")


class SendStartResponse(BaseModel):
    job_id: str


class SendStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    error: Optional[str] = None
    results: Optional[List[dict]] = None
    saved_csv_path: Optional[str] = None


