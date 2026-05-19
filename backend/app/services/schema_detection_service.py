from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class SchemaReport:
    columns: list[str]
    numeric_columns: list[str]
    categorical_columns: list[str]
    date_columns: list[str]
    possible_country_column: str | None
    possible_year_column: str | None
    possible_exam_column: str | None
    possible_score_columns: list[str]
    possible_subject_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


class SchemaDetectionService:
    COUNTRY_HINTS = ["country", "pais", "país", "nacionalidad"]
    YEAR_HINTS = ["year", "anio", "año", "periodo", "período", "vigencia"]
    EXAM_HINTS = ["exam", "prueba", "evaluacion", "evaluación", "convocatoria"]
    SCORE_HINTS = [
        "score",
        "punt",
        "nota",
        "matematic",
        "lectura",
        "lenguaje",
        "ciencia",
        "social",
        "ingles",
        "inglés",
        "español",
        "naturales",
    ]
    SUBJECT_HINTS = ["area", "área", "subject", "materia", "competencia", "mod_"]

    def detect_columns(self, df: pd.DataFrame) -> list[str]:
        return [str(column) for column in df.columns]

    def detect_numeric_columns(self, df: pd.DataFrame) -> list[str]:
        numeric = df.select_dtypes(include="number").columns.tolist()
        for column in df.columns:
            if column in numeric:
                continue
            sample = pd.to_numeric(df[column].head(500), errors="coerce")
            if sample.notna().mean() >= 0.8:
                numeric.append(column)
        return numeric

    def detect_categorical_columns(self, df: pd.DataFrame) -> list[str]:
        numeric = set(self.detect_numeric_columns(df))
        return [column for column in df.columns if column not in numeric]

    def detect_date_columns(self, df: pd.DataFrame) -> list[str]:
        date_columns = []
        for column in df.columns:
            parsed = pd.to_datetime(df[column].head(500), errors="coerce", dayfirst=True)
            if parsed.notna().mean() >= 0.7:
                date_columns.append(column)
        return date_columns

    def _first_hint(self, columns: list[str], hints: list[str]) -> str | None:
        normalized = [(column, column.lower()) for column in columns]
        for hint in hints:
            for original, lowered in normalized:
                if hint in lowered:
                    return original
        return None

    def detect_possible_country_column(self, df: pd.DataFrame) -> str | None:
        return self._first_hint(self.detect_columns(df), self.COUNTRY_HINTS)

    def detect_possible_year_column(self, df: pd.DataFrame) -> str | None:
        return self._first_hint(self.detect_columns(df), self.YEAR_HINTS)

    def detect_possible_exam_column(self, df: pd.DataFrame) -> str | None:
        return self._first_hint(self.detect_columns(df), self.EXAM_HINTS)

    def detect_possible_score_columns(self, df: pd.DataFrame) -> list[str]:
        numeric = set(self.detect_numeric_columns(df))
        return [
            column
            for column in df.columns
            if column in numeric and any(hint in column.lower() for hint in self.SCORE_HINTS)
        ]

    def detect_subject_columns(self, df: pd.DataFrame) -> list[str]:
        return [
            column
            for column in df.columns
            if any(hint in column.lower() for hint in self.SUBJECT_HINTS)
        ]

    def build_report(self, df: pd.DataFrame) -> dict[str, Any]:
        report = SchemaReport(
            columns=self.detect_columns(df),
            numeric_columns=self.detect_numeric_columns(df),
            categorical_columns=self.detect_categorical_columns(df),
            date_columns=self.detect_date_columns(df),
            possible_country_column=self.detect_possible_country_column(df),
            possible_year_column=self.detect_possible_year_column(df),
            possible_exam_column=self.detect_possible_exam_column(df),
            possible_score_columns=self.detect_possible_score_columns(df),
            possible_subject_columns=self.detect_subject_columns(df),
        )
        return report.to_dict()


def infer_metadata_from_filename(path: str | Path) -> dict[str, Any]:
    name = Path(path).stem.lower()
    countries = {
        "colombia": "Colombia",
        "brasil": "Brasil",
        "brazil": "Brasil",
        "mexico": "México",
        "méxico": "México",
        "chile": "Chile",
        "peru": "Perú",
        "perú": "Perú",
        "argentina": "Argentina",
        "dominicana": "República Dominicana",
        "latam": "Latinoamérica",
    }
    exams = ["saber11", "saber pro", "saberpro", "enem", "planea", "simce", "paes", "erce", "pisa", "aprender"]
    detected_country = next((value for key, value in countries.items() if key in name), "No detectado")
    detected_exam = next((exam.upper().replace("SABER11", "Saber 11").replace("SABERPRO", "Saber Pro") for exam in exams if exam in name), "No detectada")
    years = [int(token) for token in name.replace("_", " ").replace("-", " ").split() if token.isdigit() and len(token) == 4]
    return {
        "detected_country": detected_country,
        "detected_exam": detected_exam,
        "detected_years": sorted(set(years)),
    }
