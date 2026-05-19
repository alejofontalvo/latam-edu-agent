# Sistema RAG

## Objetivo

RAG permite responder sobre metodología, diccionarios de variables, informes técnicos y guías oficiales sin depender únicamente del conocimiento general del modelo.

## Flujo

```mermaid
flowchart TD
  Docs["PDF / TXT / MD / DOCX"] --> Extract["Extracción de texto"]
  Extract --> Chunk["Fragmentación"]
  Chunk --> Embed["Embeddings locales"]
  Embed --> Chroma["ChromaDB"]
  Pregunta["Pregunta del usuario"] --> Retrieve["Recuperación semántica"]
  Chroma --> Retrieve
  Retrieve --> Answer["Respuesta con contexto y fuentes"]
```

## Implementación

Funciones principales:

- `upload_documents()`
- `extract_text()`
- `chunk_documents()`
- `retrieve_context()`
- `generate_answer_with_context()`

## Nota técnica

La versión académica usa embeddings determinísticos locales basados en hashing para evitar dependencias de API. En una versión avanzada se recomienda reemplazarlo por embeddings de OpenAI, Azure OpenAI, Sentence Transformers u otro proveedor especializado.
