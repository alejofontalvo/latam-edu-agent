# Datasets

## Fuentes sugeridas

- ICFES: Saber 11 y Saber Pro.
- INEP Brasil: ENEM.
- UNESCO / LLECE: ERCE.
- OECD: PISA con países latinoamericanos.
- Ministerio de Educación de Chile: SIMCE y PAES.
- México: PLANEA y fuentes oficiales relacionadas.

## Formatos soportados

- CSV.
- XLSX.
- JSON.
- Parquet.

## Proceso implementado

1. Carga del archivo original.
2. Lectura con Pandas.
3. Normalización de nombres de columnas.
4. Normalización básica de países y pruebas.
5. Tratamiento de valores faltantes.
6. Perfilamiento automático.
7. Registro en SQLite.
8. Guardado del archivo procesado como CSV.

## Variables esperadas

La solución no exige un esquema fijo, pero funciona mejor si el dataset incluye variables como:

- `country` o `pais`.
- `year`.
- `exam` o `prueba`.
- `region`.
- `gender`.
- `school_type`.
- `socioeconomic_level`.
- Puntajes por área: `score_math`, `score_reading`, `score_science`.

## Precauciones

El agente no debe inventar cifras. Toda estadística debe provenir de un dataset cargado o de un documento oficial citado.
