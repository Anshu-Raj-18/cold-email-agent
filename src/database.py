import sqlite3
import json
import os
import csv
from typing import Optional, Dict, Any, List

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "agent.db")
DEFAULT_PROFESSORS_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "professors.csv")
DEFAULT_APPLICATIONS_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "applications.csv")

def get_db_path() -> str:
    return os.getenv("AGENT_DB_PATH", DEFAULT_DB_PATH)

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    target_path = db_path or get_db_path()
    try:
        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        conn = sqlite3.connect(target_path)
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE IF NOT EXISTS _fs_test (id INTEGER PRIMARY KEY);")
        conn.commit()
        return conn
    except Exception:
        fallback_path = os.path.join(os.path.expanduser("~"), ".coldmailer", "agent.db")
        os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
        conn = sqlite3.connect(fallback_path)
        conn.row_factory = sqlite3.Row
        return conn

def check_and_repair_table(conn: sqlite3.Connection, table_name: str, required_columns: List[str], create_sql: str) -> None:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    table_exists = cursor.fetchone() is not None
    if table_exists:
        cursor.execute(f"PRAGMA table_info({table_name});")
        existing_cols = {row["name"] for row in cursor.fetchall()}
        missing = [col for col in required_columns if col not in existing_cols]
        if missing:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            cursor.execute(create_sql)
    else:
        cursor.execute(create_sql)
    conn.commit()

def init_db(db_path: Optional[str] = None) -> None:
    conn = get_connection(db_path)

    # 1. Candidates table
    candidates_cols = ["id", "name", "email", "phone", "location", "education", "skills", "projects", "research_interests", "resume_path"]
    candidates_sql = """
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        location TEXT,
        education TEXT,
        skills TEXT,
        projects TEXT,
        research_interests TEXT,
        resume_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    check_and_repair_table(conn, "candidates", candidates_cols, candidates_sql)

    # 2. Professors table
    professors_cols = ["id", "name", "iit", "department", "designation", "email", "research_areas", "research_summary", "profile_url", "lab_url", "source_urls"]
    professors_sql = """
    CREATE TABLE IF NOT EXISTS professors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        iit TEXT NOT NULL,
        department TEXT,
        designation TEXT,
        email TEXT NOT NULL UNIQUE,
        research_areas TEXT,
        research_summary TEXT,
        profile_url TEXT,
        lab_url TEXT,
        source_urls TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    check_and_repair_table(conn, "professors", professors_cols, professors_sql)

    # 3. Matches table
    matches_cols = ["id", "candidate_id", "professor_id", "research_score", "technical_score", "project_score", "recent_research_score", "background_score", "total_score", "match_reason", "gaps"]
    matches_sql = """
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        professor_id INTEGER NOT NULL,
        research_score REAL NOT NULL,
        technical_score REAL NOT NULL,
        project_score REAL NOT NULL,
        recent_research_score REAL NOT NULL,
        background_score REAL NOT NULL,
        total_score REAL NOT NULL,
        match_reason TEXT,
        gaps TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id),
        FOREIGN KEY(professor_id) REFERENCES professors(id)
    );
    """
    check_and_repair_table(conn, "matches", matches_cols, matches_sql)

    # 4. Applications table
    applications_cols = ["id", "professor_id", "match_id", "subject", "email_body", "cover_letter_path", "resume_path", "status", "drafted_at", "approved_at", "sent_at", "response", "response_date", "followup_date", "notes"]
    applications_sql = """
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        professor_id INTEGER NOT NULL,
        match_id INTEGER,
        subject TEXT,
        email_body TEXT,
        cover_letter_path TEXT,
        resume_path TEXT,
        status TEXT DEFAULT 'Discovered',
        drafted_at TIMESTAMP,
        approved_at TIMESTAMP,
        sent_at TIMESTAMP,
        response TEXT,
        response_date TIMESTAMP,
        followup_date TIMESTAMP,
        notes TEXT,
        FOREIGN KEY(professor_id) REFERENCES professors(id),
        FOREIGN KEY(match_id) REFERENCES matches(id)
    );
    """
    check_and_repair_table(conn, "applications", applications_cols, applications_sql)
    conn.close()

