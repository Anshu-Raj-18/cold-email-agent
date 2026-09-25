from typing import Dict, Any, List

def analyze_paper_synergy(
    candidate_profile: Dict[str, Any],
    professor_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs deep research paper and publication synergy analysis between
    Anshu Raj's project work and the professor's research focus/papers.
    """
    cand_projects = candidate_profile.get("research_projects", [])
    
    prof_papers = professor_data.get("recent_papers", [])
    prof_areas = professor_data.get("research_areas", [])
    if isinstance(prof_areas, str):
        prof_areas = [a.strip() for a in prof_areas.split(",") if a.strip()]
        
    paper_alignments = []
    
    # Check alignments across Vision, Speech/Translation, Deep Learning, Image Restoration, Analytics & ML
    for paper in prof_papers:
        p_lower = paper.lower()
        if any(term in p_lower for term in ["multimodal", "audio", "speech", "translation", "asr", "tts", "language", "nlp", "text", "conversational"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Direct synergy with candidate's AURA Hindi-to-Tribal speech translation system (ASR, Vosk, PyTorch, MMS-TTS, 82.5k pairs)."
            })
        elif any(term in p_lower for term in ["restoration", "enhancement", "resolution", "microscopic", "image", "vision", "cv", "opencv", "super-resolution"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Direct synergy with candidate's Deep Learning Image Enhancer restoring microscopic images and generating 2x higher-resolution outputs."
            })
        elif any(term in p_lower for term in ["analytics", "dashboard", "chat", "data analysis", "pandas", "streamlit", "pattern"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Aligns with candidate's WhatsApp Chat Analyzer extracting user activity trends and chat statistics."
            })
        elif any(term in p_lower for term in ["explainable", "generative", "neural", "deep learning", "optimization", "graph", "signal", "electronics", "hardware"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Synergizes with candidate's B.Tech ECE background (8.8 CGPA) and SIH 1st Rank winning ML/DL engineering skills."
            })

    # Summary synthesis
    if paper_alignments:
        synergy_summary = f"Strong paper synergy identified with {len(paper_alignments)} recent publications in {', '.join(prof_areas[:2]) if prof_areas else 'AI/ML'}."
    else:
        synergy_summary = "Foundational methodological compatibility in machine learning, computer vision, and speech processing."

    return {
        "aligned_papers_count": len(paper_alignments),
        "aligned_papers": paper_alignments,
        "synergy_summary": synergy_summary
    }
