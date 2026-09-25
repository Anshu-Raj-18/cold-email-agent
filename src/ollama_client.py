import os
import json
import httpx
from typing import Dict, Any, Optional

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

_OLLAMA_CHECKED = False
_OLLAMA_ONLINE = False

def is_ollama_online() -> bool:
    global _OLLAMA_CHECKED, _OLLAMA_ONLINE
    if _OLLAMA_CHECKED:
        return _OLLAMA_ONLINE
    try:
        res = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=0.5)
        _OLLAMA_ONLINE = (res.status_code == 200)
    except Exception:
        _OLLAMA_ONLINE = False
    _OLLAMA_CHECKED = True
    return _OLLAMA_ONLINE

def query_ollama(prompt: str, system_prompt: Optional[str] = None, model: str = OLLAMA_MODEL) -> Optional[str]:
    """Queries local Ollama instance with timeout and fallback handling."""
    if not is_ollama_online():
        return None

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass
    return None

def generate_personalized_alignment(
    candidate_profile: Dict[str, Any],
    professor_data: Dict[str, Any]
) -> str:
    """
    Generates a truthful, grounded 1-2 sentence alignment paragraph
    connecting candidate's exact background to the professor's research.
    """
    prof_name = professor_data.get("name", "Professor")
    prof_lab = professor_data.get("lab_name", professor_data.get("lab_url", "your research laboratory"))
    prof_areas = ", ".join(professor_data.get("research_areas", ["artificial intelligence", "machine learning"]))
    institution_name = professor_data.get("institution", professor_data.get("iit", "your institution"))

    if is_ollama_online():
        system_prompt = (
            "You are an academic cold email assistant. You must write strictly grounded, factual content. "
            "Do NOT invent candidate projects or skills. Only reference B.Tech ECE background, AURA speech translation (Vosk/PyTorch/SQLite), "
            "Deep Learning Image Enhancer (OpenCV/PyTorch), 1st Rank SIH Hackathon winner, computer vision, and machine learning."
        )

        user_prompt = f"""
Write a single concise paragraph (3-4 sentences) for a formal academic cover letter expressing motivation to work with {prof_name} at {institution_name}.
Professor's Research Focus: {prof_areas}
Candidate's Verified Focus: B.Tech in ECE (8.8 CGPA), 1st Rank SIH Hackathon Winner, AURA Speech Translation AI, Deep Learning Image Enhancement, hands-on ML/DL & API development.

Requirements:
- Emphasize genuine motivation for the research environment in {institution_name}.
- Connect the candidate's core interest in machine learning and computer vision to the professor's research topics.
- Keep tone humble, professional, and academic.
- Return ONLY the paragraph text without quotes or preamble.
"""
        llm_output = query_ollama(user_prompt, system_prompt=system_prompt)
        if llm_output and len(llm_output) > 50:
            return llm_output

    # Grounded Deterministic Fallback (Matching Master Template style)
    return (
        f"I am particularly motivated by the research environment at {institution_name} and would be honored to "
        f"contribute to ongoing projects involving {prof_areas}. My background in machine learning models, "
        f"computer vision pipelines, and system integration aligns closely with your laboratory's focus, and I am "
        f"eager to apply my technical skills to support your ongoing research initiatives."
    )
