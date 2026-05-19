import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import httpx
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.config.column_mappings import COLUMN_MAPPINGS, NORMALIZED_COLUMNS
from app.config.datasets_registry import DATASETS_REGISTRY
from app.models.entities import Dataset, DatasetColumn, NormalizedResult
from app.utils.data_cleaning import prepare_dataset
from app.utils.file_reader import read_tabular_file


settings = get_settings()
SCORE_COLUMNS = [
    "math_score",
    "reading_score",
    "science_score",
    "social_score",
    "english_score",
    "global_score",
]


def _safe_filename(filename: str) -> str:
    return Path(filename).name.replace(" ", "_")


def _registry_key(registry_id: str) -> str:
    parts = registry_id.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else registry_id


def _resolve_path(path: str | Path) -> Path:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = settings.project_dir / file_path
    return file_path


def detect_schema(df: pd.DataFrame) -> list[dict]:
    schema = []
    for column in df.columns:
        series = df[column]
        samples = series.dropna().astype(str).head(5).tolist()
        schema.append(
            {
                "name": column,
                "dtype": str(series.dtype),
                "null_count": int(series.isna().sum()),
                "non_null_count": int(series.notna().sum()),
                "sample_values": samples,
            }
        )
    return schema


def generate_data_profile(df: pd.DataFrame) -> dict:
    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(exclude="number")
    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "numeric_columns": numeric.columns.tolist(),
        "categorical_columns": categorical.columns.tolist(),
        "missing_values": {column: int(value) for column, value in df.isna().sum().items()},
        "preview": df.head(10).to_dict(orient="records"),
    }


def read_registered_dataset(registry_item: dict[str, Any]) -> pd.DataFrame:
    if registry_item.get("format") == "socrata_api":
        token = settings.datos_gov_co_app_token
        if not token:
            raise ValueError(
                f"{registry_item['id']} requiere DATOS_GOV_CO_APP_TOKEN para consultar datos.gov.co."
            )
        response = httpx.get(
            registry_item["path"],
            headers={"X-App-Token": token},
            params={"$limit": registry_item.get("max_rows", 50000)},
            timeout=90,
        )
        response.raise_for_status()
        return pd.DataFrame(response.json())

    path = _resolve_path(registry_item["path"])
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo registrado: {path}")
    max_rows = registry_item.get("max_rows")
    if registry_item.get("format") == "csv":
        return pd.read_csv(
            path,
            sep=registry_item.get("delimiter", ","),
            encoding=registry_item.get("encoding", "utf-8"),
            nrows=max_rows,
        )
    return read_tabular_file(path)


