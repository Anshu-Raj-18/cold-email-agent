import os
import re
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from src.database import get_connection
from src.notifier import notify_professor_reply, notify_ooo_detected, notify_bounce_quarantined
from src.gmail_sender import load_env_file

def decode_mime_words(raw_header: Optional[str]) -> str:
    if not raw_header:
        return ""
    decoded_parts = decode_header(raw_header)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            result.append(str(part))
    return " ".join(result)

def extract_body_snippet(msg: email.message.Message, max_len: int = 400) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdisp:
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='ignore')
            
    clean_lines = [line.strip() for line in body.splitlines() if line.strip() and not line.strip().startswith(">")]
    full_clean = " ".join(clean_lines)
    return full_clean[:max_len] + ("..." if len(full_clean) > max_len else "")

def extract_ooo_return_date(text: str) -> Optional[str]:
    """
    Intelligently extracts out-of-office return dates (e.g. 'until August 24th', 'back on Aug 25', 'until 25 August').
    """
    patterns = [
        r'(?:until|till|back on|returning on|return on|after)\s+([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?',
        r'(?:until|till|back on|returning on|return on|after)\s+(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)',
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})'
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            if len(groups) == 2:
                if groups[0].isalpha():
                    month_str, day_str = groups[0], groups[1]
                else:
                    day_str, month_str = groups[0], groups[1]
                try:
                    dt = datetime.strptime(f'{day_str} {month_str} 2026', '%d %B %Y')
                    return dt.strftime('%Y-%m-%d')
                except Exception:
                    try:
                        dt = datetime.strptime(f'{day_str} {month_str} 2026', '%d %b %Y')
                        return dt.strftime('%Y-%m-%d')
                    except Exception:
                        pass
    return None

def extract_bounced_email(text: str) -> Optional[str]:
    """Extracts failed recipient from delivery failure notification text."""
    patterns = [
        r'wasn\'t delivered to\s+([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',
        r'failed recipient:\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)',
        r'<([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+)>:\s*550'
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).lower().strip()
    return None

