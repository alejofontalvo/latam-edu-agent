from __future__ import annotations

import json
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.models.entities import Dataset
from app.services.dataset_service import list_datasets, load_processed_dataset
from app.services.schema_detection_service import SchemaDetectionService


class DatasetCatalogService:
    def __init__(self, db: Session):
        self.db = db
        self.schema_detector = SchemaDetectionService()

    def scan_available_datasets(self) -> list[dict[str, Any]]:
        return list_datasets(self.db)

    def register_dataset(self, metadata: dict[str, Any]) -> dict[str, Any]:
        dataset = Dataset(**metadata)
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return {"id": dataset.id, "registry_id": dataset.registry_id}

    def get_dataset_catalog(self) -> dict[str, Any]:
        datasets = self.scan_available_datasets()
        return {
            "datasets": datasets,
            "countries": self.get_available_countries(),
            "exams": self.get_available_exams(),
            "years": self.get_available_years(),
            "subjects": self.get_available_subjects(),
            "variables": self.get_comparable_variables(),
            "data_modes": sorted(set("demo" if item.get("is_demo") else "real" for item in datasets)),
        }

    def get_available_countries(self) -> list[str]:
        return sorted(set(item["country"] for item in self.scan_available_datasets() if item.get("country")))

    def get_available_exams(self) -> list[str]:
        return sorted(set(item["exam"] for item in self.scan_available_datasets() if item.get("exam")))

    def get_available_years(self) -> list[int]:
        return sorted(set(item["year"] for item in self.scan_available_datasets() if item.get("year")))

    def get_available_subjects(self) -> list[str]:
        subjects = set()
        for item in self.scan_available_datasets():
            subjects.update(item.get("areas") or [])
        return sorted(subjects)

    def get_dataset_schema(self, dataset_id: str) -> dict[str, Any]:
        df = load_processed_dataset(dataset_id, self.db)
        return self.schema_detector.build_report(df)

    def get_dataset_quality_report(self, dataset_id: str) -> dict[str, Any]:
        df = load_processed_dataset(dataset_id, self.db)
        missing_ratio = float(df.isna().mean().mean()) if not df.empty else 1.0
        numeric_columns = self.schema_detector.detect_numeric_columns(df)
        quality_score = max(0, round(100 - missing_ratio * 60 - max(0, 5 - len(numeric_columns)) * 4, 2))
        return {
            "dataset_id": dataset_id,
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "missing_ratio": round(missing_ratio, 4),
            "numeric_columns": numeric_columns,
            "quality_score": quality_score,
            "status": "ok" if quality_score >= 60 else "revisar",
        }

    def get_comparable_variables(self) -> dict[str, list[str]]:
        return {
            "numeric": [
                "score",
                "score_normalized_0_100",
                "global_score",
                "math_score",
                "reading_score",
                "science_score",
                "social_score",
                "english_score",
            ],
            "categorical": ["country", "exam", "year", "region", "gender", "institution_type", "socioeconomic_level", "subject"],
        }
