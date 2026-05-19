# Gemini y Fuentes API

## Gemini

LATAM EduAgent permite usar Gemini como proveedor LLM sin cambiar el frontend.

Configura `backend/.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key
GEMINI_MODEL=gemini-1.5-flash
```

Reinicia el backend:

```bash
uvicorn app.main:app --reload
```

El servicio `app/services/llm_service.py` enviará el prompt interno, el contexto analítico y el contexto RAG a Gemini.

## datos.gov.co

La fuente `kgxf-xxbe` fue registrada como:

```txt
saber11_colombia_api_2010_2022
```

URL:

```txt
https://www.datos.gov.co/api/v3/views/kgxf-xxbe/query.json
```

La API respondió `authentication_required`, por eso quedó con estado `pendiente_token` y `public=False`.

Para habilitarla:

```env
DATOS_GOV_CO_APP_TOKEN=tu_token
```

Luego ejecuta:

```bash
python scripts/ingest_dataset.py --id saber11_colombia_api_2010_2022
```

Si el volumen es alto, agrega `max_rows` en `datasets_registry.py` para controlar la primera ingesta local.
