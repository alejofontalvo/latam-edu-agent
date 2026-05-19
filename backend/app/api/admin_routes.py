from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.database import get_db
from app.services.dataset_service import ingest_all_registered_datasets, ingest_registered_dataset
from app.services.data_ingestion_service import DataIngestionService
from app.services.rag_service import index_documents_directory


router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_api_key: str | None = Header(default=None)) -> None:
    if x_admin_api_key != get_settings().admin_api_key:
        raise HTTPException(status_code=401, detail="ADMIN_API_KEY inválida o ausente.")


@router.get("/system/status")
def system_status(_: None = Depends(require_admin)):
    settings = get_settings()
    return {
        "status": "ok",
        "database_url": settings.database_url,
        "data_dir": str(settings.data_dir),
        "chroma_dir": str(settings.chroma_dir),
    }


@router.post("/datasets/refresh")
def refresh_datasets(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return {"datasets": ingest_all_registered_datasets(db)}


@router.post("/datasets/ingest")
def ingest_dataset(registry_id: str, db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return ingest_registered_dataset(registry_id, db)


@router.post("/rag/index-documents")
def index_documents(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return index_documents_directory(db)


@router.post("/ingest")
def ingest_incoming(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return {"reports": DataIngestionService(db).ingest_all_from_folder()}


@router.post("/reindex")
def reindex(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    return index_documents_directory(db)


@router.get("/ingestion-report")
def ingestion_report(_: None = Depends(require_admin)):
    from app.config import get_settings

    reports_dir = get_settings().project_dir / "data" / "ingestion_reports"
    reports = sorted(reports_dir.glob("*.json"), reverse=True)
    return {"reports": [str(path) for path in reports[:20]]}