def scan_inbox_for_professor_replies() -> Dict[str, Any]:
    """
    Scans Gmail inbox via IMAP SSL to:
    1. Detect real professor replies (updates status to 'Replied' or 'Interested' and sends Discord notification).
    2. Extract OOO return dates (e.g. 'until Aug 24' -> schedules resume date and alerts Discord).
    3. Quarantine bounced/invalid email domains and notifies Discord.
    """
    load_env_file()
    user_email = os.getenv("GMAIL_USER", "adepunikhil79@gmail.com")
    raw_pass = os.getenv("GMAIL_APP_PASSWORD", "")
    secret_pass = raw_pass.replace(" ", "").strip()
    
    if not secret_pass:
        return {
            "status": "dry_run",
            "message": "GMAIL_APP_PASSWORD not configured. Skipping live inbox scanning.",
            "detected_replies": [],
            "bounced_emails": [],
            "ooo_schedules": []
        }
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, iit as institution FROM professors")
    tracked_profs = {row["email"].lower(): row for row in cursor.fetchall()}
    
    detected_replies = []
    bounced_emails = []
    ooo_schedules = []
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(user_email, secret_pass)
        mail.select("INBOX")
        
        since_date = (datetime.now() - timedelta(days=14)).strftime("%d-%b-%Y")
        status, search_data = mail.search(None, f'(SINCE "{since_date}")')
        
        if status == 'OK' and search_data[0]:
            msg_ids = search_data[0].split()
            for msg_id in msg_ids[-100:]:
                res, data = mail.fetch(msg_id, "(RFC822)")
                if res != 'OK' or not data or not data[0]:
                    continue
                    
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                from_hdr = decode_mime_words(msg.get("From"))
                subject_hdr = decode_mime_words(msg.get("Subject"))
                
                sender_email = ""
                if "<" in from_hdr and ">" in from_hdr:
                    sender_email = from_hdr.split("<")[-1].split(">")[0].strip().lower()
                else:
                    sender_email = from_hdr.strip().lower()
                    
                body_snippet = extract_body_snippet(msg)
                
                # 1. Check for Bounce / Delivery Failure
                if "mailer-daemon" in sender_email or "postmaster" in sender_email or "Delivery Status Notification" in subject_hdr:
                    failed_recipient = extract_bounced_email(body_snippet)
                    if failed_recipient and failed_recipient in tracked_profs:
                        cursor.execute("""
                        UPDATE applications
                        SET status = 'Bounced / Invalid Email', notes = 'Domain or mailbox not found', response_type = 'Bounce', response_date = CURRENT_TIMESTAMP
                        WHERE professor_id IN (SELECT id FROM professors WHERE email = ?)
                        """, (failed_recipient,))
                        bounced_emails.append(failed_recipient)
                        notify_bounce_quarantined(failed_recipient)
                    continue
                    
                # 2. Check for Tracked Professor or Application Subject
                is_tracked_prof = sender_email in tracked_profs
                is_app_reply = "application for research internship" in subject_hdr.lower() or "re: application" in subject_hdr.lower()
                
                if is_tracked_prof or is_app_reply:
                    prof_info = tracked_profs.get(sender_email, {
                        "name": from_hdr.split("<")[0].strip() or "Professor",
                        "institution": "National Institute"
                    })
                    
                    # Check for Out of Office (OOO)
                    is_ooo = "automatic reply" in subject_hdr.lower() or "out of office" in subject_hdr.lower() or "away" in body_snippet.lower() or "travel" in body_snippet.lower()
                    return_date = extract_ooo_return_date(body_snippet) if is_ooo else None
                    
                    if is_ooo and return_date:
                        cursor.execute("""
                        UPDATE applications
                        SET status = ?, available_after = ?, response = ?, response_type = 'OOO', response_date = CURRENT_TIMESTAMP
                        WHERE professor_id IN (SELECT id FROM professors WHERE email = ?)
                        """, (f"OOO (Returns {return_date})", return_date, body_snippet, sender_email))
                        
                        notify_ooo_detected(
                            professor_name=prof_info['name'],
                            institution=prof_info.get('institution', 'National Institute'),
                            email_addr=sender_email,
                            return_date=return_date,
                            snippet=body_snippet
                        )
                        
                        ooo_schedules.append({
                            "professor_name": prof_info["name"],
                            "email": sender_email,
                            "return_date": return_date,
                            "snippet": body_snippet
                        })
                    else:
                        snippet_lower = body_snippet.lower()
                        interested_keywords = ["interview", "discuss", "meet", "schedule", "opportunity", "shortlisted", "join", "cv", "resume", "available", "welcome"]
                        is_interested = any(kw in snippet_lower for kw in interested_keywords) and "not part of" not in snippet_lower
                        new_status = "Interested" if is_interested else "Replied"
                        
                        cursor.execute("""
                        UPDATE applications
                        SET status = ?, response = ?, response_type = 'Reply', response_date = CURRENT_TIMESTAMP
                        WHERE professor_id IN (SELECT id FROM professors WHERE email = ?)
                        """, (new_status, body_snippet, sender_email))
                        
                        notify_professor_reply(
                            professor_name=prof_info['name'],
                            institution=prof_info.get('institution', 'National Institute'),
                            email_addr=sender_email,
                            snippet=body_snippet,
                            status=new_status
                        )
                        
                        detected_replies.append({
                            "professor_name": prof_info["name"],
                            "email": sender_email,
                            "subject": subject_hdr,
                            "status": new_status,
                            "snippet": body_snippet
                        })
                        
        mail.close()
        mail.logout()
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "total_replies": len(detected_replies),
            "total_bounces_quarantined": len(bounced_emails),
            "total_ooo_scheduled": len(ooo_schedules),
            "replies": detected_replies,
            "bounced_emails": bounced_emails,
            "ooo_schedules": ooo_schedules
        }
    except Exception as e:
        conn.close()
        return {
            "status": "error",
            "message": f"Inbox scan failed: {str(e)}",
            "detected_replies": []
        }
