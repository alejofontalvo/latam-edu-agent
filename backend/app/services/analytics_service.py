from typing import Any

import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from app.models.entities import Document, GeneratedEvaluation
from app.services.dataset_service import SCORE_COLUMNS, list_datasets, load_processed_dataset


def _load_scope(db: Session, dataset_ids: list[int | str] | None = None) -> pd.DataFrame:
    frames = []
    datasets = list_datasets(db)
    selected = set(str(item) for item in dataset_ids or [])
    for dataset in datasets:
        if selected and str(dataset["id"]) not in selected and dataset["registry_id"] not in selected:
            continue
        try:
            frames.append(load_processed_dataset(dataset["registry_id"], db))
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _apply_filters(df: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    filtered = df.copy()
    for column, expected in filters.items():
        if expected in (None, "", []):
            continue
        if column not in filtered.columns:
            continue
        if isinstance(expected, list):
            filtered = filtered[filtered[column].astype(str).isin([str(item) for item in expected])]
        else:
            filtered = filtered[filtered[column].astype(str).str.lower() == str(expected).lower()]
    return filtered


def _numeric_mean(df: pd.DataFrame, columns: list[str]) -> dict[str, float | None]:
    result = {}
    for column in columns:
        if column in df.columns:
            series = pd.to_numeric(df[column], errors="coerce").dropna()
            result[column] = float(series.mean()) if not series.empty else None
    return result


def get_global_kpis(db: Session) -> dict:
    datasets = list_datasets(db)
    df = _load_scope(db)
    countries = sorted({item["country"] for item in datasets})
    areas = sorted({area for item in datasets for area in item.get("areas", [])})
    score_means = _numeric_mean(df, SCORE_COLUMNS)
    global_average = score_means.get("global_score") or (
        sum(value for value in score_means.values() if value is not None)
        / max(1, len([value for value in score_means.values() if value is not None]))
    )
    return {
        "countries": len(countries),
        "datasets": len(datasets),
        "records": int(sum(item["row_count"] for item in datasets)),
        "documents": int(db.query(Document).count()),
        "evaluations": int(db.query(GeneratedEvaluation).count()),
        "global_average": round(global_average or 0, 2),
        "areas": areas,
        "demo_mode": any(item["is_demo"] for item in datasets),
    }


def get_basic_statistics(dataset_id: int | str, db: Session) -> dict:
    df = load_processed_dataset(dataset_id, db)
    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(exclude="number")

    numeric_stats = {}
    for column in numeric.columns:
        series = numeric[column].dropna()
        numeric_stats[column] = {
            "mean": float(series.mean()) if not series.empty else None,
            "median": float(series.median()) if not series.empty else None,
            "std": float(series.std()) if len(series) > 1 else 0.0,
            "min": float(series.min()) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "p25": float(series.quantile(0.25)) if not series.empty else None,
            "p75": float(series.quantile(0.75)) if not series.empty else None,
        }

    categorical_stats = {}
    for column in categorical.columns[:20]:
        categorical_stats[column] = df[column].astype(str).value_counts().head(15).to_dict()

    return {
        "dataset_id": dataset_id,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "score_means": _numeric_mean(df, SCORE_COLUMNS),
        "numeric_statistics": numeric_stats,
        "categorical_statistics": categorical_stats,
        "charts": build_dataset_charts(df),
    }


def build_dataset_charts(df: pd.DataFrame) -> dict:
    charts = {}
    if df.empty:
        return charts
    if "region" in df.columns and "global_score" in df.columns:
        region = (
            df.groupby("region")["global_score"]
            .mean()
            .sort_values(ascending=False)
            .head(12)
            .reset_index(name="average_score")
        )
        charts["regions"] = {
            "chart_type": "bar",
            "title": "Ranking regional por puntaje global",
            "x_key": "region",
            "y_key": "average_score",
            "data": region.to_dict("records"),
            "insight": "Las regiones superiores muestran mejores resultados promedio en el dataset seleccionado.",
        }
    for dimension in ["gender", "institution_type", "socioeconomic_level"]:
        if dimension in df.columns and "global_score" in df.columns:
            grouped = df.groupby(dimension)["global_score"].mean().reset_index(name="average_score")
            charts[dimension] = {
                "chart_type": "bar",
                "title": f"Promedio por {dimension}",
                "x_key": dimension,
                "y_key": "average_score",
                "data": grouped.to_dict("records"),
                "insight": "Este gráfico ayuda a detectar brechas entre grupos comparables.",
            }
    return charts


def query_statistics(
    dataset_id: int | str | None,
    metric: str | None,
    operation: str,
    group_by: str | None,
    filters: dict[str, Any],
    percentile: float | None,
    db: Session,
) -> dict:
    df = load_processed_dataset(dataset_id, db) if dataset_id else _load_scope(db)
    df = _apply_filters(df, filters)
    operation = operation.lower()

    if df.empty:
        return {
            "chart_type": "empty",
            "title": "Sin datos disponibles",
            "x_key": "label",
            "y_key": "value",
            "data": [],
            "insight": "No hay datos para los filtros seleccionados.",
        }

    if metric and metric not in df.columns:
        raise ValueError(f"La métrica '{metric}' no existe en el dataset.")
    if group_by and group_by not in df.columns:
        raise ValueError(f"La variable de agrupación '{group_by}' no existe en el dataset.")

    metric = metric or "global_score"
    if metric not in df.columns:
        metric = next((column for column in SCORE_COLUMNS if column in df.columns), None)
    if not metric:
        raise ValueError("No hay métricas numéricas disponibles para analizar.")

    df[metric] = pd.to_numeric(df[metric], errors="coerce")
    agg_name = f"{operation}_{metric}"

    if group_by:
        grouped = df.groupby(group_by)[metric]
        if operation == "median":
            result_df = grouped.median().reset_index(name=agg_name)
        elif operation == "count":
            result_df = grouped.count().reset_index(name=agg_name)
        elif operation == "percentile":
            result_df = grouped.quantile((percentile or 50) / 100).reset_index(name=agg_name)
        else:
            result_df = grouped.mean().reset_index(name=agg_name)
        data = result_df.to_dict("records")
        x_key = group_by
        y_key = agg_name
    else:
        series = df[metric].dropna()
        value = float(series.mean()) if not series.empty else None
        data = [{"label": operation, "value": value}]
        x_key = "label"
        y_key = "value"

    return {
        "dataset_id": dataset_id,
        "chart_type": "bar",
        "title": f"{operation.title()} de {metric}" + (f" por {group_by}" if group_by else ""),
        "x_key": x_key,
        "y_key": y_key,
        "data": data,
        "result": data,
        "insight": generate_insight(data, x_key, y_key),
    }


def compare_groups(
    metric: str,
    dimension: str,
    filters: dict[str, Any],
    dataset_ids: list[int | str],
    db: Session,
) -> dict:
    df = _apply_filters(_load_scope(db, dataset_ids), filters)
    if df.empty or metric not in df.columns or dimension not in df.columns:
        return {
            "chart_type": "bar",
            "title": "Comparación sin datos suficientes",
            "x_key": dimension,
            "y_key": "average_score",
            "data": [],
            "insight": "No hay datos suficientes para esta comparación.",
        }

    df[metric] = pd.to_numeric(df[metric], errors="coerce")
    df = df.dropna(subset=[dimension, metric])
    if df.empty:
        return {
            "chart_type": "bar",
            "title": "Comparación sin datos suficientes",
            "x_key": dimension,
            "y_key": "average_score",
            "data": [],
            "insight": "No hay puntajes válidos para esta comparación.",
        }
    grouped = (
        df.groupby(dimension)[metric]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="average_score")
    )
    grouped = grouped.replace({np.nan: None})
    return {
        "chart_type": "bar",
        "title": f"Comparativo por {dimension}",
        "x_key": dimension,
        "y_key": "average_score",
        "data": grouped.to_dict("records"),
        "insight": generate_insight(grouped.to_dict("records"), dimension, "average_score"),
    }


