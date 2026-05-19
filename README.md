# LATAM EduAgent

Plataforma local de inteligencia artificial y analítica educativa para consultar, comparar y generar evaluaciones sobre pruebas estatales latinoamericanas como Saber 11, Saber Pro, ENEM, ERCE, PISA, SIMCE, PAES y PLANEA.

La versión actual funciona como un observatorio dinámico prealimentado: el usuario final no sube datasets ni necesita seleccionar país, año, prueba o archivo para empezar. El administrador agrega datos por detrás y LATAM EduAgent detecta qué existe, normaliza variables comparables y permite que el chat genere análisis, gráficas, tablas y reportes con base en el catálogo disponible.

## Filosofía dinámica

LATAM EduAgent no depende de países predefinidos. La plataforma se construye automáticamente con los datasets que agregues al backend. Si hoy solo existe Colombia, analiza Colombia; si mañana agregas Brasil, México o Perú, las comparaciones del chat los incorporan según las variables detectadas.

El flujo principal es:

1. El administrador deja archivos en `data/incoming` o registra fuentes internas.
2. El backend ingiere, detecta esquema, normaliza columnas y actualiza el catálogo.
3. El usuario pregunta en lenguaje natural.
4. El agente consulta el catálogo, decide qué análisis corresponde y llama al motor estadístico.
5. Los cálculos los hace Python/Pandas/SQL, no el LLM.
6. Gemini interpreta los resultados sin inventar cifras y devuelve respuesta, gráficas, tablas, insights, recomendaciones y limitaciones.

## Qué incluye

- Frontend React/Vite/Tailwind con dashboard premium, dark mode, sidebar, microinteracciones y gráficos.
- Backend FastAPI con catálogo interno de datasets, SQLite por defecto y PostgreSQL opcional.
- Catálogo dinámico de datasets, países, pruebas, años, variables y calidad de datos.
- Modelo normalizado en formato largo para comparar países, pruebas, años, materias, regiones, género, institución y nivel socioeconómico.
- Chat IA como centro de la experiencia, conectado a catálogo interno, motor analítico, RAG y generador de evaluaciones.
- Proveedor LLM configurable: modo local, OpenAI o Gemini.
- RAG con documentos indexados por administrador en ChromaDB.
- Exportaciones CSV, Excel y endpoints JSON para Power BI.
- Scripts para seed demo, ingesta interna, indexado documental, rebuild y exportación.
- Docker y n8n documentados como mejoras opcionales, no obligatorias.

## Ejecución local

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Web: `http://localhost:5173`

## Preparar datos demo

Los datos demo son simulados y están marcados como demo. Sirven para que la plataforma se vea viva durante la presentación.

```bash
cd backend
source venv/bin/activate
python scripts/seed_demo_data.py
python scripts/rebuild_database.py
python scripts/ingest_all_datasets.py
python scripts/index_documents.py
python scripts/export_powerbi_files.py
```

Datasets demo incluidos:

- Colombia / Saber 11 / 2023 / 50.000 registros simulados.
- Brasil / ENEM / 2022 / 80.000 registros simulados.
- México / PLANEA / 2021 / 30.000 registros simulados.
- Chile / SIMCE / 2022 / 25.000 registros simulados.
- Latinoamérica / ERCE / 2019 / 100.000 registros simulados.

## Fuentes reales agregadas localmente

Además de los datos demo, el catálogo incluye fuentes reales entregadas como archivos locales:

- Saber Pro Genéricas Colombia 2014, 2015, 2020, 2021, 2023 y 2024.
- APRENDER Argentina 2024 Secundaria agregada.
- Pruebas Nacionales República Dominicana 2016-2024.
- Informe nacional Perú en PISA 2022 indexado en RAG.

Para mantener la ejecución local ágil, los archivos Saber Pro están registrados con `max_rows=50000` por año. Puedes quitar o aumentar ese límite en `backend/app/config/datasets_registry.py`.

## Alimentar el sistema con nuevos datasets

### Opción recomendada: ingesta automática desde `data/incoming`

1. Copia cualquier `CSV`, `XLSX`, `JSON` o `Parquet` a:

```txt
data/incoming/
```

2. Ejecuta:

```bash
cd backend
source venv/bin/activate
python scripts/ingest_incoming_datasets.py
```

El sistema:

- Detecta formato.
- Infere país, prueba y años cuando sea posible.
- Detecta columnas numéricas, categóricas, fechas y puntajes.
- Sugiere/aplica mapeos de columnas.
- Normaliza resultados en formato largo.
- Guarda procesados en `data/processed`.
- Registra metadatos en `data/metadata`.
- Mueve archivos a `data/archive`.
- Actualiza el catálogo que ve el frontend.

También puedes ingerir un archivo puntual:

```bash
python scripts/ingest_dataset.py --file data/incoming/saber11_2023.csv
```

### Opción avanzada: registro controlado

1. Copia el archivo a `data/raw/<pais>/<prueba>/`.
2. Regístralo en `backend/app/config/datasets_registry.py`.
3. Si necesitas mapeos manuales, ajusta `backend/app/config/column_mappings.py` o el servicio de mapeo.
4. Ejecuta:

```bash
python scripts/ingest_dataset.py --id saber11_colombia_2023
```

O ingiere todos:

```bash
python scripts/ingest_all_datasets.py
```

## Modelo normalizado

La tabla lógica principal es `normalized_results` en formato largo:

```txt
id, dataset_id, country, exam, year, region, city, institution_name,
institution_type, gender, age, socioeconomic_level, subject, score,
score_scale_min, score_scale_max, score_normalized_0_100, global_score,
data_mode, source_file, raw_data_json
```

