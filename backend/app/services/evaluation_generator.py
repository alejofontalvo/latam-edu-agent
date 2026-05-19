import json
from sqlalchemy.orm import Session

from app.models.entities import GeneratedEvaluation


def generate_evaluation(
    area: str,
    country: str,
    exam_reference: str,
    difficulty: str,
    number_of_questions: int,
    topic: str | None,
    db: Session,
) -> dict:
    questions = []
    topic_text = topic or "competencias generales"
    for index in range(1, number_of_questions + 1):
        questions.append(
            {
                "number": index,
                "area": area,
                "country": country,
                "exam_reference": exam_reference,
                "difficulty": difficulty,
                "topic": topic_text,
                "question": (
                    f"Pregunta {index}: En el contexto de {exam_reference}, un estudiante debe "
                    f"resolver una situación de {area} sobre {topic_text}. ¿Cuál alternativa "
                    "presenta la interpretación más adecuada?"
                ),
                "options": {
                    "A": "Selecciona una respuesta sin justificarla con evidencia.",
                    "B": "Identifica datos relevantes, los relaciona y sustenta la conclusión.",
                    "C": "Repite literalmente una frase del enunciado sin analizarla.",
                    "D": "Descarta toda la información contextual del problema.",
                },
                "correct_answer": "B",
                "explanation": (
                    "La opción B es correcta porque integra evidencia del enunciado, "
                    "razonamiento y una conclusión coherente con la competencia evaluada."
                ),
            }
        )

    payload = {
        "title": f"Evaluación {exam_reference} - {area}",
        "instructions": "Seleccione la respuesta correcta en cada pregunta.",
        "questions": questions,
    }
    entity = GeneratedEvaluation(
        title=payload["title"],
        area=area,
        country=country,
        exam_reference=exam_reference,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)

    return {"evaluation_id": entity.id, **payload}
