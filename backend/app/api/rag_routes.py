from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.schemas import RagQueryRequest
from app.services.rag_service import generate_answer_with_context, list_documents, retrieve_context, upload_documents


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/upload-documents")
async def rag_upload(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    try:
        return await upload_documents(files, db)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/documents")
def rag_documents(db: Session = Depends(get_db)):
    return list_documents(db)


@router.post("/query")
def rag_query(payload: RagQueryRequest):
    try:
        retrieved = retrieve_context(payload.question, payload.top_k)
        return {
            "answer": generate_answer_with_context(payload.question, retrieved["context"]),
            "sources": retrieved["sources"],
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
