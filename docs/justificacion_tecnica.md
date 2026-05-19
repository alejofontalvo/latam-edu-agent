# Justificación Técnica

## Elección del stack

FastAPI permite construir una API clara, rápida y fácil de documentar con Swagger. React con Vite ofrece una interfaz ligera para una demostración académica. SQLite reduce fricción de instalación, mientras SQLAlchemy deja abierta la migración a PostgreSQL.

## Datasets y analítica

Pandas es suficiente para la primera versión por su madurez y facilidad de uso. Polars puede incorporarse si se manejan archivos de gran tamaño.

## RAG

ChromaDB local permite indexar documentos técnicos sin infraestructura adicional. RAG es necesario para responder sobre metodología, definiciones y documentos oficiales con fuentes.

## LLM

El proyecto usa un LLM preentrenado. Entrenar un modelo desde cero no es recomendable para esta etapa por requerimientos de datos, cómputo, evaluación y mantenimiento.

## Base de datos

SQLite es la opción inicial por simplicidad. PostgreSQL se recomienda para concurrencia, producción, datasets grandes y conexión empresarial.

## Docker y n8n

Ambos se dejan como mejoras opcionales. Incluirlos como requisito central aumentaría la complejidad de la entrega sin mejorar necesariamente la demostración académica inicial.