Un estudiante o registro puede producir varias filas, una por materia. Esto facilita comparar “Matemáticas”, “Lectura”, “Ciencias” u otras áreas entre los países que existan. Si un dataset no tiene alguna columna, el valor queda nulo y la respuesta del chat debe advertir limitaciones.

## RAG administrativo

El usuario final consulta documentos, pero no los carga. Para indexar documentos:

```bash
python scripts/index_documents.py
```

Ubicación sugerida:

```txt
data/documents/
├── icfes/
├── inep/
├── unesco/
├── oecd/
├── ministerios/
└── otros/
```

## Usar Gemini

Configura el backend en `backend/.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key_de_gemini
GEMINI_MODEL=gemini-2.5-flash-lite
```

Luego reinicia FastAPI:

```bash
uvicorn app.main:app --reload
```

No publiques ni pegues tu API key en documentación o capturas. Después de cambiar `.env`, reinicia FastAPI.

## Fuente API datos.gov.co

Se registró la fuente:

```txt
https://www.datos.gov.co/api/v3/views/kgxf-xxbe/query.json
```

Corresponde a `Resultados únicos Saber 11`. La consulta directa respondió que requiere autenticación o token de aplicación. Para activarla, define:

```env
DATOS_GOV_CO_APP_TOKEN=tu_token
```

Luego cambia `public` si deseas mostrarla y ejecuta:

```bash
python scripts/ingest_dataset.py --id saber11_colombia_api_2010_2022
```

## Power BI

Exportar archivos compatibles:

```bash
python scripts/export_powerbi_files.py
```

Genera:

- `data/exports/powerbi/catalog.csv`
- `data/exports/powerbi/normalized_results.csv`
- `data/exports/powerbi/countries.csv`
- `data/exports/powerbi/exams.csv`
- `data/exports/powerbi/kpis.csv`
- `data/exports/powerbi/comparisons.csv`
- `data/exports/powerbi/data_quality.csv`

Endpoints:

```txt
GET /powerbi/catalog
GET /powerbi/dataset/{dataset_id}
GET /powerbi/normalized-results
GET /powerbi/kpis
GET /powerbi/comparisons
GET /powerbi/data-quality
```

## Endpoints públicos

```txt
GET /
GET /health
GET /system/status
GET /catalog
GET /catalog/countries
GET /catalog/exams
GET /catalog/years
GET /catalog/subjects
GET /catalog/variables
GET /catalog/datasets
GET /datasets
GET /datasets/{dataset_id}
GET /datasets/{dataset_id}/summary
GET /datasets/{dataset_id}/columns
GET /datasets/{dataset_id}/filters
GET /datasets/{dataset_id}/preview
GET /countries
GET /countries/{country}/exams
GET /exams
GET /analytics/kpis
POST /analytics/auto
POST /analytics/overview
POST /analytics/trends
POST /analytics/gaps
POST /analytics/chart
GET /analytics/basic/{dataset_id}
POST /analytics/query
POST /analytics/compare
POST /chat
POST /evaluations/generate
GET /rag/documents
POST /rag/query
GET /reports/export/csv/{dataset_id}
GET /reports/export/excel/{dataset_id}
```

## Endpoints admin

Protegidos con header:

```txt
X-Admin-Api-Key: valor_de_ADMIN_API_KEY
```

```txt
POST /admin/datasets/refresh
POST /admin/datasets/ingest?registry_id=saber11_colombia_2023
POST /admin/ingest
POST /admin/reindex
GET /admin/ingestion-report
POST /admin/rag/index-documents
GET /admin/system/status
```

## Uso como usuario final

El usuario final entra al frontend y puede:

- Explorar el Observatorio LATAM.
- Preguntar libremente en el chat IA sin seleccionar dataset.
- Analizar KPIs y gráficos generados desde el catálogo completo.
- Comparar países, pruebas, años y grupos detectados automáticamente.
- Generar evaluaciones.
- Revisar documentos RAG ya indexados.
- Exportar reportes para Power BI.

## Uso como administrador

El administrador:

- Descarga o agrega datasets en `data/raw`.
- O deja archivos directamente en `data/incoming`.
- Registra fuentes en `datasets_registry.py`.
- Ajusta mapeos de columnas.
- Ejecuta `python scripts/ingest_incoming_datasets.py` o `python scripts/ingest_dataset.py --file ...`.
- Indexa documentos RAG.
- Exporta archivos Power BI.
- Puede usar endpoints admin con `ADMIN_API_KEY`.

## Prompt interno del agente

El agente opera con esta regla central:

```txt
Eres LATAM EduAgent, un analista inteligente de datos educativos para pruebas estatales y evaluaciones estandarizadas de Latinoamérica.

Tu tarea no es esperar que el usuario seleccione un dataset, país o año. Tu tarea es interpretar la pregunta del usuario, revisar automáticamente qué datos existen en el sistema y generar análisis con base en los datasets disponibles.

Reglas:
- No inventes cifras.
- No asumas países, años o pruebas que no estén en el catálogo.
- Antes de responder análisis estadístico, consulta el catálogo de datos disponibles.
- Si hay datos suficientes, solicita al motor analítico los cálculos necesarios.
- Si no hay datos suficientes, explica qué información falta.
- Si hay datos demo, aclara que son demostrativos.
- Usa RAG solo para contexto, metodología, definiciones y explicación documental.
- Las estadísticas deben venir del backend, no del LLM.
- Si las escalas de evaluación son diferentes, advierte que la comparación requiere normalización.
- Responde siempre en español claro, técnico y útil.
```

## Docker opcional

Docker no es obligatorio. Para una entrega académica se recomienda ejecución local. Docker se mantiene como mejora futura para producción, reproducibilidad y despliegue cloud.
