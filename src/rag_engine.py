import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma

from src.config import config

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    RAG Engine managing ChromaDB vector indexing and Gemini outreach generation chain.
    """

    def __init__(self):
        config.validate_gemini_key()
        
        # Initialize Gemini Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.embedding_model,
            google_api_key=config.gemini_api_key
        )
        
        # Initialize Gemini LLM with low temperature (0.1) for strictly factual generation
        self.llm = ChatGoogleGenerativeAI(
            model=config.gemini_model,
            google_api_key=config.gemini_api_key,
            temperature=0.1
        )

    def _chunk_student_profile(self, text: str) -> List[str]:
        """Splits profile text into distinct paragraphs/chunks."""
        raw_chunks = text.split("\n\n")
        return [c.strip() for c in raw_chunks if c.strip()]

    def build_vector_store(
        self,
        student_profile_text: str,
        professor_papers: List[Dict[str, Any]]
    ) -> Chroma:
        """
        Ingests student profile and professor paper abstracts into ChromaDB
        tagged with metadata distinguishing `source: student` and `source: professor`.
        """
        documents: List[Document] = []

        # 1. Chunk & tag student profile sections
        student_chunks = self._chunk_student_profile(student_profile_text)
        for i, chunk in enumerate(student_chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": "student",
                        "chunk_id": f"student_chunk_{i}"
                    }
                )
            )

        # 2. Add professor paper abstracts
        for i, paper in enumerate(professor_papers):
            content = f"Title: {paper['title']}\nYear: {paper['year']}\nVenue: {paper['venue']}\nAbstract: {paper['abstract']}"
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": "professor",
                        "paper_id": paper.get("paper_id", f"paper_{i}"),
                        "title": paper.get("title", ""),
                        "year": str(paper.get("year", "")),
                        "venue": paper.get("venue", ""),
                        "url": paper.get("url", "")
                    }
                )
            )

        # Build in-memory Chroma vectorstore for ephemeral session
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name="academic_outreach_rag"
        )
        
        logger.info(f"Indexed {len(documents)} items into ChromaDB ({len(student_chunks)} student chunks, {len(professor_papers)} papers).")
        return vectorstore

    def find_overlap(
        self,
        vectorstore: Chroma,
        professor_name: str,
        top_k: int = 3
    ) -> Tuple[List[Document], List[Document]]:
        """
        Retrieves relevant professor research papers and matching student project experience.
        """
        # Search professor documents
        prof_docs = vectorstore.similarity_search(
            query=f"Research publications by {professor_name}",
            k=top_k,
            filter={"source": "professor"}
        )

        # Combine prof titles/topics for student matching query
        prof_topics_summary = " ".join([doc.page_content for doc in prof_docs])
        
        # Search candidate profile for relevant projects
        student_docs = vectorstore.similarity_search(
            query=f"Technical project experience and coursework relevant to: {prof_topics_summary}",
            k=top_k,
            filter={"source": "student"}
        )

        return prof_docs, student_docs

    def generate_email(
        self,
        professor_name: str,
        institution: str,
        prof_docs: List[Document],
        student_docs: List[Document]
    ) -> Dict[str, str]:
        """
        Generates a concise, highly personalized cold outreach email using RAG context.
        """
        prof_context = "\n---\n".join([f"Paper: {doc.metadata.get('title')}\nDetails:\n{doc.page_content}" for doc in prof_docs])
        student_context = "\n---\n".join([doc.page_content for doc in student_docs])

        prompt_template = PromptTemplate(
            template="""You are an expert academic advisor helping a prospective graduate researcher write a professional cold email to a professor.

SENDER NAME: {sender_name}
GITHUB PROFILE: {github_profile}
RESUME DRIVE LINK: {resume_drive_link}
TARGET PROFESSOR: {professor_name}
INSTITUTION: {institution}

RECENT PROFESSOR RESEARCH PAPERS:
{prof_context}

CANDIDATE PROFILE & PROJECTS:
{student_context}

CRITICAL RULES:
1. Identify EXACTLY ONE tangible technical overlap between the candidate's verified project experience and one of the professor's recent research papers.
2. DO NOT include sycophantic flattery (e.g., avoid "groundbreaking research", "prestigious lab", "I was amazed by"). Be objective, direct, and academic.
3. The email body MUST BE STRICTLY UNDER 120 WORDS.
4. Include the candidate's Google Drive Resume link ({resume_drive_link}) and GitHub profile link ({github_profile}) in the email body or signature.
5. Keep the subject line clear and concise (e.g., Prospective PhD Student / Research Inquiry - [Candidate Name]).
6. Output format MUST strictly follow:

SUBJECT: <Subject Line>

BODY:
<Email Body>

Generate the outreach email now:""",
            input_variables=["sender_name", "github_profile", "resume_drive_link", "professor_name", "institution", "prof_context", "student_context"]
        )

        chain = prompt_template | self.llm | StrOutputParser()

        raw_output = chain.invoke({
            "sender_name": config.sender_name,
            "github_profile": config.github_profile,
            "resume_drive_link": config.resume_drive_link,
            "professor_name": professor_name,
            "institution": institution,
            "prof_context": prof_context,
            "student_context": student_context
        })

        # Parse subject and body
        subject, body = self._parse_llm_output(raw_output)
        
        # Calculate word count
        word_count = len(body.split())

        return {
            "subject": subject,
            "body": body,
            "word_count": word_count,
            "matched_paper": prof_docs[0].metadata.get("title", "Recent Publication") if prof_docs else "Recent Research"
        }

    @staticmethod
    def _parse_llm_output(text: str) -> Tuple[str, str]:
        """Parses LLM output into Subject line and Body text."""
        subject = "Prospective Research Inquiry"
        body = text.strip()

        if "SUBJECT:" in text and "BODY:" in text:
            parts = text.split("BODY:")
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body_part = parts[1].strip()
            return subject_part, body_part
        elif text.startswith("Subject:"):
            lines = text.split("\n")
            subject = lines[0].replace("Subject:", "").strip()
            body = "\n".join(lines[1:]).strip()

        return subject, body
