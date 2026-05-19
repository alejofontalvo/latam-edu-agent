from bootstrap import BACKEND_DIR  # noqa: F401
from app.models.database import SessionLocal, init_db
from app.services.rag_service import index_documents_directory


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        result = index_documents_directory(db)
        print(f"Documentos indexados: {len(result['indexed'])}, chunks: {result['total_chunks']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
