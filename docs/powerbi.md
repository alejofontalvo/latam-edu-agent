# Power BI

## Salidas implementadas

1. CSV limpio: `GET /reports/export/csv/{dataset_id}`.
2. Excel limpio con diccionario: `GET /reports/export/excel/{dataset_id}`.
3. Endpoint JSON: `GET /powerbi/dataset/{dataset_id}`.

## Conectar Power BI a CSV o Excel

1. Ejecutar una exportación desde la interfaz.
2. Abrir Power BI Desktop.
3. Usar Obtener datos.
4. Seleccionar Texto/CSV o Excel.
5. Cargar el archivo generado en `data/exports`.

## Conectar Power BI a API

1. Obtener datos.
2. Seleccionar Web.
3. Usar `http://localhost:8000/powerbi/dataset/1`.
4. Expandir `records`.

## Dashboards recomendados

- Resultados generales Latinoamérica.
- Comparativo por país.
- Comparativo por año.
- Brechas por género.
- Brechas por tipo de institución.
- Brechas por nivel socioeconómico.
- Tendencias históricas.
- Análisis por área evaluada.

## Modelo sugerido

Tabla principal de resultados con dimensiones derivadas:

- País.
- Año.
- Prueba.
- Región.
- Género.
- Institución.
- Nivel socioeconómico.
- Área evaluada.
