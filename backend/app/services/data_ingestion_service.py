from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.entities import Dataset, DatasetColumn
from app.services.column_mapping_service import ColumnMappingService
from app.services.schema_detection_service import SchemaDetectionService, infer_metadata_from_filename


settings = get_settings()


class DataIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.schema = SchemaDetectionService()
        self.mapper = ColumnMappingService()

    def detect_file_format(self, path: str | Path) -> str:
        suffix = Path(path).suffix.lower()
        if suffix == ".csv" or suffix == ".txt":
            return "csv"
        if suffix in {".xlsx", ".xls"}:
            return "excel"
        if suffix == ".json":
            return "json"
        if suffix == ".parquet":
            return "parquet"
        raise ValueError(f"Formato no soportado: {suffix}")

    def read_csv(self, path: str | Path) -> pd.DataFrame:
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            for sep in [",", ";", "\t", "|"]:
                try:
                    df = pd.read_csv(path, encoding=encoding, sep=sep, low_memory=False)
                    if len(df.columns) > 1:
                        return df
                except Exception:
                    continue
        raise ValueError(f"No pude leer CSV/TXT: {path}")

    def read_excel(self, path: str | Path) -> pd.DataFrame:
        return pd.read_excel(path)

    def read_json(self, path: str | Path) -> pd.DataFrame:
        return pd.read_json(path)

    def read_parquet(self, path: str | Path) -> pd.DataFrame:
        return pd.read_parquet(path)

    def ingest_dataset_from_file(self, path: str | Path, data_mode: str = "real") -> dict[str, Any]:
        file_path = Path(path)
        file_format = self.detect_file_format(file_path)
        readers = {
            "csv": self.read_csv,
            "excel": self.read_excel,
            "json": self.read_json,
            "parquet": self.read_parquet,
        }
        df = readers[file_format](file_path)
        metadata = self.infer_metadata(file_path, df)
        dataset_id = metadata["dataset_id"]
        normalized = self.mapper.normalize_dataset(
            df=df,
            dataset_id=dataset_id,
            fallback_country=metadata["detected_country"],
            fallback_exam=metadata["detected_exam"],
            fallback_year=metadata["detected_years"][0] if metadata["detected_years"] else None,
            data_mode=data_mode,
            source_file=file_path.name,
        )
        processed_path = settings.processed_dir / f"{dataset_id}_long_processed.csv"
        normalized.to_csv(processed_path, index=False)
        self.save_processed_dataset(dataset_id, file_path, processed_path, metadata, normalized, data_mode)
        self.save_raw_metadata(dataset_id, metadata)
        return {
            "dataset_id": dataset_id,
            "source": str(file_path),
            "processed_path": str(processed_path),
            "rows": int(len(normalized)),
            "metadata": metadata,
        }

    def ingest_all_from_folder(self, folder: str | Path | None = None) -> list[dict[str, Any]]:
        incoming = Path(folder) if folder else settings.project_dir / "data" / "incoming"
        archive = settings.project_dir / "data" / "archive"
        reports = []
        for path in incoming.iterdir():
            if not path.is_file() or path.name.startswith("."):
                continue
            report = self.ingest_dataset_from_file(path)
            archived_path = archive / path.name
            archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), archived_path)
            report["archived_path"] = str(archived_path)
            reports.append(report)
        report_path = settings.project_dir / "data" / "ingestion_reports" / f"ingestion_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
        return reports

    def infer_metadata(self, path: str | Path, df: pd.DataFrame) -> dict[str, Any]:
        filename_meta = infer_metadata_from_filename(path)
        schema_report = self.schema.build_report(df)
        dataset_id = Path(path).stem.lower().replace(" ", "_").replace("-", "_")
        mapped = self.mapper.suggest_column_mappings(schema_report["columns"])
        return {
            "dataset_id": dataset_id,
            "file_name": Path(path).name,
            "file_path": str(path),
            **filename_meta,
            "detected_subjects": sorted(set(value.split("::", 1)[1] for value in mapped.values() if value.startswith("subject::"))),
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "numeric_columns": schema_report["numeric_columns"],
            "categorical_columns": schema_report["categorical_columns"],
            "mapped_columns": mapped,
            "unmapped_columns": [column for column in schema_report["columns"] if column not in mapped],
            "quality_score": self._quality_score(df, mapped),
            "status": "procesado",
        }

    def save_raw_metadata(self, dataset_id: str, metadata: dict[str, Any]) -> None:
        path = settings.metadata_dir / f"{dataset_id}.json"
        path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_processed_dataset(
        self,
        dataset_id: str,
        raw_path: Path,
        processed_path: Path,
        metadata: dict[str, Any],
        normalized: pd.DataFrame,
        data_mode: str,
    ) -> None:
        existing = self.db.query(Dataset).filter(Dataset.registry_id == dataset_id).first()
        dataset = existing or Dataset(registry_id=dataset_id)
        dataset.name = raw_path.stem.replace("_", " ").title()
        dataset.country = metadata["detected_country"]
        dataset.exam = metadata["detected_exam"]
        dataset.year = metadata["detected_years"][0] if metadata["detected_years"] else None
        dataset.year_range = ", ".join(str(year) for year in metadata["detected_years"])
        dataset.description = f"Dataset ingerido dinámicamente desde data/incoming: {raw_path.name}"
        dataset.source = "Ingesta dinámica"
        dataset.source_url = ""
        dataset.areas_json = json.dumps(metadata["detected_subjects"], ensure_ascii=False)
        dataset.status = "disponible"
        dataset.public = True
        dataset.is_demo = data_mode == "demo"
        dataset.original_filename = raw_path.name
        dataset.raw_path = str(raw_path)
        dataset.processed_path = str(processed_path)
        dataset.row_count = int(len(normalized))
        dataset.column_count = int(len(normalized.columns))
        dataset.file_size = raw_path.stat().st_size
        dataset.processed_at = datetime.utcnow()
        if not existing:
            self.db.add(dataset)
        self.db.flush()
        self.db.query(DatasetColumn).filter(DatasetColumn.dataset_id == dataset.id).delete()
        for column in normalized.columns:
            series = normalized[column]
            self.db.add(
                DatasetColumn(
                    dataset_id=dataset.id,
                    name=column,
                    dtype=str(series.dtype),
                    null_count=int(series.isna().sum()),
                    non_null_count=int(series.notna().sum()),
                    sample_values=json.dumps(series.dropna().astype(str).head(5).tolist(), ensure_ascii=False),
                )
            )
        self.db.commit()

    def _quality_score(self, df: pd.DataFrame, mapped: dict[str, str]) -> float:
        missing_ratio = float(df.isna().mean().mean()) if not df.empty else 1
        mapping_ratio = len(mapped) / max(1, len(df.columns))
        return round(max(0, min(100, 100 - missing_ratio * 45 + mapping_ratio * 25)), 2)