def clean_duplicate_applications(db_path: Optional[str] = None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM applications
    WHERE id NOT IN (
        SELECT MAX(id) FROM applications GROUP BY professor_id
    )
    """)
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def seed_candidate_profile(profile: Dict[str, Any], db_path: Optional[str] = None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()

    name = profile.get("name", "Anshu Raj")
    email = profile.get("email", "qismcdeltat@gmail.com")
    phone = profile.get("phone", "+91 9110949492")
    location = profile.get("location", "Kolkata, India")
    education = json.dumps(profile.get("education", []))
    skills = json.dumps(profile.get("technical_skills", {}))
    projects = json.dumps(profile.get("research_projects", []))
    research_interests = json.dumps(profile.get("research_interests", []))
    resume_path = profile.get("resume_filename", "Anshu_Raj_Resume.pdf")

    cursor.execute("""
    INSERT INTO candidates (name, email, phone, location, education, skills, projects, research_interests, resume_path, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(email) DO UPDATE SET
        name=excluded.name,
        phone=excluded.phone,
        location=excluded.location,
        education=excluded.education,
        skills=excluded.skills,
        projects=excluded.projects,
        research_interests=excluded.research_interests,
        resume_path=excluded.resume_path,
        updated_at=CURRENT_TIMESTAMP;
    """, (name, email, phone, location, education, skills, projects, research_interests, resume_path))
    
    conn.commit()
    cursor.execute("SELECT id FROM candidates WHERE email = ?", (email,))
    row = cursor.fetchone()
    candidate_id = row["id"] if row else 1
    conn.close()
    return candidate_id

def get_candidate_profile(db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "location": row["location"],
        "education": json.loads(row["education"]),
        "technical_skills": json.loads(row["skills"]),
        "research_projects": json.loads(row["projects"]),
        "research_interests": json.loads(row["research_interests"]),
        "resume_path": row["resume_path"]
    }

def has_contacted_professor(email: str, db_path: Optional[str] = None) -> bool:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id 
    FROM applications a 
    JOIN professors p ON a.professor_id = p.id
    WHERE p.email = ? AND a.status IN ('Sent', 'Waiting', 'Replied', 'Interested', 'Approved')
    """, (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def insert_or_update_professor(prof_data: Dict[str, Any], db_path: Optional[str] = None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    name = prof_data.get("name", "")
    iit = prof_data.get("institution", prof_data.get("iit", ""))
    department = prof_data.get("department", "")
    designation = prof_data.get("designation", "")
    email = prof_data.get("email", "").strip().lower()
    research_areas = json.dumps(prof_data.get("research_areas", [])) if isinstance(prof_data.get("research_areas"), list) else prof_data.get("research_areas", "")
    research_summary = prof_data.get("research_summary", "")
    profile_url = prof_data.get("profile_url", "")
    lab_url = prof_data.get("lab_url", "")
    source_urls = json.dumps(prof_data.get("source_urls", []))

    cursor.execute("""
    INSERT INTO professors (name, iit, department, designation, email, research_areas, research_summary, profile_url, lab_url, source_urls)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
        name=excluded.name,
        iit=excluded.iit,
        department=excluded.department,
        designation=excluded.designation,
        research_areas=excluded.research_areas,
        research_summary=excluded.research_summary,
        profile_url=excluded.profile_url,
        lab_url=excluded.lab_url,
        source_urls=excluded.source_urls;
    """, (name, iit, department, designation, email, research_areas, research_summary, profile_url, lab_url, source_urls))
    
    conn.commit()
    cursor.execute("SELECT id FROM professors WHERE email = ?", (email,))
    row = cursor.fetchone()
    prof_id = row["id"] if row else 1
    conn.close()
    return prof_id

def save_match(match_data: Dict[str, Any], db_path: Optional[str] = None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO matches (candidate_id, professor_id, research_score, technical_score, project_score, recent_research_score, background_score, total_score, match_reason, gaps)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        match_data["candidate_id"],
        match_data["professor_id"],
        match_data["research_score"],
        match_data["technical_score"],
        match_data["project_score"],
        match_data["recent_research_score"],
        match_data["background_score"],
        match_data["total_score"],
        match_data.get("match_reason", ""),
        match_data.get("gaps", "")
    ))
    conn.commit()
    match_id = cursor.lastrowid
    conn.close()
    return match_id

def create_application_record(app_data: Dict[str, Any], db_path: Optional[str] = None) -> int:
    conn = get_connection(db_path)
    cursor = conn.cursor()
    prof_id = app_data["professor_id"]
    match_id = app_data.get("match_id")

    if not match_id:
        cursor.execute("SELECT id FROM matches WHERE professor_id = ? ORDER BY id DESC LIMIT 1", (prof_id,))
        m_row = cursor.fetchone()
        if m_row:
            match_id = m_row["id"]
    
    cursor.execute("SELECT id FROM applications WHERE professor_id = ?", (prof_id,))
    existing = cursor.fetchone()
    
    if existing:
        app_id = existing["id"]
        cursor.execute("""
        UPDATE applications
        SET match_id = COALESCE(?, match_id),
            subject = COALESCE(NULLIF(?, ''), subject),
            email_body = COALESCE(NULLIF(?, ''), email_body),
            cover_letter_path = COALESCE(NULLIF(?, ''), cover_letter_path),
            resume_path = COALESCE(NULLIF(?, ''), resume_path),
            status = CASE WHEN status = 'Discovered' THEN 'Email Drafted' ELSE status END,
            drafted_at = COALESCE(drafted_at, CURRENT_TIMESTAMP)
        WHERE id = ?
        """, (
            match_id,
            app_data.get("subject", ""),
            app_data.get("email_body", ""),
            app_data.get("cover_letter_path", ""),
            app_data.get("resume_path", ""),
            app_id
        ))
    else:
        cursor.execute("""
        INSERT INTO applications (professor_id, match_id, subject, email_body, cover_letter_path, resume_path, status, drafted_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Email Drafted', CURRENT_TIMESTAMP)
        """, (
            prof_id,
            match_id,
            app_data.get("subject", ""),
            app_data.get("email_body", ""),
            app_data.get("cover_letter_path", ""),
            app_data.get("resume_path", "")
        ))
        app_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Automatically export updated tables to CSV
    export_professors_csv()
    export_applications_csv()
    return app_id

def export_professors_csv(csv_path: Optional[str] = None, db_path: Optional[str] = None) -> str:
    """Exports all professors from SQLite database to CSV file."""
    target_csv = csv_path or DEFAULT_PROFESSORS_CSV
    os.makedirs(os.path.dirname(target_csv), exist_ok=True)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, iit as institution, department, designation, email, research_areas, research_summary, profile_url FROM professors ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    with open(target_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Institution", "Department", "Designation", "Email", "Research Areas", "Research Summary", "Profile URL"])
        for r in rows:
            writer.writerow([r["id"], r["name"], r["institution"], r["department"], r["designation"], r["email"], r["research_areas"], r["research_summary"], r["profile_url"]])
    return target_csv

def export_applications_csv(csv_path: Optional[str] = None, db_path: Optional[str] = None) -> str:
    """Exports all applications from SQLite database to CSV file."""
    target_csv = csv_path or DEFAULT_APPLICATIONS_CSV
    os.makedirs(os.path.dirname(target_csv), exist_ok=True)
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.id, p.name as professor, p.iit as institution, p.email as professor_email,
           a.subject, a.status, a.drafted_at, a.sent_at, a.notes
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    ORDER BY a.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    with open(target_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Application ID", "Professor", "Institution", "Email", "Subject", "Status", "Drafted At", "Sent At", "Notes"])
        for r in rows:
            writer.writerow([r["id"], r["professor"], r["institution"], r["professor_email"], r["subject"], r["status"], r["drafted_at"], r["sent_at"], r["notes"]])
    return target_csv
