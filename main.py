import sys
import os
import argparse
import logging
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any

from src.config import config
from src.database import (
    init_db,
    seed_candidate_profile,
    get_candidate_profile,
    insert_or_update_professor,
    save_match,
    create_application_record,
    export_professors_csv,
    export_applications_csv,
    get_connection
)
from src.scraper import discover_professors
from src.academic_fetcher import AcademicFetcher
from src.matching_engine import calculate_match_score
from src.rag_engine import RAGEngine
from src.pdf_generator import generate_cover_letter_pdf
from src.email_generator import generate_application_package_content
from src.email_service import EmailService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("cold_mailer")

def print_header():
    print("=" * 75)
    print("   NATIONAL IIT/IIIT/NIT PROFESSOR RESEARCH MATCHING & RAG OUTREACH PIPELINE")
    print("   Candidate: Anshu Raj (qismcdeltat@gmail.com) | B.Tech ECE Heritage Institute")
    print("=" * 75)

def parse_args():
    parser = argparse.ArgumentParser(description="National Academic Cold Outreach RAG Pipeline")
    parser.add_argument("--tier", type=str, default="ALL", help="Institution type (ALL, IIT, IIIT, IISc, NIT, IISER, ISB, IIM)")
    parser.add_argument("--domain", type=str, default="Machine Learning Computer Vision Speech AI Deep Learning", help="Domain search terms")
    parser.add_argument("--batch-size", type=int, default=5, help="Number of emails to process & review in one batch (5-10)")
    parser.add_argument("--threshold", type=float, default=70.0, help="Minimum match score percentage (e.g. 70.0)")
    parser.add_argument("--professor", type=str, help="Single target professor name override")
    parser.add_argument("--institution", type=str, help="Single target university override")
    parser.add_argument("--dry-run", action="store_true", help="Run RAG pipeline & draft generation without Gmail API sending")
    return parser.parse_args()

