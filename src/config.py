import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Application Configuration Settings"""
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "models/text-embedding-004"))
    
    gmail_credentials_file: Path = field(
        default_factory=lambda: Path(os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"))
    )
    gmail_token_file: Path = field(
        default_factory=lambda: Path(os.getenv("GMAIL_TOKEN_FILE", "token.json"))
    )
    
    sender_name: str = field(default_factory=lambda: os.getenv("SENDER_NAME", "Anshu Raj"))
    sender_email: str = field(default_factory=lambda: os.getenv("SENDER_EMAIL", "qismcdeltat@gmail.com"))
    github_profile: str = field(default_factory=lambda: os.getenv("GITHUB_PROFILE", "https://github.com/Anshu-Raj-18"))
    resume_drive_link: str = field(
        default_factory=lambda: os.getenv("RESUME_DRIVE_LINK", "https://drive.google.com/file/d/1XW5vi2Rfq8miIzVFq7OhoBLv9d0olVnX/view?usp=sharing")
    )
    semantic_scholar_api_key: str = field(default_factory=lambda: os.getenv("SEMANTIC_SCHOLAR_API_KEY", ""))
    
    profile_path: Path = field(default_factory=lambda: Path("profile/resume_summary.txt"))
    chroma_db_dir: Path = field(default_factory=lambda: Path(".chroma_db"))

    def validate_gemini_key(self) -> None:
        """Validates that Gemini API key is present."""
        if not self.gemini_api_key or self.gemini_api_key.strip() == "" or self.gemini_api_key == "your_gemini_api_key_here":
            raise ValueError(
                "\n[ERROR] GEMINI_API_KEY is not set in your .env file.\n"
                "Please set GEMINI_API_KEY=your_key_here in .env to use Gemini embeddings and RAG chain."
            )

    def validate_profile(self) -> None:
        """Validates that student profile exists."""
        if not self.profile_path.exists():
            raise FileNotFoundError(
                f"\n[ERROR] Profile file not found at {self.profile_path}.\n"
                "Please create 'profile/resume_summary.txt' with your technical background."
            )

config = Config()
