from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.dataset_service import (
    get_countries,
    get_country_exams,
    get_dataset_columns,
    get_dataset_filters,
    get_dataset_preview,
    get_dataset_summary,
    get_exams,
    list_datasets,
    resolve_dataset,
)


router = APIRouter(tags=["datasets"])


@router.get("/datasets")
def datasets(db: Session = Depends(get_db)):
    return list_datasets(db)


@router.get("/datasets/{dataset_id}")
def dataset_detail(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return get_dataset_summary(dataset_id, db)["dataset"]
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/summary")
def dataset_summary(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return get_dataset_summary(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/columns")
def dataset_columns(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return get_dataset_columns(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/filters")
def dataset_filters(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return get_dataset_filters(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/datasets/{dataset_id}/preview")
def dataset_preview(dataset_id: str, limit: int = 20, db: Session = Depends(get_db)):
    try:
        return get_dataset_preview(dataset_id, db, limit)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/countries")
def countries(db: Session = Depends(get_db)):
    return get_countries(db)


@router.get("/countries/{country}/exams")
def country_exams(country: str, db: Session = Depends(get_db)):
    return get_country_exams(country, db)


@router.get("/exams")
def exams(db: Session = Depends(get_db)):
    return get_exams(db)