def main():
    print_header()
    args = parse_args()

    # 1. Initialize DB and Seed Candidate Profile
    init_db()
    profile_json_path = Path("data/candidate_profile.json")
    if profile_json_path.exists():
        import json
        with open(profile_json_path, "r", encoding="utf-8") as f:
            cand_profile = json.load(f)
        seed_candidate_profile(cand_profile)
    else:
        try:
            config.validate_profile()
        except Exception as e:
            print(e)
            sys.exit(1)
        cand_profile = {
            "name": config.sender_name,
            "email": config.sender_email,
            "phone": "+91 9110949492",
            "location": "Kolkata, India",
            "research_interests": ["Machine Learning & Deep Learning", "Computer Vision & Image Restoration", "Speech Processing & Translation AI"],
            "technical_skills": {"languages": ["Python", "C", "SQL"], "ml": ["PyTorch", "OpenCV", "Scikit-learn", "FastAPI"]},
            "research_projects": [{"title": "AURA — AI for Unified Regional Access", "domain": "Speech Processing AI"}]
        }

    cand = get_candidate_profile() or cand_profile

    print(f"\n[1/5] Verified Candidate: {cand['name']} ({cand['email']})")

    # 2. Discover Professors from 1584 Professors Excel & Scraper Catalog
    print(f"\n[2/5] Querying Faculty Catalog & Excel for '{args.domain}' across [{args.tier}]...")
    profs = discover_professors(
        institution_type=args.tier,
        institution_name=args.institution,
        research_filter=args.domain
    )

    if args.professor:
        profs = [p for p in profs if args.professor.lower() in p["name"].lower()]
        if not profs:
            profs = [{
                "name": args.professor,
                "institution": args.institution or "IIT",
                "department": "Department of Computer Science",
                "email": "professor@university.ac.in",
                "research_areas": [args.domain],
                "research_summary": f"Research on {args.domain}."
            }]

    print(f" -> Found {len(profs)} matching professors.")

    # 3. Match and Rank Professors against Anshu's Profile
    print(f"\n[3/5] Scoring & Ranking Professors against Candidate Skill Matrix...")
    ranked_profs = []
    for prof in profs:
        prof_id = insert_or_update_professor(prof)
        match_res = calculate_match_score(cand, prof, threshold=args.threshold)
        if match_res["is_shortlisted"]:
            match_id = save_match({
                "candidate_id": cand.get("id", 1),
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
            ranked_profs.append((prof, match_res, prof_id, match_id))

    ranked_profs.sort(key=lambda x: x[1]["total_score"], reverse=True)

    # Export dataset to data/professors.csv
    csv_prof_path = export_professors_csv()
    print(f" -> Shortlisted {len(ranked_profs)} faculty (Match >= {args.threshold}%). Saved to '{csv_prof_path}'.")

    if not ranked_profs:
        print("\n[INFO] No professors met the score threshold. Try lowering --threshold or changing --domain.")
        return

    # 4. Process Batch (5-10 at a time)
    batch_size = max(1, min(args.batch_size, 10))
    target_batch = ranked_profs[:batch_size]
    print(f"\n[4/5] Preparing RAG Outreach & Cover Letter PDFs for Batch of {len(target_batch)} Professors...")

    academic_fetcher = AcademicFetcher(semantic_scholar_api_key=config.semantic_scholar_api_key)
    email_svc = EmailService()

    # RAG Engine check
    use_gemini_rag = bool(config.gemini_api_key and config.gemini_api_key != "your_gemini_api_key_here")
    rag_engine = None
    if use_gemini_rag:
        try:
            rag_engine = RAGEngine()
        except Exception as e:
            logger.warning(f"Gemini RAG Engine initialization skipped: {e}")

    # 5. Human-in-the-Loop Review Loop
    print("\n" + "=" * 75)
    print(f"            HUMAN-IN-THE-LOOP BATCH REVIEW ({len(target_batch)} Emails)")
    print("=" * 75)

    for idx, (prof_data, match_res, prof_id, match_id) in enumerate(target_batch, 1):
        print(f"\n--- [{idx}/{len(target_batch)}] PROFESSOR OUTREACH DRAFT ---")
        print(f"NAME        : {prof_data['name']} ({prof_data['institution']} - {prof_data.get('department', 'CSE')})")
        print(f"EMAIL       : {prof_data['email']}")
        print(f"MATCH SCORE : {match_res['total_score']}% ({match_res['category']})")
        print(f"WHY MATCHED : {match_res['match_reason'].replace('\n', ' ')}")

        # Fetch recent academic papers via Academic API if available
        fetched_papers = academic_fetcher.fetch_papers(prof_data['name'], prof_data['institution'], max_results=3)
        if fetched_papers:
            prof_data["recent_papers"] = [p["title"] for p in fetched_papers]

        # Generate Package Content & Cover Letter PDF
        pkg = generate_application_package_content(cand, prof_data)
        pdf_path = generate_cover_letter_pdf(pkg["cover_letter_data"])

        # Save Application Record in DB & data/applications.csv
        app_id = create_application_record({
            "professor_id": prof_id,
            "match_id": match_id,
            "subject": pkg["subject"],
            "email_body": pkg["email_body"],
            "cover_letter_path": pdf_path,
            "resume_path": os.path.abspath("assets/Anshu_Raj_Resume.pdf")
        })

        print("-" * 75)
        print(f"SUBJECT: {pkg['subject']}\n")
        print("EMAIL BODY:")
        print(pkg['email_body'])
        print("-" * 75)
        print(f"COVER LETTER PDF: {pdf_path}")
        print(f"RESUME ATTACHED : assets/Anshu_Raj_Resume.pdf")

        if args.dry_run:
            print("[DRY-RUN MODE] Skipping email dispatch for this record.")
            continue

        choice = input(f"\nAction for {prof_data['name']} -> Send Email [y] | Draft in Gmail [d] | Skip [N]: ").strip().lower()
        if choice in ["y", "yes"]:
            auth_ok = email_svc.authenticate()
            if auth_ok:
                res = email_svc.send_email(prof_data['email'], pkg['subject'], pkg['email_body'])
                if res.get("status") == "success":
                    print(f" -> [SUCCESS] Sent email to {prof_data['email']}. ID: {res.get('id')}")
                else:
                    print(f" -> [ERROR] Failed to send: {res.get('error')}")
            else:
                print(" -> [NOTICE] Gmail OAuth not configured. Content saved in DB & data/applications.csv.")
        elif choice in ["d", "draft"]:
            auth_ok = email_svc.authenticate()
            if auth_ok:
                res = email_svc.create_draft(prof_data['email'], pkg['subject'], pkg['email_body'])
                if res.get("status") == "success":
                    print(f" -> [SUCCESS] Created draft in Gmail for {prof_data['email']}. ID: {res.get('id')}")
                else:
                    print(f" -> [ERROR] Failed to draft: {res.get('error')}")

    export_applications_csv()
    print("\n" + "=" * 75)
    print("   BATCH OUTREACH COMPLETED! CSV Exports updated in 'data/' directory.")
    print("   To view the visual dashboard, run: python run_server.py")
    print("=" * 75)

if __name__ == "__main__":
    main()
