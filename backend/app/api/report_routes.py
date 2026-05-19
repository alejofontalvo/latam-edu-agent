from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.powerbi_service import (
    dataset_json,
    export_csv,
    export_excel,
    normalized_results,
    powerbi_catalog,
    powerbi_comparisons,
    powerbi_data_quality,
    powerbi_kpis,
)


router = APIRouter(tags=["reports"])


@router.get("/reports/export/csv/{dataset_id}")
def report_csv(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return export_csv(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/reports/export/excel/{dataset_id}")
def report_excel(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return export_excel(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/powerbi/dataset/{dataset_id}")
def powerbi_dataset(dataset_id: str, db: Session = Depends(get_db)):
    try:
        return dataset_json(dataset_id, db)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/powerbi/catalog")
def powerbi_catalog_endpoint(db: Session = Depends(get_db)):
    return powerbi_catalog(db)


@router.get("/powerbi/normalized-results")
def powerbi_normalized_results(db: Session = Depends(get_db)):
    return normalized_results(db)


@router.get("/powerbi/kpis")
def powerbi_kpis_endpoint(db: Session = Depends(get_db)):
    return powerbi_kpis(db)


@router.get("/powerbi/comparisons")
def powerbi_comparisons_endpoint(db: Session = Depends(get_db)):
    return powerbi_comparisons(db)


@router.get("/powerbi/data-quality")
def powerbi_data_quality_endpoint(db: Session = Depends(get_db)):
    return powerbi_data_quality(db)
