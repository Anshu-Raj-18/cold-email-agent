import os
import json
import email
from email.header import decode_header
import imaplib
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.database import (
    init_db,
    seed_candidate_profile,
    get_candidate_profile,
    insert_or_update_professor,
    has_contacted_professor,
    save_match,
    create_application_record,
    clean_duplicate_applications,
    get_connection,
    export_professors_csv,
    export_applications_csv
)
from src.scraper import discover_professors, INSTITUTE_FULL_NAMES
from src.matching_engine import calculate_match_score
from src.email_generator import generate_application_package_content
from src.pdf_generator import generate_cover_letter_pdf, DEFAULT_OUTPUT_DIR
from src.email_service import EmailService
from src.followup_engine import generate_followup_email

app = FastAPI(
    title="AI-Powered National Professor Research Matching & Cold Email Agent",
    version="2.5.0"
)

os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
app.mount("/generated_cover_letters", StaticFiles(directory=DEFAULT_OUTPUT_DIR), name="cover_letters")

def decode_mime_header(header_val: str) -> str:
    if not header_val:
        return ""
    decoded_fragments = decode_header(header_val)
    header_text = ""
    for fragment, encoding in decoded_fragments:
        if isinstance(fragment, bytes):
            header_text += fragment.decode(encoding or "utf-8", errors="replace")
        else:
            header_text += str(fragment)
    return header_text

