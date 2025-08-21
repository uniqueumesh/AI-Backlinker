"""
CSV handling utilities for send outcomes
"""
from pathlib import Path
import csv
from loguru import logger
from typing import List

def save_send_outcomes(results: List[dict], out_csv: str) -> str | None:
    """
    Save send operation outcomes to CSV file.
    
    Args:
        results: List of send operation results
        out_csv: Output CSV path
        
    Returns:
        str | None: Path to saved CSV file, or None if failed
    """
    saved_path: str | None = None
    try:
        out_file = Path(out_csv)
        if out_file.parent:
            out_file.parent.mkdir(parents=True, exist_ok=True)
        with out_file.open("w", newline="", encoding="utf-8-sig") as f:
            fieldnames = ["row", "to_email", "status", "code", "message"]
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                extrasaction="ignore",
                quoting=csv.QUOTE_MINIMAL,
                dialect="excel",
            )
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "row": r.get("row", ""),
                    "to_email": r.get("to_email", ""),
                    "status": r.get("status", ""),
                    "code": r.get("code", ""),
                    "message": r.get("message", ""),
                })
        saved_path = str(out_file.resolve())
    except Exception as exc:
        logger.warning(f"auto-save send outcomes CSV failed: {exc}")
    
    return saved_path
