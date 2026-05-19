import json
from typing import Any

from app.utils.prompt_templates import SYSTEM_PROMPT


async def call_llm(prompt: str, context: str | None = None) -> str:
    try:
        from app.config import get_settings

        settings = get_settings()
        if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Contexto:\n{context or 'Sin contexto'}\n\nPregunta:\n{prompt}",
                    },
                ],
                temperature=0.2,
            )
            return response.choices[0].message.content or ""
        if settings.llm_provider.lower() == "gemini" and settings.gemini_api_key:
            import httpx

            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{settings.gemini_model}:generateContent"
            )
            response = httpx.post(
                url,
                params={"key": settings.gemini_api_key},
                json={
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": f"Contexto:\n{context or 'Sin contexto'}\n\nPregunta:\n{prompt}"
                                }
                            ],
                        }
                    ],
                    "generationConfig": {"temperature": 0.2},
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            return (
                payload.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
    except Exception as exc:
        return f"No fue posible consultar el LLM configurado: {exc}"

    return (
        "Gemini no está configurado para el chat. Define LLM_PROVIDER=gemini, "
        "GEMINI_API_KEY y GEMINI_MODEL en backend/.env, y reinicia FastAPI."
    )


def local_response(prompt: str, context: str | None = None) -> str:
    if context:
        return (
            "Respuesta generada en modo local con contexto recuperado:\n\n"
            f"{context[:1600]}\n\n"
            "Para una redacción más elaborada, configura LLM_PROVIDER=openai y OPENAI_API_KEY."
        )
    return (
        "Estoy en modo local sin LLM externo. Puedo cargar datasets, calcular estadísticas, "
        "consultar documentos indexados y generar evaluaciones base. Para respuestas generativas "
        "avanzadas configura un proveedor LLM en el archivo .env."
    )


def safe_json_loads(text: str, fallback: Any) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return fallback
