from pathlib import Path

import pandas as pd


def read_tabular_file(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(file_path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    if suffix == ".json":
        return pd.read_json(file_path)
    if suffix == ".parquet":
        return pd.read_parquet(file_path)

    raise ValueError(
        f"Formato no soportado: {suffix}. Usa CSV, XLSX, JSON o Parquet."
    )
