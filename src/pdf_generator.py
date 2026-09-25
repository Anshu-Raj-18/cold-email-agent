import os
import re
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import HexColor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "generated_cover_letters")

def sanitize_filename(name: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip())
    return re.sub(r'_+', '_', clean)

def generate_cover_letter_pdf(
    cover_letter_data: Dict[str, Any],
    output_dir: str = DEFAULT_OUTPUT_DIR
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    candidate_name = cover_letter_data.get("candidate_name", "Anshu Raj")
    prof_name = cover_letter_data.get("professor_name", "Professor")
    filename = f"Cover_Letter_{sanitize_filename(prof_name)}.pdf"
    file_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
        title=f"Cover Letter - {candidate_name} - {prof_name}",
        author=candidate_name,
        subject=f"Expression of Interest - {candidate_name}",
        creator="National AI Research Matching Agent"
    )

    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle('CLHeader', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    link_style = ParagraphStyle('CLLink', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=HexColor('#1d4ed8'))
    date_style = ParagraphStyle('CLDate', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    recipient_style = ParagraphStyle('CLRecipient', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    subject_style = ParagraphStyle('CLSubject', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14)
    salutation_style = ParagraphStyle('CLSalutation', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    body_style = ParagraphStyle('CLBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=14, textColor=HexColor('#111111'), alignment=4)
    closing_style = ParagraphStyle('CLClosing', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)

    story = []

    github_url = cover_letter_data.get("github_url") or os.getenv("GITHUB_PROFILE", "https://github.com/Anshu-Raj-18")
    resume_drive_url = cover_letter_data.get("resume_drive_url") or os.getenv("RESUME_DRIVE_LINK", "https://drive.google.com/file/d/1XW5vi2Rfq8miIzVFq7OhoBLv9d0olVnX/view?usp=sharing")

    # 1. Header Contact Information (Clean header: Name, Location, Phone, Email)
    story.append(Paragraph(f"<b>{candidate_name}</b>", header_style))
    story.append(Paragraph(f"{cover_letter_data.get('candidate_location', 'Kolkata, India')} | {cover_letter_data.get('candidate_phone', '+91 9110949492')}", header_style))
    story.append(Paragraph(f"Email: {cover_letter_data.get('candidate_email', 'qismcdeltat@gmail.com')}", header_style))
    story.append(Spacer(1, 12))

    # 2. Date
    story.append(Paragraph(f"Date: {cover_letter_data.get('date', '14 August 2026')}", date_style))
    story.append(Spacer(1, 12))

    # 3. Recipient Block (Bold Professor & Lab Name)
    story.append(Paragraph("To,", recipient_style))
    story.append(Paragraph(f"<b>{prof_name}</b>", recipient_style))
    
    lab_name = cover_letter_data.get("lab_name")
    department = cover_letter_data.get("department")
    
    if lab_name and not lab_name.startswith("http"):
        story.append(Paragraph(f"<b>{lab_name}</b>", recipient_style))
        
    if department and department != lab_name:
        story.append(Paragraph(department, recipient_style))
        
    story.append(Paragraph(cover_letter_data.get("iit_name", "Institute"), recipient_style))
    story.append(Paragraph(cover_letter_data.get("institute_location", "India"), recipient_style))
    story.append(Spacer(1, 12))

    # 4. Subject Line
    story.append(Paragraph(f"<b>{cover_letter_data.get('subject', 'Subject: Expression of Interest for Research Internship / Research Trainee Opportunity')}</b>", subject_style))
    story.append(Spacer(1, 10))

    # 5. Salutation & Greeting
    salutation = cover_letter_data.get("salutation_name", prof_name)
    story.append(Paragraph(f"Dear {salutation},", salutation_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("I hope you are doing well.", body_style))
    story.append(Spacer(1, 8))

    # 6. Body Paragraphs (Rendering bold tags and links)
    for para in cover_letter_data.get("paragraphs", []):
        story.append(Paragraph(para, body_style))
        story.append(Spacer(1, 8))

    # 7. Closing & Signature (Links placed ONLY in the closing section)
    story.append(Paragraph(cover_letter_data.get("closing_note", "Thank you very much for your time and consideration. I look forward to the possibility of working with your research group."), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Sincerely,", closing_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>{candidate_name}</b>", closing_style))
    story.append(Paragraph(f"GitHub: <font color='#1d4ed8'><a href='{github_url}'>{github_url}</a></font>", link_style))
    story.append(Paragraph(f"Resume (Google Drive): <font color='#1d4ed8'><a href='{resume_drive_url}'>{resume_drive_url}</a></font>", link_style))

    doc.build(story)
    return file_path
