from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.services.dataset_catalog_service import DatasetCatalogService


router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("")
def catalog(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).get_dataset_catalog()


@router.get("/countries")
def countries(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).get_available_countries()


@router.get("/exams")
def exams(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).get_available_exams()


@router.get("/years")
def years(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).get_available_years()


@router.get("/subjects")
def subjects(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).get_available_subjects()


@router.get("/variables")
def variables(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).get_comparable_variables()


@router.get("/datasets")
def datasets(db: Session = Depends(get_db)):
    return DatasetCatalogService(db).scan_available_datasets()