def heal_missing_application_data():
    """Self-healing backfill function for missing match data and email bodies."""
    cand = get_candidate_profile()
    if not cand:
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id as app_id, a.professor_id, a.match_id, a.subject, a.email_body, a.cover_letter_path,
           p.id as prof_id, p.name, p.iit, p.department, p.designation, p.email, p.research_areas, p.research_summary
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    """)
    apps = cursor.fetchall()

    for app_row in apps:
        prof_id = app_row["prof_id"]
        match_id = app_row["match_id"]
        email_body = app_row["email_body"]
        subject = app_row["subject"]

        # 1. Backfill match_id and match record if missing
        if not match_id:
            cursor.execute("SELECT id FROM matches WHERE professor_id = ? ORDER BY id DESC LIMIT 1", (prof_id,))
            m_row = cursor.fetchone()
            if m_row:
                match_id = m_row["id"]
            else:
                try:
                    r_areas = json.loads(app_row["research_areas"]) if app_row["research_areas"].startswith("[") else app_row["research_areas"]
                except Exception:
                    r_areas = app_row["research_areas"]
                prof_dict = {
                    "name": app_row["name"],
                    "institution": app_row["iit"],
                    "department": app_row["department"],
                    "research_areas": r_areas,
                    "research_summary": app_row["research_summary"] or ""
                }
                match_res = calculate_match_score(cand, prof_dict)
                match_id = save_match({
                    "candidate_id": cand["id"],
                    "professor_id": prof_id,
                    "research_score": match_res["research_score"],
                    "technical_score": match_res["technical_score"],
                    "project_score": match_res["project_score"],
                    "recent_research_score": match_res["recent_research_score"],
                    "background_score": match_res["background_score"],
                    "total_score": match_res["total_score"],
                    "match_reason": match_res["match_reason"],
                    "gaps": match_res["gaps"]
                })
            cursor.execute("UPDATE applications SET match_id = ? WHERE id = ?", (match_id, app_row["app_id"]))

        # 2. Backfill email_body if missing
        if not email_body or str(email_body).strip() in ["", "None"]:
            try:
                r_areas = json.loads(app_row["research_areas"]) if app_row["research_areas"].startswith("[") else app_row["research_areas"]
            except Exception:
                r_areas = app_row["research_areas"]
            prof_dict = {
                "name": app_row["name"],
                "institution": app_row["iit"],
                "department": app_row["department"],
                "email": app_row["email"],
                "research_areas": r_areas,
                "lab_name": f"{app_row['name']} Research Group"
            }
            pkg = generate_application_package_content(cand, prof_dict)
            cursor.execute("""
            UPDATE applications 
            SET email_body = ?, subject = COALESCE(NULLIF(subject, ''), ?)
            WHERE id = ?
            """, (pkg["email_body"], pkg["subject"], app_row["app_id"]))

    conn.commit()
    conn.close()
    export_professors_csv()
    export_applications_csv()

@app.on_event("startup")
def on_startup():
    init_db()
    clean_duplicate_applications()
    cand = get_candidate_profile()
    if not cand:
        profile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "candidate_profile.json")
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                seed_candidate_profile(json.load(f))
    heal_missing_application_data()

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "National Research Cold Email Agent"}

@app.get("/api/candidate")
def get_candidate():
    cand = get_candidate_profile()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
    return cand

@app.post("/api/db/clean-duplicates")
def clean_duplicates():
    count = clean_duplicate_applications()
    heal_missing_application_data()
    return {"status": "success", "removed_duplicates": count}

class DiscoverRequest(BaseModel):
    institution_type: Optional[str] = "ALL"
    institution_name: Optional[str] = None
    iit: Optional[str] = None
    research: Optional[str] = "Machine Learning Computer Vision Deep Learning"
    threshold: Optional[float] = 70.0

@app.post("/api/professors/discover-and-rank")
def discover_and_rank_professors(req: DiscoverRequest):
    cand = get_candidate_profile()
    if not cand:
        raise HTTPException(status_code=400, detail="Candidate profile not configured.")

    inst_name = req.institution_name or req.iit
    profs = discover_professors(
        institution_type=req.institution_type,
        institution_name=inst_name,
        research_filter=req.research
    )
    ranked = []

    for prof in profs:
        prof_id = insert_or_update_professor(prof)
        match_result = calculate_match_score(cand, prof, threshold=req.threshold)
        already_contacted = has_contacted_professor(prof["email"])
        
        match_id = save_match({
            "candidate_id": cand["id"],
            "professor_id": prof_id,
            "research_score": match_result["research_score"],
            "technical_score": match_result["technical_score"],
            "project_score": match_result["project_score"],
            "recent_research_score": match_result["recent_research_score"],
            "background_score": match_result["background_score"],
            "total_score": match_result["total_score"],
            "match_reason": match_result["match_reason"],
            "gaps": match_result["gaps"]
        })

        inst_val = prof.get("institution", prof.get("iit", "Institute"))
        inst_type_val = prof.get("institution_type", "IIT")

        ranked.append({
            "professor_id": prof_id,
            "match_id": match_id,
            "name": prof["name"],
            "institution": inst_val,
            "institution_type": inst_type_val,
            "iit": inst_val,
            "department": prof["department"],
            "email": prof["email"],
            "research_areas": prof["research_areas"],
            "recent_papers": prof.get("recent_papers", []),
            "total_score": match_result["total_score"],
            "category": match_result["category"],
            "is_shortlisted": match_result["is_shortlisted"],
            "already_contacted": already_contacted,
            "match_breakdown": {
                "research": f"{match_result['research_score']}/40",
                "technical": f"{match_result['technical_score']}/25",
                "project": f"{match_result['project_score']}/20",
                "paper_synergy": f"{match_result['recent_research_score']}/10",
                "background": f"{match_result['background_score']}/5"
            },
            "why_matched": match_result["match_reason"],
            "gaps": match_result["gaps"],
            "aligned_papers": match_result.get("aligned_papers", [])
        })

    ranked.sort(key=lambda x: x["total_score"], reverse=True)
    export_professors_csv()
    return {
        "total_discovered": len(profs),
        "shortlisted_count": sum(1 for r in ranked if r["is_shortlisted"]),
        "professors": ranked
    }

class PreparePackageRequest(BaseModel):
    professor_id: int
    match_id: Optional[int] = None

@app.post("/api/application/prepare")
def prepare_application_package(req: PreparePackageRequest):
    cand = get_candidate_profile()
    if not cand:
        raise HTTPException(status_code=400, detail="Candidate profile not loaded.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM professors WHERE id = ?", (req.professor_id,))
    prof_row = cursor.fetchone()
    conn.close()

    if not prof_row:
        raise HTTPException(status_code=404, detail="Professor not found.")

    try:
        r_areas = json.loads(prof_row["research_areas"]) if prof_row["research_areas"].startswith("[") else prof_row["research_areas"]
    except Exception:
        r_areas = prof_row["research_areas"]

    prof_data = {
        "name": prof_row["name"],
        "institution": prof_row["iit"],
        "department": prof_row["department"],
        "designation": prof_row["designation"],
        "email": prof_row["email"],
        "location": "India",
        "research_areas": r_areas,
        "lab_name": f"{prof_row['name']} Research Group"
    }

    for p in discover_professors(institution_type="ALL"):
        if p["email"] == prof_row["email"]:
            if "lab_name" in p:
                prof_data["lab_name"] = p["lab_name"]
            if "location" in p:
                prof_data["location"] = p["location"]
            if "full_institution_name" in p:
                prof_data["full_institution_name"] = p["full_institution_name"]
            if "recent_papers" in p:
                prof_data["recent_papers"] = p["recent_papers"]
            break

    if "full_institution_name" not in prof_data:
        prof_data["full_institution_name"] = INSTITUTE_FULL_NAMES.get(prof_data["institution"], prof_data["institution"])

    pkg_content = generate_application_package_content(cand, prof_data)
    pdf_path = generate_cover_letter_pdf(pkg_content["cover_letter_data"], output_dir=DEFAULT_OUTPUT_DIR)

    resume_filename = cand.get("resume_path", "Anshu_Raj_Resume.pdf")
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    resume_full_path = os.path.join(assets_dir, resume_filename)

    app_id = create_application_record({
        "professor_id": req.professor_id,
        "match_id": req.match_id,
        "subject": pkg_content["subject"],
        "email_body": pkg_content["email_body"],
        "cover_letter_path": pdf_path,
        "resume_path": resume_full_path
    })

    pdf_filename = os.path.basename(pdf_path)
    return {
        "application_id": app_id,
        "professor_name": prof_data["name"],
        "professor_email": prof_data["email"],
        "subject": pkg_content["subject"],
        "email_body": pkg_content["email_body"],
        "cover_letter_pdf": pdf_path,
        "cover_letter_url": f"/generated_cover_letters/{pdf_filename}",
        "constant_resume_pdf": resume_full_path,
        "status": "Email Drafted - Awaiting Human Approval"
    }

class PrepareAllPackagesRequest(BaseModel):
    institution_type: Optional[str] = "ALL"
    threshold: Optional[float] = 70.0
    research: Optional[str] = "Machine Learning Computer Vision Deep Learning"

@app.post("/api/applications/prepare-all")
def prepare_all_application_packages(req: PrepareAllPackagesRequest):
    cand = get_candidate_profile()
    if not cand:
        raise HTTPException(status_code=400, detail="Candidate profile not loaded.")

    disc_res = discover_and_rank_professors(DiscoverRequest(
        institution_type=req.institution_type,
        threshold=req.threshold,
        research=req.research
    ))

    prepared_count = 0
    for prof in disc_res.get("professors", []):
        if prof.get("is_shortlisted"):
            prepare_application_package(PreparePackageRequest(
                professor_id=prof["professor_id"],
                match_id=prof.get("match_id")
            ))
            prepared_count += 1

    return {
        "status": "success",
        "message": f"Successfully prepared {prepared_count} application packages for shortlisted faculty.",
        "prepared_count": prepared_count
    }

class SendApplicationRequest(BaseModel):
    application_id: int
    user_approved: bool
    edited_subject: Optional[str] = None
    edited_body: Optional[str] = None

@app.post("/api/application/send")
def send_application(req: SendApplicationRequest):
    if not req.user_approved:
        raise HTTPException(status_code=400, detail="User approval required before sending.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, p.email as prof_email, p.name as prof_name, p.iit as prof_institution, p.department as prof_dept, p.research_areas
    FROM applications a 
    JOIN professors p ON a.professor_id = p.id 
    WHERE a.id = ?
    """, (req.application_id,))
    app_row = cursor.fetchone()

    if not app_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Application not found.")

    subject = req.edited_subject or app_row["subject"]
    body = req.edited_body or app_row["email_body"]
    to_email = app_row["prof_email"]

    if not body or str(body).strip() in ["", "None"] or not subject:
        cand = get_candidate_profile()
        try:
            r_areas = json.loads(app_row["research_areas"]) if app_row["research_areas"].startswith("[") else app_row["research_areas"]
        except Exception:
            r_areas = app_row["research_areas"]
        prof_dict = {
            "name": app_row["prof_name"],
            "institution": app_row["prof_institution"],
            "department": app_row["prof_dept"],
            "email": app_row["prof_email"],
            "research_areas": r_areas,
            "lab_name": f"{app_row['prof_name']} Research Group"
        }
        pkg = generate_application_package_content(cand, prof_dict)
        subject = subject or pkg["subject"]
        body = body or pkg["email_body"]

    cover_letter_path = app_row["cover_letter_path"]
    resume_path = app_row["resume_path"]

    email_svc = EmailService()
    auth_ok = email_svc.authenticate()
    if not auth_ok:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Gmail API OAuth authentication required. Run 'python authenticate_gmail.py' to generate token.json."
        )

    attachments = [p for p in [cover_letter_path, resume_path] if p and os.path.exists(p)]
    res = email_svc.send_email(to_email, subject, body, attachments=attachments)

    if res.get("status") == "success":
        cursor.execute("""
        UPDATE applications 
        SET status = 'Sent', subject = ?, email_body = ?, approved_at = CURRENT_TIMESTAMP, sent_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """, (subject, body, req.application_id))
        conn.commit()
        conn.close()
        export_applications_csv()
        return {
            "status": "success",
            "message": f"Successfully sent email via Gmail API! Message ID: {res.get('id')}",
            "recipient": to_email,
            "application_id": req.application_id,
            "application_status": "Sent"
        }
    else:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Gmail API Error: {res.get('error')}")

