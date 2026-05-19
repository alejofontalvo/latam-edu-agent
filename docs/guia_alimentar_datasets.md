# Guía para Alimentar Nuevos Datasets

1. Descarga el dataset oficial o prepara el archivo.
2. Ubícalo en `data/raw/<pais>/<prueba>/`.
3. Registra sus metadatos en `backend/app/config/datasets_registry.py`.
4. Agrega mapeos en `backend/app/config/column_mappings.py` si las columnas vienen con nombres específicos del país.
5. Ejecuta `python scripts/ingest_dataset.py --id <registry_id>`.
6. Revisa `GET /datasets/{registry_id}/summary`.
7. Exporta a Power BI si lo necesitas con `python scripts/export_powerbi_files.py`.

El usuario final no ve carga de archivos. Solo ve fuentes ya procesadas y disponibles.
