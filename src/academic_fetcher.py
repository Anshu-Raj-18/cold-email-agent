import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class AcademicFetcher:
    """
    Fetches research papers and abstracts for target professors using
    Semantic Scholar and OpenAlex APIs.
    """

    def __init__(self, semantic_scholar_api_key: Optional[str] = None):
        self.s2_api_key = semantic_scholar_api_key
        self.s2_headers = {}
        if self.s2_api_key and self.s2_api_key.strip():
            self.s2_headers["x-api-key"] = self.s2_api_key.strip()

    def fetch_papers(
        self,
        professor_name: str,
        institution: str = "",
        max_results: int = 5,
        keywords: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Main interface to fetch papers for a professor.
        Attempts Semantic Scholar first, falling back to OpenAlex if needed.
        """
        logger.info(f"Fetching publications for '{professor_name}' ({institution})...")
        
        papers = self._fetch_from_semantic_scholar(professor_name, institution, max_results, keywords)
        
        if not papers:
            logger.info("Semantic Scholar returned 0 results or had rate limits. Trying OpenAlex fallback...")
            papers = self._fetch_from_openalex(professor_name, institution, max_results, keywords)
            
        return papers

    def _fetch_from_semantic_scholar(
        self,
        professor_name: str,
        institution: str,
        max_results: int,
        keywords: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Queries Semantic Scholar API for papers."""
        papers = []
        try:
            # Query paper search endpoint with author and institution filter or paper topic keywords
            query_str = f"{professor_name} {institution}".strip()
            if keywords:
                query_str += f" {keywords}"
                
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query_str,
                "limit": max_results,
                "fields": "title,abstract,year,venue,citationCount,url,authors"
            }
            
            response = requests.get(url, params=params, headers=self.s2_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                for item in results:
                    abstract = item.get("abstract") or ""
                    # Filter to papers that actually have abstracts or detailed content
                    if item.get("title"):
                        papers.append({
                            "title": item.get("title"),
                            "year": item.get("year", "N/A"),
                            "venue": item.get("venue", "Unknown Venue"),
                            "abstract": abstract if abstract else f"Paper titled '{item.get('title')}' by {professor_name}.",
                            "citation_count": item.get("citationCount", 0),
                            "url": item.get("url", ""),
                            "paper_id": item.get("paperId", ""),
                            "source_api": "Semantic Scholar"
                        })
            else:
                logger.warning(f"Semantic Scholar API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Error fetching from Semantic Scholar: {e}")
            
        return papers

    def _fetch_from_openalex(
        self,
        professor_name: str,
        institution: str,
        max_results: int,
        keywords: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Queries OpenAlex API for papers."""
        papers = []
        try:
            query_str = f"{professor_name} {institution}".strip()
            if keywords:
                query_str += f" {keywords}"

            url = "https://api.openalex.org/works"
            params = {
                "search": query_str,
                "per_page": max_results,
                "sort": "publication_year:desc"
            }
            headers = {"User-Agent": "ProfOutreachRAG/1.0 (mailto:outreach@example.com)"}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for item in results:
                    title = item.get("title", "")
                    year = item.get("publication_year", "N/A")
                    host_venue = item.get("primary_location", {}).get("source", {}) or {}
                    venue = host_venue.get("display_name", "Academic Journal/Conference")
                    
                    # OpenAlex stores abstract as inverted index
                    inv_index = item.get("abstract_inverted_index")
                    abstract = self._reconstruct_openalex_abstract(inv_index)
                    if not abstract:
                        abstract = f"Research paper titled '{title}' published in {year}."

                    citations = item.get("cited_by_count", 0)
                    doi_url = item.get("doi") or item.get("id") or ""

                    if title:
                        papers.append({
                            "title": title,
                            "year": year,
                            "venue": venue,
                            "abstract": abstract,
                            "citation_count": citations,
                            "url": doi_url,
                            "paper_id": item.get("id", ""),
                            "source_api": "OpenAlex"
                        })
            else:
                logger.warning(f"OpenAlex API status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Error fetching from OpenAlex: {e}")

        return papers

    @staticmethod
    def _reconstruct_openalex_abstract(inv_index: Optional[Dict[str, List[int]]]) -> str:
        """Reconstructs text abstract from OpenAlex inverted index structure."""
        if not inv_index:
            return ""
        try:
            word_positions = []
            for word, positions in inv_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort(key=lambda x: x[0])
            return " ".join([word for _, word in word_positions])
        except Exception:
            return ""
