import re
from typing import Dict, Any, List
from src.research_analyzer import analyze_paper_synergy

def normalize_text(text: str) -> List[str]:
    return re.findall(r'\b[a-z0-9+#.-]+\b', text.lower())

def calculate_match_score(
    candidate_profile: Dict[str, Any],
    professor_data: Dict[str, Any],
    threshold: float = 70.0
) -> Dict[str, Any]:
    cand_interests = [i.lower() for i in candidate_profile.get("research_interests", [])]
    
    cand_skills = []
    for category, skill_list in candidate_profile.get("technical_skills", {}).items():
        if isinstance(skill_list, list):
            cand_skills.extend([s.lower() for s in skill_list])
        elif isinstance(skill_list, str):
            cand_skills.append(skill_list.lower())
        
    cand_projects = candidate_profile.get("research_projects", [])

    prof_areas = professor_data.get("research_areas", [])
    if isinstance(prof_areas, str):
        prof_areas = [a.strip().lower() for a in prof_areas.split(",") if a.strip()]
    else:
        prof_areas = [a.lower() for a in prof_areas]
        
    recent_papers = professor_data.get("recent_papers", [])
    prof_summary = (
        professor_data.get("research_summary", "") + " " +
        " ".join(prof_areas) + " " +
        " ".join(recent_papers)
    ).lower()

    # --- 1. Research Overlap (40%) ---
    research_matches = []
    for interest in cand_interests:
        interest_tokens = set(normalize_text(interest))
        for area in prof_areas:
            area_tokens = set(normalize_text(area))
            if interest_tokens.intersection(area_tokens) or area in interest or interest in area:
                research_matches.append(area)
                break
    research_overlap_ratio = min(len(research_matches) / max(len(prof_areas), 1), 1.0)
    research_score = round(research_overlap_ratio * 40.0, 1)

    # --- 2. Technical Skills (25%) ---
    matched_skills = [s for s in cand_skills if s in prof_summary]
    technical_score = round(min(len(matched_skills) / 4.0, 1.0) * 25.0, 1)

    # --- 3. Project & Thesis Similarity (20%) ---
    project_matches = []
    for proj in cand_projects:
        title = proj.get("title", "")
        domain = proj.get("domain", "").lower()
        if any(term in prof_summary for term in domain.split()):
            project_matches.append(title)
    project_score = round(min(len(project_matches) / 2.0, 1.0) * 20.0, 1)

    # --- 4. Deep Paper & Recent Research Synergy (10%) ---
    paper_synergy = analyze_paper_synergy(candidate_profile, professor_data)
    aligned_count = paper_synergy["aligned_papers_count"]
    recent_research_score = round(min(aligned_count / 2.0, 1.0) * 10.0, 1)

    # --- 5. Academic Background Compatibility (5%) ---
    background_score = 5.0

    total_score = min(round(research_score + technical_score + project_score + recent_research_score + background_score, 1), 100.0)

    if total_score >= 90:
        category = "Excellent"
    elif total_score >= 80:
        category = "Strong"
    elif total_score >= 70:
        category = "Good"
    elif total_score >= 60:
        category = "Weak"
    else:
        category = "Skip"

    reasons = []
    if research_score >= 25:
        reasons.append(f"Strong research overlap in {', '.join(set(research_matches[:3])) if research_matches else 'core AI/ML domains'}.")
    if matched_skills:
        reasons.append(f"Verified technical alignment with skills: {', '.join(matched_skills[:4])}.")
    if project_matches:
        reasons.append(f"Direct project experience in: {', '.join(project_matches[:2])}.")
    if aligned_count > 0:
        reasons.append(paper_synergy["synergy_summary"])

    gaps = []
    if len(matched_skills) < 2:
        gaps.append("Domain-specific niche methodologies of the professor are not explicitly in candidate skill matrix.")

    return {
        "total_score": total_score,
        "research_score": research_score,
        "technical_score": technical_score,
        "project_score": project_score,
        "recent_research_score": recent_research_score,
        "background_score": background_score,
        "category": category,
        "is_shortlisted": total_score >= threshold,
        "match_reason": "\n- ".join(reasons) if reasons else "Good general alignment with machine learning & computer vision background.",
        "gaps": "\n- ".join(gaps) if gaps else "No major technical gap identified.",
        "matched_skills": matched_skills,
        "matched_projects": project_matches,
        "aligned_papers": paper_synergy["aligned_papers"]
    }
