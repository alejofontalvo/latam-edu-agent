import re
import unicodedata

import pandas as pd


COUNTRY_ALIASES = {
    "colombia": "Colombia",
    "co": "Colombia",
    "brasil": "Brasil",
    "brazil": "Brasil",
    "br": "Brasil",
    "chile": "Chile",
    "cl": "Chile",
    "mexico": "Mexico",
    "méxico": "Mexico",
    "mx": "Mexico",
    "peru": "Peru",
    "perú": "Peru",
    "argentina": "Argentina",
    "uruguay": "Uruguay",
    "ecuador": "Ecuador",
}

EXAM_ALIASES = {
    "saber11": "Saber 11",
    "saber_11": "Saber 11",
    "saber 11": "Saber 11",
    "saber pro": "Saber Pro",
    "enem": "ENEM",
    "erce": "ERCE",
    "llece": "LLECE",
    "pisa": "PISA",
    "simce": "SIMCE",
    "paes": "PAES",
    "planea": "PLANEA",
}


def slugify_column(name: str) -> str:
    text = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "column"


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    seen: dict[str, int] = {}
    new_columns = []
    for column in cleaned.columns:
        base = slugify_column(column)
        count = seen.get(base, 0)
        seen[base] = count + 1
        new_columns.append(base if count == 0 else f"{base}_{count + 1}")
    cleaned.columns = new_columns
    return cleaned


def normalize_country_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        if column in {"country", "pais", "país"} or "pais" in column or "country" in column:
            cleaned[column] = cleaned[column].astype(str).str.strip().str.lower().map(
                lambda value: COUNTRY_ALIASES.get(value, value.title())
            )
    return cleaned


def normalize_exam_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        if "exam" in column or "prueba" in column or "test" in column:
            cleaned[column] = cleaned[column].astype(str).str.strip().str.lower().map(
                lambda value: EXAM_ALIASES.get(value, value.upper())
            )
    return cleaned


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        if pd.api.types.is_numeric_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].fillna(cleaned[column].median())
        else:
            cleaned[column] = cleaned[column].fillna("No reportado")
    return cleaned


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_columns(df)
    cleaned = normalize_country_names(cleaned)
    cleaned = normalize_exam_names(cleaned)
    cleaned = handle_missing_values(cleaned)
    return cleaned