def detect_gaps(df: pd.DataFrame, group_variable: str, score_variable: str) -> dict:
    grouped = (
        df.groupby(group_variable)[score_variable]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="average_score")
    )
    if grouped.empty:
        return {"gap": None, "groups": []}
    top = grouped.iloc[0].to_dict()
    bottom = grouped.iloc[-1].to_dict()
    return {
        "gap": float(top["average_score"] - bottom["average_score"]),
        "top_group": top,
        "bottom_group": bottom,
        "groups": grouped.to_dict("records"),
    }


def generate_insight(data: list[dict], x_key: str, y_key: str) -> str:
    values = [row for row in data if isinstance(row.get(y_key), (int, float))]
    if len(values) < 2:
        return "Se requiere más información para generar una interpretación comparativa."
    top = max(values, key=lambda row: row[y_key])
    bottom = min(values, key=lambda row: row[y_key])
    gap = top[y_key] - bottom[y_key]
    return (
        f"{top.get(x_key)} presenta el valor más alto y {bottom.get(x_key)} el más bajo. "
        f"La brecha estimada es de {gap:.2f} puntos; conviene revisarla con variables de contexto."
    )


def generate_chart_data(result: Any) -> list[dict]:
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return [{"label": key, "value": value} for key, value in result.items()]
    return []
