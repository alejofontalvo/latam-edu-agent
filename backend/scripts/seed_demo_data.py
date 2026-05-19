import random

import pandas as pd

from bootstrap import PROJECT_DIR
from app.config.datasets_registry import DATASETS_REGISTRY


REGIONS = {
    "Colombia": ["Bogotá", "Antioquia", "Valle", "Atlántico", "Santander"],
    "Brasil": ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia", "Paraná"],
    "México": ["CDMX", "Jalisco", "Nuevo León", "Puebla", "Yucatán"],
    "Chile": ["Metropolitana", "Valparaíso", "Biobío", "Maule", "Antofagasta"],
    "Latinoamérica": ["Colombia", "Brasil", "México", "Chile", "Perú", "Argentina", "Uruguay"],
}


TARGET_ROWS = {
    "saber11_colombia_2023": 50000,
    "enem_brasil_2022": 80000,
    "planea_mexico_2021": 30000,
    "simce_chile_2022": 25000,
    "erce_latam_2019": 100000,
}


def bounded_score(base: float, spread: float = 38) -> float:
    return round(max(0, min(100, random.gauss(base, spread / 4))), 2)


def generate_dataset(registry_item: dict) -> pd.DataFrame:
    random.seed(registry_item["id"])
    rows = TARGET_ROWS.get(registry_item["id"], 10000)
    country = registry_item["country"]
    base = {
        "Colombia": 64,
        "Brasil": 67,
        "México": 62,
        "Chile": 68,
        "Latinoamérica": 63,
    }.get(country, 62)
    records = []
    for index in range(rows):
        socioeconomic = random.choices(["Bajo", "Medio", "Alto"], weights=[0.35, 0.45, 0.20])[0]
        institution = random.choices(["Pública", "Privada"], weights=[0.68, 0.32])[0]
        gender = random.choice(["Femenino", "Masculino"])
        lift = {"Bajo": -5, "Medio": 0, "Alto": 6}[socioeconomic] + (4 if institution == "Privada" else 0)
        math = bounded_score(base + lift + random.uniform(-3, 3))
        reading = bounded_score(base + lift + random.uniform(-2, 4))
        science = bounded_score(base + lift + random.uniform(-4, 2))
        social = bounded_score(base + lift + random.uniform(-3, 3))
        english = bounded_score(base + lift + random.uniform(-5, 5))
        global_score = round((math + reading + science + social + english) / 5, 2)
        records.append(
            {
                "student_id": f"{registry_item['id']}_{index + 1}",
                "country": country,
                "year": registry_item["year"],
                "exam": registry_item["exam"],
                "region": random.choice(REGIONS.get(country, REGIONS["Latinoamérica"])),
                "city": "Demo City",
                "gender": gender,
                "age": random.randint(15, 24),
                "institution_type": institution,
                "socioeconomic_level": socioeconomic,
                "math_score": math,
                "reading_score": reading,
                "science_score": science,
                "social_score": social,
                "english_score": english,
                "global_score": global_score,
            }
        )
    return pd.DataFrame(records)


def main() -> None:
    for registry_item in DATASETS_REGISTRY:
        path = PROJECT_DIR / registry_item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        df = generate_dataset(registry_item)
        df.to_csv(
            path,
            index=False,
            sep=registry_item.get("delimiter", ","),
            encoding=registry_item.get("encoding", "utf-8"),
        )
        print(f"Demo generado: {path} ({len(df)} filas simuladas)")


if __name__ == "__main__":
    main()
