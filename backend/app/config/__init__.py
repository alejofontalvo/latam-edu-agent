from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


class Settings:
    app_name: str = "LATAM EduAgent"
    app_version: str = "0.2.0"
    api_prefix: str = ""
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    base_dir: Path = BACKEND_DIR
    project_dir: Path = Path(__file__).resolve().parents[3]
    data_dir: Path = project_dir / "data"
    raw_dir: Path = data_dir / "raw"
    processed_dir: Path = data_dir / "processed"
    documents_dir: Path = data_dir / "documents"
    metadata_dir: Path = data_dir / "metadata"
    exports_dir: Path = data_dir / "exports"
    powerbi_exports_dir: Path = exports_dir / "powerbi"
    chroma_dir: Path = data_dir / "chroma"

    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{(base_dir / 'latam_edu_agent.db').as_posix()}"
    )

    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    admin_api_key: str = os.getenv("ADMIN_API_KEY", "latam-admin-dev")
    datos_gov_co_app_token: str | None = os.getenv("DATOS_GOV_CO_APP_TOKEN")

    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "200"))
    rag_collection_name: str = os.getenv("RAG_COLLECTION_NAME", "latam_edu_documents")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))

    def ensure_directories(self) -> None:
        for path in [
            self.raw_dir,
            self.processed_dir,
            self.documents_dir,
            self.metadata_dir,
            self.exports_dir,
            self.powerbi_exports_dir,
            self.chroma_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
