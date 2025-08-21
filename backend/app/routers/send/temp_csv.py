"""
Temporary CSV creation for send operations
"""
from pathlib import Path
import csv
from typing import List

def _write_rows_to_temp_csv(rows: List[dict], job_id: str) -> Path:
    """
    Write rows to a temporary CSV file for sending.
    
    Args:
        rows: List of email rows to send
        job_id: Job ID for file naming
        
    Returns:
        Path: Path to created temporary CSV file
    """
    Path("data").mkdir(parents=True, exist_ok=True)
    temp_path = Path("data") / f"send_input_{job_id}.csv"
    with temp_path.open("w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["to_email", "subject", "body"]
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,
            dialect="excel",
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({
                "to_email": (r.get("to_email") or "").strip(),
                "subject": r.get("subject") or "",
                "body": (r.get("body") or "").replace("\r"," ").replace("\n"," "),
            })
    return temp_path
