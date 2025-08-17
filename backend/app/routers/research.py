from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List
from loguru import logger

from app.models import (
    ResearchStartRequest,
    ResearchStartResponse,
    ResearchJobStatusResponse,
    ResearchResultRow,
)
from app.jobs import job_store

# Import core functions unchanged
from ai_backlinking import find_backlink_opportunities, scrape_website, _collect_page_text, _strip_html_tags, _collapse_whitespace, _extract_emails, _choose_best_email, _extract_links, _classify_support_links, _http_fetch_text  # type: ignore
from urllib.parse import urlparse
from pathlib import Path
import csv


router = APIRouter(prefix="/research", tags=["research"])


def _build_row_from_url(url: str, firecrawl_key: str | None) -> dict:
    page = scrape_website(url, firecrawl_key)
    md_text, html_text = _collect_page_text(page)
    raw_text = (md_text or "").strip()
    context_source = "firecrawl" if raw_text or html_text else "httpx"
    if not raw_text and html_text:
        raw_text = _strip_html_tags(html_text)
    if not raw_text:
        # HTTP fallback similar to CLI behavior
        text_http, html_http = _http_fetch_text(url)
        raw_text = text_http
        if html_http:
            html_text = html_http
    excerpt = _collapse_whitespace(raw_text)[:1500]
    emails = _extract_emails((md_text + "\n" + html_text))
    domain = urlparse(url).netloc
    best_email = _choose_best_email(emails, domain)
    links = _extract_links(html_text, url)
    g_url, c_url = _classify_support_links(links)
    return {
        "url": url,
        "title": "",
        "contact_email": best_email,
        "contact_emails_all": ", ".join(emails[:5]) if emails else "",
        "contact_form_url": c_url,
        "guidelines_url": g_url,
        "domain": domain or url,
        "notes": "",
        "page_excerpt": excerpt,
        "context_source": context_source,
    }


def _run_research(job_id: str, req: ResearchStartRequest) -> None:
    try:
        job_store.update(job_id, status="running", progress=0.05)
        results: List[dict]
        if req.urls:
            results = [_build_row_from_url(u, req.firecrawl_key) for u in req.urls]
        else:
            if not req.keyword:
                raise ValueError("keyword is required when urls are not provided")
            results = find_backlink_opportunities(
                req.keyword,
                serper_api_key=req.serper_key,
                firecrawl_api_key=req.firecrawl_key,
                max_results=req.max_results,
            )
        rows = [ResearchResultRow(**r) for r in results]
        saved_path: str | None = None
        try:
            # Determine output path: request param or default data/research_{job_id}.csv
            out_csv = req.out_csv
            if not out_csv:
                Path("data").mkdir(parents=True, exist_ok=True)
                out_csv = str(Path("data") / f"research_{job_id}.csv")
            out_file = Path(out_csv)
            if out_file.parent:
                out_file.parent.mkdir(parents=True, exist_ok=True)
            # Write with UTF-8 BOM so Excel shows content reliably
            with out_file.open("w", newline="", encoding="utf-8-sig") as f:
                fieldnames = [
                    "url",
                    "domain",
                    "title",
                    "contact_email",
                    "contact_emails_all",
                    "contact_form_url",
                    "guidelines_url",
                    "context_source",
                    "page_excerpt",
                ]
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    extrasaction="ignore",
                    quoting=csv.QUOTE_MINIMAL,
                    dialect="excel",
                )
                writer.writeheader()
                for r in rows:
                    rec = r.dict()
                    # Normalize values to strings and limit excerpt length
                    page_excerpt = (rec.get("page_excerpt") or "").replace("\r", " ").replace("\n", " ")[:1000]
                    row_out = {
                        "url": str(rec.get("url", "")),
                        "domain": str(rec.get("domain", "")),
                        "title": str(rec.get("title", "")),
                        "contact_email": str(rec.get("contact_email", "")),
                        "contact_emails_all": str(rec.get("contact_emails_all", "")),
                        "contact_form_url": str(rec.get("contact_form_url", "")),
                        "guidelines_url": str(rec.get("guidelines_url", "")),
                        "context_source": str(rec.get("context_source", "")),
                        "page_excerpt": page_excerpt,
                    }
                    writer.writerow(row_out)
                f.flush()
            saved_path = str(out_file.resolve())
        except Exception as exc:
            logger.warning(f"auto-save research CSV failed: {exc}")

        job_store.update(job_id, status="done", progress=1.0, result=rows if rows else [], meta={"saved_csv_path": saved_path})
    except Exception as exc:
        logger.error(f"research job failed: {exc}")
        job_store.update(job_id, status="error", error=str(exc))


@router.post("/start", response_model=ResearchStartResponse, summary="Start research job")
def start_research(req: ResearchStartRequest, bg: BackgroundTasks) -> ResearchStartResponse:
    job = job_store.create()
    bg.add_task(_run_research, job.job_id, req)
    return ResearchStartResponse(job_id=job.job_id)


@router.get("/status/{job_id}", response_model=ResearchJobStatusResponse, summary="Get research job status")
def research_status(job_id: str) -> ResearchJobStatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    # Compute saved CSV path if defaulting
    saved_csv_path = None
    if job.status == "done":
        saved_csv_path = (job.meta or {}).get("saved_csv_path")
        if not saved_csv_path:
            # Default save path convention
            default_path = Path("data") / f"research_{job_id}.csv"
            if default_path.exists():
                saved_csv_path = str(default_path.resolve())
    return ResearchJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        results=job.result if job.status == "done" else None,
        saved_csv_path=saved_csv_path,
    )


