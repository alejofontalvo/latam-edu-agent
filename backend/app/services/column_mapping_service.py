from __future__ import annotations

import json
from typing import Any

import pandas as pd


SUBJECT_MAPPINGS = {
    "Matemáticas": ["punt_matematicas", "nu_nota_mt", "math_score", "matematica", "matematicas", "matemáticas", "puntaje_matematica", "score_math", "mod_razona_cuantitat_punt"],
    "Lectura": ["punt_lectura_critica", "nu_nota_lc", "reading_score", "lectura", "lenguaje", "linguagens", "español", "espanol", "mod_lectura_critica_punt"],
    "Ciencias": ["punt_c_naturales", "nu_nota_cn", "science_score", "ciencias", "ciencias_naturales", "naturales"],
    "Sociales": ["punt_sociales_ciudadanas", "nu_nota_ch", "social_score", "sociales", "ciencias_humanas", "mod_competen_ciudada_punt"],
    "Inglés": ["punt_ingles", "english_score", "ingles", "inglés", "foreign_language", "mod_ingles_punt"],
}

STANDARD_MAPPINGS = {
    "country": ["country", "pais", "país"],
    "exam": ["exam", "prueba"],
    "year": ["year", "anio", "año", "periodo", "período", "vigencia"],
    "region": ["estu_depto_reside", "estu_inst_departamento", "sg_uf_prova", "region", "departamento", "estado", "provincia", "regional", "jurisdiccion"],
    "city": ["city", "ciudad", "municipio", "estu_inst_municipio", "distrito"],
    "gender": ["estu_genero", "tp_sexo", "gender", "sexo", "genero", "género"],
    "institution_type": ["institution_type", "tipo_institucion", "cole_naturaleza", "tp_escola", "sector", "nivel/modalidad"],
    "socioeconomic_level": ["socioeconomic_level", "fami_estratovivienda", "estrato", "nse", "estu_nse_individual", "nivel_socioeconomico"],
    "global_score": ["global_score", "punt_global", "score_global", "puntaje_global"],
}


class ColumnMappingService:
    def _normalize_name(self, value: str) -> str:
        return (
            str(value)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

    def suggest_column_mappings(self, columns: list[str]) -> dict[str, str]:
        suggestions: dict[str, str] = {}
        normalized_columns = {self._normalize_name(column): column for column in columns}
        for standard, aliases in STANDARD_MAPPINGS.items():
            for alias in aliases:
                alias_norm = self._normalize_name(alias)
                match = next((original for norm, original in normalized_columns.items() if alias_norm == norm or alias_norm in norm), None)
                if match:
                    suggestions[match] = standard
                    break
        for subject, aliases in SUBJECT_MAPPINGS.items():
            for alias in aliases:
                alias_norm = self._normalize_name(alias)
                match = next((original for norm, original in normalized_columns.items() if alias_norm == norm or alias_norm in norm), None)
                if match:
                    suggestions[match] = f"subject::{subject}"
                    break
        return suggestions

    def validate_mapping(self, mapping: dict[str, str], columns: list[str]) -> dict[str, Any]:
        missing = [column for column in mapping if column not in columns]
        return {"valid": not missing, "missing_columns": missing}

    def map_columns_to_standard_schema(self, df: pd.DataFrame) -> dict[str, str]:
        return self.suggest_column_mappings([str(column) for column in df.columns])

    def normalize_dataset(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        fallback_country: str,
        fallback_exam: str,
        fallback_year: int | None,
        data_mode: str,
        source_file: str,
    ) -> pd.DataFrame:
        mapping = self.map_columns_to_standard_schema(df)
        base = pd.DataFrame(index=df.index)
        for original, standard in mapping.items():
            if standard.startswith("subject::"):
                continue
            base[standard] = df[original]
        base["dataset_id"] = dataset_id
        base["country"] = base.get("country", fallback_country)
        base["exam"] = base.get("exam", fallback_exam)
        base["year"] = pd.to_numeric(base.get("year", fallback_year), errors="coerce")
        base["data_mode"] = data_mode
        base["source_file"] = source_file

        rows = []
        subject_mappings = {original: standard.split("::", 1)[1] for original, standard in mapping.items() if standard.startswith("subject::")}
        if not subject_mappings and "global_score" in base.columns:
            subject_mappings = {"global_score": "Global"}
        for original, subject in subject_mappings.items():
            partial = base.copy()
            partial["subject"] = subject
            partial["score"] = pd.to_numeric(df[original], errors="coerce")
            partial["global_score"] = pd.to_numeric(base.get("global_score", partial["score"]), errors="coerce")
            rows.append(partial)
        if not rows:
            partial = base.copy()
            partial["subject"] = "Sin puntaje detectado"
            partial["score"] = pd.NA
            partial["global_score"] = pd.to_numeric(base.get("global_score", pd.NA), errors="coerce")
            rows.append(partial)
        normalized = pd.concat(rows, ignore_index=True)
        for column in [
            "region",
            "city",
            "institution_name",
            "institution_type",
            "gender",
            "age",
            "socioeconomic_level",
            "score_scale_min",
            "score_scale_max",
        ]:
            if column not in normalized.columns:
                normalized[column] = None
        normalized["score_scale_min"] = normalized.groupby(["dataset_id", "subject"])["score"].transform("min")
        normalized["score_scale_max"] = normalized.groupby(["dataset_id", "subject"])["score"].transform("max")
        denominator = normalized["score_scale_max"] - normalized["score_scale_min"]
        normalized["score_normalized_0_100"] = ((normalized["score"] - normalized["score_scale_min"]) / denominator.replace(0, pd.NA)) * 100
        normalized["raw_data_json"] = "{}"
        return normalized[
            [
                "dataset_id",
                "country",
                "exam",
                "year",
                "region",
                "city",
                "institution_name",
                "institution_type",
                "gender",
                "age",
                "socioeconomic_level",
                "subject",
                "score",
                "score_normalized_0_100",
                "score_scale_min",
                "score_scale_max",
                "global_score",
                "data_mode",
                "source_file",
                "raw_data_json",
            ]
        ]

    def create_raw_data_json_for_unmapped_columns(self, df: pd.DataFrame, mapped_columns: list[str]) -> pd.Series:
        unmapped = [column for column in df.columns if column not in mapped_columns]
        if not unmapped:
            return pd.Series(["{}"] * len(df), index=df.index)
        return df[unmapped].astype(object).where(pd.notna(df[unmapped]), None).apply(
            lambda row: json.dumps(row.to_dict(), ensure_ascii=False), axis=1
        )
