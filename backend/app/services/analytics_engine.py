from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.services.chart_generation_service import ChartGenerationService
from app.services.column_mapping_service import SUBJECT_MAPPINGS
from app.services.dataset_catalog_service import DatasetCatalogService
from app.services.dataset_service import SCORE_COLUMNS, list_datasets, load_processed_dataset


SUBJECT_FROM_WIDE = {
    "math_score": "Matemáticas",
    "reading_score": "Lectura",
    "science_score": "Ciencias",
    "social_score": "Sociales",
    "english_score": "Inglés",
    "global_score": "Global",
}


class AnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db
        self.catalog = DatasetCatalogService(db)
        self.charts = ChartGenerationService()

    def _available_frames(self, dataset_ids: list[str] | None = None) -> tuple[list[dict], list[pd.DataFrame]]:
        selected = set(str(item) for item in dataset_ids or [])
        metadata = []
        frames = []
        for dataset in list_datasets(self.db):
            if selected and dataset["registry_id"] not in selected and str(dataset["id"]) not in selected:
                continue
            try:
                df = load_processed_dataset(dataset["registry_id"], self.db)
            except Exception:
                continue
            metadata.append(dataset)
            frames.append(df)
        return metadata, frames

    def _wide_to_long(self, dataset: dict, df: pd.DataFrame) -> pd.DataFrame:
        if {"subject", "score"}.issubset(df.columns):
            long_df = df.copy()
            defaults = {
                "dataset_id": dataset["registry_id"],
                "country": dataset.get("country"),
                "exam": dataset.get("exam"),
                "year": dataset.get("year"),
                "region": None,
                "city": None,
                "gender": None,
                "institution_type": None,
                "socioeconomic_level": None,
                "global_score": None,
                "data_mode": "demo" if dataset.get("is_demo") else "real",
                "source_file": dataset.get("original_filename"),
            }
            for column, value in defaults.items():
                if column not in long_df.columns:
                    long_df[column] = value
                elif value is not None:
                    long_df[column] = long_df[column].fillna(value)
            long_df["score"] = pd.to_numeric(long_df["score"], errors="coerce")
            long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
            if "score_scale_min" not in long_df.columns:
                long_df["score_scale_min"] = long_df.groupby(["dataset_id", "subject"])["score"].transform("min")
            if "score_scale_max" not in long_df.columns:
                long_df["score_scale_max"] = long_df.groupby(["dataset_id", "subject"])["score"].transform("max")
            if "score_normalized_0_100" not in long_df.columns:
                denom = (long_df["score_scale_max"] - long_df["score_scale_min"]).replace(0, np.nan)
                long_df["score_normalized_0_100"] = ((long_df["score"] - long_df["score_scale_min"]) / denom) * 100
            if "global_score" in long_df.columns:
                long_df["global_score"] = pd.to_numeric(long_df["global_score"], errors="coerce")
            return long_df.dropna(subset=["score"]).replace({np.nan: None})

        base_columns = ["dataset_id", "country", "exam", "year", "region", "city", "gender", "institution_type", "socioeconomic_level"]
        base = pd.DataFrame(index=df.index)
        for column in base_columns:
            base[column] = df[column] if column in df.columns else None
        base["dataset_id"] = dataset["registry_id"]
        if dataset.get("country") is not None:
            base["country"] = base["country"].fillna(dataset["country"])
        if dataset.get("exam") is not None:
            base["exam"] = base["exam"].fillna(dataset["exam"])
        if dataset.get("year") is not None:
            base["year"] = base["year"].fillna(dataset.get("year"))
        base["year"] = pd.to_numeric(base["year"], errors="coerce")
        base["data_mode"] = "demo" if dataset.get("is_demo") else "real"
        base["source_file"] = dataset.get("original_filename")

        long_frames = []
        for score_col, subject in SUBJECT_FROM_WIDE.items():
            if score_col not in df.columns:
                continue
            partial = base.copy()
            partial["subject"] = subject
            partial["score"] = pd.to_numeric(df[score_col], errors="coerce")
            partial["global_score"] = pd.to_numeric(df.get("global_score", partial["score"]), errors="coerce")
            long_frames.append(partial)
        if not long_frames:
            return pd.DataFrame()
        long_df = pd.concat(long_frames, ignore_index=True)
        long_df = long_df.dropna(subset=["score"])
        long_df["score_scale_min"] = long_df.groupby(["dataset_id", "subject"])["score"].transform("min")
        long_df["score_scale_max"] = long_df.groupby(["dataset_id", "subject"])["score"].transform("max")
        denom = (long_df["score_scale_max"] - long_df["score_scale_min"]).replace(0, np.nan)
        long_df["score_normalized_0_100"] = ((long_df["score"] - long_df["score_scale_min"]) / denom) * 100
        return long_df.replace({np.nan: None})

    def load_long_results(self, dataset_ids: list[str] | None = None) -> pd.DataFrame:
        metadata, frames = self._available_frames(dataset_ids)
        long_frames = [self._wide_to_long(dataset, df) for dataset, df in zip(metadata, frames)]
        long_frames = [df for df in long_frames if not df.empty]
        if not long_frames:
            return pd.DataFrame()
        return pd.concat(long_frames, ignore_index=True)

    def calculate_kpis(self) -> dict[str, Any]:
        catalog = self.catalog.get_dataset_catalog()
        long_df = self.load_long_results()
        return {
            "datasets": len(catalog["datasets"]),
            "countries": len(catalog["countries"]),
            "exams": len(catalog["exams"]),
            "years": len(catalog["years"]),
            "subjects": len(sorted(long_df["subject"].dropna().unique())) if not long_df.empty else 0,
            "records": int(sum(item["row_count"] for item in catalog["datasets"])),
            "long_records": int(len(long_df)),
            "data_state": self._data_state(catalog["datasets"]),
        }

    def _data_state(self, datasets: list[dict]) -> str:
        if not datasets:
            return "sin_datos"
        modes = set("demo" if item.get("is_demo") else "real" for item in datasets)
        if modes == {"demo"}:
            return "datos_demo"
        if modes == {"real"}:
            return "datos_reales"
        return "datos_mixtos"

    def detect_data_limitations(self, df: pd.DataFrame, metric: str = "score_normalized_0_100") -> list[str]:
        limitations = []
        if df.empty:
            return ["No hay datos cargados para responder la consulta."]
        if df["data_mode"].nunique() > 1:
            limitations.append("La base combina datos demo y datos reales; interpreta los resultados con cautela.")
        if df["exam"].nunique() > 1:
            limitations.append("Las pruebas pueden usar escalas y metodologías distintas; se recomienda comparar puntajes normalizados o tendencias.")
        if metric == "score_normalized_0_100":
            limitations.append("Los puntajes fueron normalizados a escala 0-100 dentro de cada dataset y materia para facilitar comparación exploratoria.")
        return limitations

    def _subject_from_query(self, query: str) -> str | None:
        lowered = query.lower()
        for subject, aliases in SUBJECT_MAPPINGS.items():
            if subject.lower() in lowered or any(alias.lower().replace("_", " ") in lowered for alias in aliases):
                return subject
        if "global" in lowered or "general" in lowered:
            return "Global"
        return None

    def analyze_user_query(self, query: str) -> dict[str, Any]:
        intent = self.classify_query(query)
        if intent == "trend":
            return self.analyze_trends(query=query)
        if intent == "gap":
            return self.analyze_gaps(query=query)
        if intent in {"comparison", "ranking", "chart"}:
            return self.compare_available_countries(query=query)
        return self.get_general_overview(query=query)

    def classify_query(self, query: str) -> str:
        lowered = query.lower()
        if any(token in lowered for token in ["tendencia", "tendencias", "histórico", "historico", "por año", "por anio"]):
            return "trend"
        if any(token in lowered for token in ["brecha", "género", "genero", "sexo", "publica", "privada", "socioecon"]):
            return "gap"
        if any(token in lowered for token in ["compara", "compar", "ranking", "mejor", "gráfica", "grafica", "país", "pais"]):
            return "comparison"
        if any(token in lowered for token in ["reporte", "power bi", "powerbi"]):
            return "report"
        return "overview"

    def get_general_overview(self, query: str = "") -> dict[str, Any]:
        df = self.load_long_results()
        kpis = self.calculate_kpis()
        if df.empty:
            return self._empty("overview")
        grouped = (
            df.groupby(["country"])["score_normalized_0_100"]
            .mean()
            .sort_values(ascending=False)
            .reset_index(name="average")
        )
        data = grouped.round(2).to_dict("records")
        return {
            "intent": "overview",
            "statistics": {"kpis": kpis, "average_by_country": data},
            "charts": [self.charts.generate_chart_payload("bar", "Promedio normalizado por país", data, "country", "average")],
            "tables": [self.charts.generate_table_payload("Resumen por país", data)],
            "insights": self._insights_from_ranking(data, "country", "average"),
            "recommendations": ["Usar filtros opcionales para profundizar por prueba, materia o año.", "Revisar documentación metodológica con RAG antes de tomar conclusiones fuertes."],
            "limitations": self.detect_data_limitations(df),
            "datasets_used": sorted(df["dataset_id"].dropna().unique().tolist()),
            "data_mode": kpis["data_state"],
        }

    def compare_available_countries(self, query: str = "", metric: str = "score_normalized_0_100") -> dict[str, Any]:
        df = self.load_long_results()
        if df.empty:
            return self._empty("comparison")
        subject = self._subject_from_query(query)
        if subject:
            df = df[df["subject"].astype(str).str.lower() == subject.lower()]
        if df.empty:
            return self._empty("comparison", f"No encontré datos comparables para la materia solicitada: {subject}.")
        grouped = (
            df.groupby("country")
            .agg(average=(metric, "mean"), records=(metric, "count"))
            .sort_values("average", ascending=False)
            .reset_index()
            .round(2)
        )
        data = grouped.to_dict("records")
        title = f"Promedio normalizado de {subject or 'todas las áreas'} por país"
        return {
            "intent": "comparison",
            "statistics": {"metric": metric, "subject": subject, "average_by_country": data, "countries": grouped["country"].tolist(), "total_records": int(grouped["records"].sum())},
            "charts": [self.charts.generate_chart_payload("bar", title, data, "country", "average", "Comparación generada automáticamente con países disponibles.")],
            "tables": [self.charts.generate_table_payload("Comparación por país", data)],
            "insights": self._insights_from_ranking(data, "country", "average"),
            "recommendations": ["Comparar también por año y tipo de prueba.", "Usar puntajes originales solo dentro de la misma prueba; entre pruebas usa normalización."],
            "limitations": self.detect_data_limitations(df, metric),
            "datasets_used": sorted(df["dataset_id"].dropna().unique().tolist()),
            "data_mode": self.calculate_kpis()["data_state"],
        }

    def compare_available_years(self, query: str = "") -> dict[str, Any]:
        return self.analyze_trends(query)

    def compare_subjects(self, query: str = "") -> dict[str, Any]:
        df = self.load_long_results()
        if df.empty:
            return self._empty("subject_comparison")
        grouped = (
            df.groupby("subject")
            .agg(average=("score_normalized_0_100", "mean"), records=("score", "count"))
            .sort_values("average", ascending=False)
            .reset_index()
            .round(2)
        )
        data = grouped.to_dict("records")
        return {
            "intent": "subject_comparison",
            "statistics": {"average_by_subject": data},
            "charts": [self.charts.generate_chart_payload("radar", "Comparación por área evaluada", data, "subject", "average")],
            "tables": [self.charts.generate_table_payload("Áreas evaluadas", data)],
            "insights": self._insights_from_ranking(data, "subject", "average"),
            "recommendations": ["Usar esta lectura para identificar áreas fuertes y críticas."],
            "limitations": self.detect_data_limitations(df),
            "datasets_used": sorted(df["dataset_id"].dropna().unique().tolist()),
            "data_mode": self.calculate_kpis()["data_state"],
        }

    def analyze_gaps(self, query: str = "") -> dict[str, Any]:
        df = self.load_long_results()
        if df.empty:
            return self._empty("gap")
        lowered = query.lower()
        dimension = "gender"
        if "instit" in lowered or "public" in lowered or "privad" in lowered:
            dimension = "institution_type"
        elif "socio" in lowered or "estrato" in lowered:
            dimension = "socioeconomic_level"
        elif "region" in lowered:
            dimension = "region"
        df = df.dropna(subset=[dimension, "score_normalized_0_100"])
        if df.empty:
            return self._empty("gap", f"No hay datos suficientes para analizar brechas por {dimension}.")
        grouped = (
            df.groupby(dimension)
            .agg(average=("score_normalized_0_100", "mean"), records=("score", "count"))
            .sort_values("average", ascending=False)
            .reset_index()
            .round(2)
        )
        data = grouped.to_dict("records")
        return {
            "intent": "gap",
            "statistics": {"dimension": dimension, "groups": data},
            "charts": [self.charts.generate_chart_payload("bar", f"Brechas por {dimension}", data, dimension, "average")],
            "tables": [self.charts.generate_table_payload(f"Brechas por {dimension}", data)],
            "insights": self._insights_from_ranking(data, dimension, "average"),
            "recommendations": ["Cruzar esta brecha con país, prueba y año para evitar conclusiones agregadas engañosas."],
            "limitations": self.detect_data_limitations(df),
            "datasets_used": sorted(df["dataset_id"].dropna().unique().tolist()),
            "data_mode": self.calculate_kpis()["data_state"],
        }

    def analyze_trends(self, query: str = "") -> dict[str, Any]:
        df = self.load_long_results()
        if df.empty or "year" not in df.columns:
            return self._empty("trend", "No hay años suficientes para generar tendencias.")
        df = df.dropna(subset=["year", "score_normalized_0_100"])
        grouped = (
            df.groupby("year")
            .agg(average=("score_normalized_0_100", "mean"), records=("score", "count"))
            .sort_index()
            .reset_index()
            .round(2)
        )
        if len(grouped) < 2:
            return self._empty("trend", "Se requieren al menos dos años para analizar tendencias.")
        data = grouped.to_dict("records")
        return {
            "intent": "trend",
            "statistics": {"average_by_year": data},
            "charts": [self.charts.generate_chart_payload("line", "Tendencia por año", data, "year", "average")],
            "tables": [self.charts.generate_table_payload("Tendencia por año", data)],
            "insights": self._trend_insights(data),
            "recommendations": ["Validar si los años pertenecen a pruebas comparables o si cambió la metodología."],
            "limitations": self.detect_data_limitations(df),
            "datasets_used": sorted(df["dataset_id"].dropna().unique().tolist()),
            "data_mode": self.calculate_kpis()["data_state"],
        }

    def generate_chart_payload(self, query: str) -> dict[str, Any]:
        return self.analyze_user_query(query)

    def generate_table_payload(self, query: str) -> dict[str, Any]:
        return self.analyze_user_query(query)

    def _insights_from_ranking(self, data: list[dict[str, Any]], label_key: str, value_key: str) -> list[str]:
        clean = [row for row in data if isinstance(row.get(value_key), (int, float))]
        if not clean:
            return ["No hay valores numéricos suficientes para generar insights."]
        top = max(clean, key=lambda row: row[value_key])
        bottom = min(clean, key=lambda row: row[value_key])
        gap = top[value_key] - bottom[value_key]
        return [
            f"{top[label_key]} presenta el promedio más alto ({top[value_key]:.2f}).",
            f"{bottom[label_key]} presenta el promedio más bajo ({bottom[value_key]:.2f}).",
            f"La brecha estimada es de {gap:.2f} puntos en la escala usada.",
        ]

    def _trend_insights(self, data: list[dict[str, Any]]) -> list[str]:
        first = data[0]
        last = data[-1]
        change = last["average"] - first["average"]
        direction = "aumentó" if change >= 0 else "disminuyó"
        return [f"Entre {first['year']} y {last['year']} el promedio {direction} {abs(change):.2f} puntos normalizados."]

    def _empty(self, intent: str, message: str | None = None) -> dict[str, Any]:
        return {
            "intent": intent,
            "statistics": {},
            "charts": [],
            "tables": [],
            "insights": [message or "No hay datos suficientes para responder."],
            "recommendations": ["Agrega archivos en data/incoming y ejecuta python scripts/ingest_incoming_datasets.py."],
            "limitations": ["Sin datos suficientes."],
            "datasets_used": [],
            "data_mode": "sin_datos",
        }
