import os
import sys
import time
import random
import logging
import argparse
from pathlib import Path
from typing import Dict, Any

from src.config import config
from src.email_service import EmailService
from src.database import get_connection, export_applications_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("bulk_sender")

INVALID_EMAIL_PATTERNS = [
    "professor@university.ac.in",
    "prof@university.ac.in",
    "email@institution.ac.in",
    "example@domain.com",
    "test@test.com",
    "none@none.com"
]

def is_valid_email(email_str: str) -> bool:
    if not email_str or not isinstance(email_str, str):
        return False
    clean = email_str.strip().lower()
    if "@" not in clean or "." not in clean:
        return False
    if clean in INVALID_EMAIL_PATTERNS:
        return False
    if clean.startswith("professor@") or clean.startswith("example@"):
        return False
    return True

def process_bulk_send(delay_min: float = 30.0, delay_max: float = 60.0, max_count: int = None):
    print("=" * 75, flush=True)
    print("   AUTOMATED BULK OUTREACH DISPATCH ENGINE", flush=True)
    print("   Sender: Anshu Raj (qismcdeltat@gmail.com)", flush=True)
    print(f"   Delay Range: {delay_min}s – {delay_max}s per email with random jitter", flush=True)
    print("=" * 75, flush=True)

    email_svc = EmailService()
    if not email_svc.authenticate():
        print("[ERROR] Gmail API OAuth authentication failed. Run 'python authenticate_gmail.py' first.", flush=True)
        return {"status": "error", "message": "Gmail API OAuth authentication failed."}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT a.id as app_id, a.subject, a.email_body, a.cover_letter_path, a.resume_path,
           p.email as prof_email, p.name as prof_name, p.iit as prof_institution
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    WHERE a.status = 'Email Drafted'
    ORDER BY a.id ASC
    """)
    pending = cursor.fetchall()

    if not pending:
        print("[INFO] No pending drafted applications found to send.", flush=True)
        conn.close()
        return {"status": "success", "message": "No pending applications to send.", "sent_count": 0}

    if max_count:
        pending = pending[:max_count]

    print(f"Found {len(pending)} pending applications ready for dispatch.\n", flush=True)

    sent_count = 0
    skipped_count = 0
    error_count = 0

    for idx, row in enumerate(pending, 1):
        app_id = row["app_id"]
        prof_name = row["prof_name"]
        prof_email = row["prof_email"]
        subject = row["subject"]
        body = row["email_body"]
        cover_path = row["cover_letter_path"]
        resume_path = row["resume_path"]

        if not is_valid_email(prof_email):
            skipped_count += 1
            print(f"[{idx}/{len(pending)}] [SKIPPED] ID #{app_id} | {prof_name} -> Invalid Email: '{prof_email}'", flush=True)
            continue

        attachments = [p for p in [cover_path, resume_path] if p and os.path.exists(p)]

        print(f"[{idx}/{len(pending)}] Sending to: {prof_name} ({prof_email}) | Subject: '{subject[:45]}...'", flush=True)
        
        res = email_svc.send_email(prof_email, subject, body, attachments=attachments)

        if res.get("status") == "success":
            msg_id = res.get("id")
            sent_count += 1
            cursor.execute("""
            UPDATE applications 
            SET status = 'Sent', approved_at = CURRENT_TIMESTAMP, sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (app_id,))
            conn.commit()
            export_applications_csv()
            print(f"       -> [SUCCESS] Gmail Msg ID: {msg_id} | Status updated to 'Sent'", flush=True)
        else:
            error_count += 1
            err_msg = res.get("error")
            print(f"       -> [ERROR] Dispatch Failed: {err_msg}", flush=True)

        if idx < len(pending):
            sleep_time = round(random.uniform(delay_min, delay_max), 2)
            print(f"       [WAIT] Sleeping for {sleep_time}s (anti-rate limit delay)...\n", flush=True)
            time.sleep(sleep_time)

    conn.close()
    
    summary = {
        "status": "success",
        "sent_count": sent_count,
        "skipped_count": skipped_count,
        "error_count": error_count,
        "message": f"Bulk dispatch finished: {sent_count} sent, {skipped_count} skipped, {error_count} failed."
    }
    
    print("\n" + "=" * 75, flush=True)
    print("   AUTOMATED BULK DISPATCH COMPLETED!", flush=True)
    print(f"   - Successfully Sent : {sent_count}", flush=True)
    print(f"   - Skipped (Invalid) : {skipped_count}", flush=True)
    print(f"   - Failed Errors     : {error_count}", flush=True)
    print(f"   - Tracking CSV      : data/applications.csv", flush=True)
    print("=" * 75, flush=True)
    
    return summary

def parse_args():
    parser = argparse.ArgumentParser(description="Automated Bulk Outreach Sender for ColdMailer")
    parser.add_argument("--delay-min", type=float, default=30.0, help="Minimum delay in seconds between emails (default: 30.0)")
    parser.add_argument("--delay-max", type=float, default=60.0, help="Maximum delay in seconds between emails (default: 60.0)")
    parser.add_argument("--max-count", type=int, default=None, help="Maximum number of emails to send in this run")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    process_bulk_send(delay_min=args.delay_min, delay_max=args.delay_max, max_count=args.max_count)
