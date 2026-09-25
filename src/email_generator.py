from typing import Dict, Any, Optional
from datetime import datetime
from src.ollama_client import generate_personalized_alignment

def get_salutation_name(full_name: str) -> str:
    name_clean = full_name.replace("Prof.", "").replace("Dr.", "").strip()
    parts = name_clean.split()
    return f"Prof. {parts[-1]}" if len(parts) > 1 else f"Prof. {name_clean}"

def clean_lab_name(lab_name: Optional[str], salutation_name: str) -> str:
    if not lab_name or lab_name.startswith("http") or "www." in lab_name:
        return f"{salutation_name} Research Group"
    return lab_name.strip()

def generate_application_package_content(candidate_profile: Dict[str, Any], professor_data: Dict[str, Any]) -> Dict[str, Any]:
    candidate_name = candidate_profile.get("name", "Anshu Raj")
    candidate_email = candidate_profile.get("email", "qismcdeltat@gmail.com")
    candidate_phone = candidate_profile.get("phone", "+91 9110949492")
    candidate_location = candidate_profile.get("location", "Kolkata, India")
    github_url = candidate_profile.get("github", "https://github.com/Anshu-Raj-18")
    resume_drive_url = candidate_profile.get("resume_drive_link", "https://drive.google.com/file/d/1XW5vi2Rfq8miIzVFq7OhoBLv9d0olVnX/view?usp=sharing")

    education_list = candidate_profile.get("education", [])
    primary_edu = education_list[0] if education_list else {}
    degree = primary_edu.get("degree", "B.Tech in Electronics & Communication Engineering")
    institution_edu = primary_edu.get("institution", "Heritage Institute of Technology, Kolkata")

    projects = candidate_profile.get("research_projects", [])
    p1 = projects[0] if len(projects) > 0 else {}
    p1_title = p1.get("title", "AURA — AI for Unified Regional Access")
    p1_summary = p1.get("summary", "speech translation system integrating ASR, translation retrieval, and speech synthesis")

    prof_name = professor_data.get("name", "Professor")
    salutation_name = get_salutation_name(prof_name)
    institution = professor_data.get("institution", professor_data.get("iit", "Institute"))
    full_institution_name = professor_data.get("full_institution_name", institution)
    department = professor_data.get("department", "Department of Computer Science & Engineering")
    location = professor_data.get("location", "India")
    
    raw_lab_name = professor_data.get("lab_name")
    lab_name = clean_lab_name(raw_lab_name, salutation_name)
    
    prof_areas = professor_data.get("research_areas", [])
    primary_area = prof_areas[0] if isinstance(prof_areas, list) and prof_areas else "Machine Learning & AI"
    areas_str = ", ".join(prof_areas[:3]) if isinstance(prof_areas, list) else str(prof_areas)

    # 1. Plain Text Email Subject & Body (for Gmail)
    subject = f"Application for Research Internship – {primary_area} – {candidate_name}"

    email_body = f"""Dear {salutation_name},

I hope you are doing well.

My name is {candidate_name}, and I am currently pursuing my {degree} at {institution_edu}. I am writing to express my strong interest in the research activities of the {lab_name} at {institution} and to inquire about potential research internship or research assistant opportunities under your supervision.

My core expertise spans machine learning, computer vision, data preprocessing, and API development. For my flagship project, {p1_title}, I {p1_summary}. Additionally, I have developed deep learning tools for image restoration (Deep Learning Image Enhancer) and interactive analytics platforms. I have hands-on experience with Python, PyTorch, OpenCV, Scikit-learn, SQL, and FastAPI, and I was awarded 1st Rank in the SIH Internal Hackathon.

I am keen to apply machine learning and AI techniques to {areas_str}, and I would be honored to contribute to your ongoing research projects. I have attached my customized cover letter and resume for your review. You may also view my resume and GitHub profile online:
- Online Resume (Google Drive): {resume_drive_url}
- GitHub Profile: {github_url}

If there are any current or upcoming openings in your research group, I would welcome the opportunity to discuss how my technical background aligns with your work.

Thank you very much for your time and consideration.

Sincerely,

{candidate_name}
{candidate_location} | {candidate_phone}
Email: {candidate_email}
GitHub: {github_url}
Resume (Google Drive): {resume_drive_url}"""

    # 2. Personalized Cover Letter Payload (with Bold highlights matching template)
    alignment_para = generate_personalized_alignment(candidate_profile, professor_data)
    current_date = datetime.now().strftime("%d %B %Y")

    para1 = (
        f"I am writing to express my sincere interest in the research activities of the {lab_name}, "
        f"{institution} and to seek an opportunity to contribute as a Research Intern / Research "
        f"Trainee under your guidance."
    )

    para2 = (
        f"I am currently pursuing my <b>{degree}</b> at <b>{institution_edu}</b> (CGPA: 8.8/10.0). "
        f"My technical expertise and research passion are <b>centered on machine learning, computer vision, "
        f"speech processing, and API development</b>. For my key project, <b>{p1_title}</b>, I built an offline "
        f"Hindi-to-Tribal speech translation system integrating ASR, translation retrieval, and speech synthesis, "
        f"indexing over 82,500+ translation pairs into a low-latency database."
    )

    para3 = (
        "I have gained practical experience developing machine learning pipelines, computer vision image restoration "
        "models, and REST APIs using <b>Python, PyTorch, OpenCV, Scikit-learn, SQL, and FastAPI</b>. In addition, I "
        "secured <b>1st Rank in the SIH Internal Hackathon</b> and have actively competed in over 9+ hackathons, "
        "proving my capability in rapid prototyping, scientific problem solving, and production-ready system design."
    )

    para4 = alignment_para

    para5 = (
        f"I have attached my resume and customized cover letter for your kind consideration. My full portfolio is available "
        f"on <b>GitHub</b> (<a href='{github_url}'>{github_url}</a>) and my resume can also be accessed online via "
        f"<b>Google Drive</b> (<a href='{resume_drive_url}'>{resume_drive_url}</a>). I would be grateful if my profile "
        f"could be considered for any current or upcoming research opportunities in your laboratory."
    )

    cover_letter_data = {
        "candidate_name": candidate_name,
        "candidate_location": candidate_location,
        "candidate_phone": candidate_phone,
        "candidate_email": candidate_email,
        "github_url": github_url,
        "resume_drive_url": resume_drive_url,
        "date": current_date,
        "professor_name": prof_name,
        "salutation_name": salutation_name,
        "lab_name": lab_name,
        "department": department,
        "iit_name": full_institution_name,
        "institute_location": location,
        "subject": "Subject: Expression of Interest for Research Internship / Research Trainee Opportunity",
        "paragraphs": [para1, para2, para3, para4, para5],
        "closing_note": "Thank you very much for your time and consideration. I look forward to the possibility of working with your research group."
    }

    return {
        "subject": subject,
        "email_body": email_body,
        "cover_letter_data": cover_letter_data
    }
