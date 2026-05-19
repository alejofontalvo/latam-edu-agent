# Guía de Presentación Académica

## 1. Propósito del agente

El agente busca facilitar la interacción en lenguaje natural con información de pruebas estatales latinoamericanas, permitiendo análisis educativo, generación de reportes, consulta documental y creación de evaluaciones.

## 2. Datasets

La solución usará datasets públicos y documentos técnicos de fuentes oficiales como ICFES, INEP, UNESCO, OECD y ministerios de educación de países latinoamericanos.

## 3. Recursos computacionales

Para versión académica:

- Computador con 8 GB de RAM mínimo.
- 16 GB de RAM recomendado.
- Python 3.10+.
- Node.js 18+.
- SQLite.
- ChromaDB local.
- API key de LLM opcional.

Para versión avanzada:

- 16 a 32 GB de RAM.
- PostgreSQL.
- GPU opcional si se usa LLM local.
- Servidor cloud o VPS.

## 4. Preparación del agente

El agente se prepara mediante recolección de datasets, limpieza, normalización, indexación documental con RAG, configuración de prompts, conexión con LLM, pruebas con consultas reales y validación de respuestas.

## 5. Despliegue

Primera versión:

- Local.
- Backend con FastAPI.
- Frontend con React.
- SQLite.
- ChromaDB local.

Versión avanzada:

- Render, Railway, Azure, AWS o Google Cloud.
- PostgreSQL.
- Contenedores opcionales.

## 6. Orquestador

n8n no es obligatorio. Puede plantearse como mejora futura para automatizar ingesta y actualización de datasets.

## 7. RAG

Sí se recomienda RAG, porque permite que el agente consulte documentos oficiales y evite inventar respuestas metodológicas.

## 8. Modelo propio o preentrenado

No se recomienda entrenar un modelo desde cero para la primera versión. Se usará un LLM preentrenado con RAG, porque es más eficiente, económico y realista para un proyecto académico.

## Guion de demostración

1. Mostrar arquitectura.
2. Ejecutar backend y frontend.
3. Cargar dataset de ejemplo.
4. Mostrar estadísticas básicas.
5. Hacer una consulta en chat.
6. Subir un documento y hacer una consulta RAG.
7. Generar una evaluación.
8. Exportar datos para Power BI.
9. Explicar Docker y n8n como mejoras futuras.
