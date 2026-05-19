from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.analytics_engine import AnalyticsEngine
from app.services.analytics_service import compare_groups, get_global_kpis
from app.services.dataset_service import get_countries, get_exams, list_datasets, load_processed_dataset, resolve_dataset


settings = get_settings()


def export_csv(dataset_id: int | str, db: Session) -> dict:
    dataset = resolve_dataset(dataset_id, db)
    df = load_processed_dataset(dataset.registry_id, db)
    path = settings.exports_dir / f"dataset_{dataset.registry_id}.csv"
    df.to_csv(path, index=False)
    return {"dataset_id": dataset.registry_id, "path": str(path), "rows": int(len(df))}


def export_excel(dataset_id: int | str, db: Session) -> dict:
    dataset = resolve_dataset(dataset_id, db)
    df = load_processed_dataset(dataset.registry_id, db)
    path = settings.exports_dir / f"dataset_{dataset.registry_id}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="datos_normalizados", index=False)
        dictionary = pd.DataFrame(
            [{"column": column, "dtype": str(df[column].dtype)} for column in df.columns]
        )
        dictionary.to_excel(writer, sheet_name="diccionario", index=False)
    return {"dataset_id": dataset.registry_id, "path": str(path), "rows": int(len(df))}


def dataset_json(dataset_id: int | str, db: Session) -> dict:
    dataset = resolve_dataset(dataset_id, db)
    df = load_processed_dataset(dataset.registry_id, db)
    return {
        "dataset_id": dataset.registry_id,
        "rows": int(len(df)),
        "columns": df.columns.tolist(),
        "records": df.head(5000).to_dict(orient="records"),
        "powerbi_note": "Para grandes volúmenes usa exportación CSV/Excel o conecta Power BI a PostgreSQL.",
    }


def powerbi_catalog(db: Session) -> dict:
    return {"datasets": list_datasets(db), "countries": get_countries(db), "exams": get_exams(db)}


def normalized_results(db: Session) -> dict:
    df = AnalyticsEngine(db).load_long_results()
    return {
        "rows": int(len(df)),
        "columns": df.columns.tolist(),
        "records": df.head(10000).to_dict(orient="records"),
    }


def powerbi_kpis(db: Session) -> dict:
    return AnalyticsEngine(db).calculate_kpis()


def powerbi_comparisons(db: Session) -> dict:
    engine = AnalyticsEngine(db)
    return {
        "country": engine.compare_available_countries(),
        "year": engine.analyze_trends(),
        "gender": engine.analyze_gaps("brechas por género"),
        "institution_type": engine.analyze_gaps("brechas por institución"),
    }


def powerbi_data_quality(db: Session) -> dict:
    from app.services.dataset_catalog_service import DatasetCatalogService

    service = DatasetCatalogService(db)
    reports = []
    for dataset in list_datasets(db):
        reports.append(service.get_dataset_quality_report(dataset["registry_id"]))
    return {"reports": reports}


def export_powerbi_files(db: Session) -> dict:
    settings.powerbi_exports_dir.mkdir(parents=True, exist_ok=True)
    catalog = pd.DataFrame(list_datasets(db))
    countries = pd.DataFrame(get_countries(db))
    exams = pd.DataFrame(get_exams(db))
    kpis = pd.DataFrame([get_global_kpis(db)])
    comparisons = pd.DataFrame(powerbi_comparisons(db)["country"]["data"])
    normalized = AnalyticsEngine(db).load_long_results()
    quality = pd.DataFrame(powerbi_data_quality(db)["reports"])

    outputs = {
        "catalog": settings.powerbi_exports_dir / "catalog.csv",
        "normalized_results": settings.powerbi_exports_dir / "normalized_results.csv",
        "countries": settings.powerbi_exports_dir / "countries.csv",
        "exams": settings.powerbi_exports_dir / "exams.csv",
        "kpis": settings.powerbi_exports_dir / "kpis.csv",
        "comparisons": settings.powerbi_exports_dir / "comparisons.csv",
        "data_quality": settings.powerbi_exports_dir / "data_quality.csv",
    }
    catalog.to_csv(outputs["catalog"], index=False)
    normalized.to_csv(outputs["normalized_results"], index=False)
    countries.to_csv(outputs["countries"], index=False)
    exams.to_csv(outputs["exams"], index=False)
    kpis.to_csv(outputs["kpis"], index=False)
    comparisons.to_csv(outputs["comparisons"], index=False)
    quality.to_csv(outputs["data_quality"], index=False)
    return {key: str(value) for key, value in outputs.items()}


def ensure_export_path(path: str) -> Path:
    export_path = Path(path)
    if settings.exports_dir not in export_path.parents and export_path != settings.exports_dir:
        raise ValueError("Ruta de exportación no permitida.")
    return export_path