@app.post("/api/applications/reset-pending")
def reset_all_to_pending():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = 'Email Drafted', sent_at = NULL, approved_at = NULL")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    export_applications_csv()
    return {"status": "success", "message": f"Reset {count} applications back to 'Email Drafted' (Pending).", "reset_count": count}

class SendAllPendingRequest(BaseModel):
    delay_min: Optional[float] = 10.0
    delay_max: Optional[float] = 20.0
    max_count: Optional[int] = None

@app.post("/api/applications/send-all-pending")
def send_all_pending(req: SendAllPendingRequest):
    from send_all import process_bulk_send
    res = process_bulk_send(
        delay_min=req.delay_min or 10.0,
        delay_max=req.delay_max or 20.0,
        max_count=req.max_count
    )
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message"))
    return res

@app.post("/api/application/reset-single/{app_id}")
def reset_single_to_pending(app_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = 'Email Drafted', sent_at = NULL, approved_at = NULL WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()
    export_applications_csv()
    return {"status": "success", "message": f"Application #{app_id} reset back to 'Email Drafted'."}

@app.get("/api/applications/tracker")
def list_applications():
    heal_missing_application_data()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id, p.name as professor_name, p.iit as institution, p.department, p.email,
           COALESCE(m.total_score, m_fallback.total_score) as match_score, 
           a.subject, a.status, a.drafted_at, a.sent_at
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    LEFT JOIN matches m ON a.match_id = m.id
    LEFT JOIN matches m_fallback ON m_fallback.id = (SELECT MAX(id) FROM matches WHERE professor_id = p.id)
    WHERE a.id IN (SELECT MAX(id) FROM applications GROUP BY professor_id)
    ORDER BY a.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    tracker = []
    for r in rows:
        inst_val = r["institution"]
        tracker.append({
            "application_id": r["id"],
            "professor": r["professor_name"],
            "institution": inst_val,
            "iit": inst_val,
            "department": r["department"],
            "email": r["email"],
            "match_score": f"{r['match_score']:.1f}%" if r["match_score"] is not None else "N/A",
            "subject": r["subject"],
            "status": r["status"],
            "drafted_at": r["drafted_at"],
            "sent_at": r["sent_at"]
        })
    return {"applications": tracker}

@app.get("/dashboard", response_class=HTMLResponse)
def review_dashboard():
    heal_missing_application_data()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id as app_id, a.subject, a.email_body, a.cover_letter_path, a.status, a.sent_at,
           p.name as prof_name, p.iit as institution, p.department, p.email as prof_email,
           COALESCE(m.total_score, m_fallback.total_score) as total_score,
           COALESCE(m.research_score, m_fallback.research_score) as research_score,
           COALESCE(m.technical_score, m_fallback.technical_score) as technical_score,
           COALESCE(m.project_score, m_fallback.project_score) as project_score,
           COALESCE(m.match_reason, m_fallback.match_reason) as match_reason,
           COALESCE(m.gaps, m_fallback.gaps) as gaps
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    LEFT JOIN matches m ON a.match_id = m.id
    LEFT JOIN matches m_fallback ON m_fallback.id = (SELECT MAX(id) FROM matches WHERE professor_id = p.id)
    WHERE a.id IN (SELECT MAX(id) FROM applications GROUP BY professor_id)
    ORDER BY a.id DESC
    """)
    apps = cursor.fetchall()
    conn.close()

    total_count = len(apps)
    sent_count = sum(1 for a in apps if a["status"] == "Sent")
    interested_count = sum(1 for a in apps if a["status"] == "Interested")
    replied_count = sum(1 for a in apps if a["status"] in ["Replied", "Interested"])

    app_cards_html = ""
    for app_item in apps:
        pdf_filename = os.path.basename(app_item["cover_letter_path"]) if app_item["cover_letter_path"] else ""
        pdf_url = f"/generated_cover_letters/{pdf_filename}" if pdf_filename else "#"
        is_pending = app_item["status"] == "Email Drafted"
        
        status_colors = {
            "Email Drafted": "#2563eb",
            "Sent": "#16a34a",
            "Waiting": "#ca8a04",
            "Follow-up Required": "#d97706",
            "Interested": "#9333ea",
            "Replied": "#0891b2",
            "Rejected": "#dc2626"
        }
        badge_color = status_colors.get(app_item["status"], "#64748b")
        status_badge = f'<span style="background: {badge_color}; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600;">{app_item["status"]}</span>'

        score_disp = f"{app_item['total_score']:.1f}%" if app_item['total_score'] is not None else "N/A"
        research_disp = f"{app_item['research_score']:.1f}/40" if app_item['research_score'] is not None else "0/40"
        tech_disp = f"{app_item['technical_score']:.1f}/25" if app_item['technical_score'] is not None else "0/25"
        proj_disp = f"{app_item['project_score']:.1f}/20" if app_item['project_score'] is not None else "0/20"
        why_disp = app_item['match_reason'] or "High academic synergy with candidate background in machine learning and computer vision."
        body_disp = app_item['email_body'] or ""
        subj_disp = app_item['subject'] or ""

        app_cards_html += f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                    <h2 style="margin: 0 0 4px 0; font-size: 20px; color: #0f172a;">{app_item['prof_name']} <span style="font-size: 14px; color: #64748b; font-weight: normal;">({app_item['institution']} - {app_item['department']})</span></h2>
                    <p style="margin: 0; color: #475569; font-size: 13px;">Email: <b>{app_item['prof_email']}</b></p>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    {status_badge}
                </div>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                <div style="display: flex; gap: 16px; font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
                    <span>Match Score: <span style="color: #2563eb;">{score_disp}</span></span>
                    <span>Research: {research_disp}</span>
                    <span>Technical: {tech_disp}</span>
                    <span>Projects: {proj_disp}</span>
                </div>
                <div style="font-size: 12px; color: #475569; line-height: 1.5;">
                    <b>Why matched:</b> {why_disp}
                </div>
            </div>

            <div style="margin-bottom: 14px;">
                <label style="display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 4px;">Email Subject:</label>
                <input id="subj-{app_item['app_id']}" type="text" value="{subj_disp}" style="width: 100%; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; box-sizing: border-box;" {"" if is_pending else "readonly"}>
            </div>

            <div style="margin-bottom: 16px;">
                <label style="display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 4px;">Email Body:</label>
                <textarea id="body-{app_item['app_id']}" rows="8" style="width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; line-height: 1.4; box-sizing: border-box; font-family: inherit;" {"" if is_pending else "readonly"}>{body_disp}</textarea>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; gap: 12px; align-items: center;">
                    <a href="{pdf_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; background: #f1f5f9; color: #0f172a; text-decoration: none; padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; border: 1px solid #cbd5e1;">📄 View Cover Letter PDF</a>
                    <span style="font-size: 12px; color: #64748b;">+ Resume PDF (Anshu_Raj_Resume.pdf)</span>
                </div>
                
                <div style="display: flex; gap: 8px;">
                    {f'''
                    <button onclick="approveAndSend({app_item['app_id']})" style="background: #16a34a; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer;">
                        ✓ Approve & Send via Gmail
                    </button>
                    ''' if is_pending else f'''
                    <button onclick="resetSinglePending({app_item['app_id']})" style="background: #d97706; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer;">
                        ⏪ Reset to Pending
                    </button>
                    '''}
                </div>
            </div>
        </div>
        """

    if not app_cards_html:
        app_cards_html = "<div style='text-align: center; color: #64748b; padding: 40px;'>No applications drafted yet. Run discovery across IIT, IIIT, IISc, NIT, IISER, ISB, IIM!</div>"

    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>National AI Research Matching & Outreach - Anshu Raj</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="background: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 32px 16px;">
        <div style="max-width: 900px; margin: 0 auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div>
                    <h1 style="margin: 0 0 6px 0; font-size: 24px; color: #0f172a;">National Research Outreach Dashboard</h1>
                    <p style="margin: 0; font-size: 14px; color: #64748b;">Candidate: <b>Anshu Raj</b> (qismcdeltat@gmail.com) | Target: IIT, IIIT, IISc, NIT, IISER, ISB, IIM</p>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="sendAllPending()" style="background: #16a34a; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer;">🚀 Auto-Send All Pending</button>
                    <button onclick="resetAllPending()" style="background: #2563eb; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer;">🔄 Reset All to Pending</button>
                    <button onclick="cleanDuplicates()" style="background: #ef4444; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-size: 13px; cursor: pointer;">🗑️ Clean Duplicates</button>
                    <button onclick="location.reload()" style="background: #0f172a; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; cursor: pointer;">🔄 Refresh</button>
                </div>
            </div>

            <!-- Stats Bar -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px;">
                <div style="background: white; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center;">
                    <div style="font-size: 22px; font-weight: 700; color: #0f172a;">{total_count}</div>
                    <div style="font-size: 12px; color: #64748b;">Total Tracked</div>
                </div>
                <div style="background: white; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center;">
                    <div style="font-size: 22px; font-weight: 700; color: #16a34a;">{sent_count}</div>
                    <div style="font-size: 12px; color: #64748b;">Applications Sent</div>
                </div>
                <div style="background: white; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center;">
                    <div style="font-size: 22px; font-weight: 700; color: #0891b2;">{replied_count}</div>
                    <div style="font-size: 12px; color: #64748b;">Responses</div>
                </div>
                <div style="background: white; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center;">
                    <div style="font-size: 22px; font-weight: 700; color: #9333ea;">{interested_count}</div>
                    <div style="font-size: 12px; color: #64748b;">Positive Leads</div>
                </div>
            </div>
            
            {app_cards_html}
        </div>

        <script>
            async function approveAndSend(appId) {{
                const subject = document.getElementById("subj-" + appId).value;
                const body = document.getElementById("body-" + appId).value;
                
                if(!confirm("Are you sure you want to approve and send this cold email application live via Gmail API?")) return;

                try {{
                    const res = await fetch("/api/application/send", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{
                            application_id: appId,
                            user_approved: true,
                            edited_subject: subject,
                            edited_body: body
                        }})
                    }});
                    const data = await res.json();
                    if(res.ok) {{
                        alert("Application Approved & Sent Successfully via Gmail API!");
                        location.reload();
                    }} else {{
                        alert("Error: " + data.detail);
                    }}
                }} catch(err) {{
                    alert("Failed to send application: " + err);
                }}
            }}

            async function sendAllPending() {{
                if(!confirm("Start automated bulk sending for all pending applications?\n(Emails will be sent with rate-limit delays)")) return;
                try {{
                    const res = await fetch("/api/applications/send-all-pending", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ delay_min: 10.0, delay_max: 20.0 }})
                    }});
                    const data = await res.json();
                    if(res.ok) {{
                        alert(data.message);
                        location.reload();
                    }} else {{
                        alert("Error: " + data.detail);
                    }}
                }} catch(err) {{
                    alert("Failed bulk dispatch: " + err);
                }}
            }}

            async function resetAllPending() {{
                if(!confirm("Reset all tracked application statuses back to Pending ('Email Drafted')?")) return;
                try {{
                    const res = await fetch("/api/applications/reset-pending", {{ method: "POST" }});
                    const data = await res.json();
                    alert(data.message);
                    location.reload();
                }} catch(err) {{
                    alert("Failed to reset applications: " + err);
                }}
            }}

            async function resetSinglePending(appId) {{
                try {{
                    const res = await fetch("/api/application/reset-single/" + appId, {{ method: "POST" }});
                    const data = await res.json();
                    alert(data.message);
                    location.reload();
                }} catch(err) {{
                    alert("Failed to reset application: " + err);
                }}
            }}

            async function cleanDuplicates() {{
                try {{
                    const res = await fetch("/api/db/clean-duplicates", {{ method: "POST" }});
                    const data = await res.json();
                    alert("Cleaned " + data.removed_duplicates + " duplicate entries.");
                    location.reload();
                }} catch(err) {{
                    alert("Failed to clean duplicates: " + err);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return dashboard_html
