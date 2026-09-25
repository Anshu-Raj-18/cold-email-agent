from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.database import get_connection
from src.email_generator import get_salutation_name
from src.email_service import EmailService

def is_academic_research_target(email_addr: str, subject: str) -> bool:
    """Strict verification: Only allows follow-ups for verified research applications to academic institutes."""
    e = email_addr.lower().strip()
    s = subject.lower().strip()
    
    # Must be an academic or research domain
    academic_endings = [".ac.in", ".edu", ".ernet.in", ".res.in", ".org.in", "iisc.ac.in", "iiit.ac.in", "isb.edu", "iim"]
    if not any(dom in e for dom in academic_endings):
        return False
        
    # Block list for non-academic/personal
    blocked = ["zepto", "techmahindra", "visys", "zorvyn", "gmail.com", "yahoo", "support", "no-reply", "careers"]
    if any(b in e for b in blocked):
        return False
        
    return True

def check_pending_followups(days_threshold: int = 10, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Identifies applications eligible for follow-up:
    1. Sent >= days_threshold days ago with status 'Sent' or 'Waiting'.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT a.id as app_id, a.subject, a.sent_at, a.status,
           p.id as prof_id, p.name as prof_name, p.iit as institution, p.department, p.email as prof_email
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    WHERE a.status IN ('Sent', 'Waiting', 'Follow-up Required')
    """)
    rows = cursor.fetchall()
    
    now = datetime.now()
    eligible_followups = []
    
    for r in rows:
        prof_email = r["prof_email"] or ""
        subj = r["subject"] or ""
        
        if not is_academic_research_target(prof_email, subj):
            continue
            
        sent_at_str = r["sent_at"]
        if not sent_at_str:
            continue
            
        try:
            sent_time = datetime.fromisoformat(sent_at_str.replace(" ", "T"))
        except Exception:
            try:
                sent_time = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
                
        elapsed_days = (now - sent_time).days
        if elapsed_days >= days_threshold:
            cursor.execute("UPDATE applications SET status = 'Follow-up Required' WHERE id = ?", (r["app_id"],))
            eligible_followups.append({
                "application_id": r["app_id"],
                "professor_name": r["prof_name"],
                "institution": r["institution"],
                "email": r["prof_email"],
                "subject": r["subject"],
                "sent_at": sent_at_str,
                "days_elapsed": elapsed_days
            })
            
    conn.commit()
    conn.close()
    return eligible_followups

def generate_followup_email(
    candidate_name: str = "Anshu Raj",
    prof_name: str = "Professor",
    original_subject: str = "Application for Research Internship",
    sent_date_str: str = "recently",
    is_ooo_return: bool = False
) -> Dict[str, str]:
    """
    Generates a polite, respectful, and concise academic follow-up email.
    """
    salutation = get_salutation_name(prof_name)
    followup_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject
    opening = "I hope you are having a productive week."
        
    body = f"""Dear {salutation},

{opening}

I am writing to respectfully follow up on my previous email regarding my interest in research internship opportunities under your guidance. I understand that you have a demanding schedule, and I wanted to gently reiterate my enthusiasm for contributing to your research group.

My academic resume and personalized cover letter remain available for your review, and I would be very glad to discuss how my background in machine learning and computer vision could support your ongoing projects whenever convenient.

Thank you once again for your time and consideration.

Sincerely,

{candidate_name}"""

    return {
        "subject": followup_subject,
        "email_body": body
    }

def execute_due_followups(candidate_name: str = "Anshu Raj", days_threshold: int = 10) -> Dict[str, Any]:
    """
    Automatically sends polite academic follow-ups for verified research applications.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, p.name as prof_name, p.email as prof_email, p.iit as institution
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    WHERE a.status IN ('Sent', 'Waiting', 'Follow-up Required')
    """)
    rows = cursor.fetchall()
    
    now = datetime.now()
    sent_followups = []
    email_svc = EmailService()
    
    for r in rows:
        prof_email = r["prof_email"] or ""
        subj = r["subject"] or ""
        
        if not is_academic_research_target(prof_email, subj):
            continue
            
        sent_at_str = r["sent_at"]
        if not sent_at_str:
            continue
        try:
            sent_time = datetime.fromisoformat(sent_at_str.replace(" ", "T"))
        except Exception:
            try:
                sent_time = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
                
        elapsed_days = (now - sent_time).days
        if elapsed_days >= days_threshold:
            followup_content = generate_followup_email(
                candidate_name=candidate_name,
                prof_name=r["prof_name"],
                original_subject=r["subject"],
                sent_date_str=sent_at_str
            )
            
            auth_ok = email_svc.authenticate()
            if auth_ok:
                res = email_svc.send_email(r["prof_email"], followup_content["subject"], followup_content["email_body"])
                status_val = "Followed Up" if res.get("status") == "success" else "Follow-up Drafted"
            else:
                status_val = "Follow-up Drafted"
            
            cursor.execute("""
            UPDATE applications
            SET status = ?, followup_date = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (status_val, r["id"]))
            
            sent_followups.append({
                "application_id": r["id"],
                "professor_name": r["prof_name"],
                "institution": r["institution"],
                "email": r["prof_email"],
                "status": status_val,
                "days_elapsed": elapsed_days
            })
            
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "total_followups_sent": len(sent_followups),
        "followups": sent_followups,
        "message": f"Processed {len(sent_followups)} verified academic research follow-ups."
    }
