"""
AI Backlinker Core - Main orchestration and workflow management.

This module coordinates the main workflow for finding backlink opportunities,
generating personalized emails, and managing the overall process.
"""

import os
import sys
import csv
import argparse
from pathlib import Path
from loguru import logger

from .scraping import find_backlink_opportunities
from .emails import generate_emails_for_rows
from .utils import setup_logger, build_row_from_url


def main():
    """Main CLI entry point for the AI Backlinker."""
    setup_logger()
    
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
    parser.add_argument("--out-results", default="", help="Optional path to save Phase 2 scraped results as CSV")
    parser.add_argument("--in-results", default="", help="Optional path to load Phase 2 results from CSV (skip search)")

    args = parser.parse_args()

    urls_override = [s.strip() for s in (args.urls or "").split(",") if s.strip()]
    if urls_override:
        logger.info("CLI: Phase 2 bypass (URLs provided): count={n}", n=len(urls_override))
        results = [build_row_from_url(u, args.firecrawl_key) for u in urls_override]
    elif args.in_results:
        in_path = Path(args.in_results)
        if not in_path.exists():
            logger.warning("CLI: --in-results provided but file not found: {p}", p=str(in_path))
            results = []
        else:
            try:
                with in_path.open("r", encoding="utf-8") as rf:
                    reader = csv.DictReader(rf)
                    loaded: list[dict] = []
                    for row in reader:
                        loaded.append({
                            "url": row.get("url", ""),
                            "domain": row.get("domain", ""),
                            "title": row.get("title", ""),
                            "contact_email": row.get("contact_email", ""),
                            "contact_emails_all": row.get("contact_emails_all", ""),
                            "contact_form_url": row.get("contact_form_url", ""),
                            "guidelines_url": row.get("guidelines_url", ""),
                            "context_source": row.get("context_source", "loaded"),
                            "page_excerpt": row.get("page_excerpt", ""),
                            "notes": row.get("notes", ""),
                        })
                logger.info("CLI: Phase 2 loaded from CSV: rows={n} file={p}", n=len(loaded), p=str(in_path))
                results = loaded
            except Exception as _exc:
                logger.warning(f"CLI: failed to load --in-results CSV: {_exc}")
                results = []
    else:
        logger.info("CLI: Phase 2 starting: keyword='{kw}' max_results={mr}", kw=args.keyword, mr=args.max_results)
        results = find_backlink_opportunities(
            args.keyword,
            serper_api_key=args.serper_key,
            firecrawl_api_key=args.firecrawl_key,
            max_results=args.max_results,
        )
    logger.info("CLI: Phase 2 done: results={n}", n=len(results))

    # Optionally write Phase 2 results to CSV for inspection/debugging
    if args.out_results:
        try:
            rp = Path(args.out_results)
            if rp.parent and not rp.parent.exists():
                rp.parent.mkdir(parents=True, exist_ok=True)
            with rp.open("w", newline="", encoding="utf-8") as rf:
                rwriter = csv.DictWriter(
                    rf,
                    fieldnames=[
                        "url",
                        "domain",
                        "title",
                        "contact_email",
                        "contact_emails_all",
                        "contact_form_url",
                        "guidelines_url",
                        "context_source",
                        "page_excerpt",
                    ],
                )
                rwriter.writeheader()
                for r in results:
                    rwriter.writerow({
                        "url": r.get("url", ""),
                        "domain": r.get("domain", ""),
                        "title": r.get("title", ""),
                        "contact_email": r.get("contact_email", ""),
                        "contact_emails_all": r.get("contact_emails_all", ""),
                        "contact_form_url": r.get("contact_form_url", ""),
                        "guidelines_url": r.get("guidelines_url", ""),
                        "context_source": r.get("context_source", ""),
                        "page_excerpt": r.get("page_excerpt", ""),
                    })
            logger.info("CLI: wrote Phase 2 results CSV -> {p}", p=str(rp.resolve()))
        except Exception as _exc:
            logger.warning(f"CLI: failed to write Phase 2 results CSV: {_exc}")

    if not results:
        logger.warning("CLI: no results found. If offline or missing SERPER_API_KEY, use --urls for offline test or set SERPER_API_KEY.")
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
    # Ensure parent directory exists
    try:
        if out_path.parent and not out_path.parent.exists():
            out_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as _exc:
        logger.warning(f"CLI: could not ensure output directory exists: {_exc}")
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


if __name__ == "__main__":  # pragma: no cover
    main()