def normalize_registered_dataset(df: pd.DataFrame, registry_item: dict[str, Any]) -> pd.DataFrame:
    original = df.copy()
    mapping = COLUMN_MAPPINGS.get(_registry_key(registry_item["id"]), {})
    renamed = original.rename(columns=mapping)
    renamed = prepare_dataset(renamed)

    normalized = pd.DataFrame(index=renamed.index)
    for column in NORMALIZED_COLUMNS:
        normalized[column] = None

    normalized["dataset_id"] = registry_item["id"]
    normalized["country"] = registry_item["country"]
    normalized["exam"] = registry_item["exam"]
    if "year" in renamed.columns:
        normalized["year"] = pd.to_numeric(renamed["year"], errors="coerce")
    else:
        normalized["year"] = registry_item.get("year")

    fallback_columns = {
        "region": ["region", "departamento", "estado", "uf"],
        "city": ["city", "municipio", "cidade"],
        "student_id": ["student_id", "consecutivo", "id_estudiante"],
        "gender": ["gender", "genero", "sexo"],
        "age": ["age", "edad", "idade"],
        "institution_type": ["institution_type", "school_type", "tipo_colegio"],
        "socioeconomic_level": ["socioeconomic_level", "estrato", "nivel_socioeconomico"],
        "math_score": ["math_score", "score_math", "matematicas"],
        "reading_score": ["reading_score", "score_reading", "lectura"],
        "science_score": ["science_score", "score_science", "ciencias"],
        "social_score": ["social_score", "sociales"],
        "english_score": ["english_score", "ingles"],
        "global_score": ["global_score", "score_global", "puntaje_global"],
    }

    for normalized_column, candidates in fallback_columns.items():
        for candidate in candidates:
            if candidate in renamed.columns:
                normalized[normalized_column] = renamed[candidate]
                break

    if normalized["student_id"].isna().all():
        normalized["student_id"] = [
            f"{registry_item['id']}_{index + 1}" for index in range(len(normalized))
        ]
    for score in SCORE_COLUMNS:
        normalized[score] = pd.to_numeric(normalized[score], errors="coerce")

    score_frame = normalized[SCORE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    normalized["global_score"] = normalized["global_score"].fillna(score_frame.mean(axis=1))
    if registry_item.get("store_raw_data_json", True):
        normalized["raw_data_json"] = original.astype(object).where(pd.notna(original), None).apply(
            lambda row: json.dumps(row.to_dict(), ensure_ascii=False), axis=1
        )
    else:
        normalized["raw_data_json"] = "{}"
    return normalized


def _dataset_payload(dataset: Dataset) -> dict:
    return {
        "id": dataset.id,
        "registry_id": dataset.registry_id,
        "name": dataset.name,
        "country": dataset.country,
        "exam": dataset.exam,
        "year": dataset.year,
        "year_range": dataset.year_range,
        "description": dataset.description,
        "source": dataset.source,
        "source_url": dataset.source_url,
        "areas": json.loads(dataset.areas_json or "[]"),
        "status": dataset.status,
        "public": dataset.public,
        "is_demo": dataset.is_demo,
        "original_filename": dataset.original_filename,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "file_size": dataset.file_size,
        "processed_at": dataset.processed_at.isoformat() if dataset.processed_at else None,
        "created_at": dataset.created_at.isoformat(),
    }


def list_datasets(db: Session, public_only: bool = True) -> list[dict]:
    query = db.query(Dataset)
    if public_only:
        query = query.filter(Dataset.public.is_(True))
    datasets = query.order_by(Dataset.country, Dataset.exam, Dataset.year.desc()).all()
    return [_dataset_payload(item) for item in datasets]


def resolve_dataset(dataset_id: int | str, db: Session) -> Dataset:
    dataset = None
    if isinstance(dataset_id, int) or str(dataset_id).isdigit():
        dataset = db.get(Dataset, int(dataset_id))
    if not dataset:
        dataset = db.query(Dataset).filter(Dataset.registry_id == str(dataset_id)).first()
    if not dataset:
        raise ValueError(f"No existe el dataset {dataset_id}.")
    return dataset


def load_processed_dataset(dataset_id: int | str, db: Session) -> pd.DataFrame:
    dataset = resolve_dataset(dataset_id, db)
    return pd.read_csv(dataset.processed_path)


def get_dataset_summary(dataset_id: int | str, db: Session) -> dict:
    dataset = resolve_dataset(dataset_id, db)
    df = pd.read_csv(dataset.processed_path)
    columns = [
        {
            "name": column.name,
            "dtype": column.dtype,
            "null_count": column.null_count,
            "non_null_count": column.non_null_count,
            "sample_values": json.loads(column.sample_values or "[]"),
        }
        for column in dataset.columns
    ]
    return {"dataset": _dataset_payload(dataset), "columns": columns, "profile": generate_data_profile(df)}


def get_dataset_columns(dataset_id: int | str, db: Session) -> list[dict]:
    return get_dataset_summary(dataset_id, db)["columns"]


def get_dataset_preview(dataset_id: int | str, db: Session, limit: int = 20) -> dict:
    dataset = resolve_dataset(dataset_id, db)
    df = pd.read_csv(dataset.processed_path)
    return {"dataset": _dataset_payload(dataset), "records": df.head(limit).to_dict("records")}


def get_dataset_filters(dataset_id: int | str, db: Session) -> dict:
    df = load_processed_dataset(dataset_id, db)
    filter_columns = ["country", "exam", "year", "region", "gender", "institution_type", "socioeconomic_level"]
    return {
        column: sorted([value for value in df[column].dropna().astype(str).unique().tolist()])
        for column in filter_columns
        if column in df.columns
    }


def get_countries(db: Session) -> list[dict]:
    datasets = list_datasets(db)
    countries = {}
    for item in datasets:
        country = item["country"]
        countries.setdefault(
            country,
            {
                "country": country,
                "datasets": 0,
                "records": 0,
                "exams": set(),
                "years": set(),
                "status": "disponible",
            },
        )
        countries[country]["datasets"] += 1
        countries[country]["records"] += item["row_count"]
        countries[country]["exams"].add(item["exam"])
        if item["year"]:
            countries[country]["years"].add(item["year"])

    result = []
    for item in countries.values():
        result.append(
            {
                **item,
                "exams": sorted(item["exams"]),
                "years": sorted(item["years"]),
            }
        )
    return sorted(result, key=lambda row: row["country"])


def get_country_exams(country: str, db: Session) -> list[dict]:
    return [
        item
        for item in list_datasets(db)
        if item["country"].lower() == country.lower()
    ]


def get_exams(db: Session) -> list[dict]:
    exams = {}
    for item in list_datasets(db):
        exams.setdefault(item["exam"], {"exam": item["exam"], "datasets": 0, "countries": set(), "records": 0})
        exams[item["exam"]]["datasets"] += 1
        exams[item["exam"]]["countries"].add(item["country"])
        exams[item["exam"]]["records"] += item["row_count"]
    return [
        {**value, "countries": sorted(value["countries"])}
        for value in sorted(exams.values(), key=lambda row: row["exam"])
    ]


def ingest_registered_dataset(registry_id: str, db: Session) -> dict:
    registry_item = next((item for item in DATASETS_REGISTRY if item["id"] == registry_id), None)
    if not registry_item:
        raise ValueError(f"Dataset no registrado: {registry_id}")

    raw_path = _resolve_path(registry_item["path"])
    original_df = read_registered_dataset(registry_item)
    normalized_df = normalize_registered_dataset(original_df, registry_item)
    processed_path = settings.processed_dir / f"{registry_item['id']}_processed.csv"
    normalized_df.to_csv(processed_path, index=False)

    existing = db.query(Dataset).filter(Dataset.registry_id == registry_item["id"]).first()
    dataset = existing or Dataset(registry_id=registry_item["id"])
    dataset.name = registry_item["name"]
    dataset.country = registry_item["country"]
    dataset.exam = registry_item["exam"]
    dataset.year = registry_item.get("year")
    dataset.year_range = registry_item.get("year_range", str(registry_item.get("year", "")))
    dataset.description = registry_item.get("description", "")
    dataset.source = registry_item.get("source", "")
    dataset.source_url = registry_item.get("source_url", "")
    dataset.areas_json = json.dumps(registry_item.get("areas", []), ensure_ascii=False)
    dataset.status = registry_item.get("status", "procesado")
    dataset.public = bool(registry_item.get("public", True))
    dataset.is_demo = bool(registry_item.get("is_demo", False))
    dataset.original_filename = raw_path.name
    dataset.raw_path = str(raw_path)
    dataset.processed_path = str(processed_path)
    dataset.row_count = int(len(normalized_df))
    dataset.column_count = int(len(normalized_df.columns))
    dataset.file_size = raw_path.stat().st_size if raw_path.exists() else 0
    dataset.processed_at = datetime.utcnow()
    if not existing:
        db.add(dataset)
    db.flush()

    db.query(DatasetColumn).filter(DatasetColumn.dataset_id == dataset.id).delete()
    schema = detect_schema(normalized_df)
    for column in schema:
        db.add(
            DatasetColumn(
                dataset_id=dataset.id,
                name=column["name"],
                dtype=column["dtype"],
                null_count=column["null_count"],
                non_null_count=column["non_null_count"],
                sample_values=json.dumps(column["sample_values"], ensure_ascii=False),
            )
        )

    db.query(NormalizedResult).filter(
        NormalizedResult.dataset_registry_id == registry_item["id"]
    ).delete()
    records = []
    for row in normalized_df.to_dict("records"):
        records.append(
            NormalizedResult(
                dataset_registry_id=row.get("dataset_id"),
                country=row.get("country"),
                exam=row.get("exam"),
                year=int(row["year"]) if pd.notna(row.get("year")) else None,
                student_id=row.get("student_id"),
                region=row.get("region") if pd.notna(row.get("region")) else None,
                city=row.get("city") if pd.notna(row.get("city")) else None,
                gender=row.get("gender") if pd.notna(row.get("gender")) else None,
                age=float(row["age"]) if pd.notna(row.get("age")) else None,
                institution_type=row.get("institution_type") if pd.notna(row.get("institution_type")) else None,
                socioeconomic_level=row.get("socioeconomic_level") if pd.notna(row.get("socioeconomic_level")) else None,
                math_score=float(row["math_score"]) if pd.notna(row.get("math_score")) else None,
                reading_score=float(row["reading_score"]) if pd.notna(row.get("reading_score")) else None,
                science_score=float(row["science_score"]) if pd.notna(row.get("science_score")) else None,
                social_score=float(row["social_score"]) if pd.notna(row.get("social_score")) else None,
                english_score=float(row["english_score"]) if pd.notna(row.get("english_score")) else None,
                global_score=float(row["global_score"]) if pd.notna(row.get("global_score")) else None,
                raw_data_json=row.get("raw_data_json", "{}"),
            )
        )
    db.bulk_save_objects(records)
    db.commit()
    db.refresh(dataset)
    return _dataset_payload(dataset)


def ingest_all_registered_datasets(db: Session) -> list[dict]:
    ingested = []
    for item in DATASETS_REGISTRY:
        if item.get("format") == "socrata_api" and item.get("requires_token") and not settings.datos_gov_co_app_token:
            continue
        ingested.append(ingest_registered_dataset(item["id"], db))
    return ingested


async def save_uploaded_dataset(file: UploadFile, db: Session) -> dict:
    filename = _safe_filename(file.filename or "dataset.csv")
    raw_path = settings.raw_dir / "admin_uploads" / filename
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with raw_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    original_df = read_tabular_file(raw_path)
    cleaned_df = prepare_dataset(original_df)
    processed_path = settings.processed_dir / f"{raw_path.stem}_processed.csv"
    cleaned_df.to_csv(processed_path, index=False)
    return {"path": str(processed_path), "profile": generate_data_profile(cleaned_df)}
